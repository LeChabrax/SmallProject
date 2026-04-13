import json, os

OUT = "/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/benchmark"

# ============================================================
# 1. CATALOGUES & PRICING
# ============================================================
catalogues = {
    "meta": {"phase": 1, "description": "Catalogues produits & pricing par marque", "last_updated": "2026-04-07"},
    "brands": {
        "nutriandco": {
            "name": "Nutri&Co",
            "url": "https://nutriandco.com",
            "has_subscription": True,
            "subscription_discount_pct": 15,
            "subscription_model": "Subscribe & save sur chaque produit",
            "frequencies_available": ["1 mois", "2 mois", "3 mois"],
            "flexibility": {"pause": True, "modify": True, "cancel_anytime": True, "minimum_commitment": "Aucun"},
            "products": [
                {"name": "Collagène Marin", "category": "Santé articulaire", "price_oneshot": 29.90, "price_sub": 25.42, "discount_pct": 15, "weight": "200g", "format": "Poudre"},
                {"name": "Magnésium Bisglycinate", "category": "Minéraux", "price_oneshot": 19.90, "price_sub": 16.92, "discount_pct": 15, "weight": "90 gélules", "format": "Gélules"},
                {"name": "Oméga-3 Epax", "category": "Acides gras", "price_oneshot": 22.90, "price_sub": 19.47, "discount_pct": 15, "weight": "60 capsules", "format": "Capsules"},
                {"name": "Multivitamines", "category": "Vitamines", "price_oneshot": 26.90, "price_sub": 22.87, "discount_pct": 15, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Zinc Bisglycinate", "category": "Minéraux", "price_oneshot": 12.90, "price_sub": 10.97, "discount_pct": 15, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Probiotiques", "category": "Digestion", "price_oneshot": 24.90, "price_sub": 21.17, "discount_pct": 15, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Vitamine D3 + K2", "category": "Vitamines", "price_oneshot": 14.90, "price_sub": 12.67, "discount_pct": 15, "weight": "60 gélules", "format": "Gélules"}
            ],
            "subscription_scope": "Tous les produits éligibles",
            "estimated_avg_basket_sub": 35
        },
        "nutrimuscle": {
            "name": "Nutrimuscle",
            "url": "https://www.nutrimuscle.com",
            "has_subscription": True,
            "subscription_discount_pct": "5% 1ère livraison, 15% à partir de la 2ème",
            "subscription_model": "Abonnement progressif (5% → 15%)",
            "frequencies_available": ["1 mois", "2 mois", "3 mois", "4 mois", "5 mois", "6 mois"],
            "flexibility": {"pause": True, "modify": True, "cancel_anytime": True, "minimum_commitment": "Aucun"},
            "products": [
                {"name": "Créatine Creapure", "category": "Performance", "price_oneshot": 16.95, "price_sub": 14.41, "discount_pct": 15, "weight": "350g", "format": "Poudre"},
                {"name": "Whey Native Biologique", "category": "Protéines", "price_oneshot": 19.95, "price_sub": 16.96, "discount_pct": 15, "weight": "500g", "format": "Poudre"},
                {"name": "Oméga-3 Epax", "category": "Acides gras", "price_oneshot": 19.95, "price_sub": 16.96, "discount_pct": 15, "weight": "120 capsules", "format": "Capsules"},
                {"name": "Collagène Peptan", "category": "Santé articulaire", "price_oneshot": 14.95, "price_sub": 12.71, "discount_pct": 15, "weight": "200g", "format": "Poudre"},
                {"name": "Multivitamines", "category": "Vitamines", "price_oneshot": 12.95, "price_sub": 11.01, "discount_pct": 15, "weight": "120 gélules", "format": "Gélules"},
                {"name": "Magnésium", "category": "Minéraux", "price_oneshot": 9.95, "price_sub": 8.46, "discount_pct": 15, "weight": "120 gélules", "format": "Gélules"},
                {"name": "BCAA 2.1.1", "category": "Acides aminés", "price_oneshot": 21.95, "price_sub": 18.66, "discount_pct": 15, "weight": "500g", "format": "Poudre"}
            ],
            "subscription_scope": "Quasi tous les produits (250+ références)",
            "estimated_avg_basket_sub": 45,
            "note": "Catalogue très large, 250+ produits. Première livraison -5%, puis -15% ensuite."
        },
        "novoma": {
            "name": "Novoma",
            "url": "https://novoma.com",
            "has_subscription": True,
            "subscription_discount_pct": 10,
            "subscription_model": "Abonnement -10% + avantages livraison",
            "frequencies_available": ["1 mois", "2 mois", "3 mois"],
            "flexibility": {"pause": True, "modify": True, "cancel_anytime": True, "minimum_commitment": "Aucun"},
            "products": [
                {"name": "Collagène Marin Peptan", "category": "Santé articulaire", "price_oneshot": 31.90, "price_sub": 28.71, "discount_pct": 10, "weight": "300g", "format": "Poudre"},
                {"name": "Magnésium Bisglycinate", "category": "Minéraux", "price_oneshot": 14.90, "price_sub": 13.41, "discount_pct": 10, "weight": "90 gélules", "format": "Gélules"},
                {"name": "Vitamine C Liposomale", "category": "Vitamines", "price_oneshot": 27.90, "price_sub": 25.11, "discount_pct": 10, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Multivitamines", "category": "Vitamines", "price_oneshot": 25.90, "price_sub": 23.31, "discount_pct": 10, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Probiotiques Lacto", "category": "Digestion", "price_oneshot": 21.90, "price_sub": 19.71, "discount_pct": 10, "weight": "60 gélules", "format": "Gélules"}
            ],
            "subscription_scope": "Tous les produits du catalogue",
            "estimated_avg_basket_sub": 30,
            "subscription_shipping_advantage": "Domicile 3.50€ au lieu de 4.90€, gratuit dès 50€ (vs 90€ standard)"
        },
        "nutripure": {
            "name": "Nutripure",
            "url": "https://www.nutripure.fr",
            "has_subscription": False,
            "subscription_model": "Aucun — achat one-shot uniquement",
            "products": [
                {"name": "Whey Isolate Native", "category": "Protéines", "price_oneshot": 46.90, "weight": "750g", "format": "Poudre"},
                {"name": "Whey Isolate Native 1.5kg", "category": "Protéines", "price_oneshot": 84.90, "weight": "1.5kg", "format": "Poudre"},
                {"name": "Créatine Creapure", "category": "Performance", "price_oneshot": 25.90, "weight": "300g", "format": "Poudre"},
                {"name": "Oméga-3 Epax (3 mois)", "category": "Acides gras", "price_oneshot": 69.90, "weight": "180 capsules", "format": "Capsules"},
                {"name": "Oméga-3 Epax (1 mois)", "category": "Acides gras", "price_oneshot": 27.90, "weight": "60 capsules", "format": "Capsules"},
                {"name": "Magnésium Bisglycinate (3 mois)", "category": "Minéraux", "price_oneshot": 39.90, "weight": "180 gélules", "format": "Gélules"},
                {"name": "Magnésium Bisglycinate (1 mois)", "category": "Minéraux", "price_oneshot": 18.90, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Multivitamines", "category": "Vitamines", "price_oneshot": 24.90, "weight": "60 gélules", "format": "Gélules"}
            ],
            "subscription_scope": "N/A",
            "estimated_avg_basket": 55,
            "why_no_subscription": "Positionnement ultra-premium, vente par lots (1 mois / 3 mois), stratégie de fidélisation par la qualité plutôt que par le lock-in. Formats 3 mois encouragent implicitement la récurrence."
        },
        "cuure": {
            "name": "Cuure",
            "url": "https://cuure.com",
            "has_subscription": True,
            "subscription_discount_pct": "~10% vs achat individuel",
            "subscription_model": "Box personnalisée mensuelle (questionnaire → sélection auto)",
            "frequencies_available": ["1 mois", "2 mois", "3 mois"],
            "flexibility": {"pause": True, "modify": True, "cancel_anytime": True, "minimum_commitment": "Aucun"},
            "products": [
                {"name": "Box personnalisée (3-8 compléments)", "category": "Multi", "price_range": "24-40€/mois", "format": "30 sachets quotidiens"},
                {"name": "Probiotiques", "category": "Digestion", "note": "4.4/5, 2063 avis"},
                {"name": "Magnésium", "category": "Minéraux", "note": "4.5/5, 3348 avis"},
                {"name": "Oméga-3", "category": "Acides gras"},
                {"name": "Vitamine D", "category": "Vitamines"},
                {"name": "Fer", "category": "Minéraux"},
                {"name": "Zinc", "category": "Minéraux"}
            ],
            "subscription_scope": "50+ ingrédients, 2M+ combinaisons possibles",
            "estimated_avg_basket_sub": 35,
            "unique_selling_point": "Personnalisation via questionnaire, sachets quotidiens pré-dosés, comité scientifique"
        },
        "decathlon": {
            "name": "Decathlon (Abonnement Nutrition)",
            "url": "https://abonnement.decathlon.fr",
            "has_subscription": True,
            "subscription_discount_pct": "10-15%",
            "subscription_model": "Abonnement par produit, 1 produit = 1 abonnement",
            "frequencies_available": ["1 mois", "2 mois", "3 mois"],
            "flexibility": {"pause": True, "modify": False, "cancel_anytime": True, "minimum_commitment": "Aucun", "modify_note": "Pour modifier → résilier et recréer"},
            "products": [
                {"name": "Whey Isolate 2kg", "category": "Protéines", "price_oneshot": 79.99, "price_sub": 71.99, "discount_pct": 10, "weight": "2kg", "format": "Poudre"},
                {"name": "Whey 1.5kg", "category": "Protéines", "price_oneshot": 44.99, "price_sub": 39.99, "discount_pct": 11, "weight": "1.5kg", "format": "Poudre"},
                {"name": "Whey 900g", "category": "Protéines", "price_oneshot": 28.99, "price_sub": 25.99, "discount_pct": 10, "weight": "900g", "format": "Poudre"},
                {"name": "Créatine monohydrate 300g", "category": "Performance", "price_oneshot": 14.99, "price_sub": 12.74, "discount_pct": 15, "weight": "300g", "format": "Poudre"}
            ],
            "subscription_scope": "Sélection limitée : whey, créatine, quelques compléments, croquettes",
            "estimated_avg_basket_sub": 40,
            "loyalty_program": "10 points fidélité par euro dépensé en abonnement"
        },
        "aqeelab": {
            "name": "Aqeelab Nutrition",
            "url": "https://www.aqeelab-nutrition.fr",
            "has_subscription": True,
            "subscription_discount_pct": 20,
            "subscription_model": "Subscribe & save -20% sur chaque produit",
            "frequencies_available": ["1 mois", "2 mois", "3 mois"],
            "flexibility": {"pause": True, "modify": True, "cancel_anytime": True, "minimum_commitment": "Aucun"},
            "products": [
                {"name": "Better Protein (Whey)", "category": "Protéines", "price_oneshot": 45.95, "price_sub": 36.76, "discount_pct": 20, "weight": "750g", "format": "Poudre"},
                {"name": "Créatine Monohydrate Poudre", "category": "Performance", "price_oneshot": 36.95, "price_sub": 29.56, "discount_pct": 20, "weight": "500g", "format": "Poudre"},
                {"name": "Créatine Gélules", "category": "Performance", "price_oneshot": 24.95, "price_sub": 19.96, "discount_pct": 20, "weight": "180 gélules", "format": "Gélules"},
                {"name": "Oméga-3 Wild", "category": "Acides gras", "price_oneshot": 49.95, "price_sub": 39.96, "discount_pct": 20, "weight": "120 capsules", "format": "Capsules"},
                {"name": "Ashwagandha KSM-66", "category": "Adaptogènes", "price_oneshot": 28.95, "price_sub": 23.16, "discount_pct": 20, "weight": "90 gélules", "format": "Gélules"},
                {"name": "BCAA 8.1.1", "category": "Acides aminés", "price_oneshot": 29.95, "price_sub": 23.96, "discount_pct": 20, "weight": "300g", "format": "Poudre"},
                {"name": "Magnésium Bisglycinate", "category": "Minéraux", "price_oneshot": 19.95, "price_sub": 15.96, "discount_pct": 20, "weight": "90 gélules", "format": "Gélules"},
                {"name": "Multivitamines", "category": "Vitamines", "price_oneshot": 24.95, "price_sub": 19.96, "discount_pct": 20, "weight": "60 gélules", "format": "Gélules"},
                {"name": "Collagène Marin Peptan", "category": "Santé articulaire", "price_oneshot": 28.95, "price_sub": 23.16, "discount_pct": 20, "weight": "200g", "format": "Poudre"},
                {"name": "Pre-Workout", "category": "Performance", "price_oneshot": 34.95, "price_sub": 27.96, "discount_pct": 20, "weight": "300g", "format": "Poudre"}
            ],
            "subscription_scope": "Tous les 23 produits du catalogue",
            "estimated_avg_basket_sub": 45,
            "note": "Plus haute remise abo du marché FR (20%). Catalogue petit mais ultra-ciblé."
        },
        "myprotein": {
            "name": "MyProtein",
            "url": "https://fr.myprotein.com",
            "has_subscription": True,
            "subscription_discount_pct": "30% (jusqu'à 45% en promo)",
            "subscription_model": "Subscribe & Save, remise très agressive",
            "frequencies_available": ["1 mois", "2 mois", "3 mois", "4 mois", "5 mois"],
            "flexibility": {"pause": True, "modify": True, "cancel_anytime": True, "minimum_commitment": "Aucun"},
            "products": [
                {"name": "Impact Whey Protein 1kg", "category": "Protéines", "price_oneshot": 30.49, "price_sub": 21.34, "discount_pct": 30, "weight": "1kg", "format": "Poudre"},
                {"name": "Impact Whey Protein 2.5kg", "category": "Protéines", "price_oneshot": 59.99, "price_sub": 41.99, "discount_pct": 30, "weight": "2.5kg", "format": "Poudre"},
                {"name": "Creatine Monohydrate 250g", "category": "Performance", "price_oneshot": 7.99, "price_sub": 5.59, "discount_pct": 30, "weight": "250g", "format": "Poudre"},
                {"name": "Omega 3 90 capsules", "category": "Acides gras", "price_oneshot": 8.90, "price_sub": 6.23, "discount_pct": 30, "weight": "90 capsules", "format": "Capsules"},
                {"name": "Multivitamines Alpha Men", "category": "Vitamines", "price_oneshot": 14.99, "price_sub": 10.49, "discount_pct": 30, "weight": "120 comprimés", "format": "Comprimés"},
                {"name": "BCAA 250g", "category": "Acides aminés", "price_oneshot": 12.99, "price_sub": 9.09, "discount_pct": 30, "weight": "250g", "format": "Poudre"}
            ],
            "subscription_scope": "Quasi tous les produits (1000+ références)",
            "estimated_avg_basket_sub": 35,
            "note": "Remise la plus agressive du marché (30% standard, jusqu'à 45% en promo). Modèle volume international."
        }
    }
}

# ============================================================
# 2. LOGISTIQUE
# ============================================================
logistique = {
    "meta": {"phase": 2, "description": "Logistique, transporteurs et frais par marque + grilles transporteurs FR", "last_updated": "2026-04-07"},
    "grilles_transporteurs_fr_2026": {
        "colissimo": {
            "domicile": {"250g": 5.49, "500g": 7.59, "1kg": 9.59, "2kg": 11.19, "5kg": 17.39},
            "point_retrait": {"250g": 4.79, "500g": 6.89, "1kg": 8.89, "2kg": 10.49},
            "note": "Tarifs publics TTC, professionnels bénéficient de -30 à -50%"
        },
        "mondial_relay": {
            "relais_public": {"250g": 4.10, "1kg": 5.99, "2kg": 7.99, "5kg": 15.99},
            "pro_ht": {"500g": 3.42, "1kg": 3.76, "2kg": 5.27, "4kg": 5.59},
            "note": "Tarifs pro HT très compétitifs, réseau 10 000+ points relais"
        },
        "chronopost": {
            "shop2shop": {"1kg": 4.50, "4kg": 6.95, "10kg": 13.90},
            "express_chrono13": {"2kg": "28-36€", "5kg": "33-38€"},
            "note": "Express J+1, prix élevé sauf Shop2Shop"
        },
        "dpd": {
            "relais": {"1kg": "6-8€", "5kg": "9-12€"},
            "domicile": {"1kg": "8-11€", "5kg": "12-14€"},
            "note": "DPD Predict avec créneau SMS"
        },
        "colis_prive": {
            "pro": {"1kg": "from 5€", "5kg": "8-10€"},
            "note": "Peu utilisé en nutrition, surtout retail"
        }
    },
    "par_marque": {
        "nutriandco": {
            "transporteurs": ["Mondial Relay", "Colissimo", "Chronopost"],
            "frais_relais": 4.50, "seuil_gratuit_relais": 69,
            "frais_domicile": 6.50, "seuil_gratuit_domicile": 89,
            "frais_express": "Variable", "delai_standard": "2-3 jours ouvrés"
        },
        "nutrimuscle": {
            "transporteurs": ["Mondial Relay", "Colissimo", "Chronopost"],
            "frais_relais": 5.30, "seuil_gratuit_relais": 60,
            "frais_domicile": 7.50, "seuil_gratuit_domicile": 100,
            "delai_standard": "2-3 jours ouvrés"
        },
        "novoma": {
            "transporteurs": ["Shop2Shop/Mondial Relay", "Colissimo", "DPD"],
            "frais_relais": 3.90, "seuil_gratuit_relais": 65,
            "frais_domicile": 4.90, "seuil_gratuit_domicile": 90,
            "frais_dpd": 6.90, "seuil_reduit_dpd": 90, "frais_dpd_reduit": 2.90,
            "delai_standard": "2-4 jours ouvrés",
            "avantage_abonnement": {"frais_domicile_abo": 3.50, "seuil_gratuit_domicile_abo": 50}
        },
        "nutripure": {
            "transporteurs": ["Point relais", "Colissimo"],
            "frais_relais": 4.90, "seuil_gratuit_relais": 49.90,
            "frais_domicile_standard": 5.90, "seuil_gratuit_domicile": 99,
            "frais_domicile_colissimo": 7.50, "seuil_reduit_colissimo": 99, "frais_colissimo_reduit": 1.60,
            "delai_standard": "2-5 jours ouvrés"
        },
        "cuure": {
            "transporteurs": ["Non précisé (box personnalisée)"],
            "frais_standard": 6.50,
            "seuil_gratuit": "20-39€ selon offres",
            "delai_standard": "3-5 jours ouvrés",
            "note": "Livraison quasi systématiquement incluse dans le prix de l'abo"
        },
        "decathlon": {
            "transporteurs": ["Mondial Relay", "Colissimo", "Chronopost"],
            "livraison_abo": "Offerte en point relais",
            "frais_domicile": "3-4.50€",
            "seuil_gratuit_domicile": "Variable",
            "delai_standard": "3-5 jours ouvrés",
            "note": "Livraison offerte sur abonnements nutrition en point relais"
        },
        "aqeelab": {
            "transporteurs": ["Mondial Relay", "DPD", "Chronopost"],
            "frais_relais": "3.95-6.95€", "seuil_gratuit_relais": 69,
            "frais_domicile": 6.45, "seuil_gratuit_domicile": 100,
            "delai_standard": "1-3 jours ouvrés",
            "note": "Expédition depuis Bordeaux, sous 24-48h"
        },
        "myprotein": {
            "transporteurs": ["DPD", "Colissimo"],
            "frais_relais": 3.99, "seuil_gratuit_relais": 60,
            "frais_domicile": 4.99, "seuil_gratuit_domicile": 60,
            "frais_express": 11.99, "frais_express_reduit": 6.99,
            "delai_standard": "2-4 jours ouvrés",
            "note": "Seuil gratuit identique relais et domicile (60€)"
        }
    },
    "poids_moyen_colis_nutrition": {
        "complement_gelules_1_boite": "100-200g",
        "whey_1kg": "1.1-1.3kg",
        "creatine_300g": "350-400g",
        "commande_type_2_3_produits": "400g-1.5kg",
        "commande_type_abo_mensuel": "200g-800g"
    }
}

# ============================================================
# 3. TECH STACK
# ============================================================
tech_stack = {
    "meta": {"phase": 3, "description": "Stack technique e-commerce par marque", "last_updated": "2026-04-07"},
    "brands": {
        "nutriandco": {
            "platform": "Shopify",
            "confidence": "high",
            "source": "Axome agency (Shopify Platinum Partner) — refonte Nutri&Co confirmée",
            "subscription_app": "Probablement Recharge ou Shopify Native Subscriptions",
            "psp": "Shopify Payments (Stripe)",
            "agency": "Axome"
        },
        "nutrimuscle": {
            "platform": "Shopify Plus",
            "confidence": "confirmed",
            "source": "Axome agency case study — migration vers Shopify Plus",
            "subscription_app": "Probablement Recharge (Shopify Plus)",
            "psp": "Shopify Payments (Stripe)",
            "agency": "Axome"
        },
        "novoma": {
            "platform": "Shopify",
            "confidence": "confirmed",
            "source": "Axome agency case study — refonte sous Shopify confirmée",
            "subscription_app": "Probablement Recharge ou Bold Subscriptions",
            "psp": "Shopify Payments (Stripe)",
            "agency": "Axome"
        },
        "nutripure": {
            "platform": "PrestaShop",
            "confidence": "confirmed",
            "source": "URL structure (/fr/29-gamme-produits) + Zendesk support",
            "subscription_app": "N/A (pas d'abonnement)",
            "psp": "Non confirmé (probablement Stripe ou Mollie)",
            "note": "PrestaShop = pas de module abo natif mature, pourrait expliquer l'absence d'abonnement"
        },
        "cuure": {
            "platform": "Custom (initialement Bubble, puis stack propriétaire)",
            "confidence": "high",
            "source": "Bubble.io case study — MVP initialement sur Bubble. Probablement migré vers stack custom avec croissance",
            "subscription_app": "Custom / Stripe Billing",
            "psp": "Stripe",
            "note": "Modèle box personnalisée nécessite stack custom (algorithme de recommandation)"
        },
        "decathlon": {
            "platform": "Custom (plateforme unifiée propriétaire) + Shopify pour certains marchés internationaux",
            "confidence": "confirmed",
            "source": "Presse e-commerce + Shopify case study (ShopifyQL Notebooks pour US). abonnement.decathlon.fr = sous-domaine dédié, probablement microservice interne",
            "subscription_app": "Custom interne",
            "psp": "Multi-PSP (Adyen probable pour FR)",
            "note": "Décathlon = géant omnicanal, architecture modulaire en microservices"
        },
        "aqeelab": {
            "platform": "Shopify",
            "confidence": "confirmed",
            "source": "BuiltWith.com + StoresData.com — aqeelab-nutrition.fr = Shopify",
            "subscription_app": "Probablement Recharge ou Shopify Native",
            "psp": "Shopify Payments (Stripe)"
        },
        "myprotein": {
            "platform": "Custom (THG/The Hut Group proprietary — Ingenuity Commerce)",
            "confidence": "confirmed",
            "source": "Connu dans l'industrie — THG Ingenuity est la plateforme propriétaire du groupe",
            "subscription_app": "Custom / Ingenuity Commerce",
            "psp": "Multi-PSP (Adyen, PayPal, Klarna)",
            "note": "THG = tech company, plateforme blanche vendable à d'autres marques"
        }
    },
    "summary": {
        "shopify_dominant": True,
        "shopify_brands": ["Nutri&Co", "Nutrimuscle", "Novoma", "Aqeelab"],
        "custom_brands": ["Cuure", "Decathlon", "MyProtein"],
        "prestashop_brands": ["Nutripure"],
        "common_agency": "Axome (Nutri&Co, Nutrimuscle, Novoma)",
        "insight": "4/8 marques sur Shopify (dont 3 via la même agence Axome). PrestaShop = frein potentiel à l'abonnement (Nutripure). Les gros acteurs (Decathlon, MyProtein) ont du custom."
    }
}

# ============================================================
# 4. AVIS CLIENTS
# ============================================================
avis_clients = {
    "meta": {"phase": 4, "description": "Avis clients & satisfaction par marque", "last_updated": "2026-04-07"},
    "brands": {
        "nutriandco": {
            "trustpilot_score": 4.45,
            "trustpilot_nb_avis": 4400,
            "trustpilot_url": "https://fr.trustpilot.com/review/nutriandco.com",
            "points_forts": ["Qualité des ingrédients", "Transparence (certificats d'analyse)", "Service client réactif", "Marque française"],
            "points_faibles": ["Prix jugé élevé par certains", "Quelques retards de livraison"],
            "verbatims_abo": []
        },
        "nutrimuscle": {
            "trustpilot_score": 4.05,
            "trustpilot_nb_avis": 28000,
            "trustpilot_url": "https://fr.trustpilot.com/review/nutrimuscle.com",
            "points_forts": ["Catalogue très large", "Bon rapport qualité/prix", "Livraison rapide"],
            "points_faibles": ["Ruptures de stock fréquentes", "SAV parfois lent", "Emballage perfectible"],
            "verbatims_abo": ["Abonnement pratique pour les produits récurrents", "Parfois rupture de stock = livraison décalée"]
        },
        "novoma": {
            "trustpilot_score": 4.6,
            "trustpilot_nb_avis": 7000,
            "trustpilot_url": "https://fr.trustpilot.com/review/novoma.com",
            "points_forts": ["Formules clean sans additifs", "Transparence fabrication française", "Livraison rapide et soignée", "SAV réactif et bienveillant"],
            "points_faibles": ["Quelques retards ponctuels", "Rares cas de non-efficacité"],
            "verbatims_abo": []
        },
        "nutripure": {
            "trustpilot_score": 4.75,
            "trustpilot_nb_avis": 2000,
            "trustpilot_url": "https://fr.trustpilot.com/review/nutripure.fr",
            "points_forts": ["Labels premium (Epax, Peptan, Creapure)", "Transparence maximale", "Digestibilité", "Livraison 48-72h"],
            "points_faibles": ["Goûts neutres (whey)", "Prix plus élevé que concurrents étrangers", "Quelques ruptures de stock"],
            "verbatims_abo": ["N/A — pas d'abonnement"]
        },
        "cuure": {
            "trustpilot_score": 4.5,
            "trustpilot_nb_avis": 4400,
            "trustpilot_url": "https://fr.trustpilot.com/review/cuure.com",
            "points_forts": ["Personnalisation poussée", "Praticité sachets quotidiens", "Comité scientifique", "Application mobile"],
            "points_faibles": ["Reconduction automatique pas toujours transparente", "Coût qui monte vite avec beaucoup de compléments", "Goût oméga-3", "Résultats longs (3+ mois)"],
            "verbatims_abo": ["Surprise par la reconduction automatique", "Très pratique au quotidien", "Personnalisation top"]
        },
        "decathlon": {
            "trustpilot_score": 2.5,
            "trustpilot_nb_avis": 2950,
            "trustpilot_url": "https://fr.trustpilot.com/review/www.decathlon.fr",
            "site_interne_score": 4.47,
            "site_interne_nb_avis": 1700000,
            "points_forts": ["Rapport qualité/prix imbattable", "Réseau physique 1700+ magasins", "Programme fidélité", "Nutrition sportive basique efficace"],
            "points_faibles": ["SAV critiqué en ligne", "Problèmes de livraison", "Qualité inégale selon produits", "Peu de choix premium"],
            "verbatims_abo": ["Peu de retours spécifiques sur l'abonnement nutrition"],
            "note": "Écart important entre avis internes (4.47/5) et Trustpilot (2.5/5). Le Trustpilot reflète surtout les problèmes logistiques e-commerce."
        },
        "aqeelab": {
            "trustpilot_score": 4.9,
            "trustpilot_nb_avis": 200,
            "trustpilot_url": "https://fr.trustpilot.com/review/aqeelab-nutrition.fr",
            "site_propre_score": 4.85,
            "site_propre_nb_avis": "Plusieurs milliers",
            "points_forts": ["Qualité exceptionnelle", "Transparence ingrédients", "Livraison ultra-rapide (24-48h)", "SAV français réactif", "Éco-responsable"],
            "points_faibles": ["Peu d'avis Trustpilot (marque jeune)", "Quelques écarts emballage/site"],
            "verbatims_abo": []
        },
        "myprotein": {
            "trustpilot_score": 3.1,
            "trustpilot_nb_avis": 31000,
            "trustpilot_url": "https://fr.trustpilot.com/review/myprotein.com",
            "points_forts": ["Prix les plus bas du marché", "Catalogue gigantesque", "Promos permanentes", "Remise abo 30-45%"],
            "points_faibles": ["SAV très critiqué", "Retours coûteux", "Qualité variable selon produits", "Livraison parfois longue (UK warehouse)"],
            "verbatims_abo": ["Subscribe & save pratique mais attention aux prix qui changent", "Livraison parfois décalée sans prévenir"]
        }
    },
    "ranking_trustpilot": [
        {"brand": "Aqeelab", "score": 4.9, "nb_avis": 200},
        {"brand": "Nutripure", "score": 4.75, "nb_avis": 2000},
        {"brand": "Novoma", "score": 4.6, "nb_avis": 7000},
        {"brand": "Cuure", "score": 4.5, "nb_avis": 4400},
        {"brand": "Nutri&Co", "score": 4.45, "nb_avis": 4400},
        {"brand": "Nutrimuscle", "score": 4.05, "nb_avis": 28000},
        {"brand": "MyProtein", "score": 3.1, "nb_avis": 31000},
        {"brand": "Decathlon", "score": 2.5, "nb_avis": 2950}
    ]
}

# ============================================================
# 5. MARCHÉ
# ============================================================
marche = {
    "meta": {"phase": 5, "description": "Données marché nutrition sportive FR + économie abonnement", "last_updated": "2026-04-07"},
    "marche_nutrition_sportive_fr": {
        "taille_marche_total_eur": "~1 milliard €",
        "taille_segment_specialise_eur": "210 M€ (2023)",
        "evolution": {"2016": "110 M€", "2021": "152 M€", "2023": "210 M€"},
        "cagr_pct": 8.3,
        "segmentation": {
            "proteines_pct": 85,
            "gms_distribution_pct": 66,
            "online_growing": True
        },
        "tendances": [
            "Montée du premium / clean label",
            "Explosion DTC (direct to consumer)",
            "Convergence sport / bien-être / santé",
            "Demande transparence et traçabilité",
            "Nutrition personnalisée (Cuure, etc.)"
        ],
        "sources": ["Xerfi", "Euromonitor", "Grand View Research"]
    },
    "economie_abonnement": {
        "penetration_subscription_ecommerce_fr": "Croissante mais encore faible vs US/UK",
        "churn_mensuel_supplements_pct": "8-12%",
        "retention_annuelle_pct": "25-40%",
        "ltv_abonnes_eur": "300-800€",
        "ltv_multiplier_vs_oneshot": "3-5x",
        "flexibilite_impact": "Pause/skip réduit les annulations de 15-18%",
        "discount_sweet_spot_pct": "10-15% (au-delà érode la marge)",
        "sources": ["McKinsey Subscription Economy", "Recharge Benchmarks", "Bold Commerce"]
    },
    "comportement_consommateur": {
        "frequence_achat_moyenne": "Toutes les 4-6 semaines",
        "panier_moyen_nutrition_online_eur": "35-55€",
        "motivations_abonnement": [
            "Commodité (ne plus penser à commander)",
            "Économies (remise abonné)",
            "Régularité de prise (compliance)",
            "Livraison automatique"
        ],
        "freins_abonnement": [
            "Peur de l'engagement",
            "Crainte de recevoir un produit non voulu",
            "Difficulté à annuler (friction perçue)",
            "Accumulation de stock",
            "Variantes de goût (risque mauvaise surprise)"
        ]
    },
    "ecommerce_fr_global": {
        "ca_total_2024_eur": "175 milliards €",
        "croissance_annuelle_pct": 8
    }
}

# Write all files
for name, data in [
    ("catalogues.json", catalogues),
    ("logistique.json", logistique),
    ("tech_stack.json", tech_stack),
    ("avis_clients.json", avis_clients),
    ("marche.json", marche)
]:
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ {name} ({os.path.getsize(path):,} bytes)")

print("\n🎯 All 5 JSON files written successfully!")
