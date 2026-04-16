#!/usr/bin/env python3
"""Insert KolSquare filtered prospects into the Suivi_Amb tab.

Reads `filtered_prospects_042026.csv` (output of `filter_kolsquare.py`) and
appends one row per qualified prospect to the `Suivi_Amb` tab of the
Impulse Nutrition tracking sheet, with the `KolSquare-042026` campaign tag
in column M.

Layout — Suivi_Amb has 3 header rows (lines 1-3), data from line 4.
Canonical column indices come from `common/google_sheets.py:SUIVI_AMB_COLS`.

Flaggés AGENCE (`has_agent=yes` in the CSV) are **never** inserted — they
land in a separate text file so Antoine can handle them manually via the
agency (contrat payant potentiel).

Usage :
    python kolsquare_to_sheet.py \\
        --csv ../tools/veille_kolsquare/filtered_prospects_042026.csv \\
        --dry-run              # print what would be inserted, write nothing

    python kolsquare_to_sheet.py \\
        --csv ../tools/veille_kolsquare/filtered_prospects_042026.csv \\
        --priorities P1,P2,P3  # which priority buckets to insert (default all)

    python kolsquare_to_sheet.py --csv ... --limit 10   # first N only (test)
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.google_sheets import (  # noqa: E402
    DATA_START_ROW,
    HEADER_ROW,
    SHEET_ID,
    SUIVI_AMB_COLS,
    get_worksheet,
    idx_to_col_letter,
)


logger = logging.getLogger("kolsquare_to_sheet")

CAMPAIGN_TAG = "KolSquare-042026"
TAB_NAME = "Suivi_Amb"

# Max number of columns we touch in each inserted row. Suivi_Amb has 38 cols
# (A-AL, index 0..37), so we build a row of that exact length.
ROW_LENGTH = 38

# Batch size for sheet updates — keep conservative to avoid gspread quota.
BATCH_SIZE = 20


# =========================================================================
# CSV loading
# =========================================================================


def load_filtered_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"filtered CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


# =========================================================================
# Row builders
# =========================================================================


def _format_followers_k(raw: str) -> str:
    """Matches the Suivi_Amb convention : '26' for round k, '3,3' for sub-10k."""
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return ""
    if n == 0:
        return ""
    k = n / 1000
    if k >= 10:
        return str(int(round(k)))
    return f"{k:.1f}".replace(".", ",")


def _format_engagement(raw: str) -> str:
    """Engagement in % with comma decimal — cap at 30% (drop noisy KolSquare values)."""
    try:
        e = float(raw)
    except (TypeError, ValueError):
        return ""
    if e <= 0:
        return ""
    if e > 30:
        return ""  # noisy, don't pollute the sheet
    return f"{e:.1f}".replace(".", ",")


def _action_from_priority(priority: str) -> str:
    return "premier contact — campagne KolSquare"


def _clean_prenom(raw: str, username: str) -> str:
    """Return the prénom only if it looks like a real first name.

    KolSquare often stores only the Instagram handle in the display name,
    which `filter_kolsquare._guess_first_last` then returns as the prénom.
    We don't want DMs like "Hello johann_reptile_duhaupas !" — falling back
    to an empty prénom makes `run_campaign.build_message` emit "Hello !".
    """
    p = (raw or "").strip()
    if not p:
        return ""
    if p.lower() == username.lower():
        return ""
    if "_" in p or "." in p:
        return ""
    if not p[0].isupper():
        return ""
    return p


def build_row(prospect: Dict[str, str], today: str) -> List[str]:
    """Return a 38-cell list ready to be written to Suivi_Amb."""
    row = [""] * ROW_LENGTH

    username = prospect["username"].strip().lstrip("@").lower()
    prenom = _clean_prenom(prospect.get("prenom", ""), username)
    nom_raw = prospect.get("nom", "").strip()
    # Don't carry a nom if the prenom was rejected — the whole name parsing
    # likely failed (display field was just a handle).
    nom = nom_raw if prenom else ""

    row[SUIVI_AMB_COLS["ig_link"]] = f"https://www.instagram.com/{username}/"
    row[SUIVI_AMB_COLS["username"]] = username
    row[SUIVI_AMB_COLS["statut"]] = "In-cold"
    row[SUIVI_AMB_COLS["action"]] = _action_from_priority(prospect["priority"])
    row[SUIVI_AMB_COLS["priorite"]] = "medium"
    row[SUIVI_AMB_COLS["campagne"]] = CAMPAIGN_TAG
    row[SUIVI_AMB_COLS["taux_engagement"]] = _format_engagement(prospect["engagement_pct"])
    row[SUIVI_AMB_COLS["bio"]] = prospect.get("mcp_bio", "")[:120]
    row[SUIVI_AMB_COLS["sport"]] = prospect.get("mcp_sport") or prospect.get("metier_raw", "").split(",")[0].strip()
    row[SUIVI_AMB_COLS["followers_k"]] = _format_followers_k(prospect["followers"])
    row[SUIVI_AMB_COLS["date_premier_contact"]] = today
    row[SUIVI_AMB_COLS["nom"]] = nom
    row[SUIVI_AMB_COLS["prenom"]] = prenom

    # First email only (col AF = mail)
    emails = prospect.get("emails", "")
    if emails:
        first_email = emails.split("|")[0].strip()
        row[SUIVI_AMB_COLS["mail"]] = first_email

    return row


# =========================================================================
# Sheet I/O
# =========================================================================


def find_next_empty_row(ws) -> int:
    """Return the 1-indexed sheet row where the next insertion should start."""
    all_values = ws.get_all_values()
    # Data rows start at DATA_START_ROW (index DATA_START_ROW-1 in all_values)
    data = all_values[HEADER_ROW:]
    username_col = SUIVI_AMB_COLS["username"]
    last_filled = 0
    for offset, row in enumerate(data):
        if len(row) > username_col and row[username_col].strip():
            last_filled = offset
    # last_filled is 0-indexed within data; sheet row = HEADER_ROW + last_filled + 2
    # because HEADER_ROW is 0-indexed count of headers (3) and sheet rows are 1-indexed.
    # Examples: HEADER_ROW=3, last_filled=0 → row 4 is the last filled → next = 5
    if last_filled == 0 and (not data or not data[0] or not data[0][username_col].strip()):
        return DATA_START_ROW
    return HEADER_ROW + last_filled + 2


def batch_write(ws, rows: List[List[str]], start_row: int) -> None:
    """Write `rows` starting at `start_row` in chunks of BATCH_SIZE."""
    end_col_letter = idx_to_col_letter(ROW_LENGTH - 1)
    i = 0
    while i < len(rows):
        chunk = rows[i : i + BATCH_SIZE]
        chunk_start = start_row + i
        chunk_end = chunk_start + len(chunk) - 1
        range_a1 = f"A{chunk_start}:{end_col_letter}{chunk_end}"
        logger.info("  writing rows %d-%d (%d rows)", chunk_start, chunk_end, len(chunk))
        ws.update(range_a1, chunk, value_input_option="USER_ENTERED")
        i += BATCH_SIZE


# =========================================================================
# Main
# =========================================================================


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="Path to filter_kolsquare.py output CSV")
    parser.add_argument("--dry-run", action="store_true", help="Print rows without writing")
    parser.add_argument(
        "--priorities",
        default="P1,P2,P3",
        help="Comma-separated priorities to insert (default: P1,P2,P3)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Insert first N only (testing)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    _setup_logging(args.verbose)

    allowed_priorities = {p.strip() for p in args.priorities.split(",") if p.strip()}
    logger.info("Priorities to insert : %s", sorted(allowed_priorities))

    csv_path = Path(args.csv).expanduser().resolve()
    prospects = load_filtered_csv(csv_path)
    logger.info("Loaded %d prospects from %s", len(prospects), csv_path)

    # Partition the prospects
    to_insert: List[Dict[str, str]] = []
    agence: List[Dict[str, str]] = []
    excluded = 0

    for p in prospects:
        prio = p.get("priority", "")
        if prio not in allowed_priorities:
            excluded += 1
            continue
        if p.get("has_agent", "").lower() == "yes":
            agence.append(p)
            continue
        to_insert.append(p)

    if args.limit is not None:
        to_insert = to_insert[: args.limit]

    logger.info("Eligible for insert : %d", len(to_insert))
    logger.info("Flaggés agence (not inserted) : %d", len(agence))
    logger.info("Excluded by priority filter : %d", excluded)

    if not to_insert:
        logger.warning("Nothing to insert — bail out.")
        return 0

    today = datetime.now().strftime("%d/%m/%Y")

    # Build all rows up-front
    rows = [build_row(p, today) for p in to_insert]

    # Save agence list to a file for manual handling
    if agence:
        agence_path = csv_path.parent / f"{csv_path.stem}_agences.txt"
        with agence_path.open("w", encoding="utf-8") as f:
            f.write(f"Profils KolSquare avec agent — {len(agence)} profils\n")
            f.write("A traiter manuellement (passer par l'agence).\n\n")
            for p in agence:
                f.write(
                    f"@{p['username']:<30} {p.get('nom_agent','?'):<30} "
                    f"{p.get('priority','?'):<5} {p.get('followers','?')} followers — "
                    f"{p.get('emails','').split('|')[0]}\n"
                )
        logger.info("Agence list saved : %s", agence_path)

    if args.dry_run:
        print("\n=== DRY RUN — top 10 rows that would be inserted ===")
        for p, r in list(zip(to_insert, rows))[:10]:
            clean_prenom = r[SUIVI_AMB_COLS["prenom"]]
            clean_nom = r[SUIVI_AMB_COLS["nom"]]
            name_display = f"{clean_prenom} {clean_nom}".strip() or "(no name — 'Hello !')"
            print(
                f"  {p['priority']:<3} @{p['username']:<25} "
                f"{p['followers']:>6} followers  eng {p['engagement_pct']}%  "
                f"→ {name_display} "
                f"[{p.get('mcp_verdict','?')}]"
            )
        print(f"\nTotal to insert : {len(to_insert)}")
        print(f"Flaggés agence  : {len(agence)}")
        print(f"Campagne tag    : {CAMPAIGN_TAG}")
        print("\nRe-run without --dry-run to actually write.")
        return 0

    # Real write
    logger.info("Opening %s tab ...", TAB_NAME)
    ws = get_worksheet(TAB_NAME, SHEET_ID)
    start_row = find_next_empty_row(ws)
    logger.info("Next empty row : %d — writing %d rows", start_row, len(rows))

    batch_write(ws, rows, start_row)

    logger.info(
        "Done — %d rows inserted into %s (campagne=%s) starting row %d",
        len(rows), TAB_NAME, CAMPAIGN_TAG, start_row,
    )
    if agence:
        logger.info("Reminder : %d agence profiles in _agences.txt to handle manually", len(agence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
