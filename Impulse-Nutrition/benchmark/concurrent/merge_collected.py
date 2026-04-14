"""Merge agent_collected.json into whey_catalog.json idempotently."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "whey_catalog.json"
COLLECTED = HERE / "agent_collected.json"


def main():
    catalog = json.loads(CATALOG.read_text())
    collected = json.loads(COLLECTED.read_text())
    existing_ids = {p["product_id"] for p in catalog["products"]}
    added, updated = 0, 0
    for p in collected["products"]:
        if p["product_id"] in existing_ids:
            for i, existing in enumerate(catalog["products"]):
                if existing["product_id"] == p["product_id"]:
                    catalog["products"][i] = p
                    updated += 1
                    break
        else:
            catalog["products"].append(p)
            added += 1
    catalog["meta"]["last_updated"] = "2026-04-14"
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"Added: {added}, Updated: {updated}")
    print(f"Total SKUs: {len(catalog['products'])}")
    brands = {}
    for p in catalog["products"]:
        brands[p["brand"]] = brands.get(p["brand"], 0) + 1
    for b, n in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"  {b}: {n}")


if __name__ == "__main__":
    main()
