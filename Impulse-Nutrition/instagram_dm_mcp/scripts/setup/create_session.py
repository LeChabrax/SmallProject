from instagrapi import Client
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

SESSION_DIR = Path(__file__).parent.parent.parent / "data" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Try with web API instead of mobile API
cl = Client()
cl.delay_range = [2, 5]

# Use a recent Instagram app version
cl.set_settings({
    "uuids": {
        "phone_id": cl.generate_uuid(),
        "uuid": cl.generate_uuid(),
        "client_session_id": cl.generate_uuid(),
        "advertising_id": cl.generate_uuid(),
        "android_device_id": cl.generate_android_device_id(),
    },
    "device_settings": {
        "app_version": "357.0.0.24.108",
        "android_version": 34,
        "android_release": "14",
        "dpi": "440dpi",
        "resolution": "1080x2340",
        "manufacturer": "Google",
        "device": "husky",
        "model": "Pixel 8 Pro",
        "cpu": "tensor",
        "version_code": "604247854",
    },
    "user_agent": "Instagram 357.0.0.24.108 Android (34/14; 440dpi; 1080x2340; Google; Pixel 8 Pro; husky; tensor; en_US; 604247854)"
})

def challenge_code_handler(username, choice):
    code = input(f"\nInstagram sent a code via {choice}. Enter code: ")
    return code

cl.challenge_code_handler = challenge_code_handler

print(f"Logging in as {username}...")
try:
    cl.login(username, password)
    cl.dump_settings(str(SESSION_DIR / f"{username}_session.json"))
    print("\nSession saved! MCP server should work now.")
except Exception as e:
    print(f"\nFailed: {e}")
    print(f"Type: {type(e).__name__}")
    if hasattr(cl, 'last_json'):
        print(f"Last response: {cl.last_json}")
