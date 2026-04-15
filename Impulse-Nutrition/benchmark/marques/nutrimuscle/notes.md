# Nutrimuscle — notes de revue

## Statut audit
- Audit status : `verified_live` (sources officielles consultées 2026-04-15 : /pages/abonnement + article blog)

## Vérifs live (2026-04-15)

### Remise −15% flat — correction majeure (master_data obsolète)
Le master_data initial listait `remise_pct: "5% 1ère livraison, 15% à partir de la 2ème"` et `remise_note: "Abonnement progressif (5% → 15%)"`. Cette mécanique est également confirmée par 1 source externe SEO (savoo.fr, couponasion).

**Mais les 2 sources officielles Nutrimuscle parlent exclusivement de −15% flat dès la 1ère livraison** :
- Page `/pages/abonnement` : *"Réduction −15% sur vos produits en abonnement."*
- Blog `/blogs/news/loffre-abonnement-nutrimuscle-votre-nouvel-essentiel` : *"a 15% discount on your selection"*

**Conclusion** : la mécanique progressive est **obsolète**. Nutrimuscle a vraisemblablement simplifié son modèle commercial (ce qui est cohérent avec la weakness "remise progressive peut être confuse" qui était dans l'ancien data). Corrigé dans `data.json` → `remise_pct: 15` flat.

### Livraison abo — offerte sans seuil
Citation page officielle : *"Avec l'abonnement, la livraison à domicile est offerte."* Pas de seuil. En one-shot, la livraison domicile n'est gratuite qu'à partir de 100€ et relais à partir de 60€. L'abo débloque la gratuité même sur un panier de 17€ (créatine seule). **Argument massue**, équivalent à Nutri&Co.

### Produits exclus — 4 catégories probables, Native Whey à confirmer
Aucune source officielle ne liste explicitement les exclusions de l'abo, mais plusieurs indices cohérents :
- **Packs** (Pack Starter, Pack Muscu Sèche, Pack Prise de masse, packs collagène/vitamines) : le modèle "1 produit = 1 abonnement" les exclut structurellement (composition figée). Pattern identique à Nutri&Co.
- **Gros formats (4 kg et plus, 800 gélules et plus)** : probablement exclus car ils couvrent déjà 2-3 mois de consommation, l'abo mensuel n'a pas de sens.
- **Textile et accessoires** (shakers, t-shirts) : exclus car non consommables, pas de logique de récurrence.
- **Native Whey** : mentionnée comme exclue dans une source secondaire, mais **non confirmé** par source officielle. Le master_data listait pourtant "Whey Native Biologique" dans les `produits_sample` en mode abonnable. Contradiction → à trancher par navigation live sur la fiche produit.

### Stacking codes × abo — non trivial
Pattern hétérogène :
- Certains codes influenceurs sont **explicitement cumulables** avec l'abo (NME_NABFIT, NMA_CLARABBLT, NMA_NICORI → −5% ou −10% en plus des −15% abo) — c'est une stratégie Nutrimuscle pour booster la conversion via ses ambassadeurs.
- Les codes promo classiques (welcome, saisonniers) ne sont **pas cumulables** avec l'abo en général.
- Le programme de parrainage est non cumulable avec les autres offres.

**Implication pour Impulse** : Nutrimuscle assume un stacking **partiel et sélectif** — cumul autorisé quand c'est stratégique (codes influenceurs = acquisition), bloqué sur les codes génériques. Stratégie intéressante à considérer dans la reco Impulse.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_pct` | `"5% 1ère livraison, 15% à partir de la 2ème"` (string) | `15` (int) | /pages/abonnement + blog |
| `modele_commercial.remise_note` | `"Abonnement progressif (5% → 15%)"` | `"-15% flat dès la 1ère livraison (…)"` | idem |
| `modele_commercial.livraison_abo.offerte` | `null` | `true` | /pages/abonnement |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `0` | /pages/abonnement |
| `perimetre_produit.scope` | `"Quasi tous les produits (250+ références)"` | `"Sélection de produits (250+ formats éligibles). Modèle '1 produit = 1 abonnement'."` | /pages/abonnement |
| `perimetre_produit.exclusions` | `[]` | 4 catégories listées (packs, gros formats, textile, Native Whey à confirmer) | Recherches + analogie Nutri&Co |
| `ux_page_produit.dedicated_page_url` | — | `https://www.nutrimuscle.com/pages/abonnement` (ajouté) | Confirmed live |
| `evaluation.strengths` | 6 items dont "Remise progressive" | 8 items (ajouté : -15% flat simple, Nm Club fidélité, mention home+nav+emails) | Vérifs live |
| `evaluation.weaknesses` | 2 items (dont "Remise progressive confuse" obsolète) | 3 items (ruptures stock, email pré-exp non confirmé, stacking non trivial) | Vérifs live |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Native Whey abonnable ou pas ?** Contradiction entre master_data (listée en produits_sample) et source secondaire (listée comme exclue). À trancher par navigation live sur la fiche Whey Native Biologique. Priorité moyenne.
- **Email de pré-expédition (anti-churn)** : Nutrimuscle a-t-il un email de pré-exp avec fenêtre de modification comme Nutri&Co ? Non confirmé, faiblesse potentielle. À checker via parcours abonné.
- **Gestion des ruptures de stock sur l'abo** : les verbatims signalent "rupture → livraison décalée". Comment Nutrimuscle gère-t-il ? Skip automatique ? Email notification ? Substitution ? À creuser pour la reco Impulse car c'est un signal UX/ops crucial.
- **Notes /5** (UX, offre, pertinence, globale) — à trancher en fin de revue des 8 marques pour calibrage homogène. Propositions en sparring : UX 4.5 (meilleur que Nutri&Co car page dédiée + home mention + nav mention + 6 fréquences) / Offre 4.5 (-15% flat + livraison offerte + Nm Club + grand catalogue) / Pertinence 3.5 (positionnement muscu/perf, moins proche Impulse qui est santé/sport mix) / Global 4.2.
