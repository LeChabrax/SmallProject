# Cuure — notes de revue

## Statut audit
- Audit status : `verified_live` (homepage + Centre d'Aide officiel Zendesk + 3 sources secondaires croisées 2026-04-15)

## Rôle dans le panel
**Marque la plus atypique du panel** — modèle 100% abonnement (pas de one-shot possible), personnalisation algorithmique via quiz santé, sachets quotidiens pré-dosés. Utile pour le deck Impulse comme **contre-modèle extrême** : ce qui arrive quand on pousse l'abonnement à fond, avec ses forces et ses friction points documentés.

## Vérifs live (2026-04-15)

### Prix réels confirmés (correction majeure vs master_data)
Le master_data listait "price_range: 24-40€/mois" pour la box personnalisée mais aucun prix exact. Les vérifs live donnent :
- **Programme standard** : **39,90€/mois** (référence pricing officielle mentionnée)
- **Compléments individuels** : 6€ (zinc, fer, vit C) → 29€ (collagène)
- **Cure moyenne 3 compléments** : 18-40€/mois selon composition
- **Coût/jour** : 0,66-1,33€

### Fréquences — correction importante
Le master_data listait `["1 mois", "2 mois", "3 mois"]`. **Aucune source externe (ni la homepage) ne confirme les fréquences bimestrielle ou trimestrielle**. Le modèle Cuure est **mensuel uniquement** — la "box mensuelle" est la brique de base et il n'y a pas d'option de décaler le rythme. Corrigé.

### Friction résiliation — le mécanisme caché
C'est la **vraie découverte** de la revue Cuure. Le modèle est présenté comme "100% flexible et sans engagement" mais l'architecture est en **2 temps** :
- **Suspension self-serve** : dashboard → onglet Commandes → suspendre (1 clic)
- **Résiliation définitive** : email à support@cuure.com obligatoire (pas de bouton self-serve)
- **Annulation commande** : fenêtre de 1h seulement après enregistrement

**Pourquoi c'est important** : les verbatims documentés sur Trustpilot disent *"Surprise par la reconduction automatique"*. L'explication probable est que les clients **suspendent** (pensant avoir résilié) puis sont surpris quand le prélèvement reprend au retour de suspension. Cette architecture est un **anti-pattern UX** bien connu (dark pattern à la limite de la Loi Chatel).

**Implication Impulse** : dans la reco, explicitement mettre en garde contre ce mécanisme. La résiliation doit être aussi facile que la souscription. C'est un point de différenciation potentiel pour Impulse vs Cuure.

### Livraison offerte dès 20€
Confirmé. Frais standard 6,50€. Avec un programme standard à 39,90€/mois, la livraison est **systématiquement offerte**. C'est une dépendance structurelle à ne pas oublier : le prix du programme Cuure est conçu pour dépasser le seuil de gratuité.

### Quiz santé — architecture documentée
- Durée : ~5 minutes
- Thématiques : mode de vie, habitudes alimentaires, niveau de stress, objectifs santé, sommeil, concentration, immunité, digestion
- Validation : comité scientifique (médecins nutritionnistes, pharmaciens, naturopathes, biologistes)
- Algorithme : sort 2 à 8 compléments adaptés au profil
- Résultat : box mensuelle avec 30 sachets pré-dosés, 1 par jour
- **Touch personnalisé physique** : prénom imprimé sur les sachets + messages de motivation
- **Bonus rétention** : téléconsultations avec experts nutrition accessibles aux abonnés

### Engagement psychologique
Le parcours est **conçu pour maximiser l'engagement psychologique** :
1. Le client investit 5 minutes dans le quiz → effet IKEA (plus on met d'efforts, plus on valorise)
2. La recommandation est **nominative** (prénom sur les sachets) → effet identitaire
3. L'app mobile rend l'usage quotidien → habit formation
4. Les téléconsultations créent une relation humaine → rétention émotionnelle

Ces 4 leviers constituent le **vrai produit** Cuure — les compléments eux-mêmes sont secondaires. C'est un **service de bien-être personnalisé**, pas une vente de compléments. Cette distinction est critique pour comparer Cuure aux autres marques du panel : Cuure ne joue **pas** dans le même championnat.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_pct` | `"~10% vs achat individuel"` (string) | `null` (pas pertinent — pas de one-shot de référence) | Vérifs live |
| `modele_commercial.remise_note` | Version courte | Version détaillée avec prix 18-40€, 39,90€ standard, remise théorique | leblogdeneroli + darwin-nutrition |
| `modele_commercial.frequencies` | `["1 mois", "2 mois", "3 mois"]` | `["1 mois (mensuel uniquement)"]` | homepage + sources secondaires |
| `modele_commercial.flexibility.cancel_anytime` | `true` | `"partiel — suspension OK, résiliation par email"` | support.cuure.com |
| `modele_commercial.engagement_min` | `"Aucun"` | Note détaillée architecture en 2 temps + fenêtre 1h | support.cuure.com |
| `modele_commercial.livraison_abo.offerte` | `null` | `true` (dès 20€) | cuure.com + leblogdeneroli |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `20` | idem |
| `perimetre_produit.scope` | `"50+ ingrédients, 2M+ combinaisons possibles"` | Version complète (quiz + algorithme + sachets + prénom + téléconsult) | darwin-nutrition |
| `perimetre_produit.exclusions` | `[]` | `["Pas d'achat one-shot possible"]` | Structural |
| `ux_page_produit.screenshots_files` | préfixe `cuure_*` | nommage local | refacto |
| `evaluation.strengths` | 5 items | 8 items (ajouté : engagement psychologique, téléconsult, livraison offerte, Trustpilot) | Vérifs live |
| `evaluation.weaknesses` | 4 items | 7 items (ajouté : résiliation 2 temps, fenêtre 1h, prix variable, stack custom) | support.cuure.com + blogs |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Seuil livraison exact** : la homepage dit "39€ en UE", les sources secondaires françaises disent "20€". Possible différence France vs UE. À confirmer pour le marché FR — vraisemblablement 20€.
- **Programme de fidélité Cuure** : mention homepage *"Programme de Fidélité avantageux dès la 2ème commande"* mais pas de détails trouvés. À creuser si on veut comparer aux autres marques du panel.
- **Téléconsultations** : incluses dans l'abo ou payantes ? Pas confirmé. Impact mineur sur la reco Impulse.
- **Screenshot page quiz** : on a `quiz.png` dans le dossier mais il daterait de la collecte initiale. À re-capturer via Playwright si on veut une version 2026 pour le deck.
- **Notes /5** — propositions sparring : UX **4.5** (parcours ultra fluide, quiz engageant, app mobile, bemol sur la résiliation) / Offre **3.5** (modèle unique mais pricing variable et friction résiliation baissent la note) / Pertinence **2.5** (modèle trop éloigné d'Impulse qui est un e-commerce catalogue classique, Cuure est un service personnalisé) / Global **3.5**. À trancher en fin de revue.

## Insight deck
Cuure est le **contre-modèle radical** à amener dans le deck pour illustrer les limites du "tout abonnement". 3 slides potentielles :
1. *"Le modèle poussé à l'extrême : Cuure sans one-shot"* — forces et faiblesses
2. *"Anti-pattern documenté : la résiliation en 2 temps"* — à ne pas reproduire chez Impulse
3. *"Ce qu'on peut reprendre de Cuure : le quiz santé comme outil d'acquisition"* — sans forcément adopter le modèle complet
