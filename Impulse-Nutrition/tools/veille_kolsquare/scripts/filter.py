#!/usr/bin/env python3
"""Filter KolSquare CSV export -> dedupe -> MCP Instagram qualification.

Pipeline pour la mission KolSquare (avril 2026) :
    1. Parse l'export KolSquare (semicolon-separated, UTF-8)
    2. Filtre par métier (règles tools/veille_kolsquare/filtering_rules.md)
    3. Applique des seuils de base sur followers / engagement KolSquare
    4. Dédoublonne contre Suivi_Amb, Suivi_Dot, Suivi_Paid
    5. Check MCP Instagram via compte veille antman.lass : bio, 5 derniers
       posts, sponsors concurrents, statut privé → scoring GO/MAYBE/NO-GO
    6. Écrit un CSV scoré + affiche un recap pour dry-run

Usage :
    python filter_kolsquare.py \\
        --input "../tools/veille_kolsquare/09-04-2026_IMPULSE - 09_04_26_Casting_fr-FR.csv" \\
        --output "../tools/veille_kolsquare/filtered_prospects_042026.csv"

    # Filtrage + dédoublonnage uniquement (pas de check MCP)
    python filter_kolsquare.py --input ... --output ... --no-mcp

    # Check MCP uniquement sur les 20 premiers (test)
    python filter_kolsquare.py --input ... --output ... --limit 20
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# `from infra.common.*` imports — infra/common — added to sys.path below.
# Bootstrap: anchor to project root via .mcp.json (see infra/common/paths.py).
_here = Path(__file__).resolve()
for _p in (_here, *_here.parents):
    if (_p / ".mcp.json").exists():
        sys.path.insert(0, str(_p))
        break
from infra.common.google_sheets import (  # noqa: E402
    HEADER_ROW,
    SHEET_ID,
    SUIVI_AMB_COLS,
    SUIVI_DOT_COLS,
    SUIVI_PAID_COLS,
    get_worksheet,
)
from infra.common.instagram_client import get_ig_client, sleep_random  # noqa: E402
from infra.common.constants import COMPETITORS  # noqa: E402
from infra.common.paths import PROJECT_ROOT  # noqa: E402

# Reuse the scoring logic from infra/scripts/instagram/qualify/influencer.py.
# That script isn't a package, so we add its dir to sys.path and import by
# filename.
sys.path.insert(
    0,
    str(PROJECT_ROOT / "infra" / "scripts" / "instagram" / "qualify"),
)
from influencer import qualify_profile, format_followers_k  # noqa: E402

logger = logging.getLogger("filter_kolsquare")


# =========================================================================
# KolSquare CSV layout — indices confirmed from the 2026-04-09 export header
# =========================================================================

CSV_IDX = {
    "nom_pseudo":    0,   # "Nom / Pseudo" — display name (often only this filled)
    "prenom":        1,   # "Prénom"
    "nom":           2,   # "Nom"
    "pseudo":        3,   # "Pseudo" (KolSquare internal)
    "metiers":       4,   # "Métier(s)" — comma-separated
    "url":           9,   # KolSquare profile URL
    # Réseau 1..5 blocks — each block is 5 consecutive columns starting at 10, 15, 20, 25, 30
    "reseau_blocks": [10, 15, 20, 25, 30],
    "adresse":       35,  # "Adresse"
    "telephone":     36,  # "Téléphone"
    "nom_agent":     37,  # "Nom de l'agent"
    "tel_agent":     38,  # "Téléphone de l'agent"
    # 9 email columns starting at 39
    "emails_start":  39,
    "emails_end":    48,  # exclusive
}

# Each réseau block: [offset] réseau, [+1] pseudo, [+2] url, [+3] taille, [+4] engagement
BLOCK_RESEAU = 0
BLOCK_PSEUDO = 1
BLOCK_URL = 2
BLOCK_TAILLE = 3
BLOCK_ENGAGEMENT = 4


# =========================================================================
# Métier rules — derived from tools/veille_kolsquare/filtering_rules.md
# =========================================================================

EXCLUDED_METIERS: Set[str] = {
    "politics",
    "actor", "fim_actor",
    "singer", "musician", "dj",
    "artist", "illustrator", "photographer",
    "humorist", "animator",
    "journalist", "speaker",
    "chef", "food_critic", "oenologist",
    "doctor",
    "ceo", "management", "marketing_and_communication",
    "fashion_designer", "hairdresser", "makeup_artist", "interior_designer",
    "dancer",
    "producer",
    "tatooist",
}

INCLUDED_SPORT_METIERS: Set[str] = {
    # Fitness
    "fitness", "fitness_athlete", "fitness_coach", "coach", "weight_lifting",
    # Running / athlétisme
    "running", "cross_country_running", "athletics", "other_athletics",
    "track_race", "long_jump", "pole_vaulting",
    # Endurance
    "triathlon", "cycling", "mountain_biking", "swimming", "canoeying",
    "ski_mountaineering",
    # Combat
    "boxing", "english_boxing", "fighting", "kickboxer", "judo",
    # Collectifs
    "rugby", "football", "basketball", "badminton",
    # Outdoor
    "adventurer", "climbing", "surfing", "skiing", "snowboard", "skateboard",
    "horse_riding", "windsurfing",
    # Mécaniques
    "moto_cross", "motocycling", "match_racing",
    # Autres
    "gymnastics", "artistic_gymnastics", "ice_sports", "tennis",
}

CONDITIONAL_METIERS: Set[str] = {
    "blogger", "influencer_global", "youtuber", "creator", "model",
}


# Base thresholds applied BEFORE the MCP check (on KolSquare's own data)
MIN_FOLLOWERS = 1000
MIN_ENGAGEMENT_BASE = 0.3  # % — very permissive, just cutting dead accounts


# =========================================================================
# Data model
# =========================================================================


@dataclass
class Prospect:
    # From KolSquare
    nom_pseudo: str = ""
    prenom: str = ""
    nom: str = ""
    metier_raw: str = ""
    metier_kind: str = ""  # "sport" | "conditional" | "unknown" (no métier)
    ig_username: str = ""
    ig_followers: int = 0
    ig_engagement: float = 0.0
    url_kolsquare: str = ""
    emails: List[str] = field(default_factory=list)
    nom_agent: str = ""
    has_agent: bool = False

    # From MCP check (populated in phase 3)
    mcp_checked: bool = False
    mcp_followers: int = 0
    mcp_engagement: float = 0.0
    mcp_bio: str = ""
    mcp_sponsor: str = ""  # name of competitor detected, if any
    mcp_sport: str = ""  # detected sport keyword from bio
    mcp_score: int = 0
    mcp_verdict: str = ""  # GO / MAYBE / NO-GO / DISQUALIFIÉ (privé)
    mcp_is_private: bool = False

    # Final priority
    priority: str = ""  # P1 / P2 / P3 / EXCLUDE

    def effective_followers(self) -> int:
        return self.mcp_followers or self.ig_followers

    def effective_engagement(self) -> float:
        return self.mcp_engagement or self.ig_engagement


# =========================================================================
# Phase 1 — CSV parsing + métier filter
# =========================================================================


def _parse_metiers(raw: str) -> List[str]:
    if not raw or raw.strip() in ("", "-"):
        return []
    parts = [m.strip().lower() for m in raw.split(",")]
    return [p for p in parts if p]


def classify_metiers(metiers: List[str]) -> Tuple[str, str]:
    """Return (kind, reason).

    kind ∈ {"include_sport", "include_conditional", "include_unknown", "exclude"}.
    """
    if not metiers:
        return "include_unknown", "pas de métier renseigné"

    # Any sport métier → keep
    sport_hits = [m for m in metiers if m in INCLUDED_SPORT_METIERS or m.startswith("disabilities_")]
    if sport_hits:
        return "include_sport", f"sport: {', '.join(sport_hits)}"

    # Any conditional métier → keep for MCP validation
    cond_hits = [m for m in metiers if m in CONDITIONAL_METIERS]
    if cond_hits:
        return "include_conditional", f"conditional: {', '.join(cond_hits)}"

    # All remaining métiers must be in EXCLUDED to reject
    unknown = [m for m in metiers if m not in EXCLUDED_METIERS]
    if not unknown:
        return "exclude", f"excluded: {', '.join(metiers)}"

    # Mix of unknown + maybe excluded → keep as unknown for MCP
    return "include_unknown", f"unknown: {', '.join(unknown)}"


def _pick_instagram_from_row(row: List[str]) -> Tuple[str, int, float]:
    """Return (username, followers, engagement_pct) from the 5 réseau blocks."""
    for offset in CSV_IDX["reseau_blocks"]:
        if len(row) <= offset + BLOCK_ENGAGEMENT:
            continue
        reseau = row[offset + BLOCK_RESEAU].strip().lower()
        if reseau != "instagram":
            continue
        username = row[offset + BLOCK_PSEUDO].strip().lstrip("@").lower()
        followers_raw = row[offset + BLOCK_TAILLE].strip()
        engagement_raw = row[offset + BLOCK_ENGAGEMENT].strip()

        try:
            followers = int(float(followers_raw)) if followers_raw else 0
        except ValueError:
            followers = 0

        try:
            engagement = float(engagement_raw) if engagement_raw else 0.0
        except ValueError:
            engagement = 0.0

        return username, followers, engagement
    return "", 0, 0.0


def _extract_emails(row: List[str]) -> List[str]:
    start = CSV_IDX["emails_start"]
    end = CSV_IDX["emails_end"]
    emails = []
    for i in range(start, end):
        if i >= len(row):
            break
        val = row[i].strip()
        if val and val not in emails:
            emails.append(val)
    return emails


def _guess_first_last(nom_pseudo: str, prenom: str, nom: str) -> Tuple[str, str]:
    """Return (prenom, nom) using KolSquare cols first, then parsing nom_pseudo."""
    prenom = prenom.strip()
    nom = nom.strip()
    if prenom or nom:
        return prenom, nom

    display = nom_pseudo.strip()
    if not display:
        return "", ""

    tokens = display.split()
    if len(tokens) == 1:
        return tokens[0], ""

    # Heuristic: last token in ALL CAPS → family name.
    last = tokens[-1]
    if last.isupper() and len(last) > 1:
        return " ".join(tokens[:-1]), last
    # Fall back : first = prenom, rest = nom
    return tokens[0], " ".join(tokens[1:])


def load_kolsquare_csv(path: Path) -> Tuple[List[Prospect], Dict[str, int]]:
    stats = {
        "total": 0,
        "no_instagram": 0,
        "excluded_metier": 0,
        "below_min_followers": 0,
        "below_min_engagement": 0,
        "kept": 0,
    }
    prospects: List[Prospect] = []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, None)
        if header is None:
            raise RuntimeError(f"empty CSV: {path}")

        for row in reader:
            stats["total"] += 1

            ig_username, ig_followers, ig_engagement = _pick_instagram_from_row(row)
            if not ig_username:
                stats["no_instagram"] += 1
                continue

            metier_raw = row[CSV_IDX["metiers"]].strip() if len(row) > CSV_IDX["metiers"] else ""
            metiers = _parse_metiers(metier_raw)
            kind, _reason = classify_metiers(metiers)
            if kind == "exclude":
                stats["excluded_metier"] += 1
                continue

            if ig_followers < MIN_FOLLOWERS:
                stats["below_min_followers"] += 1
                continue

            if ig_engagement < MIN_ENGAGEMENT_BASE:
                stats["below_min_engagement"] += 1
                continue

            prenom_raw = row[CSV_IDX["prenom"]] if len(row) > CSV_IDX["prenom"] else ""
            nom_raw = row[CSV_IDX["nom"]] if len(row) > CSV_IDX["nom"] else ""
            nom_pseudo_raw = row[CSV_IDX["nom_pseudo"]] if len(row) > CSV_IDX["nom_pseudo"] else ""
            prenom, nom = _guess_first_last(nom_pseudo_raw, prenom_raw, nom_raw)

            nom_agent = row[CSV_IDX["nom_agent"]].strip() if len(row) > CSV_IDX["nom_agent"] else ""
            url_kol = row[CSV_IDX["url"]].strip() if len(row) > CSV_IDX["url"] else ""

            prospects.append(Prospect(
                nom_pseudo=nom_pseudo_raw.strip(),
                prenom=prenom,
                nom=nom,
                metier_raw=metier_raw or "-",
                metier_kind=kind.replace("include_", ""),
                ig_username=ig_username,
                ig_followers=ig_followers,
                ig_engagement=ig_engagement,
                url_kolsquare=url_kol,
                emails=_extract_emails(row),
                nom_agent=nom_agent,
                has_agent=bool(nom_agent),
            ))
            stats["kept"] += 1

    return prospects, stats


# =========================================================================
# Phase 2 — Dedupe against Google Sheet
# =========================================================================


def load_tracked_usernames() -> Set[str]:
    tracked: Set[str] = set()

    def _collect(tab_name: str, col_idx: int, skip_header: int) -> int:
        n = 0
        try:
            ws = get_worksheet(tab_name, SHEET_ID)
        except Exception as e:
            logger.warning("cannot open %s: %s", tab_name, e)
            return 0
        all_rows = ws.get_all_values()
        data_rows = all_rows[skip_header:]
        for row in data_rows:
            if len(row) <= col_idx:
                continue
            u = row[col_idx].strip().lstrip("@").lower()
            # Strip Instagram URL prefixes if someone pasted a link instead
            if "instagram.com/" in u:
                u = u.rsplit("instagram.com/", 1)[-1].rstrip("/")
            if u:
                tracked.add(u)
                n += 1
        return n

    # Suivi_Amb / Suivi_Dot / Suivi_Paid : 3 header rows.
    # Archive : 1 header row, username in col A (index 0).
    for tab, col, skip in [
        ("Suivi_Amb", SUIVI_AMB_COLS["username"], HEADER_ROW),
        ("Suivi_Dot", SUIVI_DOT_COLS["insta"], HEADER_ROW),
        ("Suivi_Paid", SUIVI_PAID_COLS["insta_name"], HEADER_ROW),
        ("Archive", 0, 1),
    ]:
        added = _collect(tab, col, skip)
        logger.info("loaded %d usernames from %s", added, tab)

    return tracked


def dedupe(prospects: List[Prospect], tracked: Set[str]) -> Tuple[List[Prospect], int]:
    kept: List[Prospect] = []
    removed = 0
    for p in prospects:
        if p.ig_username in tracked:
            removed += 1
            continue
        kept.append(p)
    return kept, removed


# =========================================================================
# Phase 3 — MCP Instagram check
# =========================================================================


def mcp_qualify_all(
    prospects: List[Prospect],
    *,
    limit: Optional[int] = None,
    pause_every: int = 50,
) -> Dict[str, int]:
    """Call qualify_profile() from qualify_influencer.py on each prospect.

    Populates mcp_* fields in-place. Returns stats dict.
    """
    stats = {
        "checked": 0,
        "errors": 0,
        "private": 0,
        "sponsor_conflict": 0,
        "go": 0,
        "maybe": 0,
        "nogo": 0,
    }

    targets = prospects if limit is None else prospects[:limit]
    logger.info("MCP qualify — %d profils (compte veille)", len(targets))

    ig_client = get_ig_client("veille")
    ig_client.request_timeout = 5
    # Instagram's public (anonymous) endpoint currently returns HTTP 201 with
    # broken JSON, which makes instagrapi retry 3x before falling back to the
    # private API — wasting ~30s per profile. Force the v1 (private API) path
    # directly so we skip the broken public endpoint entirely.
    ig_client.user_info_by_username = ig_client.user_info_by_username_v1
    ig_client.user_medias = ig_client.user_medias_v1
    logger.info("veille client ready (forced v1 endpoints)")

    for idx, p in enumerate(targets, 1):
        logger.info("[%d/%d] @%s", idx, len(targets), p.ig_username)
        try:
            result = qualify_profile(ig_client, p.ig_username)
        except Exception as e:
            logger.warning("  qualify_profile exception: %s", e)
            p.mcp_checked = True
            p.mcp_verdict = f"ERREUR ({e.__class__.__name__})"
            stats["errors"] += 1
            sleep_random(3, 5)
            continue

        p.mcp_checked = True
        p.mcp_followers = result.get("followers", 0) or 0
        p.mcp_engagement = result.get("engagement_rate", 0.0) or 0.0
        p.mcp_bio = result.get("bio_excerpt", "") or ""
        p.mcp_sport = result.get("sport", "") or ""
        p.mcp_score = result.get("total_score", 0) or 0

        verdict_raw = result.get("verdict", "") or ""

        # Hard exclusions layered on top of qualify_profile's native verdict
        if "DISQUALIFIÉ" in verdict_raw or "privé" in verdict_raw.lower():
            p.mcp_is_private = True
            p.mcp_verdict = "NO-GO (privé)"
            stats["private"] += 1
        else:
            # Competitor detection from flags
            flags = result.get("flags", []) or []
            sponsor = ""
            for flag in flags:
                if flag.startswith("concurrent:"):
                    sponsor = flag.replace("concurrent:", "").strip()
                    break
            if sponsor:
                p.mcp_sponsor = sponsor
                p.mcp_verdict = f"NO-GO (sponsor: {sponsor})"
                stats["sponsor_conflict"] += 1
            elif "GO" in verdict_raw and "NO" not in verdict_raw:
                p.mcp_verdict = "GO"
                stats["go"] += 1
            elif "MAYBE" in verdict_raw:
                p.mcp_verdict = "MAYBE"
                stats["maybe"] += 1
            else:
                p.mcp_verdict = "NO-GO"
                stats["nogo"] += 1

        stats["checked"] += 1

        # Rate-limit between profiles. qualify_profile already sleeps 1s
        # between user_info and user_medias, so here we only need a short
        # pause. antman.lass is a dedicated veille account — ban risk is
        # acceptable for a one-shot mission.
        sleep_random(0.5, 1.5)

        if idx % pause_every == 0 and idx < len(targets):
            logger.info("  — breather (every %d profiles)", pause_every)
            sleep_random(15, 20)

    return stats


# =========================================================================
# Priority assignment
# =========================================================================


def compute_priority(p: Prospect) -> str:
    """Return P1 / P2 / P3 / EXCLUDE based on metier + followers + engagement."""

    # Hard exclusion (from MCP check)
    if p.mcp_checked:
        if p.mcp_is_private:
            return "EXCLUDE"
        if p.mcp_sponsor:
            return "EXCLUDE"
        if "NO-GO" in p.mcp_verdict:
            return "EXCLUDE"

    followers = p.effective_followers()
    engagement = p.effective_engagement()

    if followers < MIN_FOLLOWERS:
        return "EXCLUDE"

    # P1 : sport + eng > 1% + 5k-50k
    if (
        p.metier_kind == "sport"
        and engagement > 1.0
        and 5_000 <= followers <= 50_000
    ):
        return "P1"

    # P2 : sport + eng > 0.5% + 2k-100k
    if (
        p.metier_kind == "sport"
        and engagement > 0.5
        and 2_000 <= followers <= 100_000
    ):
        return "P2"

    # P3 : conditional/unknown with decent engagement
    if (
        p.metier_kind in ("conditional", "unknown")
        and engagement > 0.5
        and followers >= 2_000
    ):
        return "P3"

    # P3 : sport profile that missed P1/P2 thresholds (e.g. 1k-2k or 100k+)
    if p.metier_kind == "sport" and engagement > 0.5:
        return "P3"

    return "EXCLUDE"


# =========================================================================
# Output CSV + recap
# =========================================================================


OUTPUT_COLS = [
    "username", "prenom", "nom", "metier_raw", "metier_kind",
    "followers", "engagement_pct",
    "mcp_checked", "mcp_verdict", "mcp_score", "mcp_bio", "mcp_sponsor", "mcp_sport",
    "priority", "has_agent", "nom_agent",
    "emails", "url_kolsquare",
]


def write_output_csv(prospects: List[Prospect], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLS)
        for p in prospects:
            writer.writerow([
                p.ig_username,
                p.prenom,
                p.nom,
                p.metier_raw,
                p.metier_kind,
                p.effective_followers(),
                f"{p.effective_engagement():.2f}",
                "yes" if p.mcp_checked else "no",
                p.mcp_verdict,
                p.mcp_score,
                p.mcp_bio,
                p.mcp_sponsor,
                p.mcp_sport,
                p.priority,
                "yes" if p.has_agent else "no",
                p.nom_agent,
                " | ".join(p.emails),
                p.url_kolsquare,
            ])


def print_recap(
    csv_stats: Dict[str, int],
    dedupe_removed: int,
    mcp_stats: Optional[Dict[str, int]],
    prospects: List[Prospect],
) -> None:
    print()
    print("=" * 64)
    print(" KOLSQUARE FILTER — RECAP")
    print("=" * 64)
    print(f"CSV total rows              : {csv_stats['total']}")
    print(f"  no Instagram handle       : {csv_stats['no_instagram']}")
    print(f"  excluded by métier        : {csv_stats['excluded_metier']}")
    print(f"  below min followers (1k)  : {csv_stats['below_min_followers']}")
    print(f"  below min engagement 0.3% : {csv_stats['below_min_engagement']}")
    print(f"  kept after phase 1        : {csv_stats['kept']}")
    print()
    print(f"Dedupe removed (already in sheet) : {dedupe_removed}")
    print(f"After dedupe                      : {csv_stats['kept'] - dedupe_removed}")
    print()

    if mcp_stats:
        print(f"MCP check — checked   : {mcp_stats['checked']}")
        print(f"  errors              : {mcp_stats['errors']}")
        print(f"  private             : {mcp_stats['private']}")
        print(f"  sponsor conflict    : {mcp_stats['sponsor_conflict']}")
        print(f"  GO                  : {mcp_stats['go']}")
        print(f"  MAYBE               : {mcp_stats['maybe']}")
        print(f"  NO-GO (other)       : {mcp_stats['nogo']}")
        print()
    else:
        print("MCP check           : SKIPPED (--no-mcp)")
        print()

    # Priority counts
    by_prio: Dict[str, int] = {"P1": 0, "P2": 0, "P3": 0, "EXCLUDE": 0}
    for p in prospects:
        by_prio[p.priority] = by_prio.get(p.priority, 0) + 1
    print("Priority breakdown (post-scoring) :")
    for k in ("P1", "P2", "P3", "EXCLUDE"):
        print(f"  {k:<8} : {by_prio.get(k, 0)}")
    print()

    # Agence flags
    agence = [p for p in prospects if p.has_agent and p.priority != "EXCLUDE"]
    print(f"Flaggés AGENCE (à traiter manuellement) : {len(agence)}")
    if agence:
        print("  (premiers 10) :")
        for p in agence[:10]:
            print(f"    @{p.ig_username} — {p.nom_agent} — {p.priority}")
    print()

    # Top 20 by score then engagement
    ranked = sorted(
        [p for p in prospects if p.priority != "EXCLUDE"],
        key=lambda x: (x.mcp_score, x.effective_engagement()),
        reverse=True,
    )
    print(f"Top 20 GO/MAYBE profiles :")
    for p in ranked[:20]:
        followers_str = format_followers_k(p.effective_followers())
        print(
            f"  {p.priority:<3} @{p.ig_username:<25} "
            f"{followers_str:>6}k  eng {p.effective_engagement():>4.1f}%  "
            f"score {p.mcp_score:>+3d}  {p.mcp_verdict}"
        )
    print()
    print("=" * 64)


# =========================================================================
# Main
# =========================================================================


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to KolSquare CSV export")
    parser.add_argument("--output", required=True, help="Path to write filtered CSV")
    parser.add_argument("--no-mcp", action="store_true", help="Skip phase 3 (MCP Instagram check)")
    parser.add_argument("--limit", type=int, default=None, help="MCP-check at most N profiles (testing)")
    parser.add_argument("--no-dedupe", action="store_true", help="Skip dedupe against the Google Sheet")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    _setup_logging(args.verbose)

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        logger.error("input CSV not found: %s", input_path)
        return 2

    logger.info("phase 1 — parsing CSV : %s", input_path)
    prospects, csv_stats = load_kolsquare_csv(input_path)
    logger.info(
        "phase 1 done — %d rows, %d kept after métier + base filters",
        csv_stats["total"], csv_stats["kept"],
    )

    dedupe_removed = 0
    if not args.no_dedupe:
        logger.info("phase 2 — dedupe against Suivi_Amb / Suivi_Dot / Suivi_Paid / Archive")
        tracked = load_tracked_usernames()
        logger.info("tracked usernames pooled : %d", len(tracked))
        prospects, dedupe_removed = dedupe(prospects, tracked)
        logger.info("phase 2 done — removed %d duplicates", dedupe_removed)

    mcp_stats: Optional[Dict[str, int]] = None
    if not args.no_mcp:
        logger.info("phase 3 — MCP Instagram check (compte veille antman.lass)")
        mcp_stats = mcp_qualify_all(prospects, limit=args.limit)
        logger.info("phase 3 done — checked %d profiles", mcp_stats["checked"])

    # Assign priority to everyone
    for p in prospects:
        p.priority = compute_priority(p)

    write_output_csv(prospects, output_path)
    logger.info("wrote %d rows to %s", len(prospects), output_path)

    print_recap(csv_stats, dedupe_removed, mcp_stats, prospects)

    print(f"\nSTOP — dry-run. Output CSV : {output_path}")
    print("Relire le recap + le CSV, puis lancer kolsquare_to_sheet.py pour insérer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
