"""
Refresh the Analyses sheet with formulas pointing to the new Suivi_Amb layout.

Writes COUNTIF/SUM formulas for:
  - Pipeline (by Statut, col J)
  - Actions en attente (keyword search in col K)
  - Campagne en cours (by Campagne, col M)
  - Suivi contenu (cols R, X, Y)
  - Top performers (engagement, contenu)
  - Engagement distribution
  - Sponsors concurrents détectés

Usage:
    python refresh_analyses.py [--dry-run]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.google_sheets import SHEET_ID as SPREADSHEET_ID  # noqa: E402

SHEET_NAME = "Analyses"
DATA_SHEET = "Suivi_Amb"


def build_formulas():
    """Build all formulas for the Analyses sheet."""
    formulas = {}

    # ─── Section 1: Pipeline (row 2-10, col H-J) ───
    formulas["H2"] = [["Pipeline"]]
    formulas["H3"] = [["Statut", "Nb", "% du total"]]

    statuts = [
        "In-cold", "In-hot", "A recontacter", "A rediscuter",
        "Contacter manager", "Produits envoyés", "Out"
    ]
    for i, statut in enumerate(statuts):
        row = 4 + i
        formulas[f"H{row}"] = [[
            statut,
            f'=COUNTIF({DATA_SHEET}!$J:$J;"{statut}")',
            f'=IF(SUM($I$4:$I$10)>0;I{row}/SUM($I$4:$I$10);0)',
        ]]
    formulas["H11"] = [["Total", "=SUM(I4:I10)", ""]]

    # ─── Section 2: Actions en attente (row 13-23, col H-I) ───
    formulas["H13"] = [["Actions en attente"]]
    formulas["H14"] = [["Mot-clé Action", "Nb"]]

    actions = [
        "répondre", "relancer", "préparer commande", "appeler",
        "réagir story", "contacter manager", "envoyer code",
        "demander avis", "ras"
    ]
    for i, action in enumerate(actions):
        row = 15 + i
        formulas[f"H{row}"] = [[action, f'=COUNTIF({DATA_SHEET}!$K:$K;"*{action}*")']]

    # Priorities
    formulas["H25"] = [["Priorités"]]
    formulas["H26"] = [["Priorité", "Nb"]]
    for i, prio in enumerate(["high", "medium", "good"]):
        row = 27 + i
        formulas[f"H{row}"] = [[prio, f'=COUNTIF({DATA_SHEET}!$L:$L;"{prio}")']]

    # ─── Section 3: Campagne en cours (row 32-36, col H-I) ───
    formulas["H32"] = [["Campagne en cours"]]
    formulas["H33"] = [["Métrique", "Valeur"]]
    formulas["H34"] = [["Restants (sans OK/SKIP)", f'=COUNTIFS({DATA_SHEET}!$M:$M;"<>";{DATA_SHEET}!$M:$M;"<>*OK*";{DATA_SHEET}!$M:$M;"<>*SKIP*";{DATA_SHEET}!$M:$M;"<>")']]
    formulas["H35"] = [["Envoyés (OK)", f'=COUNTIF({DATA_SHEET}!$M:$M;"*OK*")']]
    formulas["H36"] = [["Skippés (SKIP)", f'=COUNTIF({DATA_SHEET}!$M:$M;"*SKIP*")']]
    formulas["H37"] = [["% complétion", f'=IF((I35+I36)>0;I35/(I35+I36);0)']]

    # ─── Section 4: Suivi contenu (row 39-45, col H-I) ───
    formulas["H39"] = [["Suivi contenu (ambassadeurs actifs)"]]
    formulas["H40"] = [["Métrique", "Valeur"]]
    formulas["H41"] = [["Bio Impulse: oui", f'=COUNTIF({DATA_SHEET}!$R:$R;"oui")']]
    formulas["H42"] = [["Bio Impulse: non", f'=COUNTIF({DATA_SHEET}!$R:$R;"non")']]
    formulas["H43"] = [["Total stories partagées", f'=SUM({DATA_SHEET}!$X:$X)']]
    formulas["H44"] = [["Total posts partagés", f'=SUM({DATA_SHEET}!$Y:$Y)']]
    formulas["H45"] = [["Moyenne stories/ambassadeur", f'=IF(COUNTIF({DATA_SHEET}!$X:$X;">0")>0;I43/COUNTIF({DATA_SHEET}!$X:$X;">0");0)']]
    formulas["H46"] = [["Moyenne posts/ambassadeur", f'=IF(COUNTIF({DATA_SHEET}!$Y:$Y;">0")>0;I44/COUNTIF({DATA_SHEET}!$Y:$Y;">0");0)']]

    # ─── Section 5: Engagement distribution (row 48-57, col H-I) ───
    formulas["H48"] = [["Distribution engagement (col W)"]]
    formulas["H49"] = [["Tranche", "Nb ambassadeurs"]]
    formulas["H50"] = [["> 5%", f'=COUNTIF({DATA_SHEET}!$W:$W;">5%")']]
    formulas["H51"] = [["3% - 5%", f'=COUNTIFS({DATA_SHEET}!$W:$W;">3%";{DATA_SHEET}!$W:$W;"<=5%")']]
    formulas["H52"] = [["1% - 3%", f'=COUNTIFS({DATA_SHEET}!$W:$W;">1%";{DATA_SHEET}!$W:$W;"<=3%")']]
    formulas["H53"] = [["< 1%", f'=COUNTIFS({DATA_SHEET}!$W:$W;">0%";{DATA_SHEET}!$W:$W;"<=1%")']]
    formulas["H54"] = [["Non renseigné", f'=COUNTIF({DATA_SHEET}!$W:$W;"")']]
    formulas["H55"] = [["Engagement moyen", f'=IFERROR(AVERAGE({DATA_SHEET}!$W:$W);0)']]

    # ─── Section 6: Followers distribution (row 57-64, col H-I) ───
    formulas["H57"] = [["Distribution followers (col U)"]]
    formulas["H58"] = [["Tranche", "Nb"]]
    formulas["H59"] = [["> 50k", f'=COUNTIF({DATA_SHEET}!$U:$U;">50")']]
    formulas["H60"] = [["10k - 50k", f'=COUNTIFS({DATA_SHEET}!$U:$U;">10";{DATA_SHEET}!$U:$U;"<=50")']]
    formulas["H61"] = [["5k - 10k", f'=COUNTIFS({DATA_SHEET}!$U:$U;">5";{DATA_SHEET}!$U:$U;"<=10")']]
    formulas["H62"] = [["2k - 5k", f'=COUNTIFS({DATA_SHEET}!$U:$U;">2";{DATA_SHEET}!$U:$U;"<=5")']]
    formulas["H63"] = [["< 2k", f'=COUNTIFS({DATA_SHEET}!$U:$U;">0";{DATA_SHEET}!$U:$U;"<=2")']]
    formulas["H64"] = [["Followers moyen (k)", f'=IFERROR(AVERAGE({DATA_SHEET}!$U:$U);0)']]

    # ─── Section 7: Top performers — contenu (row 66-73, col H-J) ───
    formulas["H66"] = [["Top 5 stories (ambassadeurs actifs)"]]
    formulas["H67"] = [["Username", "Nb stories", "Nb posts"]]
    for i in range(5):
        row = 68 + i
        formulas[f"H{row}"] = [[
            f'=IFERROR(INDEX({DATA_SHEET}!$I:$I;MATCH(LARGE({DATA_SHEET}!$X:$X;{i+1});{DATA_SHEET}!$X:$X;0));"")',
            f'=IFERROR(LARGE({DATA_SHEET}!$X:$X;{i+1});"")',
            f'=IFERROR(INDEX({DATA_SHEET}!$Y:$Y;MATCH(LARGE({DATA_SHEET}!$X:$X;{i+1});{DATA_SHEET}!$X:$X;0));"")',
        ]]

    # ─── Section 8: Sponsors concurrents (row 74-82, col H-I) ───
    formulas["H74"] = [["Sponsors concurrents détectés (col T)"]]
    formulas["H75"] = [["Marque", "Nb ambassadeurs"]]
    competitors = ["Ta.energy", "Nutripure", "CookNRUN", "Mule Bar", "Isostar", "Maurten"]
    for i, comp in enumerate(competitors):
        row = 76 + i
        formulas[f"H{row}"] = [[comp, f'=COUNTIF({DATA_SHEET}!$T:$T;"*{comp}*")']]

    # ─── Section 9: Sport distribution (row 83-92, col H-I) ───
    formulas["H83"] = [["Distribution sports (col S)"]]
    formulas["H84"] = [["Sport", "Nb"]]
    sports = ["Course à pied", "Trail", "Hyrox", "Cyclisme", "Musculation", "Triathlon", "Fitness", "CrossFit"]
    for i, sport in enumerate(sports):
        row = 85 + i
        formulas[f"H{row}"] = [[sport, f'=COUNTIF({DATA_SHEET}!$S:$S;"*{sport}*")']]

    return formulas


def main():
    parser = argparse.ArgumentParser(description="Refresh Analyses formulas")
    parser.add_argument("--dry-run", action="store_true", help="Print formulas without writing")
    args = parser.parse_args()

    formulas = build_formulas()

    if args.dry_run:
        print("Formulas to write:")
        for range_str, data in sorted(formulas.items()):
            print(f"  {range_str}: {data}")
        return

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("ERROR: gspread not installed.")
        sys.exit(1)

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "/Users/antoinechabrat/.config/google-service-account.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)

    print(f"Writing {len(formulas)} formula blocks to {SHEET_NAME}...")
    for range_str, data in formulas.items():
        ws.update(range_str, data, value_input_option="USER_ENTERED")

    print("Done! Analyses sheet updated with formulas.")


if __name__ == "__main__":
    main()
