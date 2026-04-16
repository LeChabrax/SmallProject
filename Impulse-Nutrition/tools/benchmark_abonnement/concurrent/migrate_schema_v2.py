"""
Migrate whey_catalog.json schema v1 → v2 with 3-layer price model.

v1:  price_catalog_ttc_eur (single ambiguous field)
v2:  price_nominal_ttc_eur   (site propre, prix barré if exists, else principal sticker)
     price_current_ttc_eur   (site propre, prix affiché aujourd'hui sans code)
     price_median_market_ttc_eur (idealo/ledenicheur median cross-retailers)
     + historique in field_sources

Migration strategy :
- price_catalog_ttc_eur → price_current_ttc_eur as starting point (it's the closest semantic)
- price_nominal_ttc_eur and price_median_market_ttc_eur start as null, to be filled by Phase 2/3
- Old field kept as _legacy for traceability
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"


def main():
    catalog = json.loads(CATALOG.read_text())
    migrated = 0
    for p in catalog["products"]:
        if "price_current_ttc_eur" in p:
            continue  # already migrated (idempotent)
        legacy = p.get("price_catalog_ttc_eur")
        p["price_current_ttc_eur"] = legacy
        p["price_nominal_ttc_eur"] = None
        p["price_median_market_ttc_eur"] = None
        p["price_catalog_ttc_eur_legacy"] = legacy
        if "price_catalog_ttc_eur" in p:
            del p["price_catalog_ttc_eur"]
        migrated += 1

    catalog["meta"]["schema_version"] = 2
    catalog["meta"]["schema_v2_note"] = (
        "3-layer price model : price_nominal (prix barré site propre), "
        "price_current (prix affiché site propre aujourd'hui, inclut promos permanentes), "
        "price_median_market (prix médian cross-retailers via idealo/ledenicheur). "
        "Legacy price_catalog_ttc_eur conservé en price_catalog_ttc_eur_legacy pour traçabilité."
    )
    catalog["meta"]["last_updated"] = "2026-04-14"

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"✓ Migrated {migrated} SKUs to schema v2")


if __name__ == "__main__":
    main()
