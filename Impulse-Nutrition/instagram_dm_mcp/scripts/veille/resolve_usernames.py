"""
Resolve Instagram usernames for VeilleConcu brands.

Tries multiple strategies:
1. Known mapping (curated list of brand → username)
2. Variations of brand name (lowercase, underscores, _fr, _official, etc.)
3. Instagram search API as fallback

Usage:
    python resolve_usernames.py [--dry-run] [--limit N]
"""

import time
import random
import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.google_sheets import SHEET_ID as SPREADSHEET_ID  # noqa: E402

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent.parent.parent / "data" / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"resolve_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("resolve")
log.info(f"=== resolve_usernames.py démarré — log: {LOG_FILE} ===")
# ──────────────────────────────────────────────────────────────────────────────

# Veille uses a dedicated account to avoid risking the main brand account
USERNAME = os.getenv("VEILLE_INSTAGRAM_USERNAME", "antman.lass")
PASSWORD = os.getenv("VEILLE_INSTAGRAM_PASSWORD", "Vald2003.INSTAGRAM")
SESSION_FILE = Path(__file__).parent.parent.parent / "data" / "sessions" / f"{USERNAME}_session.json"

SHEET_NAME = "VeilleConcu"

MAX_CONSECUTIVE_FAILURES = 3  # Stop after N consecutive failures (rate limit detected)

def smart_delay():
    """Random delay to avoid detection patterns."""
    time.sleep(random.uniform(2, 6))


def fake_activity(ig_client):
    """Perform random human-like activity to blend in."""
    actions = ["reels_tray", "timeline", "explore"]
    action = random.choice(actions)
    try:
        if action == "reels_tray":
            ig_client.get_reels_tray_feed("warm_start")
        elif action == "timeline":
            ig_client.get_timeline_feed()
        elif action == "explore":
            ig_client.explore_page()
    except Exception:
        pass
    time.sleep(random.uniform(1, 3))

# Known brand → Instagram username mapping
KNOWN_MAPPING = {
    "Allyouneed": "allyouneed_nutrition",  # allyouneed_fr = compte privé
    "Aqeelab": "aqeelab",
    "AYN": "ayn.nutrition",
    "BiotechUSA": "biotechusa",
    "Braineffect": "braineffect_fr",
    "Bulk": "bulk",
    "CookNRUN": "cooknrun.energyfood",
    "Cuure": "cuurevitamins",
    "EAFIT": "eafit_officiel",
    "Eiyolab": "eiyolab",
    "ESN": "esncom",
    "Etixx": "etixxsportsnutrition",
    "Fitadium": "fitadium",
    "Fitness Boutique": "fitnessboutiquefrance",
    "Fitnesspronutrition": "fitnesspronutrition",
    "Holy": "holysquad.fr",
    "Iswari": "iswari_france",
    "Lifepro": "lifeprofrance",
    "Maurten": "maurten_official",
    "Meltonic": "meltonic",
    "Mule Bar": "mulebar_sport_nutrition",
    "Myleore": "myleoremagnesie",
    "MyProtein": "myproteinfr",
    "Nduranz": "nduranz_official",
    "Nutri&Co": "nutriandco",
    "Nutrimea": "nutrimea_fr",
    "Nutrimuscle": "nutrimuscle",
    "Nutripure": "nutripure",
    "Onatera": "onatera_com",
    "Overstims": "overstims",
    "Pileje": "pileje",
    "Powerbar": "powerbar",
    "Prozis": "prozis",
    "PureAM": "pureamnutrition",
    "Pureamnutrition": "pureamnutrition",
    "Pyrenne": "pyreneperformance",
    "Runfinity": "runfinity_",
    "Sensnutrition": "sensnutrition",
    "Sunday Natural": "sundaynatural_france",
    "TA Energy": "ta.energy",
    "Teveo": "teveo",
    "Toutelanutrition": "toutelanutrition",
}


def ts():
    return datetime.now().strftime("%H:%M:%S")


def generate_variations(brand_name):
    """Generate possible Instagram username variations from a brand name."""
    name = brand_name.lower().strip()
    clean = name.replace(" ", "").replace("&", "").replace(".", "")
    with_underscore = name.replace(" ", "_").replace("&", "")

    variations = [
        clean,
        with_underscore,
        f"{clean}_fr",
        f"{clean}_france",
        f"{clean}_official",
        f"{clean}_officiel",
        f"{clean}nutrition",
        f"{clean}_nutrition",
    ]
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for v in variations:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def try_username(ig_client, username):
    """Try to fetch user info for a username. Returns user_info or None."""
    try:
        info = ig_client.user_info_by_username(username)
        return info
    except Exception:
        return None


def resolve_brand(ig_client, brand_name):
    """Resolve a brand name to a verified Instagram username."""
    # Strategy 1: Known mapping
    if brand_name in KNOWN_MAPPING:
        username = KNOWN_MAPPING[brand_name]
        info = try_username(ig_client, username)
        if info:
            return username, info, "mapping"
        smart_delay()

    # Strategy 2: Try variations
    for variation in generate_variations(brand_name):
        info = try_username(ig_client, variation)
        if info:
            return variation, info, "variation"
        smart_delay()

    # Strategy 3: Instagram search
    try:
        users = ig_client.search_users_v1(brand_name, 5)
        if users:
            for u in users:
                return u.username, ig_client.user_info(u.pk), "search"
    except Exception:
        pass

    return None, None, "not_found"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Resolve Instagram usernames for VeilleConcu")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        log.critical("gspread non installé — pip install gspread")
        sys.exit(1)

    # Connect to sheet
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "/Users/antoinechabrat/.config/google-service-account.json")
    log.info(f"Connexion Google Sheets — compte de service: {creds_path}")
    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_NAME)
        all_data = ws.get_all_values()
        log.info(f"Sheet ouvert — {len(all_data)-1} lignes dans {SHEET_NAME}")
    except Exception as e:
        log.critical(f"Impossible d'ouvrir le sheet: {e}")
        log.debug(traceback.format_exc())
        sys.exit(1)

    data_rows = all_data[1:]
    candidates = []
    for i, row in enumerate(data_rows):
        marque = row[0].strip() if len(row) > 0 else ""
        existing_username = row[1].strip() if len(row) > 1 else ""
        if not marque:
            continue
        candidates.append({
            "row": i + 2,
            "marque": marque,
            "existing_username": existing_username,
        })

    if args.limit:
        candidates = candidates[:args.limit]

    # Filter: only resolve those without a username
    to_resolve = [c for c in candidates if not c["existing_username"]]
    already_set = len(candidates) - len(to_resolve)

    log.info(f"{len(candidates)} marques total, {already_set} déjà résolues, {len(to_resolve)} à résoudre")

    if not to_resolve:
        log.info("Tout est déjà résolu!")
        return

    # Instagram login
    log.info(f"Connexion Instagram avec le compte veille: {USERNAME}")
    ig_client = Client()
    ig_client.request_timeout = 1
    if SESSION_FILE.exists():
        log.info(f"Session existante chargée: {SESSION_FILE}")
        ig_client.load_settings(SESSION_FILE)
    try:
        ig_client.login(USERNAME, PASSWORD)
        ig_client.dump_settings(SESSION_FILE)
        log.info(f"Login OK — connecté en tant que {USERNAME}")
    except Exception as e:
        log.critical(f"Echec login Instagram ({USERNAME}): {e}")
        log.debug(traceback.format_exc())
        log.critical("⛔ Arrêt — impossible de se connecter. Vérifier le compte ou résoudre le challenge manuellement.")
        sys.exit(1)

    resolved = []
    not_found = []
    consecutive_failures = 0

    for idx, acct in enumerate(to_resolve, 1):
        marque = acct["marque"]
        print(f"[{ts()}] [{idx}/{len(to_resolve)}] {marque}...", end=" ")

        username, info, method = resolve_brand(ig_client, marque)

        if username and info:
            followers = getattr(info, 'follower_count', 0) or 0
            user_id = str(info.pk)
            log.info(f"  ✓ @{username} ({followers} followers) [{method}]")
            resolved.append({
                "row": acct["row"],
                "marque": marque,
                "username": username,
                "user_id": user_id,
                "followers": followers,
            })
            consecutive_failures = 0
            # Fake activity every 3-5 iterations to look human
            if idx % random.randint(3, 5) == 0:
                fake_activity(ig_client)
        else:
            log.warning(f"  ✗ {marque} introuvable")
            not_found.append(marque)
            consecutive_failures += 1

            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                remaining = len(to_resolve) - idx
                log.warning(f"⚠️  {MAX_CONSECUTIVE_FAILURES} échecs consécutifs — rate limit probable. Arrêt. {remaining} marques restantes non traitées.")
                not_found.extend(a["marque"] for a in to_resolve[idx:])
                break

        if idx < len(to_resolve):
            smart_delay()

    # Summary
    log.info("=" * 60)
    log.info(f"Résolu: {len(resolved)}/{len(to_resolve)}")
    if not_found:
        log.warning(f"Introuvables ({len(not_found)}): {', '.join(not_found)}")
    log.info("=" * 60)
    for r in resolved:
        log.info(f"  {r['marque']:<25} → @{r['username']:<25} ({r['followers']} followers)")

    if args.dry_run:
        log.info("[DRY RUN] Aucune écriture dans le sheet")
        return

    # Write to sheet
    log.info(f"Écriture des {len(resolved)} usernames + IDs dans le sheet...")
    batch = []
    for r in resolved:
        row = r["row"]
        batch.append({"range": f"B{row}", "values": [[r["username"]]]})
        batch.append({"range": f"C{row}", "values": [[r["user_id"]]]})

    if batch:
        try:
            ws.batch_update(batch, value_input_option="USER_ENTERED")
            log.info("Done! Sheet mis à jour.")
        except Exception as e:
            log.error(f"Erreur écriture sheet: {e}")
            log.debug(traceback.format_exc())
    log.info(f"=== FIN — log complet dans {LOG_FILE} ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Interrompu par l'utilisateur (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        log.critical(f"CRASH NON GÉRÉ: {e}")
        log.critical(traceback.format_exc())
        log.critical(f"⛔ Le script a planté. Log complet dans: {LOG_FILE}")
        sys.exit(1)
