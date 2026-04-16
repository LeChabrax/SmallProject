# Nutri&Co — notes de revue

## Statut audit
- Audit status : `verified_live` (FAQ officielle consultée le 2026-04-15)

## Vérifs live (2026-04-15)

### Livraison abonnement — confirmée offerte sans seuil
La FAQ Zendesk Nutri&Co est explicite : la livraison à domicile est incluse dans l'abonnement, sans panier minimum. C'est un avantage fort vs les seuils standards du site (relais gratuit dès 69€, domicile dès 89€) — l'abo débloque la gratuité même sur un panier de 15€.

### Fréquences — correction factuelle
Le master_data initial listait `frequencies_available: ["1 mois", "2 mois", "3 mois"]`. La FAQ officielle ne mentionne **que** mensuel et trimestriel. Citation : *"Vous pouvez choisir la fréquence de livraison du ou des produits de votre choix : mensuelle ou trimestrielle."* Le "2 mois" a été retiré.

### Remise confirmée
−15% fixe appliqué à tous les produits éligibles. Pas de tranche par volume, pas de palier par durée d'engagement.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.frequencies` | `["1 mois", "2 mois", "3 mois"]` | `["1 mois", "3 mois"]` | FAQ Zendesk |
| `modele_commercial.livraison_abo.offerte` | `null` | `true` | FAQ Zendesk |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `0` | FAQ Zendesk |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Vérifs live (pass 2, 2026-04-15)

### Remise −15% — FLAT confirmé
Contradiction détectée entre sources : FAQ Zendesk dit "-15%", sources SEO secondaires (santedefaire, quelcomplementalimentaire) disent "10% mensuel / 15% trimestriel". Tranchée via WebFetch direct sur `/fr/pages/page-abonnement` : l'exemple Collagène Marin affiche **27,81€/unité identique** pour mensuel et trimestriel. C'est donc bien **−15% flat** quelle que soit la fréquence. Les sources secondaires erronées ont été ignorées.

### Stacking codes × abo — NON cumulable
Nutri&Co est explicite (Zendesk "Codes promotions NUTRI&CO") : *"Les codes promotions ne sont pas cumulables avec les abonnements, les packs, et les offres en cours."*
→ Implication forte pour la reco Impulse : le client qui arrive avec un code welcome (-15% first order) doit **choisir** entre activer son code OU souscrire à l'abo (aussi -15%). C'est une friction de conversion : on perd l'effet "découverte -15% puis rétention par l'abo".
→ À discuter dans la section Recommandation Impulse : est-ce qu'on autorise le stacking chez Impulse pour réduire cette friction ?

### Programme fidélité — levier rétention fort
- 1€ dépensé = 1 point (hors frais de port, après codes promo)
- Points cumulés sur achats abo **et** one-shot
- Paliers de récompense à 400-500 points → produits gratuits (Collagène Marin, Spiruline)
- Combiné avec l'abo = double levier : remise immédiate (-15%) + récompense long terme (points → produit offert)
→ C'est une force du modèle Nutri&Co qui mérite une slide dédiée dans le deck. Impulse n'a pas de programme fidélité aujourd'hui, c'est un gap à évoquer dans les prochaines étapes.

### Email de pré-expédition (pitch + fenêtre modif 48h)
Avant chaque expédition d'abo, Nutri&Co envoie un email au client avec un délai de 48h pour modifier la commande (produit, fréquence, skip). C'est un **anti-pattern churn** classique très bien exécuté.
→ À ajouter aux forces UX du modèle.

### Produits exclus de l'abo
**Toujours indéterminé.** Les recherches indiquent que les packs/coffrets ne peuvent pas recevoir de code promo, mais ne disent pas explicitement s'ils sont ou non abonnables. Conjecture : le modèle "1 produit = 1 abonnement" de Nutri&Co implique probablement que les packs ne sont **pas** abonnables (un pack = composition figée, pas récurrente). À confirmer par navigation live sur une fiche pack — bas priorité car pas bloquant pour la reco.

## Décisions / corrections (cumulatif)

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.frequencies` | `["1 mois", "2 mois", "3 mois"]` | `["1 mois", "3 mois"]` | FAQ Zendesk |
| `modele_commercial.livraison_abo.offerte` | `null` | `true` | FAQ Zendesk |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `0` | FAQ Zendesk |
| `modele_commercial.remise_note` | `"Subscribe & save sur chaque produit"` | `"−15% flat, identique mensuel et trimestriel (vérifié sur page abonnement)"` | WebFetch /page-abonnement |
| `evaluation.strengths` (ajouts) | — | `"Programme fidélité couplé (1€=1pt, rewards 400-500 pts)"`, `"Email pré-expédition avec fenêtre modif 48h"` | Zendesk programme fidélité + page abo |
| `evaluation.weaknesses` (ajout) | — | `"Codes welcome non cumulables avec l'abo (friction conversion)"` | Zendesk codes promos |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Notes /5** (UX, offre commerciale, pertinence, globale) — à trancher en fin de revue des 8 marques pour calibrage homogène. Propositions initiales en sparring : UX 3.5 / Offre 3.5 / Pertinence 4.5 / Global 3.8. **À reconsidérer** avec les nouveaux findings : le programme fidélité + email pré-exp + −15% flat + livraison offerte renforcent l'offre commerciale → possible 4/5. La non-cumulabilité baisse légèrement. Net : offre probablement 4/5 finalement. Fin de revue tranchera.
- **Produits exclus de l'abo** — conjecture "packs non abonnables" à confirmer par navigation live sur fiche pack. Bas priorité.
- **Verbatims spécifiques abo** — `avis.verbatims_abo` toujours vide. À creuser si on veut une slide "voice of customer" sur l'abo. Bas priorité.
