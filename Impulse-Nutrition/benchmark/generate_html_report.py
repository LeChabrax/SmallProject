#!/usr/bin/env python3
"""
Generate a comprehensive HTML report for Impulse Nutrition subscription analysis.
T2: Profitability model
T3: Subscription scoring
T4: Business metrics
T5: HTML generation
"""
import json
import math
from datetime import datetime

# ── Load data ──
with open("benchmark/impulse_products.json", "r") as f:
    data = json.load(f)

products = data["products"]
meta = data["meta"]

with open("benchmark/master_data.json", "r") as f:
    master = json.load(f)

# ── Constants ──
LOGISTICS = {"point_relais": 3.90, "domicile": 5.90, "express": 10.90}
DISCOUNTS = [0.10, 0.15, 0.20]
CHURN_RATES = [0.08, 0.10, 0.15]  # monthly
CONVERSION_RATES = [0.05, 0.10, 0.20]  # % of one-shot converting to sub

# ══════════════════════════════════════════════════════════════
# T2: PROFITABILITY MODEL
# ══════════════════════════════════════════════════════════════

def compute_profitability(products):
    for p in products:
        retail = p["retail_price"]
        cogs = p["cogs_2026"]
        scenarios = {}
        
        for disc in DISCOUNTS:
            disc_key = f"{int(disc*100)}pct"
            sub_price = round(retail * (1 - disc), 2)
            margin_after_disc = round(sub_price - cogs, 2)
            margin_pct_after_disc = round((margin_after_disc / sub_price) * 100, 1) if sub_price > 0 else 0
            
            logistics_scenarios = {}
            for lname, lcost in LOGISTICS.items():
                net_contribution = round(margin_after_disc - lcost, 2)
                status = "rentable" if net_contribution >= 3.0 else ("marginal" if net_contribution >= 0 else "déficitaire")
                logistics_scenarios[lname] = {
                    "shipping_cost": lcost,
                    "net_contribution": net_contribution,
                    "status": status,
                    "min_qty_for_viability": max(1, math.ceil(lcost / margin_after_disc)) if margin_after_disc > 0 else 999
                }
            
            scenarios[disc_key] = {
                "discount_pct": int(disc * 100),
                "sub_price": sub_price,
                "margin_after_discount": margin_after_disc,
                "margin_pct_after_discount": margin_pct_after_disc,
                "logistics": logistics_scenarios
            }
        
        # Break-even basket (minimum basket to cover shipping with 10% discount)
        margin_ratio = (p["gross_margin"] / retail) if retail > 0 else 0
        p["break_even_basket"] = {}
        for lname, lcost in LOGISTICS.items():
            # basket * (1-disc) * margin_ratio >= lcost
            # basket >= lcost / ((1-disc) * margin_ratio)
            for disc in DISCOUNTS:
                disc_key = f"{int(disc*100)}pct"
                effective_margin_ratio = (1 - disc) * margin_ratio
                if effective_margin_ratio > 0:
                    min_basket = round(lcost / effective_margin_ratio, 2)
                else:
                    min_basket = 999
                p["break_even_basket"][f"{lname}_{disc_key}"] = min_basket
        
        p["scenarios"] = scenarios
    return products


# ══════════════════════════════════════════════════════════════
# T3: SUBSCRIPTION SCORING
# ══════════════════════════════════════════════════════════════

def compute_subscription_score(products):
    for p in products:
        score = 0
        details = {}
        
        # 1. Recurrence (0-30 pts)
        rec = p["recurrence_score"]
        rec_pts = round(rec * 0.30)
        details["recurrence"] = {"raw": rec, "pts": rec_pts, "max": 30}
        score += rec_pts
        
        # 2. Margin viability (0-25 pts) — based on net contribution at 15% disc, point relais
        net_15_pr = p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        if net_15_pr >= 8:
            margin_pts = 25
        elif net_15_pr >= 5:
            margin_pts = 20
        elif net_15_pr >= 3:
            margin_pts = 15
        elif net_15_pr >= 0:
            margin_pts = 8
        else:
            margin_pts = 0
        details["margin_viability"] = {"net_contribution_15pct_pr": net_15_pr, "pts": margin_pts, "max": 25}
        score += margin_pts
        
        # 3. SKU complexity (0-15 pts) — fewer variants = easier to manage
        variants = p["sku_variants"]
        if variants == 1:
            sku_pts = 15
        elif variants == 2:
            sku_pts = 10
        else:
            sku_pts = 5
        details["sku_complexity"] = {"variants": variants, "pts": sku_pts, "max": 15}
        score += sku_pts
        
        # 4. Competitor validation (0-15 pts)
        comp_pts = 15 if p["competitor_has_sub"] else 3
        details["competitor_presence"] = {"has_sub": p["competitor_has_sub"], "pts": comp_pts, "max": 15}
        score += comp_pts
        
        # 5. Stock / demand signal (0-10 pts)
        stock = p["stock"]
        # High stock = high demand product (they order more) — but also could mean slow seller
        # Use as a proxy: 300+ = good seller
        if stock >= 500:
            stock_pts = 10
        elif stock >= 300:
            stock_pts = 7
        elif stock >= 100:
            stock_pts = 4
        else:
            stock_pts = 2
        details["demand_signal"] = {"stock": stock, "pts": stock_pts, "max": 10}
        score += stock_pts
        
        # 6. Category fit (0-5 pts)
        cat = p["category"]
        if cat == "sante":
            cat_pts = 5   # daily health = best for subscription
        elif cat == "sport":
            cat_pts = 3   # sport = good but more variable
        else:
            cat_pts = 0   # accessoire = not suitable
        details["category_fit"] = {"category": cat, "pts": cat_pts, "max": 5}
        score += cat_pts
        
        p["subscription_score"] = min(score, 100)
        p["subscription_score_details"] = details
        
        # Eligibility verdict
        if score >= 75:
            p["eligibility"] = "GO"
        elif score >= 55:
            p["eligibility"] = "MAYBE"
        else:
            p["eligibility"] = "NO-GO"
    
    return products


# ══════════════════════════════════════════════════════════════
# T4: BUSINESS METRICS
# ══════════════════════════════════════════════════════════════

def compute_business_metrics(products):
    metrics = {}
    
    # Filter eligible products only for projections
    go_products = [p for p in products if p["eligibility"] == "GO"]
    maybe_products = [p for p in products if p["eligibility"] == "MAYBE"]
    eligible = go_products + maybe_products
    
    # ── Average ticket for eligible products ──
    avg_price_go = sum(p["retail_price"] for p in go_products) / len(go_products) if go_products else 0
    avg_price_eligible = sum(p["retail_price"] for p in eligible) / len(eligible) if eligible else 0
    avg_margin_go = sum(p["gross_margin_pct"] for p in go_products) / len(go_products) if go_products else 0
    
    metrics["portfolio"] = {
        "total_products": len(products),
        "go_count": len(go_products),
        "maybe_count": len(maybe_products),
        "nogo_count": len([p for p in products if p["eligibility"] == "NO-GO"]),
        "avg_price_go": round(avg_price_go, 2),
        "avg_price_eligible": round(avg_price_eligible, 2),
        "avg_margin_pct_go": round(avg_margin_go, 1),
        "go_products": [p["sku"] for p in go_products],
        "maybe_products": [p["sku"] for p in maybe_products],
    }
    
    # ── LTV projections ──
    # Assume avg basket = 2 products at avg eligible price
    avg_basket_1p = round(avg_price_go, 2)
    avg_basket_2p = round(avg_price_go * 2, 2)
    avg_basket_3p = round(avg_price_go * 3, 2)
    
    ltv_scenarios = {}
    for basket_label, basket_value in [("1_produit", avg_basket_1p), ("2_produits", avg_basket_2p), ("3_produits", avg_basket_3p)]:
        for churn in CHURN_RATES:
            churn_key = f"churn_{int(churn*100)}pct"
            # LTV = basket / churn (geometric series)
            avg_lifetime_months = 1 / churn
            ltv = round(basket_value * avg_lifetime_months, 2)
            # Discounted LTV (with -15% subscription discount)
            ltv_discounted = round(basket_value * 0.85 * avg_lifetime_months, 2)
            
            # Cohort simulation: 100 subscribers over 12 months
            cohort_revenue = []
            remaining = 100
            cumulative = 0
            for month in range(1, 13):
                month_revenue = round(remaining * basket_value * 0.85, 2)  # 15% discount
                cumulative += month_revenue
                remaining = round(remaining * (1 - churn), 1)
                cohort_revenue.append({
                    "month": month,
                    "subscribers": round(remaining, 1),
                    "month_revenue": month_revenue,
                    "cumulative_revenue": round(cumulative, 2)
                })
            
            ltv_scenarios[f"{basket_label}_{churn_key}"] = {
                "basket": basket_value,
                "churn_monthly": churn,
                "avg_lifetime_months": round(avg_lifetime_months, 1),
                "ltv_full_price": round(basket_value * avg_lifetime_months, 2),
                "ltv_sub_price": ltv_discounted,
                "cohort_100": cohort_revenue
            }
    
    metrics["ltv"] = ltv_scenarios
    
    # ── Cross-sell matrix (from existing packs) ──
    # Analyze which products are bundled together in Shopify packs
    cross_sell = {
        "musculation": ["VSWHEYN/C/V", "VSCREAC", "VSBCAAC/P", "VSPREWC", "VSLGLU"],
        "endurance": ["VSBOISM/F", "VSELECC/P", "VSMAL", "VSBCAAC/P", "VSMAG"],
        "sante_quotidien": ["VSMVIT", "VSOME", "VSMAG", "VSVITD", "VSVITC"],
        "recuperation": ["VSCOLMN/MC/ME", "VSLGLU", "VSMAG", "VSBCAAC/P"],
        "os_articulations": ["VSCOLBN/BC/BE", "VSCUR", "VSVITD"],
        "sommeil_fatigue": ["VSSOM", "VSMAG", "VSGLY"],
    }
    
    # Bundle suggestions for subscription
    bundle_suggestions = []
    for bundle_name, skus_raw in cross_sell.items():
        products_in_bundle = []
        total_price = 0
        total_cogs = 0
        for sku_pattern in skus_raw:
            # Find first matching SKU
            for p in products:
                if p["sku"] in sku_pattern or sku_pattern.startswith(p["sku"]):
                    products_in_bundle.append(p["sku"])
                    total_price += p["retail_price"]
                    total_cogs += p["cogs_2026"]
                    break
        
        if products_in_bundle:
            sub_price = round(total_price * 0.85, 2)
            margin = round(sub_price - total_cogs, 2)
            net_pr = round(margin - 3.90, 2)  # point relais
            bundle_suggestions.append({
                "name": bundle_name,
                "products": products_in_bundle,
                "full_price": round(total_price, 2),
                "sub_price_15pct": sub_price,
                "total_cogs": round(total_cogs, 2),
                "margin_after_disc": margin,
                "net_after_shipping_pr": net_pr,
                "margin_pct": round((margin / sub_price) * 100, 1) if sub_price > 0 else 0,
            })
    
    metrics["cross_sell"] = {
        "bundles_from_packs": cross_sell,
        "bundle_economics": bundle_suggestions
    }
    
    # ── Revenue impact simulation ──
    # Assume current monthly revenue from eligible products
    # Estimate: avg 50 orders/month per eligible product × avg price
    est_monthly_orders_per_product = 50  # conservative estimate
    total_eligible_monthly_revenue = len(go_products) * est_monthly_orders_per_product * avg_price_go
    
    revenue_impact = {}
    for conv_rate in CONVERSION_RATES:
        conv_key = f"conv_{int(conv_rate*100)}pct"
        subscribers = int(len(go_products) * est_monthly_orders_per_product * conv_rate)
        # Revenue impact: subscribers pay 15% less but buy every month
        monthly_sub_revenue = round(subscribers * avg_price_go * 0.85, 2)
        monthly_cannibalized = round(subscribers * avg_price_go * 0.15, 2)  # lost from discount
        
        # But subscribers who would have churned (not rebought) now stay
        # Assume 30% of subscribers would NOT have rebought next month without sub
        incremental_revenue = round(subscribers * 0.30 * avg_price_go * 0.85, 2)
        
        revenue_impact[conv_key] = {
            "conversion_rate": conv_rate,
            "new_subscribers_month": subscribers,
            "monthly_sub_revenue": monthly_sub_revenue,
            "monthly_cannibalization": monthly_cannibalized,
            "monthly_incremental": incremental_revenue,
            "net_monthly_impact": round(incremental_revenue - monthly_cannibalized, 2),
            "annual_sub_revenue": round(monthly_sub_revenue * 12, 2),
        }
    
    metrics["revenue_impact"] = revenue_impact
    metrics["est_monthly_baseline"] = round(total_eligible_monthly_revenue, 2)
    
    # ── Cannibalisation analysis ──
    # For each product: what % of revenue is "lost" to the discount
    cannibalization = []
    for p in go_products:
        monthly_units_est = est_monthly_orders_per_product
        full_price_rev = monthly_units_est * p["retail_price"]
        for conv in [0.10, 0.20]:
            sub_units = int(monthly_units_est * conv)
            remaining_full = monthly_units_est - sub_units
            sub_rev = sub_units * p["retail_price"] * 0.85
            total_rev = remaining_full * p["retail_price"] + sub_rev
            lost = round(full_price_rev - total_rev, 2)
            cannibalization.append({
                "sku": p["sku"],
                "title": p["title"],
                "conversion_rate": conv,
                "monthly_lost_revenue": lost,
                "monthly_lost_pct": round((lost / full_price_rev) * 100, 1) if full_price_rev > 0 else 0,
            })
    metrics["cannibalization"] = cannibalization
    
    # ── Basket optimization ──
    # What basket minimums make sense?
    basket_analysis = []
    for threshold in [15, 20, 25, 30, 35, 40, 50]:
        eligible_for_threshold = [p for p in go_products if p["retail_price"] >= threshold]
        single_product_eligible = len(eligible_for_threshold)
        # 2-product combos above threshold
        combos_2p = 0
        for i, p1 in enumerate(go_products):
            for p2 in go_products[i+1:]:
                if p1["retail_price"] + p2["retail_price"] >= threshold:
                    combos_2p += 1
        
        basket_analysis.append({
            "threshold": threshold,
            "single_products_eligible": single_product_eligible,
            "two_product_combos": combos_2p,
            "note": f"{'✅ Recommandé' if threshold in [25, 30] else ''}"
        })
    metrics["basket_optimization"] = basket_analysis
    
    # ── Competitor price comparison ──
    competitor_comparison = []
    # From master_data.json
    comp_brands = master.get("marques", {})
    for cat_key, cat_label in [
        ("creatine", "Créatine"),
        ("whey", "Whey"),
        ("multivitamines", "Multivitamines"),
        ("omega3", "Omega 3"),
        ("magnesium", "Magnésium"),
        ("collagene", "Collagène"),
        ("probiotiques", "Probiotiques"),
    ]:
        impulse_products_cat = [p for p in products if p["product_category"] == cat_key]
        if not impulse_products_cat:
            continue
        impulse_avg = sum(p["retail_price"] for p in impulse_products_cat) / len(impulse_products_cat)
        
        # Find competitor prices from catalogues
        comp_prices = {}
        for brand_key, brand_data in comp_brands.items():
            cat_data = brand_data.get("catalogue", {})
            if isinstance(cat_data, dict):
                for prod in cat_data.get("produits", []):
                    prod_name = prod.get("nom", "").lower()
                    if cat_key in prod_name or cat_label.lower() in prod_name:
                        comp_prices[brand_key] = prod.get("prix_unitaire", prod.get("prix_one_shot", "N/A"))
                        break
        
        competitor_comparison.append({
            "category": cat_label,
            "impulse_price": round(impulse_avg, 2),
            "impulse_sub_15pct": round(impulse_avg * 0.85, 2),
            "competitors": comp_prices
        })
    metrics["competitor_comparison"] = competitor_comparison
    
    # ── Break-even subscriber count ──
    # Assume setup cost: Shopify app ~$50/month + dev time ~2000€ one-time
    setup_cost_onetime = 2000
    monthly_app_cost = 50  # ~Recharge or similar
    avg_margin_per_sub_monthly = sum(
        p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        for p in go_products
    ) / len(go_products) if go_products else 0
    
    if avg_margin_per_sub_monthly > 0:
        break_even_monthly = math.ceil(monthly_app_cost / avg_margin_per_sub_monthly)
        break_even_setup = math.ceil(setup_cost_onetime / avg_margin_per_sub_monthly)
    else:
        break_even_monthly = 999
        break_even_setup = 999
    
    metrics["break_even"] = {
        "setup_cost_onetime": setup_cost_onetime,
        "monthly_app_cost": monthly_app_cost,
        "avg_net_margin_per_sub_monthly": round(avg_margin_per_sub_monthly, 2),
        "subscribers_to_cover_app_cost": break_even_monthly,
        "subscribers_months_to_cover_setup": break_even_setup,
        "note": f"Il faut {break_even_monthly} abonnés actifs pour couvrir le coût de l'app, et {break_even_setup} abonné-mois pour amortir le setup."
    }
    
    return metrics


# ══════════════════════════════════════════════════════════════
# T5: HTML GENERATION
# ══════════════════════════════════════════════════════════════

def status_color(status):
    return {"rentable": "#22c55e", "marginal": "#f59e0b", "déficitaire": "#ef4444"}.get(status, "#666")

def eligibility_badge(elig):
    colors = {"GO": "#22c55e", "MAYBE": "#f59e0b", "NO-GO": "#ef4444"}
    return f'<span style="background:{colors.get(elig,"#666")};color:white;padding:2px 8px;border-radius:4px;font-weight:700;font-size:12px">{elig}</span>'

def score_bar(score, max_score=100):
    pct = (score / max_score) * 100
    color = "#22c55e" if pct >= 75 else "#f59e0b" if pct >= 55 else "#ef4444"
    return f'''<div style="display:flex;align-items:center;gap:6px">
        <div style="width:60px;height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden">
            <div style="width:{pct}%;height:100%;background:{color}"></div>
        </div>
        <span style="font-size:12px;font-weight:600;color:{color}">{score}</span>
    </div>'''

def generate_html(products, metrics):
    go = [p for p in products if p["eligibility"] == "GO"]
    maybe = [p for p in products if p["eligibility"] == "MAYBE"]
    nogo = [p for p in products if p["eligibility"] == "NO-GO"]
    
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # ── KPI Dashboard ──
    avg_margin_go = metrics["portfolio"]["avg_margin_pct_go"]
    avg_net_sub = metrics["break_even"]["avg_net_margin_per_sub_monthly"]
    
    # Best LTV scenario (2 products, 8% churn)
    best_ltv = metrics["ltv"].get("2_produits_churn_8pct", {})
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Impulse Nutrition — Analyse Rentabilité Abonnement</title>
<style>
:root {{
    --marine: #1B2B4B;
    --orange: #F05A28;
    --bg: #f8fafc;
    --card: #ffffff;
    --border: #e2e8f0;
    --text: #1e293b;
    --muted: #64748b;
    --green: #22c55e;
    --amber: #f59e0b;
    --red: #ef4444;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height:1.5; }}
.container {{ max-width:1400px; margin:0 auto; padding:20px; }}
header {{ background: var(--marine); color:white; padding:32px 0; margin-bottom:24px; }}
header .container {{ display:flex; justify-content:space-between; align-items:center; }}
header h1 {{ font-size:24px; font-weight:700; }}
header .subtitle {{ color: var(--orange); font-size:14px; margin-top:4px; }}
header .date {{ font-size:12px; opacity:0.7; }}

.kpi-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-bottom:32px; }}
.kpi-card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px; text-align:center; }}
.kpi-card .value {{ font-size:28px; font-weight:800; color:var(--marine); }}
.kpi-card .label {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }}
.kpi-card.highlight {{ border-color: var(--orange); border-width:2px; }}
.kpi-card.highlight .value {{ color: var(--orange); }}

section {{ margin-bottom:32px; }}
h2 {{ font-size:20px; font-weight:700; color:var(--marine); margin-bottom:16px; padding-bottom:8px; border-bottom:2px solid var(--orange); display:inline-block; }}
h3 {{ font-size:16px; font-weight:600; color:var(--marine); margin:16px 0 8px; }}

.card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:24px; margin-bottom:16px; }}

table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ background:var(--marine); color:white; padding:10px 8px; text-align:left; font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:0.5px; position:sticky; top:0; }}
td {{ padding:8px; border-bottom:1px solid var(--border); }}
tr:hover {{ background:#f1f5f9; }}
tr.go {{ background: #f0fdf4; }}
tr.maybe {{ background: #fffbeb; }}
tr.nogo {{ background: #fef2f2; }}

.tag {{ display:inline-block; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600; }}
.tag-go {{ background:#dcfce7; color:#166534; }}
.tag-maybe {{ background:#fef3c7; color:#92400e; }}
.tag-nogo {{ background:#fecaca; color:#991b1b; }}
.tag-rentable {{ background:#dcfce7; color:#166534; }}
.tag-marginal {{ background:#fef3c7; color:#92400e; }}
.tag-deficitaire {{ background:#fecaca; color:#991b1b; }}

.grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.grid-3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }}
@media (max-width:768px) {{ .grid-2, .grid-3 {{ grid-template-columns:1fr; }} }}

.bar {{ height:20px; border-radius:4px; display:flex; align-items:center; padding:0 8px; font-size:11px; font-weight:600; color:white; min-width:30px; }}
.cohort-chart {{ display:flex; align-items:flex-end; gap:2px; height:200px; padding:10px 0; }}
.cohort-bar {{ flex:1; background:var(--marine); border-radius:2px 2px 0 0; position:relative; min-width:20px; }}
.cohort-bar span {{ position:absolute; bottom:-20px; left:50%; transform:translateX(-50%); font-size:10px; color:var(--muted); }}

.methodology {{ background: #f1f5f9; border-radius:8px; padding:16px; font-size:13px; color:var(--muted); }}
.methodology h4 {{ color:var(--marine); margin-bottom:8px; }}
.methodology ul {{ padding-left:20px; }}
.methodology li {{ margin-bottom:4px; }}

.heatmap-cell {{ text-align:center; font-weight:700; font-size:12px; padding:6px 4px !important; }}

.source {{ font-size:11px; color:var(--muted); font-style:italic; }}

.recommendation {{ background: linear-gradient(135deg, var(--marine) 0%, #2d3f5e 100%); color:white; border-radius:12px; padding:32px; margin-bottom:16px; }}
.recommendation h3 {{ color: var(--orange); margin-top:0; }}
.recommendation p {{ color: rgba(255,255,255,0.85); }}
.recommendation .highlight-box {{ background: rgba(255,255,255,0.1); border-radius:8px; padding:16px; margin-top:12px; }}

.nav {{ position:sticky; top:0; background:white; border-bottom:1px solid var(--border); padding:8px 0; z-index:100; margin-bottom:24px; }}
.nav .container {{ display:flex; gap:16px; flex-wrap:wrap; }}
.nav a {{ color:var(--marine); text-decoration:none; font-size:13px; font-weight:500; padding:4px 8px; border-radius:4px; }}
.nav a:hover {{ background:var(--marine); color:white; }}
</style>
</head>
<body>

<header>
<div class="container">
    <div>
        <h1>🔬 Analyse Rentabilité Abonnement</h1>
        <div class="subtitle">Impulse Nutrition — Étude interne</div>
    </div>
    <div class="date">Généré le {now}</div>
</div>
</header>

<nav class="nav">
<div class="container">
    <a href="#dashboard">📊 Dashboard</a>
    <a href="#products">📦 Produits</a>
    <a href="#heatmap">🔥 Heatmap</a>
    <a href="#scoring">🏆 Scoring</a>
    <a href="#ltv">📈 LTV</a>
    <a href="#cohort">👥 Cohortes</a>
    <a href="#crosssell">🔗 Cross-sell</a>
    <a href="#basket">🛒 Paniers</a>
    <a href="#cannibalization">⚠️ Cannibalis.</a>
    <a href="#breakeven">💰 Break-even</a>
    <a href="#competitors">🏁 Concurrents</a>
    <a href="#reco">✅ Recommandation</a>
    <a href="#methodology">📋 Méthodologie</a>
</div>
</nav>

<div class="container">

<!-- ═══ DASHBOARD KPI ═══ -->
<section id="dashboard">
<h2>📊 Dashboard</h2>
<div class="kpi-grid">
    <div class="kpi-card highlight">
        <div class="value">{metrics['portfolio']['go_count']}</div>
        <div class="label">Produits éligibles (GO)</div>
    </div>
    <div class="kpi-card">
        <div class="value">{metrics['portfolio']['maybe_count']}</div>
        <div class="label">Produits à étudier (MAYBE)</div>
    </div>
    <div class="kpi-card">
        <div class="value">{avg_margin_go:.0f}%</div>
        <div class="label">Marge brute moy. (GO)</div>
    </div>
    <div class="kpi-card highlight">
        <div class="value">{avg_net_sub:.2f}€</div>
        <div class="label">Contribution nette moy./abo (15%, PR)</div>
    </div>
    <div class="kpi-card">
        <div class="value">{best_ltv.get('ltv_sub_price', 0):.0f}€</div>
        <div class="label">LTV estimée (2 prod, 8% churn)</div>
    </div>
    <div class="kpi-card">
        <div class="value">{metrics['break_even']['subscribers_to_cover_app_cost']}</div>
        <div class="label">Abonnés min (couvrir app)</div>
    </div>
</div>
</section>

<!-- ═══ PRODUCT TABLE ═══ -->
<section id="products">
<h2>📦 Analyse Produit par Produit</h2>
<p class="source" style="margin-bottom:12px">Sources : Shopify MCP (prix retail, stock) + Prix de Cession 2026 (COGS image fournie)</p>
<div class="card" style="overflow-x:auto">
<table>
<thead>
<tr>
    <th>SKU</th>
    <th>Produit</th>
    <th>Catég.</th>
    <th style="text-align:right">Prix TTC</th>
    <th style="text-align:right">COGS</th>
    <th style="text-align:right">Marge €</th>
    <th style="text-align:right">Marge %</th>
    <th style="text-align:right">-10%</th>
    <th style="text-align:right">-15%</th>
    <th style="text-align:right">-20%</th>
    <th style="text-align:right">Net PR (-15%)</th>
    <th style="text-align:center">Score</th>
    <th style="text-align:center">Verdict</th>
    <th style="text-align:right">Stock</th>
</tr>
</thead>
<tbody>'''
    
    # Sort by subscription score descending
    sorted_products = sorted(products, key=lambda p: p["subscription_score"], reverse=True)
    
    for p in sorted_products:
        s10 = p["scenarios"]["10pct"]
        s15 = p["scenarios"]["15pct"]
        s20 = p["scenarios"]["20pct"]
        net_pr_15 = s15["logistics"]["point_relais"]["net_contribution"]
        status_pr_15 = s15["logistics"]["point_relais"]["status"]
        
        row_class = p["eligibility"].lower().replace("-", "")
        elig_tag = f'tag-{p["eligibility"].lower().replace("-","")}'
        status_tag = f'tag-{status_pr_15.replace("é","e")}'
        
        cat_emoji = {"sante": "💊", "sport": "🏋️", "snack": "🍫", "accessoire": "🔧"}.get(p["category"], "")
        
        html += f'''
<tr class="{row_class}">
    <td style="font-family:monospace;font-size:11px">{p["sku"]}</td>
    <td style="font-weight:500">{p["title"]}</td>
    <td>{cat_emoji} {p["category"]}</td>
    <td style="text-align:right;font-weight:600">{p["retail_price"]:.2f}€</td>
    <td style="text-align:right;color:var(--muted)">{p["cogs_2026"]:.2f}€</td>
    <td style="text-align:right;font-weight:600">{p["gross_margin"]:.2f}€</td>
    <td style="text-align:right">{p["gross_margin_pct"]}%</td>
    <td style="text-align:right">{s10["margin_after_discount"]:.2f}€</td>
    <td style="text-align:right">{s15["margin_after_discount"]:.2f}€</td>
    <td style="text-align:right">{s20["margin_after_discount"]:.2f}€</td>
    <td style="text-align:right"><span class="tag {status_tag}">{net_pr_15:.2f}€</span></td>
    <td style="text-align:center">{score_bar(p["subscription_score"])}</td>
    <td style="text-align:center"><span class="tag {elig_tag}">{p["eligibility"]}</span></td>
    <td style="text-align:right;color:var(--muted)">{p["stock"]}</td>
</tr>'''
    
    html += '''
</tbody>
</table>
</div>
<p style="font-size:12px;color:var(--muted);margin-top:8px">
    <strong>Net PR (-15%)</strong> = Marge après remise 15% − frais Point Relais (3.90€). 
    <span class="tag tag-rentable">rentable</span> ≥ 3€ &nbsp;
    <span class="tag tag-marginal">marginal</span> 0-3€ &nbsp;
    <span class="tag tag-deficitaire">déficitaire</span> < 0€
</p>
</section>

<!-- ═══ HEATMAP ═══ -->
<section id="heatmap">
<h2>🔥 Matrice de Rentabilité (Contribution Nette)</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Contribution nette = Prix abonné − COGS − Frais de port. Vert ≥ 5€, Jaune 0-5€, Rouge < 0€</p>
<div class="card" style="overflow-x:auto">
<table>
<thead>
<tr>
    <th>Produit</th>
    <th colspan="3" style="text-align:center;background:var(--orange)">Point Relais (3.90€)</th>
    <th colspan="3" style="text-align:center">Domicile (5.90€)</th>
    <th colspan="3" style="text-align:center;background:#374151">Express (10.90€)</th>
</tr>
<tr>
    <th></th>
    <th style="text-align:center;font-size:10px">-10%</th>
    <th style="text-align:center;font-size:10px">-15%</th>
    <th style="text-align:center;font-size:10px">-20%</th>
    <th style="text-align:center;font-size:10px">-10%</th>
    <th style="text-align:center;font-size:10px">-15%</th>
    <th style="text-align:center;font-size:10px">-20%</th>
    <th style="text-align:center;font-size:10px">-10%</th>
    <th style="text-align:center;font-size:10px">-15%</th>
    <th style="text-align:center;font-size:10px">-20%</th>
</tr>
</thead>
<tbody>'''
    
    # Only show non-accessoire products
    heatmap_products = [p for p in sorted_products if p["category"] != "accessoire" and p["retail_price"] > 5]
    
    for p in heatmap_products:
        html += f'<tr><td style="font-size:12px;font-weight:500">{p["title"][:30]}</td>'
        for disc_key in ["10pct", "15pct", "20pct"]:
            val = p["scenarios"][disc_key]["logistics"]["point_relais"]["net_contribution"]
            bg = "#dcfce7" if val >= 5 else "#bbf7d0" if val >= 3 else "#fef3c7" if val >= 0 else "#fecaca"
            html += f'<td class="heatmap-cell" style="background:{bg}">{val:.1f}€</td>'
        for disc_key in ["10pct", "15pct", "20pct"]:
            val = p["scenarios"][disc_key]["logistics"]["domicile"]["net_contribution"]
            bg = "#dcfce7" if val >= 5 else "#bbf7d0" if val >= 3 else "#fef3c7" if val >= 0 else "#fecaca"
            html += f'<td class="heatmap-cell" style="background:{bg}">{val:.1f}€</td>'
        for disc_key in ["10pct", "15pct", "20pct"]:
            val = p["scenarios"][disc_key]["logistics"]["express"]["net_contribution"]
            bg = "#dcfce7" if val >= 5 else "#bbf7d0" if val >= 3 else "#fef3c7" if val >= 0 else "#fecaca"
            html += f'<td class="heatmap-cell" style="background:{bg}">{val:.1f}€</td>'
        html += '</tr>'
    
    html += '''
</tbody>
</table>
</div>
</section>

<!-- ═══ SCORING DETAIL ═══ -->
<section id="scoring">
<h2>🏆 Détail du Scoring Abonnement</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Score composite /100 basé sur 6 critères pondérés.</p>
<div class="card" style="overflow-x:auto">
<table>
<thead>
<tr>
    <th>Produit</th>
    <th style="text-align:center">Récurrence<br><span style="font-weight:400;font-size:9px">/30 pts</span></th>
    <th style="text-align:center">Marge viable<br><span style="font-weight:400;font-size:9px">/25 pts</span></th>
    <th style="text-align:center">Complexité SKU<br><span style="font-weight:400;font-size:9px">/15 pts</span></th>
    <th style="text-align:center">Concurrents<br><span style="font-weight:400;font-size:9px">/15 pts</span></th>
    <th style="text-align:center">Demande<br><span style="font-weight:400;font-size:9px">/10 pts</span></th>
    <th style="text-align:center">Catégorie<br><span style="font-weight:400;font-size:9px">/5 pts</span></th>
    <th style="text-align:center">Total</th>
    <th style="text-align:center">Verdict</th>
</tr>
</thead>
<tbody>'''
    
    for p in sorted_products:
        if p["category"] == "accessoire":
            continue
        d = p["subscription_score_details"]
        elig_tag = f'tag-{p["eligibility"].lower().replace("-","")}'
        html += f'''
<tr>
    <td style="font-weight:500;font-size:12px">{p["title"][:35]}</td>
    <td style="text-align:center">{d["recurrence"]["pts"]}</td>
    <td style="text-align:center">{d["margin_viability"]["pts"]}</td>
    <td style="text-align:center">{d["sku_complexity"]["pts"]}</td>
    <td style="text-align:center">{d["competitor_presence"]["pts"]}</td>
    <td style="text-align:center">{d["demand_signal"]["pts"]}</td>
    <td style="text-align:center">{d["category_fit"]["pts"]}</td>
    <td style="text-align:center;font-weight:700">{p["subscription_score"]}</td>
    <td style="text-align:center"><span class="tag {elig_tag}">{p["eligibility"]}</span></td>
</tr>'''
    
    html += '''
</tbody>
</table>
</div>
</section>'''

    # ── LTV Section ──
    html += '''
<section id="ltv">
<h2>📈 Projections LTV (Lifetime Value)</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">LTV = Panier moyen mensuel / Taux de churn mensuel. Remise 15% appliquée.</p>
<div class="grid-3">'''
    
    for basket_label, basket_name in [("1_produit", "1 Produit"), ("2_produits", "2 Produits"), ("3_produits", "3 Produits")]:
        html += f'<div class="card"><h3>{basket_name}</h3><table style="font-size:12px">'
        html += '<tr><th>Churn/mois</th><th style="text-align:right">Durée moy.</th><th style="text-align:right">LTV plein tarif</th><th style="text-align:right">LTV abo (-15%)</th></tr>'
        for churn in CHURN_RATES:
            key = f"{basket_label}_churn_{int(churn*100)}pct"
            ltv = metrics["ltv"][key]
            html += f'<tr><td>{int(churn*100)}%</td><td style="text-align:right">{ltv["avg_lifetime_months"]:.0f} mois</td><td style="text-align:right">{ltv["ltv_full_price"]:.0f}€</td><td style="text-align:right;font-weight:600;color:var(--orange)">{ltv["ltv_sub_price"]:.0f}€</td></tr>'
        html += '</table></div>'
    
    html += '</div></section>'
    
    # ── Cohort section ──
    html += '''
<section id="cohort">
<h2>👥 Simulation Cohorte (100 abonnés, 12 mois)</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Évolution d'une cohorte de 100 abonnés démarrant en M1, panier = 2 produits GO moyen, remise 15%.</p>
<div class="grid-3">'''
    
    for churn in CHURN_RATES:
        key = f"2_produits_churn_{int(churn*100)}pct"
        cohort = metrics["ltv"][key]["cohort_100"]
        max_rev = max(c["month_revenue"] for c in cohort)
        
        html += f'''<div class="card">
<h3>Churn {int(churn*100)}%/mois</h3>
<div class="cohort-chart">'''
        for c in cohort:
            h = (c["month_revenue"] / max_rev) * 180 if max_rev > 0 else 0
            html += f'<div class="cohort-bar" style="height:{h}px" title="M{c["month"]}: {c["subscribers"]} abo, {c["month_revenue"]:.0f}€"><span>M{c["month"]}</span></div>'
        html += f'''</div>
<table style="font-size:11px;margin-top:24px">
<tr><td>Abonnés restants M12</td><td style="text-align:right;font-weight:600">{cohort[-1]["subscribers"]:.0f}</td></tr>
<tr><td>CA cumulé 12 mois</td><td style="text-align:right;font-weight:600;color:var(--orange)">{cohort[-1]["cumulative_revenue"]:.0f}€</td></tr>
<tr><td>CA moyen/mois</td><td style="text-align:right">{cohort[-1]["cumulative_revenue"]/12:.0f}€</td></tr>
</table>
</div>'''
    
    html += '</div></section>'
    
    # ── Cross-sell ──
    html += '''
<section id="crosssell">
<h2>🔗 Cross-sell : Bundles Recommandés pour Abonnement</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Basé sur les packs existants Shopify. Calcul avec remise 15% + point relais 3.90€.</p>
<div class="grid-2">'''
    
    for bundle in metrics["cross_sell"]["bundle_economics"]:
        status = "rentable" if bundle["net_after_shipping_pr"] >= 5 else "marginal" if bundle["net_after_shipping_pr"] >= 0 else "déficitaire"
        status_tag = f'tag-{status.replace("é","e")}'
        name_labels = {
            "musculation": "💪 Pack Musculation",
            "endurance": "🏃 Pack Endurance",
            "sante_quotidien": "💊 Pack Santé Quotidien",
            "recuperation": "🧘 Pack Récupération",
            "os_articulations": "🦴 Pack Os & Articulations",
            "sommeil_fatigue": "😴 Pack Sommeil & Fatigue"
        }
        html += f'''<div class="card">
<h3>{name_labels.get(bundle["name"], bundle["name"])}</h3>
<p style="font-size:12px;color:var(--muted);margin-bottom:8px">Produits : {", ".join(bundle["products"])}</p>
<table style="font-size:12px">
<tr><td>Prix plein tarif</td><td style="text-align:right">{bundle["full_price"]:.2f}€</td></tr>
<tr><td>Prix abo (-15%)</td><td style="text-align:right;font-weight:600;color:var(--orange)">{bundle["sub_price_15pct"]:.2f}€</td></tr>
<tr><td>COGS total</td><td style="text-align:right;color:var(--muted)">{bundle["total_cogs"]:.2f}€</td></tr>
<tr><td>Marge après remise</td><td style="text-align:right;font-weight:600">{bundle["margin_after_disc"]:.2f}€</td></tr>
<tr><td>Net après port (PR)</td><td style="text-align:right"><span class="tag {status_tag}">{bundle["net_after_shipping_pr"]:.2f}€</span></td></tr>
<tr><td>Marge nette %</td><td style="text-align:right">{bundle["margin_pct"]:.1f}%</td></tr>
</table>
</div>'''
    
    html += '</div></section>'
    
    # ── Basket optimization ──
    html += '''
<section id="basket">
<h2>🛒 Optimisation du Panier Minimum</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Analyse du seuil de panier minimum pour activer la livraison offerte en abonnement.</p>
<div class="card">
<table>
<thead>
<tr>
    <th>Seuil panier</th>
    <th style="text-align:center">Produits unitaires éligibles</th>
    <th style="text-align:center">Combos 2 produits possibles</th>
    <th>Recommandation</th>
</tr>
</thead>
<tbody>'''
    
    for b in metrics["basket_optimization"]:
        highlight = ' style="background:#f0fdf4;font-weight:600"' if b["threshold"] in [25, 30] else ""
        html += f'''<tr{highlight}>
    <td style="font-weight:600">{b["threshold"]}€</td>
    <td style="text-align:center">{b["single_products_eligible"]}</td>
    <td style="text-align:center">{b["two_product_combos"]}</td>
    <td>{b["note"]}</td>
</tr>'''
    
    html += '''</tbody></table></div></section>'''
    
    # ── Cannibalisation ──
    html += '''
<section id="cannibalization">
<h2>⚠️ Analyse de Cannibalisation</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Estimation de la perte de revenus si des clients existants passent en abonnement (-15%). Hypothèse : 50 commandes/mois/produit.</p>
<div class="card" style="overflow-x:auto">
<table>
<thead>
<tr>
    <th>Produit</th>
    <th style="text-align:center" colspan="2">10% conversion</th>
    <th style="text-align:center" colspan="2">20% conversion</th>
</tr>
<tr>
    <th></th>
    <th style="text-align:right;font-size:10px">Perte €/mois</th>
    <th style="text-align:right;font-size:10px">Perte %</th>
    <th style="text-align:right;font-size:10px">Perte €/mois</th>
    <th style="text-align:right;font-size:10px">Perte %</th>
</tr>
</thead>
<tbody>'''
    
    cann = metrics["cannibalization"]
    # Group by SKU
    skus_seen = set()
    for c in cann:
        if c["sku"] in skus_seen:
            continue
        c10 = next((x for x in cann if x["sku"] == c["sku"] and x["conversion_rate"] == 0.10), None)
        c20 = next((x for x in cann if x["sku"] == c["sku"] and x["conversion_rate"] == 0.20), None)
        if c10 and c20:
            html += f'''<tr>
    <td style="font-size:12px">{c["title"][:35]}</td>
    <td style="text-align:right;color:var(--red)">{c10["monthly_lost_revenue"]:.2f}€</td>
    <td style="text-align:right;color:var(--muted)">{c10["monthly_lost_pct"]}%</td>
    <td style="text-align:right;color:var(--red);font-weight:600">{c20["monthly_lost_revenue"]:.2f}€</td>
    <td style="text-align:right;color:var(--muted)">{c20["monthly_lost_pct"]}%</td>
</tr>'''
        skus_seen.add(c["sku"])
    
    # Total
    total_10 = sum(x["monthly_lost_revenue"] for x in cann if x["conversion_rate"] == 0.10)
    total_20 = sum(x["monthly_lost_revenue"] for x in cann if x["conversion_rate"] == 0.20)
    html += f'''<tr style="font-weight:700;border-top:2px solid var(--marine)">
    <td>TOTAL</td>
    <td style="text-align:right;color:var(--red)">{total_10:.2f}€</td>
    <td></td>
    <td style="text-align:right;color:var(--red)">{total_20:.2f}€</td>
    <td></td>
</tr>'''
    
    html += '''</tbody></table>
<p style="font-size:12px;color:var(--muted);margin-top:8px">⚠️ Cette cannibalisation est compensée par : la rétention accrue (clients qui seraient partis), l'augmentation de la LTV, et le cross-sell naturel. L'effet net est généralement positif à moyen terme.</p>
</div></section>'''
    
    # ── Break-even ──
    be = metrics["break_even"]
    html += f'''
<section id="breakeven">
<h2>💰 Seuil de Rentabilité du Programme</h2>
<div class="grid-2">
<div class="card">
    <h3>Coûts estimés</h3>
    <table style="font-size:13px">
    <tr><td>Coût setup (dev, intégration)</td><td style="text-align:right;font-weight:600">{be["setup_cost_onetime"]}€</td></tr>
    <tr><td>App abonnement (/mois)</td><td style="text-align:right;font-weight:600">{be["monthly_app_cost"]}€</td></tr>
    <tr><td>Contribution nette moy./abonné/mois</td><td style="text-align:right;font-weight:600;color:var(--orange)">{be["avg_net_margin_per_sub_monthly"]:.2f}€</td></tr>
    </table>
</div>
<div class="card">
    <h3>Seuils</h3>
    <table style="font-size:13px">
    <tr><td>Abonnés pour couvrir l'app</td><td style="text-align:right;font-weight:700;font-size:24px;color:var(--marine)">{be["subscribers_to_cover_app_cost"]}</td></tr>
    <tr><td>Abonné-mois pour amortir le setup</td><td style="text-align:right;font-weight:700;font-size:24px;color:var(--marine)">{be["subscribers_months_to_cover_setup"]}</td></tr>
    <tr><td colspan="2" style="font-size:11px;color:var(--muted);padding-top:8px">{be["note"]}</td></tr>
    </table>
</div>
</div>
</section>'''
    
    # ── Competitor comparison ──
    html += '''
<section id="competitors">
<h2>🏁 Positionnement Prix vs Concurrents</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Comparaison des prix retail Impulse (et prix abonné -15%) avec les concurrents du benchmark.</p>
<div class="card">
<p style="font-size:12px;color:var(--muted)">Données concurrents issues du benchmark 8 marques (master_data.json). Les prix concurrents sont les prix one-shot — les prix abonnés concurrents sont généralement 5 à 20% inférieurs.</p>
<div class="grid-2" style="margin-top:16px">'''
    
    # Instead of using incomplete competitor data, show the benchmark summary
    comp_data = {
        "Nutri&Co": {"discount": "15%", "shipping_free": "49€", "tech": "Shopify + Recharge"},
        "Nutrimuscle": {"discount": "5→15%", "shipping_free": "Offerte", "tech": "Custom"},
        "Novoma": {"discount": "10%", "shipping_free": "Avantages abo", "tech": "Shopify"},
        "Cuure": {"discount": "~10%", "shipping_free": "Incluse", "tech": "Custom"},
        "MyProtein": {"discount": "30-45%", "shipping_free": "Offerte", "tech": "Custom"},
        "Decathlon": {"discount": "10-15%", "shipping_free": "Variable", "tech": "Custom"},
        "Aqeelab": {"discount": "20%", "shipping_free": "49€", "tech": "Shopify"},
        "Nutripure": {"discount": "❌ Pas d'abo", "shipping_free": "49€", "tech": "PrestaShop"},
    }
    
    for brand, info in comp_data.items():
        html += f'''<div style="padding:12px;border:1px solid var(--border);border-radius:8px">
    <div style="font-weight:600;margin-bottom:4px">{brand}</div>
    <div style="font-size:12px;color:var(--muted)">
        Remise abo : <strong>{info["discount"]}</strong><br>
        Livraison offerte : {info["shipping_free"]}<br>
        Tech : {info["tech"]}
    </div>
</div>'''
    
    html += '''</div>
<div style="margin-top:16px;padding:16px;background:#f8fafc;border-radius:8px;border-left:4px solid var(--orange)">
    <strong>Positionnement Impulse recommandé :</strong> 15% de remise place Impulse dans la fourchette haute FR (entre Nutri&Co à 15% et Aqeelab à 20%), 
    tout en restant réaliste sur les marges. MyProtein (30-45%) est un outlier international non reproductible pour un pure player FR premium.
</div>
</div>
</section>'''

    # ── RECOMMENDATION ──
    go_daily = [p for p in go if p["category"] == "sante"]
    go_sport = [p for p in go if p["category"] == "sport"]
    
    html += f'''
<section id="reco">
<h2>✅ Recommandation Finale</h2>

<div class="recommendation">
<h3>🎯 Modèle Commercial Recommandé</h3>
<div class="grid-3" style="margin-top:16px">
    <div class="highlight-box">
        <div style="font-size:12px;opacity:0.7">REMISE</div>
        <div style="font-size:28px;font-weight:800">-15%</div>
        <div style="font-size:12px;opacity:0.7">sur tous les produits éligibles</div>
    </div>
    <div class="highlight-box">
        <div style="font-size:12px;opacity:0.7">FRÉQUENCES</div>
        <div style="font-size:28px;font-weight:800">1 / 2 / 3 mois</div>
        <div style="font-size:12px;opacity:0.7">flexibilité maximale</div>
    </div>
    <div class="highlight-box">
        <div style="font-size:12px;opacity:0.7">ENGAGEMENT</div>
        <div style="font-size:28px;font-weight:800">Sans</div>
        <div style="font-size:12px;opacity:0.7">annulation libre</div>
    </div>
</div>
<div class="grid-2" style="margin-top:16px">
    <div class="highlight-box">
        <div style="font-size:12px;opacity:0.7">LIVRAISON OFFERTE</div>
        <div style="font-size:24px;font-weight:800">≥ 25€ en Point Relais</div>
        <div style="font-size:12px;opacity:0.7">domicile : standard (5.90€) sauf ≥ 49€</div>
    </div>
    <div class="highlight-box">
        <div style="font-size:12px;opacity:0.7">WORDING SUGGÉRÉ</div>
        <div style="font-size:20px;font-weight:700">"S'abonner & économiser 15%"</div>
        <div style="font-size:12px;opacity:0.7">CTA : "Livraison offerte en Point Relais"</div>
    </div>
</div>
</div>

<div class="grid-2">
<div class="card">
    <h3 style="color:var(--green)">✅ Produits GO ({len(go)})</h3>
    <p style="font-size:12px;color:var(--muted);margin-bottom:8px">Score ≥ 75/100 — À lancer dès le démarrage</p>
    <table style="font-size:12px">
    <tr><th>Produit</th><th style="text-align:right">Score</th><th style="text-align:right">Net PR</th></tr>'''
    
    for p in sorted(go, key=lambda x: x["subscription_score"], reverse=True):
        net = p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        html += f'<tr><td>{p["title"][:30]}</td><td style="text-align:right">{p["subscription_score"]}</td><td style="text-align:right;font-weight:600">{net:.2f}€</td></tr>'
    
    html += f'''</table>
</div>
<div class="card">
    <h3 style="color:var(--amber)">⚠️ Produits MAYBE ({len(maybe)})</h3>
    <p style="font-size:12px;color:var(--muted);margin-bottom:8px">Score 55-74 — Phase 2 ou avec conditions</p>
    <table style="font-size:12px">
    <tr><th>Produit</th><th style="text-align:right">Score</th><th style="text-align:right">Net PR</th></tr>'''
    
    for p in sorted(maybe, key=lambda x: x["subscription_score"], reverse=True):
        net = p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        html += f'<tr><td>{p["title"][:30]}</td><td style="text-align:right">{p["subscription_score"]}</td><td style="text-align:right;font-weight:600">{net:.2f}€</td></tr>'
    
    html += '''</table>
</div>
</div>
</section>'''
    
    # ── Methodology ──
    html += '''
<section id="methodology">
<h2>📋 Méthodologie & Sources</h2>

<div class="methodology">
<h4>Sources de données</h4>
<ul>
    <li><strong>Prix retail (TTC)</strong> — Shopify MCP API, 96 produits extraits le 10/04/2026</li>
    <li><strong>COGS (Prix de Cession 2026)</strong> — Document interne HCS fourni par Antoine (image), 42 SKUs</li>
    <li><strong>Coûts logistiques</strong> — Tarifs réels Impulse Nutrition : Point Relais 3.90€, Domicile 5.90€, Express 10.90€</li>
    <li><strong>Benchmark concurrents</strong> — Web scraping + analyse manuelle, 8 marques, données collectées avril 2026</li>
    <li><strong>Données marché</strong> — Xerfi, Euromonitor, Grand View Research, PwC France (via recherches web)</li>
    <li><strong>Taux de churn</strong> — Moyennes sectorielles : 8-15%/mois (source : études Recurly, Zuora, Chargebee)</li>
</ul>
</div>

<div class="methodology" style="margin-top:16px">
<h4>Formules de calcul</h4>
<ul>
    <li><strong>Marge brute</strong> = Prix TTC − COGS 2026</li>
    <li><strong>Marge brute %</strong> = Marge brute / Prix TTC × 100</li>
    <li><strong>Marge après remise</strong> = Prix TTC × (1 − remise%) − COGS</li>
    <li><strong>Contribution nette</strong> = Marge après remise − Frais de port</li>
    <li><strong>LTV</strong> = Panier mensuel × (1 − remise%) / Churn mensuel</li>
    <li><strong>Score abonnement</strong> = Récurrence (/30) + Marge viable (/25) + Complexité SKU (/15) + Concurrents (/15) + Demande (/10) + Catégorie (/5)</li>
    <li><strong>Cannibalisation</strong> = Nb clients convertis × Prix × remise% (perte brute, sans considérer la rétention additionnelle)</li>
</ul>
</div>

<div class="methodology" style="margin-top:16px">
<h4>Hypothèses & limites</h4>
<ul>
    <li>Les prix sont TTC — les marges réelles sont légèrement supérieures après déduction de la TVA sur les charges</li>
    <li>Les COGS des électrolytes effervescents sont estimés (1.50€, produit récent absent de l'image COGS)</li>
    <li>L'estimation de 50 commandes/mois/produit est une hypothèse conservative — les données de vente réelles permettraient un affinage</li>
    <li>Le churn de 8-15% est une moyenne sectorielle — le churn réel dépendra de la qualité de l'onboarding et du produit</li>
    <li>La cannibalisation suppose que les clients convertis auraient acheté au plein tarif — en réalité, certains auraient churné</li>
    <li>Les coûts de setup (2000€) et d'app (50€/mois) sont des estimations basses — Recharge/Loop peuvent coûter plus selon le volume</li>
</ul>
</div>

<div class="methodology" style="margin-top:16px">
<h4>Poids du scoring abonnement</h4>
<table style="font-size:12px;width:auto">
<tr><td style="padding:4px 12px">Récurrence naturelle</td><td style="padding:4px 12px;font-weight:600">30%</td><td style="padding:4px 12px;color:var(--muted)">Consommation quotidienne vs occasionnelle</td></tr>
<tr><td style="padding:4px 12px">Marge viable</td><td style="padding:4px 12px;font-weight:600">25%</td><td style="padding:4px 12px;color:var(--muted)">Contribution nette ≥ 3€ après remise 15% + PR</td></tr>
<tr><td style="padding:4px 12px">Complexité SKU</td><td style="padding:4px 12px;font-weight:600">15%</td><td style="padding:4px 12px;color:var(--muted)">1 variante = 15pts, 2 = 10pts, 3+ = 5pts</td></tr>
<tr><td style="padding:4px 12px">Présence concurrents</td><td style="padding:4px 12px;font-weight:600">15%</td><td style="padding:4px 12px;color:var(--muted)">Validation marché (produit en abo chez les concurrents)</td></tr>
<tr><td style="padding:4px 12px">Signal demande</td><td style="padding:4px 12px;font-weight:600">10%</td><td style="padding:4px 12px;color:var(--muted)">Stock ≥ 500 = 10pts (proxy demande)</td></tr>
<tr><td style="padding:4px 12px">Catégorie</td><td style="padding:4px 12px;font-weight:600">5%</td><td style="padding:4px 12px;color:var(--muted)">Santé quotidien > Sport > Accessoire</td></tr>
</table>
</div>
</section>

<footer style="text-align:center;padding:32px;color:var(--muted);font-size:12px;border-top:1px solid var(--border);margin-top:48px">
    <strong>Impulse Nutrition</strong> — Analyse rentabilité abonnement — Document interne confidentiel<br>
    Généré automatiquement à partir des données Shopify + COGS 2026 + Benchmark 8 marques<br>
    © HAVEA Commercial Services — Avril 2026
</footer>

</div>

<script>
// Simple sort on tables
document.querySelectorAll('th').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', function() {
        const table = this.closest('table');
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const idx = Array.from(this.parentNode.children).indexOf(this);
        const asc = this.dataset.sort !== 'asc';
        this.dataset.sort = asc ? 'asc' : 'desc';
        rows.sort((a, b) => {
            let va = a.children[idx]?.textContent?.trim() || '';
            let vb = b.children[idx]?.textContent?.trim() || '';
            const na = parseFloat(va.replace(/[^0-9.-]/g, ''));
            const nb = parseFloat(vb.replace(/[^0-9.-]/g, ''));
            if (!isNaN(na) && !isNaN(nb)) return asc ? na - nb : nb - na;
            return asc ? va.localeCompare(vb) : vb.localeCompare(va);
        });
        rows.forEach(r => tbody.appendChild(r));
    });
});
</script>
</body>
</html>'''
    
    return html


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("T2: Computing profitability model...")
    products = compute_profitability(products)
    
    print("T3: Computing subscription scores...")
    products = compute_subscription_score(products)
    
    print("T4: Computing business metrics...")
    metrics = compute_business_metrics(products)
    
    # Save enriched products
    data["products"] = products
    data["metrics"] = metrics
    with open("benchmark/impulse_products_enriched.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → Saved enriched data to benchmark/impulse_products_enriched.json")
    
    print("T5: Generating HTML report...")
    html = generate_html(products, metrics)
    
    with open("benchmark/rapport_rentabilite_abonnement.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # Summary
    go = [p for p in products if p["eligibility"] == "GO"]
    maybe = [p for p in products if p["eligibility"] == "MAYBE"]
    nogo = [p for p in products if p["eligibility"] == "NO-GO"]
    
    print(f"\n{'='*60}")
    print(f"✅ RAPPORT GÉNÉRÉ : benchmark/rapport_rentabilite_abonnement.html")
    print(f"{'='*60}")
    print(f"  Produits analysés : {len(products)}")
    print(f"  GO  : {len(go)} produits")
    print(f"  MAYBE : {len(maybe)} produits")
    print(f"  NO-GO : {len(nogo)} produits")
    print(f"\n  Top GO products:")
    for p in sorted(go, key=lambda x: x["subscription_score"], reverse=True)[:5]:
        net = p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        print(f"    {p['title'][:35]:<35} score={p['subscription_score']:>3} net_PR={net:.2f}€")
    print(f"\n  Break-even : {metrics['break_even']['subscribers_to_cover_app_cost']} abonnés pour couvrir l'app")
    print(f"  LTV estimée (2 prod, 8% churn) : {metrics['ltv']['2_produits_churn_8pct']['ltv_sub_price']:.0f}€")
