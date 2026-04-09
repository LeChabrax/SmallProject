from mcp.server.fastmcp import FastMCP
import requests
from typing import Optional, Dict, Any, List
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

INSTRUCTIONS = """
Shopify MCP server for Impulse Nutrition store.
Provides draft order creation, order management, and customer lookup.
Use this to create replacement/SAV orders, manage discounts, and look up customers.
"""

SHOPIFY_DOMAIN = os.getenv("SHOPIFY_DOMAIN", "impulse-nutrition.myshopify.com")
SHOPIFY_CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET", "")
API_VERSION = "2024-10"

BASE_URL = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}"

# Token cache
_token_cache = {"access_token": None, "expires_at": 0}


def _get_access_token() -> str:
    """Get or refresh OAuth access token using client credentials flow."""
    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["access_token"]

    resp = requests.post(
        f"https://{SHOPIFY_DOMAIN}/admin/oauth/access_token",
        data={
            "grant_type": "client_credentials",
            "client_id": SHOPIFY_CLIENT_ID,
            "client_secret": SHOPIFY_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 86400) - 120
    return data["access_token"]


def _headers() -> Dict[str, str]:
    return {
        "X-Shopify-Access-Token": _get_access_token(),
        "Content-Type": "application/json",
    }


def _get(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    resp = requests.get(f"{BASE_URL}/{endpoint}", headers=_headers(), params=params or {})
    resp.raise_for_status()
    return resp.json()


def _post(endpoint: str, payload: Dict) -> Dict[str, Any]:
    resp = requests.post(f"{BASE_URL}/{endpoint}", headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def _put(endpoint: str, payload: Dict) -> Dict[str, Any]:
    resp = requests.put(f"{BASE_URL}/{endpoint}", headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def _delete(endpoint: str) -> Dict[str, Any]:
    resp = requests.delete(f"{BASE_URL}/{endpoint}", headers=_headers())
    resp.raise_for_status()
    if resp.content:
        return resp.json()
    return {"status": "deleted"}


mcp = FastMCP(
    name="Shopify",
    instructions=INSTRUCTIONS,
)


# ── Draft Orders ──────────────────────────────────────────────


@mcp.tool()
def create_draft_order(
    line_items: List[Dict[str, Any]],
    customer_email: Optional[str] = None,
    customer_id: Optional[int] = None,
    shipping_address: Optional[Dict[str, str]] = None,
    note: Optional[str] = None,
    tags: Optional[str] = None,
    use_customer_default_address: bool = True,
) -> Dict[str, Any]:
    """Create a draft order (e.g. for SAV replacement, gifting, etc.).

    Args:
        line_items: List of items. Each item can be:
            - {"variant_id": 123, "quantity": 1} for existing products
            - {"title": "Custom item", "price": "0.00", "quantity": 1} for custom line items
        customer_email: Customer email to look up and attach.
        customer_id: Shopify customer ID (alternative to email).
        shipping_address: Shipping address dict with keys: first_name, last_name, address1, city, zip, country_code, etc.
        note: Internal note on the order.
        tags: Comma-separated tags (e.g. "SAV,replacement").
        use_customer_default_address: If True and no shipping_address, use customer's default address.
    """
    draft = {"line_items": line_items}

    if customer_id:
        draft["customer"] = {"id": customer_id}
    elif customer_email:
        draft["customer"] = {"email": customer_email}

    if shipping_address:
        draft["shipping_address"] = shipping_address
    elif use_customer_default_address:
        draft["use_customer_default_address"] = True

    if note:
        draft["note"] = note
    if tags:
        draft["tags"] = tags

    return _post("draft_orders.json", {"draft_order": draft})


@mcp.tool()
def update_draft_order(
    draft_order_id: int,
    applied_discount: Optional[Dict[str, str]] = None,
    shipping_line: Optional[Dict[str, str]] = None,
    tags: Optional[str] = None,
    note: Optional[str] = None,
    shipping_address: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Update a draft order (e.g. apply discount, change shipping, update tags).

    Args:
        draft_order_id: The draft order ID.
        applied_discount: Discount to apply. Example: {"title": "SAV", "value_type": "percentage", "value": "100.0", "description": "Renvoi SAV"}.
        shipping_line: Shipping method. Example: {"title": "Expédition gratuite", "price": "0.00"}.
        tags: Tags string (e.g. "Service client").
        note: Internal note.
        shipping_address: Updated shipping address.
    """
    draft = {"id": draft_order_id}
    if applied_discount:
        draft["applied_discount"] = applied_discount
    if shipping_line:
        draft["shipping_line"] = shipping_line
    if tags is not None:
        draft["tags"] = tags
    if note is not None:
        draft["note"] = note
    if shipping_address:
        draft["shipping_address"] = shipping_address
    return _put(f"draft_orders/{draft_order_id}.json", {"draft_order": draft})


@mcp.tool()
def complete_draft_order(
    draft_order_id: int,
    payment_pending: bool = False,
) -> Dict[str, Any]:
    """Complete a draft order (convert it to a real order).

    Args:
        draft_order_id: The draft order ID.
        payment_pending: If True, mark payment as pending. If False, mark as paid.
    """
    return _put(
        f"draft_orders/{draft_order_id}/complete.json",
        {"payment_pending": payment_pending},
    )


@mcp.tool()
def list_draft_orders(
    limit: int = 20,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """List draft orders.

    Args:
        limit: Number of draft orders to return (max 250).
        status: Filter by status: open, invoice_sent, completed.
    """
    params = {"limit": min(limit, 250)}
    if status:
        params["status"] = status
    return _get("draft_orders.json", params)


@mcp.tool()
def get_draft_order(draft_order_id: int) -> Dict[str, Any]:
    """Get details of a specific draft order.

    Args:
        draft_order_id: The draft order ID.
    """
    return _get(f"draft_orders/{draft_order_id}.json")


@mcp.tool()
def delete_draft_order(draft_order_id: int) -> Dict[str, Any]:
    """Delete a draft order.

    Args:
        draft_order_id: The draft order ID.
    """
    return _delete(f"draft_orders/{draft_order_id}.json")


# ── Orders ────────────────────────────────────────────────────


@mcp.tool()
def get_order(order_id: int) -> Dict[str, Any]:
    """Get details of a specific order.

    Args:
        order_id: The Shopify order ID.
    """
    return _get(f"orders/{order_id}.json")


@mcp.tool()
def list_orders(
    limit: int = 20,
    status: str = "any",
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """List orders.

    Args:
        limit: Number of orders (max 250).
        status: Filter: any, open, closed, cancelled.
        name: Filter by order name/number (e.g. "IMP6058").
    """
    params = {"limit": min(limit, 250), "status": status}
    if name:
        params["name"] = name
    return _get("orders.json", params)


@mcp.tool()
def search_orders(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search orders by query string.

    Args:
        query: Search query (e.g. email, order number, customer name).
        limit: Number of results.
    """
    return _get("orders.json", {"limit": limit, "status": "any", "name": query})


# ── Customers ─────────────────────────────────────────────────


@mcp.tool()
def search_customers(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search customers by name, email, or phone.

    Args:
        query: Search query.
        limit: Number of results.
    """
    return _get("customers/search.json", {"query": query, "limit": limit})


@mcp.tool()
def get_customer(customer_id: int) -> Dict[str, Any]:
    """Get customer details including addresses.

    Args:
        customer_id: The Shopify customer ID.
    """
    return _get(f"customers/{customer_id}.json")


# ── Products ──────────────────────────────────────────────────


@mcp.tool()
def search_products(title: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Search products by title.

    Args:
        title: Product title to search for.
        limit: Number of results.
    """
    params = {"limit": min(limit, 250)}
    if title:
        params["title"] = title
    return _get("products.json", params)


@mcp.tool()
def get_product(product_id: int) -> Dict[str, Any]:
    """Get product details including variants.

    Args:
        product_id: The Shopify product ID.
    """
    return _get(f"products/{product_id}.json")


@mcp.tool()
def get_product_variants(product_id: int) -> Dict[str, Any]:
    """Get all variants for a product (useful to find variant_id for draft orders).

    Args:
        product_id: The Shopify product ID.
    """
    return _get(f"products/{product_id}/variants.json")


# ── Discount Codes ────────────────────────────────────────────


@mcp.tool()
def create_discount_code(
    title: str,
    code: str,
    value: float,
    value_type: str = "percentage",
    usage_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a discount code via a price rule.

    Args:
        title: Internal name for the price rule.
        code: The discount code customers will use (e.g. "ACHAB25").
        value: Discount value (negative for discounts, e.g. -25.0 for 25% off).
        value_type: "percentage" or "fixed_amount".
        usage_limit: Max number of uses (None = unlimited).
    """
    price_rule = {
        "price_rule": {
            "title": title,
            "target_type": "line_item",
            "target_selection": "all",
            "allocation_method": "across",
            "value_type": value_type,
            "value": str(value),
            "customer_selection": "all",
            "starts_at": "2020-01-01T00:00:00Z",
        }
    }
    if usage_limit:
        price_rule["price_rule"]["usage_limit"] = usage_limit

    rule_resp = _post("price_rules.json", price_rule)
    rule_id = rule_resp["price_rule"]["id"]

    code_resp = _post(
        f"price_rules/{rule_id}/discount_codes.json",
        {"discount_code": {"code": code}},
    )
    return {
        "price_rule": rule_resp["price_rule"],
        "discount_code": code_resp["discount_code"],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
