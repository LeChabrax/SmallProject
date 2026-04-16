#!/usr/bin/env python3
"""Refresh knowledge/catalog.yaml from Shopify.

Fetches the full product catalog via the Shopify Admin API (same auth as
the shopify_mcp server), applies the taxonomie from
`catalog_taxonomy.yaml` (mapping title pattern → moment de consommation),
and writes `knowledge/catalog.yaml`.

Usage
-----
    python3 infra/scripts/refresh_catalog.py            # write
    python3 infra/scripts/refresh_catalog.py --dry-run  # print stats only

Source de vérité : Shopify (SKU, variant_id, prix). Re-run quand tu
ajoutes un produit ou quand la taxonomie change.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TAXONOMY_PATH = Path(__file__).resolve().parent / "catalog_taxonomy.yaml"
OUT_PATH = REPO_ROOT / "knowledge" / "catalog.yaml"


# =========================================================================
# Shopify fetch — réutilise la même auth que shopify_mcp (OAuth access token
# déjà provisionné via le MCP server). On passe par la variable d'env ou on
# relit le fichier de credentials du MCP.
# =========================================================================


def _load_shopify_env() -> Dict[str, str]:
    """Load Shopify credentials — same .env as shopify_mcp."""
    env_path = REPO_ROOT / "shopify_mcp" / ".env"
    creds: Dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip().strip('"').strip("'")
    # Allow override via os.environ
    for k in ("SHOPIFY_DOMAIN", "SHOPIFY_CLIENT_ID", "SHOPIFY_CLIENT_SECRET"):
        if os.environ.get(k):
            creds[k] = os.environ[k]
    for req in ("SHOPIFY_DOMAIN", "SHOPIFY_CLIENT_ID", "SHOPIFY_CLIENT_SECRET"):
        if not creds.get(req):
            print(f"ERROR: {req} manquant dans shopify_mcp/.env ou env", file=sys.stderr)
            sys.exit(1)
    return creds


def _get_access_token(creds: Dict[str, str]) -> str:
    """Client credentials OAuth flow (same as shopify_mcp)."""
    r = requests.post(
        f"https://{creds['SHOPIFY_DOMAIN']}/admin/oauth/access_token",
        data={
            "grant_type": "client_credentials",
            "client_id": creds["SHOPIFY_CLIENT_ID"],
            "client_secret": creds["SHOPIFY_CLIENT_SECRET"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    r.raise_for_status()
    return r.json()["access_token"]


def fetch_products() -> List[Dict[str, Any]]:
    """Return full product list from Shopify Admin REST API (active only)."""
    creds = _load_shopify_env()
    domain = creds["SHOPIFY_DOMAIN"]
    token = _get_access_token(creds)
    url = f"https://{domain}/admin/api/2024-10/products.json"
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    products: List[Dict[str, Any]] = []
    params = {"limit": 250, "status": "active"}
    while True:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        batch = r.json().get("products", [])
        products.extend(batch)
        # Pagination via Link header
        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                next_url = part.split(";")[0].strip().strip("<>")
                break
        if not next_url:
            break
        url = next_url
        params = {}
    return products


# =========================================================================
# Taxonomie — mapping title pattern → moment.
# =========================================================================


def load_taxonomy() -> Dict[str, Any]:
    with TAXONOMY_PATH.open() as f:
        return yaml.safe_load(f)


def classify(title: str, tax: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Return {category, moment} for a product title.

    Priority (bundles checked first because "Pack accessoires - BCAA +
    Shaker" should be a bundle, not an accessoire just because "Shaker"
    is in the name) :
    1. Bundles (patterns match → category=bundle, moment=<bucket>)
    2. Accessoires (patterns match → category=accessoire, moment=null)
    3. Complements (patterns match → category=complement, moment=<bucket>)
    4. Unclassified (category=complement, moment=null)
    """
    tl = title.lower()

    bundles = tax.get("bundles", {}) or {}
    for moment, patterns in bundles.items():
        for pat in patterns or []:
            if pat.lower() in tl:
                return {"category": "bundle", "moment": moment}

    for pat in tax.get("accessoires", []) or []:
        if pat.lower() in tl:
            return {"category": "accessoire", "moment": None}

    complements = tax.get("complements", {}) or {}
    for moment, patterns in complements.items():
        for pat in patterns or []:
            if pat.lower() in tl:
                return {"category": "complement", "moment": moment}

    return {"category": "complement", "moment": None}


# =========================================================================
# Output — knowledge/catalog.yaml
# =========================================================================


def build_entry(product: Dict[str, Any], tax: Dict[str, Any]) -> Dict[str, Any]:
    variants = product.get("variants", []) or []
    first = variants[0] if variants else {}
    cls = classify(product["title"], tax)
    entry: Dict[str, Any] = {
        "title": product["title"],
        "handle": product.get("handle", ""),
        "category": cls["category"],
        "moment": cls["moment"],
        "variant_id": str(first.get("id", "")),
        "sku": first.get("sku") or None,
        "price_eur": float(first["price"]) if first.get("price") else None,
        "page_url": f"https://impulse-nutrition.fr/products/{product.get('handle', '')}",
    }
    # Add all variants if more than one
    if len(variants) > 1:
        entry["variants"] = [
            {
                "variant_id": str(v["id"]),
                "sku": v.get("sku"),
                "title": v.get("title"),
                "price_eur": float(v["price"]) if v.get("price") else None,
            }
            for v in variants
        ]
    return entry


def group_by_moment(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in entries:
        key = e["moment"] or "_unclassified"
        if e["category"] == "accessoire":
            key = "_accessoires"
        groups[key].append(e)
    # Sort alphabetically within each group
    for k in groups:
        groups[k].sort(key=lambda x: x["title"])
    return dict(groups)


MOMENT_ORDER = [
    "avant_effort",
    "pendant_effort",
    "apres_effort",
    "au_quotidien",
    "_accessoires",
    "_unclassified",
]


def render_yaml(groups: Dict[str, List[Dict[str, Any]]]) -> str:
    header = (
        "# Catalogue Impulse Nutrition — AUTO-GÉNÉRÉ\n"
        "# Source : Shopify Admin API (produits actifs uniquement).\n"
        "# Taxonomie : infra/scripts/catalog_taxonomy.yaml\n"
        "# Refresh : python3 infra/scripts/refresh_catalog.py\n"
        f"# Dernière mise à jour : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        "#\n"
        "# Moments de consommation :\n"
        "# - avant_effort   : preworkout, barres protéinées, maltodextrine, BCAA\n"
        "# - pendant_effort : électrolytes, boissons d'effort isotoniques\n"
        "# - apres_effort   : whey isolate, whey recovery\n"
        "# - au_quotidien   : gélules, collagène, glycine, L-glutamine, vitamines, créatine\n"
        "# - _accessoires   : hardware (shaker, bidon, flasque) — pas de moment\n"
        "# - _unclassified  : produit non reconnu par la taxonomie — ajouter un pattern dans catalog_taxonomy.yaml\n"
        "\n"
    )
    out = {}
    for key in MOMENT_ORDER:
        if key in groups:
            out[key] = groups[key]
    # Any group not in MOMENT_ORDER (shouldn't happen) at the end
    for key in sorted(groups):
        if key not in out:
            out[key] = groups[key]
    return header + yaml.safe_dump(
        out, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120
    )


# =========================================================================
# Main
# =========================================================================


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print stats, don't write")
    args = parser.parse_args()

    print("Fetching Shopify products…")
    products = fetch_products()
    print(f"  → {len(products)} produits actifs")

    tax = load_taxonomy()
    entries = [build_entry(p, tax) for p in products]

    # Stats par moment
    stats: Dict[str, int] = defaultdict(int)
    unclassified: List[str] = []
    for e in entries:
        if e["category"] == "accessoire":
            stats["_accessoires"] += 1
        elif e["moment"] is None:
            stats["_unclassified"] += 1
            unclassified.append(e["title"])
        else:
            stats[e["moment"]] += 1

    print("\nRépartition par moment :")
    for key in MOMENT_ORDER:
        if key in stats:
            print(f"  {key:<20} {stats[key]:>3} produits")
    for key in sorted(stats):
        if key not in MOMENT_ORDER:
            print(f"  {key:<20} {stats[key]:>3} produits")

    if unclassified:
        print(f"\n⚠️  {len(unclassified)} produit(s) non classés :")
        for t in unclassified:
            print(f"    - {t}")
        print("  → Ajouter un pattern dans infra/scripts/catalog_taxonomy.yaml")

    if args.dry_run:
        print("\n(dry-run : pas d'écriture)")
        return

    groups = group_by_moment(entries)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render_yaml(groups))
    print(f"\n✓ Écrit : {OUT_PATH.relative_to(REPO_ROOT)} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
