"""
Qualification automatique d'influenceurs — scoring via Instagram API.

Analyse les profils Instagram et attribue un score go/no-go basé sur :
  - Nombre de followers (sweet spot 2k-100k)
  - Taux d'engagement (likes + commentaires / followers)
  - Bio (mots-clés sport/nutrition)
  - Sponsoring concurrent détecté
  - Ratio following/followers
  - Compte privé = disqualifié

Usage :
    # Qualifier une liste de usernames
    python qualify_influencer.py user1 user2 user3

    # Depuis un fichier (un username par ligne)
    python qualify_influencer.py --file prospects.txt

    # Dry run (affiche sans écrire dans le sheet)
    python qualify_influencer.py user1 user2 --dry-run

    # Écrire dans l'onglet Qualification du sheet
    python qualify_influencer.py user1 user2 --write-sheet
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.google_sheets import SHEET_ID as SPREADSHEET_ID  # noqa: E402
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402
from infra.common.constants import COMPETITORS, SPORT_KEYWORDS, NUTRITION_KEYWORDS  # noqa: E402


def ts():
    return datetime.now().strftime("%H:%M:%S")


def score_followers(count):
    """Score based on follower count. Sweet spot: 2k-100k."""
    if count is None or count == 0:
        return -3, "pas de followers"
    if count < 1000:
        return -1, f"{count} (trop petit)"
    if count < 2000:
        return 0, f"{count / 1000:.1f}k (micro)"
    if count <= 100000:
        return 2, f"{count / 1000:.1f}k (sweet spot)"
    if count <= 500000:
        return 1, f"{count / 1000:.0f}k (gros profil)"
    return 0, f"{count / 1000:.0f}k (trop gros)"


def score_engagement(posts, follower_count):
    """Compute engagement rate from recent posts."""
    if not posts or follower_count == 0:
        return 0, 0.0, "pas de données"

    total_interactions = 0
    count = 0
    for post in posts:
        likes = getattr(post, 'like_count', 0) or 0
        comments = getattr(post, 'comment_count', 0) or 0
        total_interactions += likes + comments
        count += 1

    if count == 0:
        return 0, 0.0, "pas de posts"

    avg_interactions = total_interactions / count
    rate = (avg_interactions / follower_count) * 100

    if rate >= 5:
        return 3, rate, f"{rate:.1f}% (excellent)"
    if rate >= 3:
        return 3, rate, f"{rate:.1f}% (très bon)"
    if rate >= 1:
        return 2, rate, f"{rate:.1f}% (bon)"
    if rate >= 0.5:
        return 0, rate, f"{rate:.1f}% (moyen)"
    return -1, rate, f"{rate:.1f}% (faible)"


def score_bio(biography, external_url):
    """Score based on bio content: sport keywords, competitor detection."""
    bio = (biography or "").lower()
    url = (str(external_url) if external_url else "").lower()
    full_text = bio + " " + url

    bio_score = 0
    flags = []

    # Check sport keywords
    sport_found = [kw for kw in SPORT_KEYWORDS if kw in full_text]
    if sport_found:
        bio_score += 2
        flags.append(f"sport: {', '.join(sport_found[:3])}")

    # Check nutrition keywords
    nutri_found = [kw for kw in NUTRITION_KEYWORDS if kw in full_text]
    if nutri_found:
        bio_score += 1
        flags.append(f"nutri: {', '.join(nutri_found[:2])}")

    # Check competitor sponsoring
    competitor_found = [c for c in COMPETITORS if c in full_text]
    if competitor_found:
        bio_score -= 2
        flags.append(f"concurrent: {', '.join(competitor_found[:2])}")

    # Check if already mentions impulse
    if "impulse" in full_text:
        bio_score += 1
        flags.append("déjà Impulse!")

    return bio_score, flags


def score_ratio(following, followers):
    """Score following/followers ratio. High ratio = suspicious."""
    if followers == 0:
        return -2, "no followers"
    ratio = following / followers
    if ratio > 2:
        return -2, f"ratio {ratio:.1f} (suspect)"
    if ratio > 1.5:
        return -1, f"ratio {ratio:.1f} (élevé)"
    if ratio < 0.3:
        return 1, f"ratio {ratio:.1f} (bon profil)"
    return 0, f"ratio {ratio:.1f}"


def qualify_profile(ig_client, username, debug=False):
    """Qualify a single profile. Returns score dict."""
    result = {
        "username": username,
        "total_score": 0,
        "verdict": "erreur",
        "details": {},
        "flags": [],
        "followers": 0,
        "engagement_rate": 0.0,
        "bio_excerpt": "",
        "sport": "",
    }

    try:
        info = ig_client.user_info_by_username(username)
    except Exception as e:
        result["verdict"] = f"erreur: {e}"
        return result

    # Private account = instant disqualify
    if info.is_private:
        result["verdict"] = "DISQUALIFIÉ (privé)"
        result["followers"] = info.follower_count or 0
        result["bio_excerpt"] = (info.biography or "")[:80]
        return result

    total = 0

    # 1. Followers
    f_score, f_detail = score_followers(info.follower_count)
    total += f_score
    result["details"]["followers"] = f"{f_score:+d} — {f_detail}"
    result["followers"] = info.follower_count or 0

    # 2. Engagement rate (fetch recent posts)
    sleep_random(1, 2)
    try:
        posts = ig_client.user_medias(info.pk, 12)
    except Exception:
        posts = []

    e_score, e_rate, e_detail = score_engagement(posts, info.follower_count or 0)
    total += e_score
    result["details"]["engagement"] = f"{e_score:+d} — {e_detail}"
    result["engagement_rate"] = e_rate

    # 3. Bio analysis
    b_score, b_flags = score_bio(info.biography, info.external_url)
    total += b_score
    result["details"]["bio"] = f"{b_score:+d} — {', '.join(b_flags) if b_flags else 'aucun signal'}"
    result["flags"] = b_flags
    result["bio_excerpt"] = (info.biography or "")[:80]

    # Extract sport from bio
    bio_lower = (info.biography or "").lower()
    for kw in SPORT_KEYWORDS:
        if kw in bio_lower:
            result["sport"] = kw
            break

    # 4. Following/followers ratio
    r_score, r_detail = score_ratio(info.following_count or 0, info.follower_count or 0)
    total += r_score
    result["details"]["ratio"] = f"{r_score:+d} — {r_detail}"

    # 5. Content frequency
    media_count = info.media_count or 0
    if media_count > 200:
        total += 1
        result["details"]["contenu"] = f"+1 — {media_count} posts (actif)"
    elif media_count > 50:
        result["details"]["contenu"] = f"+0 — {media_count} posts"
    else:
        total -= 1
        result["details"]["contenu"] = f"-1 — {media_count} posts (peu actif)"

    result["total_score"] = total

    # Verdict
    if total >= 6:
        result["verdict"] = "GO (excellent)"
    elif total >= 4:
        result["verdict"] = "GO"
    elif total >= 2:
        result["verdict"] = "MAYBE (à vérifier)"
    elif total >= 0:
        result["verdict"] = "BASSE PRIO"
    else:
        result["verdict"] = "NO-GO"

    return result


def format_followers_k(count):
    """Format follower count in thousands."""
    if not count:
        return ""
    k = count / 1000
    if k >= 10:
        return str(int(round(k)))
    return f"{k:.1f}".replace(".", ",")


def write_to_sheet(results):
    """Write qualification results to a 'Qualification' tab in the sheet."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("ERROR: gspread not installed.")
        return

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "/Users/antoinechabrat/.config/google-service-account.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)

    # Create or get Qualification tab
    try:
        ws = sh.worksheet("Qualification")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title="Qualification", rows=500, cols=10)

    # Headers
    headers = [
        "Date", "Username", "Followers (k)", "Engagement %",
        "Score", "Verdict", "Sport", "Flags", "Bio",
    ]

    # Find next empty row
    existing = ws.get_all_values()
    if not existing or existing[0] != headers:
        ws.update("A1", [headers])
        next_row = 2
    else:
        next_row = len(existing) + 1

    today = datetime.now().strftime("%d/%m/%Y")
    rows = []
    for r in results:
        rows.append([
            today,
            r["username"],
            format_followers_k(r["followers"]),
            f"{r['engagement_rate']:.1f}%" if r["engagement_rate"] else "",
            str(r["total_score"]),
            r["verdict"],
            r.get("sport", ""),
            " | ".join(r.get("flags", [])),
            r.get("bio_excerpt", ""),
        ])

    if rows:
        ws.update(f"A{next_row}", rows)
        print(f"\n{len(rows)} résultats écrits dans l'onglet Qualification (lignes {next_row}-{next_row + len(rows) - 1})")


def main():
    parser = argparse.ArgumentParser(description="Qualify influencer profiles via Instagram")
    parser.add_argument("usernames", nargs="*", help="Instagram usernames to qualify")
    parser.add_argument("--file", type=str, help="File with one username per line")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing to sheet")
    parser.add_argument("--write-sheet", action="store_true", help="Write results to Qualification tab")
    args = parser.parse_args()

    # Collect usernames
    usernames = list(args.usernames)
    if args.file:
        with open(args.file) as f:
            usernames.extend(line.strip() for line in f if line.strip())

    if not usernames:
        print("Aucun username fourni. Usage: python qualify_influencer.py user1 user2 [--file prospects.txt]")
        sys.exit(1)

    # Deduplicate
    usernames = list(dict.fromkeys(usernames))

    print(f"[{ts()}] Qualification de {len(usernames)} profils")

    ig_client = get_ig_client("veille")
    ig_client.request_timeout = 1
    print(f"[{ts()}] Logged in as veille ({USERNAME})")

    results = []
    for idx, uname in enumerate(usernames, 1):
        print(f"\n[{ts()}] [{idx}/{len(usernames)}] @{uname}")
        result = qualify_profile(ig_client, uname)
        results.append(result)

        # Print result
        print(f"  Score: {result['total_score']} → {result['verdict']}")
        for key, detail in result.get("details", {}).items():
            print(f"    {key}: {detail}")

        if idx < len(usernames):
            sleep_random(2, 4)

    # Summary
    print(f"\n{'='*60}")
    print(f"RÉSULTATS — {len(results)} profils qualifiés")
    print(f"{'='*60}")

    go = [r for r in results if "GO" in r["verdict"] and "NO" not in r["verdict"]]
    maybe = [r for r in results if "MAYBE" in r["verdict"]]
    nogo = [r for r in results if r["verdict"] in ("NO-GO", "BASSE PRIO") or "DISQUALIFIÉ" in r["verdict"]]

    if go:
        print(f"\n✓ GO ({len(go)}):")
        for r in sorted(go, key=lambda x: x["total_score"], reverse=True):
            print(f"  @{r['username']} — score {r['total_score']}, {format_followers_k(r['followers'])}k, engagement {r['engagement_rate']:.1f}%")

    if maybe:
        print(f"\n? MAYBE ({len(maybe)}):")
        for r in maybe:
            print(f"  @{r['username']} — score {r['total_score']}, {format_followers_k(r['followers'])}k")

    if nogo:
        print(f"\n✗ NO-GO ({len(nogo)}):")
        for r in nogo:
            print(f"  @{r['username']} — {r['verdict']}")

    # Write to sheet
    if args.write_sheet and not args.dry_run:
        write_to_sheet(results)
    elif args.dry_run:
        print("\n[DRY RUN] Résultats non écrits dans le sheet")


if __name__ == "__main__":
    main()
