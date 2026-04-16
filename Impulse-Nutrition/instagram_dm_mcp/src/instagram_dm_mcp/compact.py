"""Compact helpers shared by the MCP server and the debug CLI scripts.

Strip instagrapi payloads down to the fields that actually matter for
conversation tracking, plus pre-computed thread/message signals used by
the `/instagram-dm` skill (welcome codes, days since last reply,
voice/raven media flags, needs_action).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone


_WELCOME_CODE_RE = re.compile(
    r'\b([A-Z]{2,}25)\b'           # ACHAB25, PGAU25, any {NOM}25
    r'|-25\s*%'                     # "-25%"
    r'|code\s+(?:perso|welcome|exclusif)',  # "code perso", "code welcome"
    re.IGNORECASE,
)


def _compact_message(msg: dict) -> dict:
    """Strip a message dict down to the fields that matter for conversation tracking."""
    item_type = msg.get("item_type", "text")
    compact = {
        "id": msg.get("id"),
        "user_id": msg.get("user_id"),
        "timestamp": msg.get("timestamp"),
        "text": msg.get("text"),
        "item_type": item_type,
        "is_sent_by_viewer": msg.get("is_sent_by_viewer"),
    }
    if msg.get("shared_post_url"):
        compact["shared_post_url"] = msg["shared_post_url"]
    if msg.get("shared_post_code"):
        compact["shared_post_code"] = msg["shared_post_code"]
    if item_type in ("voice_media", "raven_media"):
        compact["media_note"] = f"{item_type} - contenu inaccessible via API"
    return compact


def _sort_messages_newest_first(messages: list) -> list:
    """Sort message dicts by timestamp descending (newest first).

    Works with both raw datetime objects and serialised strings — anything
    that supports ``>`` comparison via ``sorted``.
    """
    return sorted(messages, key=lambda m: m.get("timestamp") or "", reverse=True)


def _compact_user(user: dict) -> dict:
    """Strip a user dict to username, full_name, pk."""
    return {
        "username": user.get("username"),
        "full_name": user.get("full_name"),
        "pk": user.get("pk"),
    }


def _parse_timestamp(ts) -> datetime | None:
    """Best-effort parse of an instagrapi timestamp (datetime or str)."""
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    if isinstance(ts, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue
    return None


def _scan_messages(messages: list[dict]) -> dict:
    """Scan a list of message dicts and return pre-computed signals.

    Expects messages sorted newest-first (index 0 = most recent).
    """
    scan: dict = {
        "welcome_code_found": None,
        "welcome_code_date": None,
        "welcome_code_sender": None,
        "has_voice_media": False,
        "has_raven_media": False,
        "voice_media_count": 0,
        "raven_media_count": 0,
        "last_msg_is_from_viewer": None,
        "last_msg_date": None,
        "last_impulse_msg_date": None,
        "days_since_last_impulse_msg": None,
        "impulse_messages_count": 0,
        "prospect_messages_count": 0,
        "total_messages": len(messages),
    }

    now = datetime.now(timezone.utc)

    for i, msg in enumerate(messages):
        is_viewer = msg.get("is_sent_by_viewer")
        item_type = msg.get("item_type", "text")
        text = msg.get("text") or ""
        ts = _parse_timestamp(msg.get("timestamp"))

        if i == 0:
            scan["last_msg_is_from_viewer"] = bool(is_viewer)
            scan["last_msg_date"] = str(msg.get("timestamp", ""))

        if is_viewer:
            scan["impulse_messages_count"] += 1
            if ts and scan["last_impulse_msg_date"] is None:
                scan["last_impulse_msg_date"] = str(msg.get("timestamp", ""))
                delta = now - ts
                scan["days_since_last_impulse_msg"] = delta.days
        else:
            scan["prospect_messages_count"] += 1

        if item_type == "voice_media":
            scan["has_voice_media"] = True
            scan["voice_media_count"] += 1
        elif item_type == "raven_media":
            scan["has_raven_media"] = True
            scan["raven_media_count"] += 1

        if text and _WELCOME_CODE_RE.search(text):
            code_match = re.search(r'\b([A-Z]{2,}25)\b', text)
            if code_match:
                scan["welcome_code_found"] = code_match.group(1)
                scan["welcome_code_date"] = str(msg.get("timestamp", ""))
                scan["welcome_code_sender"] = "impulse" if is_viewer else "prospect"

    scan["needs_action"] = (
        scan["last_msg_is_from_viewer"] is False
    )

    return scan


def _compute_thread_signals(last_msg: dict | None, last_activity_at) -> dict:
    """Compute thread-level signals from the last message for list_chats summary."""
    signals: dict = {
        "last_msg_from_us": None,
        "last_msg_from_us_date": None,
        "days_since_last_impulse_msg": None,
        "needs_action": None,
    }
    if not last_msg:
        return signals

    is_viewer = last_msg.get("is_sent_by_viewer")
    signals["last_msg_from_us"] = bool(is_viewer)
    signals["needs_action"] = not bool(is_viewer)

    ts = _parse_timestamp(last_msg.get("timestamp"))
    if ts:
        signals["last_msg_from_us_date"] = ts.strftime("%d/%m/%Y")
        delta = datetime.now(timezone.utc) - ts
        if is_viewer:
            signals["days_since_last_impulse_msg"] = delta.days

    return signals
