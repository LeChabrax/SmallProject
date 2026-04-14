"""Add Impulse Whey Recovery (chocolat + vanille) to whey_catalog.json.

Product info sourced from impulse-nutrition.fr live page:
- 525g format, 39.90€ TTC
- Concentrat (whey protein concentrate) + créatine Creapure 3g + collagène Peptan 5g + magnésium
- Portion 35g → 21g protéines (~60% prot/100g)
- 15 portions par pot
- 2 arômes : chocolat, vanille

Idempotent via product_id check.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
SNAPSHOT = "2026-04-14"

RECOVERY_COMMON = {
    "brand": "impulse_nutrition",
    "type": "concentrat_fromagere",
    "native_vs_fromagere": "fromagere",
    "format_g": 525,
    "origin_milk": "UE",
    "certifications": ["Creapure®", "Peptan®"],
    "protein_pct_100g": 60,
    "protein_per_serving_g": 21,
    "serving_size_g": 35,
    "servings_per_pack": 15,
    "bcaa_per_serving_g": None,
    "carbs_per_serving_g": None,
    "fat_per_serving_g": None,
    "lactose_level": "present",
    "price_nominal_ttc_eur": 39.90,
    "price_current_ttc_eur": 39.90,
    "price_median_market_ttc_eur": None,
    "price_catalog_ttc_eur_legacy": 39.90,
    "price_subscription_ttc_eur": None,
    "subscription_discount_pct": None,
    "channels": ["Site propre"],
    "snapshot_date": SNAPSHOT,
    "source": "webfetch_impulse_nutrition_fr_2026-04-14",
    "price_gap_note": "Blend recovery (concentrat whey + créatine Creapure 3g + collagène Peptan 5g + magnésium). Pas comparable 1-pour-1 aux whey pures — 60% protéines car le reste = additifs de récupération.",
}


def main():
    catalog = json.loads(CATALOG.read_text())
    existing_ids = {p["product_id"] for p in catalog["products"]}

    new_skus = [
        {
            **RECOVERY_COMMON,
            "product_id": "impulse_nutrition_whey_recovery_525g_chocolat",
            "product_name": "Whey Recovery",
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "vanille"],
            "source_url": "https://impulse-nutrition.fr/products/whey-recovery-saveur-chocolat",
        },
        {
            **RECOVERY_COMMON,
            "product_id": "impulse_nutrition_whey_recovery_525g_vanille",
            "product_name": "Whey Recovery",
            "flavor": "vanille",
            "flavors_available_sample": ["chocolat", "vanille"],
            "source_url": "https://impulse-nutrition.fr/products/whey-recovery-saveur-vanille",
        },
    ]

    added = 0
    for sku in new_skus:
        if sku["product_id"] in existing_ids:
            print(f"  SKIP {sku['product_id']} (already exists)")
            continue
        catalog["products"].append(sku)
        added += 1
        print(f"✓ Added {sku['product_id']}")

    catalog["meta"]["last_updated"] = SNAPSHOT
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n✓ Total SKUs : {len(catalog['products'])}")


if __name__ == "__main__":
    main()
