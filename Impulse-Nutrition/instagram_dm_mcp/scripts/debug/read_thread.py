
import os
import sys
import json
from pathlib import Path
from instagrapi import Client
from dotenv import load_dotenv

# Add current dir and instagram_dm_mcp/src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from instagram_dm_mcp.compact import _compact_message, _sort_messages_newest_first

load_dotenv(Path(__file__).parent.parent.parent / ".env")

USERNAME = os.getenv("INSTAGRAM_USERNAME", "impulse_nutrition_fr")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = Path(__file__).parent.parent.parent / "data" / "sessions" / f"{USERNAME}_session.json"

def main():
    if len(sys.argv) < 2:
        print("Usage: python read_thread.py <thread_id>")
        return

    thread_id = sys.argv[1]
    
    client = Client()
    if SESSION_FILE.exists():
        client.load_settings(SESSION_FILE)
    client.login(USERNAME, PASSWORD)

    print(f"Fetching messages for thread {thread_id}...")
    messages = client.direct_messages(thread_id, amount=10)
    msg_dicts = [
        m.dict() if hasattr(m, 'dict') else (m if isinstance(m, dict) else {})
        for m in messages
    ]
    msg_dicts = _sort_messages_newest_first(msg_dicts)
    
    for m in msg_dicts:
        is_viewer = m.get("is_sent_by_viewer")
        sender = "Us" if is_viewer else "Them"
        text = m.get("text") or f"[{m.get('item_type')}]"
        ts = m.get("timestamp")
        print(f"[{ts}] {sender}: {text}")

if __name__ == "__main__":
    main()
