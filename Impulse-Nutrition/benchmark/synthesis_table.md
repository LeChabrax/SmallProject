# Benchmark abonnement — Tableau de synthèse comparatif

_Section 4 du deck mission. Généré à partir de `benchmark/marques/<brand>/data.json` via `build_synthesis_table.py`._
_Dernière mise à jour : 2026-04-15 — 8/8 marques verified_live._

---

## Table 1 — Modèle commercial

| Marque | Remise | Fréquences | Livraison abo | Engagement | Stacking codes |
|---|---|---|---|---|---|
| **Aqeelab Nutrition** | −20% | 3 (1 mois, 2 mois, 3 mois) | ❓ Non explicité | ✅ Aucun | ❌ Zéro |
| **Nutri&Co** | −15% | 2 (1 mois, 3 mois) | ✅ Flat (sans seuil) | ✅ Aucun | ❌ Zéro |
| **Nutrimuscle** | −15% | 6 (1 mois, 2 mois, 3 mois, 4 mois, 5 mois, 6 mois) | ✅ Flat (sans seuil) | ✅ Aucun | ⚪ Partiel |
| **Novoma** | −10% | 3 (1 mois, 2 mois, 3 mois) | ⚪ Stepped (dès 50€) | ✅ Aucun | ⚪ Partiel |
| **Cuure** | — | 1 (1 mois (mensuel uniquement)) | ✅ dès 20€ | ✅ Aucun | ❓ Non documenté |
| **MyProtein** | Jusqu'à 45% (variable, 30% standard en moyenne) | 5 (1 mois, 2 mois, 3 mois, 4 mois, 5 mois) | ✅ Flat (sans seuil) | ✅ Aucun | ✅ Possible |
| **Decathlon (Abonnement Nutrition)** | 10-15% (stepped par produit, pas flat) | 3 (1 mois, 2 mois, 3 mois) | ⚪ Relais only | ✅ Aucun | ❓ Non documenté |
| **Nutripure** | — | — | ❓ Non explicité | — | ❓ Non documenté |

## Table 2 — Périmètre produit + UX

| Marque | Scope | Exclusions | Ticket moyen | Page dédiée | Home / Nav | CTA |
|---|---|---|---|---|---|---|
| **Aqeelab Nutrition** | Tous les 23 produits du catalogue | Aucune documentée | 45€ | ✅ | ✅ / ✅ | S'abonner & économiser |
| **Nutri&Co** | Produits individuels uniquement — le modèle '1 produit = 1 abonnement'… | Packs de compléments · Coffrets cadeaux | 35€ | ✅ | ❌ / ❌ | S'abonner |
| **Nutrimuscle** | Sélection de produits (250+ formats éligibles). Modèle '1 produit = 1 … | Packs · Gros formats · Textile et accessoires | 45€ | ✅ | ✅ / ✅ | S'abonner |
| **Novoma** | Tous les produits individuels du catalogue (aucune exclusion explicite… | Packs probablement exclus | 30€ | ✅ | ❌ / ❌ | S'abonner |
| **Cuure** | Box personnalisée uniquement — aucun catalogue individuel public. 50+ … | Pas d'achat one-shot poss | 35€ | ✅ | ✅ / ✅ | Découvrir ma formule |
| **MyProtein** | Quasi tous les produits (1000+ références) | Aucune documentée | 35€ | ✅ | ✅ / ✅ | S'abonner |
| **Decathlon (Abonnement Nutrition)** | Scope plus large que prévu (vérifié 2026-04-15). Catégorie nutrition c… | Produits one-shot ou sais · Probables : promotions po | 40€ | ✅ | ✅ / ✅ | S'abonner |
| **Nutripure** | N/A | Aucune documentée | — | ❌ | ❌ / ❌ | N/A |

## Table 3 — Évaluation synthétique

| Marque | UX /5 | Offre /5 | Pertinence /5 | **Global /5** | Trustpilot | Highlight |
|---|---|---|---|---|---|---|
| **Aqeelab Nutrition** | 4.5 | 4.0 | 4.5 | **4.3** | 4.9 / 200 | Remise -20% flat à vie |
| **Nutri&Co** | 3.5 | 4.0 | 4.5 | **4.0** | 4.45 / 4.4k | Toggle clair sur la fiche produit |
| **Nutrimuscle** | 4.0 | 4.0 | 3.5 | **3.8** | 4.05 / 28.0k | Page dédiée complète |
| **Novoma** | 3.5 | 3.0 | 4.5 | **3.7** | 4.6 / 7.0k | Page dédiée très bien structurée |
| **Cuure** | 4.0 | 3.0 | 2.0 | **3.0** | 4.5 / 4.4k | UX 100% orientée abonnement |
| **MyProtein** | 3.5 | 3.5 | 1.5 | **2.8** | 3.1 / 31.0k | Remise la plus agressive du panel en valeur brute |
| **Decathlon (Abonnement Nutrition)** | 2.5 | 3.0 | 2.0 | **2.5** | 2.5 / 3.0k | Sous-site dédié |
| **Nutripure** | — | — | 4.5 | **N/A** | 4.75 / 2.0k | UX produit très clean et premium |

---

## Lecture stratégique

### Deux patterns antagonistes détectés

**Pattern A — Acquisition agressive** (Aqeelab, Nutri&Co, Nutrimuscle, MyProtein)
- Remise élevée (−15% à −45%) + livraison offerte sans seuil + zéro engagement (sauf Aqeelab)
- Cible : conversion rapide, accepte de sacrifier la marge sur la livraison
- Risque : cannibalisation du one-shot, lock-in psychologique seulement

**Pattern B — Rentabilité prudente** (Novoma, Decathlon)
- Remise modérée (−10% à −15%) + livraison stepped (frais réduits, pas offerte) + zéro engagement
- Cible : protéger la marge, offrir un avantage tangible mais chiffré
- Risque : moins attractif en CTA, moins de conversion en haut de funnel

**Cas atypiques** :
- **Cuure** : modèle 100% abo personnalisé (quiz + box). Hors championnat Impulse.
- **Nutripure** : pas d'abonnement — mise sur les packs permanents (−10 à −25%) + fidélité + qualité premium. Prouve que l'abo n'est pas obligatoire pour fidéliser.

### Classement par note globale

1. 🥇 **Aqeelab** (4,3) — remise massue −20% à vie, UX persuasive avec montant économisé en €, mais engagement 2 mois à vérifier Loi Chatel
2. 🥈 **Nutri&Co** (4,0) — la référence proche Impulse, offre solide et email pré-expédition 48h, module discret qui pourrait être plus visible
3. 🥉 **Nutrimuscle** (3,8) — visibilité maximale (home + nav + emails), 6 fréquences, offre claire, moins proche Impulse en positionnement
4. **Novoma** (3,7) — positionnement santé premium très proche Impulse, offre la plus modérée mais bien construite (FAQ, rationale santé)
5. **Cuure** (3,0) — excellent UX orienté service, trop éloigné structurellement d'Impulse
6. **MyProtein** (2,8) — remise la plus haute en valeur brute mais illisible, pire Trustpilot du panel
7. **Decathlon** (2,5) — contre-modèle UX (sous-domaine séparé, 1 produit = 1 abo)
8. **Nutripure** (contrôle) — pas d'abo, mais le cas prouve que la qualité + packs permanents suffisent parfois

### Top 3 inspirations pour la reco Impulse

| Rang | Source | Quoi reprendre |
|---|---|---|
| 1 | **Aqeelab** | Wording 'S'abonner & économiser' + affichage du montant économisé en euros |
| 2 | **Nutri&Co** | Email de pré-expédition avec fenêtre de modification 48h (anti-churn éprouvé) |
| 3 | **Nutrimuscle** | Visibilité max : mention homepage + navigation + newsletter |

### Top 3 anti-patterns à éviter

| Rang | Source | Quoi éviter |
|---|---|---|
| 1 | **Decathlon** | Sous-domaine séparé + '1 produit = 1 abo' + 'modification = résiliation+recréation' |
| 2 | **Cuure** | Résiliation en 2 temps (suspension self-serve vs email pour résilier) |
| 3 | **MyProtein** | Prix de base instables qui rendent la remise abo illisible |
