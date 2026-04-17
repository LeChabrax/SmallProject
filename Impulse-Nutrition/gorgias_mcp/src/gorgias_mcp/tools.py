"""All MCP tools exposed by the Gorgias server.

Tool names and core return shapes are backward-compatible with the legacy
single-file implementation. Notable additions:

- `list_tickets` accepts `status` / `channel` / `view_id` filters that resolve
  to the working `/api/views/{view_id}/items` endpoint instead of the broken
  `/tickets?status=` query param.
- `list_views` exposes the static view-id maps so the skill can introspect
  available filters.
- `get_ticket_stats` paginates view items and reports a `capped` flag when
  the result set exceeds the cap.
- `assign_ticket` reuses a TTL-cached user list.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from .cache import ttl_cache
from .client import get_client
from .slim import extract_customer_email, slim_customer, slim_message, slim_ticket
from .views import build_maps, resolve_view_id

logger = logging.getLogger(__name__)

DEFAULT_AGENT_EMAIL = os.getenv("GORGIAS_DEFAULT_AGENT", "achabrat@havea.com")
STATS_PAGE_SIZE = 100
STATS_MAX_PAGES = 5  # cap at 500 to keep get_ticket_stats fast

# Inbound-only channels that can't be used as outbound reply channel in Gorgias V2.
# When a ticket arrives via one of these, the agent reply must go out via email
# (or the channel's own native outbound if supported). Mapping keeps the reply
# flowing to the customer's verified email address.
_INBOUND_ONLY_CHANNELS = {
    "contact_form": "email",
    "help_center": "email",
    "yotpo-review": "email",
    "internal-note": "email",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _list_view_items(view_id: int, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return get_client().get(f"/views/{view_id}/items", params=params or {})


def _list_tickets_endpoint(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return get_client().get("/tickets", params=params or {})


@ttl_cache(seconds=600)
def _cached_users() -> List[Dict[str, Any]]:
    resp = get_client().get("/users", params={"limit": 100})
    return resp.get("data", []) or []


@ttl_cache(seconds=3600)
def _views_maps() -> Dict[str, Dict[str, int]]:
    """Fetch `/api/views` once per hour and build alias maps.

    View IDs are account-specific, so they're resolved at runtime from
    the live Gorgias response rather than hardcoded.
    """
    resp = get_client().get("/views", params={"limit": 100})
    return build_maps(resp.get("data", []) or [])


# ---------------------------------------------------------------------------
# Ticket tools
# ---------------------------------------------------------------------------


def list_tickets(
    limit: int = 30,
    order_by: str = "updated_datetime:desc",
    status: Optional[str] = None,
    channel: Optional[str] = None,
    view_id: Optional[int] = None,
) -> Dict[str, Any]:
    """List recent support tickets.

    Filtering precedence: explicit `view_id` > `channel` > `status`.
    When any filter is given, the request goes through `/views/{id}/items`
    (the only endpoint that honors these filters in V2). Without filters,
    falls back to the raw `/tickets` listing.

    Args:
        limit: Number of tickets to return (max 100).
        order_by: Sort order (e.g. "created_datetime:desc").
        status: System view alias (open, closed, snoozed, unassigned, all).
        channel: Channel view alias (email, contact_form, chat, help_center).
        view_id: Raw Gorgias view id, overrides status/channel.
    """
    capped_limit = min(int(limit), 100)
    if view_id is not None:
        resolved_view: Optional[int] = int(view_id)
    elif status or channel:
        resolved_view = resolve_view_id(
            _views_maps(), status=status, channel=channel
        )
    else:
        resolved_view = None
    params = {"limit": capped_limit, "order_by": order_by}
    if resolved_view is not None:
        resp = _list_view_items(resolved_view, params)
    else:
        resp = _list_tickets_endpoint(params)
    return {
        "tickets": [slim_ticket(t) for t in resp.get("data", []) or []],
        "total": resp.get("meta", {}).get("total_resources"),
        "view_id": resolved_view,
    }


def list_views() -> Dict[str, Dict[str, int]]:
    """Return live view-id maps resolved from `/api/views` (system/channel/user)."""
    maps = _views_maps()
    return {
        "system": dict(maps.get("system", {})),
        "channel": dict(maps.get("channel", {})),
        "user": dict(maps.get("user", {})),
    }


def get_ticket(ticket_id: int) -> Dict[str, Any]:
    """Get full details of a specific ticket."""
    return slim_ticket(get_client().get(f"/tickets/{int(ticket_id)}"))


def list_ticket_messages(
    ticket_id: int,
    limit: int = 30,
    full_body: bool = False,
) -> Dict[str, Any]:
    """List all messages in a ticket.

    Args:
        ticket_id: The Gorgias ticket id.
        limit: Number of messages to return.
        full_body: If True, return the full body text (no truncation).
    """
    resp = get_client().get(
        f"/tickets/{int(ticket_id)}/messages",
        params={"limit": int(limit)},
    )
    return {
        "messages": [
            slim_message(m, full_body=full_body) for m in resp.get("data", []) or []
        ]
    }


def search_tickets(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search tickets by id, customer email, or substring.

    Strategy (the Gorgias `/search` endpoint returns 405; this is the
    documented replacement):
      1. If `query` is numeric → try direct `get_ticket(query)`.
      2. Lookup customers by email → pull each customer's tickets.
      3. Fallback: scan the Inbox view (open tickets) and substring-match
         against subject / customer name / customer email.
    """
    q = (query or "").strip()
    q_lower = q.lower()
    tickets_by_id: Dict[int, Dict] = {}

    if q.isdigit():
        try:
            t = get_client().get(f"/tickets/{int(q)}")
            if t and t.get("id"):
                tickets_by_id[t["id"]] = t
        except Exception as e:  # noqa: BLE001
            logger.debug("search_tickets numeric lookup miss: %s", e)

    if len(tickets_by_id) < limit:
        try:
            cust_resp = get_client().get("/customers", params={"limit": 10, "email": q})
            for c in cust_resp.get("data", []) or []:
                cid = c.get("id")
                if not cid:
                    continue
                t_resp = get_client().get(
                    "/tickets",
                    params={
                        "customer_id": cid,
                        "limit": limit,
                        "order_by": "updated_datetime:desc",
                    },
                )
                for t in t_resp.get("data", []) or []:
                    tid = t.get("id")
                    if tid and tid not in tickets_by_id:
                        tickets_by_id[tid] = t
                        if len(tickets_by_id) >= limit:
                            break
                if len(tickets_by_id) >= limit:
                    break
        except Exception as e:  # noqa: BLE001
            logger.warning("search_tickets customer lookup failed: %s", e)

    if len(tickets_by_id) < limit and q_lower:
        try:
            inbox_id = _views_maps().get("system", {}).get("open")
            if inbox_id is None:
                raise RuntimeError("Inbox view id not resolvable")
            recent = _list_view_items(
                inbox_id,
                {"limit": 100, "order_by": "updated_datetime:desc"},
            )
            for t in recent.get("data", []) or []:
                tid = t.get("id")
                if not tid or tid in tickets_by_id:
                    continue
                subject = (t.get("subject") or "").lower()
                customer = t.get("customer") or {}
                c_name = (customer.get("name") or "").lower()
                c_email = (customer.get("email") or "").lower()
                if q_lower in subject or q_lower in c_name or q_lower in c_email:
                    tickets_by_id[tid] = t
                    if len(tickets_by_id) >= limit:
                        break
        except Exception as e:  # noqa: BLE001
            logger.warning("search_tickets fallback scan failed: %s", e)

    results = list(tickets_by_id.values())[:limit]
    return {
        "tickets": [slim_ticket(t) for t in results],
        "total": len(results),
    }


def _next_cursor_from_meta(meta: Dict[str, Any]) -> Optional[str]:
    """Extract the cursor token from a `meta.next_items` URL (or None)."""
    next_items = (meta or {}).get("next_items")
    if not next_items:
        return None
    qs = parse_qs(urlparse(next_items).query)
    cursor = qs.get("cursor", [None])[0]
    return cursor


def get_ticket_stats() -> Dict[str, Any]:
    """Return ticket counts by status.

    Paginates each system view up to STATS_MAX_PAGES * STATS_PAGE_SIZE
    items. Returns `{"count": N, "capped": bool}` per status — `capped`
    means the real count is at least N (likely higher).
    """
    system_map = _views_maps().get("system", {})
    out: Dict[str, Dict[str, Any]] = {}
    for status in ["open", "closed", "snoozed", "unassigned"]:
        view_id = system_map.get(status)
        if view_id is None:
            out[status] = {"count": 0, "capped": False, "error": f"view '{status}' not found"}
            continue
        count = 0
        capped = False
        cursor: Optional[str] = None
        for page in range(STATS_MAX_PAGES):
            params: Dict[str, Any] = {"limit": STATS_PAGE_SIZE}
            if cursor:
                params["cursor"] = cursor
                params["direction"] = "next"
            resp = _list_view_items(view_id, params)
            data = resp.get("data", []) or []
            count += len(data)
            cursor = _next_cursor_from_meta(resp.get("meta") or {})
            if not cursor:
                break
            if page == STATS_MAX_PAGES - 1:
                capped = True
        out[status] = {"count": count, "capped": capped}
    return out


# ---------------------------------------------------------------------------
# Customer tools
# ---------------------------------------------------------------------------


def list_customers(limit: int = 30, order_by: str = "updated_datetime:desc") -> Dict[str, Any]:
    """List customers."""
    resp = get_client().get(
        "/customers",
        params={"limit": int(limit), "order_by": order_by},
    )
    return {"customers": [slim_customer(c) for c in resp.get("data", []) or []]}


def get_customer(customer_id: int) -> Dict[str, Any]:
    """Get details of a specific customer."""
    return slim_customer(get_client().get(f"/customers/{int(customer_id)}"))


def search_customers(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search customers by email (the only field Gorgias indexes here)."""
    resp = get_client().get(
        "/customers",
        params={"limit": int(limit), "email": query},
    )
    return {"customers": [slim_customer(c) for c in resp.get("data", []) or []]}


# ---------------------------------------------------------------------------
# Tag tools
# ---------------------------------------------------------------------------


def list_tags() -> Dict[str, Any]:
    """List all available tags. Returns `{"tags": [{id, name}, ...]}`."""
    resp = get_client().get("/tags", params={"limit": 100})
    return {
        "tags": [
            {"id": tag.get("id"), "name": tag.get("name")}
            for tag in resp.get("data", []) or []
        ]
    }


# ---------------------------------------------------------------------------
# Mutation tools
# ---------------------------------------------------------------------------


def reply_to_ticket(
    ticket_id: int,
    body_text: str,
    close_after: bool = False,
) -> Dict[str, Any]:
    """Send a reply (public message) to a ticket and optionally close it."""
    client = get_client()
    ticket = client.get(f"/tickets/{int(ticket_id)}")
    customer = ticket.get("customer") or {}
    to_address = extract_customer_email(ticket)
    if not to_address:
        raise ValueError(f"Ticket {ticket_id} has no usable customer email")

    source_channel = ticket.get("channel") or "email"
    reply_channel = _INBOUND_ONLY_CHANNELS.get(source_channel, source_channel)
    payload = {
        "channel": reply_channel,
        "via": "api",
        "from_agent": True,
        "sender": {"id": None},
        "receiver": {
            "id": customer.get("id"),
            "name": customer.get("name") or to_address,
            "email": to_address,
        },
        "subject": ticket.get("subject"),
        "body_text": body_text,
        "body_html": body_text.replace("\n", "<br />"),
    }
    msg = client.post(f"/tickets/{int(ticket_id)}/messages", json=payload)

    closed = False
    if close_after:
        client.put(f"/tickets/{int(ticket_id)}", json={"status": "closed"})
        closed = True

    return {
        "message_id": msg.get("id"),
        "ticket_id": int(ticket_id),
        "ticket_closed": closed,
    }


def close_ticket(ticket_id: int) -> Dict[str, Any]:
    """Mark a ticket as closed."""
    get_client().put(f"/tickets/{int(ticket_id)}", json={"status": "closed"})
    return {"ticket_id": int(ticket_id), "status": "closed"}


def assign_ticket(
    ticket_id: int,
    agent_email: str = "",
) -> Dict[str, Any]:
    """Assign a ticket to a Gorgias user.

    Uses a TTL-cached user list (10 min) to avoid scanning all 100 users
    on every call. Pass `agent_email=""` to use the configured default.
    """
    target_email = (agent_email or DEFAULT_AGENT_EMAIL).lower()
    users = _cached_users()
    match = next(
        (u for u in users if (u.get("email") or "").lower() == target_email),
        None,
    )
    if not match:
        return {
            "error": f"No Gorgias user found with email {target_email}",
            "ticket_id": int(ticket_id),
        }
    get_client().put(
        f"/tickets/{int(ticket_id)}",
        json={"assignee_user": {"id": match["id"]}},
    )
    return {
        "ticket_id": int(ticket_id),
        "assigned_to": {"id": match["id"], "email": match.get("email")},
    }
