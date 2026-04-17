"""Field reducers for Gorgias tickets / messages / customers.

Gorgias API responses are verbose (50+ fields per ticket). Slimming keeps
LLM context lean while preserving every field the `/gorgias` skill needs.
"""

from typing import Any, Dict


def slim_ticket(t: Dict[str, Any]) -> Dict[str, Any]:
    customer = t.get("customer") or {}
    assignee = t.get("assignee_user") or {}
    return {
        "id": t.get("id"),
        "subject": t.get("subject"),
        "status": t.get("status"),
        "channel": t.get("channel"),
        "customer": {
            "id": customer.get("id"),
            "name": customer.get("name"),
            "email": customer.get("email"),
        },
        "assignee": {
            "id": assignee.get("id"),
            "name": assignee.get("name"),
        } if assignee.get("id") else None,
        "created_datetime": t.get("created_datetime"),
        "updated_datetime": t.get("updated_datetime"),
        "tags": [tag.get("name") for tag in (t.get("tags") or [])],
        "messages_count": t.get("messages_count"),
    }


def slim_message(m: Dict[str, Any], full_body: bool = False) -> Dict[str, Any]:
    source = m.get("source") or {}
    sender = source.get("from") or {}
    body = m.get("body_text") or ""
    if not full_body and len(body) > 600:
        body = body[:600] + "..."
    return {
        "id": m.get("id"),
        "created_datetime": m.get("created_datetime"),
        "from_agent": m.get("from_agent"),
        "sender": {"name": sender.get("name"), "address": sender.get("address")},
        "body_text": body,
    }


def slim_customer(c: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "id": c.get("id"),
        "name": c.get("name"),
        "email": c.get("email"),
        "created_datetime": c.get("created_datetime"),
        "updated_datetime": c.get("updated_datetime"),
    }
    if c.get("nb_tickets") is not None:
        result["nb_tickets"] = c["nb_tickets"]
    return result


def extract_customer_email(ticket: Dict[str, Any]) -> str:
    """Pull a usable email from a ticket's customer.

    Tries `customer.email` first, then `customer.channels[type=email]`
    (Gorgias V2 schema), then falls back to identity entries.
    """
    customer = ticket.get("customer") or {}
    if customer.get("email"):
        return customer["email"]
    for ch in customer.get("channels") or []:
        if ch.get("type") == "email" and ch.get("address"):
            return ch["address"]
    for ident in customer.get("identities") or []:
        if ident.get("channel") == "email" and ident.get("address"):
            return ident["address"]
    return ""
