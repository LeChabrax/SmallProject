"""
Script d'envoi promo -20% Gamme Au Quotidien (20-29 mars)
Batch 2 — 11 comptes, texte uniquement (pas de photos)
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────
# Config
# ──────────────────────────────────────────
USERNAME = os.getenv("INSTAGRAM_USERNAME", "impulse_nutrition_fr")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "2025Impulse!")
SESSION_FILE = Path(__file__).parent / f"{USERNAME}_session.json"

PROGRESS_FILE = Path(__file__).parent / "send_promo_progress.json"
LOG_FILE = Path(__file__).parent / "send_promo_log.txt"

# Délai entre chaque envoi (secondes) — prudent pour éviter le rate-limit IG
DELAY_BETWEEN_ACCOUNTS = 3    # secondes entre comptes

# ──────────────────────────────────────────
# Message template
# ──────────────────────────────────────────
MESSAGE_TEMPLATE = """Hello {greeting} !

J'espère que tu vas bien !

Je voulais te parler directement ici pour être sûr que tu ne passes pas à côté !

Du 20 au 29 mars, on lance -20% sur toute la Gamme Au Quotidien, cumulable avec ton code ambassadeur à -15%. C'est vraiment le moment idéal pour en parler à ta communauté !

Tous les visuels et exemples sont disponibles sur ton espace Affiliatly ou via ce lien : https://drive.google.com/drive/folders/1fmK0n3kV8SyJp8h-dcMrdwnzGBMdTw9a?usp=sharing, tout est prêt à l'emploi pour tes stories et posts. Pense à bien glisser ton code et ton lien dans tes stories, ça aide vraiment !

N'hésite pas si tu as des questions, à toi de jouer !

Sportivement,
Antoine"""

# ──────────────────────────────────────────
# Comptes à envoyer : (username, prenom_ou_vide)
# Ordre = ordre dans le spreadsheet (R291→R413)
# SKIP : melissa_biarritz (introuvable), nicepositive (-20% check déjà envoyé),
#        alexx_adamo / _williamroth / antoinepmr (répondre au message)
# ──────────────────────────────────────────
ACCOUNTS = [
    ("thomas_kohlanta21",  "Thomas"),
    ("baba_au_run",        "Jean-Baptiste"),
    ("audrey.merle95",     "Audrey"),
    ("celia.merle",        "Celia"),
    ("aurfleury",          "Aurore"),
    ("baptiste_mischler",  "Baptiste"),
    ("mathilde_doudoux",   "Mathilde"),
    ("marathon.manu",      "Emmanuel"),
    ("oscar_lombardot",    "Oscar"),
    ("kelly.r.u.n",        "Kelly"),
    ("marieschoenenburg",  "Marie"),
]

# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def build_message(prenom: str) -> str:
    greeting = prenom.strip() if prenom.strip() else ""
    if greeting:
        return MESSAGE_TEMPLATE.format(greeting=greeting)
    else:
        # Sans prénom : "Hello !" sans espace supplémentaire
        return MESSAGE_TEMPLATE.replace("Hello {greeting} !", "Hello !")


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────

def load_qualified() -> set:
    """Charge les usernames qualifiés depuis qualify_results.json (status='send').
    Si le fichier n'existe pas, tous les comptes sont considérés qualifiés."""
    qfile = Path(__file__).parent / "qualify_results.json"
    if not qfile.exists():
        return None  # None = pas de filtre
    with open(qfile, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {u for u, v in data.items() if v.get("status") == "send"}


def main():
    log("=" * 60)
    log(f"Démarrage envoi promo -20% — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    qualified = load_qualified()
    if qualified is not None:
        log(f"Filtre qualify_results.json actif — {len(qualified)} comptes qualifiés")
    else:
        log(f"Pas de filtre qualify — tous les comptes traités")
    log(f"Comptes dans ACCOUNTS : {len(ACCOUNTS)}")
    log("=" * 60)

    # Connexion Instagram
    client = Client()
    client.request_timeout = 1  # délai entre appels (défaut instagrapi)
    if SESSION_FILE.exists():
        log(f"Chargement session : {SESSION_FILE.name}")
        client.load_settings(SESSION_FILE)
    client.login(USERNAME, PASSWORD)
    client.dump_settings(SESSION_FILE)
    log("Connexion Instagram OK")

    # Patch HTTP timeout (30s) — instagrapi ne passe pas de timeout aux requêtes requests
    import functools
    _orig_post = client.private.post
    _orig_get  = client.private.get
    def _post_t(*a, **kw): kw.setdefault("timeout", 30); return _orig_post(*a, **kw)
    def _get_t(*a,  **kw): kw.setdefault("timeout", 30); return _orig_get(*a,  **kw)
    client.private.post = _post_t
    client.private.get  = _get_t
    log("HTTP timeout patché à 30s")

    # Chargement progression
    progress = load_progress()
    log(f"Comptes déjà traités (reprise) : {len(progress)}")

    sent_count = 0
    error_count = 0

    for i, (username, prenom) in enumerate(ACCOUNTS, start=1):
        if username in progress and progress[username].get("done"):
            log(f"[{i}/{len(ACCOUNTS)}] SKIP (déjà envoyé) : @{username}")
            continue
        if qualified is not None and username not in qualified:
            log(f"[{i}/{len(ACCOUNTS)}] SKIP (non qualifié) : @{username}")
            continue

        message = build_message(prenom)
        greeting_display = prenom.strip() or "(sans prénom)"
        log(f"\n[{i}/{len(ACCOUNTS)}] @{username} — prénom : {greeting_display}")

        account_progress = {"username": username, "done": False, "errors": []}

        # 1. Envoi du message texte
        try:
            user_id = client.user_id_from_username(username)
            dm = client.direct_send(message, [user_id])
            log(f"  ✓ Message texte envoyé (id={getattr(dm, 'id', '?')})")
            account_progress["text_sent"] = True
        except Exception as e:
            err = f"Erreur message texte : {e}"
            log(f"  ✗ {err}")
            account_progress["errors"].append(err)
            error_count += 1
            progress[username] = account_progress
            save_progress(progress)
            time.sleep(DELAY_BETWEEN_ACCOUNTS)
            continue

        account_progress["done"] = True
        sent_count += 1
        log(f"  → Compte @{username} traité avec succès ({i}/{len(ACCOUNTS)})")

        progress[username] = account_progress
        save_progress(progress)

        # Pause entre comptes
        if i < len(ACCOUNTS):
            log(f"  Pause {DELAY_BETWEEN_ACCOUNTS}s avant le prochain compte...")
            time.sleep(DELAY_BETWEEN_ACCOUNTS)

    log("\n" + "=" * 60)
    log(f"TERMINÉ — {sent_count} comptes OK, {error_count} erreurs")
    log(f"Progression sauvegardée : {PROGRESS_FILE}")
    log(f"Log complet : {LOG_FILE}")
    log("=" * 60)


if __name__ == "__main__":
    main()
