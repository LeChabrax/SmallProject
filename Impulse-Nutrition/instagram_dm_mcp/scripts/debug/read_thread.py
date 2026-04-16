"""Debug probe: dump the 10 latest messages of a given thread."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from instagram_dm_mcp.compact import _sort_messages_newest_first  # noqa: E402
from infra.common.instagram_client import get_ig_client  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("Usage: python read_thread.py <thread_id>")
        return

    thread_id = sys.argv[1]
    client = get_ig_client("impulse")

    print(f"Fetching messages for thread {thread_id}...")
    messages = client.direct_messages(thread_id, amount=10)
    msg_dicts = [
        m.dict() if hasattr(m, "dict") else (m if isinstance(m, dict) else {})
        for m in messages
    ]
    msg_dicts = _sort_messages_newest_first(msg_dicts)

    for m in msg_dicts:
        sender = "Us" if m.get("is_sent_by_viewer") else "Them"
        text = m.get("text") or f"[{m.get('item_type')}]"
        print(f"[{m.get('timestamp')}] {sender}: {text}")


if __name__ == "__main__":
    main()
