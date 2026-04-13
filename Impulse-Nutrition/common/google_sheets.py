"""Google Sheets access + column schema for Impulse Nutrition spreadsheets.

This module is the SINGLE SOURCE OF TRUTH for column indices in the
`Suivi_Amb`, `Suivi_Dot`, `Suivi_Paid` and `VeilleConcu` tabs.

Scripts in `instagram_dm_mcp/` used to hardcode `row[8]` / `row[27]` / `row[32]`
inline and drifted from the real sheet as columns were added. The constants
below are derived from the actual headers of the spreadsheet
(audited 2026-04-13) — do not modify unless the sheet is re-designed.

See `docs/reference_sheet_schema.md` for the human-readable version.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

SHEET_ID = "1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4"

DEFAULT_CREDS_PATH = Path.home() / ".config" / "google-service-account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Rows 1-2 = section labels ("Contact", "Info de base", "Infos athlètes").
# Row 3 = actual column headers.
# Row 4+ = data.
HEADER_ROW = 3
DATA_START_ROW = 4


# =========================================================================
# Column maps — keys are semantic names, values are 0-indexed positions.
# =========================================================================

# Suivi_Amb — pipeline ambassadeur entrée / affiliation pure.
# Real header row 3 was audited on 2026-04-13.
SUIVI_AMB_COLS = {
    "type":               0,   # A — "Type"
    "message":            1,   # B — "Message"
    "premier_message":    2,   # C — "Premier Message"
    "commandes":          3,   # D — "Commandes"
    "relance":            4,   # E — "Relance"
    "avis":               5,   # F — "Avis"
    "mention_bio":        6,   # G — "Mention Bio"
    "ig_link":            7,   # H — "IG link"
    "username":           8,   # I — "Compte @"
    "statut":             9,   # J — "Statut"
    "action":             10,  # K — "Action/Commentaire"
    "priorite":           11,  # L — "Priorités identifiées"
    "campagne":           12,  # M — "Campagne"
    "code_affilie":       13,  # N — "Code affiliation"
    "nb_utilisation":     14,  # O — "Nb Utilsation"
    "code_credit":        15,  # P — "Code crédit"
    "nb_credit_used":     16,  # Q — "Nb Credit Used"
    "lien_affilie":       17,  # R — "Lien affiliation"
    "taux_engagement":    18,  # S — "Taux engagement"
    "affiliatly":         19,  # T — "Affiliatly"
    "mail_amb":           20,  # U — "Mail Ambassadeur"
    "bio":                21,  # V — "Bio"
    "sport":              22,  # W — "Sport"
    "sponsor":            23,  # X — "Sponsor"
    "followers_k":        24,  # Y — "Followers (k)"
    "date_premier_contact": 25,  # Z — "Date"
    "nb_story":           26,  # AA — "Nb Story"
    "nb_post":            27,  # AB — "Nb post"
    "colonne_32":         28,  # AC — "Column 32"
    "nom":                29,  # AD — "Nom"
    "prenom":             30,  # AE — "Prenom"
    "mail":               31,  # AF — "Mail"
    "numero":             32,  # AG — "Numéro"
    "adresse":            33,  # AH — "Adresse"
    "info_contract":      34,  # AI — "Info contract"
    "id_influ":           35,  # AJ — "ID Influ"
    "contract":           36,  # AK — "Contract"
    "date_1ere_commande": 37,  # AL — "Date 1ère commande"
}

# Suivi_Dot — dotation mensuelle (S/M/L tiers, 4 mois renouvelables).
# Contract type "ATHLETE" in generate_contract.py.
SUIVI_DOT_COLS = {
    "name":                 0,  # A — "Name"
    "management":           1,  # B — "Management" (agence)
    "statut_deal":          2,  # C — "Statut Deal"
    "type":                 3,  # D — "Type" (S / M / L)
    "action":               4,  # E — "Action / Com"
    "mail":                 5,  # F — "Mail"
    "numero":               6,  # G — "Numéro"
    "prenom":               7,  # H — "Prénom"
    "nom":                  8,  # I — "Nom"
    "affiliatly":           9,  # J — "Affiliatly"
    "code_dotation":        10, # K — "Code Dotation"
    "id_influ":             11, # L — "ID Influ"
    "insta":                12, # M — "Insta"
    "tiktok":               13, # N — "@TikTok"
    "youtube":              14, # O — "@YT"
    "strava":               15, # P — "@Strava"
    # Q(16) reserved
    "code":                 17, # R — "Code"
    "util_ytd":             18, # S — "Util YTD"
    "kf_actual":            19, # T — "kF Actual"
    "evolution":            20, # U — "Evolution"
    "whitelisting":         21, # V — "Whitelisting"
    # W(22) reserved
    "followers_k_init":     23, # X — "(k)Insta Init"
    "debut":                24, # Y — "Début"
    "fin":                  25, # Z — "Fin"
    "duree":                26, # AA — "Durée"
    "dotation_eur":         27, # AB — "Dotation (€)"
    "seuil_renouvellement": 28, # AC — "Seuil renouvellement"
    "agreement":            29, # AD — "Agreement"
    "pdf":                  30, # AE — "PDF"
    "adresse":              31, # AF — "Adresse"
}

# Suivi_Paid — contrats rémunérés (fixe HT + variable).
# Contract type "INFLUENCEUR" in generate_contract.py.
SUIVI_PAID_COLS = {
    "name":              0,  # A — "Name"
    "management":        1,  # B — "Management"
    "statut_deal":       2,  # C — "Statut Deal"
    "type":              3,  # D — "Type"
    "action":            4,  # E — "Action / Com"
    "mail":              5,  # F — "Mail"
    "prenom":            6,  # G — "Prénom"
    "nom":               7,  # H — "Nom"
    "affiliatly":        8,  # I — "Affiliatly"
    "insta_name":        9,  # J — "@InstaName"
    "insta_id":          10, # K — "@Insta ID"
    "tiktok":            11, # L — "@TikTok"
    "youtube":           12, # M — "@YT"
    "date_derniere_cmd": 13, # N — "Date dernière commande"
    # O(14) reserved
    "code":              15, # P — "Code"
    "util":              16, # Q — "Util"
    "kf_actual":         17, # R — "kF Actual"
    "evolution":         18, # S — "Evolution"
    "whitelisting":      19, # T — "Whitelisting"
    # U(20) reserved
    "followers_k_init":  21, # V — "(k)Insta Init"
    "fixe":              22, # W — "Fixe"
    "var_prov":          23, # X — "Var. prov."
    "budget_total":      24, # Y — "Budget total"
    "debut":             25, # Z — "Début"
    "fin":               26, # AA — "Fin"
    "duree":             27, # AB — "Durée"
    "eur_pct":           28, # AC — "€ / %"
    "dotation_eur":      29, # AD — "Dotation (€)"
    "seuil_util":        30, # AE — "Seuil util"
    "bio_linkt":         31, # AF — "Bio/LinkT"
    "a_la_une":          32, # AG — "à la une"
    "reels_post":        33, # AH — "Réels/post"
    "stories":           34, # AI — "Stories"
    "youtube_obl":       35, # AJ — "Youtube"
    "strava_obl":        36, # AK — "Strava"
    "tiktok_obl":        37, # AL — "Tiktok"
    "pdf":               38, # AM — "PDF"
}

# VeilleConcu — competitor tracking (1-row header, data starts row 2).
VEILLE_COLS = {
    "marque":              0,
    "instagram":           1,
    "instagram_id":        2,
    "categorie":           3,
    "positionnement":      4,
    "followers":           5,
    "following":           6,
    "nb_posts":            7,
    "engagement_pct":      8,
    "avg_likes":           9,
    "avg_comments":       10,
    "freq_post_sem":      11,
    "dernier_post":       12,
    "pct_reels":          13,
    "pct_carousels":      14,
    "pct_photos":         15,
    "bio":                16,
    "url_externe":        17,
    "verifie":            18,
    "followers_m_1":      19,
    "delta_followers":    20,
    "engagement_m_1":     21,
    "delta_engagement":   22,
    "ambassadeurs_communs": 23,
    "campagne_detectee":  24,
    "notes":              25,
    "derniere_maj":       26,
}

# VeilleConcu uses row 1 as headers, data starts row 2.
VEILLE_HEADER_ROW = 1
VEILLE_DATA_START_ROW = 2


# =========================================================================
# Client helpers
# =========================================================================


@lru_cache(maxsize=1)
def get_gspread_client(creds_path: Optional[str] = None):
    """Return a cached `gspread` client authorized against the service account.

    Lazy-imports gspread so scripts that don't touch Sheets can import this
    module cheaply. Override the default creds path via argument or the
    `GOOGLE_SERVICE_ACCOUNT_PATH` env var.
    """
    import gspread
    from google.oauth2.service_account import Credentials

    path = creds_path or os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_PATH", str(DEFAULT_CREDS_PATH)
    )
    creds = Credentials.from_service_account_file(path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet(tab_name: str, sheet_id: str = SHEET_ID):
    """Open the Impulse Nutrition spreadsheet and return a worksheet handle."""
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id).worksheet(tab_name)


def get_data_rows(
    ws, skip_header_rows: int = HEADER_ROW
) -> List[List[str]]:
    """Fetch `ws.get_all_values()` and drop the `skip_header_rows` prefix rows.

    For `Suivi_Amb`/`Suivi_Dot`/`Suivi_Paid` pass `skip_header_rows=3`.
    For `VeilleConcu` pass `skip_header_rows=1`.
    """
    rows = ws.get_all_values()
    return rows[skip_header_rows:]


def col_letter_to_idx(letter: str) -> int:
    """Convert an A1-style column letter to a 0-indexed position.

    Examples:
        'A'  -> 0
        'Z'  -> 25
        'AA' -> 26
        'AM' -> 38
    """
    letter = letter.upper().strip()
    idx = 0
    for c in letter:
        idx = idx * 26 + (ord(c) - ord("A") + 1)
    return idx - 1


def idx_to_col_letter(idx: int) -> str:
    """Inverse of `col_letter_to_idx`. 0 -> 'A', 26 -> 'AA'."""
    result = ""
    n = idx + 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(ord("A") + rem) + result
    return result
