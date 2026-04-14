"""
Source de vérité unique pour le benchmark abonnement Impulse Nutrition.

Règle d'or : TOUS les calculs de rentabilité se font en HT.
- Les prix retail Shopify sont en TTC → convertis en HT via retail_ht(ttc)
- Les COGS (image Prix de Cession 2026) sont en HT
- Les coûts logistiques sont des factures transporteur TTC → convertis en HT
- Les prix affichés au client dans le rapport restent en TTC (expérience client)
"""

TVA_RATE = 0.20  # TVA 20% sur compléments alimentaires en France
# À vérifier avec compta HCS : certaines catégories (boissons d'effort à reconstituer)
# pourraient être à 5.5%. Par défaut on applique 20% partout.

# ── Coûts logistiques ──
# Tarifs réels Impulse Nutrition négociés, encaissés TTC par le transporteur,
# TVA récupérable → on travaille en HT dans les calculs.
LOGISTICS_TTC = {
    "point_relais": 3.90,
    "domicile":     5.90,
    "express":     10.90,
}


def retail_ht(price_ttc: float) -> float:
    """Convertit un prix TTC en HT (base standard TVA 20%)."""
    return round(price_ttc / (1 + TVA_RATE), 2)


def to_ht(value_ttc: float) -> float:
    """Alias générique pour toute conversion TTC → HT."""
    return round(value_ttc / (1 + TVA_RATE), 2)


LOGISTICS_HT = {name: to_ht(cost) for name, cost in LOGISTICS_TTC.items()}

# ── Scénarios abonnement ──
DISCOUNTS = [0.10, 0.15, 0.20]         # Remises testées
CONVERSION_RATES = [0.05, 0.10, 0.20]  # % de clients one-shot convertis en abo

# ── Horizon de projection ──
HORIZON_MONTHS = 24  # Standard DTC : 24 mois pour une LTV crédible

# ── Courbes de churn multi-phases (DTC compléments) ──
#
# Modèle : au lieu d'un taux de churn constant (qui cache le cliff M1), on
# modélise une courbe mensuelle. À chaque mois, un % des abonnés restants part.
# Les clés sont les numéros de mois ; les valeurs au-delà du dernier mois listé
# prolongent la dernière valeur (plateau long-terme).
#
# Sources sectorielles : Dollar Shave Club, Harry's, Ritual, podcasts Cuure/
# Nutri&Co, Recurly DTC benchmark. Ordres de grandeur observés :
#   - M1 :     20-35 % (cliff du test)
#   - M2-3 :   8-18 %  (stock accumulé, désengagement)
#   - M4-12 :  4-7 %   (plateau des convaincus)
#   - M13+ :   2-5 %   (long-tail rentable)
CHURN_CURVES = {
    "optimiste": {
        1: 0.15,
        2: 0.08,
        3: 0.06,
        4: 0.04,
        13: 0.02,
    },
    "baseline": {
        1: 0.25,
        2: 0.12,
        3: 0.08,
        4: 0.05,
        13: 0.03,
    },
    "pessimiste": {
        1: 0.35,
        2: 0.18,
        3: 0.12,
        4: 0.07,
        13: 0.05,
    },
}


def churn_at_month(curve: dict, month: int) -> float:
    """Retourne le churn du mois donné en extrapolant la courbe (dernière valeur au plateau)."""
    applicable = [m for m in curve.keys() if m <= month]
    if not applicable:
        return 0.0
    return curve[max(applicable)]


def simulate_cohort(curve: dict, horizon: int = HORIZON_MONTHS, start_size: int = 100):
    """Simule l'évolution d'une cohorte d'abonnés selon une courbe de churn.

    Retourne une liste de dicts avec, pour chaque mois : { month, survivors, churned }.
    survivors[M] = nb d'abonnés actifs DÉBUT du mois M (avant l'application du churn du mois).
    """
    cohort = []
    survivors = start_size
    for m in range(1, horizon + 1):
        churn = churn_at_month(curve, m)
        churned_this_month = survivors * churn
        cohort.append({
            "month": m,
            "survivors_start": round(survivors, 2),
            "churn_rate": churn,
            "churned": round(churned_this_month, 2),
            "survivors_end": round(survivors - churned_this_month, 2),
        })
        survivors = survivors - churned_this_month
    return cohort


def expected_months(curve: dict, horizon: int = HORIZON_MONTHS) -> float:
    """Durée de vie moyenne (en mois) d'un abonné selon la courbe et l'horizon.

    = somme, sur chaque mois, de la probabilité d'être encore actif ce mois-là.
    Chaque abonné paye le mois 1, donc on part de 1.0 au M1 et on décroit.
    """
    total = 0.0
    prob_alive = 1.0
    for m in range(1, horizon + 1):
        total += prob_alive
        prob_alive *= (1 - churn_at_month(curve, m))
    return round(total, 2)


# Alias legacy (conservé pour rétro-compat, valeurs cohérentes avec baseline équivalent)
# Utilisé par quelques scripts qui attendaient un taux plat. Nouvelle implémentation
# recommandée : passer par CHURN_CURVES + expected_months().
CHURN_RATES = [0.08, 0.10, 0.15]

# ══════════════════════════════════════════════════════════════════════════════
# SCÉNARIOS COMPOSITES DU PROGRAMME D'ABONNEMENT
# ══════════════════════════════════════════════════════════════════════════════
#
# Au lieu d'avoir des constantes isolées (setup, app cost, churn, mix incrémental),
# on bundle tout par scénario métier cohérent. Un scénario = une décision business :
# combien j'investis dans l'infra, quelle qualité d'acquisition je vise, à quel
# churn je m'attends.
#
# Les 3 scénarios sont tous AUTO-COHÉRENTS :
#   - "lean"      → petite app, onboarding minimal, churn optimiste (on suppose
#                   que ceux qui s'abonnent sont déjà convaincus)
#   - "standard"  → Recharge Pro, onboarding propre, churn baseline (référence
#                   DTC compléments 2024-2026)
#   - "full"      → stack retention complète, churn pessimiste (on accepte de
#                   perdre plus d'abonnés early-stage contre plus de volume)
#
# ⚠️ Noter que "full" est associé au churn pessimiste : c'est contre-intuitif
# mais réaliste. Quand on scale l'acquisition agressivement (paid ads, partenariats),
# la qualité moyenne des abonnés baisse → le cliff M1 est plus violent. Le meilleur
# scénario Lean a la meilleure rétention parce qu'il cible un early adopter
# convaincu, tandis que Full cible la masse.

PROGRAM_SCENARIOS = {
    "lean": {
        "label": "🚀 Lean MVP",
        "description": (
            "Test rapide du marché avec infrastructure minimale. "
            "Objectif : prouver le concept en 3-6 mois avec 50-100 abonnés "
            "avant d'investir dans du tooling custom."
        ),
        # Coûts infra HT
        "app_monthly_ht":   20,    # Loop Subscriptions / Appstle ($9-19/mois + fees)
        "setup_onetime_ht": 1500,  # Embed natif Shopify + landing basique (2 j dev)
        # Quelle courbe de churn on applique ? Référence CHURN_CURVES
        "churn_curve_key":  "optimiste",
        # Mix comportemental pour la cannibalisation (3-voies)
        "new_customer_rate":    0.20,  # 20% sont des nouveaux clients (100% incrémental)
        "retention_save_rate":  0.30,  # 30% sont d'anciens à risque churné, capturés
        "loyalist_rate":        0.50,  # 50% sont loyaux, auraient racheté plein tarif
        # Cible d'abonnés actifs utilisée pour dériver le seuil "rentable"
        "viable_subs_target":   10,
        # Sources pour la transparence
        "app_source":   "Loop Subscriptions / Appstle ($9-19/mois + 1% fees)",
        "setup_source": "Intégration embed natif Shopify + landing simple (2 j dev)",
        "mix_source":   "Pessimiste : acquisition essentiellement via email list interne",
    },
    "standard": {
        "label": "⚖️ Standard DTC",
        "description": (
            "Launch propre avec stack standard DTC compléments. "
            "Ce qu'on présenterait au COMEX comme business case crédible. "
            "Cible : 100-500 abonnés en 12 mois."
        ),
        "app_monthly_ht":   120,
        "setup_onetime_ht": 4000,
        "churn_curve_key":  "baseline",
        "new_customer_rate":    0.25,
        "retention_save_rate":  0.35,
        "loyalist_rate":        0.40,
        "viable_subs_target":   40,
        "app_source":   "Recharge Pro ($99/mois + 1% du revenu sub ≈ 120€ HT effectif)",
        "setup_source": "Landing dédiée + email welcome + design + copy + QA (5-7 j dev)",
        "mix_source":   "Mix paid + organic + email list (benchmark Recharge DTC 2024)",
    },
    "full": {
        "label": "🏎️ Full retention",
        "description": (
            "Stack complète avec retention tooling. Pour scaler au-delà de "
            "500 abonnés, avec cohort analytics, dunning avancé, email lifecycle. "
            "Rentable à partir de ~300 abonnés actifs."
        ),
        "app_monthly_ht":   350,
        "setup_onetime_ht": 7000,
        "churn_curve_key":  "pessimiste",
        "new_customer_rate":    0.35,
        "retention_save_rate":  0.40,
        "loyalist_rate":        0.25,
        "viable_subs_target":   80,
        "app_source":   "Recharge Pro Plus ($499/mois) + Klaviyo Sub + Yotpo retention",
        "setup_source": "Full custom UX + cohort dashboards + intégrations Klaviyo (15+ j dev)",
        "mix_source":   "Acquisition agressive paid ads + partenariats, qualité lead moyenne",
    },
}


def get_scenario(key: str = "standard") -> dict:
    """Retourne le scenario demandé (default : standard)."""
    if key not in PROGRAM_SCENARIOS:
        raise ValueError(f"Scenario inconnu : {key}. Choix : {list(PROGRAM_SCENARIOS.keys())}")
    return PROGRAM_SCENARIOS[key]


# Uplift de rétention : combien de mois supplémentaires un abonné "retention save"
# vit par rapport au client one-shot qui aurait churné après 2 commandes.
# Source : benchmark Recharge/Chargebee — un sub DTC retient +3 à +6 mois vs one-shot.
RETENTION_UPLIFT_MONTHS = 4.0

# Hypothèse volume moyen de commandes/an d'un "loyaliste" (celui qui aurait racheté
# plein tarif sans abo). Sert à calculer la perte de cannibalisation du 15%.
LOYALIST_ORDERS_PER_YEAR = 6

# Sub discount par défaut (remise abonnement). Utilisé dans tout le pipeline.
# Source : aligné sur les benchmarks concurrents DTC (Nutri&Co 15%, Nutrimuscle 5-15%,
# Novoma 10%, Aqeelab 20%) — 15% est la médiane crédible.
DEFAULT_SUB_DISCOUNT = 0.15


# ══════════════════════════════════════════════════════════════════════════════
# SCORING ABONNEMENT
# ══════════════════════════════════════════════════════════════════════════════
#
# Les 6 critères pondérés qui donnent un score /100 à chaque produit pour décider
# s'il mérite d'être en abonnement. Chaque poids a une justification documentée.

SCORING_WEIGHTS = {
    "recurrence":            35,   # #1 driver d'un programme DTC (up from 30)
    "margin_viability":      25,   # Rentabilité = survie (inchangé)
    "competitor_validation": 15,   # Validation marché (inchangé)
    "sku_complexity":        10,   # Shopify gère bien les variants (down from 15)
    "demand_signal":         10,   # Signal réel de vente (inchangé, mais on améliore la formule)
    "category_fit":           5,   # Boost catégorie santé > sport > accessoire (inchangé)
}
assert sum(SCORING_WEIGHTS.values()) == 100, "Les poids du scoring doivent totaliser 100"

# Seuils de verdict basés sur le score /100. Baissés vs version précédente (75/55)
# pour laisser plus de produits en MAYBE et forcer une revue humaine sur les marges.
VERDICT_THRESHOLDS = {
    "GO":    70,    # ≥ 70 → GO (down from 75)
    "MAYBE": 50,    # 50 ≤ x < 70 → MAYBE (down from 55)
    # < 50 → NO-GO
}

# ── Seuils de statut pour la contribution nette (en HT) ──
# Note : ces seuils sont DÉRIVÉS du scenario "standard" par défaut :
#   3€ = 120€ app_cost / 40 abos target (running break-even)
# Ils sont recalculés dynamiquement par scénario si besoin dans le code.
NET_CONTRIBUTION_RENTABLE = 3.0   # ≥ 3€ HT → rentable
NET_CONTRIBUTION_MARGINAL = 0.0   # 0 ≤ x < 3 → marginal, < 0 → déficitaire


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION CONCURRENTIELLE PAR CATÉGORIE
# ══════════════════════════════════════════════════════════════════════════════
#
# Compte, pour chaque catégorie produit, combien de concurrents du benchmark
# (8 marques totales) proposent déjà cette catégorie en abonnement. Sert à
# donner un score gradient "validation marché" au lieu d'un binaire.
#
# Base : 8 marques benchmarkées — Nutri&Co, Nutrimuscle, Novoma, Cuure,
# MyProtein, Decathlon, Aqeelab, Nutripure (Nutripure n'a pas d'abo du tout).
#
# Source : analyse catalogues.json + ux_deep.json + relevés manuels avril 2026.
# À ré-auditer si un concurrent change sa gamme abonnement.
COMPETITOR_SUB_COUNT = {
    # Catégorie → (nb concurrents qui la proposent en abo, /8)
    "creatine":        4,   # Nutrimuscle, MyProtein, Aqeelab, Decathlon
    "whey":            4,   # Nutrimuscle, MyProtein, Aqeelab, Decathlon
    "multivitamines":  3,   # Nutri&Co, Novoma, Cuure
    "omega3":          3,   # Nutri&Co, Novoma, Cuure
    "magnesium":       3,   # Nutri&Co, Novoma, Cuure
    "collagene":       2,   # Nutri&Co, Nutrimuscle
    "probiotiques":    3,   # Nutri&Co, Novoma, Cuure
    "bcaa":            2,   # Nutrimuscle, MyProtein
    "fer":             2,   # Novoma, Cuure
    "vitc":            2,   # Novoma, Cuure
    "vitd":            2,   # Novoma, Cuure
    "spiruline":       1,   # Novoma
    "curcumine":       2,   # Nutri&Co, Novoma
    "sommeil":         2,   # Novoma, Cuure
    "glycine":         0,   # personne
    "glutamine":       2,   # Nutrimuscle, MyProtein
    "electrolytes":    1,   # MyProtein
    "boisson_effort":  0,   # rare en abo (consommation événementielle)
    "maltodextrine":   2,   # MyProtein, Nutrimuscle
    "preworkout":      2,   # MyProtein, Aqeelab
    "recovery":        1,   # MyProtein
    "barre":           0,   # pas en abo chez les benchmarkés
    "accessoire":      0,   # évidemment
}
TOTAL_COMPETITORS = 8      # taille de l'univers de référence


# ══════════════════════════════════════════════════════════════════════════════
# HYPOTHÈSES ILLUSTRATIVES (pas des prédictions)
# ══════════════════════════════════════════════════════════════════════════════
#
# ⚠️ Les valeurs ci-dessous servent UNIQUEMENT à produire des chiffres en valeur
# absolue dans les sections "revenue_impact" et "cannibalisation absolue" du
# rapport, pour donner une intuition de l'ordre de grandeur. Elles ne changent
# JAMAIS la décision stratégique (scoring, ranking, break-even unitaires).
#
# Les sections les utilisant sont étiquetées "💡 ILLUSTRATIF" dans le rapport.
# Remplacer par des données Shopify réelles si Antoine veut des projections
# quantitatives exactes.

ILLUSTRATIVE_ORDERS_PER_PRODUCT = 50  # commandes/mois/produit (illustratif)


# ══════════════════════════════════════════════════════════════════════════════
# ALIASES RÉTRO-COMPAT (ne pas utiliser dans du code nouveau)
# ══════════════════════════════════════════════════════════════════════════════
#
# Ces constantes pointent vers le scenario "standard" par défaut. Elles sont
# conservées pour que les scripts downstream qui importaient les anciennes
# valeurs continuent de fonctionner sans refactor. Dans le code nouveau,
# préférer `get_scenario("standard")` ou `PROGRAM_SCENARIOS["standard"]`.

SETUP_COST_ONETIME = PROGRAM_SCENARIOS["standard"]["setup_onetime_ht"]    # 4000
MONTHLY_APP_COST   = PROGRAM_SCENARIOS["standard"]["app_monthly_ht"]      # 120
