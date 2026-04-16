"""
Envoi de campagne générique — lit col M (Campagne) du Suivi_Amb,
envoie le message aux comptes éligibles, marque OK/SKIP.

Remplace send_promo_20pct.py avec un workflow plus propre :
1. Lit le sheet Suivi_Amb (col I=username, J=statut, M=campagne, AB=prénom)
2. Filtre : statut = "Produits envoyés", campagne = nom_campagne (non vide, pas OK, pas SKIP)
3. Pour chaque compte : qualifie la conversation, envoie le message, marque M = "... OK"

Usage :
    python run_campaign.py --campaign "Promo-20% mars" --message-file promo_message.txt [--dry-run]
    python run_campaign.py --campaign "Promo-20% mars" --message-template "Hello {prenom} ! ..." [--dry-run]
    python run_campaign.py --campaign "Promo-20% mars" --backfill send_promo_progress.json [--dry-run]
    python run_campaign.py --campaign "Promo-20% avril" --message-file msg.txt --all-active [--dry-run]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.dm_classifier import classify_last_message, QUESTION_SIGNALS, OK_SIGNALS  # noqa: E402
from infra.common.google_sheets import SUIVI_AMB_COLS, SHEET_ID as SPREADSHEET_ID  # noqa: E402
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402
from infra.common.logging_utils import get_logger  # noqa: E402

SHEET_NAME = "Suivi_Amb"

PROGRESS_FILE = Path(__file__).parent.parent.parent / "data" / "progress" / "campaign_progress.json"
PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
_logger = get_logger("campaign", log_dir=Path(__file__).parent.parent.parent / "data" / "logs")

NON_REPLY_TYPES = {
    "xma_reel_mention", "xma_story_share", "action_log",
    "reel_share", "story_share", "like", "reaction",
}


def log(msg: str):
    """Thin wrapper around the module logger; kept as a function so every
    existing `log(...)` call site (dozens of them) works unchanged."""
    _logger.info(msg)


def qualify_account(ig_client, username, our_user_id):
    """Check if it's safe to send a campaign message to this account."""
    try:
        user_id = ig_client.user_id_from_username(username)
        thread = ig_client.direct_thread_by_participants([int(user_id)])
        if isinstance(thread, dict):
            inner = thread.get("thread") or {}
            thread_id = inner.get("thread_id") or inner.get("id") or thread.get("id")
        else:
            thread_id = getattr(thread, "id", None) or getattr(thread, "thread_id", None)

        if not thread_id:
            return "send"  # No thread = no pending conversation

        messages = ig_client.direct_messages(str(thread_id), 5)
        if not messages:
            return "send"

        last_msg = messages[0]
        last_sender_id = str(getattr(last_msg, 'user_id', ''))
        is_from_us = (last_sender_id == our_user_id)
        item_type = str(getattr(last_msg, 'item_type', '') or "")

        if not is_from_us and item_type in NON_REPLY_TYPES:
            return "send"

        last_text = getattr(last_msg, 'text', '') or ""
        return classify_last_message(last_text, is_from_us)
    except Exception as e:
        log(f"  Qualification error: {e}")
        return "error"


def build_message(template: str, prenom: str) -> str:
    greeting = prenom.strip() if prenom.strip() else ""
    if greeting:
        return template.replace("{prenom}", greeting).replace("{greeting}", greeting)
    else:
        # Without first name: replace patterns with empty
        msg = template.replace("Hello {prenom} !", "Hello !")
        msg = msg.replace("Hello {greeting} !", "Hello !")
        msg = msg.replace("{prenom}", "").replace("{greeting}", "")
        return msg


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Run a campaign on Suivi_Amb")
    parser.add_argument("--campaign", required=True, help="Campaign name in col M (e.g. 'Promo-20%% mars')")
    parser.add_argument("--message-file", help="Path to message template file")
    parser.add_argument("--message-template", help="Inline message template (use {prenom} for first name)")
    parser.add_argument("--dry-run", action="store_true", help="Qualify only, don't send")
    parser.add_argument("--skip-qualify", action="store_true", help="Skip qualification, send to all")
    parser.add_argument("--delay", type=int, default=3, help="Minimum delay between accounts (seconds); sleep_random adds up to +2s jitter")
    parser.add_argument("--backfill", metavar="PROGRESS_JSON",
                        help="Backfill col M from a progress JSON (no Instagram login required)")
    parser.add_argument("--all-active", action="store_true",
                        help="Target all 'Produits envoyés' without pre-filling col M")
    parser.add_argument("--statut", default="Produits envoyés",
                        help="Required value in col J (Statut). Default 'Produits envoyés'. "
                             "Use 'In-cold' for KolSquare-style cold campaigns.")
    args = parser.parse_args()

    if not args.backfill and not args.message_file and not args.message_template and not args.dry_run:
        print("ERROR: Provide --message-file or --message-template (or --dry-run or --backfill)")
        sys.exit(1)

    # Load message template
    if args.message_file:
        with open(args.message_file, "r", encoding="utf-8") as f:
            message_template = f.read()
    elif args.message_template:
        message_template = args.message_template
    else:
        message_template = ""

    log("=" * 60)
    log(f"Campaign: {args.campaign}")
    log(f"Dry run: {args.dry_run}")
    log("=" * 60)

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("ERROR: gspread not installed. Run via Claude MCP or install gspread.")
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
    # I=8: Compte@, J=9: Statut, M=12: Campagne, AB=27: Prénom
    headers = all_data[0]
    data_rows = all_data[1:]

    campaign_name = args.campaign

    # Build username→row map for backfill and general use
    user_row_map = {}
    for i, row in enumerate(data_rows):
        username = row[8].strip() if len(row) > 8 else ""
        if username:
            user_row_map[username] = i + 2  # sheet row (1-indexed, +1 header)

    # --- Backfill mode: write col M from a progress JSON, then exit ---
    if args.backfill:
        with open(args.backfill, "r", encoding="utf-8") as f:
            prog = json.load(f)
        done_users = {u for u, v in prog.items() if v.get("done")}

        updates = []
        for username in done_users:
            row = user_row_map.get(username)
            if row:
                updates.append({"range": f"M{row}", "values": [[f"{campaign_name} OK"]]})
                log(f"  Backfill @{username} → row {row}")
            else:
                log(f"  WARNING: @{username} not found in sheet")

        if not args.dry_run:
            if updates:
                ws.batch_update(updates)
            log(f"Done — {len(updates)} rows updated in col M")
        else:
            log(f"[DRY RUN] Would update {len(updates)} rows")
        return

    eligible = []
    for i, row in enumerate(data_rows):
        username = row[8].strip() if len(row) > 8 else ""
        statut = row[9].strip() if len(row) > 9 else ""
        campagne = row[12].strip() if len(row) > 12 else ""
        prenom = row[SUIVI_AMB_COLS["prenom"]].strip() if len(row) > SUIVI_AMB_COLS["prenom"] else ""

        if not username:
            continue
        if statut != args.statut:
            continue

        if args.all_active:
            already_done = campagne in (f"{campaign_name} OK", f"{campaign_name} SKIP")
            if not already_done:
                eligible.append((i + 2, username, prenom))
        else:
            # Eligible if campagne matches exactly (not already OK or SKIP)
            if campagne == campaign_name:
                eligible.append((i + 2, username, prenom))

    log(f"Eligible accounts: {len(eligible)}")

    if not eligible:
        log("No eligible accounts found. Check campaign name and statut.")
        return

    ig_client = get_ig_client("impulse")
    ig_client.request_timeout = 1
    our_user_id = str(ig_client.user_id)
    log(f"Logged in as impulse (id={our_user_id})")

    # Raise the per-call timeout ceiling to 30s so long DM posts don't get
    # cut mid-flight. We do this on top of get_ig_client(), not inside it,
    # because other scripts share the helper and don't need this override.
    _orig_post = ig_client.private.post
    _orig_get = ig_client.private.get
    def _post_t(*a, **kw): kw.setdefault("timeout", 30); return _orig_post(*a, **kw)
    def _get_t(*a, **kw): kw.setdefault("timeout", 30); return _orig_get(*a, **kw)
    ig_client.private.post = _post_t
    ig_client.private.get = _get_t

    progress = load_progress()
    sent = 0
    skipped = 0
    errors = 0

    for idx, (sheet_row, username, prenom) in enumerate(eligible, 1):
        prog_key = f"{campaign_name}:{username}"
        if prog_key in progress and progress[prog_key].get("done"):
            log(f"[{idx}/{len(eligible)}] SKIP (already done): @{username}")
            continue

        log(f"\n[{idx}/{len(eligible)}] @{username} (row {sheet_row})")

        # Qualify
        if not args.skip_qualify:
            status = qualify_account(ig_client, username, our_user_id)
            log(f"  Qualification: {status}")
            if status == "flag":
                log(f"  → SKIP (influencer waiting for reply)")
                ws.update_acell(f"M{sheet_row}", f"{campaign_name} SKIP")
                progress[prog_key] = {"done": True, "status": "skip_flag"}
                save_progress(progress)
                skipped += 1
                sleep_random(args.delay, args.delay + 2)
                continue
            elif status == "review":
                log(f"  → SKIP (needs review)")
                ws.update_acell(f"M{sheet_row}", f"{campaign_name} SKIP")
                progress[prog_key] = {"done": True, "status": "skip_review"}
                save_progress(progress)
                skipped += 1
                sleep_random(args.delay, args.delay + 2)
                continue
            elif status == "error":
                errors += 1
                sleep_random(args.delay, args.delay + 2)
                continue

        if args.dry_run:
            log(f"  [DRY RUN] Would send message to @{username}")
            continue

        # Send message
        try:
            msg = build_message(message_template, prenom)
            user_id = ig_client.user_id_from_username(username)
            dm = ig_client.direct_send(msg, [user_id])
            log(f"  ✓ Message sent (id={getattr(dm, 'id', '?')})")

            # Mark as OK in sheet
            ws.update_acell(f"M{sheet_row}", f"{campaign_name} OK")
            progress[prog_key] = {"done": True, "status": "sent"}
            save_progress(progress)
            sent += 1
        except Exception as e:
            log(f"  ✗ Error: {e}")
            errors += 1
            progress[prog_key] = {"done": False, "error": str(e)}
            save_progress(progress)

        if idx < len(eligible):
            sleep_random(args.delay, args.delay + 2)

    log(f"\n{'='*60}")
    log(f"DONE — Sent: {sent}, Skipped: {skipped}, Errors: {errors}")
    log(f"{'='*60}")


if __name__ == "__main__":
    main()
