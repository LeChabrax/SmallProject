"""Debug probe: fetch 20 latest DM threads and print a compact summary."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from instagram_dm_mcp.compact import (  # noqa: E402
    _compact_message,
    _compact_user,
    _compute_thread_signals,
)
from infra.common.instagram_client import get_ig_client  # noqa: E402


def main():
    client = get_ig_client("impulse")

    print("Fetching 20 threads...")
    threads = client.direct_threads(amount=20)

    results = []
    for t in threads:
        td = t.dict() if hasattr(t, "dict") else t
        users = td.get("users", [])
        user_summaries = [_compact_user(u) for u in users]
        thread_id = td.get("id")

        last_msg = None
        try:
            messages = client.direct_messages(thread_id, amount=1)
            if messages:
                msg_dicts = [
                    m.dict() if hasattr(m, "dict") else (m if isinstance(m, dict) else {})
                    for m in messages
                ]
                last_msg = _compact_message(msg_dicts[0])
        except Exception:
            pass

        results.append({
            "thread_id": thread_id,
            "thread_title": td.get("thread_title"),
            "users": user_summaries,
            "last_message": last_msg,
            "computed": _compute_thread_signals(last_msg, td.get("last_activity_at")),
        })

    print("\n--- INBOX STATUS ---\n")
    for res in results:
        usernames = [u["username"] for u in res["users"]]
        title = res["thread_title"] or ", ".join(usernames)
        last_msg_text = res["last_message"]["text"] if res["last_message"] and res["last_message"].get("text") else "[Media/Other]"
        needs_action = "⚠️ ACTION" if res["computed"]["needs_action"] else "✅ OK"

        print(f"[{needs_action}] {title} (ID: {res['thread_id']})")
        if res["last_message"]:
            sender = "Us" if res["last_message"]["is_sent_by_viewer"] else "Them"
            print(f"  Last ({sender}): {last_msg_text[:100]}")
        print("-" * 20)


if __name__ == "__main__":
    main()
