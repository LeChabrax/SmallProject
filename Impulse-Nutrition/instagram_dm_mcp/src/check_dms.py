
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from instagrapi import Client
from dotenv import load_dotenv

# Add current dir to path
sys.path.append(str(Path(__file__).parent))
# Add repo root for common
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp_server import _compact_user, _compact_message, _sort_messages_newest_first, _compute_thread_signals

load_dotenv(Path(__file__).parent.parent.parent / ".env")

USERNAME = os.getenv("INSTAGRAM_USERNAME", "impulse_nutrition_fr")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = Path(__file__).parent.parent / "data" / "sessions" / f"{USERNAME}_session.json"

def main():
    client = Client()
    if SESSION_FILE.exists():
        print(f"Loading session from {SESSION_FILE}")
        client.load_settings(SESSION_FILE)
    
    try:
        client.login(USERNAME, PASSWORD)
        client.dump_settings(SESSION_FILE)
    except Exception as e:
        print(f"Login failed: {e}")
        return

    print(f"Fetching 20 threads for {USERNAME}...")
    threads = client.direct_threads(amount=20)
    
    results = []
    for t in threads:
        td = t.dict() if hasattr(t, 'dict') else t
        users = td.get("users", [])
        user_summaries = [_compact_user(u) for u in users]
        thread_id = td.get("id")
        
        last_msg = None
        try:
            messages = client.direct_messages(thread_id, amount=1)
            if messages:
                msg_dicts = [
                    m.dict() if hasattr(m, 'dict') else (m if isinstance(m, dict) else {})
                    for m in messages
                ]
                last_msg = _compact_message(msg_dicts[0])
        except Exception:
            pass
            
        summary = {
            "thread_id": thread_id,
            "thread_title": td.get("thread_title"),
            "users": user_summaries,
            "last_message": last_msg,
            "computed": _compute_thread_signals(last_msg, td.get("last_activity_at")),
        }
        results.append(summary)

    print("\n--- INBOX STATUS ---\n")
    for res in results:
        usernames = [u['username'] for u in res['users']]
        title = res['thread_title'] or ", ".join(usernames)
        last_msg_text = res['last_message']['text'] if res['last_message'] and res['last_message'].get('text') else "[Media/Other]"
        needs_action = "⚠️ ACTION" if res['computed']['needs_action'] else "✅ OK"
        
        print(f"[{needs_action}] {title} (ID: {res['thread_id']})")
        if res['last_message']:
            sender = "Us" if res['last_message']['is_sent_by_viewer'] else "Them"
            print(f"  Last ({sender}): {last_msg_text[:100]}")
        print("-" * 20)

if __name__ == "__main__":
    main()
