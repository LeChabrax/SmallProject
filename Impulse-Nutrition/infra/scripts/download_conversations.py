#!/usr/bin/env python3
"""Bulk-download Instagram DM threads for every tracked ambassador.

Reads the usernames from `Suivi_Amb` (col I) and `Suivi_Paid` (col J =
`@InstaName`), skips `statut = Out`, and downloads the full DM thread for
each one into `infra/data/conversations/<username>.json`.

The resulting corpus is consumed by:
    - infra/scripts/extract_tone.py            → regenerates personality.md
    - infra/scripts/extract_response_templates.py → enriches real_response_examples.md

The `infra/data/conversations/` folder is gitignored (private DMs).

Usage
-----
    # Dry run: print the list without downloading
    python3 infra/scripts/download_conversations.py --dry-run

    # First N usernames (test)
    python3 infra/scripts/download_conversations.py --limit 10

    # Full run, skip usernames already downloaded
    python3 infra/scripts/download_conversations.py

    # Force re-download of everything
    python3 infra/scripts/download_conversations.py --force
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from infra.common.google_sheets import (  # noqa: E402
    SHEET_ID,
    SUIVI_AMB_COLS,
    SUIVI_PAID_COLS,
    get_worksheet,
)
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "conversations"
INDEX_PATH = DATA_DIR / "_index.json"
PROGRESS_PATH = DATA_DIR / "_progress.json"

MESSAGES_PER_THREAD = 300

logger = logging.getLogger("download_conversations")


# -------------------------------------------------------------------------
# Sheet loading
# -------------------------------------------------------------------------


def _load_tracked_usernames() -> List[Tuple[str, str, str]]:
    """Return `[(username, source_tab, statut), ...]` from the Sheet.

    Dedupes by username (Suivi_Amb wins if also in Suivi_Paid).
    """
    seen: Dict[str, Tuple[str, str, str]] = {}

    # Suivi_Amb — primary source.
    try:
        ws_amb = get_worksheet("Suivi_Amb", SHEET_ID)
        rows = ws_amb.get_all_values()[3:]  # skip 3 header rows
        for row in rows:
            if len(row) <= SUIVI_AMB_COLS["username"]:
                continue
            username = row[SUIVI_AMB_COLS["username"]].strip().lstrip("@")
            statut = (
                row[SUIVI_AMB_COLS["statut"]].strip()
                if len(row) > SUIVI_AMB_COLS["statut"]
                else ""
            )
            if not username:
                continue
            if statut.lower() == "out":
                continue
            seen[username.lower()] = (username, "Suivi_Amb", statut)
    except Exception as e:
        logger.warning("could not read Suivi_Amb: %s", e)

    # Suivi_Paid — contract partners.
    try:
        ws_paid = get_worksheet("Suivi_Paid", SHEET_ID)
        rows = ws_paid.get_all_values()[3:]
        for row in rows:
            if len(row) <= SUIVI_PAID_COLS["insta_name"]:
                continue
            username = row[SUIVI_PAID_COLS["insta_name"]].strip().lstrip("@")
            statut = (
                row[SUIVI_PAID_COLS["statut_deal"]].strip()
                if len(row) > SUIVI_PAID_COLS["statut_deal"]
                else ""
            )
            if not username or statut.lower() == "out":
                continue
            seen.setdefault(username.lower(), (username, "Suivi_Paid", statut))
    except Exception as e:
        logger.warning("could not read Suivi_Paid: %s", e)

    return sorted(seen.values(), key=lambda t: t[0].lower())


# -------------------------------------------------------------------------
# Progress / index I/O
# -------------------------------------------------------------------------


def _load_progress() -> Dict[str, Any]:
    if PROGRESS_PATH.exists():
        with PROGRESS_PATH.open() as f:
            return json.load(f)
    return {"done": [], "errors": {}, "last_run": None}


def _save_progress(progress: Dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS_PATH.open("w") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def _load_index() -> Dict[str, Any]:
    if INDEX_PATH.exists():
        with INDEX_PATH.open() as f:
            return json.load(f)
    return {}


def _save_index(index: Dict[str, Any]) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


# -------------------------------------------------------------------------
# Instagram download
# -------------------------------------------------------------------------


def _serialize_message(msg: Any) -> Dict[str, Any]:
    """Convert an instagrapi DirectMessage into a compact dict."""
    try:
        d = msg.dict() if hasattr(msg, "dict") else dict(msg)
    except Exception:
        d = {}

    ts = d.get("timestamp") or getattr(msg, "timestamp", None)
    if hasattr(ts, "isoformat"):
        date_iso = ts.isoformat()
        ts_micro = int(ts.timestamp() * 1_000_000)
    elif isinstance(ts, (int, float)):
        ts_micro = int(ts)
        date_iso = datetime.fromtimestamp(
            ts_micro / 1_000_000, tz=timezone.utc
        ).isoformat()
    else:
        date_iso = None
        ts_micro = None

    return {
        "id": d.get("id") or getattr(msg, "id", None),
        "ts": ts_micro,
        "date_iso": date_iso,
        "is_sent_by_viewer": bool(d.get("is_sent_by_viewer")),
        "user_id": d.get("user_id") or getattr(msg, "user_id", None),
        "item_type": d.get("item_type") or getattr(msg, "item_type", None),
        "text": d.get("text") or getattr(msg, "text", None),
        "reactions": d.get("reactions"),
    }


def _download_one(
    client,
    username: str,
    source: str,
    statut: str,
    out_path: Path,
) -> Dict[str, Any]:
    """Download a single thread, write JSON file, return index entry."""
    user_id = client.user_id_from_username(username)
    thread = client.direct_thread_by_participants([int(user_id)])
    thread_dict = thread if isinstance(thread, dict) else {}
    inner = thread_dict.get("thread") or {}
    thread_id = (
        inner.get("thread_id")
        or inner.get("id")
        or thread_dict.get("id")
        or getattr(thread, "id", None)
        or getattr(thread, "thread_id", None)
    )
    if not thread_id:
        raise RuntimeError(f"no thread_id for {username}")

    raw_messages = client.direct_messages(int(thread_id), amount=MESSAGES_PER_THREAD)
    messages = [_serialize_message(m) for m in raw_messages]
    messages.sort(key=lambda m: m["ts"] or 0)

    payload = {
        "username": username,
        "source_tab": source,
        "statut_at_download": statut,
        "user_id": str(user_id),
        "thread_id": str(thread_id),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "messages": messages,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    nb_sent = sum(1 for m in messages if m["is_sent_by_viewer"])
    return {
        "username": username,
        "source": source,
        "statut": statut,
        "thread_id": str(thread_id),
        "user_id": str(user_id),
        "nb_messages": len(messages),
        "nb_sent_by_me": nb_sent,
        "nb_received": len(messages) - nb_sent,
        "first_date": messages[0]["date_iso"] if messages else None,
        "last_date": messages[-1]["date_iso"] if messages else None,
        "last_sender": (
            "me" if messages and messages[-1]["is_sent_by_viewer"] else "them"
        ),
        "downloaded_at": payload["downloaded_at"],
    }


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------


def _already_downloaded(username: str) -> bool:
    return (DATA_DIR / f"{username}.json").exists()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--skip", nargs="*", default=[], help="usernames to skip"
    )
    args = parser.parse_args()

    usernames = _load_tracked_usernames()
    skip_set: Set[str] = {u.lower() for u in args.skip}
    if skip_set:
        usernames = [u for u in usernames if u[0].lower() not in skip_set]
    if args.limit:
        usernames = usernames[: args.limit]

    print(f"Candidates : {len(usernames)} usernames")
    if args.dry_run:
        for username, source, statut in usernames:
            already = "[done]" if _already_downloaded(username) else "[todo]"
            print(f"  {already} {username:30} {source:12} {statut}")
        return 0

    client = get_ig_client("impulse")
    progress = _load_progress()
    index = _load_index()

    processed = 0
    for i, (username, source, statut) in enumerate(usernames, start=1):
        out_path = DATA_DIR / f"{username}.json"
        if out_path.exists() and not args.force:
            print(f"  [{i:3d}/{len(usernames)}] skip {username} (already DL)")
            continue

        print(f"  [{i:3d}/{len(usernames)}] download {username} ({source}, {statut})")
        try:
            entry = _download_one(client, username, source, statut, out_path)
            index[username] = entry
            progress.setdefault("done", []).append(username)
            progress["errors"].pop(username, None)
            processed += 1
        except Exception as e:
            tb = traceback.format_exc(limit=3)
            logger.warning("failed %s: %s", username, e)
            progress.setdefault("errors", {})[username] = {
                "error": str(e),
                "traceback": tb,
                "at": datetime.now(timezone.utc).isoformat(),
            }

        if processed and processed % 5 == 0:
            _save_progress(progress)
            _save_index(index)

        sleep_random(3, 8)
        if processed and processed % 10 == 0:
            print("  …cooling down")
            sleep_random(15, 30)

    progress["last_run"] = datetime.now(timezone.utc).isoformat()
    _save_progress(progress)
    _save_index(index)
    print(f"Done. Downloaded {processed} new threads.")
    print(f"Errors : {len(progress.get('errors') or {})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
