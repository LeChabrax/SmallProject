"""
Merge price_refresh JSON from the v2 refresh agent into whey_catalog.json.

Applies 3-layer price patches idempotently. Tracks per-field sources.
Expected input file: agent_prices_v2.json (JSON block pasted manually from agent output).
"""

import json
from difflib import get_close_matches
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
INPUT = HERE / "agent_prices_v2.json"


def main():
    if not INPUT.exists():
        print(f"! {INPUT.name} not found — paste the agent JSON into this file first")
        return
    catalog = json.loads(CATALOG.read_text())
    patches = json.loads(INPUT.read_text())

    by_id = {p["product_id"]: p for p in catalog["products"]}
    catalog_ids = list(by_id.keys())
    applied, skipped, issues = 0, 0, []
    for entry in patches.get("price_refresh", []):
        pid = entry["product_id"]
        if pid not in by_id:
            # Try fuzzy match (catalog has double-encoded format like "bulk_whey_1kg_1000g_choc")
            matches = get_close_matches(pid, catalog_ids, n=1, cutoff=0.6)
            if matches:
                pid = matches[0]
            else:
                skipped += 1
                issues.append(f"SKIP {entry['product_id']} (no match in catalog)")
                continue
        product = by_id[pid]
        field_sources = product.setdefault("field_sources", {})

        for field in ("price_nominal_ttc_eur", "price_current_ttc_eur", "price_median_market_ttc_eur"):
            if field in entry and entry[field] is not None:
                product[field] = entry[field]
                src_key = field.replace("_ttc_eur", "_source_url")
                note_key = field.replace("_ttc_eur", "_source_note")
                field_sources[field] = {
                    "source_url": entry.get(src_key) or entry.get("nominal_source_url") or entry.get("current_source_url") or entry.get("price_median_source_url"),
                    "source_note": entry.get(note_key),
                    "patched_at": entry.get("snapshot_date", "2026-04-14"),
                }

        if entry.get("price_gap_note"):
            product["price_gap_note"] = entry["price_gap_note"]
        applied += 1

    catalog["meta"]["last_updated"] = "2026-04-14"
    catalog["meta"]["schema_v2_refresh_round"] = (
        "v2 3-layer price refresh via idealo/ledenicheur/brand sites"
    )
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))

    print(f"✓ Applied {applied}, skipped {skipped}")
    for i in issues[:10]:
        print(f"  {i}")
    if patches.get("failures"):
        print(f"\nAgent failures ({len(patches['failures'])}):")
        for f in patches["failures"][:10]:
            print(f"  {f}")


if __name__ == "__main__":
    main()
