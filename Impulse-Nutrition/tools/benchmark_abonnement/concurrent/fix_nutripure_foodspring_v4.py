"""
Phase 8 corrections — Nutripure + Foodspring v4.

Data collected via Playwright direct navigation :

Nutripure (Prestashop, variants via radio buttons) :
- Whey Isolat Native 750g chocolat : 39,90€ ✓ (déjà correct)
- Whey Isolat Native 2kg chocolat : 104,90€ (was 90€, +16%)
- Whey Isolat Native 4kg chocolat : 179,90€ (was 159,90€, +13%)

Source : https://www.nutripure.fr/fr/musculation/147-whey-chocolat-isolate.html
Méthode : click variant radio (id=332 pour 2kg, id=47 pour 4kg), read "Ajouter au panier" text

Foodspring (foodspring.fr DNS dead, fallback Amazon FR) :
- Whey Protein 750g vanille : 39,90€ nominal / 29,96€ current
  (was 32,95€ sourced via paraplus.fr)
Source : https://www.amazon.fr/foodspring-croissance-musculaire-solubilit%C3%A9-ultra-filtr%C3%A9e/dp/B0CTR3FZ7W
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
SNAPSHOT = "2026-04-14"

FIXES = {
    "nutripure_whey_isolat_native_2kg_2000g_chocolat": (
        104.90, 104.90,
        "Confirmé via Playwright click sur variant radio Seau 2KG (id=332). Page nutripure.fr. Agent v2 avait mal lu '90€' (probablement le 'à partir de' affiché sur la page parent).",
        "https://www.nutripure.fr/fr/musculation/147-1115-whey-chocolat-isolate.html#/332-poids_poudre-seau_2kg",
    ),
    "nutripure_whey_isolat_native_4kg_4000g_chocolat": (
        179.90, 179.90,
        "Confirmé via Playwright click sur variant radio Seau 4KG (id=47). Prix réel 179,90€ (pas 159,90€ extrapolé).",
        "https://www.nutripure.fr/fr/musculation/147-674-whey-chocolat-isolate.html#/47-poids_poudre-seau_4kg",
    ),
    "foodspring_whey_protein_750g_vanille": (
        39.90, 29.96,
        "Site foodspring.fr = DNS dead (brand pas disponible en FR direct). Prix récupéré via Amazon FR fiche vanille 750g : 29,96€ current (39,90€ RRP affiché). Agent v2 avait 32,95€ via revendeur paraplus.fr, désormais obsolète.",
        "https://www.amazon.fr/foodspring-croissance-musculaire-solubilit%C3%A9-ultra-filtr%C3%A9e/dp/B0CTR3FZ7W",
    ),
}


def main():
    catalog = json.loads(CATALOG.read_text())
    by_id = {p["product_id"]: p for p in catalog["products"]}

    fixed = 0
    for pid, (nominal, current, note, url) in FIXES.items():
        if pid not in by_id:
            print(f"  MISSING {pid}")
            continue
        p = by_id[pid]
        old_n, old_c = p.get("price_nominal_ttc_eur"), p.get("price_current_ttc_eur")
        p["price_nominal_ttc_eur"] = nominal
        p["price_current_ttc_eur"] = current
        p["price_gap_note"] = note
        p["source_url"] = url
        p["snapshot_date"] = SNAPSHOT
        fs = p.setdefault("field_sources", {})
        fs["price_nominal_ttc_eur"] = {"source_url": url, "source_note": note, "patched_at": SNAPSHOT}
        fs["price_current_ttc_eur"] = {"source_url": url, "source_note": note, "patched_at": SNAPSHOT}
        fixed += 1
        print(f"✓ FIX {pid}: {old_n}/{old_c} → {nominal}/{current}")

    catalog["meta"]["last_updated"] = SNAPSHOT
    catalog["meta"]["v4_fix_round"] = "Phase 8 : Nutripure variants via Playwright click + Foodspring Amazon fallback"
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n✓ Fixed {fixed} SKUs")


if __name__ == "__main__":
    main()
