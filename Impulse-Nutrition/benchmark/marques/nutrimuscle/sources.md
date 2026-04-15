# Nutrimuscle — sources consultées

_Format : `- [YYYY-MM-DD] URL — phrase extraite entre guillemets`_

## FAQ / pages officielles

- [2026-04-15] https://www.nutrimuscle.com/pages/abonnement (WebFetch direct)
  > "Réduction -15% sur vos produits en abonnement."
  > "Avec l'abonnement, la livraison à domicile est offerte." (pas de seuil mentionné — confirmé gratuit sans condition de montant)
  > Page dédiée avec 3 pictos : -15%, livraison gratuite, sans engagement. Catalogue des produits éligibles (250+ formats). Lien vers espace abonné.

- [2026-04-15] https://eu.nutrimuscle.com/blogs/news/loffre-abonnement-nutrimuscle-votre-nouvel-essentiel (WebFetch direct)
  > "a 15% discount on your selection"
  > "You now have the choice between 250 available formats!"
  > Article blog confirmant **-15% flat dès la 1ère livraison**, sans période d'attente.

- [2026-04-15] https://eu.nutrimuscle.com/pages/nos-offres
  > Programme Nm Club (fidélité) : points collectés sur achats → produits gratuits. Parrainage : -10% pour le filleul, 10% en carte cadeau pour le parrain (non cumulable avec autres offres).

- [2026-04-15] https://www.nutrimuscle.com/pages/paiements-reductions
  > Conditions générales des remises et codes promo.

## Contradictions détectées

- **"5% 1ère livraison puis 15%"** : cette mécanique progressive était listée dans `master_data.json` et confirmée par 1 source externe SEO (savoo.fr, couponasion). Or les 2 sources officielles Nutrimuscle (/pages/abonnement + /blogs/news/loffre-abonnement) parlent exclusivement de **-15% flat dès la 1ère livraison**. Conclusion : la mécanique progressive semble **obsolète**, Nutrimuscle a vraisemblablement simplifié son modèle. Corrigé dans `data.json`. À re-vérifier par achat test si crucial pour la reco.

- **Native Whey exclue ?** : une source secondaire (webreader IA sur un article) l'a listée parmi les exclusions, mais aucune source officielle ne le confirme explicitement. Flag "à confirmer par navigation live".

## Verbatims / avis

- [Trustpilot] https://fr.trustpilot.com/review/nutrimuscle.com — **4.05 / 5 sur 28 000 avis** (volume 6× supérieur à Nutri&Co). Points forts : catalogue très large, bon rapport qualité/prix, livraison rapide. Points faibles : ruptures de stock fréquentes, SAV parfois lent, emballage perfectible.
- Verbatims spécifiques abo (dans `avis.verbatims_abo`) :
  - *"Abonnement pratique pour les produits récurrents"* (positif)
  - *"Parfois rupture de stock = livraison décalée"* (négatif — signal UX ops)
