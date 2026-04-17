"""Blast DM Instagram - Mission Avis 17/04/2026.
Délais random 5-10s. Reprend où ça s'était arrêté via sent_log.json.
Lancement: python3 blast_avis.py
"""
import json
import os
import random
import sys
import time
from pathlib import Path

# Ajouter le path de l'instagram_dm_mcp pour réutiliser la session
ROOT = Path(__file__).resolve().parents[3]  # → Impulse-Nutrition/
sys.path.insert(0, str(ROOT / "instagram_dm_mcp" / "src"))
os.environ["INSTAGRAM_USERNAME"] = "impulse_nutrition_fr"
os.environ["INSTAGRAM_PASSWORD"] = "2025Impulse!"

from instagrapi import Client

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "queue_remaining.json"
LOG = HERE / "sent_log.json"
DRIVE_URL = "https://drive.google.com/file/d/16NjXmEff9zZ-KDOSYmrNkApfmtXoLngU/view?usp=sharing"

MSG_TEMPLATE = """Hello {prenom} ! J'espère que tu vas bien.

Super nouvelle, on est trop content de te présenter notre nouveauté : tu peux maintenant laisser un avis directement depuis ton espace perso sur notre site !

On t'a préparé une petite vidéo tuto pour t'expliquer, y'a plus qu'à suivre les instructions 😉
👉 {url}

N'hésite pas à y faire un tour pour découvrir la nouvelle interface et déposer tes avis sur les produits que tu as reçus. Ça nous aide énormément 🙏

Sportivement,
Antoine"""

MSG_NO_NAME = """Hello ! J'espère que tu vas bien.

Super nouvelle, on est trop content de te présenter notre nouveauté : tu peux maintenant laisser un avis directement depuis ton espace perso sur notre site !

On t'a préparé une petite vidéo tuto pour t'expliquer, y'a plus qu'à suivre les instructions 😉
👉 {url}

N'hésite pas à y faire un tour pour découvrir la nouvelle interface et déposer tes avis sur les produits que tu as reçus. Ça nous aide énormément 🙏

Sportivement,
Antoine"""


def extract_first_name(full_name: str) -> str | None:
    """Extract a clean first name from Instagram full_name. None if not confident."""
    if not full_name:
        return None
    # Strip emojis and special chars; keep letters with accents
    import re
    cleaned = re.sub(r'[^a-zA-ZÀ-ÿ\s\-]', '', full_name).strip()
    if not cleaned:
        return None
    parts = cleaned.split()
    if not parts:
        return None
    first = parts[0]
    # Reject if too short or junk like "le", "by", "de", "the", "coach", etc.
    blacklist = {"le", "la", "by", "de", "the", "coach", "mr", "mrs", "ms", "dr"}
    if len(first) < 2 or first.lower() in blacklist:
        # Try second part
        if len(parts) > 1 and parts[1].lower() not in blacklist and len(parts[1]) >= 2:
            first = parts[1]
        else:
            return None
    return first.capitalize()


def load_log():
    if LOG.exists():
        return json.loads(LOG.read_text())
    return {"batch_1": {"date": "2026-04-17", "sent": []}}


def save_log(log):
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2))


def main():
    queue = json.loads(QUEUE.read_text())
    log = load_log()

    if "batch_2" not in log:
        log["batch_2"] = {"date": "2026-04-17", "started": time.strftime("%H:%M:%S"), "sent": [], "failed": []}

    sent_handles = {x["handle"] for batch in log.values() if isinstance(batch, dict) for x in batch.get("sent", [])}
    failed_handles = {x["handle"] for batch in log.values() if isinstance(batch, dict) for x in batch.get("failed", [])}

    todo = [h for h in queue if h not in sent_handles and h not in failed_handles]
    print(f"[{time.strftime('%H:%M:%S')}] Queue: {len(queue)} | déjà ok: {len(sent_handles)} | failed: {len(failed_handles)} | à faire: {len(todo)}", flush=True)

    cl = Client()
    session_path = ROOT / "instagram_dm_mcp" / "data" / "sessions" / f"{os.environ['INSTAGRAM_USERNAME']}_session.json"
    if not session_path.exists():
        raise SystemExit(f"Session file missing: {session_path}. Lance le MCP d'abord pour générer la session.")
    cl.load_settings(session_path)
    # Valide la session sans refaire un login (qui déclencherait un blocage IP)
    try:
        cl.get_timeline_feed()
        print(f"[{time.strftime('%H:%M:%S')}] Session existante valide", flush=True)
    except Exception as e:
        raise SystemExit(f"Session expirée: {e}. Relance le MCP Instagram pour la régénérer.")
    print(f"[{time.strftime('%H:%M:%S')}] Login OK", flush=True)

    # Prénoms depuis le Sheet (col AE) → plus de hang sur user_info
    handle_to_prenom = json.loads((HERE / "handle_to_prenom.json").read_text())
    cl.request_timeout = 12
    for i, handle in enumerate(todo, 1):
        try:
            prenom = handle_to_prenom.get(handle, "").strip() or None
            user_id = cl.user_id_from_username(handle)
            msg = (MSG_TEMPLATE if prenom else MSG_NO_NAME).format(prenom=prenom or "", url=DRIVE_URL)
            result = cl.direct_send(msg, user_ids=[int(user_id)])
            msg_id = getattr(result, 'id', str(result))
            log["batch_2"]["sent"].append({"handle": handle, "prenom": prenom, "msg_id": str(msg_id)})
            print(f"[{time.strftime('%H:%M:%S')}] {i}/{len(todo)} ✅ @{handle} ({prenom or 'no-name'})", flush=True)
        except Exception as e:
            log["batch_2"]["failed"].append({"handle": handle, "error": str(e)[:200]})
            print(f"[{time.strftime('%H:%M:%S')}] {i}/{len(todo)} ❌ @{handle}: {str(e)[:120]}", flush=True)

        save_log(log)
        if i < len(todo):
            delay = random.uniform(5, 10)
            time.sleep(delay)

    log["batch_2"]["finished"] = time.strftime("%H:%M:%S")
    save_log(log)
    print(f"[{time.strftime('%H:%M:%S')}] DONE — sent {len(log['batch_2']['sent'])}, failed {len(log['batch_2']['failed'])}", flush=True)


if __name__ == "__main__":
    main()
