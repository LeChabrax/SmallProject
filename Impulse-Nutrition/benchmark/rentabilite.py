"""
Modèle de rentabilité logistique — Benchmark Abonnement Impulse Nutrition

Wrapper pédagogique standalone qui calcule des scénarios de contribution nette
à différentes hypothèses de prix / marge / logistique. Utilisé pour alimenter
le deck PPTX (scénarios narratifs) et produire rentabilite_output.json.

⚠️ Convention : toutes les valeurs sont en HT (prix, marge, logistique).
   Voir benchmark/constants.py pour la règle d'or du benchmark.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    TVA_RATE,
    LOGISTICS_HT,
    LOGISTICS_TTC,
    NET_CONTRIBUTION_RENTABLE,
)

# Remise d'abonnement de référence pour le modèle standalone
DISCOUNT_RATE = 0.15  # aligné sur le rapport principal

# Prix HT testés (paliers commerciaux courants, en HT).
# Note : l'ancien script testait des prix TTC, on passe tout en HT pour cohérence.
PRICES_HT = [12, 15, 20, 25, 30, 35, 40, 50, 60, 75]

# Marges brutes HT testées (après passage en HT du prix)
MARGIN_RATES = [0.60, 0.70, 0.80]  # Impulse est sur ces ordres (cf. rapport principal)

# Coûts logistiques HT (dérivés des tarifs transporteur TTC)
LOGISTICS_COSTS_HT = [LOGISTICS_HT["point_relais"], LOGISTICS_HT["domicile"], LOGISTICS_HT["express"]]

# Scénarios narratifs pour les slides deck (prix HT)
NARRATIVE_SCENARIOS = [
    {"label": "Produit solo basse gamme (ex: créatine)", "price_ht": 12},
    {"label": "Produit solo mid-range (ex: oméga-3)",    "price_ht": 20},
    {"label": "Pack 2 produits",                          "price_ht": 35},
    {"label": "Pack 3 produits premium",                  "price_ht": 55},
]


def compute_contribution(price_ht, discount, margin, logistics_ht):
    """Contribution nette HT = marge brute sur prix remisé - coût logistique HT."""
    net_price_ht = price_ht * (1 - discount)
    gross_margin_ht = net_price_ht * margin
    contribution_ht = gross_margin_ht - logistics_ht
    return {
        "price_ht": price_ht,
        "price_ttc_equiv": round(price_ht * (1 + TVA_RATE), 2),
        "discount_pct": discount * 100,
        "net_price_ht": round(net_price_ht, 2),
        "gross_margin_ht": round(gross_margin_ht, 2),
        "logistics_cost_ht": logistics_ht,
        "contribution_nette_ht": round(contribution_ht, 2),
        "is_profitable": contribution_ht >= NET_CONTRIBUTION_RENTABLE,
        "margin_rate_on_original": round(gross_margin_ht / price_ht * 100, 1),
    }


def compute_min_basket_ht(discount, margin, logistics_ht):
    """Seuil de panier HT minimum pour qu'une livraison offerte soit rentable."""
    return round(logistics_ht / (margin * (1 - discount)), 2)


def main():
    print("=" * 76)
    print("MODÈLE DE RENTABILITÉ LOGISTIQUE — ABONNEMENT IMPULSE NUTRITION")
    print(f"Remise abonnement : {DISCOUNT_RATE*100:.0f}%  |  TVA : {TVA_RATE*100:.0f}%  |  Tous chiffres en HT")
    print("=" * 76)

    results = []

    pr_ht = LOGISTICS_HT["point_relais"]
    print(f"\n📊 TABLEAU COMPLET (Marge 70% HT, Point Relais {pr_ht:.2f}€ HT)")
    print(f"{'Prix HT':>8} | {'Prix TTC':>8} | {'Net HT':>8} | {'Marge HT':>9} | {'Logi HT':>8} | {'Contrib HT':>10} | {'OK':>4}")
    print("-" * 76)

    for price_ht in PRICES_HT:
        row = compute_contribution(price_ht, DISCOUNT_RATE, 0.70, pr_ht)
        results.append(row)
        status = "✅" if row["is_profitable"] else "❌"
        print(
            f"{row['price_ht']:>6}€   | "
            f"{row['price_ttc_equiv']:>6}€   | "
            f"{row['net_price_ht']:>6}€   | "
            f"{row['gross_margin_ht']:>7}€   | "
            f"{row['logistics_cost_ht']:>6}€   | "
            f"{row['contribution_nette_ht']:>8}€   | "
            f"{status}"
        )

    # Seuils de rentabilité
    dom_ht = LOGISTICS_HT["domicile"]
    exp_ht = LOGISTICS_HT["express"]
    print(f"\n\n📐 SEUILS DE PANIER MINIMUM (livraison offerte rentable, HT)")
    print(f"{'Marge HT':>9} | PR {pr_ht:.2f}€ HT | Dom {dom_ht:.2f}€ HT | Exp {exp_ht:.2f}€ HT")
    print("-" * 60)

    thresholds = {}
    for m in MARGIN_RATES:
        row_data = {}
        row_str = f"{int(m*100)}%      "
        for l in LOGISTICS_COSTS_HT:
            threshold_ht = compute_min_basket_ht(DISCOUNT_RATE, m, l)
            row_data[round(l, 2)] = threshold_ht
            row_str += f"   | {threshold_ht:>10}€"
        thresholds[m] = row_data
        print(row_str)

    # Seuil recommandé (marge 70% HT, Point Relais HT)
    recommended_threshold_ht = compute_min_basket_ht(DISCOUNT_RATE, 0.70, pr_ht)
    recommended_threshold_ttc = round(recommended_threshold_ht * (1 + TVA_RATE), 2)
    print(f"\n✅ SEUIL RECOMMANDÉ (marge 70% HT, Point Relais) : {recommended_threshold_ht:.2f}€ HT ≈ {recommended_threshold_ttc:.2f}€ TTC")
    print(f"   → Arrondi commercial suggéré (TTC vitrine) : 25€")

    # Scénarios narratifs pour le deck
    print("\n\n📖 SCÉNARIOS NARRATIFS POUR LE DECK (HT)")
    narrative_results = []
    for scenario in NARRATIVE_SCENARIOS:
        row = compute_contribution(scenario["price_ht"], DISCOUNT_RATE, 0.70, pr_ht)
        row["label"] = scenario["label"]
        narrative_results.append(row)
        status = "✅ VIABLE" if row["is_profitable"] else "❌ FRAGILE"
        print(f"\n  {scenario['label']} — {scenario['price_ht']}€ HT")
        print(f"    Après remise {DISCOUNT_RATE*100:.0f}% : {row['net_price_ht']}€ HT")
        print(f"    Marge brute (70% HT) : {row['gross_margin_ht']}€")
        print(f"    Livraison offerte : -{row['logistics_cost_ht']}€ HT")
        print(f"    → Contribution nette HT : {row['contribution_nette_ht']}€  {status}")

    # Export JSON pour le deck
    output = {
        "convention": "Toutes les valeurs sont en HT (TVA récupérable côté entreprise).",
        "tva_rate": TVA_RATE,
        "discount_rate": DISCOUNT_RATE,
        "logistics_ht": LOGISTICS_HT,
        "logistics_ttc_source": LOGISTICS_TTC,
        "recommended_threshold_ht": recommended_threshold_ht,
        "recommended_threshold_ttc": recommended_threshold_ttc,
        "recommended_threshold_rounded_ttc": 25,
        "full_matrix": [
            {
                "price_ht": p,
                "price_ttc_equiv": round(p * (1 + TVA_RATE), 2),
                "m60_pr": compute_contribution(p, DISCOUNT_RATE, 0.60, LOGISTICS_HT["point_relais"]),
                "m70_dom": compute_contribution(p, DISCOUNT_RATE, 0.70, LOGISTICS_HT["domicile"]),
                "m80_exp": compute_contribution(p, DISCOUNT_RATE, 0.80, LOGISTICS_HT["express"]),
            }
            for p in PRICES_HT
        ],
        "narrative_scenarios": narrative_results,
        "thresholds_ht": {
            f"m{int(m*100)}": {
                f"pr_{round(LOGISTICS_HT['point_relais'], 2)}": thresholds[m][round(LOGISTICS_HT["point_relais"], 2)],
                f"dom_{round(LOGISTICS_HT['domicile'], 2)}":   thresholds[m][round(LOGISTICS_HT["domicile"], 2)],
                f"exp_{round(LOGISTICS_HT['express'], 2)}":    thresholds[m][round(LOGISTICS_HT["express"], 2)],
            }
            for m in MARGIN_RATES
        },
    }

    with open("benchmark/rentabilite_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ Données exportées → benchmark/rentabilite_output.json (HT)")
    return output


if __name__ == "__main__":
    main()
