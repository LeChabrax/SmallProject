"""
build_synthesis_table.py — Section 4 du deck mission abonnement.

Agrège les 8 marques/<brand>/data.json en 3 tables comparatives
(modèle commercial, périmètre + UX, évaluation + scores) + classement
final + insights stratégiques. Écrit 2 artefacts :
  - benchmark/synthesis_table.md (markdown, pour l'intégration deck)
  - benchmark/synthesis_table.html (rendu HTML standalone, style distinctif)

Exécution :
    python3 benchmark/scripts/build_synthesis_table.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARQUES = ROOT / "marques"
OUT_MD = ROOT / "synthesis_table.md"
OUT_HTML = ROOT / "synthesis_table.html"

# Ordre d'affichage = classement par note globale descendante (Nutripure en dernier = contrôle)
BRAND_ORDER = [
    "aqeelab",
    "nutriandco",
    "nutrimuscle",
    "novoma",
    "cuure",
    "myprotein",
    "decathlon",
    "nutripure",
]


def load_brands() -> dict:
    brands = {}
    for slug in BRAND_ORDER:
        path = MARQUES / slug / "data.json"
        brands[slug] = json.loads(path.read_text(encoding="utf-8"))
    return brands


def fmt_remise(d: dict) -> str:
    mc = d.get("modele_commercial", {})
    pct = mc.get("remise_pct")
    if pct is None:
        return "—"
    if isinstance(pct, (int, float)):
        return f"−{pct}%"
    return str(pct)


def fmt_freqs(d: dict) -> str:
    freqs = d.get("modele_commercial", {}).get("frequencies", [])
    if not freqs:
        return "—"
    return f"{len(freqs)} ({', '.join(freqs)[:50]})"


def fmt_livraison(d: dict) -> str:
    l = d.get("modele_commercial", {}).get("livraison_abo", {})
    offerte = l.get("offerte")
    seuil = l.get("seuil_eur")
    if offerte is True and seuil == 0:
        return "✅ Flat (sans seuil)"
    if offerte == "relais uniquement":
        return "⚪ Relais only"
    if offerte is True and seuil and seuil > 0:
        return f"✅ dès {seuil}€"
    if offerte is False:
        return f"⚪ Stepped (dès {seuil}€)" if seuil else "❌ Payante"
    if offerte is None:
        return "❓ Non explicité"
    return "—"


def fmt_engagement(d: dict) -> str:
    eng = d.get("modele_commercial", {}).get("engagement_min", "")
    if eng is None:
        return "—"
    if "Aucun" in eng or eng == "":
        return "✅ Aucun"
    if "2 mois" in eng:
        return "⚠️ 2 mois min"
    if "partiel" in eng.lower() or "friction" in eng.lower():
        return "⚠️ Friction"
    return eng[:40]


def fmt_stacking(d: dict) -> str:
    note = (d.get("modele_commercial", {}).get("remise_note") or "").lower()
    weak = " ".join(d.get("evaluation", {}).get("weaknesses", [])).lower()
    if "non cumulable" in note or "non cumulable" in weak or "zéro" in weak:
        return "❌ Zéro"
    if "partiel" in note or "partiel" in weak or "1ère livraison" in note or "influenceur" in weak:
        return "⚪ Partiel"
    if "cumul" in note or "sitewide" in note:
        return "✅ Possible"
    return "❓ Non documenté"


def fmt_scope(d: dict) -> str:
    scope = d.get("perimetre_produit", {}).get("scope") or "—"
    return scope[:70] + "…" if len(scope) > 70 else scope


def fmt_exclusions(d: dict) -> str:
    ex = d.get("perimetre_produit", {}).get("exclusions", [])
    if not ex:
        return "Aucune documentée"
    # Extraire le keyword principal de chaque exclusion
    short = []
    for e in ex[:3]:
        first = e.split("—")[0].split("(")[0].strip()
        short.append(first[:25])
    return " · ".join(short)


def fmt_ticket(d: dict) -> str:
    t = d.get("perimetre_produit", {}).get("ticket_moyen_estime_eur")
    return f"{t}€" if t else "—"


def fmt_dedicated_page(d: dict) -> str:
    return "✅" if d.get("ux_page_produit", {}).get("dedicated_page") else "❌"


def fmt_home_nav(d: dict) -> str:
    ux = d.get("ux_page_produit", {})
    home = ux.get("homepage_mention")
    nav = ux.get("navigation_mention")
    home_ok = bool(home) and home not in (False, None, "")
    nav_ok = bool(nav) and nav not in (False, None, "")
    return f"{'✅' if home_ok else '❌'} / {'✅' if nav_ok else '❌'}"


def fmt_cta(d: dict) -> str:
    cta = d.get("ux_page_produit", {}).get("wording_cta") or "—"
    return cta.split("—")[0].split("(")[0].strip()[:35]


def fmt_score(s) -> str:
    if s is None:
        return "—"
    return f"{s}"


def fmt_trustpilot(d: dict) -> str:
    avis = d.get("avis", {})
    score = avis.get("trustpilot_score")
    n = avis.get("trustpilot_nb_avis")
    if score is None:
        return "—"
    n_fmt = f"{n / 1000:.1f}k" if isinstance(n, (int, float)) and n >= 1000 else str(n)
    return f"{score} / {n_fmt}"


def fmt_highlight(d: dict) -> str:
    """Extrait la première strength comme highlight narratif court."""
    strengths = d.get("evaluation", {}).get("strengths", [])
    if not strengths:
        return "—"
    s = strengths[0]
    # Raccourcir à la 1ère virgule ou 1ère parenthèse
    short = s.split(",")[0].split("(")[0].split(":")[0].strip()
    return short[:90] + ("…" if len(short) > 90 else "")


def build_md(brands: dict) -> str:
    lines = [
        "# Benchmark abonnement — Tableau de synthèse comparatif",
        "",
        "_Section 4 du deck mission. Généré à partir de `benchmark/marques/<brand>/data.json` via `build_synthesis_table.py`._",
        "_Dernière mise à jour : 2026-04-15 — 8/8 marques verified_live._",
        "",
        "---",
        "",
        "## Table 1 — Modèle commercial",
        "",
        "| Marque | Remise | Fréquences | Livraison abo | Engagement | Stacking codes |",
        "|---|---|---|---|---|---|",
    ]
    for slug in BRAND_ORDER:
        d = brands[slug]
        lines.append(
            f"| **{d['brand']}** | {fmt_remise(d)} | {fmt_freqs(d)} | "
            f"{fmt_livraison(d)} | {fmt_engagement(d)} | {fmt_stacking(d)} |"
        )

    lines += [
        "",
        "## Table 2 — Périmètre produit + UX",
        "",
        "| Marque | Scope | Exclusions | Ticket moyen | Page dédiée | Home / Nav | CTA |",
        "|---|---|---|---|---|---|---|",
    ]
    for slug in BRAND_ORDER:
        d = brands[slug]
        lines.append(
            f"| **{d['brand']}** | {fmt_scope(d)} | {fmt_exclusions(d)} | "
            f"{fmt_ticket(d)} | {fmt_dedicated_page(d)} | {fmt_home_nav(d)} | {fmt_cta(d)} |"
        )

    lines += [
        "",
        "## Table 3 — Évaluation synthétique",
        "",
        "| Marque | UX /5 | Offre /5 | Pertinence /5 | **Global /5** | Trustpilot | Highlight |",
        "|---|---|---|---|---|---|---|",
    ]
    for slug in BRAND_ORDER:
        d = brands[slug]
        ev = d.get("evaluation", {})
        global_score = ev.get("score_global")
        global_cell = f"**{global_score}**" if global_score else "**N/A**"
        lines.append(
            f"| **{d['brand']}** | {fmt_score(ev.get('score_ux'))} | "
            f"{fmt_score(ev.get('score_offre_commerciale'))} | "
            f"{fmt_score(ev.get('score_pertinence_vs_impulse'))} | "
            f"{global_cell} | {fmt_trustpilot(d)} | {fmt_highlight(d)} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Lecture stratégique",
        "",
        "### Deux patterns antagonistes détectés",
        "",
        "**Pattern A — Acquisition agressive** (Aqeelab, Nutri&Co, Nutrimuscle, MyProtein)",
        "- Remise élevée (−15% à −45%) + livraison offerte sans seuil + zéro engagement (sauf Aqeelab)",
        "- Cible : conversion rapide, accepte de sacrifier la marge sur la livraison",
        "- Risque : cannibalisation du one-shot, lock-in psychologique seulement",
        "",
        "**Pattern B — Rentabilité prudente** (Novoma, Decathlon)",
        "- Remise modérée (−10% à −15%) + livraison stepped (frais réduits, pas offerte) + zéro engagement",
        "- Cible : protéger la marge, offrir un avantage tangible mais chiffré",
        "- Risque : moins attractif en CTA, moins de conversion en haut de funnel",
        "",
        "**Cas atypiques** :",
        "- **Cuure** : modèle 100% abo personnalisé (quiz + box). Hors championnat Impulse.",
        "- **Nutripure** : pas d'abonnement — mise sur les packs permanents (−10 à −25%) + fidélité + qualité premium. Prouve que l'abo n'est pas obligatoire pour fidéliser.",
        "",
        "### Classement par note globale",
        "",
        "1. 🥇 **Aqeelab** (4,3) — remise massue −20% à vie, UX persuasive avec montant économisé en €, mais engagement 2 mois à vérifier Loi Chatel",
        "2. 🥈 **Nutri&Co** (4,0) — la référence proche Impulse, offre solide et email pré-expédition 48h, module discret qui pourrait être plus visible",
        "3. 🥉 **Nutrimuscle** (3,8) — visibilité maximale (home + nav + emails), 6 fréquences, offre claire, moins proche Impulse en positionnement",
        "4. **Novoma** (3,7) — positionnement santé premium très proche Impulse, offre la plus modérée mais bien construite (FAQ, rationale santé)",
        "5. **Cuure** (3,0) — excellent UX orienté service, trop éloigné structurellement d'Impulse",
        "6. **MyProtein** (2,8) — remise la plus haute en valeur brute mais illisible, pire Trustpilot du panel",
        "7. **Decathlon** (2,5) — contre-modèle UX (sous-domaine séparé, 1 produit = 1 abo)",
        "8. **Nutripure** (contrôle) — pas d'abo, mais le cas prouve que la qualité + packs permanents suffisent parfois",
        "",
        "### Top 3 inspirations pour la reco Impulse",
        "",
        "| Rang | Source | Quoi reprendre |",
        "|---|---|---|",
        "| 1 | **Aqeelab** | Wording 'S'abonner & économiser' + affichage du montant économisé en euros |",
        "| 2 | **Nutri&Co** | Email de pré-expédition avec fenêtre de modification 48h (anti-churn éprouvé) |",
        "| 3 | **Nutrimuscle** | Visibilité max : mention homepage + navigation + newsletter |",
        "",
        "### Top 3 anti-patterns à éviter",
        "",
        "| Rang | Source | Quoi éviter |",
        "|---|---|---|",
        "| 1 | **Decathlon** | Sous-domaine séparé + '1 produit = 1 abo' + 'modification = résiliation+recréation' |",
        "| 2 | **Cuure** | Résiliation en 2 temps (suspension self-serve vs email pour résilier) |",
        "| 3 | **MyProtein** | Prix de base instables qui rendent la remise abo illisible |",
        "",
    ]
    return "\n".join(lines)


def build_html(brands: dict) -> str:
    """Rendu HTML distinctif : finance-research avec Space Grotesk + JetBrains Mono, palette crème/ink/ambre."""
    rows_t1 = []
    rows_t2 = []
    rows_t3 = []

    for slug in BRAND_ORDER:
        d = brands[slug]
        ev = d.get("evaluation", {})

        rows_t1.append(
            f"<tr><td class='brand'>{d['brand']}</td>"
            f"<td>{fmt_remise(d)}</td>"
            f"<td>{fmt_freqs(d)}</td>"
            f"<td>{fmt_livraison(d)}</td>"
            f"<td>{fmt_engagement(d)}</td>"
            f"<td>{fmt_stacking(d)}</td></tr>"
        )
        rows_t2.append(
            f"<tr><td class='brand'>{d['brand']}</td>"
            f"<td class='scope'>{fmt_scope(d)}</td>"
            f"<td class='excl'>{fmt_exclusions(d)}</td>"
            f"<td class='num'>{fmt_ticket(d)}</td>"
            f"<td class='c'>{fmt_dedicated_page(d)}</td>"
            f"<td class='c'>{fmt_home_nav(d)}</td>"
            f"<td>{fmt_cta(d)}</td></tr>"
        )

        def score_cell(s):
            if s is None:
                return "<td class='num mut'>—</td>"
            cls = "num"
            if s >= 4.0:
                cls = "num hi"
            elif s >= 3.0:
                cls = "num mid"
            else:
                cls = "num lo"
            return f"<td class='{cls}'>{s}</td>"

        global_score = ev.get("score_global")
        global_cell = (
            f"<td class='num global'>{global_score}</td>"
            if global_score else "<td class='num mut'>N/A</td>"
        )
        rows_t3.append(
            f"<tr><td class='brand'>{d['brand']}</td>"
            f"{score_cell(ev.get('score_ux'))}"
            f"{score_cell(ev.get('score_offre_commerciale'))}"
            f"{score_cell(ev.get('score_pertinence_vs_impulse'))}"
            f"{global_cell}"
            f"<td class='num'>{fmt_trustpilot(d)}</td>"
            f"<td class='highlight'>{fmt_highlight(d)}</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Benchmark abonnement — Synthèse comparative</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0a0f1e;
    --cream: #f5f1e8;
    --cream-2: #ebe6d8;
    --ink-2: #1e2433;
    --amber: #c96e1f;
    --amber-hi: #e8871a;
    --muted: #6b6558;
    --rule: #c7bfa9;
    --hi: #0d6e3d;
    --mid: #c96e1f;
    --lo: #8b2a1b;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: var(--cream); color: var(--ink); }}
  body {{
    font-family: 'Space Grotesk', -apple-system, sans-serif;
    font-size: 13px;
    line-height: 1.45;
    padding: 48px 40px 80px;
    max-width: 1400px;
    margin: 0 auto;
  }}
  h1 {{
    font-size: 42px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 8px;
    line-height: 1;
  }}
  .kicker {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: 4px;
  }}
  .sub {{
    font-size: 14px;
    color: var(--muted);
    margin: 0 0 48px;
    max-width: 700px;
  }}
  h2 {{
    font-size: 18px;
    font-weight: 700;
    margin: 56px 0 4px;
    letter-spacing: -0.01em;
  }}
  h2 .num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--amber);
    margin-right: 8px;
    font-weight: 600;
  }}
  h2 + .caption {{
    font-size: 11px;
    color: var(--muted);
    font-style: italic;
    margin: 0 0 18px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 11.5px;
    margin-bottom: 8px;
  }}
  th {{
    text-align: left;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    padding: 10px 10px 10px 0;
    border-bottom: 1.5px solid var(--ink);
  }}
  td {{
    padding: 12px 10px 12px 0;
    border-bottom: 0.5px solid var(--rule);
    vertical-align: top;
  }}
  tr:hover td {{ background: rgba(201, 110, 31, 0.04); }}
  td.brand {{
    font-weight: 600;
    font-size: 12.5px;
    width: 150px;
    white-space: nowrap;
  }}
  td.num {{
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }}
  td.num.hi {{ color: var(--hi); font-weight: 600; }}
  td.num.mid {{ color: var(--mid); font-weight: 600; }}
  td.num.lo {{ color: var(--lo); font-weight: 600; }}
  td.num.mut {{ color: var(--muted); }}
  td.num.global {{
    font-size: 14px;
    font-weight: 700;
    color: var(--ink);
    background: rgba(201, 110, 31, 0.08);
    text-align: center;
    min-width: 40px;
  }}
  td.c {{ text-align: center; }}
  td.scope {{ color: var(--muted); font-size: 10.5px; max-width: 280px; }}
  td.excl {{ color: var(--muted); font-size: 10.5px; max-width: 220px; }}
  td.highlight {{ color: var(--ink); font-size: 11px; max-width: 320px; }}
  .insight {{
    background: var(--ink);
    color: var(--cream);
    padding: 32px 36px;
    margin: 56px 0 0;
    border-left: 4px solid var(--amber);
  }}
  .insight h2 {{
    color: var(--cream);
    margin-top: 0;
    font-size: 22px;
  }}
  .insight h2 .num {{ color: var(--amber-hi); }}
  .insight h3 {{
    color: var(--amber-hi);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 24px 0 8px;
  }}
  .insight p {{ margin: 4px 0; font-size: 12.5px; color: #d8d3c4; }}
  .insight strong {{ color: var(--cream); }}
  .insight .rank {{ margin: 4px 0; font-size: 12.5px; }}
  .insight .rank strong {{ color: var(--amber-hi); font-family: 'JetBrains Mono', monospace; font-weight: 600; margin-right: 8px; }}
  .patterns {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin: 16px 0 8px;
  }}
  .pattern {{
    padding: 16px 20px;
    border: 1px solid rgba(245, 241, 232, 0.15);
  }}
  .pattern.a {{ border-left: 3px solid var(--amber-hi); }}
  .pattern.b {{ border-left: 3px solid #6b8d7a; }}
  .pattern h4 {{
    margin: 0 0 8px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--cream);
  }}
  .pattern ul {{ margin: 6px 0 0; padding-left: 16px; font-size: 11.5px; color: #c9c3b0; }}
  .pattern li {{ margin: 2px 0; }}
  .footer {{
    margin-top: 64px;
    padding-top: 24px;
    border-top: 0.5px solid var(--rule);
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    color: var(--muted);
    letter-spacing: 0.05em;
  }}
</style>
</head>
<body>

<div class="kicker">Benchmark nutrition sportive FR · 2026-04-15</div>
<h1>Modèles d'abonnement<br>8 marques, 3 lectures</h1>
<p class="sub">Synthèse comparative du panel de référence pour la mission Impulse. 8/8 marques audités en live. Section 4 du deck interne comité projet.</p>

<h2><span class="num">01 /</span>Modèle commercial</h2>
<p class="caption">Remise, fréquences, livraison, engagement, stacking codes — les leviers commerciaux bruts.</p>
<table>
<thead><tr>
<th>Marque</th><th>Remise</th><th>Fréquences</th><th>Livraison abo</th><th>Engagement</th><th>Stacking</th>
</tr></thead>
<tbody>
{''.join(rows_t1)}
</tbody>
</table>

<h2><span class="num">02 /</span>Périmètre produit · UX fiche</h2>
<p class="caption">Ce qui est abonnable, où l'offre est visible sur le site, et comment elle est formulée.</p>
<table>
<thead><tr>
<th>Marque</th><th>Scope</th><th>Exclusions</th><th>Panier moy.</th><th>Page dédiée</th><th>Home / Nav</th><th>CTA</th>
</tr></thead>
<tbody>
{''.join(rows_t2)}
</tbody>
</table>

<h2><span class="num">03 /</span>Évaluation synthétique</h2>
<p class="caption">Notes /5 calibrées en fin de revue homogène (UX, Offre, Pertinence vs Impulse, Global = moyenne).</p>
<table>
<thead><tr>
<th>Marque</th><th>UX /5</th><th>Offre /5</th><th>Pertinence /5</th><th>Global /5</th><th>Trustpilot</th><th>Highlight</th>
</tr></thead>
<tbody>
{''.join(rows_t3)}
</tbody>
</table>

<div class="insight">
<h2><span class="num">04 /</span>Lecture stratégique</h2>

<h3>Deux patterns antagonistes</h3>
<div class="patterns">
<div class="pattern a">
  <h4>A · Acquisition agressive</h4>
  <p>Aqeelab, Nutri&Co, Nutrimuscle, MyProtein</p>
  <ul>
    <li>Remise −15% à −45%</li>
    <li>Livraison offerte sans seuil</li>
    <li>Zéro engagement (sauf Aqeelab)</li>
    <li>Sacrifice marge logistique</li>
  </ul>
</div>
<div class="pattern b">
  <h4>B · Rentabilité prudente</h4>
  <p>Novoma, Decathlon</p>
  <ul>
    <li>Remise −10% à −15%</li>
    <li>Livraison stepped (frais réduits)</li>
    <li>Zéro engagement</li>
    <li>Protège la marge — moins attractif</li>
  </ul>
</div>
</div>

<h3>Top 3 inspirations pour Impulse</h3>
<p class="rank"><strong>01</strong> <strong style="color:var(--cream)">Aqeelab</strong> · Wording «&nbsp;S'abonner & économiser&nbsp;» + affichage du montant économisé en euros</p>
<p class="rank"><strong>02</strong> <strong style="color:var(--cream)">Nutri&amp;Co</strong> · Email de pré-expédition avec fenêtre de modification 48h (anti-churn éprouvé)</p>
<p class="rank"><strong>03</strong> <strong style="color:var(--cream)">Nutrimuscle</strong> · Visibilité max : mention homepage + navigation + newsletter</p>

<h3>Top 3 anti-patterns à éviter</h3>
<p class="rank"><strong>01</strong> <strong style="color:var(--cream)">Decathlon</strong> · Sous-domaine séparé + «&nbsp;1 produit = 1 abo&nbsp;» + modification = résiliation + recréation</p>
<p class="rank"><strong>02</strong> <strong style="color:var(--cream)">Cuure</strong> · Résiliation en 2 temps : suspension self-serve vs email obligatoire pour résilier</p>
<p class="rank"><strong>03</strong> <strong style="color:var(--cream)">MyProtein</strong> · Prix de base instables qui rendent la remise abo illisible pour le client</p>
</div>

<p class="footer">
benchmark/synthesis_table.html · généré par build_synthesis_table.py · source : benchmark/marques/&lt;brand&gt;/data.json · 8/8 verified_live
</p>

</body>
</html>
"""


def main() -> None:
    brands = load_brands()
    OUT_MD.write_text(build_md(brands), encoding="utf-8")
    print(f"  [ok] {OUT_MD.relative_to(ROOT.parent)}")
    OUT_HTML.write_text(build_html(brands), encoding="utf-8")
    print(f"  [ok] {OUT_HTML.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
