"""
build_master.py — Rebuild benchmark/master_data.json from per-brand sources.

Source de vérité = benchmark/marques/<brand>/data.json (structure alignée
sur le brief mission). Ce script agrège les 8 marques + _transversal.json
et régénère master_data.json dans son format historique pour que les
consommateurs existants (generate_html_report.py, generate_deck_v2.py)
continuent à tourner sans refacto.

Usage :
    python3 benchmark/build_master.py

Ne pas éditer master_data.json à la main.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARQUES = ROOT / "marques"
TRANSVERSAL = MARQUES / "_transversal.json"
OUT = ROOT / "master_data.json"

# Ordre des marques dans master_data.json
BRAND_ORDER = [
    "nutriandco",
    "nutrimuscle",
    "novoma",
    "nutripure",
    "cuure",
    "decathlon",
    "aqeelab",
    "myprotein",
]


def brand_to_legacy(data: dict) -> dict:
    """Transforme la structure brief mission → structure plate historique."""
    mc = data.get("modele_commercial", {}) or {}
    pp = data.get("perimetre_produit", {}) or {}
    uxp = data.get("ux_page_produit", {}) or {}
    ev = data.get("evaluation", {}) or {}
    flex = mc.get("flexibility", {}) or {}
    extras = data.get("_extras", {}) or {}

    flex_out = {
        "pause": flex.get("pause"),
        "modify": flex.get("modify"),
        "cancel_anytime": flex.get("cancel_anytime"),
        "minimum_commitment": mc.get("engagement_min"),
    }
    # Fusion des extras flexibility (ex: modify_note)
    for k, v in (extras.get("flexibility") or {}).items():
        flex_out.setdefault(k, v)

    catalogue = {
        "name": data.get("brand"),
        "url": data.get("url"),
        "has_subscription": data.get("has_subscription", False),
        "subscription_discount_pct": mc.get("remise_pct"),
        "subscription_model": mc.get("remise_note"),
        "frequencies_available": mc.get("frequencies", []),
        "flexibility": flex_out,
        "products": pp.get("produits_sample", []),
        "subscription_scope": pp.get("scope"),
        "estimated_avg_basket_sub": pp.get("ticket_moyen_estime_eur"),
        # Nouveau champ (pas présent dans le master historique, ajouté pour le brief mission)
        "subscription_shipping": mc.get("livraison_abo", {}),
    }
    # On conserve subscription_exclusions uniquement si non vide (évite de polluer
    # le diff vs master historique qui ne contenait pas ce champ chez beaucoup de marques).
    if pp.get("exclusions"):
        catalogue["subscription_exclusions"] = pp["exclusions"]
    # Fusion des extras catalogue (note, unique_selling_point, loyalty_program, etc.)
    for k, v in (extras.get("catalogue") or {}).items():
        catalogue.setdefault(k, v)

    subscription_ux = {
        "wording_cta": uxp.get("wording_cta"),
        "wording_pitch": uxp.get("wording_pitch"),
        "placement_on_product_page": uxp.get("placement_module"),
        "toggle_style": uxp.get("toggle_style"),
        "frequency_selector": uxp.get("frequency_selector"),
        "price_display": uxp.get("price_display"),
        "dedicated_page": uxp.get("dedicated_page"),
        "homepage_mention": uxp.get("homepage_mention"),
        "navigation_mention": uxp.get("navigation_mention"),
        "email_mention": uxp.get("email_mention"),
    }
    # Fusion des extras subscription_ux (savings_display, onboarding_flow, etc.)
    for k, v in (extras.get("subscription_ux") or {}).items():
        subscription_ux.setdefault(k, v)

    ux_deep = {
        "screenshots": uxp.get("screenshots_files", []),
        "subscription_ux": subscription_ux,
        "overall_ux_score": ev.get("score_ux"),
        "strengths": ev.get("strengths", []),
        "weaknesses": ev.get("weaknesses", []),
    }
    # Fusion des extras ux_deep (ex. app_mobile, loyalty_program, dedicated_page_url)
    for k, v in (extras.get("ux_deep") or {}).items():
        ux_deep.setdefault(k, v)
    # Scores du brief mission préservés en plus (non-destructif)
    ux_deep["scores"] = {
        "ux": ev.get("score_ux"),
        "offre_commerciale": ev.get("score_offre_commerciale"),
        "pertinence_vs_impulse": ev.get("score_pertinence_vs_impulse"),
        "global": ev.get("score_global"),
    }

    return {
        "catalogue": catalogue,
        "logistique": data.get("logistique", {}),
        "tech": data.get("tech", {}),
        "avis": data.get("avis", {}),
        "ux_deep": ux_deep,
    }


def main() -> None:
    if not TRANSVERSAL.exists():
        raise SystemExit(f"Missing {TRANSVERSAL}. Run split_master_to_brands.py first.")

    transversal_blob = json.loads(TRANSVERSAL.read_text(encoding="utf-8"))

    meta = dict(transversal_blob.get("meta", {}))
    meta["last_updated"] = str(date.today())
    meta["source_of_truth"] = "benchmark/marques/<brand>/data.json"
    meta["generator"] = "benchmark/build_master.py"

    brands = {}
    audit_statuses = {}
    for slug in BRAND_ORDER:
        brand_path = MARQUES / slug / "data.json"
        if not brand_path.exists():
            raise SystemExit(f"Missing {brand_path}")
        data = json.loads(brand_path.read_text(encoding="utf-8"))
        brands[slug] = brand_to_legacy(data)
        audit_statuses[slug] = data.get("_meta", {}).get("audit_status", "raw")

    meta["audit_statuses"] = audit_statuses

    master = {
        "meta": meta,
        "brands": brands,
        "transversal": transversal_blob.get("transversal", {}),
        "comparative": transversal_blob.get("comparative", {}),
    }

    OUT.write_text(
        json.dumps(master, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[ok] {OUT.relative_to(ROOT.parent)} rebuilt from {len(brands)} brands")
    verified = sum(1 for s in audit_statuses.values() if s == "verified_live")
    print(f"     audit: {verified}/{len(brands)} verified_live, {len(brands) - verified} raw")


if __name__ == "__main__":
    main()
