"""
Migration one-shot : Suivi_Amb (ancien) → Suivi_Amb_v2 (nouveau layout 29 colonnes).

Lit toutes les données de l'ancien sheet, transforme col E en Action + Campagne + Commentaire,
et écrit dans Suivi_Amb_v2.

Usage :
    python migrate_suivi_amb.py [--dry-run]  # dry-run = affiche sans écrire
"""

import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# Google Sheets MCP helpers — ce script est conçu pour tourner via Claude MCP
# mais peut aussi être exécuté standalone avec gspread.
# ---------------------------------------------------------------------------

try:
    import gspread
    from google.oauth2.service_account import Credentials
    USE_GSPREAD = True
except ImportError:
    USE_GSPREAD = False

SPREADSHEET_ID = "1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4"
OLD_SHEET = "Suivi_Amb"
NEW_SHEET = "Suivi_Amb_v2"

# Old sheet: 2 group header rows + 1 header row → data starts at row 4 (index 3)
OLD_HEADER_ROWS = 3

# ---------------------------------------------------------------------------
# Column mapping: old index → new index
# Old columns (0-indexed from A):
#   0=Compte@, 1=IGlink, 2=Maiavis, 3=Statut, 4=Action/Com, 5=Priorité,
#   6=IDInflu, 7=typecontrat, 8=Sport, 9=Sponsor, 10=Followers, 11=Date,
#   12=Tauxengagement, 13=%FRengagée, 14=Col32, 15=Message, 16=PremierMsg,
#   17=Relance, 18=Avis, 19=MentionBio, 20=Type, 21=Col32, 22=NbStory,
#   23=Nbpost, 24=Messageavis, 25=Affiliatly, 26=Relanceenvoyée, 27=MailAmba,
#   28=Bio, 29=Highlight, 30=LinkT, 31=Info, 32=Nbcommande, 33=Nbutilecode,
#   34=€, 35=Col32, 36=Lienaffiliation, 37=Codeaffiliation, 38=Msgcommande,
#   39=Nom, 40=Prenom, 41=Mail, 42=Numéro, 43=Adresse, 44=Commentaire
# ---------------------------------------------------------------------------

# Direct column mappings: new_index → old_index
DIRECT_MAP = {
    0: 0,    # A Compte @ ← A
    1: 1,    # B IG link ← B
    2: 3,    # C Statut ← D
    # 3 (D Action) ← transformed from E (4)
    # 4 (E Campagne) ← transformed from E (4)
    5: 5,    # F Priorité ← F
    6: 8,    # G Sport ← I
    7: 9,    # H Sponsor ← J
    8: 10,   # I Followers ← K
    9: 11,   # J Date 1er contact ← L
    10: 12,  # K Taux engagement ← M
    11: 13,  # L % FR engagée ← N
    12: 7,   # M Type contrat ← H
    # 13 (N Bio Impulse) ← empty
    # 14 (O Nb partages) ← empty
    # 15 (P Dernier partage) ← empty
    16: 25,  # Q Affiliatly ← Z
    17: 37,  # R Code affiliation ← AL
    18: 36,  # S Lien affiliation ← AK
    19: 32,  # T Cdes envoyées ← AG
    20: 33,  # U Utilisations code ← AH
    21: 34,  # V CA généré ← AI
    22: 40,  # W Prénom ← AO
    23: 39,  # X Nom ← AN
    24: 41,  # Y Mail ← AP
    25: 42,  # Z Numéro ← AQ
    26: 43,  # AA Adresse ← AR
    27: 6,   # AB ID Influ ← G
    # 28 (AC Commentaire) ← AS (44) + AF Info (31) + leftovers from E
}


def safe_get(row, idx):
    """Get value from row by index, return '' if out of range."""
    if idx < len(row):
        return row[idx] if row[idx] is not None else ""
    return ""


def transform_action_column(old_e_value):
    """
    Transform old col E (Action/Commentaire) into:
      (action, campagne, comment_extra)
    """
    val = str(old_e_value).strip()
    val_lower = val.lower()

    if not val:
        return ("", "", "")

    # Exact matches first
    if val_lower == "ras":
        return ("RAS", "", "")

    if val_lower == "ras - promo envoyée":
        return ("RAS", "Promo-20% mars OK", "")

    if val_lower == "répondre au message":
        return ("Répondre", "", "")

    if val_lower in ("à relancer", "a relancer"):
        return ("Relancer", "", "")

    # "à relancer en [mois/date]"
    m = re.match(r"(?:à|a) relancer en (.+)", val_lower)
    if m:
        return ("Relancer", "", f"Relancer en {m.group(1)}")

    if val_lower == "préparer sa commande":
        return ("Préparer commande", "", "")

    if val_lower == "réagir à story" or val_lower == "reagir a story":
        return ("Réagir story", "", "")

    if val_lower == "demander avis produits":
        return ("Demander avis", "", "")

    if val_lower == "demander avis produits - promo envoyée" or \
       val_lower == "demander avis - promo envoyée":
        return ("Demander avis", "Promo-20% mars OK", "")

    if val_lower == "-20% check":
        return ("RAS", "Promo-20% mars OK", "")

    if val_lower == "ras - promo envoyée":
        return ("RAS", "Promo-20% mars OK", "")

    # Fraichtouch / Contacter manager
    if "fraichtouch" in val_lower or "contacter manager" in val_lower:
        return ("Contacter manager", "", val)

    # "Appeler ... +33..."
    if val_lower.startswith("appeler"):
        return ("Appeler", "", val)

    # "Hyper chaud envoyer commande"
    if "hyper chaud" in val_lower:
        return ("Préparer commande", "", "Hyper chaud")

    # "répondre à son mail dotation"
    if "répondre à son mail" in val_lower or "répondre a son mail" in val_lower:
        return ("Répondre", "", val)

    # "envoyer code" or similar
    if "envoyer code" in val_lower or "envoyer le code" in val_lower:
        return ("Envoyer code", "", "")

    # Default: best-effort match, preserve original as comment
    # Try to detect action keywords
    if "relancer" in val_lower or "relance" in val_lower:
        return ("Relancer", "", val)
    if "répondre" in val_lower or "repondre" in val_lower:
        return ("Répondre", "", val)
    if "commande" in val_lower:
        return ("Préparer commande", "", val)
    if "avis" in val_lower:
        return ("Demander avis", "", val)
    if "story" in val_lower:
        return ("Réagir story", "", val)
    if "promo" in val_lower and "envoyée" in val_lower:
        return ("RAS", "Promo-20% mars OK", val)

    # Free text → preserve in comment
    return ("", "", val)


def build_commentaire(old_commentaire, old_info, extra_from_e):
    """Concatenate old AS (Commentaire) + AF (Info) + extra from E transform."""
    parts = []
    if extra_from_e:
        parts.append(extra_from_e)
    if old_info:
        parts.append(str(old_info))
    if old_commentaire:
        parts.append(str(old_commentaire))
    return " | ".join(parts)


def migrate_row(old_row):
    """Transform a single old row into a new row (29 columns)."""
    new_row = [""] * 29

    # Direct mappings
    for new_idx, old_idx in DIRECT_MAP.items():
        new_row[new_idx] = safe_get(old_row, old_idx)

    # Transform col E → Action (D=3), Campagne (E=4), extra for Commentaire
    old_e = safe_get(old_row, 4)
    action, campagne, extra = transform_action_column(old_e)
    new_row[3] = action
    new_row[4] = campagne

    # Build Commentaire (AC=28)
    old_commentaire = safe_get(old_row, 44)
    old_info = safe_get(old_row, 31)
    new_row[28] = build_commentaire(old_commentaire, old_info, extra)

    # Leave N (13), O (14), P (15) empty — filled by audit_ambassadors.py

    return new_row


def read_old_data_gspread():
    """Read old sheet data via gspread."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(OLD_SHEET)
    return ws.get_all_values()


def write_new_data_gspread(rows):
    """Write migrated data to new sheet via gspread."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(NEW_SHEET)

    if rows:
        end_col = chr(ord("A") + len(rows[0]) - 1)
        cell_range = f"A2:{end_col}{len(rows) + 1}"
        ws.update(cell_range, rows, value_input_option="RAW")


def main():
    parser = argparse.ArgumentParser(description="Migrate Suivi_Amb to v2 layout")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing")
    parser.add_argument("--spot-check", type=int, default=20,
                        help="Number of rows to spot-check (default 20)")
    args = parser.parse_args()

    if not USE_GSPREAD:
        print("ERROR: gspread not installed. Install with: pip install gspread google-auth")
        print("Or run this migration via Claude MCP (recommended).")
        sys.exit(1)

    print("Reading old Suivi_Amb data...")
    all_values = read_old_data_gspread()

    # Skip header rows
    data_rows = all_values[OLD_HEADER_ROWS:]
    print(f"Found {len(data_rows)} data rows (after {OLD_HEADER_ROWS} header rows)")

    # Filter out empty rows
    data_rows = [r for r in data_rows if any(cell.strip() for cell in r if cell)]
    print(f"Non-empty rows: {len(data_rows)}")

    # Migrate
    migrated = []
    for i, old_row in enumerate(data_rows):
        new_row = migrate_row(old_row)
        migrated.append(new_row)

    print(f"Migrated {len(migrated)} rows")

    # Spot-check
    print(f"\n{'='*60}")
    print(f"SPOT-CHECK (first {args.spot_check} rows)")
    print(f"{'='*60}")
    headers = ["Compte @", "IG link", "Statut", "Action", "Campagne", "Priorité",
               "Sport", "Sponsor", "Followers", "Date 1er contact", "Taux engagement",
               "% FR engagée", "Type contrat", "Bio Impulse", "Nb partages",
               "Dernier partage", "Affiliatly", "Code affiliation", "Lien affiliation",
               "Cdes envoyées", "Utilisations code", "CA généré", "Prénom", "Nom",
               "Mail", "Numéro", "Adresse", "ID Influ", "Commentaire"]

    for i, row in enumerate(migrated[:args.spot_check]):
        username = row[0]
        print(f"\n--- Row {i+1}: @{username} ---")
        for j, (h, v) in enumerate(zip(headers, row)):
            if v:  # Only show non-empty
                print(f"  {chr(65+j)} {h}: {v[:80]}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would write {len(migrated)} rows to {NEW_SHEET}")
        return

    print(f"\nWriting {len(migrated)} rows to {NEW_SHEET}...")
    write_new_data_gspread(migrated)
    print("Migration complete!")


if __name__ == "__main__":
    main()
