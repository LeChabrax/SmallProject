"""
Phase 4 cleanup + expand whey_catalog.json :
1. Delete nutrimuscle_musclewhey (produit retiré du catalogue)
2. Fix myprotein 5kg : n'existe qu'en "sans arôme", rename SKU
3. Fix myprotein clear whey 1kg : n'existe qu'en 875g, corriger format + name
4. Add missing formats (sourced from nutrimuscle.com and nutripure.fr live):
   - Nutrimuscle Whey Native 500g / 2.25kg / 4kg (concentrat)
   - Nutrimuscle Whey Native Isolate 500g / 2.25kg / 4kg
   - Nutripure Whey Isolat Native 4kg
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
SNAPSHOT = "2026-04-14"


def main():
    catalog = json.loads(CATALOG.read_text())
    products = catalog["products"]

    # ── 1. Delete nutrimuscle_musclewhey (obsolete)
    before = len(products)
    products[:] = [p for p in products if p["product_id"] != "nutrimuscle_musclewhey_mix_conc_iso_1000g_chocolat"]
    print(f"✓ Deleted 1 obsolete SKU (musclewhey) — {before} → {len(products)}")

    # ── 2. Fix myprotein 5kg chocolat → sans arôme (le 5kg n'existe qu'en neutre)
    for p in products:
        if p["product_id"] == "myprotein_impact_whey_protein_5kg_5000g_chocolat":
            p["product_id"] = "myprotein_impact_whey_protein_5kg_5000g_sans_arome"
            p["product_name"] = "Impact Whey Protein 5kg (Sans arôme)"
            p["flavor"] = "sans arôme"
            p["flavors_available_sample"] = ["sans arôme"]
            p["price_gap_note"] = "Format 5kg uniquement disponible en 'Sans arôme ajouté' sur myprotein.fr. Le chocolat n'est pas commercialisé en 5kg."
            print(f"✓ Fixed MyProtein 5kg → sans arôme")
            break

    # ── 3. Fix myprotein clear whey 1kg → 875g (format 1kg inexistant)
    for p in products:
        if p["product_id"] == "myprotein_clear_whey_isolate_1kg_1000g_fraise":
            p["product_id"] = "myprotein_clear_whey_isolate_875g_fraise"
            p["product_name"] = "Clear Whey Isolate 875g"
            p["format_g"] = 875
            # Recalc servings from 875/25 = 35
            p["servings_per_pack"] = 35
            p["price_gap_note"] = "Format 1kg inexistant chez MyProtein (max 875g = 35 portions)."
            print(f"✓ Fixed MyProtein Clear Whey 1kg → 875g")
            break

    # ── 4. Add missing formats
    new_skus = [
        # Nutrimuscle Whey Native Concentrat — 3 formats manquants (on a déjà 1kg)
        {
            "brand": "nutrimuscle",
            "product_id": "nutrimuscle_whey_native_concentrat_500g_chocolat",
            "product_name": "Whey Native Concentrat 500g",
            "type": "concentrat_natif",
            "native_vs_fromagere": "native",
            "format_g": 500,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "vanille", "nature"],
            "origin_milk": "France (Lactalis)",
            "certifications": ["Certifié, lait Lactalis FR"],
            "protein_pct_100g": 80,
            "protein_per_serving_g": 24,
            "serving_size_g": 30,
            "servings_per_pack": 16,
            "bcaa_per_serving_g": 5,
            "carbs_per_serving_g": 3.5,
            "fat_per_serving_g": 1.5,
            "lactose_level": "present",
            "price_nominal_ttc_eur": 19.95,
            "price_current_ttc_eur": 19.95,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon", "revendeurs"],
            "source_url": "https://www.nutrimuscle.com/products/whey-native",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
        {
            "brand": "nutrimuscle",
            "product_id": "nutrimuscle_whey_native_concentrat_2250g_chocolat",
            "product_name": "Whey Native Concentrat 2,25kg",
            "type": "concentrat_natif",
            "native_vs_fromagere": "native",
            "format_g": 2250,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "vanille", "nature"],
            "origin_milk": "France (Lactalis)",
            "certifications": ["Certifié, lait Lactalis FR"],
            "protein_pct_100g": 80,
            "protein_per_serving_g": 24,
            "serving_size_g": 30,
            "servings_per_pack": 75,
            "bcaa_per_serving_g": 5,
            "carbs_per_serving_g": 3.5,
            "fat_per_serving_g": 1.5,
            "lactose_level": "present",
            "price_nominal_ttc_eur": 80.95,
            "price_current_ttc_eur": 80.95,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon", "revendeurs"],
            "source_url": "https://www.nutrimuscle.com/products/whey-native",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
        {
            "brand": "nutrimuscle",
            "product_id": "nutrimuscle_whey_native_concentrat_4000g_chocolat",
            "product_name": "Whey Native Concentrat 4kg",
            "type": "concentrat_natif",
            "native_vs_fromagere": "native",
            "format_g": 4000,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "vanille", "nature"],
            "origin_milk": "France (Lactalis)",
            "certifications": ["Certifié, lait Lactalis FR"],
            "protein_pct_100g": 80,
            "protein_per_serving_g": 24,
            "serving_size_g": 30,
            "servings_per_pack": 133,
            "bcaa_per_serving_g": 5,
            "carbs_per_serving_g": 3.5,
            "fat_per_serving_g": 1.5,
            "lactose_level": "present",
            "price_nominal_ttc_eur": 131.95,
            "price_current_ttc_eur": 131.95,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon", "revendeurs"],
            "source_url": "https://www.nutrimuscle.com/products/whey-native",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
        # Nutrimuscle Whey Native Isolate — 3 formats manquants (on a déjà 1kg)
        {
            "brand": "nutrimuscle",
            "product_id": "nutrimuscle_whey_native_isolate_500g_chocolat",
            "product_name": "Whey Native Isolate 500g",
            "type": "isolat_natif",
            "native_vs_fromagere": "native",
            "format_g": 500,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "nature", "vanille", "choco cookie", "fraise", "banane"],
            "origin_milk": "France (Lactalis)",
            "certifications": ["Certifié, lait Lactalis FR"],
            "protein_pct_100g": 87,
            "protein_per_serving_g": 25,
            "serving_size_g": 30,
            "servings_per_pack": 16,
            "bcaa_per_serving_g": 6,
            "carbs_per_serving_g": 1.5,
            "fat_per_serving_g": 0.8,
            "lactose_level": "faible",
            "price_nominal_ttc_eur": 31.95,
            "price_current_ttc_eur": 31.95,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon", "revendeurs"],
            "source_url": "https://www.nutrimuscle.com/products/whey-native-isolate",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
        {
            "brand": "nutrimuscle",
            "product_id": "nutrimuscle_whey_native_isolate_2250g_chocolat",
            "product_name": "Whey Native Isolate 2,25kg",
            "type": "isolat_natif",
            "native_vs_fromagere": "native",
            "format_g": 2250,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "nature", "vanille", "choco cookie", "fraise", "banane"],
            "origin_milk": "France (Lactalis)",
            "certifications": ["Certifié, lait Lactalis FR"],
            "protein_pct_100g": 87,
            "protein_per_serving_g": 25,
            "serving_size_g": 30,
            "servings_per_pack": 75,
            "bcaa_per_serving_g": 6,
            "carbs_per_serving_g": 1.5,
            "fat_per_serving_g": 0.8,
            "lactose_level": "faible",
            "price_nominal_ttc_eur": 116.95,
            "price_current_ttc_eur": 116.95,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon", "revendeurs"],
            "source_url": "https://www.nutrimuscle.com/products/whey-native-isolate",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
        {
            "brand": "nutrimuscle",
            "product_id": "nutrimuscle_whey_native_isolate_4000g_chocolat",
            "product_name": "Whey Native Isolate 4kg",
            "type": "isolat_natif",
            "native_vs_fromagere": "native",
            "format_g": 4000,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "nature", "vanille", "choco cookie", "fraise", "banane"],
            "origin_milk": "France (Lactalis)",
            "certifications": ["Certifié, lait Lactalis FR"],
            "protein_pct_100g": 87,
            "protein_per_serving_g": 25,
            "serving_size_g": 30,
            "servings_per_pack": 133,
            "bcaa_per_serving_g": 6,
            "carbs_per_serving_g": 1.5,
            "fat_per_serving_g": 0.8,
            "lactose_level": "faible",
            "price_nominal_ttc_eur": 190.95,
            "price_current_ttc_eur": 190.95,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon", "revendeurs"],
            "source_url": "https://www.nutrimuscle.com/products/whey-native-isolate",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
        # Nutripure 4kg nouveau format
        {
            "brand": "nutripure",
            "product_id": "nutripure_whey_isolat_native_4kg_4000g_chocolat",
            "product_name": "Whey Isolat Native 4kg",
            "type": "isolat_natif",
            "native_vs_fromagere": "native",
            "format_g": 4000,
            "flavor": "chocolat",
            "flavors_available_sample": ["chocolat", "vanille", "neutre", "noisette", "fraise"],
            "origin_milk": "France (pâturages)",
            "certifications": ["EN 17444"],
            "protein_pct_100g": 85,
            "protein_per_serving_g": 25,
            "serving_size_g": 30,
            "servings_per_pack": 133,
            "bcaa_per_serving_g": 5,
            "carbs_per_serving_g": 0.3,
            "fat_per_serving_g": 0.2,
            "lactose_level": "tres_faible",
            "price_nominal_ttc_eur": 159.90,
            "price_current_ttc_eur": 159.90,
            "price_median_market_ttc_eur": None,
            "price_catalog_ttc_eur_legacy": None,
            "price_subscription_ttc_eur": None,
            "subscription_discount_pct": None,
            "channels": ["Site propre", "Amazon"],
            "source_url": "https://www.nutripure.fr/fr/musculation/13-whey-isolate-native.html",
            "snapshot_date": SNAPSHOT,
            "source": "webfetch_direct_2026-04-14",
        },
    ]

    # Check for duplicates before adding
    existing_ids = {p["product_id"] for p in products}
    added = 0
    for new in new_skus:
        if new["product_id"] in existing_ids:
            print(f"  SKIP {new['product_id']} (already exists)")
            continue
        products.append(new)
        added += 1
    print(f"✓ Added {added} new SKUs (missing formats)")

    catalog["meta"]["last_updated"] = SNAPSHOT
    catalog["meta"]["cleanup_round"] = "Phase 4 : delete obsolete + fix inexistent SKUs + add missing formats"
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n✓ Total SKUs : {len(products)}")


if __name__ == "__main__":
    main()
