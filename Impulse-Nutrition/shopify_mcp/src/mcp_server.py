from mcp.server.fastmcp import FastMCP
import requests
from typing import Optional, Dict, Any, List
import os
import time
import logging
from datetime import datetime, timezone
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


def _graphql(query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
    resp = requests.post(
        f"{BASE_URL}/graphql.json",
        headers=_headers(),
        json={"query": query, "variables": variables or {}},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data


def _set_combines_with(
    price_rule_id: int,
    order_discounts: bool,
    product_discounts: bool,
    shipping_discounts: bool,
) -> Dict[str, Any]:
    mutation = """
    mutation($id: ID!, $combines: DiscountCombinesWithInput!) {
      discountCodeBasicUpdate(
        id: $id,
        basicCodeDiscount: { combinesWith: $combines }
      ) {
        codeDiscountNode { id }
        userErrors { field message }
      }
    }
    """
    result = _graphql(
        mutation,
        {
            "id": f"gid://shopify/DiscountCodeNode/{price_rule_id}",
            "combines": {
                "orderDiscounts": order_discounts,
                "productDiscounts": product_discounts,
                "shippingDiscounts": shipping_discounts,
            },
        },
    )
    user_errors = (
        result.get("data", {})
        .get("discountCodeBasicUpdate", {})
        .get("userErrors", [])
    )
    if user_errors:
        raise RuntimeError(f"discountCodeBasicUpdate userErrors: {user_errors}")
    return result


# ============================================================================
# Slim helpers — used by tools with `compact=True` (default).
#
# Shopify REST objects are extremely verbose (each variant has 30+ fields,
# orders carry full client_details, presentment_money copies, taxes lines, …).
# The slim helpers below keep ONLY the fields actually used downstream by
# Antoine's pipeline (draft orders, SAV, dotation tagging, code lookups).
#
# Pass `compact=False` on any tool to get the full Shopify payload back —
# useful for debug or for rare cases where a non-essential field matters.
# ============================================================================


def _slim_variant(v: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": v.get("id"),
        "product_id": v.get("product_id"),
        "title": v.get("title"),
        "sku": v.get("sku"),
        "price": v.get("price"),
        "compare_at_price": v.get("compare_at_price"),
        "inventory_quantity": v.get("inventory_quantity"),
        "option1": v.get("option1"),
        "option2": v.get("option2"),
        "option3": v.get("option3"),
    }


def _slim_product(p: Dict[str, Any]) -> Dict[str, Any]:
    variants = p.get("variants") or []
    return {
        "id": p.get("id"),
        "title": p.get("title"),
        "handle": p.get("handle"),
        "product_type": p.get("product_type"),
        "vendor": p.get("vendor"),
        "status": p.get("status"),
        "tags": p.get("tags"),
        "variants": [_slim_variant(v) for v in variants],
    }


def _slim_address(a: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not a:
        return None
    return {
        "name": a.get("name"),
        "first_name": a.get("first_name"),
        "last_name": a.get("last_name"),
        "address1": a.get("address1"),
        "address2": a.get("address2"),
        "city": a.get("city"),
        "province": a.get("province"),
        "zip": a.get("zip"),
        "country": a.get("country"),
        "country_code": a.get("country_code"),
        "phone": a.get("phone"),
        "company": a.get("company"),
    }


def _slim_line_item(li: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": li.get("id"),
        "variant_id": li.get("variant_id"),
        "product_id": li.get("product_id"),
        "title": li.get("title"),
        "variant_title": li.get("variant_title"),
        "sku": li.get("sku"),
        "quantity": li.get("quantity"),
        "price": li.get("price"),
        "total_discount": li.get("total_discount"),
    }


def _slim_order(o: Dict[str, Any]) -> Dict[str, Any]:
    """Compact a full Shopify order payload to ~12 fields actually used."""
    return {
        "id": o.get("id"),
        "name": o.get("name"),
        "created_at": o.get("created_at"),
        "updated_at": o.get("updated_at"),
        "financial_status": o.get("financial_status"),
        "fulfillment_status": o.get("fulfillment_status"),
        "total_price": o.get("total_price"),
        "currency": o.get("currency"),
        "tags": o.get("tags"),
        "note": o.get("note"),
        "email": o.get("email"),
        "customer": _slim_customer(o.get("customer")) if o.get("customer") else None,
        "shipping_address": _slim_address(o.get("shipping_address")),
        "line_items": [_slim_line_item(li) for li in (o.get("line_items") or [])],
        "discount_codes": o.get("discount_codes"),
        "discount_applications": [
            {
                "title": d.get("title"),
                "code": d.get("code"),
                "value": d.get("value"),
                "value_type": d.get("value_type"),
            }
            for d in (o.get("discount_applications") or [])
        ],
        "refunds_count": len(o.get("refunds") or []),
    }


def _slim_customer(c: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not c:
        return None
    return {
        "id": c.get("id"),
        "email": c.get("email"),
        "first_name": c.get("first_name"),
        "last_name": c.get("last_name"),
        "phone": c.get("phone"),
        "tags": c.get("tags"),
        "orders_count": c.get("orders_count"),
        "total_spent": c.get("total_spent"),
        "default_address": _slim_address(c.get("default_address")),
    }


def _maybe_slim(payload: Any, slimmer, key: str, compact: bool) -> Any:
    """Apply `slimmer` to `payload[key]` (or a list at `payload[key+'s']`)
    when `compact=True`. Returns the original payload structure shape so
    callers don't need to change."""
    if not compact or not isinstance(payload, dict):
        return payload
    if key in payload and isinstance(payload[key], dict):
        return {key: slimmer(payload[key])}
    plural = key + "s"
    if plural in payload and isinstance(payload[plural], list):
        return {plural: [slimmer(item) for item in payload[plural]]}
    return payload


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
    """Create a draft order (SAV replacement, dotation envoi, gift).

    This is the entry point of the canonical SAV replacement flow documented
    in `knowledge/process/sav_unified.md`. After creating the draft, call
    `update_draft_order` to apply the mandatory SAV defaults
    (discount 100 %, shipping gratuit, tag `Service client`), then
    `complete_draft_order` to convert it to a real order.

    Args:
        line_items: List of line-item dicts. Each may be:
            - `{"variant_id": 123, "quantity": 1}` — existing product variant.
            - `{"title": "Custom", "price": "0.00", "quantity": 1}` — custom line item.
        customer_email: Email to look up the customer.
        customer_id: Shopify customer ID (alternative to email).
        shipping_address: Full address dict (`first_name`, `last_name`,
            `address1`, `city`, `zip`, `country_code`, `phone`, …).
        note: Internal note — always include the original order reference and
            the SAV reason (e.g. "Replacement IMP4938 — Chronopost bloqué").
        tags: Comma-separated. For SAV cases use `Service client`, for
            dotation use `Dotation influenceur`.
        use_customer_default_address: If True and no explicit address, defer
            to the customer's saved default.

    Returns:
        `{"draft_order": {...}}` as returned by Shopify. The draft ID is
        `draft_order["draft_order"]["id"]`.

    Example — SAV replacement draft:

        draft = create_draft_order(
            line_items=[
                {"variant_id": 51956593230155, "quantity": 1},  # Shaker 450ml
                {"variant_id": 51956610367819, "quantity": 1},  # Bidon 750ml
            ],
            customer_email="alex@example.com",
            note="Replacement IMP4938 — colis bloqué Chronopost",
            tags="Service client",
        )
        draft_id = draft["draft_order"]["id"]
        update_draft_order(
            draft_id,
            applied_discount={"title": "SAV", "value_type": "percentage",
                              "value": "100.0", "description": "SAV"},
            shipping_line={"title": "Expédition gratuite", "price": "0.00"},
        )
        complete_draft_order(draft_id)

    Limitation: `update_draft_order` cannot modify `line_items`. If you need
    to add or remove a product after creation, delete the draft and recreate
    it with the full set of line items.
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
def get_order(order_id: int, compact: bool = True) -> Dict[str, Any]:
    """Get details of a specific order.

    Args:
        order_id: The Shopify order ID.
        compact: If True (default), return only the ~12 fields actually used
            (id, name, status, totals, tags, line_items slim, customer slim).
            Pass False to get the full Shopify payload (~80 fields).
    """
    return _maybe_slim(_get(f"orders/{order_id}.json"), _slim_order, "order", compact)


@mcp.tool()
def list_orders(
    limit: int = 20,
    status: str = "any",
    name: Optional[str] = None,
    compact: bool = True,
) -> Dict[str, Any]:
    """List orders.

    Args:
        limit: Number of orders (max 250).
        status: Filter: any, open, closed, cancelled.
        name: Filter by order name/number (e.g. "IMP6058").
        compact: If True (default), return slimmed orders. False = full payload.
    """
    params = {"limit": min(limit, 250), "status": status}
    if name:
        params["name"] = name
    return _maybe_slim(_get("orders.json", params), _slim_order, "order", compact)


@mcp.tool()
def search_orders(query: str, limit: int = 20, compact: bool = True) -> Dict[str, Any]:
    """Search orders by name (order number).

    Shopify's REST `orders.json?name=` matches the `name` field of the order,
    which is typically the order number prefixed by the store prefix (e.g.
    `IMP6923`). It does NOT search across email, customer name, or line items
    — use `search_customers` then `get_order` for broader lookups.

    Args:
        query: Order name/number (e.g. `IMP6923`, with or without `#`).
        limit: Max results (capped at 250 by Shopify).
        compact: If True (default), return slimmed orders.

    Returns:
        `{"orders": [...]}` as returned by Shopify (slimmed if compact=True).
    """
    return _maybe_slim(
        _get("orders.json", {"limit": limit, "status": "any", "name": query}),
        _slim_order,
        "order",
        compact,
    )


# ── Customers ─────────────────────────────────────────────────


@mcp.tool()
def search_customers(query: str, limit: int = 10, compact: bool = True) -> Dict[str, Any]:
    """Search customers by name, email, or phone.

    Args:
        query: Search query.
        limit: Number of results.
        compact: If True (default), return slimmed customers.
    """
    return _maybe_slim(
        _get("customers/search.json", {"query": query, "limit": limit}),
        _slim_customer,
        "customer",
        compact,
    )


@mcp.tool()
def get_customer(customer_id: int, compact: bool = True) -> Dict[str, Any]:
    """Get customer details including addresses.

    Args:
        customer_id: The Shopify customer ID.
        compact: If True (default), return slimmed customer.
    """
    return _maybe_slim(
        _get(f"customers/{customer_id}.json"),
        _slim_customer,
        "customer",
        compact,
    )


# ── Products ──────────────────────────────────────────────────


@mcp.tool()
def search_products(
    title: Optional[str] = None,
    limit: int = 20,
    compact: bool = True,
) -> Dict[str, Any]:
    """Search products by title.

    Args:
        title: Product title to search for.
        limit: Number of results.
        compact: If True (default), return slim products (id, title, sku,
            price, status, slim variants — 8 fields/product). False = full
            Shopify payload (~50 fields/product, 30+ fields/variant).
    """
    params = {"limit": min(limit, 250)}
    if title:
        params["title"] = title
    return _maybe_slim(_get("products.json", params), _slim_product, "product", compact)


@mcp.tool()
def list_products_compact(limit: int = 250) -> Dict[str, Any]:
    """List the entire active Impulse Nutrition catalog in a flat compact form.

    Convenience tool that returns one slim variant per product, perfect for
    looking up a `variant_id` to drop into `create_draft_order(line_items=…)`.
    Use this instead of paginating through `search_products` when you want a
    quick scan of the whole catalog (~96 products × ~10 fields each).

    Args:
        limit: Max products to return (capped at 250 by Shopify in one page).

    Returns:
        `{"products": [{"id": ..., "title": ..., "variants": [...]}, ...]}`
    """
    raw = _get("products.json", {"limit": min(limit, 250), "status": "active"})
    return {"products": [_slim_product(p) for p in raw.get("products", [])]}


@mcp.tool()
def get_product(product_id: int, compact: bool = True) -> Dict[str, Any]:
    """Get product details including variants.

    Args:
        product_id: The Shopify product ID.
        compact: If True (default), return a slim product (10 fields + slim variants).
    """
    return _maybe_slim(
        _get(f"products/{product_id}.json"),
        _slim_product,
        "product",
        compact,
    )


@mcp.tool()
def get_product_variants(product_id: int, compact: bool = True) -> Dict[str, Any]:
    """Get all variants for a product (useful to find variant_id for draft orders).

    Args:
        product_id: The Shopify product ID.
        compact: If True (default), return slimmed variants.
    """
    raw = _get(f"products/{product_id}/variants.json")
    if not compact or not isinstance(raw, dict):
        return raw
    if "variants" in raw and isinstance(raw["variants"], list):
        return {"variants": [_slim_variant(v) for v in raw["variants"]]}
    return raw


# ── Discount Codes ────────────────────────────────────────────


def _create_affiliate_code(name: str, percent: float) -> Dict[str, Any]:
    """Internal — clone of the ALEXTV pattern. Used by the two affiliate tools."""
    starts_at = datetime.now(timezone.utc).isoformat()
    rule_resp = _post(
        "price_rules.json",
        {
            "price_rule": {
                "title": name,
                "value_type": "percentage",
                "value": str(percent),
                "customer_selection": "all",
                "target_type": "line_item",
                "target_selection": "all",
                "allocation_method": "across",
                "starts_at": starts_at,
                "ends_at": None,
                "usage_limit": None,
                "once_per_customer": True,
            }
        },
    )
    rule_id = rule_resp["price_rule"]["id"]
    code_resp = _post(
        f"price_rules/{rule_id}/discount_codes.json",
        {"discount_code": {"code": name}},
    )
    _set_combines_with(
        rule_id,
        order_discounts=False,
        product_discounts=True,
        shipping_discounts=True,
    )
    return {
        "price_rule": rule_resp["price_rule"],
        "discount_code": code_resp["discount_code"],
        "combines_with": {
            "orderDiscounts": False,
            "productDiscounts": True,
            "shippingDiscounts": True,
        },
    }


@mcp.tool()
def create_affiliate_code(name: str) -> Dict[str, Any]:
    """Create an ambassador affiliate discount code (clone of ALEXTV pattern).

    Canonical Impulse Nutrition ambassador code: -15% percentage, unlimited uses,
    once_per_customer=true, starts now, no end date, combinesWith order=false /
    product=true / shipping=true. This is THE pattern for every Suivi_Amb
    ambassador — see knowledge/process/create_codes.md §1.

    Args:
        name: The code name (will be uppercased — e.g. "florine" -> "FLORINE").
    """
    return _create_affiliate_code(name=name.upper(), percent=-15.0)


@mcp.tool()
def create_paid_affiliate_code(name: str, percent: float = -20.0) -> Dict[str, Any]:
    """Create a paid-contract affiliate discount code (clone of LRA20 pattern).

    Same as create_affiliate_code but with a configurable percentage (default
    -20%) for paid partnership contracts. See knowledge/process/create_codes.md §1
    table §6.

    Args:
        name: The code name (will be uppercased).
        percent: Discount value, negative (default -20.0 = 20% off). A positive
            value will be auto-flipped to negative.
    """
    if percent > 0:
        percent = -percent
    return _create_affiliate_code(name=name.upper(), percent=percent)


@mcp.tool()
def create_discount_code(
    title: str,
    code: str,
    value: float,
    value_type: str = "percentage",
    usage_limit: Optional[int] = None,
    once_per_customer: bool = False,
    starts_at: Optional[str] = None,
    ends_at: Optional[str] = None,
    combines_order_discounts: bool = False,
    combines_product_discounts: bool = True,
    combines_shipping_discounts: bool = True,
) -> Dict[str, Any]:
    """Create a generic discount code via a price rule.

    For the canonical -15% ambassador pattern (ALEXTV), prefer
    `create_affiliate_code(name)` which auto-locks all the right fields. Use
    this generic tool for SAV, dotation, credit, welcome (-25%) or one-off
    custom codes.

    Args:
        title: Internal name for the price rule.
        code: The discount code customers will use (e.g. "ACHAB25").
        value: Discount value (negative for discounts, e.g. -25.0).
        value_type: "percentage" or "fixed_amount".
        usage_limit: Max number of uses (None = unlimited).
        once_per_customer: Limit to one redemption per customer (default False).
        starts_at: ISO datetime; defaults to now if omitted.
        ends_at: Optional ISO datetime end date.
        combines_order_discounts: Combine with other order-level discounts.
        combines_product_discounts: Combine with product discounts.
        combines_shipping_discounts: Combine with shipping discounts.
    """
    rule_payload = {
        "price_rule": {
            "title": title,
            "target_type": "line_item",
            "target_selection": "all",
            "allocation_method": "across",
            "value_type": value_type,
            "value": str(value),
            "customer_selection": "all",
            "starts_at": starts_at or datetime.now(timezone.utc).isoformat(),
            "once_per_customer": once_per_customer,
        }
    }
    if usage_limit is not None:
        rule_payload["price_rule"]["usage_limit"] = usage_limit
    if ends_at is not None:
        rule_payload["price_rule"]["ends_at"] = ends_at

    rule_resp = _post("price_rules.json", rule_payload)
    rule_id = rule_resp["price_rule"]["id"]

    code_resp = _post(
        f"price_rules/{rule_id}/discount_codes.json",
        {"discount_code": {"code": code}},
    )

    _set_combines_with(
        rule_id,
        order_discounts=combines_order_discounts,
        product_discounts=combines_product_discounts,
        shipping_discounts=combines_shipping_discounts,
    )

    return {
        "price_rule": rule_resp["price_rule"],
        "discount_code": code_resp["discount_code"],
        "combines_with": {
            "orderDiscounts": combines_order_discounts,
            "productDiscounts": combines_product_discounts,
            "shippingDiscounts": combines_shipping_discounts,
        },
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
