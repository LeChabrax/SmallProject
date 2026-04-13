#!/usr/bin/env python3
"""
Add Hypotheses section to existing HTML report.
Inserts between #reco and #methodology.
"""
import json

with open("benchmark/impulse_products_enriched.json", "r") as f:
    data = json.load(f)

products = data["products"]
go_products = [p for p in products if p["eligibility"] == "GO"]

# ── Product lookup by SKU ──
by_sku = {p["sku"]: p for p in products}

# ══════════════════════════════════════════════════════════════
# CLIENT PROFILES FOR H2 (Custom Box Multi-Frequency)
# ══════════════════════════════════════════════════════════════

PROFILES = {
    "muscu": {
        "name": "💪 Profil Musculation",
        "description": "Pratiquant assidu, 4-5 séances/semaine",
        "items": [
            {"sku": "VSWHEYC", "freq_months": 1, "label": "Whey Isolate Chocolat"},
            {"sku": "VSCREAC", "freq_months": 1, "label": "Créatine Creapure"},
            {"sku": "VSBCAAP", "freq_months": 1, "label": "BCAA Pêche"},
            {"sku": "VSMVIT", "freq_months": 2, "label": "Multivitamines"},
            {"sku": "VSOME", "freq_months": 2, "label": "Omega 3 EPAX"},
            {"sku": "VSLGLU", "freq_months": 2, "label": "L-Glutamine"},
        ]
    },
    "endurance": {
        "name": "🏃 Profil Endurance",
        "description": "Trail/running, 3-4 sorties/semaine",
        "items": [
            {"sku": "VSBOISM", "freq_months": 1, "label": "Boisson effort Menthe"},
            {"sku": "VSELECP", "freq_months": 1, "label": "Électrolytes Pêche"},
            {"sku": "VSMAL", "freq_months": 2, "label": "Maltodextrine"},
            {"sku": "VSMAG", "freq_months": 2, "label": "Magnésium"},
            {"sku": "VSCOLMN", "freq_months": 3, "label": "Collagène Marin Nature"},
            {"sku": "VSVITD", "freq_months": 3, "label": "Vitamine D3"},
        ]
    },
    "sante": {
        "name": "💊 Profil Santé Quotidien",
        "description": "Bien-être général, routine quotidienne",
        "items": [
            {"sku": "VSMVIT", "freq_months": 1, "label": "Multivitamines"},
            {"sku": "VSOME", "freq_months": 1, "label": "Omega 3 EPAX"},
            {"sku": "VSMAG", "freq_months": 1, "label": "Magnésium"},
            {"sku": "VSVITD", "freq_months": 3, "label": "Vitamine D3"},
            {"sku": "VSPBIOT", "freq_months": 2, "label": "Pré-Probiotiques"},
            {"sku": "VSSOM", "freq_months": 2, "label": "Sommeil +"},
        ]
    }
}

# ── H3: Curated Packs ──
CURATED_PACKS = {
    "starter_sante": {
        "name": "Starter Santé",
        "emoji": "💊",
        "items": ["VSMVIT", "VSOME", "VSMAG"],
        "freq": 1,
    },
    "performance_muscu": {
        "name": "Performance Muscu",
        "emoji": "💪",
        "items": ["VSWHEYC", "VSCREAC", "VSBCAAP"],
        "freq": 1,
    },
    "endurance_essentials": {
        "name": "Endurance Essentials",
        "emoji": "🏃",
        "items": ["VSBOISM", "VSELECP", "VSMAG"],
        "freq": 1,
    },
    "bien_etre_complet": {
        "name": "Bien-être Complet",
        "emoji": "🌿",
        "items": ["VSMVIT", "VSOME", "VSMAG", "VSVITD", "VSPBIOT"],
        "freq": 1,
    },
    "recovery_pro": {
        "name": "Recovery Pro",
        "emoji": "🧘",
        "items": ["VSCOLMN", "VSLGLU", "VSMAG"],
        "freq": 1,
    }
}

DISCOUNT = 0.15
SHIPPING_PR = 3.90
SHIPPING_DOM = 5.90

def model_h2_profile(profile):
    """Model a custom box with multi-frequency products."""
    items = profile["items"]
    
    # Calculate over 12 months
    monthly_shipments = {}  # month -> list of items to ship
    annual_cost_full = 0
    annual_cogs = 0
    
    for item in items:
        sku = item["sku"]
        p = by_sku.get(sku)
        if not p:
            continue
        freq = item["freq_months"]
        qty_per_year = 12 // freq
        annual_cost_full += p["retail_price"] * qty_per_year
        annual_cogs += p["cogs_2026"] * qty_per_year
        
        for month in range(1, 13):
            if month % freq == 1 or freq == 1:  # ship in months 1, 1+freq, 1+2*freq...
                if month not in monthly_shipments:
                    monthly_shipments[month] = []
                monthly_shipments[month].append({
                    "sku": sku,
                    "label": item["label"],
                    "price": p["retail_price"],
                    "cogs": p["cogs_2026"]
                })
    
    annual_cost_sub = round(annual_cost_full * (1 - DISCOUNT), 2)
    monthly_payment = round(annual_cost_sub / 12, 2)
    annual_margin = round(annual_cost_sub - annual_cogs, 2)
    
    # Shipping: count actual shipments (months with items)
    num_shipments = len(monthly_shipments)
    annual_shipping_pr = round(num_shipments * SHIPPING_PR, 2)
    annual_net = round(annual_margin - annual_shipping_pr, 2)
    monthly_net = round(annual_net / 12, 2)
    
    # Monthly breakdown
    monthly_detail = []
    for month in range(1, 13):
        items_this_month = monthly_shipments.get(month, [])
        ship_value = sum(i["price"] for i in items_this_month) * (1 - DISCOUNT)
        ship_cogs = sum(i["cogs"] for i in items_this_month)
        shipping = SHIPPING_PR if items_this_month else 0
        net = round(ship_value - ship_cogs - shipping, 2) if items_this_month else 0
        monthly_detail.append({
            "month": month,
            "items": [i["label"] for i in items_this_month],
            "items_count": len(items_this_month),
            "shipment_value": round(ship_value, 2),
            "cogs": round(ship_cogs, 2),
            "shipping": shipping,
            "net_contribution": net,
        })
    
    return {
        "annual_full_price": round(annual_cost_full, 2),
        "annual_sub_price": annual_cost_sub,
        "monthly_payment": monthly_payment,
        "savings_annual": round(annual_cost_full - annual_cost_sub, 2),
        "annual_cogs": round(annual_cogs, 2),
        "annual_margin": annual_margin,
        "num_shipments": num_shipments,
        "annual_shipping_pr": annual_shipping_pr,
        "annual_net_contribution": annual_net,
        "monthly_net_avg": monthly_net,
        "monthly_detail": monthly_detail,
    }


def model_h3_pack(pack):
    """Model a curated pack subscription."""
    items = pack["items"]
    total_price = sum(by_sku[s]["retail_price"] for s in items if s in by_sku)
    total_cogs = sum(by_sku[s]["cogs_2026"] for s in items if s in by_sku)
    sub_price = round(total_price * (1 - DISCOUNT), 2)
    margin = round(sub_price - total_cogs, 2)
    net_pr = round(margin - SHIPPING_PR, 2)
    net_dom = round(margin - SHIPPING_DOM, 2)
    
    # Progressive discount: 15% M1-M3, 17% M4-M6, 20% M7+
    progressive = []
    for period, disc, label in [(3, 0.15, "M1-M3"), (3, 0.17, "M4-M6"), (6, 0.20, "M7-M12")]:
        sp = round(total_price * (1 - disc), 2)
        mg = round(sp - total_cogs, 2)
        nt = round(mg - SHIPPING_PR, 2)
        progressive.append({
            "period": label,
            "months": period,
            "discount": f"{int(disc*100)}%",
            "sub_price": sp,
            "margin": mg,
            "net_pr": nt,
        })
    
    annual_revenue = sum(p["sub_price"] * p["months"] for p in progressive)
    annual_margin = sum(p["margin"] * p["months"] for p in progressive)
    annual_shipping = SHIPPING_PR * 12
    annual_net = round(annual_margin - annual_shipping, 2)
    
    return {
        "full_price": round(total_price, 2),
        "sub_price_15": sub_price,
        "cogs": round(total_cogs, 2),
        "margin_15": margin,
        "net_pr_15": net_pr,
        "net_dom_15": net_dom,
        "margin_pct": round((margin / sub_price) * 100, 1) if sub_price > 0 else 0,
        "progressive": progressive,
        "annual_revenue_progressive": round(annual_revenue, 2),
        "annual_net_progressive": annual_net,
        "products": [by_sku[s]["title"] for s in items if s in by_sku],
    }


# ══════════════════════════════════════════════════════════════
# BUILD HTML SECTION
# ══════════════════════════════════════════════════════════════

def build_hypotheses_html():
    html = '''
<!-- ═══════════════════════════════════════════════════════════ -->
<!-- HYPOTHÈSES STRATÉGIQUES — Ajouté au rapport existant       -->
<!-- ═══════════════════════════════════════════════════════════ -->

<section id="hypotheses" style="margin-top:48px">
<h2>🧪 Hypothèses Stratégiques — Modèles d'Abonnement</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:24px">
    4 hypothèses de modèle d'abonnement évaluées. Chaque hypothèse est modélisée avec des profils clients types et une analyse économique complète.
</p>

<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:32px">
    <a href="#h1" style="text-decoration:none;padding:16px;border:2px solid var(--border);border-radius:12px;text-align:center;transition:all 0.2s" onmouseover="this.style.borderColor='var(--orange)'" onmouseout="this.style.borderColor='var(--border)'">
        <div style="font-size:24px">📦</div>
        <div style="font-weight:700;color:var(--marine);font-size:14px;margin-top:4px">H1 : Subscribe & Save</div>
        <div style="font-size:11px;color:var(--muted)">Classique, 1 produit = 1 abo</div>
    </a>
    <a href="#h2" style="text-decoration:none;padding:16px;border:2px solid var(--orange);border-radius:12px;text-align:center;background:linear-gradient(135deg,#fff5f0,white)">
        <div style="font-size:24px">🎨</div>
        <div style="font-weight:700;color:var(--orange);font-size:14px;margin-top:4px">H2 : Box Custom ⭐</div>
        <div style="font-size:11px;color:var(--muted)">Multi-fréquence + paiement lissé</div>
    </a>
    <a href="#h3" style="text-decoration:none;padding:16px;border:2px solid var(--border);border-radius:12px;text-align:center">
        <div style="font-size:24px">🎁</div>
        <div style="font-weight:700;color:var(--marine);font-size:14px;margin-top:4px">H3 : Packs Curatés</div>
        <div style="font-size:11px;color:var(--muted)">Pré-composés, remise progressive</div>
    </a>
    <a href="#h4" style="text-decoration:none;padding:16px;border:2px solid var(--border);border-radius:12px;text-align:center">
        <div style="font-size:24px">🔄</div>
        <div style="font-weight:700;color:var(--marine);font-size:14px;margin-top:4px">H4 : Hybride</div>
        <div style="font-size:11px;color:var(--muted)">Curated → Custom progressif</div>
    </a>
</div>

<!-- ═══ H1: SUBSCRIBE & SAVE CLASSIQUE ═══ -->
<div class="card" id="h1" style="border-left:4px solid var(--marine)">
<h3 style="color:var(--marine)">📦 Hypothèse 1 : Subscribe & Save Classique</h3>
<p style="font-size:13px;color:var(--muted);margin-bottom:16px">
    Le modèle standard du marché. Chaque produit a son propre abonnement indépendant avec une fréquence au choix.
</p>

<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px">
    <div style="background:#f1f5f9;padding:12px;border-radius:8px;text-align:center">
        <div style="font-size:11px;color:var(--muted)">Remise</div>
        <div style="font-size:20px;font-weight:800;color:var(--marine)">-15%</div>
    </div>
    <div style="background:#f1f5f9;padding:12px;border-radius:8px;text-align:center">
        <div style="font-size:11px;color:var(--muted)">Fréquences</div>
        <div style="font-size:20px;font-weight:800;color:var(--marine)">1/2/3 mois</div>
    </div>
    <div style="background:#f1f5f9;padding:12px;border-radius:8px;text-align:center">
        <div style="font-size:11px;color:var(--muted)">Engagement</div>
        <div style="font-size:20px;font-weight:800;color:var(--marine)">Sans</div>
    </div>
    <div style="background:#f1f5f9;padding:12px;border-radius:8px;text-align:center">
        <div style="font-size:11px;color:var(--muted)">Livraison offerte</div>
        <div style="font-size:20px;font-weight:800;color:var(--marine)">≥ 25€ PR</div>
    </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div>
        <h4 style="color:var(--green);font-size:13px;margin-bottom:8px">✅ Avantages</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li>Simple à mettre en place (apps Shopify existantes : Recharge, Loop, Skio)</li>
            <li>Familier pour le consommateur (modèle MyProtein, Nutri&Co)</li>
            <li>25 produits éligibles immédiatement</li>
            <li>Contribution nette moyenne de ~10€/abo/mois</li>
            <li>Pas de gestion de stock complexe</li>
        </ul>
    </div>
    <div>
        <h4 style="color:var(--red);font-size:13px;margin-bottom:8px">❌ Inconvénients</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li>Chaque produit = 1 expédition = 1 frais de port (pas d'optimisation logistique)</li>
            <li>Pas de cross-sell naturel (le client reste sur 1 produit)</li>
            <li>Faible ticket moyen (souvent 1 seul produit ~15-25€)</li>
            <li>Churn élevé (le client ne s'attache qu'à 1 produit)</li>
        </ul>
    </div>
</div>
<div style="margin-top:12px;padding:8px 12px;background:#f8fafc;border-radius:6px;font-size:12px">
    <strong>Complexité technique :</strong> ⭐ Faible — App Shopify plug & play (~50€/mois)
</div>
</div>

<!-- ═══ H2: BOX CUSTOM MULTI-FRÉQUENCE ═══ -->
<div class="card" id="h2" style="border-left:4px solid var(--orange);background:linear-gradient(135deg,#fffaf7,white)">
<h3 style="color:var(--orange)">🎨 Hypothèse 2 : Box Custom Multi-Fréquence ⭐ <span style="background:var(--orange);color:white;padding:2px 8px;border-radius:4px;font-size:11px;vertical-align:middle">RECOMMANDÉE</span></h3>
<p style="font-size:13px;color:var(--muted);margin-bottom:16px">
    Le client compose sa box personnalisée avec des fréquences différentes par produit.<br>
    <strong>Innovation clé :</strong> paiement lissé mensuellement, même si certains produits sont livrés tous les 2 ou 3 mois.
</p>

<div style="background:var(--marine);color:white;padding:16px;border-radius:8px;margin-bottom:16px">
    <div style="font-size:12px;opacity:0.7;margin-bottom:8px">💡 CONCEPT</div>
    <div style="font-size:14px;line-height:1.6">
        Le client choisit : <strong>"Whey chaque mois + Créatine chaque mois + Vitamines tous les 3 mois"</strong>.<br>
        Le système calcule le <strong>coût annuel total</strong>, applique la remise, et divise en <strong>12 mensualités égales</strong>.<br>
        Chaque mois, on expédie uniquement les produits dus → <strong>optimisation logistique naturelle</strong>.
    </div>
</div>'''

    # Model the 3 profiles
    for profile_key, profile in PROFILES.items():
        model = model_h2_profile(profile)
        
        html += f'''
<div style="margin-bottom:24px;padding:20px;background:#f8fafc;border-radius:12px;border:1px solid var(--border)">
<h4 style="margin-bottom:4px">{profile["name"]}</h4>
<p style="font-size:12px;color:var(--muted);margin-bottom:12px">{profile["description"]}</p>

<table style="font-size:12px;margin-bottom:12px">
<thead>
<tr style="background:var(--marine)">
    <th style="color:white;padding:6px 8px">Produit</th>
    <th style="color:white;padding:6px 8px;text-align:center">Fréquence</th>
    <th style="color:white;padding:6px 8px;text-align:right">Prix unitaire</th>
    <th style="color:white;padding:6px 8px;text-align:right">Qté/an</th>
    <th style="color:white;padding:6px 8px;text-align:right">Coût/an</th>
</tr>
</thead>
<tbody>'''
        
        for item in profile["items"]:
            p = by_sku.get(item["sku"])
            if not p:
                continue
            qty = 12 // item["freq_months"]
            annual = p["retail_price"] * qty
            freq_label = f'Chaque mois' if item["freq_months"] == 1 else f'Tous les {item["freq_months"]} mois'
            freq_color = "#22c55e" if item["freq_months"] == 1 else "#f59e0b" if item["freq_months"] == 2 else "#3b82f6"
            html += f'''<tr>
    <td style="font-weight:500">{item["label"]}</td>
    <td style="text-align:center"><span style="background:{freq_color};color:white;padding:1px 6px;border-radius:3px;font-size:10px">{freq_label}</span></td>
    <td style="text-align:right">{p["retail_price"]:.2f}€</td>
    <td style="text-align:center">{qty}×</td>
    <td style="text-align:right">{annual:.2f}€</td>
</tr>'''
        
        html += f'''</tbody>
</table>

<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px">
    <div style="background:white;padding:10px;border-radius:6px;text-align:center;border:1px solid var(--border)">
        <div style="font-size:10px;color:var(--muted)">Prix plein/an</div>
        <div style="font-size:16px;font-weight:700;color:var(--muted);text-decoration:line-through">{model["annual_full_price"]:.0f}€</div>
    </div>
    <div style="background:white;padding:10px;border-radius:6px;text-align:center;border:1px solid var(--border)">
        <div style="font-size:10px;color:var(--muted)">Prix abo/an (-15%)</div>
        <div style="font-size:16px;font-weight:700;color:var(--orange)">{model["annual_sub_price"]:.0f}€</div>
    </div>
    <div style="background:var(--orange);padding:10px;border-radius:6px;text-align:center;color:white">
        <div style="font-size:10px;opacity:0.8">Mensualité</div>
        <div style="font-size:20px;font-weight:800">{model["monthly_payment"]:.2f}€</div>
    </div>
    <div style="background:white;padding:10px;border-radius:6px;text-align:center;border:1px solid var(--border)">
        <div style="font-size:10px;color:var(--muted)">Économie/an</div>
        <div style="font-size:16px;font-weight:700;color:var(--green)">{model["savings_annual"]:.0f}€</div>
    </div>
    <div style="background:white;padding:10px;border-radius:6px;text-align:center;border:1px solid var(--border)">
        <div style="font-size:10px;color:var(--muted)">Expéditions/an</div>
        <div style="font-size:16px;font-weight:700;color:var(--marine)">{model["num_shipments"]}</div>
    </div>
</div>

<!-- Monthly timeline -->
<div style="margin-top:12px">
<div style="font-size:11px;font-weight:600;color:var(--marine);margin-bottom:6px">📅 Calendrier des expéditions sur 12 mois :</div>
<div style="display:grid;grid-template-columns:repeat(12,1fr);gap:3px">'''
        
        for md in model["monthly_detail"]:
            count = md["items_count"]
            if count == 0:
                bg = "#f1f5f9"
                txt = "—"
                fc = "var(--muted)"
            elif count <= 2:
                bg = "#dcfce7"
                txt = f'{count}p'
                fc = "#166534"
            elif count <= 4:
                bg = "#fef3c7"
                txt = f'{count}p'
                fc = "#92400e"
            else:
                bg = "#fed7aa"
                txt = f'{count}p'
                fc = "#9a3412"
            
            html += f'''<div style="background:{bg};padding:4px;border-radius:4px;text-align:center;font-size:10px">
    <div style="color:var(--muted);font-size:8px">M{md["month"]}</div>
    <div style="font-weight:700;color:{fc}">{txt}</div>
</div>'''
        
        html += f'''</div>
</div>

<div style="margin-top:8px;display:grid;grid-template-columns:1fr 1fr;gap:8px">
    <div style="font-size:11px;color:var(--muted)">
        💰 Marge nette annuelle (après port PR) : <strong style="color:var(--green)">{model["annual_net_contribution"]:.2f}€</strong>
    </div>
    <div style="font-size:11px;color:var(--muted)">
        📊 Contribution nette moyenne/mois : <strong style="color:var(--marine)">{model["monthly_net_avg"]:.2f}€</strong>
    </div>
</div>
</div>'''
    
    # H2 pros/cons
    html += '''
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px">
    <div>
        <h4 style="color:var(--green);font-size:13px;margin-bottom:8px">✅ Avantages</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li><strong>Ticket moyen élevé</strong> : 40-80€/mois vs 15-25€ en S&S classique</li>
            <li><strong>Paiement lissé</strong> : mensualités fixes = prévisibilité client + trésorerie régulière</li>
            <li><strong>Cross-sell intégré</strong> : le client découvre de nouveaux produits naturellement</li>
            <li><strong>Optimisation logistique</strong> : on regroupe les produits → moins d'expéditions par produit</li>
            <li><strong>Rétention supérieure</strong> : multi-produit = plus dur de quitter (switching cost)</li>
            <li><strong>Différenciation</strong> : aucun concurrent FR ne propose ce modèle</li>
        </ul>
    </div>
    <div>
        <h4 style="color:var(--red);font-size:13px;margin-bottom:8px">❌ Inconvénients</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li><strong>Complexité technique</strong> : pas d'app Shopify standard pour ça → dev custom ou Recharge + Bundles</li>
            <li><strong>Gestion logistique</strong> : colis de taille variable chaque mois</li>
            <li><strong>Paiement échelonné</strong> : engagement implicite du client (risque de litige si annulation mid-cycle)</li>
            <li><strong>UX complexe</strong> : builder de box = parcours client plus long</li>
            <li><strong>Support client</strong> : plus de questions sur "qu'est-ce que je reçois ce mois-ci ?"</li>
        </ul>
    </div>
</div>
<div style="margin-top:12px;padding:8px 12px;background:#fff5f0;border-radius:6px;font-size:12px;border:1px solid #fed7aa">
    <strong>Complexité technique :</strong> ⭐⭐⭐ Élevée — Dev custom nécessaire ou Recharge Advanced + Bold Bundles (~150-300€/mois)
</div>
</div>

<!-- ═══ H3: PACKS CURATÉS ═══ -->
<div class="card" id="h3" style="border-left:4px solid #8b5cf6">
<h3 style="color:#8b5cf6">🎁 Hypothèse 3 : Packs Curatés avec Remise Progressive</h3>
<p style="font-size:13px;color:var(--muted);margin-bottom:16px">
    Des packs pré-composés par usage, en abonnement mensuel. La remise augmente avec la fidélité : 15% → 17% → 20%.
</p>

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px">'''
    
    for pack_key, pack in CURATED_PACKS.items():
        model = model_h3_pack(pack)
        html += f'''
<div style="background:#f8fafc;padding:16px;border-radius:8px;border:1px solid var(--border)">
    <div style="font-size:18px;margin-bottom:4px">{pack["emoji"]} <strong>{pack["name"]}</strong></div>
    <div style="font-size:11px;color:var(--muted);margin-bottom:8px">{" + ".join(model["products"])}</div>
    
    <table style="font-size:11px;width:100%">
    <tr><td>Prix plein</td><td style="text-align:right;text-decoration:line-through;color:var(--muted)">{model["full_price"]:.2f}€</td></tr>
    <tr><td>M1-M3 (-15%)</td><td style="text-align:right;font-weight:600">{model["progressive"][0]["sub_price"]:.2f}€</td></tr>
    <tr><td>M4-M6 (-17%)</td><td style="text-align:right;font-weight:600">{model["progressive"][1]["sub_price"]:.2f}€</td></tr>
    <tr><td>M7-M12 (-20%)</td><td style="text-align:right;font-weight:600;color:var(--orange)">{model["progressive"][2]["sub_price"]:.2f}€</td></tr>
    <tr style="border-top:1px solid var(--border)"><td>Net PR (M1-M3)</td><td style="text-align:right;font-weight:700;color:{"var(--green)" if model["net_pr_15"] >= 3 else "var(--amber)"}">{model["net_pr_15"]:.2f}€</td></tr>
    <tr><td>CA annuel progressif</td><td style="text-align:right;font-weight:700;color:var(--marine)">{model["annual_revenue_progressive"]:.0f}€</td></tr>
    </table>
</div>'''
    
    html += '''</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px">
    <div>
        <h4 style="color:var(--green);font-size:13px;margin-bottom:8px">✅ Avantages</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li><strong>Simple à comprendre</strong> : le client choisit 1 pack, c'est tout</li>
            <li><strong>Remise progressive = rétention</strong> : plus tu restes, plus tu économises</li>
            <li><strong>Cross-sell intégré</strong> : le client découvre des produits qu'il n'aurait pas achetés seul</li>
            <li><strong>Logistique prévisible</strong> : même colis chaque mois</li>
            <li><strong>Ticket moyen élevé</strong> : 45-80€/pack vs 15-25€ en S&S</li>
        </ul>
    </div>
    <div>
        <h4 style="color:var(--red);font-size:13px;margin-bottom:8px">❌ Inconvénients</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li>Pas de personnalisation → frustration si 1 produit ne plaît pas</li>
            <li>La remise progressive érode la marge à long terme</li>
            <li>Besoin de créer les packs "justes" (risque de mauvaise composition)</li>
            <li>Moins flexible que H2</li>
        </ul>
    </div>
</div>
<div style="margin-top:12px;padding:8px 12px;background:#f3f0ff;border-radius:6px;font-size:12px;border:1px solid #c4b5fd">
    <strong>Complexité technique :</strong> ⭐⭐ Moyenne — Recharge + Bundles existants, config ~2-3 jours
</div>
</div>

<!-- ═══ H4: HYBRIDE ═══ -->
<div class="card" id="h4" style="border-left:4px solid #0ea5e9">
<h3 style="color:#0ea5e9">🔄 Hypothèse 4 : Modèle Hybride Progressif</h3>
<p style="font-size:13px;color:var(--muted);margin-bottom:16px">
    Combiner le meilleur de H1/H2/H3 : démarrage simple, puis personnalisation croissante avec la fidélité.
</p>

<div style="position:relative;padding:20px 0">
    <!-- Timeline -->
    <div style="position:absolute;top:50%;left:0;right:0;height:4px;background:linear-gradient(to right,#0ea5e9,var(--orange),var(--green));border-radius:2px"></div>
    
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;position:relative">
        <div style="background:white;padding:16px;border-radius:12px;border:2px solid #0ea5e9;text-align:center">
            <div style="background:#0ea5e9;color:white;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-weight:800">1</div>
            <div style="font-weight:700;color:var(--marine);font-size:13px">Phase 1 : Onboarding</div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">Mois 1-3</div>
            <div style="font-size:12px;margin-top:8px;text-align:left;color:var(--text)">
                • Choix parmi 5 packs curatés<br>
                • Remise -15% fixe<br>
                • Livraison PR offerte<br>
                • 1 shaker offert à l'inscription
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:12px;border:2px solid var(--orange);text-align:center">
            <div style="background:var(--orange);color:white;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-weight:800">2</div>
            <div style="font-weight:700;color:var(--marine);font-size:13px">Phase 2 : Personnalisation</div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">Mois 4-6</div>
            <div style="font-size:12px;margin-top:8px;text-align:left;color:var(--text)">
                • Déblocage du "builder" custom<br>
                • Ajout/retrait de produits au pack<br>
                • Remise monte à -17%<br>
                • Choix de fréquences par produit
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:12px;border:2px solid var(--green);text-align:center">
            <div style="background:var(--green);color:white;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-weight:800">3</div>
            <div style="font-weight:700;color:var(--marine);font-size:13px">Phase 3 : Full Custom</div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">Mois 7+</div>
            <div style="font-size:12px;margin-top:8px;text-align:left;color:var(--text)">
                • Box 100% personnalisable<br>
                • Fréquences indépendantes/produit<br>
                • Paiement lissé mensuel<br>
                • Remise -20% + livraison dom offerte
            </div>
        </div>
    </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px">
    <div>
        <h4 style="color:var(--green);font-size:13px;margin-bottom:8px">✅ Avantages</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li><strong>Onboarding simple</strong> : pas de paralysie du choix au début</li>
            <li><strong>Gamification naturelle</strong> : le client "débloque" des features</li>
            <li><strong>Rétention maximale</strong> : switching cost croissant + remise croissante</li>
            <li><strong>Data progressive</strong> : on apprend les préférences client avant d'ouvrir la custom</li>
            <li><strong>Marge protégée</strong> : la remise max (-20%) n'est atteinte qu'à M7+ (clients fidèles = LTV élevée)</li>
        </ul>
    </div>
    <div>
        <h4 style="color:var(--red);font-size:13px;margin-bottom:8px">❌ Inconvénients</h4>
        <ul style="font-size:12px;color:var(--muted);padding-left:16px">
            <li><strong>Complexité technique maximale</strong> : 3 expériences à développer</li>
            <li><strong>Communication complexe</strong> : expliquer le système en 3 phases</li>
            <li><strong>Frustration potentielle</strong> : "pourquoi je ne peux pas customiser tout de suite ?"</li>
            <li><strong>Coût de développement</strong> : 3-6 mois de dev, ~5000-10000€</li>
        </ul>
    </div>
</div>
<div style="margin-top:12px;padding:8px 12px;background:#ecfeff;border-radius:6px;font-size:12px;border:1px solid #a5f3fc">
    <strong>Complexité technique :</strong> ⭐⭐⭐⭐ Très élevée — Dev custom + Recharge Advanced + logique de progression (~5-10K€)
</div>
</div>

<!-- ═══ COMPARATIF DES HYPOTHÈSES ═══ -->
<div class="card" style="margin-top:24px">
<h3 style="color:var(--marine)">📊 Tableau Comparatif des 4 Hypothèses</h3>
<div style="overflow-x:auto">
<table>
<thead>
<tr>
    <th>Critère</th>
    <th style="text-align:center;background:var(--marine)">H1 : S&S Classique</th>
    <th style="text-align:center;background:var(--orange)">H2 : Box Custom ⭐</th>
    <th style="text-align:center;background:#8b5cf6">H3 : Packs Curatés</th>
    <th style="text-align:center;background:#0ea5e9">H4 : Hybride</th>
</tr>
</thead>
<tbody>
<tr>
    <td style="font-weight:600">Ticket moyen/mois</td>
    <td style="text-align:center">15-25€</td>
    <td style="text-align:center;font-weight:700;color:var(--orange)">40-80€</td>
    <td style="text-align:center">45-70€</td>
    <td style="text-align:center">45-80€</td>
</tr>
<tr>
    <td style="font-weight:600">Marge nette/abo/mois (PR)</td>
    <td style="text-align:center">~10€</td>
    <td style="text-align:center;font-weight:700;color:var(--orange)">~15-25€</td>
    <td style="text-align:center">~12-20€</td>
    <td style="text-align:center">~12-25€</td>
</tr>
<tr>
    <td style="font-weight:600">Rétention estimée</td>
    <td style="text-align:center">25-35%/an</td>
    <td style="text-align:center;font-weight:700;color:var(--orange)">40-55%/an</td>
    <td style="text-align:center">35-45%/an</td>
    <td style="text-align:center">45-60%/an</td>
</tr>
<tr>
    <td style="font-weight:600">Cross-sell</td>
    <td style="text-align:center">❌ Faible</td>
    <td style="text-align:center">✅ Fort</td>
    <td style="text-align:center">✅ Fort</td>
    <td style="text-align:center">✅✅ Très fort</td>
</tr>
<tr>
    <td style="font-weight:600">Coût de mise en place</td>
    <td style="text-align:center;color:var(--green)">500-1000€</td>
    <td style="text-align:center;color:var(--amber)">3000-5000€</td>
    <td style="text-align:center;color:var(--green)">1000-2000€</td>
    <td style="text-align:center;color:var(--red)">5000-10000€</td>
</tr>
<tr>
    <td style="font-weight:600">Time to market</td>
    <td style="text-align:center;color:var(--green)">1-2 semaines</td>
    <td style="text-align:center;color:var(--amber)">1-2 mois</td>
    <td style="text-align:center;color:var(--green)">2-3 semaines</td>
    <td style="text-align:center;color:var(--red)">3-6 mois</td>
</tr>
<tr>
    <td style="font-weight:600">Différenciation marché</td>
    <td style="text-align:center">❌ Standard</td>
    <td style="text-align:center;font-weight:700;color:var(--orange)">✅✅ Unique</td>
    <td style="text-align:center">⚡ Moyen</td>
    <td style="text-align:center">✅✅ Unique</td>
</tr>
<tr style="background:#f8fafc;font-weight:700">
    <td>NOTE GLOBALE</td>
    <td style="text-align:center">⭐⭐⭐</td>
    <td style="text-align:center;color:var(--orange);font-size:16px">⭐⭐⭐⭐⭐</td>
    <td style="text-align:center">⭐⭐⭐⭐</td>
    <td style="text-align:center">⭐⭐⭐⭐</td>
</tr>
</tbody>
</table>
</div>
</div>

<!-- ═══ RECOMMANDATION STRATÉGIQUE ═══ -->
<div style="background:linear-gradient(135deg,var(--marine) 0%,#2d3f5e 100%);color:white;border-radius:12px;padding:32px;margin-top:24px">
<h3 style="color:var(--orange);margin-top:0">🎯 Recommandation Stratégique : Déploiement en 2 phases</h3>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:16px">
    <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:20px">
        <div style="font-size:12px;opacity:0.7">PHASE 1 — Lancement immédiat</div>
        <div style="font-size:18px;font-weight:700;margin:8px 0">H1 + H3 combinés</div>
        <ul style="font-size:12px;opacity:0.85;padding-left:16px">
            <li>Subscribe & Save sur les 25 produits GO</li>
            <li>5 packs curatés en abonnement</li>
            <li>Remise 15%, sans engagement</li>
            <li>PR offert ≥ 25€</li>
            <li><strong>Budget : 1000-2000€ • Délai : 2-3 semaines</strong></li>
        </ul>
    </div>
    <div style="background:rgba(240,90,40,0.2);border-radius:8px;padding:20px;border:1px solid rgba(240,90,40,0.4)">
        <div style="font-size:12px;color:var(--orange)">PHASE 2 — Après validation (M3-M6)</div>
        <div style="font-size:18px;font-weight:700;margin:8px 0">H2 : Box Custom Builder</div>
        <ul style="font-size:12px;opacity:0.85;padding-left:16px">
            <li>Builder de box multi-fréquence</li>
            <li>Paiement lissé mensuel</li>
            <li>Remise progressive (15% → 20%)</li>
            <li>Ouvert aux abonnés existants + nouveaux</li>
            <li><strong>Budget : 3000-5000€ • Délai : 1-2 mois</strong></li>
        </ul>
    </div>
</div>
<p style="font-size:12px;opacity:0.7;margin-top:16px;text-align:center">
    Phase 1 valide le concept et génère les premiers abonnés. Phase 2 apporte la différenciation et maximise le ticket moyen.
</p>
</div>

</section>'''
    
    return html


# ══════════════════════════════════════════════════════════════
# INJECT INTO EXISTING HTML
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    hypotheses_html = build_hypotheses_html()
    
    with open("benchmark/rapport_rentabilite_abonnement.html", "r", encoding="utf-8") as f:
        full_html = f.read()
    
    # Add nav link
    nav_addition = '    <a href="#hypotheses">🧪 Hypothèses</a>\n'
    full_html = full_html.replace(
        '<a href="#methodology">�� Méthodologie</a>',
        '<a href="#hypotheses">🧪 Hypothèses</a>\n    <a href="#methodology">📋 Méthodologie</a>'
    )
    
    # Insert hypotheses section before methodology
    insertion_point = '<section id="methodology">'
    full_html = full_html.replace(
        insertion_point,
        hypotheses_html + '\n\n' + insertion_point
    )
    
    with open("benchmark/rapport_rentabilite_abonnement.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print("✅ Section Hypothèses ajoutée au rapport HTML")
    print(f"   Fichier : benchmark/rapport_rentabilite_abonnement.html")
    
    # Profile summaries
    for pk, profile in PROFILES.items():
        model = model_h2_profile(profile)
        print(f"\n   {profile['name']}:")
        print(f"     Mensualité : {model['monthly_payment']:.2f}€/mois")
        print(f"     Économie/an : {model['savings_annual']:.0f}€")
        print(f"     Marge nette/an : {model['annual_net_contribution']:.2f}€")
        print(f"     Expéditions/an : {model['num_shipments']}")
