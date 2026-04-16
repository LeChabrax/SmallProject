"""Génère les slides 12-19 (synthèse, rentabilité+heatmap PR, reco, verdict,
next steps, décision) et les injecte dans deck.html entre les markers
FINAL_SLIDES_BEGIN/END.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARQUES = ROOT / "marques"
DECK = Path(__file__).resolve().parent / "deck.html"

BRAND_ORDER_BY_RANK = [
    "aqeelab", "nutriandco", "nutrimuscle", "novoma", "cuure", "myprotein", "decathlon", "nutripure",
]


def load_brands():
    return {s: json.loads((MARQUES / s / "data.json").read_text(encoding="utf-8")) for s in BRAND_ORDER_BY_RANK}


def load_impulse_products():
    return json.loads((ROOT / "impulse_products_enriched.json").read_text(encoding="utf-8"))


def nav(active):
    items = ["Intro", "Méthodologie", "Benchmark", "Synthèse", "Rentabilité", "Recommandation", "Next steps"]
    html = '<nav class="nav">'
    for it in items:
        cls = "nav__item nav__item--active" if it == active else "nav__item"
        html += f'<span class="{cls}">{it}</span>'
    html += '</nav>'
    return html


def footer(page, total=18):
    return f'''<div class="footer">
    <div class="footer__confidential">Internal document — Strictly confidential</div>
    <div class="footer__pagination"><strong>{page:02d}</strong> / {total}</div>
  </div>'''


# ─── Slide 12 — Synthèse + quadrant ────────────────────────────────────

def slide_synthesis(brands):
    # Build table rows
    rows_html = ""
    # Order by global score desc, Nutripure last (control)
    ranked = sorted(
        [s for s in BRAND_ORDER_BY_RANK if s != "nutripure"],
        key=lambda s: -(brands[s].get("evaluation", {}).get("score_global") or 0),
    )
    ranked.append("nutripure")
    for i, slug in enumerate(ranked):
        d = brands[slug]
        mc = d.get("modele_commercial", {})
        ev = d.get("evaluation", {})
        avis = d.get("avis", {})

        remise = mc.get("remise_pct")
        if isinstance(remise, (int, float)):
            remise_label = f"−{remise}%"
        elif remise:
            remise_label = str(remise)[:14]
        else:
            remise_label = "—"

        freqs = mc.get("frequencies", [])
        freq_label = str(len(freqs)) if freqs else "—"

        liv = mc.get("livraison_abo", {}) or {}
        if liv.get("offerte") is True and liv.get("seuil_eur") == 0:
            liv_label = '<td class="num yes">Sans seuil</td>'
        elif liv.get("offerte") == "relais uniquement":
            liv_label = '<td class="num partial">Relais only</td>'
        elif liv.get("offerte") is True:
            liv_label = f'<td class="num yes">Dès {liv["seuil_eur"]}€</td>'
        elif liv.get("offerte") is False:
            liv_label = f'<td class="num partial">Stepped {liv.get("seuil_eur", "?")}€</td>'
        else:
            liv_label = '<td class="num">—</td>'

        eng = mc.get("engagement_min", "") or ""
        if "Aucun" in eng or eng == "":
            eng_label = '<td class="num yes">Aucun</td>'
        elif "2 mois" in eng:
            eng_label = '<td class="num no">2 mois</td>'
        elif not d.get("has_subscription", False):
            eng_label = '<td class="num">—</td>'
        else:
            eng_label = '<td class="num partial">Friction</td>'

        global_score = ev.get("score_global")
        global_cell = f'<td class="global">{global_score}</td>' if global_score else '<td class="num">contrôle</td>'

        row_class = "top-row" if i < 3 else ""
        rows_html += f'''
    <tr class="{row_class}">
      <td class="name">{d.get("brand", slug)}</td>
      <td class="num">{remise_label}</td>
      <td class="num">{freq_label}</td>
      {liv_label}
      {eng_label}
      <td class="num">{ev.get("score_ux") or "—"}</td>
      <td class="num">{ev.get("score_offre_commerciale") or "—"}</td>
      <td class="num">{ev.get("score_pertinence_vs_impulse") or "—"}</td>
      {global_cell}
    </tr>'''

    # Quadrant SVG : X = remise % (0-30), Y = livraison (stepped=0, offerte=1)
    # Bubble size = note globale (2-5)
    quadrant_points = []
    for slug in BRAND_ORDER_BY_RANK:
        d = brands[slug]
        mc = d.get("modele_commercial", {})
        ev = d.get("evaluation", {})
        remise = mc.get("remise_pct")
        if not isinstance(remise, (int, float)):
            # Parse first int from string
            import re
            m = re.search(r'\d+', str(remise or ""))
            remise_val = int(m.group()) if m else 0
        else:
            remise_val = int(remise)
        liv = mc.get("livraison_abo", {}) or {}
        y_val = 1.0 if (liv.get("offerte") is True) else (0.4 if liv.get("offerte") else 0)
        score = ev.get("score_global") or 2.5
        quadrant_points.append({
            "name": d.get("brand", slug)[:12],
            "x": remise_val,
            "y": y_val,
            "score": score,
            "slug": slug,
        })

    # Build SVG : 600x440 viewport, plot area 80-560 x 60-380
    svg = '<svg class="quadrant-svg" viewBox="0 0 600 460" xmlns="http://www.w3.org/2000/svg">'
    # Background grid
    svg += '<rect x="80" y="60" width="480" height="320" fill="none" stroke="#C7BFA9" stroke-width="0.8"/>'
    # Mid lines — more visible
    svg += '<line x1="320" y1="60" x2="320" y2="380" stroke="#4A525E" stroke-width="0.8" stroke-dasharray="6 4"/>'
    svg += '<line x1="80" y1="220" x2="560" y2="220" stroke="#4A525E" stroke-width="0.8" stroke-dasharray="6 4"/>'
    # Additional grid lines for 10% and 20%
    for val in [10, 20]:
        gx = 80 + (val / 30) * 480
        svg += f'<line x1="{gx}" y1="60" x2="{gx}" y2="380" stroke="#C7BFA9" stroke-width="0.5" stroke-dasharray="3 5"/>'
    # Axes labels
    svg += '<text x="320" y="425" text-anchor="middle" font-size="13" fill="#0A0F1E" font-weight="700" letter-spacing="0.08em">REMISE ABO (%)</text>'
    svg += '<text x="20" y="220" text-anchor="middle" font-size="13" fill="#0A0F1E" font-weight="700" letter-spacing="0.08em" transform="rotate(-90, 20, 220)">LIVRAISON</text>'
    # X axis ticks
    for val in [0, 10, 20, 30]:
        x = 80 + (val / 30) * 480
        svg += f'<line x1="{x}" y1="380" x2="{x}" y2="390" stroke="#0A0F1E" stroke-width="1.5"/>'
        svg += f'<text x="{x}" y="406" text-anchor="middle" font-size="12" fill="#0A0F1E" font-weight="600">{val}%</text>'
    # Y axis labels
    svg += '<text x="72" y="66" text-anchor="end" font-size="11" fill="#0A0F1E" font-weight="600">Offerte</text>'
    svg += '<text x="72" y="224" text-anchor="end" font-size="11" fill="#0A0F1E" font-weight="600">Stepped</text>'
    svg += '<text x="72" y="384" text-anchor="end" font-size="11" fill="#0A0F1E" font-weight="600">Payante</text>'

    # Zone labels
    svg += '<text x="440" y="100" text-anchor="middle" font-size="11" fill="#279989" font-weight="700" font-style="italic">ACQUISITION AGRESSIVE</text>'
    svg += '<text x="200" y="360" text-anchor="middle" font-size="11" fill="#C96E1F" font-weight="700" font-style="italic">RENTABILITÉ PRUDENTE</text>'

    # Plot points — circles at true position, labels offset to avoid overlap
    # First pass: draw all circles
    coords = []
    for p in quadrant_points:
        x = 80 + (min(p["x"], 30) / 30) * 480
        y = 380 - (p["y"] * 320)
        r = 8 + (p["score"] - 2) * 6
        fill = "#279989" if p["score"] >= 3.5 else "#C96E1F"
        svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" opacity="0.7" stroke="white" stroke-width="2"/>'
        coords.append((x, y, r, p["name"]))

    # Second pass: place labels with collision avoidance on labels only
    label_positions = []
    for x, y, r, name in coords:
        label_x = x + r + 6
        label_y = y + 4
        label_anchor = "start"
        if x > 420:
            label_x = x - r - 6
            label_anchor = "end"
        # Push label up/down if it overlaps a previous label
        for lx, ly in label_positions:
            if abs(label_x - lx) < 80 and abs(label_y - ly) < 18:
                label_y = ly - 20
        label_positions.append((label_x, label_y))
        svg += f'<text x="{label_x}" y="{label_y}" text-anchor="{label_anchor}" font-size="11" fill="#0A0F1E" font-weight="700">{name}</text>'
    svg += '</svg>'

    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 12 — SYNTHÈSE COMPARATIVE + QUADRANT POSITIONNEMENT
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Synthèse")}
  <h1 class="title">8 marques × 8 dimensions · deux patterns antagonistes visibles d'un coup d'œil.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="synth__grid">
      <div>
        <table class="synth__table">
          <thead><tr>
            <th>Marque</th>
            <th>Remise</th>
            <th>Fréq.</th>
            <th>Livraison abo</th>
            <th>Engagement</th>
            <th>UX</th>
            <th>Offre</th>
            <th>Pert.</th>
            <th>Global</th>
          </tr></thead>
          <tbody>{rows_html}
          </tbody>
        </table>
      </div>
      <div class="synth__quadrant">
        <div class="synth__quadrant-title">Positionnement · remise × livraison</div>
        {svg}
        <div class="synth__insight">
          <strong>Pattern A — Acquisition agressive</strong> (Aqeelab · Nutri&Co · Nutrimuscle · MyProtein) :
          livraison offerte sans seuil + remise −15 à −45%. Sacrifie la marge logistique pour la conversion.
          <br><br>
          <strong>Pattern B — Rentabilité prudente</strong> (Novoma · Decathlon) :
          livraison stepped + remise modérée. Protège la marge mais moins attractif en CTA.
        </div>
      </div>
    </div>
  </div>
  {footer(12)}
</section>'''


# ─── Slides 13-14 — RENTABILITE matrice livraison x remise ────────────

def _cell_bg_pct(val):
    if val >= 30:
        return "#dcfce7"
    if val >= 15:
        return "#bbf7d0"
    if val >= 0:
        return "#fef3c7"
    return "#fecaca"


def _group_variants(products):
    """Group products with same price + same COGS into one line."""
    import re
    groups = {}
    for p in products:
        # Key = price + cogs rounded to detect same contribution
        key = (p.get("retail_price", 0), round(p.get("cogs_ht", 0), 1))
        base = re.sub(r'\s+(cacao|exotique|nature|citron|pêche|menthe|cerise|fruits rouges|vanille|chocolat|choco-coco|chocolat).*', '', p.get("title", ""), flags=re.IGNORECASE).strip()
        group_key = (key, base)
        if group_key not in groups:
            groups[group_key] = {"product": p, "variants": []}
        groups[group_key]["variants"].append(p.get("title", ""))

    result = []
    for (key, base), g in groups.items():
        p = g["product"].copy()
        if len(g["variants"]) > 1:
            # Merge title
            p["title"] = f'{base} ({len(g["variants"])} parfums)'
        result.append(p)
    return result


def _rentab_table(products):
    grouped = _group_variants(products)
    # Sort by contribution % at -15% point relais
    def _sort_key(p):
        nc = p.get("scenarios", {}).get("15pct", {}).get("logistics", {}).get("point_relais", {}).get("net_contribution", 0)
        sub_ht = p.get("scenarios", {}).get("15pct", {}).get("sub_price_ht", 1)
        return -(nc / sub_ht * 100) if sub_ht > 0 else 0
    grouped.sort(key=_sort_key)
    rows = ""
    for p in grouped:
        title = p.get("title", "?")
        if len(title) > 38:
            title = title[:37] + "..."
        rows += f'<tr><td class="product-name">{title}</td>'
        for mode in ["point_relais", "domicile", "express"]:
            for disc in ["10pct", "15pct", "20pct"]:
                nc = p.get("scenarios", {}).get(disc, {}).get("logistics", {}).get(mode, {}).get("net_contribution", 0)
                sub_ht = p.get("scenarios", {}).get(disc, {}).get("sub_price_ht", 1)
                pct = (nc / sub_ht * 100) if sub_ht > 0 else 0
                bg = _cell_bg_pct(pct)
                rows += f'<td style="background:{bg}">{pct:.0f}%</td>'
        rows += '</tr>'
    return rows, len(grouped)


def slide_rentab(impulse, cat_filter, slide_num, cat_label):
    products = impulse.get("products", [])
    if isinstance(cat_filter, list):
        filtered = [p for p in products if p.get("category") in cat_filter and p.get("retail_price", 0) > 5]
    else:
        filtered = [p for p in products if p.get("category") == cat_filter and p.get("retail_price", 0) > 5]
    rows_html, grouped_count = _rentab_table(filtered)

    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE {slide_num} — RENTABILITE {cat_label.upper()}
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Rentabilité")}
  <h1 class="title">Rentabilité {cat_label} · contribution nette HT par produit × livraison × remise.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div style="overflow:auto;flex:1">
      <table class="rentab__table">
        <thead>
          <tr>
            <th rowspan="2" style="text-align:left;min-width:170px">Produit</th>
            <th colspan="3" class="group-pr">Point Relais (3,90€)</th>
            <th colspan="3" class="group-dom">Domicile (5,90€)</th>
            <th colspan="3" class="group-exp">Express (10,90€)</th>
          </tr>
          <tr>
            <th class="sub">-10%</th><th class="sub">-15%</th><th class="sub">-20%</th>
            <th class="sub">-10%</th><th class="sub">-15%</th><th class="sub">-20%</th>
            <th class="sub">-10%</th><th class="sub">-15%</th><th class="sub">-20%</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <div class="rentab__legend">
      <div class="rentab__legend-item"><div class="rentab__legend-sw" style="background:#dcfce7"></div>Rentable (≥ 30%)</div>
      <div class="rentab__legend-item"><div class="rentab__legend-sw" style="background:#bbf7d0"></div>Correct (15-30%)</div>
      <div class="rentab__legend-item"><div class="rentab__legend-sw" style="background:#fef3c7"></div>Marginal (0-15%)</div>
      <div class="rentab__legend-item"><div class="rentab__legend-sw" style="background:#fecaca"></div>Déficitaire (&lt; 0%)</div>
      <span style="margin-left:auto;font-size:10px;color:var(--grey-500)">% = contribution nette HT / prix abo HT · {grouped_count} lignes ({len(filtered)} SKUs)</span>
    </div>
  </div>
  {footer(slide_num, total=18)}
</section>'''


# Keep old function name for compat in main()
def slide_heatmap(impulse):
    products = impulse.get("products", [])

    # Group products by category, sorted by score within each
    categories = {"sante": "Santé", "sport": "Sport", "snack": "Snack", "accessoire": "Accessoire"}
    cat_order = ["sante", "sport", "snack", "accessoire"]

    rows_html = ""
    for cat in cat_order:
        cat_products = sorted(
            [p for p in products if p.get("category") == cat],
            key=lambda p: -(p.get("subscription_score") or 0),
        )
        if not cat_products:
            continue

        cells = ""
        for p in cat_products:
            elig = p.get("eligibility", "unknown")
            elig_class = {"GO": "go", "MAYBE": "maybe", "NO-GO": "nogo"}.get(elig, "maybe")
            title = p.get("title", "?")
            if len(title) > 22:
                title = title[:21] + "…"
            score = p.get("subscription_score") or 0
            price = p.get("retail_price", 0)
            margin = p.get("gross_margin_pct_ht", 0)
            cells += f'''
          <div class="hm2__cell hm2__cell--{elig_class}" title="{p.get('title', '')} | {price}€ TTC | marge {margin:.0f}% HT">
            <div class="hm2__cell-title">{title}</div>
            <div class="hm2__cell-row">
              <span class="hm2__cell-score">{score}</span>
              <span class="hm2__cell-price">{price:.0f}€</span>
              <span class="hm2__cell-margin">{margin:.0f}%</span>
            </div>
          </div>'''

        cat_label = categories.get(cat, cat)
        cat_count = len(cat_products)
        go_in_cat = sum(1 for p in cat_products if p.get("eligibility") == "GO")
        rows_html += f'''
        <div class="hm2__row">
          <div class="hm2__row-label">
            <div class="hm2__row-cat">{cat_label}</div>
            <div class="hm2__row-count">{cat_count} SKUs · {go_in_cat} GO</div>
          </div>
          <div class="hm2__row-cells">{cells}
          </div>
        </div>'''

    # Counts
    go_count = sum(1 for p in products if p.get("eligibility") == "GO")
    maybe_count = sum(1 for p in products if p.get("eligibility") == "MAYBE")
    nogo_count = sum(1 for p in products if p.get("eligibility") == "NO-GO")

    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 13 — HEATMAP PR · 43 SKUs scorés par catégorie
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Rentabilité")}
  <h1 class="title">Heatmap rentabilité · 43 SKUs Impulse classés par catégorie · score abo /100.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="hm2">{rows_html}
    </div>
    <div class="hm2__bottom">
      <div class="hm2__legend">
        <div class="hm2__legend-item"><div class="hm2__legend-sw hm2__legend-sw--go"></div>GO ({go_count}) · score ≥ 70</div>
        <div class="hm2__legend-item"><div class="hm2__legend-sw hm2__legend-sw--maybe"></div>MAYBE ({maybe_count}) · score 40-69</div>
        <div class="hm2__legend-item"><div class="hm2__legend-sw hm2__legend-sw--nogo"></div>NO-GO ({nogo_count}) · score &lt; 40</div>
        <div class="hm2__legend-item" style="margin-left:24px;opacity:0.7">Chaque cellule : nom · score /100 · prix TTC · marge brute HT%</div>
      </div>
      <div class="hm2__insight">
        <strong style="color:var(--mint-soft)">Lecture :</strong> Les 18 SKUs GO couvrent l'intégralité de la gamme Santé (17/17 éligibles) + 1 sport premium (Preworkout). Les 7 NO-GO sont exclusivement accessoires et snacks non-récurrents. La gamme Sport contient 12 MAYBE qui pourront basculer GO en Phase 2 si le churn M3 est maitrisé.
      </div>
    </div>
  </div>
  {footer(13, total=18)}
</section>'''


# ─── Slide 14 — P&L 3 scénarios ──────────────────────────────────────

def slide_profitability():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 14 — P&L · 3 SCÉNARIOS DE PANIER ABO
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Rentabilité")}
  <h1 class="title">P&L abonnement · 3 paniers types modélisés · contribution nette HT solide à tous les niveaux.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="pnl__grid">
      <div class="pnl-card pnl-card--full">
        <div class="pnl-card__header">
          <div class="pnl-card__title">Mono-produit ~15€</div>
          <div class="pnl-card__total">3,18<span class="unit"> €</span></div>
        </div>
        <div class="pnl-card__subtitle">Magnésium Bisglycinate 15,90€ · marge HT 76%</div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">PVM net HT (−15%)</span><span class="pnl-card__line-value">11,26 €</span></div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">COGS HT</span><span class="pnl-card__line-value">−3,16 €</span></div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">Cout log HT (domicile)</span><span class="pnl-card__line-value">−4,92 €</span></div>
        <div class="pnl-card__line pnl-card__line--total"><span class="pnl-card__line-label"><strong>Contribution nette</strong></span><span class="pnl-card__line-value"><strong>3,18 € · 24%</strong></span></div>
        <div class="pnl-card__verdict pnl-card__verdict--warn">Viable mais tendu · pousse vers l'upsell 2+ produits</div>
      </div>

      <div class="pnl-card pnl-card--full">
        <div class="pnl-card__header">
          <div class="pnl-card__title">Panier ~35€ · seuil livraison offerte</div>
          <div class="pnl-card__total">15,35<span class="unit"> €</span></div>
        </div>
        <div class="pnl-card__subtitle">Magnésium + Multivit 34,80€ · point d'équilibre reco</div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">PVM net HT (−15%)</span><span class="pnl-card__line-value">24,65 €</span></div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">COGS HT cumulé</span><span class="pnl-card__line-value">−4,38 €</span></div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">Cout log HT (domicile)</span><span class="pnl-card__line-value">−4,92 €</span></div>
        <div class="pnl-card__line pnl-card__line--total"><span class="pnl-card__line-label"><strong>Contribution nette</strong></span><span class="pnl-card__line-value"><strong>15,35 € · 53%</strong></span></div>
        <div class="pnl-card__verdict pnl-card__verdict--ok">Sweet spot · confortable meme avec livraison offerte</div>
      </div>

      <div class="pnl-card pnl-card--full">
        <div class="pnl-card__header">
          <div class="pnl-card__title">Pack 3 SKUs ~50€</div>
          <div class="pnl-card__total">20,83<span class="unit"> €</span></div>
        </div>
        <div class="pnl-card__subtitle">Magnésium + Multivit + Créatine 47,70€</div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">PVM net HT (−15%)</span><span class="pnl-card__line-value">33,79 €</span></div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">COGS HT cumulé</span><span class="pnl-card__line-value">−8,04 €</span></div>
        <div class="pnl-card__line"><span class="pnl-card__line-label">Cout log HT (domicile)</span><span class="pnl-card__line-value">−4,92 €</span></div>
        <div class="pnl-card__line pnl-card__line--total"><span class="pnl-card__line-label"><strong>Contribution nette</strong></span><span class="pnl-card__line-value"><strong>20,83 € · 52%</strong></span></div>
        <div class="pnl-card__verdict pnl-card__verdict--ok">Objectif Phase 2 · excellent rendement</div>
      </div>
    </div>

    <div style="margin-top:30px;padding:22px 32px;background:var(--ink);color:var(--cream);border-left:5px solid var(--mint);font-size:15px;line-height:1.6">
      <strong style="color:var(--mint-soft)">Break-even :</strong> A −15% avec livraison domicile (4,92€ HT), le seuil de viabilité est un panier de <strong>7,53€ HT</strong> soit ~9€ TTC. Tous les SKUs santé individuels sont au-dessus. Le seuil 35€ pour la livraison offerte est une <strong>incitation a l'upsell</strong>, pas une protection marge.
    </div>
  </div>
  {footer(14, total=18)}
</section>'''


# ─── Slides 15-17 — Recommandation ─────────────────────────────────────

def slide_reco_products():
    # Load product data for dynamic listing
    impulse = load_impulse_products()
    products = impulse.get("products", [])

    def _nc_pct(p):
        nc = p.get("scenarios", {}).get("15pct", {}).get("logistics", {}).get("point_relais", {}).get("net_contribution", 0)
        sub_ht = p.get("scenarios", {}).get("15pct", {}).get("sub_price_ht", 1)
        return round(nc / sub_ht * 100) if sub_ht > 0 else 0

    sante = sorted([p for p in products if p.get("category") == "sante" and p.get("retail_price", 0) > 5],
                    key=lambda p: -_nc_pct(p))
    sport = sorted([p for p in products if p.get("category") == "sport" and p.get("retail_price", 0) > 5],
                    key=lambda p: -_nc_pct(p))

    # Group variants for display
    def _dedup(prods):
        seen = set()
        result = []
        for p in prods:
            import re
            base = re.sub(r'\s+(cacao|exotique|nature|citron|pêche|menthe|cerise|fruits rouges|vanille|chocolat|choco-coco).*', '', p.get("title", ""), flags=re.IGNORECASE).strip()
            key = (base, p.get("retail_price", 0))
            if key in seen:
                continue
            seen.add(key)
            result.append(p)
        return result

    sante_dedup = _dedup(sante)
    sport_dedup = _dedup(sport)

    sante_rows = ""
    for p in sante_dedup:
        title = p.get("title", "?")
        if len(title) > 22:
            title = title[:21] + "..."
        sante_rows += f'<div class="reco-line"><span class="reco-line__name">{title}</span><span class="reco-line__price">{p["retail_price"]:.0f}€</span><span class="reco-line__nc">{_nc_pct(p)}%</span></div>\n'

    sport_rows = ""
    for p in sport_dedup:
        title = p.get("title", "?")
        if len(title) > 22:
            title = title[:21] + "..."
        nc = _nc_pct(p)
        warn = ' reco-line--warn' if nc < 10 else ''
        sport_rows += f'<div class="reco-line{warn}"><span class="reco-line__name">{title}</span><span class="reco-line__price">{p["retail_price"]:.0f}€</span><span class="reco-line__nc">{nc}%</span></div>\n'

    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 15 — RECO 1/3 · PRODUITS ÉLIGIBLES
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Recommandation")}
  <h1 class="title">Recommandation 1/3 · toute la gamme Santé en Phase 1, Sport rentable en Phase 2.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="reco3__grid">
      <div class="reco3__col">
        <div class="reco3__col-header reco3__col-header--go">Phase 1 · Santé ({len(sante_dedup)} SKUs)</div>
        <div class="reco3__col-subheader"><span>Produit</span><span>Prix</span><span>NC%</span></div>
        {sante_rows}
      </div>
      <div class="reco3__col">
        <div class="reco3__col-header reco3__col-header--maybe">Phase 2 · Sport ({len(sport_dedup)} SKUs)</div>
        <div class="reco3__col-subheader"><span>Produit</span><span>Prix</span><span>NC%</span></div>
        {sport_rows}
      </div>
      <div class="reco3__col">
        <div class="reco3__col-header reco3__col-header--no">Exclus</div>
        <div class="reco-line"><span class="reco-line__name">Packs / coffrets</span></div>
        <div class="reco-line"><span class="reco-line__name">Accessoires</span></div>
        <div class="reco-line"><span class="reco-line__name">Portions unitaires (3€)</span></div>
        <div class="reco-line"><span class="reco-line__name">Produits saisonniers</span></div>
      </div>
    </div>
    <div style="margin-top:12px;font-size:11px;color:var(--grey-500)">NC% = contribution nette a -15% point relais / prix abo HT. Variantes gout regroupees (meme rentabilite).</div>
  </div>
  {footer(15, total=18)}
</section>'''


def slide_reco_commercial():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 16 — RECO 2/3 · MODÈLE COMMERCIAL (2 approches)
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Recommandation")}
  <h1 class="title">Recommandation 2/3 · modèle commercial · 2 approches a arbitrer par le comité.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <table class="reco-compare">
      <thead>
        <tr>
          <th class="reco-compare__label"></th>
          <th class="reco-compare__col reco-compare__col--reco">Pack custom abo<br><span style="font-weight:400;font-size:10px">Recommandé</span></th>
          <th class="reco-compare__col reco-compare__col--alt">Par produit<br><span style="font-weight:400;font-size:10px">Alternative / fallback</span></th>
        </tr>
      </thead>
      <tbody>
        <tr><td class="reco-compare__label">Remise</td><td>−10% flat</td><td>−10% flat</td></tr>
        <tr><td class="reco-compare__label">Fréquences</td><td>1 / 2 / 3 mois</td><td>1 / 2 / 3 mois</td></tr>
        <tr><td class="reco-compare__label">Format</td><td><strong>Pack composé par le client</strong></td><td>1 produit = 1 abonnement</td></tr>
        <tr><td class="reco-compare__label">Livraison offerte</td><td>Dès 35€ (49€ protéines)</td><td>Si commandes groupées > 35€</td></tr>
        <tr><td class="reco-compare__label">Colis</td><td><strong>1 colis par cycle</strong></td><td>Fragmenté si fréquences différentes</td></tr>
        <tr><td class="reco-compare__label">Panier moyen</td><td>35€+ (garanti par design)</td><td>15-25€ (mono-produit fréquent)</td></tr>
        <tr><td class="reco-compare__label">Engagement</td><td>Aucun · résiliation 1 clic</td><td>Aucun · résiliation 1 clic</td></tr>
        <tr><td class="reco-compare__label">Espace abonné</td><td>Modifier produits + fréquence + pause</td><td>Modifier fréquence + pause par produit</td></tr>
        <tr><td class="reco-compare__label">Email 48h</td><td>Oui · fenêtre de modification</td><td>Oui · fenêtre de modification</td></tr>
        <tr><td class="reco-compare__label">Stacking codes</td><td>Welcome OK · promos non cumul</td><td>Welcome OK · promos non cumul</td></tr>
        <tr><td class="reco-compare__label">Implémentation</td><td>Dev custom ou app avancée</td><td>Recharge / Bold standard</td></tr>
      </tbody>
      <tfoot>
        <tr>
          <td class="reco-compare__label" style="font-weight:700;color:var(--ink)">Verdict</td>
          <td style="background:rgba(39,153,137,0.1);font-weight:700;color:var(--mint-dark)">Recommandé si le dev est faisable</td>
          <td style="background:rgba(254,217,146,0.2);font-weight:700;color:#8B6914">Fallback si contrainte technique</td>
        </tr>
      </tfoot>
    </table>
  </div>
  {footer(16, total=18)}
</section>'''


def slide_reco_ux():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 17 — RECO 3/3 · UX · POSITIONNEMENT
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Recommandation")}
  <h1 class="title">Recommandation 3/3 · 5 patterns à copier · 5 anti-patterns à éviter absolument.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="reco-products-grid">
      <div class="reco-col reco-col--go">
        <div class="reco-col__title">À copier · patterns gagnants du panel</div>
        <div class="reco-item"><div class="reco-item__icon">+</div><div class="reco-item__text">CTA <strong>"S'abonner &amp; économiser"</strong><em>Source Aqeelab · déclencheur psychologique sur le CTA</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">+</div><div class="reco-item__text"><strong>Affichage du montant économisé en euros</strong> sur la fiche<em>Source Aqeelab · pattern persuasif unique (vs abstraction du %)</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">+</div><div class="reco-item__text"><strong>Page dédiée /pages/abonnement</strong> avec pitch éditorial santé<em>Source Novoma · "Les compléments marchent mieux sur le long terme"</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">+</div><div class="reco-item__text"><strong>Visibilité maximale</strong> : homepage + nav + newsletter<em>Source Nutrimuscle · le plus visible du panel</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">+</div><div class="reco-item__text"><strong>Email pré-expédition 48h</strong> avec fenêtre de modification<em>Source Nutri&amp;Co · seul mécanisme anti-churn documenté</em></div></div>
      </div>
      <div class="reco-col reco-col--no">
        <div class="reco-col__title">À éviter · anti-patterns documentés</div>
        <div class="reco-item"><div class="reco-item__icon">✗</div><div class="reco-item__text"><strong>Sous-domaine séparé</strong><em>Source Decathlon · friction redirect, parcours abonné isolé</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">✗</div><div class="reco-item__text"><strong>"1 produit = 1 abo"</strong><em>Source Decathlon · mauvaise UX multi-abos, pas de panier abo</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">✗</div><div class="reco-item__text"><strong>Résiliation en 2 temps</strong> (suspension vs email)<em>Source Cuure · dark pattern à la limite Loi Chatel</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">✗</div><div class="reco-item__text"><strong>Engagement minimum forcé</strong><em>Source Aqeelab · friction d'entrée tue la conversion</em></div></div>
        <div class="reco-item"><div class="reco-item__icon">✗</div><div class="reco-item__text"><strong>Prix de base instables</strong><em>Source MyProtein · promos permanentes rendent la remise abo illisible</em></div></div>
      </div>
    </div>
  </div>
  {footer(17, total=18)}
</section>'''


# ─── Slide 18 — Verdict 1 page ─────────────────────────────────────────

def slide_next_final():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 18 — NEXT STEPS (verdict + roadmap + décision)
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Next steps")}
  <h1 class="title">Next steps · verdict, roadmap et décision attendue du comité.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div style="padding:14px 32px;background:rgba(39,153,137,0.08);border-left:5px solid var(--mint);text-align:left;font-family:var(--font-display);font-size:20px;font-weight:300;line-height:1.5;letter-spacing:-0.01em;color:var(--ink)">
      Pack abo <strong>−10% flat</strong> · <strong>17 SKUs santé</strong> en Phase 1 · <strong>sans engagement</strong> · livraison offerte dès <strong>35€</strong>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:20px">
      <div style="border-top:4px solid var(--mint);padding:16px 0">
        <div style="font-size:10px;font-weight:700;color:var(--mint);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px">Phase 1 · MVP</div>
        <ul style="font-size:12px;color:var(--ink);line-height:1.6;list-style:none;padding:0">
          <li>17 SKUs gamme Santé complete</li>
          <li>Design UX : fiche + page abo + email 48h</li>
          <li>Choix tech (Recharge / app custom)</li>
          <li>Audit juridique Loi Chatel</li>
          <li><strong>Objectif : 50-100 abonnés actifs</strong></li>
        </ul>
      </div>
      <div style="border-top:4px solid var(--beige);padding:16px 0">
        <div style="font-size:10px;font-weight:700;color:#8B6914;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px">Phase 2 · Optimisation</div>
        <ul style="font-size:12px;color:var(--ink);line-height:1.6;list-style:none;padding:0">
          <li>Ajout sport rentable (Preworkout, BCAA, Whey)</li>
          <li>Test A/B wording CTA</li>
          <li>Analyse cohortes churn par SKU</li>
          <li>Programme fidélité cumulable</li>
          <li><strong>Objectif : mesurer churn 90j</strong></li>
        </ul>
      </div>
      <div style="border-top:4px solid var(--grey-500);padding:16px 0">
        <div style="font-size:10px;font-weight:700;color:var(--grey-500);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px">Phase 3 · Scale</div>
        <ul style="font-size:12px;color:var(--ink);line-height:1.6;list-style:none;padding:0">
          <li>Scale a tout le catalogue éligible</li>
          <li>Parrainage abo cross-canal</li>
          <li>Quiz d'onboarding léger</li>
          <li>Intégration programme ambassadeurs</li>
          <li><strong>Objectif : abo = 15-20% du CA</strong></li>
        </ul>
      </div>
    </div>

    <div style="margin-top:24px;border-top:2px solid var(--ink);padding-top:16px">
      <div style="font-size:10px;font-weight:700;color:var(--ink);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px">Décision attendue du comité</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
        <div style="padding:12px 16px;background:var(--grey-100);font-size:13px;line-height:1.4"><strong>01</strong> · Validez-vous le modèle commercial (pack abo −10%, sans engagement, livraison dès 35€) ?</div>
        <div style="padding:12px 16px;background:var(--grey-100);font-size:13px;line-height:1.4"><strong>02</strong> · Validez-vous le périmètre Phase 1 (17 SKUs santé) ?</div>
        <div style="padding:12px 16px;background:var(--grey-100);font-size:13px;line-height:1.4"><strong>03</strong> · Validez-vous le budget (app ~500€/mois + setup ~5 000€ + audit juridique) ?</div>
      </div>
    </div>
  </div>
  {footer(18, total=18)}
</section>'''


def _old_slide_verdict():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 18 — VERDICT 1 PAGE (synthèse one-look)
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide verdict-slide">
  <nav class="nav">
    <span class="nav__item">Intro</span>
    <span class="nav__item">Méthodologie</span>
    <span class="nav__item">Benchmark</span>
    <span class="nav__item">Synthèse</span>
    <span class="nav__item">Rentabilité</span>
    <span class="nav__item nav__item--active">Recommandation</span>
    <span class="nav__item">Next steps</span>
  </nav>
  <h1 class="title">Verdict en un coup d'œil · le modèle Impulse à valider par le comité.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="verdict__big">
      Lancer <strong>Subscribe &amp; Save −15% flat</strong><br>
      sur <strong>6 SKUs MVP</strong>, <strong>sans engagement</strong>,<br>
      livraison offerte dès <strong>35€</strong>.
    </div>
    <div class="verdict__pillars">
      <div class="verdict__pillar">
        <div class="verdict__pillar-label">Scope</div>
        <div class="verdict__pillar-value">6 SKUs</div>
        <div class="verdict__pillar-text">Santé récurrent : Magnésium, Oméga-3, Multivit, Pré-Probiotiques, Sommeil+, Créatine</div>
      </div>
      <div class="verdict__pillar">
        <div class="verdict__pillar-label">Économie abo</div>
        <div class="verdict__pillar-value">−15%</div>
        <div class="verdict__pillar-text">Flat · aligné référence marché FR · laisse une marge de manœuvre pour promos ponctuelles</div>
      </div>
      <div class="verdict__pillar">
        <div class="verdict__pillar-label">Rentabilité</div>
        <div class="verdict__pillar-value">53%</div>
        <div class="verdict__pillar-text">Taux de contribution nette HT sur un panier 35€ — break-even à 39 abonnés actifs</div>
      </div>
      <div class="verdict__pillar">
        <div class="verdict__pillar-label">Timeline</div>
        <div class="verdict__pillar-value">6 sem.</div>
        <div class="verdict__pillar-text">Design + tech + soft launch · objectif MVP : 50-100 abonnés actifs à M3</div>
      </div>
    </div>
  </div>
  {footer(18, total=18)}
</section>'''


# ─── Slide 19 — Next steps ─────────────────────────────────────────────

def slide_next_steps():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 19 — ROADMAP + ACTIONS IMMÉDIATES
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page">
  {nav("Next steps")}
  <h1 class="title">Roadmap 3 phases · 8 actions immédiates à lancer dès validation comité.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="phases">
      <div class="phase">
        <div class="phase__label">Phase 1 · MVP</div>
        <div class="phase__title">0–3 mois</div>
        <div class="phase__dur">Fondations produit &amp; UX</div>
        <div class="phase__body">
          <ul>
            <li>6 SKUs du Top GO scoring rentabilité</li>
            <li>Toggle fiche produit + page dédiée + mention homepage</li>
            <li>Engagement zéro · −15% flat · livraison offerte dès 35€</li>
            <li>Email pré-expédition 48h actif</li>
            <li><strong>Objectif</strong> : 50-100 abonnés actifs, mesurer churn 90j</li>
          </ul>
        </div>
      </div>
      <div class="phase">
        <div class="phase__label">Phase 2 · OPT</div>
        <div class="phase__title">3–6 mois</div>
        <div class="phase__dur">Optimisation &amp; élargissement</div>
        <div class="phase__body">
          <ul>
            <li>Ajout du Whey avec lock goût à la souscription</li>
            <li>Test A/B wording "S'abonner" vs "S'abonner &amp; économiser"</li>
            <li>Programme de fidélité cumulable</li>
            <li>Analyse cohortes churn par SKU</li>
            <li>Élargissement fréquences sur gros formats</li>
          </ul>
        </div>
      </div>
      <div class="phase">
        <div class="phase__label">Phase 3 · SCALE</div>
        <div class="phase__title">6–12 mois</div>
        <div class="phase__dur">Scale &amp; différenciation</div>
        <div class="phase__body">
          <ul>
            <li>Élargir à tous les SKUs éligibles (hors packs/accessoires)</li>
            <li>Programme de parrainage abo cross-canal</li>
            <li>Quiz d'onboarding léger (inspiré Cuure)</li>
            <li>Intégration programme ambassadeurs</li>
            <li>Optimisation algo upsell 2 → 3 produits</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="actions">
      <div class="actions__title">8 actions immédiates · à lancer dès validation</div>
      <div class="action"><div class="action__n">01</div><div class="action__text">Validation comité projet du modèle commercial</div></div>
      <div class="action"><div class="action__n">02</div><div class="action__text">Audit Loi Chatel avec juriste <em style="opacity:0.6">(1-2 jours)</em></div></div>
      <div class="action"><div class="action__n">03</div><div class="action__text">Choix tech Recharge / Shopify Native / Bold · devis</div></div>
      <div class="action"><div class="action__n">04</div><div class="action__text">Export Shopify 90 jours · baseline potentiel abonnés</div></div>
      <div class="action"><div class="action__n">05</div><div class="action__text">Design / maquettes : fiche + page abo + email 48h</div></div>
      <div class="action"><div class="action__n">06</div><div class="action__text">Mise en place technique <em style="opacity:0.6">(2-3 semaines)</em></div></div>
      <div class="action"><div class="action__n">07</div><div class="action__text">Lancement soft · 6 SKUs · mesure baseline 1 mois</div></div>
      <div class="action"><div class="action__n">08</div><div class="action__text">Lancement officiel · après ajustements UX</div></div>
    </div>
  </div>
  {footer(19, total=18)}
</section>'''


# ─── Slide 20 — Décision attendue ──────────────────────────────────────

def slide_decision():
    return f'''
<!-- ═════════════════════════════════════════════════════════════════
     SLIDE 20 — DÉCISION ATTENDUE DU COMITÉ
     ═════════════════════════════════════════════════════════════════ -->
<section class="slide slide--page decision-slide">
  {nav("Next steps")}
  <h1 class="title">Décision attendue du comité · 3 questions oui/non pour débloquer le lancement.</h1>
  <div class="title__rule"></div>
  <div class="body">
    <div class="decision-questions">
      <div class="decision-q">
        <div class="decision-q__num">01</div>
        <div class="decision-q__text">Validez-vous le <strong>modèle commercial</strong> : −15% flat, sans engagement, livraison offerte dès 35€, stacking partiel avec codes welcome et ambassadeurs ?</div>
        <div class="decision-q__boxes">
          <div class="decision-q__box">OUI</div>
          <div class="decision-q__box">NON</div>
        </div>
      </div>
      <div class="decision-q">
        <div class="decision-q__num">02</div>
        <div class="decision-q__text">Validez-vous le <strong>périmètre MVP Phase 1</strong> : 6 SKUs santé-récurrent (Magnésium, Oméga-3, Multivit, Pré-Probiotiques, Sommeil+, Créatine) ?</div>
        <div class="decision-q__boxes">
          <div class="decision-q__box">OUI</div>
          <div class="decision-q__box">NON</div>
        </div>
      </div>
      <div class="decision-q">
        <div class="decision-q__num">03</div>
        <div class="decision-q__text">Validez-vous le <strong>budget d'investissement</strong> : app abo (~500€/mois) + setup initial design/intégration (~5 000€) + audit juridique (~1 500€) ?</div>
        <div class="decision-q__boxes">
          <div class="decision-q__box">OUI</div>
          <div class="decision-q__box">NON</div>
        </div>
      </div>
    </div>
  </div>
  {footer(20, total=18)}
</section>'''


def main():
    brands = load_brands()
    impulse = load_impulse_products()

    slides_html = ""
    slides_html += slide_synthesis(brands)
    slides_html += slide_rentab(impulse, "sante", 13, "Santé")
    slides_html += slide_rentab(impulse, ["sport", "snack", "accessoire"], 14, "Sport & autres")
    slides_html += slide_reco_products()
    slides_html += slide_reco_commercial()
    slides_html += slide_reco_ux()
    slides_html += slide_next_final()

    # Replace <!-- FINAL_SLIDES_BEGIN --> ... <!-- FINAL_SLIDES_END --> block, or insert before </body>
    html = DECK.read_text(encoding="utf-8")
    marker_start = "<!-- FINAL_SLIDES_BEGIN -->"
    marker_end = "<!-- FINAL_SLIDES_END -->"
    new_block = f"{marker_start}\n{slides_html}\n{marker_end}"
    if marker_start in html and marker_end in html:
        before = html.split(marker_start)[0]
        after = html.split(marker_end)[1]
        html = before + new_block + after
    else:
        html = html.replace("</body>", f"{new_block}\n\n</body>")
    DECK.write_text(html, encoding="utf-8")
    print(f"[ok] 9 final slides (12-20) injected into {DECK.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
