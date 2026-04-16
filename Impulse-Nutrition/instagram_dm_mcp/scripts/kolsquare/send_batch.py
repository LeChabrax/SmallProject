#!/usr/bin/env python3
"""Send the pitch_initial_plain.txt DM to a hardcoded list of KolSquare profiles.

One-shot batch script for the KolSquare-042026 campaign — targets the 10 top
P1 profiles (by MCP score) identified in the 2026-04-13 planning session.
After each successful send, updates col K of Suivi_Amb with
"premier message sent".

Usage :
    .venv/bin/python kolsquare_send_batch.py --dry-run   # lookup only
    .venv/bin/python kolsquare_send_batch.py             # real send
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.google_sheets import (  # noqa: E402
    HEADER_ROW,
    SHEET_ID,
    SUIVI_AMB_COLS,
    get_worksheet,
)
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402

# Reuse build_message() from the campaign runner script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "campaign"))
from run import build_message  # noqa: E402

USERNAMES = [
    "isa_nutricoaching",
    "majin.junior",
    "laurunmind",
    "claracopponi",
    "julius.giavarra",
    "nicolai.chris",
    "enrico.smeraldi",
    "janvberkel",
    "jeannelehair",
    "alexia__bailly",
]

TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "templates" / "pitch_initial_plain.txt"
ACTION_K = "premier message sent"
DELAY_BETWEEN_SENDS = 4  # seconds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Lookup only, no send, no sheet update")
    args = parser.parse_args()

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # -----------------------------------------------------------------
    # 1. Locate the 10 rows in Suivi_Amb
    # -----------------------------------------------------------------
    print(f"Opening Suivi_Amb ...")
    ws = get_worksheet("Suivi_Amb", SHEET_ID)
    all_values = ws.get_all_values()
    data = all_values[HEADER_ROW:]

    target_set = {u.lower() for u in USERNAMES}
    username_to_info: dict[str, tuple[int, str]] = {}  # key: lowercase username

    for offset, row in enumerate(data):
        if len(row) <= SUIVI_AMB_COLS["username"]:
            continue
        u = row[SUIVI_AMB_COLS["username"]].strip().lstrip("@").lower()
        if u in target_set:
            sheet_row = HEADER_ROW + offset + 1  # 1-indexed sheet row
            prenom = (
                row[SUIVI_AMB_COLS["prenom"]].strip()
                if len(row) > SUIVI_AMB_COLS["prenom"] else ""
            )
            username_to_info[u] = (sheet_row, prenom)

    missing = [u for u in USERNAMES if u.lower() not in username_to_info]
    if missing:
        print(f"ERROR: missing from Suivi_Amb: {missing}")
        return 2

    print(f"Found all {len(USERNAMES)} profiles in Suivi_Amb.\n")
    print(f"{'#':>2}  {'row':>4}  {'username':<28}  {'prenom':<15}  first line of DM")
    print("-" * 100)
    for i, u in enumerate(USERNAMES, 1):
        sheet_row, prenom = username_to_info[u.lower()]
        msg = build_message(template, prenom)
        first_line = msg.split("\n")[0]
        print(f"{i:>2}  {sheet_row:>4}  @{u:<27}  {prenom or '(-)':<15}  {first_line}")

    if args.dry_run:
        print("\n[DRY RUN] no DM sent, no sheet update.")
        return 0

    # -----------------------------------------------------------------
    # 2. Instagram login (main account)
    # -----------------------------------------------------------------
    cl = get_ig_client("impulse")
    cl.request_timeout = 5
    print(f"\nLogged in as impulse")

    # -----------------------------------------------------------------
    # 3. Send DMs
    # -----------------------------------------------------------------
    sent: list[tuple[str, int]] = []
    errors: dict[str, str] = {}

    for i, u in enumerate(USERNAMES, 1):
        sheet_row, prenom = username_to_info[u.lower()]
        msg = build_message(template, prenom)

        print(f"\n[{i}/{len(USERNAMES)}] @{u} (row {sheet_row}, prenom='{prenom or '-'}')")
        try:
            user_id = cl.user_id_from_username(u)
            dm = cl.direct_send(msg, [user_id])
            dm_id = getattr(dm, "id", "?")
            print(f"  ✓ sent (dm id={dm_id})")
            sent.append((u, sheet_row))
        except Exception as e:
            print(f"  ✗ error: {e}")
            errors[u] = str(e)

        if i < len(USERNAMES):
            sleep_random(DELAY_BETWEEN_SENDS, DELAY_BETWEEN_SENDS + 3)

    # -----------------------------------------------------------------
    # 4. Batch update col K for successfully sent
    # -----------------------------------------------------------------
    if sent:
        print(f"\nUpdating col K for {len(sent)} rows ...")
        updates = [
            {"range": f"K{row}", "values": [[ACTION_K]]}
            for _, row in sent
        ]
        ws.batch_update(updates)
        print(f"  ✓ col K updated")

    # -----------------------------------------------------------------
    # 5. Summary
    # -----------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"DONE — sent: {len(sent)}/{len(USERNAMES)}, errors: {len(errors)}")
    print(f"{'=' * 60}")
    if errors:
        print("Errors:")
        for u, e in errors.items():
            print(f"  @{u}: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
