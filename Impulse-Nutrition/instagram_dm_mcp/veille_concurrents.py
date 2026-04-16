"""
Veille concurrentielle — analyse automatique des concurrents via Instagram.

Lit l'onglet VeilleConcu du Google Sheet (col A = marques, col B = @ Instagram),
analyse chaque profil Instagram et remplit les colonnes C-AA automatiquement.

Colonnes remplies par le script :
  B  @ Instagram     — résolu automatiquement si vide (recherche par nom de marque)
  C  ID Instagram    — pk numérique du compte
  F  Followers       — nombre brut
  G  Following       — nombre brut
  H  Nb Posts        — media_count
  I  Engagement %    — avg(likes+comments)/followers sur 12 derniers posts
  J  Avg Likes       — moyenne likes
  K  Avg Comments    — moyenne commentaires
  L  Freq. post/sem  — estimation basée sur les 12 derniers posts
  M  Dernier post    — date DD/MM/YYYY
  N  % Reels         — part de reels/vidéos dans les 12 derniers posts
  O  % Carrousels    — part de carrousels
  P  % Photos        — part de photos
  Q  Bio             — texte de la bio (tronqué 200 car)
  R  URL externe     — lien dans la bio
  S  Vérifié         — oui/non
  T  Followers M-1   — copié depuis F avant mise à jour (historique)
  U  Delta Followers %  — croissance vs M-1
  V  Engagement M-1  — copié depuis I avant mise à jour
  W  Delta Engagement pts — évolution vs M-1
  X  Ambassadeurs communs — cross-ref avec col T de Suivi_Amb
  AA Dernière MAJ    — date du run

Colonnes manuelles (non touchées par le script) :
  D  Catégorie       — direct / indirect / adjacent
  E  Positionnement  — à remplir par Antoine
  Y  Dernière campagne détectée — à remplir manuellement ou par Claude
  Z  Notes           — observations libres

Usage :
    # Analyser tous les concurrents du sheet
    python veille_concurrents.py

    # Limiter à N comptes
    python veille_concurrents.py --limit 5

    # Dry run (affiche sans écrire)
    python veille_concurrents.py --dry-run
"""

import argparse
import time
import random
import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from instagrapi import Client
from dotenv import load_dotenv

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from infra.common.google_sheets import SUIVI_AMB_COLS, VEILLE_COLS  # noqa: E402

load_dotenv()

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "data" / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"veille_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("veille")
log.info(f"=== veille_concurrents.py démarré — log: {LOG_FILE} ===")
# ──────────────────────────────────────────────────────────────────────────────

# Veille uses a dedicated account to avoid risking the main brand account
VEILLE_USERNAME = os.getenv("VEILLE_INSTAGRAM_USERNAME", "antman.lass")
VEILLE_PASSWORD = os.getenv("VEILLE_INSTAGRAM_PASSWORD", "Vald2003.INSTAGRAM")
SESSION_FILE = Path(__file__).parent / "data" / "sessions" / f"{VEILLE_USERNAME}_session.json"

SPREADSHEET_ID = "1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4"
SHEET_NAME = "VeilleConcu"
AMB_SHEET = "Suivi_Amb"

MAX_CONSECUTIVE_FAILURES = 3  # Stop after N consecutive failures (rate limit detected)


def smart_delay():
    """Random delay to avoid detection patterns."""
    time.sleep(random.uniform(2, 7))


def fake_activity(ig_client):
    """Perform random human-like activity to blend in.
    Called every few iterations to look like a real user."""
    actions = [
        "reels_tray",
        "timeline",
        "explore",
    ]
    action = random.choice(actions)
    try:
        if action == "reels_tray":
            ig_client.get_reels_tray_feed("warm_start")
        elif action == "timeline":
            ig_client.get_timeline_feed()
        elif action == "explore":
            ig_client.explore_page()
    except Exception:
        pass  # Don't care if it fails, just want the activity logged
    time.sleep(random.uniform(1, 3))


def ts():
    return datetime.now().strftime("%H:%M:%S")


def log_exception(context: str, exc: Exception):
    """Log full traceback for an exception with context."""
    log.error(f"{context}: {exc}")
    log.debug(traceback.format_exc())


def analyze_competitor(ig_client, username):
    """Analyze a competitor's Instagram profile. Returns dict with all metrics."""
    result = {
        "username": username,
        "user_id": "",
        "followers": 0,
        "following": 0,
        "posts_count": 0,
        "bio": "",
        "external_url": "",
        "is_verified": False,
        "engagement_rate": 0.0,
        "avg_likes": 0,
        "avg_comments": 0,
        "pct_reels": 0,
        "pct_carousels": 0,
        "pct_photos": 0,
        "freq_per_week": 0.0,
        "last_post_date": "",
        "error": None,
    }

    try:
        info = ig_client.user_info_by_username(username)
    except Exception as e:
        result["error"] = str(e)
        log_exception(f"user_info_by_username({username})", e)
        return result

    result["user_id"] = str(info.pk)
    result["followers"] = info.follower_count or 0
    result["following"] = info.following_count or 0
    result["posts_count"] = info.media_count or 0
    result["bio"] = (info.biography or "")[:200]
    result["external_url"] = str(info.external_url or "")
    result["is_verified"] = bool(info.is_verified)

    # Fetch recent posts
    smart_delay()
    try:
        posts = ig_client.user_medias(info.pk, 12)
    except Exception as e:
        log_exception(f"user_medias({username})", e)
        posts = []

    if posts and result["followers"] > 0:
        total_likes = 0
        total_comments = 0
        media_types = {"photo": 0, "video": 0, "carousel": 0}

        for post in posts:
            likes = getattr(post, 'like_count', 0) or 0
            comments = getattr(post, 'comment_count', 0) or 0
            total_likes += likes
            total_comments += comments

            media_type = str(getattr(post, 'media_type', ''))
            if media_type == '8':
                media_types["carousel"] += 1
            elif media_type == '2':
                media_types["video"] += 1
            else:
                media_types["photo"] += 1

        count = len(posts)
        result["avg_likes"] = int(total_likes / count)
        result["avg_comments"] = int(total_comments / count)
        avg_interactions = (total_likes + total_comments) / count
        result["engagement_rate"] = round((avg_interactions / result["followers"]) * 100, 2)

        # Post type percentages
        result["pct_reels"] = round((media_types["video"] / count) * 100)
        result["pct_carousels"] = round((media_types["carousel"] / count) * 100)
        result["pct_photos"] = round((media_types["photo"] / count) * 100)

        # Post frequency: estimate from date range of fetched posts
        dates = []
        for post in posts:
            taken_at = getattr(post, 'taken_at', None)
            if taken_at and isinstance(taken_at, datetime):
                dates.append(taken_at)

        if len(dates) >= 2:
            dates.sort()
            span_days = (dates[-1] - dates[0]).days
            if span_days > 0:
                result["freq_per_week"] = round((len(dates) / span_days) * 7, 1)

        # Last post date
        if dates:
            result["last_post_date"] = max(dates).strftime("%d/%m/%Y")

    return result


def resolve_username(ig_client, brand_name):
    """Try to find Instagram username from brand name via search."""
    try:
        users = ig_client.search_users(brand_name, 5)
        if users:
            # Return the first result that looks like a brand account
            for u in users:
                uname = u.username.lower()
                brand_lower = brand_name.lower().replace(" ", "").replace("&", "")
                if brand_lower in uname or uname in brand_lower:
                    return u.username
            # Fallback: return first result
            return users[0].username
    except Exception:
        pass
    return ""


def find_common_ambassadors(ws_amb, competitor_name):
    """Cross-reference Suivi_Amb col T (Sponsor) with competitor name."""
    try:
        all_data = ws_amb.get_all_values()
    except Exception:
        return ""

    common = []
    for row in all_data[1:]:
        sponsor = row[SUIVI_AMB_COLS["sponsor"]].strip() if len(row) > SUIVI_AMB_COLS["sponsor"] else ""
        username = row[SUIVI_AMB_COLS["username"]].strip() if len(row) > SUIVI_AMB_COLS["username"] else ""
        if sponsor and competitor_name.lower() in sponsor.lower() and username:
            common.append(f"@{username}")

    return ", ".join(common[:5]) + ("..." if len(common) > 5 else "") if common else ""


def main():
    parser = argparse.ArgumentParser(description="Veille concurrentielle — VeilleConcu sheet")
    parser.add_argument("--limit", type=int, default=None, help="Max accounts to process")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing to sheet")
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

    # Also open Suivi_Amb for cross-ref
    try:
        ws_amb = sh.worksheet(AMB_SHEET)
    except Exception as e:
        log.warning(f"Impossible d'ouvrir {AMB_SHEET} pour cross-ref: {e}")
        ws_amb = None

    # Parse rows: A=0 Marque, B=1 @Instagram, C=2 ID, F=5 Followers, I=8 Engagement
    data_rows = all_data[1:]  # skip headers
    candidates = []
    for i, row in enumerate(data_rows):
        marque = row[0].strip() if len(row) > 0 else ""
        ig_username = row[1].strip() if len(row) > 1 else ""
        if not marque:
            continue
        # Read current followers/engagement for M-1 historique
        current_followers = row[5].strip() if len(row) > 5 else ""
        current_engagement = row[8].strip() if len(row) > 8 else ""
        candidates.append({
            "row": i + 2,  # 1-indexed + header
            "marque": marque,
            "username": ig_username,
            "prev_followers": current_followers,
            "prev_engagement": current_engagement,
        })

    if args.limit:
        candidates = candidates[:args.limit]

    log.info(f"Veille concurrentielle — {len(candidates)} marques dans VeilleConcu")

    # Instagram login
    log.info(f"Connexion Instagram avec le compte veille: {VEILLE_USERNAME}")
    ig_client = Client()
    ig_client.request_timeout = 1
    if SESSION_FILE.exists():
        log.info(f"Session existante chargée: {SESSION_FILE}")
        ig_client.load_settings(SESSION_FILE)
    try:
        ig_client.login(VEILLE_USERNAME, VEILLE_PASSWORD)
        ig_client.dump_settings(SESSION_FILE)
        log.info(f"Login OK — connecté en tant que {VEILLE_USERNAME}")
    except Exception as e:
        log.critical(f"Echec login Instagram ({VEILLE_USERNAME}): {e}")
        log.debug(traceback.format_exc())
        log.critical("⛔ Arrêt — impossible de se connecter à Instagram. Vérifier le compte ou résoudre le challenge.")
        sys.exit(1)

    today = datetime.now().strftime("%d/%m/%Y")
    updates = []
    consecutive_failures = 0

    for idx, acct in enumerate(candidates, 1):
        marque = acct["marque"]
        username = acct["username"]

        # Resolve username if missing
        if not username:
            log.info(f"[{idx}/{len(candidates)}] {marque} — username manquant, recherche en cours...")
            username = resolve_username(ig_client, marque)
            if username:
                log.info(f"[{idx}/{len(candidates)}] {marque} — username trouvé: @{username}")
            else:
                log.warning(f"[{idx}/{len(candidates)}] {marque} — username introuvable, skip")
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    remaining = len(candidates) - idx
                    log.warning(f"⚠️  {MAX_CONSECUTIVE_FAILURES} échecs consécutifs — rate limit probable. Arrêt. {remaining} marques restantes.")
                    break
                continue
            smart_delay()
        else:
            log.info(f"[{idx}/{len(candidates)}] {marque} (@{username})")

        result = analyze_competitor(ig_client, username)

        if result["error"]:
            log.error(f"[{idx}/{len(candidates)}] {marque} (@{username}) — ERREUR: {result['error']}")
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                remaining = len(candidates) - idx
                log.warning(f"⚠️  {MAX_CONSECUTIVE_FAILURES} échecs consécutifs — rate limit probable. Arrêt. {remaining} marques restantes.")
                break
            if idx < len(candidates):
                smart_delay()
            continue

        consecutive_failures = 0
        log.info(f"  → {result['followers']} followers, {result['engagement_rate']}% eng, avg {result['avg_likes']} likes")

        # Fake activity every 3-5 iterations to look human
        if idx % random.randint(3, 5) == 0:
            fake_activity(ig_client)

        # Compute deltas (M-1)
        prev_f = acct["prev_followers"]
        prev_e = acct["prev_engagement"]
        delta_followers = ""
        delta_engagement = ""

        if prev_f:
            try:
                prev_f_num = float(str(prev_f).replace(",", ".").replace("%", "").replace(" ", ""))
                if prev_f_num > 0:
                    delta_followers = f"{((result['followers'] - prev_f_num) / prev_f_num) * 100:.1f}%"
            except (ValueError, ZeroDivisionError):
                pass

        if prev_e:
            try:
                prev_e_num = float(str(prev_e).replace(",", ".").replace("%", "").replace(" ", ""))
                delta_engagement = f"{result['engagement_rate'] - prev_e_num:+.2f} pts"
            except ValueError:
                pass

        # Cross-ref ambassadeurs communs
        common_amb = ""
        if ws_amb:
            common_amb = find_common_ambassadors(ws_amb, marque)

        # Build row update: cols B through AA
        row_num = acct["row"]
        row_update = {
            "row": row_num,
            "B": username,                                    # @ Instagram
            "C": result["user_id"],                           # ID Instagram
            # D, E = manual (Catégorie, Positionnement)
            "F": str(result["followers"]),                    # Followers
            "G": str(result["following"]),                    # Following
            "H": str(result["posts_count"]),                  # Nb Posts
            "I": f"{result['engagement_rate']}%",             # Engagement %
            "J": str(result["avg_likes"]),                    # Avg Likes
            "K": str(result["avg_comments"]),                 # Avg Comments
            "L": str(result["freq_per_week"]),                # Freq post/sem
            "M": result["last_post_date"],                    # Dernier post
            "N": f"{result['pct_reels']}%",                   # % Reels
            "O": f"{result['pct_carousels']}%",               # % Carrousels
            "P": f"{result['pct_photos']}%",                  # % Photos
            "Q": result["bio"],                               # Bio
            "R": result["external_url"],                      # URL externe
            "S": "oui" if result["is_verified"] else "non",   # Vérifié
            "T": prev_f if prev_f else "",                    # Followers M-1
            "U": delta_followers,                             # Delta Followers %
            "V": prev_e if prev_e else "",                    # Engagement M-1
            "W": delta_engagement,                            # Delta Engagement pts
            "X": common_amb,                                  # Ambassadeurs communs
            # Y = manual (Dernière campagne détectée)
            # Z = manual (Notes)
            "AA": today,                                      # Dernière MAJ
        }
        updates.append(row_update)

        if idx < len(candidates):
            smart_delay()

    # Apply updates to sheet
    if args.dry_run:
        log.info(f"[DRY RUN] {len(updates)} lignes à mettre à jour")
        for u in updates[:5]:
            log.info(f"  Row {u['row']}: @{u['B']} — {u['F']} followers, {u['I']} engagement")
        return

    if not updates:
        log.info("Aucune mise à jour à faire.")
        return

    log.info(f"Écriture de {len(updates)} lignes dans VeilleConcu...")

    # Batch update per column range to avoid overwriting manual columns
    col_map = {
        "B": 1, "C": 2, "F": 5, "G": 6, "H": 7, "I": 8, "J": 9, "K": 10,
        "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17,
        "S": 18, "T": 19, "U": 20, "V": 21, "W": 22, "X": 23, "AA": 26,
    }

    batch = []
    for u in updates:
        row = u["row"]
        for col_letter, col_idx in col_map.items():
            value = u.get(col_letter, "")
            batch.append({
                "range": f"{col_letter}{row}",
                "values": [[value]],
            })

    # Write in chunks to avoid API limits
    CHUNK_SIZE = 50
    for i in range(0, len(batch), CHUNK_SIZE):
        chunk = batch[i:i + CHUNK_SIZE]
        try:
            ws.batch_update(chunk, value_input_option="USER_ENTERED")
        except Exception as e:
            log.error(f"Erreur écriture sheet (chunk {i//CHUNK_SIZE + 1}): {e}")
            log.debug(traceback.format_exc())
        if i + CHUNK_SIZE < len(batch):
            smart_delay()

    # Summary
    log.info(f"Done! {len(updates)} concurrents mis à jour dans VeilleConcu.")
    sorted_results = sorted(updates, key=lambda x: int(x.get("F", "0") or "0"), reverse=True)
    log.info(f"{'Marque':<25} {'Followers':<12} {'Engagement':<12} {'Avg Likes':<10}")
    log.info("-" * 60)
    for u in sorted_results[:10]:
        log.info(f"@{u['B']:<24} {u['F']:<12} {u['I']:<12} {u['J']:<10}")
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
