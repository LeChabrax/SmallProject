#!/usr/bin/env python3
"""
Generate a comprehensive HTML report for Impulse Nutrition subscription analysis.
T2: Profitability model
T3: Subscription scoring
T4: Business metrics
T5: HTML generation

Convention HT/TTC (voir benchmark/constants.py) :
  - Tous les calculs de rentabilité (marge, contribution, LTV, break-even) sont en HT.
  - Les prix affichés au client (vitrine, panier) restent en TTC.
  - Les seuils de "rentable/marginal/déficitaire" sont exprimés en HT.
"""
import json
import math
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    TVA_RATE,
    LOGISTICS_TTC,
    LOGISTICS_HT,
    DISCOUNTS,
    CONVERSION_RATES,
    NET_CONTRIBUTION_RENTABLE,
    NET_CONTRIBUTION_MARGINAL,
    SETUP_COST_ONETIME,
    MONTHLY_APP_COST,
    CHURN_CURVES,
    HORIZON_MONTHS,
    expected_months,
    simulate_cohort,
    churn_at_month,
    # Nouveaux imports (scénarios + scoring + cannibalisation comportementale)
    PROGRAM_SCENARIOS,
    get_scenario,
    RETENTION_UPLIFT_MONTHS,
    LOYALIST_ORDERS_PER_YEAR,
    DEFAULT_SUB_DISCOUNT,
    SCORING_WEIGHTS,
    VERDICT_THRESHOLDS,
    COMPETITOR_SUB_COUNT,
    TOTAL_COMPETITORS,
    ILLUSTRATIVE_ORDERS_PER_PRODUCT,
)

# ── Load data ──
with open("benchmark/impulse_products.json", "r") as f:
    data = json.load(f)

products = data["products"]
meta = data["meta"]

with open("benchmark/master_data.json", "r") as f:
    master = json.load(f)

# ══════════════════════════════════════════════════════════════
# T2: PROFITABILITY MODEL
# ══════════════════════════════════════════════════════════════

def compute_profitability(products):
    """Calcule les scénarios de rentabilité par produit, entièrement en HT.

    Inputs lus sur chaque produit :
      - retail_price_ht  : prix vitrine TTC converti en HT (source build_impulse_products)
      - retail_price_ttc : prix vitrine TTC (affichage client)
      - cogs_ht          : prix de cession fournisseur HT

    Pour chaque remise d'abonnement, on stocke :
      - sub_price_ht / sub_price_ttc (affichage)
      - margin_after_discount : HT
      - logistics[name].net_contribution : HT, après frais logistiques HT
    """
    for p in products:
        retail_ht_val = p["retail_price_ht"]
        retail_ttc = p["retail_price_ttc"]
        cogs_ht = p["cogs_ht"]
        scenarios = {}

        for disc in DISCOUNTS:
            disc_key = f"{int(disc*100)}pct"
            sub_price_ht = round(retail_ht_val * (1 - disc), 2)
            sub_price_ttc = round(retail_ttc * (1 - disc), 2)
            margin_after_disc_ht = round(sub_price_ht - cogs_ht, 2)
            margin_pct_after_disc = round((margin_after_disc_ht / sub_price_ht) * 100, 1) if sub_price_ht > 0 else 0

            logistics_scenarios = {}
            for lname, lcost_ht in LOGISTICS_HT.items():
                net_contribution = round(margin_after_disc_ht - lcost_ht, 2)
                if net_contribution >= NET_CONTRIBUTION_RENTABLE:
                    status = "rentable"
                elif net_contribution >= NET_CONTRIBUTION_MARGINAL:
                    status = "marginal"
                else:
                    status = "déficitaire"
                logistics_scenarios[lname] = {
                    "shipping_cost_ht": lcost_ht,
                    "shipping_cost_ttc": LOGISTICS_TTC[lname],
                    "shipping_cost": lcost_ht,  # alias legacy
                    "net_contribution": net_contribution,
                    "status": status,
                    "min_qty_for_viability": max(1, math.ceil(lcost_ht / margin_after_disc_ht)) if margin_after_disc_ht > 0 else 999
                }

            scenarios[disc_key] = {
                "discount_pct": int(disc * 100),
                "sub_price_ht": sub_price_ht,
                "sub_price_ttc": sub_price_ttc,
                "sub_price": sub_price_ttc,  # legacy, affichage client
                "margin_after_discount": margin_after_disc_ht,  # HT
                "margin_pct_after_discount": margin_pct_after_disc,
                "logistics": logistics_scenarios
            }

        # Break-even basket : panier minimum pour que la livraison offerte soit rentable.
        # Les seuils client sont affichés en TTC (réalité e-commerce), calcul sous-jacent en HT.
        margin_ratio_ht = (p["gross_margin_ht"] / retail_ht_val) if retail_ht_val > 0 else 0
        p["break_even_basket"] = {}
        for lname, lcost_ht in LOGISTICS_HT.items():
            for disc in DISCOUNTS:
                disc_key = f"{int(disc*100)}pct"
                effective_margin_ratio = (1 - disc) * margin_ratio_ht
                if effective_margin_ratio > 0:
                    min_basket_ht = lcost_ht / effective_margin_ratio
                    min_basket_ttc = round(min_basket_ht * (1 + TVA_RATE), 2)
                else:
                    min_basket_ttc = 999
                p["break_even_basket"][f"{lname}_{disc_key}"] = min_basket_ttc

        p["scenarios"] = scenarios
    return products


# ══════════════════════════════════════════════════════════════
# T3: SUBSCRIPTION SCORING
# ══════════════════════════════════════════════════════════════

def _recurrence_pts(recurrence_score: int) -> int:
    """Convertit un score /100 en points pondérés selon SCORING_WEIGHTS."""
    return round(recurrence_score * SCORING_WEIGHTS["recurrence"] / 100)


def _margin_pts(net_15_pr: float) -> int:
    """Points marge viable (/25) basés sur la contribution nette HT (-15% + PR).

    Seuils :
      ≥ 8€ → pleine validation (au-dessus de toutes les cibles d'abos)
      ≥ 5€ → très solide
      ≥ 3€ → rentable (seuil "standard" breakpoint)
      ≥ 0€ → marginal (à revoir humainement)
      < 0€ → déficitaire (zéro point)
    """
    max_pts = SCORING_WEIGHTS["margin_viability"]
    if net_15_pr >= 8:  return max_pts                      # 25
    if net_15_pr >= 5:  return round(max_pts * 0.80)        # 20
    if net_15_pr >= 3:  return round(max_pts * 0.60)        # 15
    if net_15_pr >= 0:  return round(max_pts * 0.32)        # 8
    return 0


def _sku_complexity_pts(variants: int) -> int:
    """Points complexité SKU (/10). Moins de variants = plus facile à gérer."""
    max_pts = SCORING_WEIGHTS["sku_complexity"]
    if variants == 1:   return max_pts
    if variants == 2:   return round(max_pts * 0.65)
    return round(max_pts * 0.30)


def _competitor_pts(product_category: str) -> tuple[int, int]:
    """Points validation concurrentielle (/15) — gradient basé sur le nombre de
    concurrents qui proposent cette catégorie en abonnement.

    Retourne (pts, nb_competitors_with_sub).
    """
    max_pts = SCORING_WEIGHTS["competitor_validation"]
    n = COMPETITOR_SUB_COUNT.get(product_category, 0)
    ratio = n / TOTAL_COMPETITORS
    if ratio >= 0.75:  return max_pts, n                     # 75%+ du marché : validation forte
    if ratio >= 0.50:  return round(max_pts * 0.73), n       # 50-75%
    if ratio >= 0.25:  return round(max_pts * 0.47), n       # 25-50%
    if ratio >= 0.10:  return round(max_pts * 0.27), n       # 10-25% (niche)
    return round(max_pts * 0.07), n                          # personne ou presque


def _demand_signal_pts(sku, stock, empirical_velocity):
    """Points signal de demande (/10).

    Préfère la vélocité réelle si `empirical_sales_velocity.json` existe ;
    sinon fallback sur le stock comme proxy imparfait.

    Retourne (pts, source) où source est "velocity" ou "stock".
    """
    max_pts = SCORING_WEIGHTS["demand_signal"]
    if empirical_velocity and sku in empirical_velocity:
        velocity = empirical_velocity[sku]   # commandes/mois réelles
        if velocity >= 50: return max_pts,              "velocity"
        if velocity >= 20: return round(max_pts * 0.70), "velocity"
        if velocity >= 10: return round(max_pts * 0.40), "velocity"
        return round(max_pts * 0.20),                    "velocity"
    # Fallback legacy : stock comme proxy
    if stock >= 500: return max_pts,               "stock"
    if stock >= 300: return round(max_pts * 0.70), "stock"
    if stock >= 100: return round(max_pts * 0.40), "stock"
    return round(max_pts * 0.20),                  "stock"


def _category_fit_pts(category: str) -> int:
    """Points fit catégoriel (/5) — la santé quotidienne est la plus abo-friendly."""
    max_pts = SCORING_WEIGHTS["category_fit"]
    if category == "sante": return max_pts                   # 5
    if category == "sport": return round(max_pts * 0.60)     # 3
    return 0                                                  # accessoire / snack


# Loader optionnel des vélocités réelles (Shopify export)
_velocity_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "empirical_sales_velocity.json")
if os.path.exists(_velocity_path):
    with open(_velocity_path, "r", encoding="utf-8") as _f:
        EMPIRICAL_VELOCITY = json.load(_f)
else:
    EMPIRICAL_VELOCITY = None


def compute_subscription_score(products):
    """Score abonnement /100 basé sur 6 critères pondérés depuis SCORING_WEIGHTS.

    Les helpers _recurrence_pts, _margin_pts, etc. sont sourcés des constantes
    de `constants.py`, donc changer un poids dans les constants propage partout
    sans toucher ce fichier.
    """
    for p in products:
        net_15_pr = p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        rec_raw = p["recurrence_score"]
        rec_pts = _recurrence_pts(rec_raw)
        marg_pts = _margin_pts(net_15_pr)
        sku_pts = _sku_complexity_pts(p["sku_variants"])
        comp_pts, comp_count = _competitor_pts(p["product_category"])
        dem_pts, dem_source = _demand_signal_pts(p["sku"], p["stock"], EMPIRICAL_VELOCITY)
        cat_pts = _category_fit_pts(p["category"])

        total_score = rec_pts + marg_pts + sku_pts + comp_pts + dem_pts + cat_pts

        p["subscription_score"] = min(total_score, 100)
        p["subscription_score_details"] = {
            "recurrence":         {"raw": rec_raw, "pts": rec_pts, "max": SCORING_WEIGHTS["recurrence"], "source": p.get("recurrence_source", "formula")},
            "margin_viability":   {"net_contribution_15pct_pr": net_15_pr, "pts": marg_pts, "max": SCORING_WEIGHTS["margin_viability"]},
            "sku_complexity":     {"variants": p["sku_variants"], "pts": sku_pts, "max": SCORING_WEIGHTS["sku_complexity"]},
            "competitor_presence": {"competitors_with_sub": comp_count, "total_competitors": TOTAL_COMPETITORS, "pts": comp_pts, "max": SCORING_WEIGHTS["competitor_validation"]},
            "demand_signal":      {"source": dem_source, "value": EMPIRICAL_VELOCITY.get(p["sku"]) if EMPIRICAL_VELOCITY else p["stock"], "pts": dem_pts, "max": SCORING_WEIGHTS["demand_signal"]},
            "category_fit":       {"category": p["category"], "pts": cat_pts, "max": SCORING_WEIGHTS["category_fit"]},
        }

        # Verdict GO/MAYBE/NO-GO basé sur les seuils VERDICT_THRESHOLDS
        if total_score >= VERDICT_THRESHOLDS["GO"]:
            p["eligibility"] = "GO"
        elif total_score >= VERDICT_THRESHOLDS["MAYBE"]:
            p["eligibility"] = "MAYBE"
        else:
            p["eligibility"] = "NO-GO"

    return products


# ══════════════════════════════════════════════════════════════
# T4: BUSINESS METRICS
# ══════════════════════════════════════════════════════════════

def compute_business_metrics(products):
    """T4 : LTV, cross-sell, cannibalisation, break-even — tout en HT côté rentabilité.

    Certains affichages restent en TTC (ticket moyen vitrine, comparaison concurrents)
    car c'est la perception client. Les champs sont suffixés pour lever l'ambiguïté.
    """
    metrics = {}

    go_products = [p for p in products if p["eligibility"] == "GO"]
    maybe_products = [p for p in products if p["eligibility"] == "MAYBE"]
    eligible = go_products + maybe_products

    # ── Ticket moyen (HT pour le calcul, TTC pour l'affichage client) ──
    avg_price_go_ttc = sum(p["retail_price_ttc"] for p in go_products) / len(go_products) if go_products else 0
    avg_price_go_ht = sum(p["retail_price_ht"] for p in go_products) / len(go_products) if go_products else 0
    avg_price_eligible_ttc = sum(p["retail_price_ttc"] for p in eligible) / len(eligible) if eligible else 0
    avg_margin_go_ht_pct = sum(p["gross_margin_pct_ht"] for p in go_products) / len(go_products) if go_products else 0

    metrics["portfolio"] = {
        "total_products": len(products),
        "go_count": len(go_products),
        "maybe_count": len(maybe_products),
        "nogo_count": len([p for p in products if p["eligibility"] == "NO-GO"]),
        "avg_price_go_ttc": round(avg_price_go_ttc, 2),
        "avg_price_go_ht": round(avg_price_go_ht, 2),
        "avg_price_go": round(avg_price_go_ttc, 2),  # legacy alias
        "avg_price_eligible_ttc": round(avg_price_eligible_ttc, 2),
        "avg_margin_pct_go_ht": round(avg_margin_go_ht_pct, 1),
        "avg_margin_pct_go": round(avg_margin_go_ht_pct, 1),  # legacy alias
        "go_products": [p["sku"] for p in go_products],
        "maybe_products": [p["sku"] for p in maybe_products],
    }

    # ── Projections LTV (HT, basées sur courbes de churn multi-phases) ──
    # Panier = 1/2/3 produits au prix GO moyen.
    avg_basket_1p_ht = round(avg_price_go_ht, 2)
    avg_basket_2p_ht = round(avg_price_go_ht * 2, 2)
    avg_basket_3p_ht = round(avg_price_go_ht * 3, 2)
    avg_basket_1p_ttc = round(avg_price_go_ttc, 2)
    avg_basket_2p_ttc = round(avg_price_go_ttc * 2, 2)
    avg_basket_3p_ttc = round(avg_price_go_ttc * 3, 2)

    SUB_DISCOUNT = 0.15

    # Pré-calcul des expected_months et cohortes pour chaque scénario
    scenario_metrics = {}
    for scenario_name, curve in CHURN_CURVES.items():
        em = expected_months(curve, HORIZON_MONTHS)
        cohort_raw = simulate_cohort(curve, horizon=HORIZON_MONTHS)
        scenario_metrics[scenario_name] = {
            "curve": curve,
            "expected_months": em,
            "cohort_raw": cohort_raw,
        }

    ltv_scenarios = {}
    basket_configs = [
        ("1_produit", avg_basket_1p_ht, avg_basket_1p_ttc),
        ("2_produits", avg_basket_2p_ht, avg_basket_2p_ttc),
        ("3_produits", avg_basket_3p_ht, avg_basket_3p_ttc),
    ]
    for basket_label, basket_ht, basket_ttc in basket_configs:
        for scenario_name, sm in scenario_metrics.items():
            em = sm["expected_months"]
            # LTV = panier HT × (1 - remise) × mois moyens (expected_months issu de la courbe)
            ltv_full_ht = round(basket_ht * em, 2)
            ltv_sub_ht = round(basket_ht * (1 - SUB_DISCOUNT) * em, 2)

            # Cohorte HT sur HORIZON_MONTHS à partir de la courbe
            cohort_revenue = []
            cumulative = 0.0
            for row in sm["cohort_raw"]:
                survivors_start = row["survivors_start"]
                # On considère que l'abonné paie au début du mois
                month_revenue = round(survivors_start * basket_ht * (1 - SUB_DISCOUNT), 2)
                cumulative += month_revenue
                cohort_revenue.append({
                    "month": row["month"],
                    "subscribers": row["survivors_end"],
                    "survivors_start": survivors_start,
                    "churn_rate": row["churn_rate"],
                    "month_revenue": month_revenue,
                    "cumulative_revenue": round(cumulative, 2),
                })

            ltv_scenarios[f"{basket_label}_{scenario_name}"] = {
                "basket_ht": basket_ht,
                "basket_ttc": basket_ttc,
                "basket": basket_ttc,  # legacy display
                "scenario": scenario_name,
                "avg_lifetime_months": em,
                "ltv_full_price": ltv_full_ht,
                "ltv_sub_price": ltv_sub_ht,
                "cohort": cohort_revenue,
                "cohort_100": cohort_revenue,  # alias legacy
            }

    metrics["ltv"] = ltv_scenarios
    metrics["churn_curves"] = {
        name: {
            "curve": sm["curve"],
            "expected_months": sm["expected_months"],
        }
        for name, sm in scenario_metrics.items()
    }
    metrics["horizon_months"] = HORIZON_MONTHS
    
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
    
    # Bundle suggestions for subscription (calcul en HT + affichage TTC)
    bundle_suggestions = []
    logistics_pr_ht = LOGISTICS_HT["point_relais"]
    for bundle_name, skus_raw in cross_sell.items():
        products_in_bundle = []
        total_price_ht = 0
        total_price_ttc = 0
        total_cogs_ht = 0
        for sku_pattern in skus_raw:
            for p in products:
                if p["sku"] in sku_pattern or sku_pattern.startswith(p["sku"]):
                    products_in_bundle.append(p["sku"])
                    total_price_ht += p["retail_price_ht"]
                    total_price_ttc += p["retail_price_ttc"]
                    total_cogs_ht += p["cogs_ht"]
                    break

        if products_in_bundle:
            sub_price_ht = round(total_price_ht * 0.85, 2)
            sub_price_ttc = round(total_price_ttc * 0.85, 2)
            margin_ht = round(sub_price_ht - total_cogs_ht, 2)
            net_pr_ht = round(margin_ht - logistics_pr_ht, 2)
            bundle_suggestions.append({
                "name": bundle_name,
                "products": products_in_bundle,
                "full_price_ttc": round(total_price_ttc, 2),
                "full_price": round(total_price_ttc, 2),  # legacy affichage
                "full_price_ht": round(total_price_ht, 2),
                "sub_price_15pct_ttc": sub_price_ttc,
                "sub_price_15pct": sub_price_ttc,  # legacy affichage
                "sub_price_15pct_ht": sub_price_ht,
                "total_cogs": round(total_cogs_ht, 2),
                "margin_after_disc": margin_ht,  # HT
                "net_after_shipping_pr": net_pr_ht,  # HT
                "margin_pct": round((margin_ht / sub_price_ht) * 100, 1) if sub_price_ht > 0 else 0,
            })

    metrics["cross_sell"] = {
        "bundles_from_packs": cross_sell,
        "bundle_economics": bundle_suggestions
    }
    
    # ── Cannibalisation comportementale 3-voies (modèle honnête) ──
    # Chaque nouvel abonné se décompose en 3 cohortes avec des impacts différents :
    #   - NEW customer : 100% incrémental, gain = LTV complète de sa durée de vie
    #   - RETENTION save : aurait churné, gain = uplift de durée × contribution mensuelle
    #   - LOYALIST : aurait acheté plein tarif, perte = discount × orders/an
    #
    # Le split (new/retention/loyalist) dépend du scénario de programme (acquisition
    # plus ou moins agressive → qualité de mix différente).

    # Contribution mensuelle moyenne par abonné : même calcul que pour le break-even
    avg_contribution_per_sub_monthly = sum(
        p["scenarios"]["15pct"]["logistics"]["point_relais"]["net_contribution"]
        for p in go_products
    ) / len(go_products) if go_products else 0

    cannibalization_by_scenario = {}
    for scenario_key, scenario in PROGRAM_SCENARIOS.items():
        # Paramètres cohérents au scénario
        lifetime_months = expected_months(CHURN_CURVES[scenario["churn_curve_key"]])
        mix_new = scenario["new_customer_rate"]
        mix_retention = scenario["retention_save_rate"]
        mix_loyalist = scenario["loyalist_rate"]

        # Gain par abonné pour chaque cohorte (en € HT annualisés)
        # 1. Nouveau client : sa LTV nette complète (= contribution lifetime)
        gain_new_per_sub = mix_new * avg_contribution_per_sub_monthly * lifetime_months
        # 2. Retention save : uplift de durée (on prolonge la vie du client existant)
        gain_retention_per_sub = mix_retention * avg_contribution_per_sub_monthly * RETENTION_UPLIFT_MONTHS
        # 3. Loyaliste : perte de 15% sur ses commandes/an qu'il aurait payées plein tarif
        loss_loyalist_per_sub = mix_loyalist * avg_price_go_ht * DEFAULT_SUB_DISCOUNT * LOYALIST_ORDERS_PER_YEAR

        net_per_sub_annual = gain_new_per_sub + gain_retention_per_sub - loss_loyalist_per_sub
        net_per_sub_monthly = net_per_sub_annual / 12

        cannibalization_by_scenario[scenario_key] = {
            "label": scenario["label"],
            "churn_curve_key": scenario["churn_curve_key"],
            "lifetime_months_baseline": lifetime_months,
            "mix": {
                "new_customer_rate": mix_new,
                "retention_save_rate": mix_retention,
                "loyalist_rate": mix_loyalist,
                "source": scenario["mix_source"],
            },
            "per_sub_breakdown": {
                "gain_new_annual": round(gain_new_per_sub, 2),
                "gain_retention_annual": round(gain_retention_per_sub, 2),
                "loss_loyalist_annual": round(loss_loyalist_per_sub, 2),
                "net_annual": round(net_per_sub_annual, 2),
                "net_monthly": round(net_per_sub_monthly, 2),
            },
            # Projection pour les conversion_rates illustratifs (multiplié par nb abonnés)
            "illustrative_projections": {},
        }

        # Projection illustrative : combien de nouveaux abos si on applique les CONVERSION_RATES
        # à l'hypothèse ILLUSTRATIVE_ORDERS_PER_PRODUCT. Clairement labellé illustratif.
        for conv_rate in CONVERSION_RATES:
            illustrative_new_subs_month = int(len(go_products) * ILLUSTRATIVE_ORDERS_PER_PRODUCT * conv_rate)
            cannibalization_by_scenario[scenario_key]["illustrative_projections"][f"conv_{int(conv_rate*100)}pct"] = {
                "conversion_rate": conv_rate,
                "new_subs_per_month": illustrative_new_subs_month,
                "monthly_net_impact_ht": round(illustrative_new_subs_month * net_per_sub_monthly, 2),
                "annual_net_impact_ht": round(illustrative_new_subs_month * net_per_sub_annual, 2),
            }

    metrics["cannibalization_behavioral"] = cannibalization_by_scenario

    # ── Legacy "revenue_impact" section — gardée illustrative avec badge dans le HTML ──
    # Cette section est kept pour rétro-compatibilité du rendu existant mais marquée
    # "💡 ILLUSTRATIF" car elle multiplie linéairement par ILLUSTRATIVE_ORDERS_PER_PRODUCT.
    revenue_impact = {}
    for conv_rate in CONVERSION_RATES:
        conv_key = f"conv_{int(conv_rate*100)}pct"
        subscribers = int(len(go_products) * ILLUSTRATIVE_ORDERS_PER_PRODUCT * conv_rate)
        monthly_sub_revenue_ht = round(subscribers * avg_price_go_ht * (1 - DEFAULT_SUB_DISCOUNT), 2)
        # On utilise le net_monthly du scenario standard pour le net_monthly_impact
        std_net_per_sub_monthly = cannibalization_by_scenario["standard"]["per_sub_breakdown"]["net_monthly"]
        net_impact = round(subscribers * std_net_per_sub_monthly, 2)
        revenue_impact[conv_key] = {
            "conversion_rate": conv_rate,
            "new_subscribers_month": subscribers,
            "monthly_sub_revenue": monthly_sub_revenue_ht,
            "net_monthly_impact": net_impact,
            "annual_sub_revenue": round(monthly_sub_revenue_ht * 12, 2),
        }
    metrics["revenue_impact"] = revenue_impact
    metrics["est_monthly_baseline"] = round(len(go_products) * ILLUSTRATIVE_ORDERS_PER_PRODUCT * avg_price_go_ht, 2)
    metrics["est_monthly_orders_per_product"] = ILLUSTRATIVE_ORDERS_PER_PRODUCT

    # ── Cannibalisation par SKU (perte de recette HT liée à la remise) ──
    # Toujours illustrative (basée sur ILLUSTRATIVE_ORDERS_PER_PRODUCT)
    cannibalization = []
    for p in go_products:
        monthly_units_est = ILLUSTRATIVE_ORDERS_PER_PRODUCT
        full_price_rev_ht = monthly_units_est * p["retail_price_ht"]
        for conv in [0.10, 0.20]:
            sub_units = int(monthly_units_est * conv)
            remaining_full = monthly_units_est - sub_units
            sub_rev_ht = sub_units * p["retail_price_ht"] * (1 - DEFAULT_SUB_DISCOUNT)
            total_rev_ht = remaining_full * p["retail_price_ht"] + sub_rev_ht
            lost_ht = round(full_price_rev_ht - total_rev_ht, 2)
            cannibalization.append({
                "sku": p["sku"],
                "title": p["title"],
                "conversion_rate": conv,
                "monthly_lost_revenue": lost_ht,
                "monthly_lost_pct": round((lost_ht / full_price_rev_ht) * 100, 1) if full_price_rev_ht > 0 else 0,
            })
    metrics["cannibalization"] = cannibalization
    
    # ── Basket optimization ──
    # Seuils de panier client → exprimés en TTC (c'est ce que voit le client sur le site)
    basket_analysis = []
    for threshold in [15, 20, 25, 30, 35, 40, 50]:
        eligible_for_threshold = [p for p in go_products if p["retail_price_ttc"] >= threshold]
        single_product_eligible = len(eligible_for_threshold)
        combos_2p = 0
        for i, p1 in enumerate(go_products):
            for p2 in go_products[i+1:]:
                if p1["retail_price_ttc"] + p2["retail_price_ttc"] >= threshold:
                    combos_2p += 1
        
        basket_analysis.append({
            "threshold": threshold,
            "single_products_eligible": single_product_eligible,
            "two_product_combos": combos_2p,
            "note": f"{'✅ Recommandé' if threshold in [25, 30] else ''}"
        })
    metrics["basket_optimization"] = basket_analysis
    
    # ── Comparaison concurrents (affichage TTC, perception client) ──
    competitor_comparison = []
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
        impulse_avg_ttc = sum(p["retail_price_ttc"] for p in impulse_products_cat) / len(impulse_products_cat)

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
            "impulse_price": round(impulse_avg_ttc, 2),
            "impulse_sub_15pct": round(impulse_avg_ttc * 0.85, 2),
            "competitors": comp_prices
        })
    metrics["competitor_comparison"] = competitor_comparison

    # ── Break-even programme (HT) par scénario ──
    # Pour chaque scénario (lean / standard / full), on calcule :
    #   (1) Running break-even : combien d'abonnés ACTIFS pour couvrir l'app mensuelle
    #   (2) Setup break-even : combien de nouveaux abonnés pour amortir le setup
    #       (dépend de la durée de vie moyenne = expected_months de la courbe du scénario)
    #
    # La contribution mensuelle moyenne `avg_contribution_per_sub_monthly` est
    # invariante (elle dépend des produits, pas du scénario).

    break_even_by_scenario = {}
    for scenario_key, scenario in PROGRAM_SCENARIOS.items():
        app_cost = scenario["app_monthly_ht"]
        setup_cost = scenario["setup_onetime_ht"]
        lifetime = expected_months(CHURN_CURVES[scenario["churn_curve_key"]])
        lifetime_contribution = avg_contribution_per_sub_monthly * lifetime

        if avg_contribution_per_sub_monthly > 0:
            running_be = math.ceil(app_cost / avg_contribution_per_sub_monthly)
        else:
            running_be = 999
        if lifetime_contribution > 0:
            setup_be = math.ceil(setup_cost / lifetime_contribution)
        else:
            setup_be = 999

        # Seuil de contribution nette "rentable" dérivé dynamiquement du scénario :
        # = app_cost / viable_subs_target → arrondi à la 2e décimale
        viable_threshold = round(app_cost / scenario["viable_subs_target"], 2)

        break_even_by_scenario[scenario_key] = {
            "label": scenario["label"],
            "app_monthly_ht": app_cost,
            "setup_onetime_ht": setup_cost,
            "churn_curve_key": scenario["churn_curve_key"],
            "lifetime_months": lifetime,
            "lifetime_contribution_per_sub_ht": round(lifetime_contribution, 2),
            "running_break_even_subs": running_be,
            "setup_break_even_new_subs": setup_be,
            "viable_subs_target": scenario["viable_subs_target"],
            "viable_net_contribution_threshold": viable_threshold,
            "note": (
                f"Il faut {running_be} abonnés actifs chaque mois pour couvrir "
                f"l'app ({app_cost}€ HT/mois). Il faut {setup_be} nouveaux abonnés "
                f"pour amortir le setup de {setup_cost}€ HT, sur une durée de vie "
                f"moyenne de {lifetime:.1f} mois (courbe {scenario['churn_curve_key']})."
            ),
        }

    metrics["break_even_by_scenario"] = break_even_by_scenario

    # Legacy "break_even" : on garde l'ancienne structure en utilisant le scenario standard
    # (tout le rendu HTML existant le consomme)
    std_be = break_even_by_scenario["standard"]
    metrics["break_even"] = {
        "setup_cost_onetime": std_be["setup_onetime_ht"],
        "monthly_app_cost": std_be["app_monthly_ht"],
        "baseline_expected_months": std_be["lifetime_months"],
        "avg_net_margin_per_sub_monthly": round(avg_contribution_per_sub_monthly, 2),
        "avg_lifetime_contribution_per_sub": std_be["lifetime_contribution_per_sub_ht"],
        "subscribers_to_cover_app_cost": std_be["running_break_even_subs"],
        "subscribers_to_amortize_setup": std_be["setup_break_even_new_subs"],
        "subscribers_months_to_cover_setup": std_be["setup_break_even_new_subs"],  # legacy alias
        "note": std_be["note"],
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
    avg_margin_go = metrics["portfolio"]["avg_margin_pct_go_ht"]
    avg_net_sub = metrics["break_even"]["avg_net_margin_per_sub_monthly"]
    
    # LTV affichée sur le dashboard : scénario baseline, 2 produits
    best_ltv = metrics["ltv"].get("2_produits_baseline", {})
    
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

/* Panneaux pédagogiques : format distinctif, fond chaud, bordure orange */
.edu-panel {{
    background: #fff8f0;
    border-left: 4px solid var(--orange);
    border-radius: 8px;
    padding: 16px 20px;
    margin: 16px 0;
    font-size: 13px;
    color: #4a3a2a;
}}
.edu-panel h4 {{ color: var(--orange); margin-bottom: 8px; font-weight: 700; font-size: 14px; }}
.edu-panel .formula {{ background: rgba(240,90,40,0.08); padding: 8px 12px; border-radius: 4px; font-family: 'SF Mono', Menlo, monospace; font-size: 12px; margin: 8px 0; }}
.edu-panel .example {{ margin-top: 8px; padding-top: 8px; border-top: 1px dashed rgba(240,90,40,0.3); }}
.edu-panel .takeaway {{ margin-top: 8px; font-weight: 600; color: var(--marine); }}

/* Badge ILLUSTRATIF : avertissement sur les sections basées sur des valeurs non prédictives */
.badge-illustrative {{
    display: inline-block;
    background: #fef3c7;
    color: #92400e;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1px solid #fcd34d;
    margin-left: 8px;
    vertical-align: middle;
}}

/* Scenario cards : 3 colonnes Lean/Standard/Full */
.scenario-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 16px;
}}
@media (max-width:968px) {{ .scenario-grid {{ grid-template-columns: 1fr; }} }}
.scenario-card {{
    background: var(--card);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
}}
.scenario-card.standard {{ border-color: var(--orange); }}
.scenario-card h3 {{ color: var(--marine); margin-bottom: 4px; }}
.scenario-card .scenario-desc {{ font-size: 12px; color: var(--muted); margin-bottom: 12px; line-height: 1.4; }}
.scenario-card .scenario-kpi {{ display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; }}
.scenario-card .scenario-kpi strong {{ color: var(--marine); }}
.scenario-card .scenario-kpi.big {{ font-size: 15px; padding: 10px 0; border-top: 1px solid var(--border); margin-top: 8px; }}
.scenario-card .scenario-kpi.big .value {{ font-size: 22px; font-weight: 800; color: var(--orange); }}

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
    <a href="#scenarios">🎯 Scénarios</a>
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
        <div class="label">Marge brute HT moy. (GO)</div>
    </div>
    <div class="kpi-card highlight">
        <div class="value">{avg_net_sub:.2f}€</div>
        <div class="label">Contribution nette HT moy./abo (-15%, PR)</div>
    </div>
    <div class="kpi-card">
        <div class="value">{best_ltv.get('ltv_sub_price', 0):.0f}€</div>
        <div class="label">LTV HT (2 prod, churn baseline)</div>
    </div>
    <div class="kpi-card">
        <div class="value">{metrics['break_even']['subscribers_to_cover_app_cost']}</div>
        <div class="label">Abonnés min (couvrir app Standard)</div>
    </div>
</div>
</section>

<!-- ═══ SCÉNARIOS COMPOSITES ═══ -->
<section id="scenarios">
<h2>🎯 3 Scénarios de Programme — Vue d'ensemble</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Chaque scénario bundle tous les paramètres cohérents (coûts infra, courbe de churn, mix d'acquisition). Les métriques clés sont calculées de bout en bout pour chaque scénario. Le <strong>Standard</strong> (bordure orange) est le cas de référence affiché ailleurs dans le rapport.</p>
<div class="scenario-grid">'''

    # Récap des 3 scénarios avec les KPIs les plus parlants
    for scenario_key in ["lean", "standard", "full"]:
        scen_meta = PROGRAM_SCENARIOS[scenario_key]
        be = metrics["break_even_by_scenario"][scenario_key]
        cannib_b = metrics["cannibalization_behavioral"][scenario_key]
        ltv = metrics["ltv"][f"2_produits_{scen_meta['churn_curve_key']}"]
        css_class = " standard" if scenario_key == "standard" else ""
        net_per_sub = cannib_b["per_sub_breakdown"]["net_annual"]
        net_color = "var(--green)" if net_per_sub > 0 else "var(--red)"
        html += f'''
<div class="scenario-card{css_class}">
    <h3>{scen_meta["label"]}</h3>
    <div class="scenario-desc">{scen_meta["description"]}</div>
    <div class="scenario-kpi"><span>Courbe de churn</span><strong>{scen_meta["churn_curve_key"]}</strong></div>
    <div class="scenario-kpi"><span>Durée de vie moyenne</span><strong>{be["lifetime_months"]:.1f} mois</strong></div>
    <div class="scenario-kpi"><span>LTV abo HT (2 prod)</span><strong>{ltv["ltv_sub_price"]:.0f}€</strong></div>
    <div class="scenario-kpi"><span>App + setup HT</span><strong>{be["app_monthly_ht"]}€/mo + {be["setup_onetime_ht"]}€</strong></div>
    <div class="scenario-kpi"><span>Running break-even</span><strong>{be["running_break_even_subs"]} abonnés actifs</strong></div>
    <div class="scenario-kpi"><span>Setup break-even</span><strong>{be["setup_break_even_new_subs"]} nouveaux abos</strong></div>
    <div class="scenario-kpi big"><span>Net / abo / an</span><span class="value" style="color:{net_color}">{net_per_sub:+.0f}€</span></div>
</div>'''

    html += '''
</div>
<p style="font-size:12px;color:var(--muted);margin-top:12px">💡 <strong>Lecture actionnable</strong> : démarrer en <strong>Lean</strong> pour prouver le concept (break-even à 3 abonnés, risque minimal), migrer vers <strong>Standard</strong> à partir de 100 abonnés actifs, envisager <strong>Full</strong> seulement au-dessus de 500 abonnés. Ces seuils tombent des calculs de running break-even ci-dessus.</p>
</section>

<!-- ═══ PRODUCT TABLE ═══ -->
<section id="products">
<h2>📦 Analyse Produit par Produit</h2>
<p class="source" style="margin-bottom:12px">Sources : Shopify MCP (prix retail TTC, stock) + Prix de Cession 2026 HT (COGS image fournie). <strong>Toutes les marges et contributions nettes sont en HT</strong> (TVA 20% déduite du prix retail, TVA récupérable sur COGS et logistique).</p>
<div class="card" style="overflow-x:auto">
<table>
<thead>
<tr>
    <th>SKU</th>
    <th>Produit</th>
    <th>Catég.</th>
    <th style="text-align:right">Prix TTC</th>
    <th style="text-align:right">Prix HT</th>
    <th style="text-align:right">COGS HT</th>
    <th style="text-align:right">Marge € HT</th>
    <th style="text-align:right">Marge % HT</th>
    <th style="text-align:right">-10% HT</th>
    <th style="text-align:right">-15% HT</th>
    <th style="text-align:right">-20% HT</th>
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
    <td style="text-align:right;font-weight:600">{p["retail_price_ttc"]:.2f}€</td>
    <td style="text-align:right">{p["retail_price_ht"]:.2f}€</td>
    <td style="text-align:right;color:var(--muted)">{p["cogs_ht"]:.2f}€</td>
    <td style="text-align:right;font-weight:600">{p["gross_margin_ht"]:.2f}€</td>
    <td style="text-align:right">{p["gross_margin_pct_ht"]}%</td>
    <td style="text-align:right">{s10["margin_after_discount"]:.2f}€</td>
    <td style="text-align:right">{s15["margin_after_discount"]:.2f}€</td>
    <td style="text-align:right">{s20["margin_after_discount"]:.2f}€</td>
    <td style="text-align:right"><span class="tag {status_tag}">{net_pr_15:.2f}€</span></td>
    <td style="text-align:center">{score_bar(p["subscription_score"])}</td>
    <td style="text-align:center"><span class="tag {elig_tag}">{p["eligibility"]}</span></td>
    <td style="text-align:right;color:var(--muted)">{p["stock"]}</td>
</tr>'''
    
    html += f'''
</tbody>
</table>
</div>
<p style="font-size:12px;color:var(--muted);margin-top:8px">
    <strong>Net PR (-15%)</strong> = Marge HT après remise 15% − frais Point Relais HT ({LOGISTICS_HT["point_relais"]:.2f}€ HT, {LOGISTICS_TTC["point_relais"]:.2f}€ TTC).
    <span class="tag tag-rentable">rentable</span> ≥ {NET_CONTRIBUTION_RENTABLE:.0f}€ HT &nbsp;
    <span class="tag tag-marginal">marginal</span> {NET_CONTRIBUTION_MARGINAL:.0f}-{NET_CONTRIBUTION_RENTABLE:.0f}€ HT &nbsp;
    <span class="tag tag-deficitaire">déficitaire</span> &lt; {NET_CONTRIBUTION_MARGINAL:.0f}€ HT
</p>
</section>

<!-- ═══ HEATMAP ═══ -->
<section id="heatmap">
<h2>🔥 Matrice de Rentabilité (Contribution Nette HT)</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Contribution nette HT = Prix abonné HT − COGS HT − Frais de port HT. Vert ≥ 5€, Jaune 0-5€, Rouge &lt; 0€. <strong>Tous les chiffres sont en HT</strong> (TVA 20% déduite du prix et des frais de port).</p>
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
    
    html += f'''
</tbody>
</table>
</div>

<div class="edu-panel">
<h4>🎓 Comment on classe un produit en GO / MAYBE / NO-GO</h4>
<p>Chaque produit reçoit un score composite /100 basé sur 6 critères pondérés, documentés dans <code>constants.py</code> → <code>SCORING_WEIGHTS</code>. Les poids ont été calibrés d\'après les drivers de succès observés en DTC compléments :</p>
<table style="font-size:12px;margin:8px 0">
<tr><td style="padding:4px 12px"><strong>Récurrence</strong></td><td style="padding:4px 12px">{SCORING_WEIGHTS["recurrence"]} pts</td><td style="padding:4px 12px;color:var(--muted)">Le #1 driver : un produit qui se consomme en 1 mois est un candidat abo naturel, un accessoire ne l\'est pas.</td></tr>
<tr><td style="padding:4px 12px"><strong>Marge viable</strong></td><td style="padding:4px 12px">{SCORING_WEIGHTS["margin_viability"]} pts</td><td style="padding:4px 12px;color:var(--muted)">Contribution nette HT à ≥3€ (seuil Standard) = programme rentable.</td></tr>
<tr><td style="padding:4px 12px"><strong>Validation concurrents</strong></td><td style="padding:4px 12px">{SCORING_WEIGHTS["competitor_validation"]} pts</td><td style="padding:4px 12px;color:var(--muted)">Gradient : si 75%+ des benchmarkés ont la catégorie en abo, forte validation marché.</td></tr>
<tr><td style="padding:4px 12px"><strong>Complexité SKU</strong></td><td style="padding:4px 12px">{SCORING_WEIGHTS["sku_complexity"]} pts</td><td style="padding:4px 12px;color:var(--muted)">Moins de variants = moins de risque d\'erreur en prep.</td></tr>
<tr><td style="padding:4px 12px"><strong>Signal de demande</strong></td><td style="padding:4px 12px">{SCORING_WEIGHTS["demand_signal"]} pts</td><td style="padding:4px 12px;color:var(--muted)">Vélocité réelle si disponible, sinon fallback sur stock (proxy imparfait).</td></tr>
<tr><td style="padding:4px 12px"><strong>Fit catégorie</strong></td><td style="padding:4px 12px">{SCORING_WEIGHTS["category_fit"]} pts</td><td style="padding:4px 12px;color:var(--muted)">Santé quotidienne &gt; sport &gt; accessoire/snack.</td></tr>
</table>
<div class="example"><strong>Seuils de verdict :</strong> score ≥ {VERDICT_THRESHOLDS["GO"]} → <span class="tag tag-go">GO</span>, score ≥ {VERDICT_THRESHOLDS["MAYBE"]} → <span class="tag tag-maybe">MAYBE</span>, sinon <span class="tag tag-nogo">NO-GO</span>.</div>
<div class="takeaway">👉 Les seuils ont été baissés par rapport à la V1 (75/55 → 70/50) pour faire basculer plus de produits en MAYBE et forcer une revue humaine plutôt qu\'un rejet automatique. Un produit MAYBE (50-69) a un ou deux critères fragiles mais peut devenir GO avec des ajustements (amélioration logistique, packaging, etc.).</div>
</div>
</section>'''

    # ── LTV Section ──
    horizon = metrics.get("horizon_months", HORIZON_MONTHS)
    scenario_order = ["optimiste", "baseline", "pessimiste"]
    scenario_labels = {
        "optimiste":  "🟢 Optimiste",
        "baseline":   "🟡 Baseline",
        "pessimiste": "🔴 Pessimiste",
    }
    curves_info = metrics["churn_curves"]

    html += f'''
<section id="ltv">
<h2>📈 Projections LTV (Lifetime Value) — HT</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">
LTV = Panier HT × (1 − remise) × durée de vie moyenne.
La durée de vie est calculée à partir d\'une <strong>courbe de churn multi-phases</strong>
(pas un taux plat) : cliff M1, décroissance M2-M3, plateau M4+.
Horizon de projection : <strong>{horizon} mois</strong>. Remise 15% appliquée. Chiffres en HT.
</p>
<div class="grid-3">'''

    for basket_label, basket_name in [("1_produit", "1 Produit"), ("2_produits", "2 Produits"), ("3_produits", "3 Produits")]:
        html += f'<div class="card"><h3>{basket_name}</h3><table style="font-size:12px">'
        html += '<tr><th>Scénario</th><th style="text-align:right">Durée moy.</th><th style="text-align:right">LTV plein tarif HT</th><th style="text-align:right">LTV abo HT (-15%)</th></tr>'
        for scenario in scenario_order:
            key = f"{basket_label}_{scenario}"
            ltv = metrics["ltv"][key]
            em = curves_info[scenario]["expected_months"]
            html += (
                f'<tr><td>{scenario_labels[scenario]}</td>'
                f'<td style="text-align:right">{em:.1f} mois</td>'
                f'<td style="text-align:right">{ltv["ltv_full_price"]:.0f}€</td>'
                f'<td style="text-align:right;font-weight:600;color:var(--orange)">{ltv["ltv_sub_price"]:.0f}€</td></tr>'
            )
        html += '</table></div>'

    html += '</div>'

    # Affichage des courbes de churn (phases)
    html += '<div class="card" style="margin-top:16px"><h3>Courbes de churn utilisées</h3><p style="font-size:12px;color:var(--muted);margin-bottom:8px">Taux de churn mensuel appliqué à chaque phase du cycle de vie de l\'abonné. Le cliff M1 est le plus violent en DTC compléments (20-35%).</p><table style="font-size:12px"><thead><tr><th>Phase</th><th style="text-align:right">🟢 Optimiste</th><th style="text-align:right">🟡 Baseline</th><th style="text-align:right">🔴 Pessimiste</th></tr></thead><tbody>'

    phase_labels = [
        ("M1 (cliff d\'essai)", 1),
        ("M2", 2),
        ("M3", 3),
        ("M4-M12 (plateau)", 4),
        ("M13+ (long-tail)", 13),
    ]
    for phase_name, month in phase_labels:
        html += f'<tr><td>{phase_name}</td>'
        for scenario in scenario_order:
            curve = curves_info[scenario]["curve"]
            rate = churn_at_month(curve, month)
            color = "#22c55e" if rate < 0.08 else "#f59e0b" if rate < 0.15 else "#ef4444"
            html += f'<td style="text-align:right;color:{color};font-weight:600">{rate*100:.0f}%/mois</td>'
        html += '</tr>'

    html += f'<tr style="border-top:2px solid var(--border);font-weight:700"><td>Durée de vie moyenne</td><td style="text-align:right">{curves_info["optimiste"]["expected_months"]:.1f} mois</td><td style="text-align:right">{curves_info["baseline"]["expected_months"]:.1f} mois</td><td style="text-align:right">{curves_info["pessimiste"]["expected_months"]:.1f} mois</td></tr></tbody></table></div>'

    # Panneau pédagogique LTV : explication formule + impact du cliff M1
    ex_basket = metrics["ltv"]["2_produits_baseline"]["basket_ht"]
    ex_em_base = curves_info["baseline"]["expected_months"]
    ex_em_pess = curves_info["pessimiste"]["expected_months"]
    ex_ltv_base = round(ex_basket * 0.85 * ex_em_base, 0)
    ex_ltv_pess = round(ex_basket * 0.85 * ex_em_pess, 0)
    ltv_drop_pct = round((1 - ex_ltv_pess / ex_ltv_base) * 100) if ex_ltv_base else 0
    html += f'''
<div class="edu-panel">
<h4>🎓 Pourquoi la LTV chute avec le cliff M1</h4>
<p>La Lifetime Value, c\'est combien d\'argent tu encaisses en moyenne par abonné sur toute sa durée de vie :</p>
<div class="formula">LTV_HT = panier_HT × (1 − remise) × durée_vie_moyenne</div>
<div class="example">
<strong>Exemple avec un panier de 2 produits ({ex_basket:.2f}€ HT), remise 15%, scénario baseline :</strong><br>
LTV = {ex_basket:.2f} × 0.85 × {ex_em_base:.1f} = <strong>{ex_ltv_base:.0f}€ HT</strong><br>
<br>
Avec un cliff M1 plus violent (pessimiste 35% vs baseline 25%), la durée de vie passe de {ex_em_base:.1f} à {ex_em_pess:.1f} mois → LTV tombe à <strong>{ex_ltv_pess:.0f}€ HT</strong> ({ltv_drop_pct}% de revenus en moins).
</div>
<div class="takeaway">👉 Le M1 est le mois le plus critique. Un onboarding raté multiplie par 2 le churn du premier mois et divise la LTV de 30%. C\'est pourquoi soigner le welcome email + le packaging + la clarté de l\'annulation sont les investissements les plus rentables.</div>
</div>
</section>'''

    # ── Cohort section ──
    html += f'''
<section id="cohort">
<h2>👥 Simulation Cohorte (100 abonnés, {horizon} mois) — HT</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Évolution d\'une cohorte de 100 abonnés démarrant en M1, panier = 2 produits GO moyen, remise 15%. Les barres montrent la recette HT mensuelle — le <strong>cliff M1-M3 est le vrai enjeu</strong> du programme.</p>
<div class="grid-3">'''

    for scenario in scenario_order:
        key = f"2_produits_{scenario}"
        cohort = metrics["ltv"][key]["cohort_100"]
        max_rev = max((c["month_revenue"] for c in cohort), default=0)
        em = curves_info[scenario]["expected_months"]

        html += f'''<div class="card">
<h3>{scenario_labels[scenario]}</h3>
<p style="font-size:11px;color:var(--muted);margin-bottom:8px">Durée de vie moyenne : <strong>{em:.1f} mois</strong></p>
<div class="cohort-chart">'''
        for c in cohort:
            h = (c["month_revenue"] / max_rev) * 180 if max_rev > 0 else 0
            html += f'<div class="cohort-bar" style="height:{h}px" title="M{c["month"]}: {c["subscribers"]:.0f} abo, {c["month_revenue"]:.0f}€ HT"><span>M{c["month"]}</span></div>'
        m12 = cohort[min(11, len(cohort)-1)]
        last = cohort[-1]
        html += f'''</div>
<table style="font-size:11px;margin-top:24px">
<tr><td>Abonnés restants M12</td><td style="text-align:right;font-weight:600">{m12["subscribers"]:.0f}</td></tr>
<tr><td>Abonnés restants M{horizon}</td><td style="text-align:right;font-weight:600">{last["subscribers"]:.0f}</td></tr>
<tr><td>CA HT cumulé M12</td><td style="text-align:right;font-weight:600;color:var(--orange)">{m12["cumulative_revenue"]:.0f}€</td></tr>
<tr><td>CA HT cumulé M{horizon}</td><td style="text-align:right;font-weight:700;color:var(--orange)">{last["cumulative_revenue"]:.0f}€</td></tr>
</table>
</div>'''

    html += '</div></section>'
    
    # ── Cross-sell ──
    html += f'''
<section id="crosssell">
<h2>🔗 Cross-sell : Bundles Recommandés pour Abonnement</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Basé sur les packs existants Shopify. Remise 15% + Point Relais ({LOGISTICS_HT["point_relais"]:.2f}€ HT). Prix affichés TTC, marges et contribution nette HT.</p>
<div class="grid-2">'''

    for bundle in metrics["cross_sell"]["bundle_economics"]:
        status = "rentable" if bundle["net_after_shipping_pr"] >= NET_CONTRIBUTION_RENTABLE else ("marginal" if bundle["net_after_shipping_pr"] >= NET_CONTRIBUTION_MARGINAL else "déficitaire")
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
<tr><td>Prix plein tarif TTC</td><td style="text-align:right">{bundle["full_price_ttc"]:.2f}€</td></tr>
<tr><td>Prix abo TTC (-15%)</td><td style="text-align:right;font-weight:600;color:var(--orange)">{bundle["sub_price_15pct_ttc"]:.2f}€</td></tr>
<tr><td>COGS total HT</td><td style="text-align:right;color:var(--muted)">{bundle["total_cogs"]:.2f}€</td></tr>
<tr><td>Marge HT après remise</td><td style="text-align:right;font-weight:600">{bundle["margin_after_disc"]:.2f}€</td></tr>
<tr><td>Net HT après port (PR)</td><td style="text-align:right"><span class="tag {status_tag}">{bundle["net_after_shipping_pr"]:.2f}€</span></td></tr>
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
    
    # ── Cannibalisation comportementale (split 3-voies) ──
    cannib_scenarios = metrics["cannibalization_behavioral"]
    html += '''
<section id="cannibalization">
<h2>⚠️ Cannibalisation vs valeur incrémentale (modèle 3-voies)</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Chaque nouvel abonné n\'est pas un "ancien client qu\'on remise de 15%". C\'est un mix de <strong>trois cohortes comportementales</strong> : nouveaux clients (100% incrémentaux), clients existants qu\'on sauve d\'un churn naturel (retention), et clients loyaux qui auraient racheté plein tarif (vraie cannibalisation). Chaque scénario de programme a un mix différent selon la qualité d\'acquisition.</p>
<div class="scenario-grid">'''

    for scenario_key in ["lean", "standard", "full"]:
        c = cannib_scenarios[scenario_key]
        pb = c["per_sub_breakdown"]
        mix = c["mix"]
        css_class = " standard" if scenario_key == "standard" else ""
        net_color = "var(--green)" if pb["net_annual"] > 0 else "var(--red)"
        html += f'''
<div class="scenario-card{css_class}">
    <h3>{c["label"]}</h3>
    <p style="font-size:11px;color:var(--muted);margin-bottom:12px">{mix["source"]}</p>
    <div class="scenario-kpi"><span>🟢 Nouveaux clients</span><strong>{mix["new_customer_rate"]*100:.0f}%</strong></div>
    <div class="scenario-kpi"><span>🟡 Retention save</span><strong>{mix["retention_save_rate"]*100:.0f}%</strong></div>
    <div class="scenario-kpi"><span>🔴 Loyalistes</span><strong>{mix["loyalist_rate"]*100:.0f}%</strong></div>
    <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border);font-size:12px">
        <div style="padding:4px 0;color:var(--green)">+ {pb["gain_new_annual"]:.0f}€/an gain new</div>
        <div style="padding:4px 0;color:#3b82f6">+ {pb["gain_retention_annual"]:.0f}€/an gain retention</div>
        <div style="padding:4px 0;color:var(--red)">− {pb["loss_loyalist_annual"]:.0f}€/an perte loyaliste</div>
    </div>
    <div class="scenario-kpi big"><span>Net / abo / an</span><span class="value" style="color:{net_color}">{pb["net_annual"]:+.0f}€</span></div>
</div>'''

    html += '''
</div>

<div class="edu-panel">
<h4>🎓 Pourquoi l\'abonnement est net-positif malgré la remise</h4>
<p>L\'intuition naïve : "si je remise 15%, je perds 15% de marge". Mauvaise analyse. La réalité c\'est que chaque nouvel abonné fait partie d\'un mix :</p>
<ul style="margin:8px 0;padding-left:20px">
<li><strong>Nouveaux clients</strong> (20-35% du mix selon le scénario) — auraient jamais acheté sans l\'abo → <strong>100% incrémental</strong>, gain = leur LTV complète</li>
<li><strong>Retention saves</strong> (30-40%) — anciens clients marginaux qui auraient churné après 2 commandes → on capture un <strong>uplift de 4 mois de contribution supplémentaire</strong></li>
<li><strong>Loyalistes</strong> (25-50%) — auraient racheté plein tarif → perte = 15% × 6 commandes/an du prix moyen</li>
</ul>
<div class="formula">Net_annual_per_sub = (%new × LTV) + (%retention × contrib × uplift) − (%loyalist × prix × remise × 6)</div>'''

    # Exemple chiffré sur le scénario standard
    std = cannib_scenarios["standard"]
    std_pb = std["per_sub_breakdown"]
    avg_contrib_std = metrics["break_even"]["avg_net_margin_per_sub_monthly"]
    avg_lifetime = std["lifetime_months_baseline"]
    html += f'''
<div class="example">
<strong>Exemple scénario standard :</strong> avg_contribution_mensuelle = {avg_contrib_std:.2f}€ HT, durée de vie = {avg_lifetime:.1f} mois, uplift retention = {RETENTION_UPLIFT_MONTHS:.0f} mois, prix moyen GO = {metrics["portfolio"]["avg_price_go_ht"]}€ HT, {LOYALIST_ORDERS_PER_YEAR} commandes/an par loyaliste<br>
• Gain new : 0.25 × {avg_contrib_std:.2f} × {avg_lifetime:.1f} = <strong>{std_pb["gain_new_annual"]:.0f}€</strong><br>
• Gain retention : 0.35 × {avg_contrib_std:.2f} × {RETENTION_UPLIFT_MONTHS:.0f} = <strong>{std_pb["gain_retention_annual"]:.0f}€</strong><br>
• Perte loyaliste : 0.40 × {metrics["portfolio"]["avg_price_go_ht"]} × 0.15 × {LOYALIST_ORDERS_PER_YEAR} = <strong>{std_pb["loss_loyalist_annual"]:.0f}€</strong><br>
• <strong>Net = +{std_pb["net_annual"]:.0f}€/abo/an</strong> ({std_pb["net_monthly"]:.2f}€/mois)
</div>
<div class="takeaway">👉 Le programme est <strong>net-positif dès le premier abonné</strong> dans les 3 scénarios, contrairement à ce que suggère l\'analyse naïve "remise × subs". Le levier principal c\'est la <strong>qualité du mix d\'acquisition</strong> : plus tu attires de nouveaux clients (paid ads, partenariats) vs cannibalisant ta liste email, plus le programme est rentable.</div>
</div>

<h3 style="margin-top:24px">💡 Cannibalisation par produit <span class="badge-illustrative">ILLUSTRATIF</span></h3>
<p style="font-size:12px;color:var(--muted);margin-bottom:8px">Projection basée sur l\'hypothèse illustrative de <strong>{ILLUSTRATIVE_ORDERS_PER_PRODUCT} commandes/mois/produit</strong>. Ces chiffres sont des ordres de grandeur, pas des prédictions — ne pas les utiliser pour dimensionner un budget. Pour des projections absolues fiables, il faut un export Shopify 90 jours.</p>
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
    <th style="text-align:right;font-size:10px">Perte HT €/mois</th>
    <th style="text-align:right;font-size:10px">Perte %</th>
    <th style="text-align:right;font-size:10px">Perte HT €/mois</th>
    <th style="text-align:right;font-size:10px">Perte %</th>
</tr>
</thead>
<tbody>'''

    cann = metrics["cannibalization"]
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
<p style="font-size:12px;color:var(--muted);margin-top:8px">⚠️ Cette projection est une <strong>vue unitaire</strong> (combien d\'euros bruts sont décalés par produit). Pour comprendre l\'impact net réel du programme, voir l\'analyse comportementale au-dessus qui intègre les gains incrémentaux.</p>
</div></section>'''
    
    # ── Break-even (3 scénarios + panneau pédagogique) ──
    be_all = metrics["break_even_by_scenario"]
    avg_contrib = metrics["break_even"]["avg_net_margin_per_sub_monthly"]
    html += f'''
<section id="breakeven">
<h2>💰 Seuil de Rentabilité — 3 scénarios de programme</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">Selon la stack technique choisie (Lean MVP / Standard DTC / Full retention), les coûts et le break-even varient fortement. Le scénario <strong>Standard</strong> est le cas de référence présenté par défaut.</p>
<div class="scenario-grid">'''

    for scenario_key in ["lean", "standard", "full"]:
        be = be_all[scenario_key]
        scen_meta = PROGRAM_SCENARIOS[scenario_key]
        css_class = " standard" if scenario_key == "standard" else ""
        html += f'''
<div class="scenario-card{css_class}">
    <h3>{be["label"]}</h3>
    <div class="scenario-desc">{scen_meta["description"]}</div>
    <div class="scenario-kpi"><span>Setup HT</span><strong>{be["setup_onetime_ht"]}€</strong></div>
    <div class="scenario-kpi"><span>App HT / mois</span><strong>{be["app_monthly_ht"]}€</strong></div>
    <div class="scenario-kpi"><span>Durée de vie moy.</span><strong>{be["lifetime_months"]:.1f} mois</strong></div>
    <div class="scenario-kpi"><span>Contrib. lifetime / abo</span><strong>{be["lifetime_contribution_per_sub_ht"]:.0f}€ HT</strong></div>
    <div class="scenario-kpi big"><span>Abonnés actifs requis</span><span class="value">{be["running_break_even_subs"]}</span></div>
    <div class="scenario-kpi big"><span>Nouveaux abos setup</span><span class="value">{be["setup_break_even_new_subs"]}</span></div>
    <div style="font-size:11px;color:var(--muted);margin-top:8px;line-height:1.4">💡 {scen_meta["app_source"]}</div>
</div>'''

    html += f'''
</div>

<div class="edu-panel">
<h4>🎓 Comprendre le calcul du break-even</h4>
<p>On calcule deux choses distinctes :</p>
<div class="formula">running_break_even = coût mensuel de l\'app / contribution nette mensuelle par abo</div>
<div class="formula">setup_break_even = coût setup / (contribution mensuelle × durée de vie moyenne)</div>
<div class="example">
<strong>Exemple (Standard, contribution moyenne {avg_contrib:.2f}€ HT/mois) :</strong><br>
• Running : {be_all["standard"]["app_monthly_ht"]}€ / {avg_contrib:.2f}€ = <strong>{be_all["standard"]["running_break_even_subs"]} abonnés actifs</strong> pour couvrir l\'app chaque mois<br>
• Setup : chaque nouvel abo contribue {avg_contrib:.2f}€ × {be_all["standard"]["lifetime_months"]:.1f} mois = {be_all["standard"]["lifetime_contribution_per_sub_ht"]:.0f}€ sur sa vie → il faut {be_all["standard"]["app_monthly_ht"] and be_all["standard"]["setup_break_even_new_subs"]} nouveaux abos pour amortir les {be_all["standard"]["setup_onetime_ht"]}€ de setup
</div>
<div class="takeaway">👉 Le running break-even est indépendant du churn. Le setup break-even dépend du churn parce qu\'il faut que les abonnés vivent assez longtemps pour amortir l\'investissement initial. C\'est pourquoi le Full scénario (churn pessimiste) demande bien plus de nouveaux abonnés malgré une contribution unitaire identique.</div>
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
    multivit_ttc_example = 18.90
    multivit_ht_example = round(multivit_ttc_example / (1 + TVA_RATE), 2)
    html += f'''
<section id="methodology">
<h2>📋 Méthodologie & Sources</h2>

<div class="methodology">
<h4>Sources de données</h4>
<ul>
    <li><strong>Prix retail vitrine (TTC)</strong> — Shopify MCP API, 96 produits extraits le 10/04/2026. Convertis en HT via /1.20 pour les calculs de marge.</li>
    <li><strong>COGS HT (Prix de Cession 2026)</strong> — Document interne HCS fourni par Antoine (image), 42 SKUs. Hypothèse : valeurs HT (prix de gros fournisseur, TVA récupérable). À confirmer avec la compta HCS.</li>
    <li><strong>Coûts logistiques</strong> — Tarifs réels Impulse Nutrition en TTC : Point Relais {LOGISTICS_TTC["point_relais"]:.2f}€, Domicile {LOGISTICS_TTC["domicile"]:.2f}€, Express {LOGISTICS_TTC["express"]:.2f}€ — convertis en HT ({LOGISTICS_HT["point_relais"]:.2f}€ / {LOGISTICS_HT["domicile"]:.2f}€ / {LOGISTICS_HT["express"]:.2f}€) pour les calculs.</li>
    <li><strong>Benchmark concurrents</strong> — Web scraping + analyse manuelle, 8 marques, données collectées avril 2026 (prix affichés TTC, perception client).</li>
    <li><strong>Données marché</strong> — Xerfi, Euromonitor, Grand View Research, PwC France (via recherches web).</li>
    <li><strong>Courbes de churn DTC compléments</strong> — Courbes multi-phases avec cliff M1, décroissance M2-M3, plateau M4-M12, long-tail M13+. 3 scénarios (optimiste / baseline / pessimiste). Sources : benchmarks publics Harry's, Dollar Shave Club, Ritual ; podcasts Cuure/Nutri&Co ; rapports Recurly DTC.</li>
</ul>
</div>

<div class="methodology" style="margin-top:16px">
<h4>🔑 Convention HT / TTC</h4>
<p style="margin-bottom:8px"><strong>Règle d\'or : tous les calculs de rentabilité sont en HT.</strong> Taux de TVA appliqué : <strong>{TVA_RATE*100:.0f}%</strong> (taux standard France sur compléments alimentaires).</p>
<ul>
    <li><strong>Prix retail HT</strong> = Prix TTC / {1+TVA_RATE:.2f}. Exemple : Multivit {multivit_ttc_example:.2f}€ TTC → {multivit_ht_example:.2f}€ HT.</li>
    <li><strong>COGS</strong> sont déjà en HT dans l\'image source (prix de cession fournisseur, TVA récupérable).</li>
    <li><strong>Coûts logistiques HT</strong> = Facture transporteur TTC / {1+TVA_RATE:.2f}. La TVA est récupérable donc le coût réel pour l\'entreprise est le HT.</li>
    <li><strong>Prix affichés au client</strong> (tableau produits, comparaison concurrents, seuils panier) restent en TTC — c\'est la perception vitrine.</li>
</ul>
</div>

<div class="methodology" style="margin-top:16px">
<h4>Formules de calcul (HT)</h4>
<ul>
    <li><strong>Marge brute HT</strong> = Prix retail HT − COGS HT</li>
    <li><strong>Marge brute % HT</strong> = Marge brute HT / Prix retail HT × 100</li>
    <li><strong>Marge HT après remise</strong> = Prix retail HT × (1 − remise) − COGS HT</li>
    <li><strong>Contribution nette HT</strong> = Marge HT après remise − Frais de port HT</li>
    <li><strong>LTV HT</strong> = Panier HT × (1 − remise) × durée de vie moyenne. La durée de vie moyenne est calculée à partir d\'une courbe de churn mensuelle multi-phases (expected_months = somme sur l\'horizon de la probabilité d\'être encore actif chaque mois).</li>
    <li><strong>Score abonnement</strong> = Récurrence (/30) + Marge viable (/25) + Complexité SKU (/15) + Concurrents (/15) + Demande (/10) + Catégorie (/5)</li>
    <li><strong>Cannibalisation</strong> = perte de recettes HT due à la remise, avant effet de rétention</li>
</ul>
</div>

<div class="methodology" style="margin-top:16px">
<h4>Hypothèses & limites</h4>
<ul>
    <li>Taux de TVA uniforme à {TVA_RATE*100:.0f}% — à valider : certaines boissons d\'effort à reconstituer pourraient être à 5.5% selon la qualification fiscale HCS.</li>
    <li>Les COGS des électrolytes effervescents sont estimés à 1.50€ HT (absent de l\'image COGS, produit récent) — à confirmer fournisseur.</li>
    <li>L\'hypothèse de {ILLUSTRATIVE_ORDERS_PER_PRODUCT} commandes/mois/produit est purement <strong>illustrative</strong> (badge visible sur les sections concernées). Elle n\'affecte pas les décisions stratégiques (scoring, ranking, break-even unitaires) mais sert à projeter des valeurs absolues pour donner une intuition de l\'ordre de grandeur.</li>
    <li>Les courbes de churn (optimiste 15/8/6/4/2 — baseline 25/12/8/5/3 — pessimiste 35/18/12/7/5) sont des benchmarks DTC compléments, pas des données Impulse. À remesurer 6 mois après lancement pour recalibrer le modèle.</li>
    <li>La cannibalisation suppose que les clients convertis auraient acheté au plein tarif — en réalité, certains auraient churné.</li>
    <li>Les coûts de setup ({SETUP_COST_ONETIME}€ HT) et d\'app ({MONTHLY_APP_COST}€ HT/mois) sont des <strong>bornes basses</strong> — Recharge/Loop/PayWhirl peuvent facturer jusqu\'à 200€/mois selon le volume. Devis à obtenir.</li>
</ul>
</div>'''

    html += '''
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
    for scenario in ["optimiste", "baseline", "pessimiste"]:
        ltv = metrics['ltv'][f'2_produits_{scenario}']
        em = metrics['churn_curves'][scenario]['expected_months']
        print(f"  LTV 2 prod, {scenario:11} ({em:.1f} mois): {ltv['ltv_sub_price']:.0f}€ HT")
