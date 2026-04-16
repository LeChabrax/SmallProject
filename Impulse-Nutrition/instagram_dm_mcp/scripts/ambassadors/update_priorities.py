"""
Check Instagram DMs and update col L (Priorité) in Suivi_Amb.

Rules:
  high   — Last message from influencer (unreplied) OR Action contains "répondre"/"préparer commande"/"appeler"/"envoyer code"
  medium — Last message from us (waiting) OR Action contains "relancer"/"réagir story"/"contacter manager"/"demander avis"
  good   — Partnership active, all OK OR Action contains "ras"

Usage:
    python update_priorities.py [--limit N] [--dry-run]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.google_sheets import SUIVI_AMB_COLS, SHEET_ID as SPREADSHEET_ID  # noqa: E402
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402

SHEET_NAME = "Suivi_Amb"

# Keywords that map to priorities (searched case-insensitive in col K text)
HIGH_KEYWORDS = ["répondre", "préparer commande", "appeler", "envoyer code"]
MEDIUM_KEYWORDS = ["relancer", "réagir story", "contacter manager", "demander avis"]
GOOD_KEYWORDS = ["ras"]


def ts():
    return datetime.now().strftime("%H:%M:%S")


def keyword_priority(action_text):
    """Check action text for priority keywords. Returns priority or None."""
    text = action_text.lower().strip()
    if not text:
        return None

    for kw in HIGH_KEYWORDS:
        if kw in text:
            return "high"
    for kw in MEDIUM_KEYWORDS:
        if kw in text:
            return "medium"
    for kw in GOOD_KEYWORDS:
        if kw in text:
            return "good"
    return None


def determine_priority(action, last_sender, has_thread):
    """Determine priority based on action keywords and last DM sender."""
    # Keyword-based override first
    kw_prio = keyword_priority(action)
    if kw_prio:
        # But if action says RAS and last msg is from influencer → bump to high
        if kw_prio == "good" and last_sender == "influencer":
            return "high"
        return kw_prio

    # DM-based priority
    if last_sender == "influencer":
        return "high"
    elif last_sender == "us":
        return "medium"
    elif not has_thread:
        return "medium"
    else:
        return "good"


def main():
    parser = argparse.ArgumentParser(description="Update priorities in Suivi_Amb")
    parser.add_argument("--limit", type=int, default=None, help="Max accounts to process")
    parser.add_argument("--dry-run", action="store_true", help="Print without updating sheet")
    parser.add_argument("--statut-filter", default=None,
                        help="Only process accounts with this statut (default: all non-Out)")
    args = parser.parse_args()

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("ERROR: gspread not installed.")
        sys.exit(1)

    # Read sheet
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "/Users/antoinechabrat/.config/google-service-account.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    all_data = ws.get_all_values()

    # New layout: row 1 = headers, data from row 2
    # I=8: Compte@, J=9: Statut, K=10: Action/Commentaire, L=11: Priorité, AG=32: ID Influ
    data_rows = all_data[1:]

    # Filter accounts
    candidates = []
    for i, row in enumerate(data_rows):
        username = row[SUIVI_AMB_COLS["username"]].strip() if len(row) > SUIVI_AMB_COLS["username"] else ""
        statut = row[SUIVI_AMB_COLS["statut"]].strip() if len(row) > SUIVI_AMB_COLS["statut"] else ""
        action = row[SUIVI_AMB_COLS["action"]].strip() if len(row) > SUIVI_AMB_COLS["action"] else ""
        current_prio = row[SUIVI_AMB_COLS["priorite"]].strip() if len(row) > SUIVI_AMB_COLS["priorite"] else ""
        id_influ = row[SUIVI_AMB_COLS["id_influ"]].strip() if len(row) > SUIVI_AMB_COLS["id_influ"] else ""

        if not username:
            continue
        if statut == "Out":
            continue
        if args.statut_filter and statut != args.statut_filter:
            continue

        candidates.append({
            "row": i + 2,  # sheet row (1-indexed + header)
            "username": username,
            "statut": statut,
            "action": action,
            "current_prio": current_prio,
            "id_influ": id_influ,
        })

    if args.limit:
        candidates = candidates[:args.limit]

    print(f"[{ts()}] Processing {len(candidates)} accounts")

    ig_client = get_ig_client("impulse")
    ig_client.request_timeout = 1
    our_user_id = str(ig_client.user_id)
    print(f"[{ts()}] Logged in as impulse (id={our_user_id})")

    updates = []
    for idx, acct in enumerate(candidates, 1):
        username = acct["username"]
        print(f"[{ts()}] [{idx}/{len(candidates)}] @{username}", end="")

        try:
            # Get user ID (prefer stored ID)
            if acct["id_influ"]:
                user_id = acct["id_influ"]
            else:
                user_id = str(ig_client.user_id_from_username(username))

            thread = ig_client.direct_thread_by_participants([int(user_id)])
            if isinstance(thread, dict):
                inner = thread.get("thread") or {}
                thread_id = inner.get("thread_id") or inner.get("id") or thread.get("id")
            else:
                thread_id = getattr(thread, "id", None) or getattr(thread, "thread_id", None)

            if not thread_id:
                priority = determine_priority(acct["action"], None, False)
                print(f" → no thread → {priority}")
                updates.append((acct["row"], priority))
                sleep_random(2, 4)
                continue

            messages = ig_client.direct_messages(str(thread_id), 3)
            if not messages:
                priority = determine_priority(acct["action"], None, True)
                print(f" → no messages → {priority}")
                updates.append((acct["row"], priority))
                sleep_random(2, 4)
                continue

            last_msg = messages[0]
            last_sender_id = str(getattr(last_msg, 'user_id', ''))
            last_sender = "us" if last_sender_id == our_user_id else "influencer"

            priority = determine_priority(acct["action"], last_sender, True)
            changed = priority != acct["current_prio"]
            marker = " ←" if changed else ""
            print(f" → last={last_sender} → {priority}{marker}")
            updates.append((acct["row"], priority))

        except Exception as e:
            print(f" → ERROR: {e}")
            # Keep existing priority on error
            if acct["current_prio"]:
                updates.append((acct["row"], acct["current_prio"]))

        if idx < len(candidates):
            sleep_random(2, 4)

    # Apply updates
    if args.dry_run:
        print(f"\n[DRY RUN] Would update {len(updates)} priorities")
        for row, prio in updates[:20]:
            print(f"  Row {row} → {prio}")
        return

    print(f"\nUpdating {len(updates)} priorities in sheet...")
    # Batch update col L
    if updates:
        cells_to_update = [{'range': f'L{row}', 'values': [[prio]]} for row, prio in updates]
        ws.batch_update(cells_to_update)

    print("Done!")

    # Summary
    from collections import Counter
    counts = Counter(p for _, p in updates)
    print(f"\nSummary: {dict(counts)}")


if __name__ == "__main__":
    main()
