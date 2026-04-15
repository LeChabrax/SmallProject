# Section 5 — Analyse rentabilité / logistique

_Section 5 du deck mission. Construite à partir de `impulse_products.json` (COGS réels, 43 SKUs) + `rapport_rentabilite_abonnement.html` (modélisation LTV / cohortes) + benchmark logistique des 8 marques._
_Hypothèses TVA 20%, COGS HT fournisseur (Image Prix de Cession 2026). Dernière mise à jour : 2026-04-15._

---

## 1. Coût logistique moyen France — benchmark panel

### Tarifs Impulse (source fiable)

| Mode | Frais TTC | Frais HT |
|---|---|---|
| Point relais (Mondial Relay) | 3,90 € | **3,25 €** |
| Domicile (Colissimo) | 5,90 € | **4,92 €** |
| Express (Chronopost) | 10,90 € | 9,08 € |

### Fourchette du panel concurrent (one-shot standard, hors abo)

| Marque | Relais | Dom. | Source |
|---|---|---|---|
| **Impulse** | 3,25 € HT | 4,92 € HT | `impulse_products.json` |
| Nutri&Co | 4,50 € | 6,50 € | FAQ Zendesk |
| Nutrimuscle | 5,30 € | 7,50 € | CGV officiel |
| Novoma | 3,90 € | 4,90 € | /pages/livraison |
| Novoma (abo) | — | **3,50 €** | idem |
| Nutripure | 4,90 € | 5,90 € | CGV officiel |
| Aqeelab | 3,95-6,95 € | 6,45 € | CGV officiel |
| MyProtein | 3,99 € | 4,99 € | CGV officiel |
| Decathlon | **offert abo** | 3-4,50 € | FAQ abo |

→ **Impulse se situe en bas de fourchette marché** (3,25-4,92€ HT). Le brief posait une fourchette 4-7€ HT — Impulse est **en dessous**, c'est un avantage structurel à capitaliser dans la reco abo.

---

## 2. Modélisation — 3 scénarios du brief

_Hypothèses communes : remise abo **−15%** (choix Impulse), livraison domicile offerte (4,92€ HT à absorber), TVA 20%, COGS HT fournisseur réel._

### Scénario 1 — Mono-produit 15€ (Magnésium Bisglycinate)

_Prix retail Impulse : 15,90€ TTC. Marge brute HT : 76% avant remise._

| Élément | Valeur HT |
|---|---|
| Prix retail TTC | 15,90 € |
| Prix retail HT | 13,25 € |
| − Remise abo −15% | −1,99 € |
| **PVM net HT** | **11,26 €** |
| − COGS HT | −3,16 € |
| Marge brute après remise | 8,10 € |
| − Coût log HT (domicile offerte) | −4,92 € |
| **Contribution nette HT** | **3,18 €** ✅ |
| Taux de contribution | **24%** |

> ✅ **Rentable** mais le coût logistique pèse 44% de la marge brute après remise. C'est tendu sur un mono-produit à bas ticket — la marge brute Impulse élevée (76%) sauve la mise, mais toute hausse de tarif Colissimo fragiliserait ce scénario.

### Scénario 2 — Panier 35€ (Magnésium + Multivitamines)

_Panier type : Magnésium 15,90€ + Multivit 18,90€ = 34,80€ TTC. Marge brute HT moyenne : 84%._

| Élément | Valeur HT |
|---|---|
| Panier TTC | 34,80 € |
| Panier HT | 29,00 € |
| − Remise abo −15% | −4,35 € |
| **PVM net HT** | **24,65 €** |
| − COGS HT cumulé | −4,38 € |
| Marge brute après remise | 20,27 € |
| − Coût log HT (domicile offerte) | −4,92 € |
| **Contribution nette HT** | **15,35 €** ✅ |
| Taux de contribution | **53%** |

> ✅ **Très rentable**. C'est exactement le point d'équilibre où le deuxième SKU absorbe complètement le coût logistique. **C'est la justification du seuil de livraison offerte à 35€** — au-dessus, le modèle économique devient confortable sur toutes les combinaisons de SKUs.

### Scénario 3 — Pack 3 SKUs ~50€ (Magnésium + Multivit + Créatine)

_Panier santé + sport : Magnésium 15,90€ + Multivit 18,90€ + Créatine 12,90€ = 47,70€ TTC. Le panier cible qu'on veut encourager._

| Élément | Valeur HT |
|---|---|
| Panier TTC | 47,70 € |
| Panier HT | 39,75 € |
| − Remise abo −15% | −5,96 € |
| **PVM net HT** | **33,79 €** |
| − COGS HT cumulé | −8,04 € |
| Marge brute après remise | 25,75 € |
| − Coût log HT (domicile offerte) | −4,92 € |
| **Contribution nette HT** | **20,83 €** ✅ |
| Taux de contribution | **52%** |

> ✅ **Idéal.** La contribution nette est près de 7× supérieure au scénario mono-produit. C'est le panier cible à encourager via l'upsell dans le parcours de souscription.

---

## 3. Sensibilité à la remise — tableau comparatif

_Même panier 35€ (Magnésium + Multivit), variation de la remise._

| Remise | PVM net HT | Marge HT après remise | Contribution nette HT | Taux |
|---|---|---|---|---|
| **−10%** (Novoma) | 26,10 € | 21,72 € | **16,80 €** | 58% |
| **−15%** (reco Impulse) | 24,65 € | 20,27 € | **15,35 €** | 53% |
| **−20%** (Aqeelab) | 23,20 € | 18,82 € | **13,90 €** | 48% |
| **−30%** (MyProtein) | 20,30 € | 15,92 € | **11,00 €** | 38% |
| **−45%** (MyProtein promo) | 15,95 € | 11,57 € | **6,65 €** | 19% |

> **Lecture** : sur un panier 35€, Impulse peut se permettre jusqu'à **−30% de remise et rester largement rentable** (11€ de contribution nette). Le choix de **−15% est donc prudent et laisse une marge de manœuvre** en cas de campagne promo ponctuelle. À l'inverse, le modèle MyProtein à −45% flash est soutenable **uniquement** grâce aux volumes internationaux qu'Impulse n'a pas.

---

## 4. Seuil de rentabilité — panier minimum

### Question du brief

> *"À partir de quel ticket moyen l'abonnement avec livraison offerte est-il rentable si on accorde −10% de remise ?"*

### Réponse modélisée

À −10% de remise et avec un coût log domicile 4,92€ HT, le panier mini rentable dépend de la marge brute du SKU :

| Marge brute HT | Panier HT minimum | Panier TTC minimum |
|---|---|---|
| 90% (multivit, sommeil, spiruline) | ~6 € | ~7 € |
| 80% (pré-probiotiques) | ~7 € | ~8 € |
| 75% (magnésium) | ~7 € | ~8 € |
| 65% (oméga-3, créatine, collagène) | ~8 € | ~10 € |
| **Seuil universel (le moins marge)** | **~8 € HT** | **~10 € TTC** |

_Formule : `panier_min_HT = coût_log_HT / (marge_brute_pct × (1 − remise))`_

> **Conclusion** : tous les SKUs éligibles Impulse sont rentables dès 10€ TTC minimum, même au pire cas (marge 65%). Le **seuil 35€ de la reco** est donc **très prudent** et sert surtout à **encourager l'upsell** (augmenter le panier moyen) plutôt qu'à protéger la marge.

### Arbitrage stratégique

**Option A — Seuil 35€ TTC** (reco actuelle, prudente)
- Avantage : encourage l'upsell 2→3 SKUs → LTV supérieure
- Risque : friction sur les mono-produits à faible ticket (certains clients vont abandonner)

**Option B — Livraison offerte sans seuil** (pattern Nutri&Co, Nutrimuscle, MyProtein)
- Avantage : conversion maximale, CTA simple "livraison offerte sur l'abo"
- Risque : marge tendue sur les mono-produits à 12-15€, dépendance au volume

**Recommandation** : **Option A pour le lancement** → plus sûre, permet d'observer la réalité des paniers. **Révision vers Option B en Phase 2** si le taux de conversion est insuffisant.

---

## 5. Scénarios cohorte — projection 24 mois

_Distillé du `rapport_rentabilite_abonnement.html` — simulation 100 abonnés, 24 mois, panier 2 SKUs (Magnésium + Oméga-3), remise −15%, livraison offerte._

| Scénario | Durée vie moy. | LTV brute HT | LTV nette HT (après COGS + log) |
|---|---|---|---|
| 🟢 **Optimiste** | 13,8 mois | ~568 € | **481 €** |
| 🟡 **Baseline** | 10,8 mois | ~445 € | **378 €** |
| 🔴 **Pessimiste** | 7,6 mois | ~313 € | **267 €** |

### Interprétation

- **LTV pessimiste à 267€** reste supérieure au CAC typique du marché FR compléments alimentaires (estimé 40-80€ sur Meta Ads)
- **Ratio LTV / CAC baseline** : ~5-9× → très sain
- **Break-even sur l'app de souscription** (coût estimé ~500€/mois) : **14 abonnés actifs** (source : rapport_rentabilite_abonnement.html)

→ **Le modèle économique est solide dès les premiers 50 abonnés** du MVP Phase 1.

---

## 6. Break-even — combien d'abonnés pour couvrir l'investissement ?

### Hypothèses

- **Coût app abonnement** : 500€/mois (fourchette Recharge / Bold / Shopify Native)
- **Coût fixe design + setup initial** : 5 000€ one-shot (maquettes + intégration)
- **Contribution nette moyenne par abonné/mois** : ~13€ (panier baseline 35€ à −15%, hypothèse centrale)

### Calcul

- **Break-even mensuel** (couvrir l'app seule) : 500 / 13 = **39 abonnés actifs**
- **Break-even total** (amortir le setup sur 12 mois) : (5 000 / 12 + 500) / 13 = **70 abonnés actifs** la première année
- **ROI positif dès le 2e mois** à 100 abonnés actifs

### Projection réaliste

| Mois | Abonnés actifs (objectif) | Contribution nette mensuelle | Statut |
|---|---|---|---|
| M1 | 20 | 260 € | Investissement |
| M3 | 50 | 650 € | Break-even app |
| M6 | 100 | 1 300 € | Break-even total |
| M12 | 200+ | 2 600 € | ROI positif |

---

## 7. Risques rentabilité à surveiller

| Risque | Impact | Mitigation |
|---|---|---|
| **Hausse tarifs Colissimo / Mondial Relay** | Grignote la marge contributive | Renégocier annuellement via BigBlue, prévoir un seuil livraison ajustable |
| **Cannibalisation one-shot** | Clients existants basculent vers abo −15% → baisse du CA brut | Mesurer le % de new customers vs migration, ajuster la mise en avant |
| **Churn élevé sur Whey (Phase 2)** | Risque mauvaise surprise goût | Lock goût au lieu de variation libre, email pré-expédition |
| **Ruptures de stock** | Verbatim Nutrimuscle et Cuure montrent que ça tue la confiance | Stock buffer de sécurité calé sur la base abo prévisionnelle, notification proactive |
| **SAV débordé** | Abo amplifie l'importance du SAV (leçon MyProtein Trustpilot 3,1) | Process dédié gestion des plaintes abo, auto-crédit en cas de retard > 3j |

---

## 8. Conclusion rentabilité

> **Le modèle −15% flat avec livraison offerte dès 35€ est largement rentable sur Impulse** grâce à des marges brutes HT exceptionnellement élevées (62-92% selon SKU) et à un coût logistique compétitif (3,25€ relais / 4,92€ domicile HT, en bas de fourchette marché).

**3 chiffres à retenir pour le comité** :

1. **Contribution nette HT sur un panier abo 35€ : 15,35 €** (soit 53% du panier HT)
2. **Break-even atteint dès 39 abonnés actifs** (couvre l'app ; ROI total à 70 abonnés)
3. **LTV baseline 378€ HT** pour une durée de vie de 10,8 mois → ratio LTV/CAC très sain

---

_Pour le détail complet des calculs par SKU, voir `benchmark/rapport_rentabilite_abonnement.html` (43 produits scorés individuellement avec matrice contribution nette, scoring rentabilité, simulation cohortes par scénario)._
