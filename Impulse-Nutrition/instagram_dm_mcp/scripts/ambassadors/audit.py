"""
Audit ambassadeurs — remplit cols R, U, V, X, Y du Suivi_Amb :
  R (Bio Impulse)  : "oui" / "non" — présence de "impulse" ou du code affilié dans la bio
  U (Followers k)  : Nombre de followers formaté en milliers (ex: 6,4) — TOUS sauf Out
  V (Date)         : Date du premier message envoyé par Antoine (DD/MM/YYYY) — sauf In-cold et Out
  X (Nb Story)     : Nombre de stories partagées en DM (pagination complète) — sauf In-cold et Out
  Y (Nb post)      : Nombre de posts/reels partagés en DM (pagination complète) — sauf In-cold et Out

Populations :
  - U seulement    : In-cold inclus, Out exclus
  - U + V + X + Y  : In-cold exclus, Out exclus

Usage :
    python audit_ambassadors.py [--limit N] [--dry-run] [--debug] [--skip-bio]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.google_sheets import SUIVI_AMB_COLS, SHEET_ID as SPREADSHEET_ID  # noqa: E402
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402
from infra.common.logging_utils import get_logger  # noqa: E402

log = get_logger(
    "ambassadors_audit",
    log_dir=Path(__file__).resolve().parents[2] / "data" / "logs",
)

SHEET_NAME = "Suivi_Amb"

# item_types classification
STORY_ITEM_TYPES = {"story_share", "xma_story_share", "xma_reel_mention"}
POST_ITEM_TYPES = {
    "clip", "media_share", "reel_share", "xma_media_share", "post_share",
}


def ts():
    return datetime.now().strftime("%H:%M:%S")


def format_followers(count):
    """Format follower count in thousands with comma (e.g. 6400 → '6,4')."""
    if count is None or count == 0:
        return ""
    k = count / 1000
    if k >= 10:
        return str(int(round(k)))
    else:
        return f"{k:.1f}".replace(".", ",")


def check_bio_impulse(user_info, code_affiliation):
    """Check if 'impulse' or the affiliate code appears in the user's bio."""
    bio = (user_info.biography or "").lower()
    external_url = str(user_info.external_url or "").lower()

    has_impulse = "impulse" in bio or "impulse" in external_url

    has_code = False
    if code_affiliation:
        code_lower = code_affiliation.lower().strip()
        if code_lower and (code_lower in bio or code_lower in external_url):
            has_code = True

    return "oui" if (has_impulse or has_code) else "non"


def analyze_thread(ig_client, thread_id, our_user_id, debug=False):
    """Paginate through ALL messages in thread.

    Returns (story_count, post_count, first_sent_date) where first_sent_date
    is the date of the oldest message sent by us (DD/MM/YYYY).
    """
    story_count = 0
    post_count = 0
    first_sent_ts = None  # oldest timestamp of our messages
    cursor = None

    while True:
        try:
            if cursor:
                messages = ig_client.direct_messages(str(thread_id), 100, cursor)
            else:
                messages = ig_client.direct_messages(str(thread_id), 100)
        except Exception as e:
            print(f" [paginate error: {e}]", end="")
            break

        if not messages:
            break

        for msg in messages:
            sender_id = str(getattr(msg, 'user_id', ''))
            item_type = str(getattr(msg, 'item_type', '') or "")
            ts_val = getattr(msg, 'timestamp', None)

            if sender_id != our_user_id:
                if debug and item_type not in ("text", "action_log", "like", ""):
                    print(f"\n    [debug] item_type={item_type!r}")
                if item_type in STORY_ITEM_TYPES:
                    story_count += 1
                elif item_type in POST_ITEM_TYPES:
                    post_count += 1
            else:
                # Track oldest message sent by us
                if ts_val is not None:
                    if first_sent_ts is None or ts_val < first_sent_ts:
                        first_sent_ts = ts_val

        # Pagination: if fewer than requested, we've reached the end
        if len(messages) < 100:
            break

        # Use last message ID as cursor for next page (older messages)
        last_msg = messages[-1]
        next_cursor = getattr(last_msg, 'id', None)
        if not next_cursor:
            break
        cursor = next_cursor

    # Format first sent date
    first_sent_date = ""
    if first_sent_ts is not None:
        try:
            if isinstance(first_sent_ts, (int, float)):
                # Microsecond timestamps from Instagram
                if first_sent_ts > 1e12:
                    dt = datetime.fromtimestamp(first_sent_ts / 1e6)
                else:
                    dt = datetime.fromtimestamp(first_sent_ts)
            else:
                # datetime object (instagrapi modern)
                dt = first_sent_ts
            first_sent_date = dt.strftime("%d/%m/%Y")
        except Exception:
            first_sent_date = ""

    return story_count, post_count, first_sent_date


def get_thread_id(ig_client, user_id_str):
    """Resolve thread ID from participant user ID."""
    try:
        thread = ig_client.direct_thread_by_participants([int(user_id_str)])
        if isinstance(thread, dict):
            inner = thread.get("thread") or {}
            return inner.get("thread_id") or inner.get("id") or thread.get("id")
        else:
            return getattr(thread, "id", None) or getattr(thread, "thread_id", None)
    except Exception as e:
        print(f" [thread error: {e}]", end="")
        return None


def main():
    parser = argparse.ArgumentParser(description="Audit ambassadors — update cols U, V, X, Y (and R)")
    parser.add_argument("--limit", type=int, default=None, help="Max accounts to process")
    parser.add_argument("--dry-run", action="store_true", help="Print without updating sheet")
    parser.add_argument("--debug", action="store_true", help="Print item_types found in DMs")
    parser.add_argument("--skip-bio", action="store_true", help="Skip col R (bio check) — faster")
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

    # Row 1 = headers, data from row 2
    # I=8: Compte@, J=9: Statut, N=13: Code affiliation, AG=32: ID Influ
    data_rows = all_data[1:]

    EXCLUDED_FROM_ALL = {"Out"}
    EXCLUDED_FROM_THREAD = {"In-cold", "Out"}  # skip V/X/Y for these

    candidates = []
    for i, row in enumerate(data_rows):
        username = row[SUIVI_AMB_COLS["username"]].strip() if len(row) > SUIVI_AMB_COLS["username"] else ""
        statut = row[SUIVI_AMB_COLS["statut"]].strip() if len(row) > SUIVI_AMB_COLS["statut"] else ""
        code_affiliation = row[SUIVI_AMB_COLS["code_affilie"]].strip() if len(row) > SUIVI_AMB_COLS["code_affilie"] else ""
        id_influ = row[SUIVI_AMB_COLS["id_influ"]].strip() if len(row) > SUIVI_AMB_COLS["id_influ"] else ""

        if not username or username.lower() == "compte @":
            continue
        if statut in EXCLUDED_FROM_ALL:
            continue

        candidates.append({
            "row": i + 2,
            "username": username,
            "statut": statut,
            "code_affiliation": code_affiliation,
            "id_influ": id_influ,
            "skip_thread": statut in EXCLUDED_FROM_THREAD,
        })

    if args.limit:
        candidates = candidates[:args.limit]

    in_cold_count = sum(1 for c in candidates if c["skip_thread"])
    full_count = len(candidates) - in_cold_count
    print(f"[{ts()}] Auditing {len(candidates)} ambassadors ({full_count} full U/V/X/Y, {in_cold_count} U-only In-cold)")

    ig_client = get_ig_client("impulse")
    ig_client.request_timeout = 1
    our_user_id = str(ig_client.user_id)
    print(f"[{ts()}] Logged in as impulse (id={our_user_id})")
    log.info("audit starting on %d candidates (impulse user_id=%s)", len(candidates), our_user_id)

    results = []
    bio_yes = 0
    bio_no = 0
    total_stories = 0
    total_posts = 0

    for idx, acct in enumerate(candidates, 1):
        username = acct["username"]
        skip_thread = acct["skip_thread"]
        print(f"[{ts()}] [{idx}/{len(candidates)}] @{username} ({acct['statut']})", end="")

        # 1. Get user info (bio + followers)
        followers_str = ""
        bio_result = "erreur"
        try:
            user_info = ig_client.user_info_by_username(username)
            followers_str = format_followers(user_info.follower_count)
            if args.skip_bio:
                bio_result = None
            else:
                bio_result = check_bio_impulse(user_info, acct["code_affiliation"])
        except Exception as e:
            bio_result = f"erreur: {e}" if not args.skip_bio else None

        if bio_result == "oui":
            bio_yes += 1
        elif bio_result == "non":
            bio_no += 1

        sleep_random(1, 2)

        # 2. DM analysis (skip for In-cold)
        story_count = 0
        post_count = 0
        first_date = ""

        if not skip_thread:
            user_id = acct["id_influ"]
            if not user_id:
                try:
                    user_id = str(ig_client.user_id_from_username(username))
                except Exception:
                    user_id = ""

            if user_id:
                thread_id = get_thread_id(ig_client, user_id)
                if thread_id:
                    story_count, post_count, first_date = analyze_thread(
                        ig_client, thread_id, our_user_id, debug=args.debug
                    )

        total_stories += story_count
        total_posts += post_count

        tag = " [U only]" if skip_thread else f" → date={first_date or '-'}, stories={story_count}, posts={post_count}"
        print(f" → followers={followers_str or '-'}{', bio=' + bio_result if bio_result is not None else ''}{tag}")

        results.append({
            "row": acct["row"],
            "bio": bio_result,
            "followers": followers_str,
            "stories": story_count,
            "posts": post_count,
            "first_date": first_date,
            "skip_thread": skip_thread,
        })

        if idx < len(candidates):
            sleep_random(2, 4)

    # Apply updates
    if args.dry_run:
        print(f"\n[DRY RUN] Would update {len(results)} rows")
        if not args.skip_bio:
            print(f"Bio Impulse: {bio_yes} oui, {bio_no} non")
        print(f"Total stories: {total_stories}, Total posts: {total_posts}")
        return

    print(f"\nUpdating {len(results)} rows in sheet...")
    updates = []
    for r in results:
        row = r["row"]
        # U: followers for everyone
        updates.append({"range": f"U{row}", "values": [[r["followers"]]]})
        # R: bio (unless --skip-bio)
        if r["bio"] is not None:
            updates.append({"range": f"R{row}", "values": [[r["bio"]]]})
        # V, X, Y: only for non-In-cold
        if not r["skip_thread"]:
            updates.append({"range": f"V{row}", "values": [[r["first_date"]]]})
            updates.append({"range": f"X{row}", "values": [[str(r["stories"]) if r["stories"] else ""]]})
            updates.append({"range": f"Y{row}", "values": [[str(r["posts"]) if r["posts"] else ""]]})

    ws.batch_update(updates)

    print("Done!")
    print(f"\nSummary:")
    if not args.skip_bio:
        print(f"  Bio Impulse: {bio_yes} oui / {bio_no} non")
    print(f"  Total stories shared: {total_stories}")
    print(f"  Total posts shared: {total_posts}")
    print(f"  Accounts audited: {len(results)} ({full_count} full, {in_cold_count} U-only)")


if __name__ == "__main__":
    main()
