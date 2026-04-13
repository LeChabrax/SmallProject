"""
Modèle de rentabilité logistique — Benchmark Abonnement Impulse Nutrition
Calcule la contribution nette pour différents scénarios prix / marge / coût logistique.
"""

import json
import csv

# Paramètres
DISCOUNT_RATE = 0.10  # 10% remise abonnement
PRICES = [15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 90]  # en €
MARGIN_RATES = [0.40, 0.45, 0.50]  # marge brute sur prix net après remise
LOGISTICS_COSTS = [4.0, 5.0, 7.0]  # € HT coût expédition (Colissimo / Mondial Relay / pick-up)

# Scénarios narratifs pour les slides
NARRATIVE_SCENARIOS = [
    {"label": "Produit solo (ex: créatine 300g)", "price": 15},
    {"label": "Produit mid-range (ex: oméga-3 60 caps)", "price": 35},
    {"label": "Pack 2-3 produits", "price": 55},
]


def compute_contribution(price, discount, margin, logistics):
    """Contribution nette = marge brute sur prix remisé - coût logistique."""
    net_price = price * (1 - discount)
    gross_margin = net_price * margin
    contribution = gross_margin - logistics
    return {
        "price": price,
        "discount_pct": discount * 100,
        "net_price": round(net_price, 2),
        "gross_margin": round(gross_margin, 2),
        "logistics_cost": logistics,
        "contribution_nette": round(contribution, 2),
        "is_profitable": contribution > 0,
        "margin_rate_on_original": round(gross_margin / price * 100, 1),
    }


def compute_min_basket(discount, margin, logistics):
    """Seuil minimal de panier pour que livraison offerte soit rentable."""
    # P_min = L / (m × (1 - d))
    p_min = logistics / (margin * (1 - discount))
    return round(p_min, 2)


def main():
    print("=" * 70)
    print("MODÈLE DE RENTABILITÉ LOGISTIQUE — ABONNEMENT IMPULSE NUTRITION")
    print(f"Remise abonnement : {DISCOUNT_RATE*100:.0f}%")
    print("=" * 70)

    results = []

    # Tableau complet
    print("\n📊 TABLEAU COMPLET (Marge 45%, Logistique 5€)")
    print(f"{'Prix TTC':>8} | {'Prix net':>8} | {'Marge brute':>11} | {'Logistique':>10} | {'Contribution':>12} | {'Rentable':>8}")
    print("-" * 70)

    for price in PRICES:
        row = compute_contribution(price, DISCOUNT_RATE, 0.45, 5.0)
        results.append(row)
        status = "✅" if row["is_profitable"] else "❌"
        print(
            f"{row['price']:>6}€ TTC | "
            f"{row['net_price']:>6}€    | "
            f"{row['gross_margin']:>8}€    | "
            f"{row['logistics_cost']:>7}€    | "
            f"{row['contribution_nette']:>9}€    | "
            f"{status}"
        )

    # Seuils de rentabilité
    print("\n\n📐 SEUILS DE PANIER MINIMUM (livraison offerte rentable)")
    print(f"{'Marge':>8} | {'Logistique 4€':>13} | {'Logistique 5€':>13} | {'Logistique 7€':>13}")
    print("-" * 55)

    thresholds = {}
    for m in MARGIN_RATES:
        row_data = {}
        row_str = f"{int(m*100)}%    "
        for l in LOGISTICS_COSTS:
            threshold = compute_min_basket(DISCOUNT_RATE, m, l)
            row_data[l] = threshold
            row_str += f"   | {threshold:>10}€    "
        thresholds[m] = row_data
        print(row_str)

    # Seuil recommandé (marge 45%, logistique 5€)
    recommended_threshold = compute_min_basket(DISCOUNT_RATE, 0.45, 5.0)
    print(f"\n✅ SEUIL RECOMMANDÉ (marge 45%, logistique 5€) : {recommended_threshold:.2f}€")
    print(f"   → Arrondi opérationnel suggéré : 25€ minimum de commande")

    # Scénarios narratifs
    print("\n\n📖 SCÉNARIOS NARRATIFS POUR LE DECK")
    narrative_results = []
    for scenario in NARRATIVE_SCENARIOS:
        row = compute_contribution(scenario["price"], DISCOUNT_RATE, 0.45, 5.0)
        row["label"] = scenario["label"]
        narrative_results.append(row)
        status = "✅ VIABLE" if row["is_profitable"] else "❌ FRAGILE"
        print(f"\n  {scenario['label']} — {scenario['price']}€")
        print(f"    Après remise {DISCOUNT_RATE*100:.0f}% : {row['net_price']}€")
        print(f"    Marge brute (45%) : {row['gross_margin']}€")
        print(f"    Livraison offerte : -{row['logistics_cost']}€")
        print(f"    → Contribution nette : {row['contribution_nette']}€  {status}")

    # Analyse LTV
    print("\n\n💰 ANALYSE LTV — Valeur sur 12 mois (abonnement mensuel)")
    print(f"{'Panier':>8} | {'One-shot CA':>12} | {'Abo CA':>8} | {'Abo marge nette':>15} | {'LTV vs one-shot':>15}")
    print("-" * 70)
    for price in [25, 35, 50]:
        one_shot_revenue = price  # hypothèse: 4 achats one-shot par an
        abo_monthly_revenue = price * (1 - DISCOUNT_RATE) * 12
        abo_margin = abo_monthly_revenue * 0.45 - 5.0 * 12
        ltv_gain = abo_margin - (one_shot_revenue * 4 * 0.45)
        print(f"{price:>6}€    | {one_shot_revenue*4:>9}€    | {abo_monthly_revenue:>5}€  | {abo_margin:>12}€    | +{ltv_gain:>11}€")

    # Export JSON pour le deck
    output = {
        "discount_rate": DISCOUNT_RATE,
        "recommended_threshold": recommended_threshold,
        "recommended_threshold_rounded": 25,
        "full_matrix": [
            {
                "price": p,
                "m40_l4": compute_contribution(p, DISCOUNT_RATE, 0.40, 4.0),
                "m45_l5": compute_contribution(p, DISCOUNT_RATE, 0.45, 5.0),
                "m50_l7": compute_contribution(p, DISCOUNT_RATE, 0.50, 7.0),
            }
            for p in PRICES
        ],
        "narrative_scenarios": narrative_results,
        "thresholds": {
            "m40": {"l4": thresholds[0.40][4.0], "l5": thresholds[0.40][5.0], "l7": thresholds[0.40][7.0]},
            "m45": {"l4": thresholds[0.45][4.0], "l5": thresholds[0.45][5.0], "l7": thresholds[0.45][7.0]},
            "m50": {"l4": thresholds[0.50][4.0], "l5": thresholds[0.50][5.0], "l7": thresholds[0.50][7.0]},
        },
    }

    with open("benchmark/rentabilite_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ Données exportées → benchmark/rentabilite_output.json")
    return output


if __name__ == "__main__":
    main()
