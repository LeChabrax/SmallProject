"""
Qualification des conversations avant envoi promo -20%

Pour chaque compte, récupère les derniers messages et analyse :
- Si dernier msg = nous → OK
- Si dernier msg = influenceur + question/attente de réponse → FLAG
- Si dernier msg = influenceur + accusé de réception neutre ("ok", "merci", etc.) → OK

Usage :
    python qualify_conversations.py [--limit N]  # N comptes max (défaut = tous)
    python qualify_conversations.py --limit 10   # premier batch de 10
"""

import time
import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME", "impulse_nutrition_fr")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = Path(__file__).parent.parent.parent / "data" / "sessions" / f"{USERNAME}_session.json"

QUALIFY_RESULTS_FILE = Path(__file__).parent.parent.parent / "qualify_results.json"
DELAY = 2  # secondes entre comptes (lecture seule)

# Allow `from infra.common.*` imports (infra/common at repo root via sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from infra.common.dm_classifier import classify_last_message, QUESTION_SIGNALS, OK_SIGNALS  # noqa: E402


# ──────────────────────────────────────────
# Liste complète des comptes (ordre spreadsheet R291→R413)
# Format : (username, prenom, row_sheet, action_colF)
# Les SKIP sont inclus pour le mapping row mais marqués skip=True
# ──────────────────────────────────────────
ALL_ACCOUNTS_ORDERED = [
    # Row 291-321 : demander avis produits
    ("cecile_altara",          "Cécile",    291, "demander avis produits", False),
    ("manon.dupont",           "Manon",     292, "demander avis produits", False),
    ("_noemie.blgr_",          "Noémie",    293, "demander avis produits", False),
    ("antoineclmtt",           "Antoine",   294, "demander avis produits", False),
    ("aymericfondo",           "Aymeric",   295, "demander avis produits", False),
    ("bao_antruong",           "Bao",       296, "demander avis produits", False),
    ("cam.kl__",               "Camille",   297, "demander avis produits", False),
    ("chloe.dthr",             "Chloé",     298, "demander avis produits", False),
    ("elsa_jacobbad",          "Elsa",      299, "demander avis produits", False),
    ("emma.martineau",         "Emma",      300, "demander avis produits", False),
    ("emmapetithuguenin",      "Emma",      301, "demander avis produits", False),
    ("fit.sharon",             "Sharon",    302, "demander avis produits", False),
    ("justine__bvr",           "Justine",   303, "demander avis produits", False),
    ("lapuertaontheroad",      "Alex",      304, "demander avis produits", False),
    ("luciehorpin",            "Lucie",     305, "demander avis produits", False),
    ("manons.fit",             "Manon",     306, "demander avis produits", False),
    ("mapageblanche_",         "Delphée",   307, "demander avis produits", False),
    ("melissa_on_the_run",     "Melissa",   308, "demander avis produits", False),
    ("melmrt__",               "Mélanie",   309, "demander avis produits", False),
    ("muntagnolu_corsu",       "Alexandre", 310, "demander avis produits", False),
    ("ninho_run_yoga",         "Ninho",     311, "demander avis produits", False),
    ("petit_gouter",           "Maud",      312, "demander avis produits", False),
    ("pinau_steve_",           "Steve",     313, "demander avis produits", False),
    ("ribesquitterie",         "",          314, "demander avis produits", False),
    ("romane_blucheau",        "Romane",    315, "demander avis produits", False),
    ("runnewiam",              "Maï",       316, "demander avis produits", False),
    ("teo_libretti",           "Téo",       317, "demander avis produits", False),
    ("tery.bray",              "Tery",      318, "demander avis produits", False),
    ("valentin_runner",        "Valentin",  319, "demander avis produits", False),
    ("violaine.and",           "Violaine",  320, "demander avis produits", False),
    ("une_petitebbrune",       "Mylène",    321, "demander avis produits", False),
    # Row 322 : SKIP (introuvable)
    ("melissa_biarritz",       "Melissa",   322, "introuvable",            True),
    # Row 323-409 : RAS
    ("justine.rouux",          "Justine",   323, "RAS",                    False),
    ("meloeecms",              "",          324, "RAS",                    False),
    ("meluulv",                "Meluv",     325, "RAS",                    False),
    ("clohtdz",                "Cloé",      326, "RAS",                    False),
    ("_adeloise",              "Adéloïse",  327, "RAS",                    False),
    ("_marie_adam_",           "Marie",     328, "RAS",                    False),
    ("agatouvv",               "Agathe",    329, "RAS",                    False),
    ("alicemauguin",           "Alice",     330, "RAS",                    False),
    ("allanrkt99",             "Allan",     331, "RAS",                    False),
    ("amaiasblt",              "Amaia",     332, "RAS",                    False),
    ("andonimgrt",             "Andoni",    333, "RAS",                    False),
    ("anixlml",                "Anissa",    334, "RAS",                    False),
    ("athena_fred__",          "Athéna et Fred", 335, "RAS",               False),
    ("banou_coach",            "Albane",    336, "RAS",                    False),
    ("bourasmarine",           "Marine",    337, "RAS",                    False),
    ("c_claclou",              "Clara",     338, "RAS",                    False),
    ("cam.leleu",              "Camille",   339, "RAS",                    False),
    ("cedric.dnj",             "Cédric",    340, "RAS",                    False),
    ("chlo.gt",                "Chloé",     341, "RAS",                    False),
    ("coachju76",              "Julien",    342, "RAS",                    False),
    ("corentinfolliot",        "Corentin",  343, "RAS",                    False),
    ("daniel__violette",       "Daniel",    344, "RAS",                    False),
    ("dedelfitfun",            "Delphine",  345, "RAS",                    False),
    ("del_margaux",            "Margaux",   346, "RAS",                    False),
    ("djebryn",                "Djebryn",   347, "RAS",                    False),
    ("eli_fun_run",            "Elisabeth", 348, "RAS",                    False),
    ("emi.mama_run",           "Emilie",    349, "RAS",                    False),
    ("emilie.brd05",           "Emilie",    350, "RAS",                    False),
    ("emma_scbr",              "Emma",      351, "RAS",                    False),
    ("en_haut_cest_plus_beau", "Yannick",   352, "RAS",                    False),
    ("estef_en_course",        "Estef",     353, "RAS",                    False),
    ("esther_denisart",        "Esther",    354, "RAS",                    False),
    ("fitbychaton",            "Charlotte", 355, "RAS",                    False),
    ("floriansrvs",            "Florian",   356, "RAS",                    False),
    ("flow___coaching",        "",          357, "RAS",                    False),
    ("gaetanpetit__",          "Gaetan",    358, "RAS",                    False),
    ("gwendal_tpm",            "Gwendal",   359, "RAS",                    False),
    ("gwladyslarzul",          "Gwladys",   360, "RAS",                    False),
    ("hugomlt.fit",            "Hugo",      361, "RAS",                    False),
    ("hugorun_",               "Hugo",      362, "RAS",                    False),
    ("jessica_luisa_sl",       "Jessica",   363, "RAS",                    False),
    ("jessicadtrn",            "Jessica",   364, "RAS",                    False),
    ("ju_fitrun",              "Julie",     365, "RAS",                    False),
    ("justealextv",            "Alexandre", 366, "RAS",                    False),
    ("justine_fulla",          "Justine",   367, "RAS",                    False),
    ("justine.lemr",           "Justine",   368, "RAS",                    False),
    ("juuullyy",               "Juju",      369, "RAS",                    False),
    ("kalista_cruz",           "Kalista",   370, "RAS",                    False),
    ("kleden_fvc",             "Kleden",    371, "RAS",                    False),
    ("laetimou_",              "Laëtitia",  372, "RAS",                    False),
    ("laupapn",                "Laura",     373, "RAS",                    False),
    ("laurine__br",            "Laurine",   374, "RAS",                    False),
    ("leabyn_",                "Léa",       375, "RAS",                    False),
    ("lolaa_fitt",             "Lola",      376, "RAS",                    False),
    ("louanneguiton",          "Lou-Anne",  377, "RAS",                    False),
    ("lucierose76",            "Lucie",     378, "RAS",                    False),
    ("ludovico_coach",         "Ludovico",  379, "RAS",                    False),
    ("lydie_rld",              "Lydie",     380, "RAS",                    False),
    ("maelys_cassan",          "Maëlys",    381, "RAS",                    False),
    ("manalohaa",              "Manon",     382, "RAS",                    False),
    ("margaux_running",        "Margaux",   383, "RAS",                    False),
    ("marierouviere",          "Marie",     384, "RAS",                    False),
    ("marion.petitpas",        "Marion",    385, "RAS",                    False),
    ("martin_desmidt",         "Martin",    386, "RAS",                    False),
    ("marylamalice",           "Marianne",  387, "RAS",                    False),
    ("matbriere",              "Mathilde",  388, "RAS",                    False),
    ("max_sola",               "Max",       389, "RAS",                    False),
    ("maya_dsft",              "Maya",      390, "RAS",                    False),
    ("melanie_lucas_coaching", "Mélanie",   391, "RAS",                    False),
    ("movewithclo",            "Chloé",     392, "RAS",                    False),
    ("nadiarunsparis",         "Nadia",     393, "RAS",                    False),
    ("nate_lgll",              "Nathan",    394, "RAS",                    False),
    # Row 395 : nicepositive — déjà envoyé (-20% check)
    ("nicepositive",           "Thomas",    395, "-20% check",             True),
    ("oceanezaepfeloff",       "Océane",    396, "RAS",                    False),
    ("paul_chardin",           "Paul",      397, "RAS",                    False),
    ("pauline.65",             "Pauline",   398, "RAS",                    False),
    ("paulineminguy",          "Pauline",   399, "RAS",                    False),
    ("robin.coach_trail_running", "Robin",  400, "RAS",                    False),
    ("running_withmathy",      "Mathilde",  401, "RAS",                    False),
    ("runzoe_",                "Zoé",       402, "RAS",                    False),
    ("samcupping8",            "Sam",       403, "RAS",                    False),
    ("sandrahuon",             "Sandra",    404, "RAS",                    False),
    ("siana_life_",            "Anaïs",     405, "RAS",                    False),
    ("sonny_dcf_",             "Sonny",     406, "RAS",                    False),
    ("une.patissiere.sportive","Christine", 407, "RAS",                    False),
    ("vinc.efit",              "Vincent",   408, "RAS",                    False),
    ("yocorun7z",              "Yoann",     409, "RAS",                    False),
    # Row 410-412 : SKIP
    ("alexx_adamo",            "Alex",      410, "répondre au message",    True),
    ("_williamroth",           "William",   411, "répondre au message",    True),
    ("antoinepmr",             "Antoine",   412, "répondre au message",    True),
    # Row 413 : SEND malgré répondre au message
    ("candiice_and_running",   "Candice",   413, "répondre au message",    False),
]

# Comptes déjà traités / envoyés
ALREADY_DONE = {"cecile_altara"}


def load_results() -> dict:
    if QUALIFY_RESULTS_FILE.exists():
        with open(QUALIFY_RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_results(results: dict):
    with open(QUALIFY_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def ts():
    return datetime.now().strftime("%H:%M:%S")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Nombre de comptes à traiter")
    args = parser.parse_args()

    # Connexion
    client = Client()
    if SESSION_FILE.exists():
        client.load_settings(SESSION_FILE)
    client.login(USERNAME, PASSWORD)
    client.dump_settings(SESSION_FILE)
    our_user_id = str(client.user_id)
    print(f"[{ts()}] Connecté en tant que {USERNAME} (id={our_user_id})")

    # Charger résultats existants
    results = load_results()

    # Filtrer : comptes à qualifier (ni SKIP, ni déjà done, ni cecile_altara)
    candidates = [
        (u, p, row, col_f)
        for (u, p, row, col_f, skip) in ALL_ACCOUNTS_ORDERED
        if not skip and u not in ALREADY_DONE
    ]

    if args.limit:
        # Exclure ceux déjà qualifiés dans les runs précédents
        remaining = [c for c in candidates if c[0] not in results]
        batch = remaining[:args.limit]
    else:
        batch = [c for c in candidates if c[0] not in results]

    print(f"[{ts()}] Comptes à qualifier dans ce batch : {len(batch)}")
    print()

    send_list = []
    flag_list = []
    review_list = []

    for i, (username, prenom, row, col_f) in enumerate(batch, start=1):
        print(f"[{ts()}] [{i}/{len(batch)}] @{username} (row {row})")

        try:
            user_id = client.user_id_from_username(username)
            thread = client.direct_thread_by_participants([int(user_id)])
            # direct_thread_by_participants renvoie un dict ou un objet DirectThread
            if isinstance(thread, dict):
                # Structure: {"thread": {"thread_id": "...", ...}, "status": ...}
                inner = thread.get("thread") or {}
                thread_id = inner.get("thread_id") or inner.get("id") or thread.get("id")
            else:
                thread_id = getattr(thread, "id", None) or getattr(thread, "thread_id", None)
            if not thread_id:
                raise ValueError("Thread ID introuvable dans la réponse")
            messages = client.direct_messages(str(thread_id), 5)

            if not messages:
                print(f"  → Aucun message dans le thread")
                status = "no_thread"
                last_text = ""
                last_sender = ""
            else:
                last_msg = messages[0]
                last_sender_id = str(getattr(last_msg, 'user_id', ''))
                is_from_us = (last_sender_id == our_user_id)
                last_text = getattr(last_msg, 'text', '') or ""
                last_sender = "nous" if is_from_us else "influenceur"
                item_type = str(getattr(last_msg, 'item_type', '') or "")

                # Mentions story / reactions automatiques IG → pas besoin de reply
                NON_REPLY_TYPES = {"xma_reel_mention", "xma_story_share", "action_log",
                                   "reel_share", "story_share", "like", "reaction"}
                if not is_from_us and item_type in NON_REPLY_TYPES:
                    status = "send"
                    last_text = f"[{item_type}]"
                else:
                    status = classify_last_message(last_text, is_from_us)

                preview = last_text[:80].replace("\n", " ")
                marker = "✅" if status == "send" else ("⚠️ FLAG" if status == "flag" else "🔍 REVIEW")
                print(f"  Dernier msg ({last_sender}) : \"{preview}\"")
                print(f"  → {marker}")

        except Exception as e:
            print(f"  ✗ Erreur : {e}")
            status = "error"
            last_text = ""
            last_sender = ""

        results[username] = {
            "username": username,
            "prenom": prenom,
            "row": row,
            "col_f_original": col_f,
            "status": status,
            "last_sender": last_sender,
            "last_text_preview": last_text[:120],
        }
        save_results(results)

        if status == "send":
            send_list.append(username)
        elif status == "flag":
            flag_list.append(username)
        elif status == "review":
            review_list.append(username)

        if i < len(batch):
            time.sleep(DELAY)

    # Résumé
    print()
    print("=" * 60)
    print(f"RÉSUMÉ BATCH ({len(batch)} comptes)")
    print(f"  ✅ SEND   ({len(send_list)}) : {', '.join(send_list) or '-'}")
    print(f"  ⚠️  FLAG   ({len(flag_list)}) : {', '.join(flag_list) or '-'}")
    print(f"  🔍 REVIEW ({len(review_list)}) : {', '.join(review_list) or '-'}")
    print(f"Résultats sauvegardés : {QUALIFY_RESULTS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
