"""Apply enrichments.json patches onto whey_catalog.json.

Idempotent : run N times, same result.
Tracks per-field sources via `field_sources` dict.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
ENRICHMENTS = HERE / "enrichments.json"


def main():
    catalog = json.loads(CATALOG.read_text())
    enrich = json.loads(ENRICHMENTS.read_text())
    products_by_id = {p["product_id"]: p for p in catalog["products"]}

    applied, skipped = 0, 0
    for entry in enrich["enrichments"]:
        pid = entry["product_id"]
        if pid not in products_by_id:
            skipped += 1
            print(f"  SKIP {pid} (not in catalog)")
            continue
        product = products_by_id[pid]
        patch = entry["patch"]
        source_url = entry["source_url"]
        source_note = entry.get("source_note", "")
        field_sources = product.setdefault("field_sources", {})
        for field, value in patch.items():
            product[field] = value
            field_sources[field] = {
                "source_url": source_url,
                "source_note": source_note,
                "patched_at": "2026-04-14",
            }
        applied += 1
        print(f"  PATCH {pid}: {len(patch)} fields")

    catalog["meta"]["last_updated"] = "2026-04-14"
    catalog["meta"]["enrichment_round"] = "round 2 : nutrition backfill via OFF + fddb + retailer pages"
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n✓ Applied {applied} enrichments, skipped {skipped}")


if __name__ == "__main__":
    main()
