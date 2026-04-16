#!/usr/bin/env python3
"""
H2 Refactored: Custom Box Quantity-Based Model
- Single delivery frequency per cycle (1/2/3 months)
- Quantity per product varies based on consumption rate
- Personalized recommendations based on weight/training/goals
- Minimizes shipments = lower logistics cost
"""
import json, math, re

# ── Load enriched data ──
with open('benchmark/impulse_products_enriched.json') as f:
    data = json.load(f)
products = data['products']
by_sku = {p['sku']: p for p in products}

# ── Real consumption rates (days per unit) ──
# Already in data as 'consumption_days'
# Whey 20j, BCAA 30j, Multivit 30j, VitD 60j, Electrolytes 20j, etc.

# ── Helper: compute quantities needed for a cycle ──
def qty_for_cycle(sku, cycle_months):
    """How many units needed to cover cycle_months"""
    p = by_sku[sku]
    days_in_cycle = cycle_months * 30
    conso = p['consumption_days']
    if conso >= 365:  # accessories, skip
        return 0
    return math.ceil(days_in_cycle / conso)

# ── Personalization factors ──
# Weight-based adjustments for protein products
WEIGHT_FACTORS = {
    'light': {'label': '< 65 kg', 'protein_factor': 0.8, 'desc': 'Besoins protéiques modérés'},
    'medium': {'label': '65-85 kg', 'protein_factor': 1.0, 'desc': 'Besoins protéiques standards'},
    'heavy': {'label': '> 85 kg', 'protein_factor': 1.3, 'desc': 'Besoins protéiques élevés'},
}

# Training frequency adjustments for workout supplements
TRAINING_FACTORS = {
    'moderate': {'label': '2-3x/sem', 'workout_factor': 0.7, 'desc': 'Sportif régulier'},
    'active': {'label': '4-5x/sem', 'workout_factor': 1.0, 'desc': 'Sportif assidu'},
    'intense': {'label': '6-7x/sem', 'workout_factor': 1.3, 'desc': 'Athlète / compétiteur'},
}

# SKUs affected by weight (protein-related)
PROTEIN_SKUS = {'VSWHEYC', 'VSWHEYN', 'VSWHEYV', 'VSRECMC', 'VSRECMV', 'VSBCAAC', 'VSBCAAP', 'VSLGLU', 'VSCREAC'}
# SKUs affected by training frequency (workout supplements)
WORKOUT_SKUS = {'VSPREWC', 'VSBOISM', 'VSBOISF', 'VSMAL', 'VSELECC', 'VSELECP', 'VSELEFC', 'VSELEFCV', 'VSELEFP'}

def adjusted_qty(sku, cycle_months, weight='medium', training='active'):
    """Quantity adjusted for weight and training"""
    base = qty_for_cycle(sku, cycle_months)
    if base == 0:
        return 0
    factor = 1.0
    if sku in PROTEIN_SKUS:
        factor *= WEIGHT_FACTORS[weight]['protein_factor']
    if sku in WORKOUT_SKUS:
        factor *= TRAINING_FACTORS[training]['workout_factor']
    return max(1, math.ceil(base * factor))

# ── 3 Client Profiles with quantity-based boxes ──
PROFILES = {
    'muscu': {
        'name': '💪 Objectif Prise de Masse',
        'icon': '💪',
        'weight': 'heavy',
        'training': 'intense',
        'goal': 'Prise de masse / musculation intensive',
        'cycle_months': 3,
        'products': [
            {'sku': 'VSWHEYC', 'reason': 'Apport protéique quotidien post-training'},
            {'sku': 'VSCREAC', 'reason': 'Créatine quotidienne — performance & récupération'},
            {'sku': 'VSBCAAP', 'reason': 'BCAA intra-training — préservation musculaire'},
            {'sku': 'VSMVIT', 'reason': 'Micronutriments essentiels — base quotidienne'},
            {'sku': 'VSOME', 'reason': 'Omega 3 — inflammation & récupération'},
            {'sku': 'VSLGLU', 'reason': 'L-Glutamine — récupération intensive'},
        ]
    },
    'endurance': {
        'name': '🏃 Objectif Endurance / Trail',
        'icon': '🏃',
        'weight': 'medium',
        'training': 'active',
        'goal': 'Performance endurance / trail / running',
        'cycle_months': 2,
        'products': [
            {'sku': 'VSBOISM', 'reason': 'Boisson effort — séances longues'},
            {'sku': 'VSELECP', 'reason': 'Électrolytes — hydratation optimale'},
            {'sku': 'VSMAL', 'reason': 'Maltodextrine — énergie longue durée'},
            {'sku': 'VSMAG', 'reason': 'Magnésium — crampes & récupération'},
            {'sku': 'VSCOLMN', 'reason': 'Collagène marin — articulations sollicitées'},
            {'sku': 'VSVITD', 'reason': 'Vitamine D — immunité sportifs outdoor'},
        ]
    },
    'sante': {
        'name': '💊 Objectif Bien-être / Santé',
        'icon': '💊',
        'weight': 'light',
        'training': 'moderate',
        'goal': 'Bien-être général / santé au quotidien',
        'cycle_months': 3,
        'products': [
            {'sku': 'VSMVIT', 'reason': 'Base micronutritionnelle quotidienne'},
            {'sku': 'VSOME', 'reason': 'Omega 3 — cardiovasculaire & cognition'},
            {'sku': 'VSMAG', 'reason': 'Magnésium — stress & sommeil'},
            {'sku': 'VSSOM', 'reason': 'Sommeil — qualité de récupération nocturne'},
            {'sku': 'VSPBIOT', 'reason': 'Probiotiques — santé digestive'},
            {'sku': 'VSVITD', 'reason': 'Vitamine D — immunité (1 pot/3 mois suffit)'},
        ]
    }
}

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import LOGISTICS_HT, LOGISTICS_TTC, TVA_RATE

DISCOUNT = 0.15  # -15% on subscription
SHIPPING_PR = LOGISTICS_HT["point_relais"]       # HT pour les calculs de marge
SHIPPING_PR_TTC = LOGISTICS_TTC["point_relais"]  # TTC pour affichage client

print("=" * 80)
print("H2 REFACTORED: CUSTOM BOX — QUANTITY-BASED MODEL")
print("=" * 80)

profile_results = {}

for pk, prof in PROFILES.items():
    cycle = prof['cycle_months']
    w = prof['weight']
    t = prof['training']
    
    print(f"\n{'─' * 60}")
    print(f"{prof['name']} — Cycle de {cycle} mois")
    print(f"Profil: {WEIGHT_FACTORS[w]['label']}, {TRAINING_FACTORS[t]['label']}")
    print(f"{'─' * 60}")
    
    items = []
    total_retail_ttc = 0
    total_retail_ht = 0
    total_cogs_ht = 0

    for prod in prof['products']:
        p = by_sku[prod['sku']]
        qty = adjusted_qty(prod['sku'], cycle, w, t)
        retail_ttc = p['retail_price_ttc']
        retail_ht = p['retail_price_ht']
        cogs_unit = p['cogs_ht']
        line_retail_ttc = retail_ttc * qty
        line_retail_ht = retail_ht * qty
        line_cogs = cogs_unit * qty
        total_retail_ttc += line_retail_ttc
        total_retail_ht += line_retail_ht
        total_cogs_ht += line_cogs
        items.append({
            'sku': prod['sku'],
            'title': p['title'],
            'reason': prod['reason'],
            'conso_days': p['consumption_days'],
            'qty': qty,
            'unit_price': retail_ttc,        # TTC affiché
            'unit_price_ht': retail_ht,
            'unit_cogs': cogs_unit,           # HT
            'line_total': line_retail_ttc,    # TTC affiché
            'line_total_ht': line_retail_ht,
            'line_cogs': line_cogs,           # HT
        })
        print(f"  {p['title']:35} | {p['consumption_days']:2}j/unité → {qty:2}x | {retail_ttc:6.2f}€ TTC × {qty} = {line_retail_ttc:7.2f}€")

    # Affichage client (TTC)
    total_sub_ttc = total_retail_ttc * (1 - DISCOUNT)
    savings_ttc = total_retail_ttc - total_sub_ttc
    monthly_payment_ttc = total_sub_ttc / cycle

    # Marge (HT)
    total_sub_ht = total_retail_ht * (1 - DISCOUNT)

    # Only 1 shipment per cycle (the whole point!)
    shipments_per_year = 12 // cycle
    shipping_annual_ht = shipments_per_year * SHIPPING_PR

    # Annual projections (HT pour la marge, TTC pour l'affichage CA client)
    annual_retail_ttc = total_retail_ttc * (12 / cycle)
    annual_sub_ttc = total_sub_ttc * (12 / cycle)
    annual_sub_ht = total_sub_ht * (12 / cycle)
    annual_cogs_ht = total_cogs_ht * (12 / cycle)
    annual_margin_ht = annual_sub_ht - annual_cogs_ht - shipping_annual_ht

    # Compat legacy pour le rendu HTML existant
    total_retail = total_retail_ttc
    total_sub = total_sub_ttc
    savings = savings_ttc
    monthly_payment = monthly_payment_ttc
    total_cogs = total_cogs_ht
    shipping_annual = shipping_annual_ht
    annual_retail = annual_retail_ttc
    annual_sub = annual_sub_ttc
    annual_cogs = annual_cogs_ht
    annual_margin = annual_margin_ht
    
    # vs frequency model (old H2): 12 shipments/year
    old_shipping = 12 * SHIPPING_PR
    shipping_saved = old_shipping - shipping_annual
    
    print(f"\n  📦 RÉSUMÉ DU COLIS (1 livraison / {cycle} mois):")
    print(f"  Prix catalogue:  {total_retail:8.2f}€")
    print(f"  Prix abonné (-{DISCOUNT*100:.0f}%): {total_sub:8.2f}€ (économie {savings:.2f}€)")
    print(f"  💳 Mensualité:   {monthly_payment:8.2f}€/mois")
    print(f"  COGS total:      {total_cogs:8.2f}€")
    print(f"  Marge brute/colis: {total_sub - total_cogs:8.2f}€ ({(total_sub - total_cogs)/total_sub*100:.0f}%)")
    print(f"\n  📊 PROJECTION ANNUELLE:")
    print(f"  CA abonné:       {annual_sub:8.2f}€")
    print(f"  COGS:            {annual_cogs:8.2f}€")
    print(f"  Shipping ({shipments_per_year} envois): {shipping_annual:8.2f}€")
    print(f"  📈 Marge nette:  {annual_margin:8.2f}€/an")
    print(f"  🚚 Économie shipping vs fréquence: {shipping_saved:.2f}€/an ({shipments_per_year} envois vs 12)")
    
    profile_results[pk] = {
        'name': prof['name'],
        'icon': prof['icon'],
        'goal': prof['goal'],
        'cycle': cycle,
        'weight': WEIGHT_FACTORS[w]['label'],
        'training': TRAINING_FACTORS[t]['label'],
        'items': items,
        'total_retail': total_retail,
        'total_sub': total_sub,
        'savings': savings,
        'monthly_payment': monthly_payment,
        'total_cogs': total_cogs,
        'shipments_per_year': shipments_per_year,
        'shipping_annual': shipping_annual,
        'annual_sub': annual_sub,
        'annual_cogs': annual_cogs,
        'annual_margin': annual_margin,
        'shipping_saved': shipping_saved,
        'margin_pct': (annual_sub - annual_cogs) / annual_sub * 100
    }

# ── Comparison table: Quantity vs Frequency model ──
print(f"\n{'=' * 80}")
print("COMPARAISON: MODÈLE QUANTITÉ vs MODÈLE FRÉQUENCE")
print(f"{'=' * 80}")
print(f"{'Métrique':35} | {'Fréquence (ancien H2)':22} | {'Quantité (nouveau H2)':22}")
print(f"{'─' * 35}-+-{'─' * 22}-+-{'─' * 22}")
print(f"{'Livraisons/an':35} | {'12':>22} | {'4-6':>22}")
print(f"{'Coût shipping/an (PR)':35} | {'46.80€':>22} | {'15.60-23.40€':>22}")
print(f"{'Complexité logistique':35} | {'Élevée (multi-freq)':>22} | {'Simple (1 freq)':>22}")
print(f"{'Personnalisation':35} | {'Par fréquence':>22} | {'Par quantité + reco':>22}")
print(f"{'Poids colis moyen':35} | {'Léger (1-2 produits)':>22} | {'Lourd (5-8 produits)':>22}")
print(f"{'Upsell naturel':35} | {'Faible':>22} | {'Fort (reco moteur)':>22}")
print(f"{'Expérience unboxing':35} | {'Banale':>22} | {'Premium (box complète)':>22}")

# ── Shipping weight analysis ──
print(f"\n{'=' * 80}")
print("ANALYSE POIDS COLIS — viabilité Colissimo/Mondial Relay")
print(f"{'=' * 80}")

# Estimated weights per product (grams)
WEIGHTS = {
    'VSWHEYC': 750, 'VSWHEYN': 750, 'VSWHEYV': 750,
    'VSRECMC': 750, 'VSRECMV': 750,
    'VSCREAC': 300, 'VSBCAAP': 250, 'VSBCAAC': 250,
    'VSMVIT': 80, 'VSOME': 100, 'VSSOM': 80, 'VSFER': 60,
    'VSVITC': 60, 'VSPBIOT': 80, 'VSCUR': 80, 'VSVITD': 60,
    'VSMAG': 100, 'VSLGLU': 250, 'VSGLY': 300,
    'VSCOLBC': 300, 'VSCOLBE': 300, 'VSCOLBN': 250,
    'VSCOLMC': 300, 'VSCOLME': 300, 'VSCOLMN': 250,
    'VSPREWC': 250, 'VSMAL': 500,
    'VSBOISM': 450, 'VSBOISF': 450,
    'VSELECC': 250, 'VSELECP': 250,
    'VSELEFC': 100, 'VSELEFCV': 100, 'VSELEFP': 100,
    'VSSPI': 120,
}

for pk, res in profile_results.items():
    total_weight = 0
    for item in res['items']:
        w = WEIGHTS.get(item['sku'], 100)
        total_weight += w * item['qty']
    print(f"{res['name']:35} | {total_weight/1000:.1f} kg | {'⚠️ > 5kg' if total_weight > 5000 else '✅ OK'} | {len(res['items'])} produits, {sum(i['qty'] for i in res['items'])} unités")
    profile_results[pk]['total_weight_kg'] = total_weight / 1000

# ── Now inject into HTML ──
print(f"\n{'=' * 80}")
print("INJECTION HTML EN COURS...")
print(f"{'=' * 80}")

with open('benchmark/rapport_rentabilite_abonnement.html', 'r') as f:
    html = f.read()

# Build the new H2 section HTML
def build_h2_html():
    h = []
    h.append('''
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- H2 REFACTORED: CUSTOM BOX QUANTITY-BASED                   -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div id="h2-quantity" style="margin-top:40px; padding:30px; background:linear-gradient(135deg, #f0f4ff 0%, #fff5f0 100%); border-radius:16px; border:2px solid #F05A28;">
        <h3 style="color:#1B2B4B; font-size:1.5rem; margin-bottom:5px;">
            ⭐ Hypothèse 2 — Box Custom Quantity-Based
        </h3>
        <p style="color:#666; margin-bottom:20px; font-size:0.95rem;">
            <strong>Principe clé :</strong> Le client choisit ses produits et son cycle de livraison (1, 2 ou 3 mois). 
            Les <em>quantités</em> de chaque produit s'ajustent automatiquement à la durée du cycle selon la vitesse de consommation réelle.
            <strong>Résultat : 1 seule livraison par cycle</strong>, pas de micro-colis, coût shipping divisé par 2 à 3.
        </p>

        <!-- Concept visuel -->
        <div style="background:white; border-radius:12px; padding:20px; margin-bottom:25px; border-left:4px solid #F05A28;">
            <h4 style="color:#F05A28; margin-bottom:12px;">🧠 Comment ça fonctionne</h4>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; text-align:center;">
                <div style="background:#f8f9fa; padding:15px; border-radius:10px;">
                    <div style="font-size:2rem;">🎯</div>
                    <div style="font-weight:600; color:#1B2B4B; margin:8px 0;">1. Profil</div>
                    <div style="font-size:0.85rem; color:#666;">Poids, fréquence d'entraînement, objectif</div>
                </div>
                <div style="background:#f8f9fa; padding:15px; border-radius:10px;">
                    <div style="font-size:2rem;">📦</div>
                    <div style="font-weight:600; color:#1B2B4B; margin:8px 0;">2. Sélection</div>
                    <div style="font-size:0.85rem; color:#666;">Choix des produits + cycle (1/2/3 mois)</div>
                </div>
                <div style="background:#f8f9fa; padding:15px; border-radius:10px;">
                    <div style="font-size:2rem;">⚖️</div>
                    <div style="font-weight:600; color:#1B2B4B; margin:8px 0;">3. Quantités auto</div>
                    <div style="font-size:0.85rem; color:#666;">Ajustées selon la conso réelle par produit</div>
                </div>
                <div style="background:#f8f9fa; padding:15px; border-radius:10px;">
                    <div style="font-size:2rem;">💳</div>
                    <div style="font-weight:600; color:#1B2B4B; margin:8px 0;">4. Paiement lissé</div>
                    <div style="font-size:0.85rem; color:#666;">Montant total ÷ nb de mois = mensualité fixe</div>
                </div>
            </div>
        </div>

        <!-- Personalization engine -->
        <div style="background:white; border-radius:12px; padding:20px; margin-bottom:25px; border-left:4px solid #1B2B4B;">
            <h4 style="color:#1B2B4B; margin-bottom:12px;">⚙️ Moteur de personnalisation</h4>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                <div>
                    <h5 style="color:#F05A28; margin-bottom:8px;">Ajustement par poids corporel</h5>
                    <table style="width:100%; font-size:0.85rem; border-collapse:collapse;">
                        <tr style="background:#f8f9fa;"><th style="padding:6px; text-align:left;">Profil</th><th style="text-align:center;">Facteur protéines</th><th style="text-align:left;">Effet</th></tr>
                        <tr><td style="padding:6px;">< 65 kg</td><td style="text-align:center;">×0.8</td><td>Moins de whey/BCAA/créatine</td></tr>
                        <tr style="background:#f8f9fa;"><td style="padding:6px;">65-85 kg</td><td style="text-align:center;">×1.0</td><td>Quantités standard</td></tr>
                        <tr><td style="padding:6px;">> 85 kg</td><td style="text-align:center;">×1.3</td><td>Plus de protéines par cycle</td></tr>
                    </table>
                </div>
                <div>
                    <h5 style="color:#F05A28; margin-bottom:8px;">Ajustement par fréquence d'entraînement</h5>
                    <table style="width:100%; font-size:0.85rem; border-collapse:collapse;">
                        <tr style="background:#f8f9fa;"><th style="padding:6px; text-align:left;">Fréquence</th><th style="text-align:center;">Facteur workout</th><th style="text-align:left;">Effet</th></tr>
                        <tr><td style="padding:6px;">2-3×/sem</td><td style="text-align:center;">×0.7</td><td>Moins de preworkout/boisson</td></tr>
                        <tr style="background:#f8f9fa;"><td style="padding:6px;">4-5×/sem</td><td style="text-align:center;">×1.0</td><td>Quantités standard</td></tr>
                        <tr><td style="padding:6px;">6-7×/sem</td><td style="text-align:center;">×1.3</td><td>Davantage de suppléments training</td></tr>
                    </table>
                </div>
            </div>
            <p style="margin-top:12px; font-size:0.85rem; color:#888; font-style:italic;">
                💡 Exemple : un athlète de 90kg qui s'entraîne 6×/sem recevra ~30% de whey en plus et ~30% de preworkout en plus qu'un sportif de 70kg à 3×/sem.
            </p>
        </div>
    ''')

    # Profile cards
    for pk, res in profile_results.items():
        cycle = res['cycle']
        h.append(f'''
        <div style="background:white; border-radius:12px; padding:20px; margin-bottom:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <div>
                    <h4 style="color:#1B2B4B; margin:0;">{res['name']}</h4>
                    <span style="font-size:0.85rem; color:#666;">{res['goal']} | {res['weight']}, {res['training']}</span>
                </div>
                <div style="background:#F05A28; color:white; padding:8px 16px; border-radius:20px; font-weight:700; font-size:1.1rem;">
                    {res['monthly_payment']:.2f}€/mois
                </div>
            </div>
            
            <div style="display:flex; gap:15px; margin-bottom:15px;">
                <div style="flex:1; background:#f0f4ff; padding:12px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.75rem; color:#666;">📦 Cycle</div>
                    <div style="font-size:1.2rem; font-weight:700; color:#1B2B4B;">Tous les {cycle} mois</div>
                </div>
                <div style="flex:1; background:#fff5f0; padding:12px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.75rem; color:#666;">🚚 Livraisons/an</div>
                    <div style="font-size:1.2rem; font-weight:700; color:#F05A28;">{res['shipments_per_year']} seulement</div>
                </div>
                <div style="flex:1; background:#f0fff0; padding:12px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.75rem; color:#666;">⚖️ Poids colis</div>
                    <div style="font-size:1.2rem; font-weight:700; color:#27ae60;">{res['total_weight_kg']:.1f} kg</div>
                </div>
                <div style="flex:1; background:#fffff0; padding:12px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.75rem; color:#666;">💰 Économie/an</div>
                    <div style="font-size:1.2rem; font-weight:700; color:#f39c12;">{res['savings'] * 12/cycle:.0f}€</div>
                </div>
            </div>

            <table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
                <thead>
                    <tr style="background:#1B2B4B; color:white;">
                        <th style="padding:8px; text-align:left; border-radius:6px 0 0 0;">Produit</th>
                        <th style="padding:8px; text-align:center;">Durée/unité</th>
                        <th style="padding:8px; text-align:center;">Qté/{cycle} mois</th>
                        <th style="padding:8px; text-align:center;">Prix unitaire</th>
                        <th style="padding:8px; text-align:center;">Sous-total</th>
                        <th style="padding:8px; text-align:left; border-radius:0 6px 0 0;">Pourquoi</th>
                    </tr>
                </thead>
                <tbody>''')
        
        for i, item in enumerate(res['items']):
            bg = '#f8f9fa' if i % 2 == 0 else 'white'
            h.append(f'''
                    <tr style="background:{bg};">
                        <td style="padding:8px; font-weight:600;">{item['title']}</td>
                        <td style="padding:8px; text-align:center;">{item['conso_days']}j</td>
                        <td style="padding:8px; text-align:center; font-weight:700; color:#F05A28;">{item['qty']}×</td>
                        <td style="padding:8px; text-align:center;">{item['unit_price']:.2f}€</td>
                        <td style="padding:8px; text-align:center; font-weight:600;">{item['line_total']:.2f}€</td>
                        <td style="padding:8px; font-size:0.8rem; color:#666;">{item['reason']}</td>
                    </tr>''')
        
        h.append(f'''
                </tbody>
                <tfoot>
                    <tr style="background:#1B2B4B; color:white; font-weight:700;">
                        <td style="padding:10px; border-radius:0 0 0 6px;" colspan="2">TOTAL COLIS</td>
                        <td style="padding:10px; text-align:center;">{sum(i['qty'] for i in res['items'])} unités</td>
                        <td style="padding:10px; text-align:center;"></td>
                        <td style="padding:10px; text-align:center;">{res['total_retail']:.2f}€</td>
                        <td style="padding:10px; border-radius:0 0 6px 0;"></td>
                    </tr>
                </tfoot>
            </table>

            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin-top:15px;">
                <div style="background:#f8f9fa; padding:12px; border-radius:8px;">
                    <div style="font-size:0.75rem; color:#888;">Prix catalogue ({cycle} mois)</div>
                    <div style="font-size:1rem; text-decoration:line-through; color:#999;">{res['total_retail']:.2f}€</div>
                </div>
                <div style="background:#fff5f0; padding:12px; border-radius:8px;">
                    <div style="font-size:0.75rem; color:#888;">Prix abonné (-15%)</div>
                    <div style="font-size:1rem; font-weight:700; color:#F05A28;">{res['total_sub']:.2f}€</div>
                </div>
                <div style="background:#f0fff0; padding:12px; border-radius:8px;">
                    <div style="font-size:0.75rem; color:#888;">Marge nette annuelle</div>
                    <div style="font-size:1rem; font-weight:700; color:#27ae60;">{res['annual_margin']:.0f}€</div>
                </div>
            </div>
        </div>''')

    # Comparison with frequency model
    h.append('''
        <div style="background:white; border-radius:12px; padding:20px; margin-bottom:20px; border-left:4px solid #27ae60;">
            <h4 style="color:#1B2B4B; margin-bottom:12px;">📊 Quantité vs Fréquence — Pourquoi c'est mieux</h4>
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                <thead>
                    <tr style="background:#f8f9fa;">
                        <th style="padding:10px; text-align:left;">Critère</th>
                        <th style="padding:10px; text-align:center;">❌ Modèle Fréquence<br><small>(produits livrés séparément)</small></th>
                        <th style="padding:10px; text-align:center;">✅ Modèle Quantité<br><small>(tout dans 1 colis)</small></th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td style="padding:8px;">🚚 Livraisons/an</td><td style="padding:8px; text-align:center; color:#e74c3c;">12</td><td style="padding:8px; text-align:center; color:#27ae60; font-weight:700;">4 à 6</td></tr>
                    <tr style="background:#f8f9fa;"><td style="padding:8px;">💸 Coût shipping/an</td><td style="padding:8px; text-align:center; color:#e74c3c;">46.80€</td><td style="padding:8px; text-align:center; color:#27ae60; font-weight:700;">15.60 — 23.40€</td></tr>
                    <tr><td style="padding:8px;">📦 Complexité picking</td><td style="padding:8px; text-align:center;">Élevée (multi-fréquence)</td><td style="padding:8px; text-align:center; font-weight:600;">Simple (1 fréquence/client)</td></tr>
                    <tr style="background:#f8f9fa;"><td style="padding:8px;">🎁 Expérience client</td><td style="padding:8px; text-align:center;">Petits colis séparés</td><td style="padding:8px; text-align:center; font-weight:600;">Box complète, effet "unboxing"</td></tr>
                    <tr><td style="padding:8px;">🧠 Personnalisation</td><td style="padding:8px; text-align:center;">Limitée (fréquence fixe)</td><td style="padding:8px; text-align:center; font-weight:600;">Forte (poids, training, objectif)</td></tr>
                    <tr style="background:#f8f9fa;"><td style="padding:8px;">📈 Upsell</td><td style="padding:8px; text-align:center;">Faible</td><td style="padding:8px; text-align:center; font-weight:600;">Reco moteur = +1-2 produits/box</td></tr>
                    <tr><td style="padding:8px;">🔄 Rétention estimée</td><td style="padding:8px; text-align:center;">6-8 mois</td><td style="padding:8px; text-align:center; font-weight:600;">8-12 mois (engagement box)</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Payment split explanation -->
        <div style="background:white; border-radius:12px; padding:20px; margin-bottom:20px; border-left:4px solid #f39c12;">
            <h4 style="color:#1B2B4B; margin-bottom:12px;">💳 Paiement lissé — Comment ça marche</h4>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px;">
                <div style="background:#fffff0; padding:15px; border-radius:10px; text-align:center;">
                    <div style="font-size:0.85rem; color:#666; margin-bottom:8px;">Cycle 1 mois</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#f39c12;">1× paiement</div>
                    <div style="font-size:0.85rem; color:#888; margin-top:5px;">Paiement classique à la commande</div>
                </div>
                <div style="background:#fff5f0; padding:15px; border-radius:10px; text-align:center; border:2px solid #F05A28;">
                    <div style="font-size:0.85rem; color:#666; margin-bottom:8px;">Cycle 2 mois</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#F05A28;">2× mensualités</div>
                    <div style="font-size:0.85rem; color:#888; margin-top:5px;">Total ÷ 2 = paiement M1 + M2</div>
                </div>
                <div style="background:#f0f4ff; padding:15px; border-radius:10px; text-align:center;">
                    <div style="font-size:0.85rem; color:#666; margin-bottom:8px;">Cycle 3 mois</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#1B2B4B;">3× mensualités</div>
                    <div style="font-size:0.85rem; color:#888; margin-top:5px;">Total ÷ 3 = paiement M1 + M2 + M3</div>
                </div>
            </div>
            <p style="margin-top:15px; font-size:0.85rem; color:#666;">
                <strong>Avantage client :</strong> Une box de 150€ à 50€/mois est plus facile à accepter qu'un one-shot de 150€.<br>
                <strong>Avantage Impulse :</strong> Cashflow prévisible, engagement psychologique plus fort (le client "paie déjà"), rétention améliorée.<br>
                <strong>Techniquement :</strong> Réalisable via Shopify Subscriptions + Stripe (paiements programmés).
            </p>
        </div>
    </div>
    ''')
    
    return '\n'.join(h)

# ──────────────────────────────────────────────────────────────────────
# Replace ciblé du bloc H2 par les commentaires anchors.
#
# Le bloc H2 généré par add_hypotheses.py est précédé par le commentaire
#   <!-- ═══ H2: BOX CUSTOM MULTI-FRÉQUENCE ═══ -->
# et suivi par
#   <!-- ═══ H3: PACKS CURATÉS ═══ -->
#
# Ces commentaires sont uniques dans le HTML et servent d'anchors fiables.
# On remplace tout le bloc entre ces deux anchors (anchors inclus pour la
# borne haute, anchor H3 conservé pour la borne basse).
# ──────────────────────────────────────────────────────────────────────
H2_START_ANCHOR = "<!-- ═══ H2: BOX CUSTOM MULTI-FRÉQUENCE ═══ -->"
H3_START_ANCHOR = "<!-- ═══ H3: PACKS CURATÉS ═══ -->"

h2_anchor_pos = html.find(H2_START_ANCHOR)
h3_anchor_pos = html.find(H3_START_ANCHOR)

if h2_anchor_pos == -1 or h3_anchor_pos == -1:
    print("❌ Anchors H2/H3 introuvables — le rapport HTML n'a pas été généré par add_hypotheses.py ?")
    print(f"   H2 anchor trouvé : {h2_anchor_pos != -1}")
    print(f"   H3 anchor trouvé : {h3_anchor_pos != -1}")
else:
    new_h2 = build_h2_html()
    # On remplace de h2_anchor_pos (inclusif) jusqu'à h3_anchor_pos (exclusif).
    # Le nouveau bloc H2 commence par son propre commentaire + div id="h2-quantity",
    # on le préfixe avec l'anchor H2 pour préserver l'anchor pour d'éventuels
    # re-runs.
    html = (
        html[:h2_anchor_pos]
        + H2_START_ANCHOR + "\n"
        + new_h2
        + "\n    "
        + html[h3_anchor_pos:]
    )
    print(f"✅ H2 remplacé via anchors (positions {h2_anchor_pos}→{h3_anchor_pos})")

with open('benchmark/rapport_rentabilite_abonnement.html', 'w') as f:
    f.write(html)

size = len(html)
print(f"📄 Rapport mis à jour: {size/1024:.0f} KB")
print("✅ Done!")
