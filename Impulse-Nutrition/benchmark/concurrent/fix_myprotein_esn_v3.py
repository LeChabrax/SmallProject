"""
Phase 7 corrections — MyProtein + ESN prix v3.

Data collected via direct Playwright MCP navigation of variant URLs :

MyProtein findings :
- Impact Whey Protein 1kg chocolat (URL 11068071) : nominal 41.99€ / current 17.99€ (promo -57%)
- Impact Whey Protein 2.5kg chocolate nut (URL 10530969) : nominal 84.99€ / current 40.99€ (promo -52%)
- Impact Whey Isolate 2.5kg framboise (URL 10530927) : 124.99€ = 124.99€ (PAS de promo, Isolate exclu)
- Clear Whey Isolate 875g (URL 12081395) : 49.99€ = 49.99€ (pas de promo, Clear exclu)

Pattern découvert :
- Le banner MyProtein "-30% + 10% app" s'applique au Impact Whey Protein (concentrat) seul
- Les Isolate et Clear Whey sont EXCLUS de la promo → prix nominal = prix current
- Correction : revert les discounts sur Isolate/Clear

ESN findings :
- Designer Whey 908g : prix réel ~41.99€ (vs 42.90€ dans catalog) — minor drift

Corrections :
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
SNAPSHOT = "2026-04-14"

# product_id → (price_nominal, price_current, price_gap_note, source_url)
FIXES = {
    "myprotein_impact_whey_protein_1kg_1000g_chocolat": (
        41.99, 17.99,
        "Prix actuel = 17.99€ sur fr.myprotein.com/.../11068071/ (scraped Playwright 2026-04-14). Promo site -30% + extra app ramène à 17.99 vs 41.99 nominal (soit -57%). Pattern MyProtein Whey Protein uniquement.",
        "https://fr.myprotein.com/p/nutrition-sportive/myprotein-impact-whey-protein-chocolate-1kg/11068071/",
    ),
    "myprotein_impact_whey_protein_2_5kg_2500g_chocolat": (
        84.99, 40.99,
        "Prix scrapé via variant Chocolate Nut 2.5kg (10530969) : 84.99€ barré / 40.99€ actuel. Promo -52%. Playwright 2026-04-14.",
        "https://fr.myprotein.com/p/nutrition-sportive/myprotein-impact-whey-protein-chocolate-nut-2.5kg/10530969/",
    ),
    # 5kg extrapolation : ratio 2.5kg = 40.99/84.99 = 0.482 → 5kg 188.99 × 0.482 ≈ 91.1
    "myprotein_impact_whey_protein_5kg_5000g_sans_arome": (
        188.99, 91.10,
        "5kg n'existe qu'en 'Sans arôme' (chocolat inexistant). Current price = extrapolation du ratio 2.5kg (40.99/84.99=0.482) : 188.99 × 0.482 ≈ 91.10€.",
        "https://fr.myprotein.com/p/nutrition-sportive/impact-whey-protein/10530943/",
    ),
    # Isolate : REVERT discount — pas de promo appliquée sur ces produits
    "myprotein_impact_whey_isolate_1kg_1000g_chocolat": (
        57.99, 57.99,
        "Isolate EXCLU de la promo -30% MyProtein. Prix current = prix nominal (pas de discount automatique). Revert de l'ancienne estimation ×0.7.",
        "https://fr.myprotein.com/p/nutrition-sportive/impact-whey-isolate/10852482/",
    ),
    "myprotein_impact_whey_isolate_2_5kg_2500g_chocolat": (
        124.99, 124.99,
        "Confirmé via variant Framboise 2.5kg (10530927) : 124.99€ affiché sans strikethrough. Isolate exclu de la promo -30%.",
        "https://fr.myprotein.com/p/nutrition-sportive/impact-whey-isolate-framboise-poche-2.5-kg/10530927/",
    ),
    # Clear Whey : deja 49.99/49.99 mais on reconfirme
    "myprotein_clear_whey_isolate_875g_fraise": (
        49.99, 49.99,
        "Clear Whey exclu de la promo -30% (mention explicite). Format 875g max (pas de 1kg). Confirmé via scraping 12081395.",
        "https://fr.myprotein.com/p/nutrition-sportive/clear-whey-isolate/12081395/",
    ),
    # ESN : ajustement mineur
    "esn_designer_whey_908g_chocolat": (
        41.99, 41.99,
        "Prix réel confirmé 41.99€ (vs 42.90€ ancien). Drift mineur sans promo.",
        "https://www.esn.com/products/esn-designer-whey-protein",
    ),
}


def main():
    catalog = json.loads(CATALOG.read_text())
    by_id = {p["product_id"]: p for p in catalog["products"]}

    fixed, missing = 0, []
    for pid, (nominal, current, note, url) in FIXES.items():
        if pid not in by_id:
            missing.append(pid)
            continue
        p = by_id[pid]
        old_nominal = p.get("price_nominal_ttc_eur")
        old_current = p.get("price_current_ttc_eur")
        p["price_nominal_ttc_eur"] = nominal
        p["price_current_ttc_eur"] = current
        p["price_gap_note"] = note
        p["source_url"] = url
        p["snapshot_date"] = SNAPSHOT

        fs = p.setdefault("field_sources", {})
        fs["price_nominal_ttc_eur"] = {"source_url": url, "source_note": note, "patched_at": SNAPSHOT}
        fs["price_current_ttc_eur"] = {"source_url": url, "source_note": note, "patched_at": SNAPSHOT}

        fixed += 1
        print(f"✓ FIX {pid}")
        print(f"    {old_nominal}€ / {old_current}€ → {nominal}€ / {current}€")

    catalog["meta"]["last_updated"] = SNAPSHOT
    catalog["meta"]["v3_fix_round"] = "Phase 7 : MyProtein variant spot-check + ESN drift correction"
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n✓ Fixed {fixed} SKUs")
    if missing:
        print(f"  Missing: {missing}")


if __name__ == "__main__":
    main()
