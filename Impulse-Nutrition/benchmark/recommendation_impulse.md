# Recommandation Impulse — Modèle d'abonnement

_Section 6 du deck mission. Distillée à partir des 8 `marques/<brand>/notes.md` + `synthesis_table.md` + contexte Impulse (`impulse_products.json`, `rapport_rentabilite_abonnement.html`)._
_Dernière mise à jour : 2026-04-15._

---

## Verdict en une phrase

> Lancer un **Subscribe & Save à −15% flat** sur une sélection curée de **6 SKUs** à consommation naturellement récurrente, **sans engagement**, avec **livraison domicile offerte dès 35€**, intégré en toggle sur chaque fiche produit, avec email anti-churn 48h avant chaque renouvellement.

## Contexte d'entrée

| Contrainte | Valeur | Implication pour la reco |
|---|---|---|
| Tech e-commerce | Shopify (confirmé) | Intégration Recharge / Bold / Native Subscriptions — pas de refonte lourde |
| Catalogue | 43 produits (17 santé + 20 sport + 4 accessoires + 2 snacks) | Sélection curée sur 6-10 SKUs au lancement |
| Positionnement | Premium FR, made in France, transparence qualité | S'inspirer de Nutri&Co / Novoma, pas de MyProtein / Decathlon |
| Logistique | BigBlue + Mondial Relay / Colissimo | Coûts HT : relais 3,25€, domicile 4,92€ |
| Persona client | Vouvoiement service client formel | Tone de l'email pré-expédition → Impulse Nutrition (pas Antoine) |

---

## 1. Produits éligibles — sélection curée

### ✅ Candidats naturels (MVP Phase 1 — 6 SKUs)

| SKU | Catégorie | Pourquoi abonner |
|---|---|---|
| **Magnésium Bisglycinate** | Santé · Minéraux | Consommation quotidienne, 1-2 mois/pot, récurrence garantie |
| **Oméga-3 EPAX®** | Santé · Acides gras | Quotidien, 1-2 mois, SKU phare Impulse |
| **Multivitamines** | Santé · Vitamines | Quotidien, 1-2 mois, panier d'entrée naturel |
| **Pré-Probiotiques** | Santé · Digestion | Quotidien, cure de 2-3 mois, récurrence naturelle |
| **Sommeil +** | Santé · Adaptogènes | Quotidien le soir, récurrence totale |
| **Créatine Monohydrate** | Sport · Performance | 5 g/jour, 1-2 mois, SKU d'acquisition sportive |

_(Les 6 SKUs retenus correspondent tous au top GO du scoring rentabilité dans `rapport_rentabilite_abonnement.html` — score ≥ 79.)_

### ⚠️ À traiter avec précaution (Phase 2, après validation Phase 1)

- **Whey** (avec variantes de goût) — risque de mauvaise surprise au renouvellement. Si lancé, **figer le goût à la souscription** avec bouton "changer de goût" accessible dans l'espace abonné.
- **Collagène Marin** — selon format et goût, à tester après les 6 SKUs neutres.

### ❌ À exclure du lancement

| Catégorie | Raison |
|---|---|
| Packs / coffrets / bundles | Composition figée incompatible avec abo récurrent (pattern Nutri&Co, Nutrimuscle, Novoma) |
| Accessoires (shakers, doseurs, textile) | Pas de récurrence naturelle |
| Snacks (barres, boissons ponctuelles) | Consommation irrégulière, saisonnière |
| Électrolytes effervescents | Consommation événementielle (entraînement), récent, COGS encore estimé |
| Produits en rupture de formule ou saisonniers | Risque d'indisponibilité au renouvellement |

---

## 2. Modèle commercial recommandé

### Remise : **−15% flat**

**Justification** :
- **Aligné Nutri&Co + Nutrimuscle** — la référence marché FR premium sur laquelle se positionner
- **Sous Aqeelab (−20%)** mais avec **zéro engagement** en contrepartie — plus éthique et conforme Loi Chatel (voir risques §5)
- **Au-dessus de Novoma (−10%)** — plus attractif en CTA sans sacrifier la marge
- **Soutenable** selon le rapport rentabilité (marges brutes Impulse entre 40% et 65% HT selon SKU)

### Fréquences : **1 mois / 2 mois / 3 mois**

**Justification** :
- **1 mois** : hauts volumes quotidiens (créatine, whey)
- **2 mois** : sweet spot pour un pot de 60 gélules (magnésium, multivit) — absent chez Nutri&Co (2 options seulement), Impulse peut s'en différencier
- **3 mois** : gros formats, ticket plus élevé
- **Pas de 4/5/6 mois** au lancement — Nutrimuscle l'a fait mais c'est une différenciation marginale qui alourdit l'onboarding

### Livraison abo : **offerte domicile dès 35€** (modèle hybride)

**Justification** — pattern intermédiaire entre Nutri&Co (flat sans seuil) et Novoma (stepped 50€) :
- **35€** = seuil réaliste pour un panier de 2 SKUs chez Impulse (prix moyen ~20€)
- **Protège la marge** sur les mono-produits à bas ticket (créatine seule ~15€)
- **Incite à l'upsell 2→3 produits** → meilleur LTV
- **En dessous de 35€** : tarif relais 3,25€ HT (pas de pénalité excessive pour le client)

### Engagement : **Aucun, annulation 1 clic dans l'espace abonné**

**Justification** :
- **Conformité Loi Chatel sans effort** — la résiliation doit être aussi facile que la souscription
- **Leçon Aqeelab** — l'engagement 2 mois minimum est une friction d'entrée qui tue la conversion
- **Leçon Cuure** — l'architecture "suspension self-serve vs résiliation par email" crée du mécontentement documenté ("surprise par la reconduction automatique")
- **Différenciation forte** : transparence totale = signal de confiance supérieur à Aqeelab et Cuure

### Stacking codes : **partiel sélectif** (approche Nutrimuscle)

| Type de code | Cumul avec abo ? | Raison |
|---|---|---|
| **Code welcome first order** | ✅ Oui sur la 1ère commande abo | Réduire la friction conversion |
| **Codes promo ponctuels génériques** | ❌ Non | Protéger la marge sur les renouvellements |
| **Codes ambassadeurs / influenceurs** | ✅ Oui | Booster l'acquisition via le réseau ambassadeurs |
| **Code de parrainage** | ❌ Non | Programme distinct |

Cette approche est **plus claire** que Nutrimuscle (qui a un pattern similaire mais mal communiqué) et **plus souple** que Nutri&Co (zéro stacking).

---

## 3. UX / Positionnement recommandé

### Wording CTA : **"S'abonner & économiser"** (inspiré Aqeelab)

Ne pas se contenter du basique "S'abonner" (Nutri&Co, Nutrimuscle, Novoma, Decathlon, MyProtein). Le mot **"économiser"** est un déclencheur psychologique qui rend le bénéfice tangible sur le CTA lui-même.

### Affichage du montant économisé en euros (inspiré Aqeelab)

Sur chaque fiche produit, afficher :

```
Prix one-shot :     29,90 €
Prix abonné :       25,42 €   ·   Vous économisez 4,48 €
```

C'est **le pattern le plus persuasif** observé dans le panel. Beaucoup plus tangible que "−15%" abstrait. Aqeelab est le seul à le faire.

### Placement module : toggle radio sur chaque fiche produit

Au-dessus du bouton "Ajouter au panier", intégré naturellement au sélecteur de prix et de format. Pattern universel validé par Nutri&Co, Nutrimuscle, Aqeelab, Novoma.

### Page dédiée `/pages/abonnement`

Structure inspirée de **Novoma** (la plus claire du panel) :

1. **Hero pitch éditorial** (inspiré Novoma) — *"Les compléments agissent sur la durée. L'abonnement, c'est pour laisser le temps à vos résultats."* Justification santé, pas juste promotion.
2. **Processus en 3 étapes illustré** : choix SKU → choix fréquence → paiement
3. **5 avantages chiffrés** : −15% à vie, livraison offerte dès 35€, fenêtre de modification 48h, sans engagement, gérer depuis l'espace abonné
4. **FAQ complète** (6-8 questions sur les sujets sensibles : annulation, modification, livraison manquée, changement de format, rupture de stock, cumul codes)
5. **Lien vers espace abonné**

### Visibilité (inspirée Nutrimuscle)

- ✅ **Bannière homepage** avec CTA direct "S'abonner & économiser"
- ✅ **Mention navigation** principale (lien explicite)
- ✅ **Mention dans les emails** (welcome + post-purchase + newsletter mensuelle)
- ✅ **Lien footer**

### Email pré-expédition avec fenêtre de modification 48h (inspiré Nutri&Co)

Anti-pattern churn éprouvé. Envoyé automatiquement 48h avant chaque prélèvement, avec bouton direct :

- "Modifier ma prochaine commande"
- "Reporter d'une semaine"
- "Suspendre mon abonnement"

C'est le seul mécanisme documenté du panel qui réduit les plaintes "surpris par le renouvellement". Nutri&Co le fait très bien, à répliquer tel quel.

---

## 4. Seuil de rentabilité — modélisation simplifiée

_(Détail complet dans la section 5 du deck — ici on pose le raisonnement.)_

### Exemple mono-produit — Magnésium Bisglycinate 19,90€

| Élément | Valeur HT |
|---|---|
| Prix retail TTC | 19,90 € |
| Prix retail HT | 16,58 € |
| Remise abo −15% | −2,49 € |
| **PVM net HT** | **14,09 €** |
| COGS estimé HT | ~5,00 € (fourchette moyenne) |
| Marge brute HT avant log | 9,09 € |
| Coût log HT (domicile offerte) | −4,92 € |
| **Contribution nette HT** | **4,17 €** |

→ **Rentable en mono-produit sous condition** que la marge brute soit ≥ 55%. C'est **tendu** pour les SKUs à marge 40%.

### Exemple panier 2 SKUs — Magnésium + Oméga-3 à 42€

| Élément | Valeur HT |
|---|---|
| Panier TTC | 42,00 € |
| Panier HT | 35,00 € |
| Remise abo −15% | −5,25 € |
| **PVM net HT** | **29,75 €** |
| COGS cumulé HT | ~11,00 € |
| Marge brute HT avant log | 18,75 € |
| Coût log HT (domicile offerte) | −4,92 € |
| **Contribution nette HT** | **13,83 €** |

→ **Très rentable** dès que le panier dépasse 35€ HT. C'est la justification du **seuil de livraison offerte à 35€**.

### Conclusion seuil

Le **seuil de livraison offerte à 35€** garantit la rentabilité même sur les SKUs à marge 40-50%. En dessous, la rentabilité dépend fortement du COGS réel — à valider SKU par SKU lors de la mise en place technique.

---

## 5. Risques et anti-patterns à éviter

| Risque | Source leçon | Contre-mesure Impulse |
|---|---|---|
| Sous-domaine séparé = friction redirect | Decathlon | Intégrer dans `impulse-nutrition.fr` natif, pas de sous-domaine |
| "1 produit = 1 abo" = mauvaise UX multi | Decathlon | Autoriser le panier multi-produits dans une même commande abo |
| Modification = résiliation + recréation | Decathlon | Gérer pause / skip / modification SKU / changement fréquence dans l'espace abonné, sans casser l'abo |
| Résiliation en 2 temps (suspension + email) | Cuure | Résiliation définitive self-serve en 1 clic depuis l'espace abonné |
| Engagement minimum forcé | Aqeelab | Zéro engagement, compatible Loi Chatel de bout en bout |
| Prix de base instables | MyProtein | Prix one-shot stables (pas de promos permanentes qui rendent la remise abo illisible) |
| Page dédiée invisible | Nutri&Co | Mention homepage + navigation + emails (pattern Nutrimuscle) |
| Friction reconduction auto | Cuure + verbatims | Email pré-expédition 48h avec fenêtre de modification (pattern Nutri&Co) |
| Opacité programme fidélité | Aqeelab RePoints | Si programme fidélité lancé, communication transparente dès la homepage |

---

## 6. Roadmap déploiement suggérée

### Phase 1 — MVP (mois 0-3)

- **6 SKUs** du Top GO du scoring rentabilité (Magnésium, Oméga-3, Multivitamines, Pré-Probiotiques, Sommeil +, Créatine)
- **Toggle fiche produit** + **page dédiée** `/pages/abonnement` + **mention homepage**
- **Engagement zéro**, **−15% flat**, **livraison offerte dès 35€**
- **Email pré-expédition 48h** actif dès le 1er renouvellement
- **Objectif quantitatif** : 50-100 abonnements actifs, mesurer churn à 3 mois
- **KPIs à suivre** : taux de conversion fiche → abo, taux de churn à 30/60/90 jours, panier moyen abo vs one-shot

### Phase 2 — Optimisation (mois 3-6)

- **Ajout du Whey** avec lock goût à la souscription (bouton "changer de goût" dans l'espace abonné)
- **Test A/B** : wording "S'abonner" vs "S'abonner & économiser"
- **Programme de fidélité cumulable** (inspiré Novoma : points sur achats abo, dépensables sur commandes one-shot → upsell)
- **Analyse cohortes churn par SKU** → éventuelle correction remise ou fréquence par catégorie
- **Élargissement fréquences** si demande client (4-6 mois sur les gros formats uniquement)

### Phase 3 — Scale (mois 6-12)

- **Élargir** à tous les SKUs éligibles (hors packs / accessoires / snacks)
- **Programme de parrainage abo** (inspiré Decat'Club de Decathlon : points sur compte global cross-canal)
- **Quiz d'onboarding léger** (inspiré Cuure, mais sans le modèle 100% abo) — outil d'acquisition sur la page dédiée
- **Optimisation algorithme recommandation** : upsell 2→3 produits dans le flow de souscription
- **Intégration avec le programme ambassadeurs** : codes influenceurs cumulables avec abo, tracking cross-canal

---

## 7. Prochaines étapes immédiates

1. **Validation comité projet** du modèle commercial (remise, fréquences, engagement, livraison, stacking)
2. **Audit Loi Chatel** : valider la compatibilité avec un juriste avant GA (1-2 jours)
3. **Choix tech** : Recharge vs Shopify Native Subscriptions vs Bold Subscriptions — devis et benchmark fonctionnel (1 semaine)
4. **Mesure baseline** : export Shopify 90 jours pour estimer le potentiel d'abonnés par SKU et confirmer le scoring rentabilité
5. **Design / maquettes** : fiche produit avec toggle + page abo dédiée + email pré-expédition (1-2 semaines)
6. **Mise en place technique** : intégration app choisie + configuration SKUs éligibles + email workflow (2-3 semaines)
7. **Lancement soft** : 6 SKUs, communication limitée (newsletter + homepage), mesure baseline (1 mois)
8. **Lancement officiel** : après 1 mois de soft launch et ajustements UX

---

_Référentiel complet : 8 fiches marques dans `benchmark/marques/<brand>/`. Chaque source (citation, URL, verbatim) est traçable via les fichiers `sources.md` et `notes.md`._
