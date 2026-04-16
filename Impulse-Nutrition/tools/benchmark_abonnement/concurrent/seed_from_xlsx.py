"""
Seed whey_catalog.json from the Vitavea xlsx backport + Impulse Nutrition.

Reads: ../benchmark_whey_vitavea.xlsx
Writes: ./whey_catalog.json

Vitavea columns (B, C) are intentionally skipped — Vitavea is not in the final benchmark.
Impulse data comes from Shopify MCP pricing + manual grammage from impulse-nutrition.fr.
"""

import json
import os
import re
from datetime import date
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
XLSX = HERE.parent / "benchmark_whey_vitavea.xlsx"
OUT = HERE / "whey_catalog.json"
SNAPSHOT = str(date.today())


def parse_number(value, default=None):
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).replace(",", ".")
    s = re.sub(r"(?<=\d)[\s\u00a0](?=\d)", "", s)
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else default


def normalize_type(raw):
    if not raw:
        return None
    s = raw.lower()
    is_native = "natif" in s or "native" in s
    is_hydrol = "hydrol" in s or "clear" in s
    is_iso = "isolat" in s or "iso" in s
    is_concentrate = "concentrat" in s and "+" not in s and "iso" not in s
    is_mix = "mix" in s or ("+" in s)
    if is_hydrol:
        return "clear_hydrolysat"
    if is_mix:
        return "mix_concentrat_isolat"
    if is_iso and is_native:
        return "isolat_natif"
    if is_concentrate and is_native:
        return "concentrat_natif"
    if is_iso:
        return "isolat_fromagere"
    if is_concentrate:
        return "concentrat_fromagere"
    return s.strip()


def native_vs_fromagere(raw_whey_native):
    if not raw_whey_native:
        return None
    return "native" if "nativ" in raw_whey_native.lower() else "fromagere"


def lactose_level(raw):
    if not raw:
        return None
    s = raw.lower()
    if "<" in s or "très faible" in s or "sl" in s:
        return "tres_faible"
    if "faible" in s or "low" in s:
        return "faible"
    if "présent" in s or "present" in s:
        return "present"
    return s.strip()


def parse_certifications(raw):
    if not raw:
        return []
    return [c.strip() for c in re.split(r"[,/]", raw) if c.strip()]


def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def build_product_id(brand, product_name, format_g, flavor):
    return f"{slugify(brand)}_{slugify(product_name)}_{int(format_g)}g_{slugify(flavor)}"


BRAND_CODE_BY_COLUMN = {
    # Vitavea (B, C) skipped — not in benchmark
    "D": ("nutripure", "Whey Isolat Native 750g", "chocolat", "https://www.nutripure.fr/produits/whey-isolat-native-chocolat"),
    "E": ("nutripure", "Whey Isolat Native 2kg", "chocolat", "https://www.nutripure.fr/produits/whey-isolat-native-chocolat"),
    "F": ("nutrimuscle", "Whey Native Concentrat", "chocolat", "https://www.nutrimuscle.com/products/whey-concentree-native"),
    "G": ("nutrimuscle", "Whey Native Isolate", "chocolat", "https://www.nutrimuscle.com/products/whey-isolat-native"),
    "H": ("nutrimuscle", "Musclewhey (Mix Conc+Iso)", "chocolat", "https://www.nutrimuscle.com/products/musclewhey"),
    "I": ("myprotein", "Impact Whey Protein 1kg", "chocolat", "https://www.myprotein.fr/fr/p/nutrition-sportive/impact-whey-protein/10530943/"),
    "J": ("myprotein", "Impact Whey Protein 2,5kg", "chocolat", "https://www.myprotein.fr/fr/p/nutrition-sportive/impact-whey-protein/10530943/"),
    "K": ("myprotein", "Impact Whey Protein 5kg", "chocolat", "https://www.myprotein.fr/fr/p/nutrition-sportive/impact-whey-protein/10530943/"),
    "L": ("myprotein", "Impact Whey Isolate 1kg", "chocolat", "https://www.myprotein.fr/fr/p/nutrition-sportive/impact-whey-isolate/10852482/"),
    "M": ("myprotein", "Impact Whey Isolate 2,5kg", "chocolat", "https://www.myprotein.fr/fr/p/nutrition-sportive/impact-whey-isolate/10852482/"),
    "N": ("myprotein", "Clear Whey Isolate 1kg", "fraise", "https://www.myprotein.fr/fr/p/nutrition-sportive/clear-whey-isolate/12377069/"),
    "O": ("bulk", "Pure Whey Protein 1kg", "chocolat", "https://www.bulk.com/fr/pure-whey-protein-1.html"),
    "P": ("bulk", "Pure Whey Protein 2,5kg", "chocolat", "https://www.bulk.com/fr/pure-whey-protein-1.html"),
    "Q": ("bulk", "Pure Whey Protein 5kg", "chocolat", "https://www.bulk.com/fr/pure-whey-protein-1.html"),
    "R": ("bulk", "Pure Whey Isolate 1kg", "chocolat", "https://www.bulk.com/fr/pure-whey-isolate-90.html"),
    "S": ("bulk", "Pure Whey Isolate 2,5kg", "chocolat", "https://www.bulk.com/fr/pure-whey-isolate-90.html"),
    "T": ("bulk", "Clear Whey Isolate 500g", "fraise", "https://www.bulk.com/fr/clear-whey-isolate.html"),
    "U": ("decathlon", "Whey Protein 900g (Concentrat)", "chocolat", "https://www.decathlon.fr/p/mp/corength/whey-chocolat-corength/_/R-p-336437"),
    "V": ("decathlon", "Pure Whey 100% Isolate 900g", "chocolat", "https://www.decathlon.fr/p/mp/corength/whey-isolate-chocolat/_/R-p-336438"),
}

ROW_FIELDS = {
    4: "type_raw",
    5: "format_g",
    6: "flavors_available_raw",
    8: "protein_pct_100g",
    9: "protein_per_serving_g",
    10: "serving_size_g",
    11: "servings_per_pack",
    12: "bcaa_per_serving_g",
    13: "carbs_per_serving_g",
    14: "fat_per_serving_g",
    15: "whey_native_raw",
    16: "lactose_raw",
    17: "certifications_raw",
    18: "origin_milk",
    20: "price_catalog_ttc_eur",
    24: "channels_raw",
}


def load_xlsx():
    wb = openpyxl.load_workbook(XLSX, data_only=False)
    ws = wb["Benchmark Whey Concurrents"]
    products = []
    for col_letter, (brand, product_name, flavor, source_url) in BRAND_CODE_BY_COLUMN.items():
        cells = {field: ws[f"{col_letter}{row}"].value for row, field in ROW_FIELDS.items()}

        format_g = parse_number(cells["format_g"])
        if not format_g:
            continue

        entry = {
            "brand": brand,
            "product_id": build_product_id(brand, product_name, format_g, flavor),
            "product_name": product_name,
            "type": normalize_type(cells["type_raw"]),
            "native_vs_fromagere": native_vs_fromagere(cells["whey_native_raw"]),
            "format_g": int(format_g),
            "flavor": flavor,
            "flavors_available_sample": [f.strip() for f in re.split(r"[,/]", str(cells["flavors_available_raw"] or "")) if f.strip()][:5],
            "origin_milk": cells["origin_milk"],
            "certifications": parse_certifications(cells["certifications_raw"]),
            "protein_pct_100g": parse_number(cells["protein_pct_100g"]),
            "protein_per_serving_g": parse_number(cells["protein_per_serving_g"]),
            "serving_size_g": parse_number(cells["serving_size_g"]),
            "servings_per_pack": parse_number(cells["servings_per_pack"]),
            "bcaa_per_serving_g": parse_number(cells["bcaa_per_serving_g"]),
            "carbs_per_serving_g": parse_number(cells["carbs_per_serving_g"]),
            "fat_per_serving_g": parse_number(cells["fat_per_serving_g"]),
            "lactose_level": lactose_level(cells["lactose_raw"]),
            "price_catalog_ttc_eur": parse_number(cells["price_catalog_ttc_eur"]),
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": [c.strip() for c in re.split(r"[,/]", str(cells["channels_raw"] or "")) if c.strip()],
            "source_url": source_url,
            "snapshot_date": SNAPSHOT,
            "source": "xlsx_vitavea_backport",
        }
        products.append(entry)
    return products


def impulse_products():
    """Hardcoded from Shopify MCP lookup + impulse-nutrition.fr.

    Grammage Impulse Whey Isolate = 750g (verifié manuellement via site).
    Format portion individuelle 30g ignoré (hors périmètre benchmark multi-format).
    """
    base = {
        "brand": "impulse_nutrition",
        "type": "isolat_natif",
        "native_vs_fromagere": "native",
        "format_g": 750,
        "origin_milk": "France",
        "certifications": [],
        "protein_pct_100g": 85.0,
        "protein_per_serving_g": 25.5,
        "serving_size_g": 30,
        "servings_per_pack": 25,
        "bcaa_per_serving_g": 5.3,
        "carbs_per_serving_g": 1.0,
        "fat_per_serving_g": 0.5,
        "lactose_level": "faible",
        "price_subscription_ttc_eur": None,
        "subscription_discount_pct": None,
        "channels": ["site_propre"],
        "snapshot_date": SNAPSHOT,
        "source": "shopify_mcp_plus_manual_website",
        "source_url": "https://impulse-nutrition.fr/products/whey-isolate-saveur-chocolat",
    }
    return [
        {
            **base,
            "product_id": "impulse_nutrition_whey_isolate_750g_chocolat",
            "product_name": "Whey Isolate",
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "vanille", "nature"],
            "price_catalog_ttc_eur": 39.90,
        },
        {
            **base,
            "product_id": "impulse_nutrition_whey_isolate_750g_vanille",
            "product_name": "Whey Isolate",
            "flavor": "vanille",
            "flavors_available_sample": ["chocolat", "vanille", "nature"],
            "price_catalog_ttc_eur": 39.90,
            "source_url": "https://impulse-nutrition.fr/products/whey-isolate-saveur-vanille",
        },
        {
            **base,
            "product_id": "impulse_nutrition_whey_isolate_750g_nature",
            "product_name": "Whey Isolate",
            "flavor": "nature",
            "flavors_available_sample": ["chocolat", "vanille", "nature"],
            "price_catalog_ttc_eur": 37.90,
            "source_url": "https://impulse-nutrition.fr/products/whey-isolate-nature",
        },
    ]


def main():
    xlsx_products = load_xlsx()
    impulse = impulse_products()
    catalog = {
        "meta": {
            "schema_version": 1,
            "description": "Whey concurrents benchmark — raw SKU data. Derived prices (€/kg, €/g prot., discount) computed at build time.",
            "last_updated": SNAPSHOT,
            "sources": {
                "xlsx_vitavea_backport": "benchmark_whey_vitavea.xlsx (HAVEA internal, April 2026)",
                "shopify_mcp_plus_manual_website": "Shopify MCP + impulse-nutrition.fr (April 2026)",
            },
        },
        "products": impulse + xlsx_products,
    }
    OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"Wrote {len(catalog['products'])} SKUs to {OUT}")
    brands = {}
    for p in catalog["products"]:
        brands[p["brand"]] = brands.get(p["brand"], 0) + 1
    for b, n in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"  {b}: {n}")


if __name__ == "__main__":
    main()
