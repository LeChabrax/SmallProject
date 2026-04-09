from mcp.server.fastmcp import FastMCP
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

INSTRUCTIONS = """
This server provides access to Gorgias customer support tickets for Impulse Nutrition.
Use it to search, list and read support tickets and customers.
"""

GORGIAS_DOMAIN = os.getenv("GORGIAS_DOMAIN", "impulse-nutrition-vitavea")
GORGIAS_EMAIL = os.getenv("GORGIAS_EMAIL", "achabrat@havea.com")
GORGIAS_API_KEY = os.getenv("GORGIAS_API_KEY", "")

BASE_URL = f"https://{GORGIAS_DOMAIN}.gorgias.com/api"
AUTH = HTTPBasicAuth(GORGIAS_EMAIL, GORGIAS_API_KEY)

mcp = FastMCP(
    name="Gorgias",
    instructions=INSTRUCTIONS
)


def _get(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a GET request to Gorgias API."""
    resp = requests.get(f"{BASE_URL}/{endpoint}", auth=AUTH, params=params or {})
    resp.raise_for_status()
    return resp.json()


def _post(endpoint: str, payload: Dict) -> Dict[str, Any]:
    """Make a POST request to Gorgias API."""
    resp = requests.post(f"{BASE_URL}/{endpoint}", auth=AUTH, json=payload)
    resp.raise_for_status()
    return resp.json()


def _put(endpoint: str, payload: Dict) -> Dict[str, Any]:
    """Make a PUT request to Gorgias API."""
    resp = requests.put(f"{BASE_URL}/{endpoint}", auth=AUTH, json=payload)
    resp.raise_for_status()
    return resp.json()


def _slim_ticket(t: Dict) -> Dict:
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


def _slim_message(m: Dict) -> Dict:
    source = m.get("source") or {}
    sender = source.get("from") or {}
    body = m.get("body_text") or ""
    if len(body) > 600:
        body = body[:600] + "..."
    return {
        "id": m.get("id"),
        "created_datetime": m.get("created_datetime"),
        "from_agent": m.get("from_agent"),
        "sender": {"name": sender.get("name"), "address": sender.get("address")},
        "body_text": body,
    }


def _slim_customer(c: Dict) -> Dict:
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


@mcp.tool()
def list_tickets(
    limit: int = 30,
    order_by: str = "updated_datetime:desc",
    status: Optional[str] = None,
    channel: Optional[str] = None,
) -> Dict[str, Any]:
    """List recent support tickets.

    Args:
        limit: Number of tickets to return (max 100).
        order_by: Sort order (e.g. "created_datetime:desc", "updated_datetime:desc").
        status: Filter by status: open, closed, snoozed, unresolved.
        channel: Filter by channel: email, chat, facebook, instagram, etc.
    """
    params = {"limit": min(limit, 100), "order_by": order_by}
    if status:
        params["status"] = status
    if channel:
        params["channel"] = channel
    resp = _get("tickets", params)
    return {
        "tickets": [_slim_ticket(t) for t in resp.get("data", [])],
        "total": resp.get("meta", {}).get("total_resources"),
    }


@mcp.tool()
def get_ticket(ticket_id: int) -> Dict[str, Any]:
    """Get full details of a specific ticket.

    Args:
        ticket_id: The Gorgias ticket ID.
    """
    return _slim_ticket(_get(f"tickets/{ticket_id}"))


@mcp.tool()
def list_ticket_messages(ticket_id: int, limit: int = 30) -> Dict[str, Any]:
    """List all messages in a ticket.

    Args:
        ticket_id: The Gorgias ticket ID.
        limit: Number of messages to return.
    """
    resp = _get(f"tickets/{ticket_id}/messages", {"limit": limit})
    return {"messages": [_slim_message(m) for m in resp.get("data", [])]}


@mcp.tool()
def search_tickets(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search tickets by keyword.

    Args:
        query: Search query (searches subject, body, customer name/email).
        limit: Number of results to return.
    """
    resp = _get("search", {"type": "ticket", "query": query, "limit": limit})
    return {
        "tickets": [_slim_ticket(hit.get("object", hit)) for hit in resp.get("data", [])],
        "total": resp.get("meta", {}).get("total_resources"),
    }


@mcp.tool()
def list_customers(limit: int = 30, order_by: str = "updated_datetime:desc") -> Dict[str, Any]:
    """List customers.

    Args:
        limit: Number of customers to return.
        order_by: Sort order.
    """
    resp = _get("customers", {"limit": limit, "order_by": order_by})
    return {"customers": [_slim_customer(c) for c in resp.get("data", [])]}


@mcp.tool()
def get_customer(customer_id: int) -> Dict[str, Any]:
    """Get details of a specific customer.

    Args:
        customer_id: The Gorgias customer ID.
    """
    return _slim_customer(_get(f"customers/{customer_id}"))


@mcp.tool()
def search_customers(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search customers by name or email.

    Args:
        query: Search query.
        limit: Number of results.
    """
    resp = _get("customers", {"limit": limit, "email": query})
    return {"customers": [_slim_customer(c) for c in resp.get("data", [])]}


@mcp.tool()
def get_ticket_stats() -> Dict[str, Any]:
    """Get a summary of ticket counts by status (open, closed, snoozed, unresolved)."""
    results = {}
    for status in ["open", "closed", "snoozed", "unresolved"]:
        resp = _get("tickets", {"limit": 1, "status": status})
        results[status] = resp.get("meta", {}).get("total_resources", "unknown")
    return results


@mcp.tool()
def list_tags() -> Dict[str, Any]:
    """List all available tags in Gorgias."""
    resp = _get("tags", {"limit": 100})
    return [{"id": tag.get("id"), "name": tag.get("name")} for tag in resp.get("data", [])]


@mcp.tool()
def reply_to_ticket(
    ticket_id: int,
    body_text: str,
    close_after: bool = False,
) -> Dict[str, Any]:
    """Send a reply to a ticket from contact@impulse-nutrition.fr.

    Args:
        ticket_id: The Gorgias ticket ID.
        body_text: The plain text body of the reply (will also be sent as HTML with line breaks).
        close_after: If True, close the ticket after sending the reply.
    """
    ticket = _get(f"tickets/{ticket_id}")
    customer = ticket.get("customer", {})
    customer_email = None
    if customer:
        for identity in customer.get("identities", []):
            if identity.get("type") == "email":
                customer_email = identity.get("value")
                break
        if not customer_email:
            customer_email = customer.get("email")

    body_html = body_text.replace("\n", "<br />")

    payload = {
        "ticket_id": ticket_id,
        "channel": "email",
        "via": "helpdesk",
        "from_agent": True,
        "public": True,
        "source": {
            "type": "email",
            "from": {"name": "Contact Impulse-nutrition", "address": "contact@impulse-nutrition.fr"},
            "to": [{"address": customer_email}] if customer_email else [],
        },
        "body_text": body_text,
        "body_html": f"<div>{body_html}</div>",
    }

    result = _post(f"tickets/{ticket_id}/messages", payload)

    closed = False
    if close_after:
        _put(f"tickets/{ticket_id}", {"status": "closed"})
        closed = True

    return {"message_id": result.get("id"), "ticket_id": ticket_id, "ticket_closed": closed}


@mcp.tool()
def close_ticket(ticket_id: int) -> Dict[str, Any]:
    """Close a ticket without sending a reply.

    Args:
        ticket_id: The Gorgias ticket ID.
    """
    _put(f"tickets/{ticket_id}", {"status": "closed"})
    return {"ticket_id": ticket_id, "status": "closed"}


@mcp.tool()
def assign_ticket(ticket_id: int, agent_email: str = "achabrat@havea.com") -> Dict[str, Any]:
    """Assign a ticket to an agent.

    Args:
        ticket_id: The Gorgias ticket ID.
        agent_email: Email of the agent to assign (default: achabrat@havea.com).
    """
    users = _get("users", {"limit": 50})
    agent_id = None
    for user in users.get("data", []):
        if user.get("email") == agent_email:
            agent_id = user.get("id")
            break
    if not agent_id:
        return {"error": f"Agent {agent_email} not found"}
    _put(f"tickets/{ticket_id}", {"assignee_user": {"id": agent_id}})
    return {"ticket_id": ticket_id, "assigned_to": agent_email}


if __name__ == "__main__":
    mcp.run(transport="stdio")
