"""Génère les 8 slides marques HTML et les injecte dans deck.html
avant le commentaire <!-- INSERT_BRAND_SLIDES_HERE -->.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARQUES = ROOT / "marques"
DECK = Path(__file__).resolve().parent / "deck.html"

BRAND_ORDER = ["aqeelab", "nutriandco", "nutrimuscle", "novoma", "cuure", "myprotein", "decathlon", "nutripure"]

BRAND_SCREENSHOT = {
    "nutriandco": "abonnement_page.png",
    "nutrimuscle": "abonnement_page.png",
    "novoma": "abonnement_page.png",
    "nutripure": "homepage.png",
    "cuure": "produits.png",
    "decathlon": "homepage.png",
    "aqeelab": "product_sub.png",
    "myprotein": "product_sub.png",
}

# 1-liner verdict par marque — le "pitch" que le comité retient
BRAND_VERDICT = {
    "aqeelab": "<strong>Le plus agressif du panel</strong> · −20% flat à vie · seul pb = engagement 2 mois",
    "nutriandco": "<strong>La référence proche d'Impulse</strong> · −15% + email anti-churn 48h · module trop discret",
    "nutrimuscle": "<strong>La visibilité maximale</strong> · 6 fréquences + mention home/nav/newsletter",
    "novoma": "<strong>Le modèle prudent</strong> · −10% + livraison stepped · argument santé long terme",
    "cuure": "<strong>Le modèle 100% abo</strong> · quiz santé + box personnalisée · résiliation 2 temps anti-pattern",
    "myprotein": "<strong>Le volume international</strong> · jusqu'à −45% mais remise illisible sur prix volatils",
    "decathlon": "<strong>Le contre-modèle UX</strong> · sous-domaine séparé + '1 produit = 1 abo'",
    "nutripure": "<strong>Sans abonnement</strong> · mise sur packs permanents et fidélité plutôt que lock-in",
}

# Annotations CSS overlay par marque : positions approximatives (% sur le screenshot)
BRAND_ANNOTATIONS = {
    "aqeelab": [
        ("34%", "24%", "Toggle abo au-dessus du CTA"),
        ("34%", "48%", "Montant économisé en €"),
    ],
    "nutriandco": [
        ("20%", "30%", "Page dédiée /pages/abonnement"),
        ("60%", "55%", "Grid produits éligibles"),
    ],
    "nutrimuscle": [
        ("15%", "20%", "Pitch '−15% + livraison offerte'"),
        ("50%", "50%", "Processus 3 étapes"),
    ],
    "novoma": [
        ("20%", "22%", "Argumentation santé long terme"),
        ("55%", "48%", "Avantages chiffrés"),
    ],
    "cuure": [
        ("30%", "30%", "Quiz santé ~5 min"),
        ("50%", "55%", "Box 100% personnalisée"),
    ],
    "myprotein": [
        ("25%", "25%", "Badge remise variable"),
        ("55%", "48%", "Toggle abo"),
    ],
    "decathlon": [
        ("20%", "25%", "Sous-domaine dédié séparé"),
        ("55%", "50%", "Processus 4 étapes"),
    ],
    "nutripure": [
        ("25%", "28%", "Aucun module abo"),
        ("60%", "45%", "Packs multi-mois à la place"),
    ],
}


def fmt_remise(mc):
    pct = mc.get("remise_pct")
    if pct is None:
        return "—"
    if isinstance(pct, (int, float)):
        return f"−{pct}%"
    s = str(pct)
    return s[:22]


def fmt_livraison(mc):
    liv = mc.get("livraison_abo", {}) or {}
    if liv.get("offerte") is True and liv.get("seuil_eur") == 0:
        return "Offerte sans seuil"
    if liv.get("offerte") == "relais uniquement":
        return "Relais uniquement"
    if liv.get("offerte") is True and liv.get("seuil_eur"):
        return f"Offerte dès {liv['seuil_eur']}€"
    if liv.get("offerte") is False:
        return f"Stepped dès {liv.get('seuil_eur', '?')}€"
    return "N/A"


def fmt_engagement(mc):
    eng = mc.get("engagement_min", "") or ""
    if "Aucun" in eng or eng == "":
        return "Aucun"
    if "2 mois" in eng:
        return "2 mois min"
    if "partiel" in eng.lower() or "friction" in eng.lower():
        return "Friction"
    return eng[:16]


def fmt_flexibility(mc):
    flex = mc.get("flexibility", {}) or {}
    parts = []
    if flex.get("pause"):
        parts.append("Pause")
    if flex.get("modify"):
        parts.append("Modif")
    if flex.get("cancel_anytime"):
        parts.append("Annul.")
    return " / ".join(parts) if parts else "N/A"


def fmt_frequencies(mc):
    freqs = mc.get("frequencies", [])
    if not freqs:
        return "—"
    return " / ".join(str(f) for f in freqs)


def fmt_freq_tags(mc):
    freqs = mc.get("frequencies", [])
    if not freqs:
        return "—"
    return " ".join(f'<span class="brand__tag brand__tag--freq">{f}</span>' for f in freqs)


def fmt_flex_tags(mc):
    flex = mc.get("flexibility", {}) or {}
    tags = []
    if flex.get("pause"):
        tags.append('<span class="brand__tag brand__tag--yes">Pause</span>')
    if flex.get("modify"):
        tags.append('<span class="brand__tag brand__tag--yes">Modif</span>')
    if flex.get("cancel_anytime"):
        tags.append('<span class="brand__tag brand__tag--yes">Annul.</span>')
    return " ".join(tags) if tags else '<span class="brand__tag brand__tag--no">N/A</span>'


def _yn_tag(val):
    if val:
        return '<span class="brand__tag brand__tag--yes">Oui</span>'
    return '<span class="brand__tag brand__tag--no">Non</span>'


def _presence_tags(ux):
    items = [
        ("Page", ux.get("dedicated_page")),
        ("Home", ux.get("homepage_mention")),
        ("Nav", ux.get("navigation_mention")),
    ]
    return " ".join(
        f'<span class="brand__tag brand__tag--{"yes" if v else "no"}">{label}</span>'
        for label, v in items
    )


def score_class(score):
    if score is None:
        return "brand__score--na"
    if score >= 4.0:
        return "brand__score--hi"
    if score >= 3.0:
        return "brand__score--mid"
    return "brand__score--lo"


def render_score(score):
    if score is None:
        return '<div class="brand__score-value">—</div>'
    return f'<div class="brand__score-value">{score}<span class="unit"> /5</span></div>'


def render_brand_slide(idx, slug, data, total=21):
    mc = data.get("modele_commercial", {}) or {}
    pp = data.get("perimetre_produit", {}) or {}
    ev = data.get("evaluation", {}) or {}
    ux = data.get("ux_page_produit", {}) or {}
    avis = data.get("avis", {}) or {}
    has_sub = data.get("has_subscription", False)

    brand_name = data.get("brand", slug)
    url = data.get("url", "")
    remise = fmt_remise(mc)
    freqs = mc.get("frequencies", [])
    freq_count = len(freqs) if freqs else 0
    ticket = pp.get("ticket_moyen_estime_eur")
    liv = fmt_livraison(mc)
    eng = fmt_engagement(mc)
    strengths = ev.get("strengths", [])
    weaknesses = ev.get("weaknesses", [])
    global_score = ev.get("score_global")
    trust_score = avis.get("trustpilot_score")
    trust_n = avis.get("trustpilot_nb_avis")
    if trust_n and trust_n >= 1000:
        trust_n_label = f"{trust_n / 1000:.1f}k"
    else:
        trust_n_label = str(trust_n) if trust_n else "—"

    screenshot_file = BRAND_SCREENSHOT[slug]
    screenshot_path = f"../../marques/{slug}/screenshots/{screenshot_file}"

    verdict = BRAND_VERDICT.get(slug, "")

    # Global badge
    if global_score is None:
        badge = '<div class="brand__global-badge brand__global-badge--no-sub">CONTRÔLE</div>'
    else:
        badge = f'<div class="brand__global-badge">{global_score}<span class="unit">/5</span></div>'

    # Force + faiblesse (1 de chaque, courte)
    force = _short(strengths[0], 140) if strengths else "—"
    faiblesse = _short(weaknesses[0], 140) if weaknesses else "—"

    # Annotations
    annots_html = ""
    for top_pct, left_pct, label in BRAND_ANNOTATIONS.get(slug, []):
        annots_html += f'''
      <div class="annot" style="top:{top_pct};left:{left_pct}">
        <div class="annot__dot"></div>
        <div class="annot__label">{label}</div>
      </div>'''

    # Hero stat (remise)
    if has_sub:
        hero_label = "REMISE ABO"
        hero_value = remise
    else:
        hero_label = "ABONNEMENT"
        hero_value = "—"

    # Ticket KPI
    ticket_display = f"{ticket}<span class='unit'>€</span>" if ticket else "—"

    # Trustpilot KPI
    if trust_score:
        trust_display = f"{trust_score}<span class='unit'>/5</span>"
        trust_sub = f"{trust_n_label} avis"
    else:
        trust_display = "—"
        trust_sub = "—"

    # Scorecard 3 scores (UX, Offre, Pertinence) + Global est dans le badge
    sc_ux = ev.get("score_ux")
    sc_offre = ev.get("score_offre_commerciale")
    sc_pert = ev.get("score_pertinence_vs_impulse")

    no_sub_class = " brand--no-sub" if not has_sub else ""

    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE {idx:02d} — {brand_name.upper()}
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page{no_sub_class}">
  <nav class="nav">
    <span class="nav__item">Intro</span>
    <span class="nav__item">Méthodologie</span>
    <span class="nav__item nav__item--active">Benchmark</span>
    <span class="nav__item">Synthèse</span>
    <span class="nav__item">Rentabilité</span>
    <span class="nav__item">Recommandation</span>
    <span class="nav__item">Next steps</span>
  </nav>

  <div class="brand__title-row">
    <h1 class="brand__title-name">{brand_name}</h1>
    {badge}
  </div>
  <div class="brand__title-verdict">{verdict}</div>
  <div class="title__rule" style="margin-top:20px;margin-bottom:40px"></div>

  <div class="body">
    <div class="brand__grid">
      <div class="brand__screen-wrap">
        <img class="brand__screen" src="{screenshot_path}" alt="{brand_name} screenshot">{annots_html}
        <div class="brand__screen-caption">
          <span class="brand__screen-caption-url">{url.replace('https://','').replace('http://','').rstrip('/')}</span>
          <span class="brand__screen-caption-type">{screenshot_file.replace('_', ' ').replace('.png', '')}</span>
        </div>
      </div>

      <div class="brand__right">
        <div class="brand__data">
          <div class="brand__panel">
            <div class="brand__panel-title">Modèle commercial</div>
            <div class="brand__row"><div class="brand__lbl">Remise</div><div class="brand__val"><strong>{remise if has_sub else '—'}</strong></div></div>
            <div class="brand__row"><div class="brand__lbl">Fréquences</div><div class="brand__val">{fmt_freq_tags(mc) if has_sub else '—'}</div></div>
            <div class="brand__row"><div class="brand__lbl">Livraison</div><div class="brand__val">{liv if has_sub else '—'}</div></div>
            <div class="brand__row"><div class="brand__lbl">Engagement</div><div class="brand__val{' brand__val--warn' if eng not in ('Aucun', '') else ''}">{eng if has_sub else '—'}</div></div>
            <div class="brand__row"><div class="brand__lbl">Flexibilité</div><div class="brand__val">{fmt_flex_tags(mc) if has_sub else '—'}</div></div>
            <div class="brand__row"><div class="brand__lbl">Scope</div><div class="brand__val">{_short(pp.get('scope', '—'), 90)}</div></div>
            <div class="brand__row"><div class="brand__lbl">Exclusions</div><div class="brand__val{' brand__val--muted' if not pp.get('exclusions') else ''}">{_short(', '.join(pp.get('exclusions', [])), 90) or 'Aucune'}</div></div>
          </div>
          <div class="brand__panel">
            <div class="brand__panel-title">UX &amp; Visibilité</div>
            <div class="brand__row"><div class="brand__lbl">CTA</div><div class="brand__val"><strong>"{ux.get('wording_cta', '—')}"</strong></div></div>
            <div class="brand__row"><div class="brand__lbl">Module</div><div class="brand__val">{_short(ux.get('placement_module', '—'), 80)}</div></div>
            <div class="brand__row"><div class="brand__lbl">Présence</div><div class="brand__val">{_presence_tags(ux)}</div></div>
            <div class="brand__row"><div class="brand__lbl">Email</div><div class="brand__val">{_short(str(ux.get('email_mention') or 'Non documenté'), 80)}</div></div>
            <div class="brand__row"><div class="brand__lbl">Trustpilot</div><div class="brand__val"><strong>{trust_score or '—'}</strong>/5 <span style="color:var(--grey-500)">({trust_n_label} avis)</span></div></div>
          </div>
        </div>

        <div class="brand__feedback">
          <div class="brand__feedback-item brand__feedback-item--plus">
            <div class="brand__feedback-icon">+</div>
            <div class="brand__feedback-text">{force}</div>
          </div>
          <div class="brand__feedback-item brand__feedback-item--minus">
            <div class="brand__feedback-icon">−</div>
            <div class="brand__feedback-text">{faiblesse}</div>
          </div>
        </div>

        <div class="brand__scores">
          <div class="brand__score {score_class(sc_ux)}">
            <div class="brand__score-label">UX</div>
            {render_score(sc_ux)}
          </div>
          <div class="brand__score {score_class(sc_offre)}">
            <div class="brand__score-label">Offre</div>
            {render_score(sc_offre)}
          </div>
          <div class="brand__score {score_class(sc_pert)}">
            <div class="brand__score-label">Pertinence</div>
            {render_score(sc_pert)}
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer__confidential">Internal document — Strictly confidential</div>
    <div class="footer__pagination"><strong>{idx:02d}</strong> / {total}</div>
  </div>
</section>
'''


def _short(text, max_len):
    if not text:
        return "—"
    text = str(text)
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def main():
    # Generate the 8 brand slides as HTML
    slides_html = ""
    for i, slug in enumerate(BRAND_ORDER):
        data_path = MARQUES / slug / "data.json"
        data = json.loads(data_path.read_text(encoding="utf-8"))
        slides_html += render_brand_slide(4 + i, slug, data, total=21)

    # Read current deck.html
    html = DECK.read_text(encoding="utf-8")

    # Remove any previously injected brand slides block
    marker_start = "<!-- BRAND_SLIDES_BEGIN -->"
    marker_end = "<!-- BRAND_SLIDES_END -->"
    if marker_start in html and marker_end in html:
        before = html.split(marker_start)[0]
        after = html.split(marker_end)[1]
        html = before + marker_start + marker_end + after

    # Insert before </body>
    new_block = f"{marker_start}\n{slides_html}\n{marker_end}"
    if marker_start not in html:
        html = html.replace("</body>", f"{new_block}\n\n</body>")
    else:
        html = html.replace(
            f"{marker_start}{marker_end}",
            new_block,
        )

    DECK.write_text(html, encoding="utf-8")
    print(f"[ok] {len(BRAND_ORDER)} brand slides injected into {DECK.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
