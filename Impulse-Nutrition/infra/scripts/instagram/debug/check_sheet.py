"""Quick grep over Suivi_Amb rows. Usage: python check_sheet.py <query>."""

import sys
from pathlib import Path

# Bootstrap: anchor to project root via .mcp.json (see infra/common/paths.py).
_here = Path(__file__).resolve()
for _p in (_here, *_here.parents):
    if (_p / ".mcp.json").exists():
        sys.path.insert(0, str(_p))
        break
from infra.common.google_sheets import get_worksheet  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python check_sheet.py <query>")
        return

    query = sys.argv[1].lower()
    wks = get_worksheet("Suivi_Amb")
    all_values = wks.get_all_values()
    headers = all_values[0]

    hits = [(i, row) for i, row in enumerate(all_values[1:], start=2)
            if query in " ".join(row).lower()]

    if not hits:
        print("No results found.")
        return

    for i, row in hits:
        print(f"Row {i}:")
        for h, v in zip(headers, row):
            if v:
                print(f"  {h}: {v}")
        print("-" * 20)


if __name__ == "__main__":
    main()
