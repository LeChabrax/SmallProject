from mcp.server.fastmcp import FastMCP
import requests
from typing import Optional, Dict, Any, List
import os
import re
import struct
import time
from dotenv import load_dotenv

load_dotenv(override=True)

BIGBLUE_API_KEY = os.getenv("BIGBLUE_API_KEY", "")
_session_token = os.getenv("BIGBLUE_SESSION_TOKEN", "")

AUTH0_CLIENT_ID = "bwjJGmcIeffoDRyuSi9yXNpZZn0AFYPi"
BIGBLUE_EMAIL = "achabrat@havea.com"
SSO_BASE = "https://sso.bigblue.co"
ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")
BASE_URL = "https://api.bigblue.co/bigblue.storeapi.v1.PublicAPI"
HELPDESK_BASE = "https://api.bigblue.co/bigblue.helpdesk.v0.Service"
HEADERS = {
    "Authorization": f"Bearer {BIGBLUE_API_KEY}",
    "Content-Type": "application/json",
}

INSTRUCTIONS = """
This server provides access to Bigblue fulfillment orders for Impulse Nutrition.
Use it to track orders, check delivery status, cancel orders, and manage logistics.
It also provides access to the BigBlue helpdesk to create support tickets (claims)
for missing products, damaged products, wrong deliveries, etc.
All helpdesk messages must be written in French.
"""

mcp = FastMCP(name="Bigblue", instructions=INSTRUCTIONS)


# --- Protobuf helpers for gRPC-web ---

def _encode_varint(value: int) -> bytes:
    result = b""
    while value > 0x7F:
        result += bytes([0x80 | (value & 0x7F)])
        value >>= 7
    result += bytes([value])
    return result


def _encode_string(field_number: int, value: str) -> bytes:
    tag = (field_number << 3) | 2
    encoded = value.encode("utf-8")
    return _encode_varint(tag) + _encode_varint(len(encoded)) + encoded


def _encode_submessage(field_number: int, data: bytes) -> bytes:
    tag = (field_number << 3) | 2
    return _encode_varint(tag) + _encode_varint(len(data)) + data


def _grpc_web_frame(proto_msg: bytes) -> bytes:
    return struct.pack(">BI", 0, len(proto_msg)) + proto_msg


def _grpc_web_post(endpoint: str, proto_msg: bytes) -> bytes:
    """POST to a gRPC-web endpoint using the session token."""
    global _session_token
    headers = {
        "Authorization": f"Bearer {_session_token}",
        "Content-Type": "application/grpc-web+proto",
        "x-grpc-web": "1",
    }
    resp = requests.post(
        f"{HELPDESK_BASE}/{endpoint}",
        headers=headers,
        data=_grpc_web_frame(proto_msg),
    )
    if resp.status_code == 401:
        raise PermissionError("TOKEN_EXPIRED: BigBlue session token has expired. Call trigger_token_refresh() then update_session_token(new_token).")
    resp.raise_for_status()
    body = resp.content
    if len(body) > 5:
        msg_len = struct.unpack(">I", body[1:5])[0]
        return body[5 : 5 + msg_len]
    return b""


def _extract_strings(data: bytes) -> List[str]:
    """Extract readable strings from protobuf binary data."""
    return [s.decode("utf-8") for s in re.findall(rb"[\x20-\x7e]{4,}", data)]


def _post(method: str, payload: Dict = {}) -> Dict[str, Any]:
    """Make a POST request to Bigblue API."""
    resp = requests.post(f"{BASE_URL}/{method}", headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def _find_order_by_ref(reference: str) -> Optional[Dict]:
    """Find an order by store reference (IMPxxxx) by paginating through orders."""
    cursor = None
    for _ in range(20):
        payload: Dict[str, Any] = {"page_size": 100}
        if cursor:
            payload["page_token"] = cursor
        result = _post("ListOrders", payload)
        orders = result.get("orders", [])
        for o in orders:
            ext = (o.get("external_id") or "").lower()
            if reference.lower() in ext:
                return o
        cursor = result.get("next_page_token")
        if not cursor or not orders:
            break
    return None


@mcp.tool()
def get_order(reference: str) -> Dict[str, Any]:
    """Get full details of a specific order by store reference.

    Args:
        reference: The store order reference (e.g. IMP5685).
    """
    order = _find_order_by_ref(reference)
    if order:
        return order
    return {"error": f"Order {reference} not found"}


@mcp.tool()
def list_orders(
    page_size: int = 20,
    page_token: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """List recent Bigblue fulfillment orders.

    Args:
        page_size: Number of orders to return (max 100).
        page_token: Pagination token from previous response.
        status: Filter by status (e.g. PENDING, IN_PREPARATION, SHIPPED, DELIVERED, CANCELLED).
    """
    payload: Dict[str, Any] = {"page_size": min(page_size, 100)}
    if page_token:
        payload["page_token"] = page_token
    if status:
        payload["status"] = status
    return _post("ListOrders", payload)


@mcp.tool()
def get_tracking(reference: str) -> Dict[str, Any]:
    """Get tracking information for an order by store reference.

    Args:
        reference: The store order reference (e.g. IMP5685).
    """
    order = _find_order_by_ref(reference)
    if not order:
        return {"error": f"Order {reference} not found"}
    bigblue_id = order.get("id")
    result = _post("ListTrackings", {"order_id": bigblue_id})
    trackings = result.get("trackings", [])
    if trackings:
        t = trackings[0]
        return {
            "reference": reference,
            "bigblue_id": bigblue_id,
            "carrier": t.get("carrier_service"),
            "tracking_number": t.get("tracking_number"),
            "tracking_url": t.get("tracking_url"),
            "status": t.get("status", {}).get("code"),
            "status_message": t.get("status", {}).get("message"),
            "last_event": t.get("events", [{}])[0] if t.get("events") else {},
            "all_events": t.get("events", []),
        }
    return {"reference": reference, "status": order.get("status", {}).get("code"), "message": "No tracking yet"}


@mcp.tool()
def cancel_order(reference: str) -> Dict[str, Any]:
    """Cancel an order (only possible if not yet shipped).

    Args:
        reference: The store order reference (e.g. IMP5685).
    """
    order = _find_order_by_ref(reference)
    if not order:
        return {"error": f"Order {reference} not found"}
    bigblue_id = order.get("id")
    return _post("CancelOrder", {"order_id": bigblue_id})


@mcp.tool()
def list_inventories(page_size: int = 50) -> Dict[str, Any]:
    """List current inventory levels for all products.

    Args:
        page_size: Number of products to return.
    """
    return _post("ListInventories", {"page_size": min(page_size, 100)})


@mcp.tool()
def update_order(
    reference: str,
    shipping_method: Optional[str] = None,
    pickup_point: Optional[Dict[str, str]] = None,
    shipping_address: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Update an existing order (e.g. change shipping method or pickup point).

    Only works on orders that are still PENDING (not yet shipped).

    Args:
        reference: The store order reference (e.g. IMP6472).
        shipping_method: New shipping method (e.g. "Livraison en point relais", "Expédition gratuite").
        pickup_point: Pickup point info. Example: {"id": "7351Y", "display_name": "SARL FATY PRESSING WILSON", "postal": "92300", "country": "FR", "carrier_service": "chronopost-2shop-direct"}.
        shipping_address: Updated shipping address with keys: first_name, last_name, phone, email, line1, city, postal, country, etc.
    """
    order = _find_order_by_ref(reference)
    if not order:
        return {"error": f"Order {reference} not found"}

    status_code = order.get("status", {}).get("code", "")
    if status_code not in ("PENDING", "EXCEPTION"):
        return {"error": f"Order {reference} has status {status_code} — can only update PENDING or EXCEPTION orders"}

    # Build update payload from existing order + overrides
    updated = {
        "id": order["id"],
        "external_id": order.get("external_id"),
        "store": order.get("store"),
        "language": order.get("language", "fr"),
        "currency": order.get("currency", "EUR"),
        "shipping_address": shipping_address or order.get("shipping_address", {}),
        "line_items": order.get("line_items", []),
        "shipping_price": order.get("shipping_price", "0"),
        "shipping_tax": order.get("shipping_tax", "0"),
        "shipping_method": shipping_method or order.get("shipping_method", ""),
        "total": order.get("total", "0"),
    }

    if pickup_point:
        updated["pickup_point"] = pickup_point

    result = _post("UpdateOrder", {"order": updated})
    return result


# --- Helpdesk tools (gRPC-web, requires BIGBLUE_SESSION_TOKEN) ---

VALID_TOPICS = [
    "Report missing products",
    "Report damaged products",
    "Report the delivery of wrong products",
    "Investigate a delivery never received by the customer",
    "Investigate a delayed order",
]


@mcp.tool()
def list_support_tickets() -> Dict[str, Any]:
    """List all open support tickets on Bigblue helpdesk.

    Requires BIGBLUE_SESSION_TOKEN (Auth0 JWT from dashboard login).
    """
    if not _session_token:
        return {"error": "BIGBLUE_SESSION_TOKEN not set in .env"}
    try:
        proto_msg = bytes([0x30, 0x64])  # page_size = 100
        raw = _grpc_web_post("ListTickets", proto_msg)
        strings = _extract_strings(raw)
        return {"tickets_raw_strings": strings, "byte_count": len(raw)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_support_ticket(ticket_id: str) -> Dict[str, Any]:
    """Get details of a specific support ticket.

    Args:
        ticket_id: The Bigblue ticket ID (e.g. 3C4DhiOaQJk7AGszwephOZ39N12).
    """
    if not _session_token:
        return {"error": "BIGBLUE_SESSION_TOKEN not set in .env"}
    try:
        proto_msg = _encode_string(1, ticket_id)
        raw = _grpc_web_post("GetTicket", proto_msg)
        strings = _extract_strings(raw)
        return {"ticket_raw_strings": strings, "byte_count": len(raw)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_support_ticket(
    order_reference: str,
    topic: str,
    description: str,
    product_ids: Optional[List[str]] = None,
    new_order_reference: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a support ticket (claim) on Bigblue helpdesk.

    IMPORTANT: Always write description in French. Always confirm with the user before calling.

    Args:
        order_reference: The Bigblue order reference (e.g. IMPUS1006357).
        topic: One of: "Report missing products", "Report damaged products",
               "Report the delivery of wrong products",
               "Investigate a delivery never received by the customer",
               "Investigate a delayed order".
        description: Detailed description of the issue in French.
        product_ids: List of Bigblue product IDs concerned (e.g. ["IMPU-016323-XXXX"]).
        new_order_reference: If a replacement order was already created, its reference.
    """
    if not _session_token:
        return {"error": "BIGBLUE_SESSION_TOKEN not set in .env"}
    if topic not in VALID_TOPICS:
        return {"error": f"Invalid topic. Must be one of: {VALID_TOPICS}"}

    try:
        # Build the description text matching BigBlue's expected format
        desc_parts = []
        if product_ids:
            for pid in product_ids:
                desc_parts.append(f"missing product: {pid} - quantity: 1")
        if new_order_reference:
            desc_parts.append(f"New order: {new_order_reference}")
        else:
            desc_parts.append("No new order created.")
        desc_parts.append(f"Comment: {description}")
        full_description = "\n\n".join(desc_parts)

        # Build protobuf message
        # Field mapping (reverse-engineered from captured requests):
        # field 1 = order_reference
        # field 5 = topic
        # field 4 = description
        # field 6 = sub-message with order details
        # field 7 = sub-message with product details
        proto_msg = _encode_string(1, order_reference)
        proto_msg += _encode_string(5, topic)
        proto_msg += _encode_string(4, full_description)

        # Sub-message for order context (field 6)
        order_sub = _encode_string(1, order_reference)
        proto_msg += _encode_submessage(6, order_sub)

        # Sub-message for products (field 7)
        if product_ids:
            for pid in product_ids:
                product_sub = _encode_string(1, pid)
                proto_msg += _encode_submessage(7, product_sub)

        raw = _grpc_web_post("CreateTicket", proto_msg)
        strings = _extract_strings(raw)
        return {
            "success": True,
            "ticket_raw_strings": strings,
            "order_reference": order_reference,
            "topic": topic,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def reply_to_support_ticket(ticket_id: str, message: str) -> Dict[str, Any]:
    """Send a reply message on an existing Bigblue support ticket.

    IMPORTANT: Always write message in French. Always confirm with the user before calling.

    Args:
        ticket_id: The Bigblue ticket ID.
        message: The reply message in French.
    """
    if not _session_token:
        return {"error": "BIGBLUE_SESSION_TOKEN not set in .env"}
    try:
        # Field mapping from captured CreateMessage request:
        # field 1 = ticket_id
        # field 2 = message text (based on the captured body structure)
        proto_msg = _encode_string(1, ticket_id)
        proto_msg += _encode_string(2, message)
        raw = _grpc_web_post("CreateMessage", proto_msg)
        strings = _extract_strings(raw)
        return {"success": True, "message_raw_strings": strings}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def trigger_token_refresh() -> Dict[str, Any]:
    """Trigger a BigBlue magic link email to refresh the session token.

    This sends a passwordless login email to achabrat@havea.com (forwarded to personal Gmail).
    After calling this tool, Claude should:
    1. Search Gmail for the BigBlue auth email (from: noreply@sso.bigblue.co OR sso.bigblue.co)
    2. Extract the magic link URL from the email body
    3. Use Playwright to navigate to the link and capture the JWT from the redirect URL
    4. Call update_session_token(token) with the extracted token
    """
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "connection": "email",
        "email": BIGBLUE_EMAIL,
        "send": "link",
        "authParams": {
            "scope": "openid",
            "response_type": "token id_token",
            "audience": "https://api.bigblue.co",
            "redirect_uri": "https://app.bigblue.co/logincallback",
        },
    }
    try:
        resp = requests.post(
            f"{SSO_BASE}/passwordless/start",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return {
            "success": True,
            "message": f"Magic link sent to {BIGBLUE_EMAIL}. Check Gmail (forwarded from Outlook) and extract the link.",
            "next_step": "Search Gmail for 'from:sso.bigblue.co' or subject 'Sign in to Bigblue', then call update_session_token(token).",
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def update_session_token(token: str) -> Dict[str, Any]:
    """Update the BigBlue session token in memory and in .env file.

    Args:
        token: The new JWT bearer token extracted from the BigBlue magic link redirect.
    """
    global _session_token
    _session_token = token

    # Update .env file
    env_path = os.path.abspath(ENV_FILE)
    try:
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                content = f.read()
            if "BIGBLUE_SESSION_TOKEN=" in content:
                content = re.sub(
                    r"BIGBLUE_SESSION_TOKEN=.*",
                    f"BIGBLUE_SESSION_TOKEN={token}",
                    content,
                )
            else:
                content += f"\nBIGBLUE_SESSION_TOKEN={token}\n"
        else:
            content = f"BIGBLUE_SESSION_TOKEN={token}\n"
        with open(env_path, "w") as f:
            f.write(content)
        return {"success": True, "message": "Token updated in memory and .env file."}
    except Exception as e:
        return {"success": True, "memory_updated": True, "env_error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
