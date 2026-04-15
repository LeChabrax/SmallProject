"""
split_master_to_brands.py — one-shot migration.

Lit benchmark/master_data.json et éclate la data en dossiers par marque
alignés sur la structure EXACTE du brief mission (modele_commercial,
perimetre_produit, ux_page_produit, evaluation) pour que la génération
du deck soit directe.

Crée :
  benchmark/marques/<brand>/
    ├── data.json       # source de vérité par marque
    ├── notes.md        # verbatims, vérifs live, décisions
    ├── sources.md      # URLs citées avec date + phrase extraite
    └── screenshots/    # dossier vide, screenshots déplacés par git mv

Ainsi que :
  benchmark/marques/_transversal.json   # transversal + comparative + meta
                                          du master (non spécifique à une marque)

Ne touche pas à master_data.json — on le régénère ensuite via build_master.py.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Source par défaut = backup (l'original, jamais touché par build_master).
# Permet de rerun le split sans pollution des champs ajoutés par le round-trip.
MASTER_BACKUP = ROOT / "master_data.json.backup"
MASTER_CURRENT = ROOT / "master_data.json"
OUT = ROOT / "marques"

# Mapping slug dossier → display name pour notes.md / sources.md uniquement
# (le "brand" dans data.json provient du master d'origine pour fidélité).
BRAND_DISPLAY = {
    "nutriandco": "Nutri&Co",
    "nutrimuscle": "Nutrimuscle",
    "novoma": "Novoma",
    "nutripure": "Nutripure",
    "cuure": "Cuure",
    "decathlon": "Decathlon",
    "aqeelab": "Aqeelab",
    "myprotein": "MyProtein",
}


# Champs du master_data.catalogue qui sont mappés dans le schéma canonique.
# Les autres champs (note, unique_selling_point, loyalty_program, etc.) sont
# capturés dans `_extras.catalogue` pour préserver 100% de l'information.
CATALOGUE_MAPPED = {
    "name", "url", "has_subscription",
    "subscription_discount_pct", "subscription_model",
    "frequencies_available", "flexibility",
    "products", "subscription_scope", "subscription_exclusions",
    "estimated_avg_basket_sub",
}

# Pareil pour ux_deep.
UX_DEEP_MAPPED = {"screenshots", "subscription_ux", "overall_ux_score", "strengths", "weaknesses"}

# Pareil pour ux_deep.subscription_ux.
SUB_UX_MAPPED = {
    "wording_cta", "wording_pitch", "placement_on_product_page", "toggle_style",
    "frequency_selector", "price_display", "dedicated_page",
    "homepage_mention", "navigation_mention", "email_mention",
}

# Pareil pour catalogue.flexibility.
FLEX_MAPPED = {"pause", "modify", "cancel_anytime", "minimum_commitment"}


def extract_extras(source: dict, mapped_keys: set) -> dict:
    """Retourne tous les champs de `source` qui ne sont pas dans `mapped_keys`."""
    return {k: v for k, v in (source or {}).items() if k not in mapped_keys}


def transform_brand(slug: str, brand_data: dict) -> dict:
    """Transforme la structure plate master_data → structure brief mission."""
    cat = brand_data.get("catalogue", {}) or {}
    ux = brand_data.get("ux_deep", {}) or {}
    sub_ux = ux.get("subscription_ux", {}) or {}

    flex = cat.get("flexibility", {}) or {}

    extras = {
        "catalogue": extract_extras(cat, CATALOGUE_MAPPED),
        "ux_deep": extract_extras(ux, UX_DEEP_MAPPED),
        "subscription_ux": extract_extras(sub_ux, SUB_UX_MAPPED),
        "flexibility": extract_extras(flex, FLEX_MAPPED),
    }

    return {
        # Le nom officiel du catalogue prime (ex: "Aqeelab Nutrition", "Decathlon (Abonnement Nutrition)")
        # pour rester fidèle à master_data. BRAND_DISPLAY ne sert que pour l'affichage notes/sources.
        "brand": cat.get("name") or BRAND_DISPLAY.get(slug, slug),
        "slug": slug,
        "url": cat.get("url"),
        "has_subscription": cat.get("has_subscription", False),

        "modele_commercial": {
            "remise_pct": cat.get("subscription_discount_pct"),
            "remise_note": cat.get("subscription_model"),
            "frequencies": cat.get("frequencies_available", []),
            "flexibility": {
                "pause": flex.get("pause"),
                "modify": flex.get("modify"),
                "cancel_anytime": flex.get("cancel_anytime"),
            },
            "engagement_min": flex.get("minimum_commitment"),
            # Nouveau champ — non présent dans master_data, à remplir via vérif live
            "livraison_abo": {
                "offerte": None,
                "seuil_eur": None,
                "note": None,
            },
        },

        "perimetre_produit": {
            "scope": cat.get("subscription_scope"),
            "exclusions": cat.get("subscription_exclusions", []),
            "produits_sample": cat.get("products", []),
            "ticket_moyen_estime_eur": cat.get("estimated_avg_basket_sub"),
        },

        "ux_page_produit": {
            "wording_cta": sub_ux.get("wording_cta"),
            "wording_pitch": sub_ux.get("wording_pitch"),
            "placement_module": sub_ux.get("placement_on_product_page"),
            "toggle_style": sub_ux.get("toggle_style"),
            "frequency_selector": sub_ux.get("frequency_selector"),
            "price_display": sub_ux.get("price_display"),
            "dedicated_page": sub_ux.get("dedicated_page"),
            "homepage_mention": sub_ux.get("homepage_mention"),
            "navigation_mention": sub_ux.get("navigation_mention"),
            "email_mention": sub_ux.get("email_mention"),
            "screenshots_files": ux.get("screenshots", []),
        },

        "evaluation": {
            "strengths": ux.get("strengths", []),
            "weaknesses": ux.get("weaknesses", []),
            "score_ux": ux.get("overall_ux_score"),
            "score_offre_commerciale": None,
            "score_pertinence_vs_impulse": None,
            "score_global": None,
            "note": "Scores offre/pertinence/global à arbitrer en fin de revue pour calibrage homogène",
        },

        # Rubriques préservées tel quel (pas demandées par le brief mais utiles)
        "logistique": brand_data.get("logistique", {}),
        "tech": brand_data.get("tech", {}),
        "avis": brand_data.get("avis", {}),

        # Bucket lossless : tout ce qui n'est pas dans le schéma canonique est préservé ici.
        # Réinjecté dans master_data.json par build_master.py.
        "_extras": extras,

        "_meta": {
            "last_updated": str(date.today()),
            "audit_status": "raw",  # raw | needs_review | verified_live
            "source_format": "split from master_data.json",
        },
    }


NOTES_TEMPLATE = """# {brand} — notes de revue

## Statut audit
- Audit status : `raw` (pas encore vérifié en live)

## Vérifs live
_À remplir au fil de la revue._

## Décisions / corrections
_À remplir au fil de la revue._

## Questions ouvertes
- Notes /5 (UX, offre commerciale, pertinence, globale) — à trancher en fin de revue des 8 marques pour calibrage homogène
"""

SOURCES_TEMPLATE = """# {brand} — sources consultées

_Format : `- [YYYY-MM-DD] URL — phrase extraite entre guillemets`_

## FAQ / pages officielles
_À remplir au fil de la revue._

## Verbatims / avis
_À remplir au fil de la revue._
"""


def main() -> None:
    # Priorité au backup (source d'origine) pour garantir l'idempotence même
    # après plusieurs round-trips split ↔ build.
    source = MASTER_BACKUP if MASTER_BACKUP.exists() else MASTER_CURRENT
    print(f"  source: {source.relative_to(ROOT)}")
    master = json.loads(source.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)

    for slug, brand_data in master["brands"].items():
        brand_dir = OUT / slug
        brand_dir.mkdir(exist_ok=True)
        (brand_dir / "screenshots").mkdir(exist_ok=True)

        data_path = brand_dir / "data.json"

        # Idempotence : on ne touche pas aux marques déjà verifiées en live
        # (sinon on écraserait les corrections manuelles de la revue).
        if data_path.exists():
            existing = json.loads(data_path.read_text(encoding="utf-8"))
            if existing.get("_meta", {}).get("audit_status") in ("verified_live", "needs_review"):
                print(f"  [skip] {slug} (audit_status={existing['_meta']['audit_status']})")
                continue

        data = transform_brand(slug, brand_data)
        data_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        display = BRAND_DISPLAY.get(slug, slug)
        notes_path = brand_dir / "notes.md"
        if not notes_path.exists():
            notes_path.write_text(NOTES_TEMPLATE.format(brand=display), encoding="utf-8")
        sources_path = brand_dir / "sources.md"
        if not sources_path.exists():
            sources_path.write_text(SOURCES_TEMPLATE.format(brand=display), encoding="utf-8")

        print(f"  [ok] {slug} → {brand_dir.relative_to(ROOT)}")

    # Bloc transversal : tout ce qui n'est pas par marque
    transversal_blob = {
        "_note": "Généré par split_master_to_brands.py. Réinjecté dans master_data.json par build_master.py.",
        "meta": master.get("meta", {}),
        "transversal": master.get("transversal", {}),
        "comparative": master.get("comparative", {}),
    }
    (OUT / "_transversal.json").write_text(
        json.dumps(transversal_blob, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"  [ok] transversal → {(OUT / '_transversal.json').relative_to(ROOT)}")

    print(f"\nSplit terminé : {len(master['brands'])} marques écrites dans {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
