# MyProtein (FR) — notes de revue

## Statut audit
- Audit status : `verified_live` (fr.myprotein.com + /c/subscribe/ en WebFetch direct + recherches codes promo + Trustpilot, 2026-04-15). **Pass FR uniquement** — pas de vérif live sur la version .com internationale (hors périmètre décidé avec l'utilisateur).

## Rôle dans le panel
**Leader mondial volume** — le plus gros catalogue (1000+ références), le plus gros volume Trustpilot (31 000 avis), la remise faciale la plus haute (jusqu'à -45%), le plus bas prix plancher. Mais aussi **le pire Trustpilot** (3,1/5) et un positionnement mass-market très éloigné d'Impulse. Rôle dans le deck : **cas "subscribe & save mature à l'échelle"** vs les autres marques qui sont plus jeunes ou plus boutique.

## Vérifs live (2026-04-15)

### Remise variable — pas flat (nuance importante)
Le master_data disait "30% (jusqu'à 45% en promo)" — c'est globalement confirmé mais avec une nuance :
- Le programme s'appelle officiellement **"Subscribe and Gain"** (nom interne)
- Côté user : affiché comme "S'abonner" en FR
- Page officielle : **"Jusqu'à 45% de réduction sans contrat"**
- Les sources secondaires mentionnent "45% à 50%" dans les meilleurs cas
- **Remise variable** selon le produit et les promos en cours, pas flat comme les marques FR premium

**Point critique** : les prix de base MyProtein sont eux-mêmes instables (promos permanentes sitewide). Donc la remise -30% abo affichée s'applique sur un prix-barré déjà volatil → **la vraie économie perçue par le client est difficile à lire**. C'est confirmé par le verbatim *"Subscribe & save pratique mais attention aux prix qui changent"*.

**Implication Impulse** : ne pas reproduire ce pattern. Un prix de base stable + une remise abo claire = plus de confiance client qu'une remise élevée sur un prix volatil.

### Livraison abo offerte — confirmée ✅
Citation officielle : *"Livraison gratuite sur toutes les commandes récurrentes"*. Pas de seuil mentionné pour les abonnés. En one-shot : seuil gratuit à 55€, sinon 3,99€ relais ou 4,99€ domicile.

C'est le **4e cas de livraison flat offerte** du panel (avec Nutri&Co, Nutrimuscle, Cuure). Novoma et Decathlon sont en stepped (partiellement subventionné), Aqeelab est ambigu.

### Engagement confirmé à "Aucun" ✅
Citation officielle : *"Annulez à tout moment - pas d'engagement"*. Pause possible à tout moment avec reprise quand le client est prêt. Bonne nouvelle vs Aqeelab qui a un engagement 2 mois.

### Stacking codes × abo — partiel
Les codes promo individuels **ne sont pas cumulables entre eux**, mais peuvent être combinés avec les **promos sitewide** (soldes, bundles, ventes flash). L'effet sur l'abo est indirect : comme les prix de base baissent en promo, l'abo appliqué sur le prix réduit donne une remise effective plus haute.

Exemple théorique : Impact Whey 1kg 30,49€ → promo -20% sitewide → 24,39€ → abo -30% → 17,07€ (vs 21,34€ hors promo). Donc l'**effet cumulé** peut atteindre -44% en promo.

### Page dédiée /c/subscribe/ ✅
Existe et référencée dans la navigation + bannière homepage avec CTA "Souscrire". Plus visible que chez Nutri&Co ou Aqeelab.

### Programme de parrainage bonus
Citation search : *"Les amis gagneront une remise exceptionnelle de 25% et des livraisons gratuites pendant 3 mois"*. C'est un mécanisme très incitatif pour les filleuls, mais à vérifier si c'est spécifiquement pour l'abonnement ou pour une commande one-shot.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_pct` | `"30% (jusqu'à 45% en promo)"` (string) | Même ordre de grandeur + précision "jusqu'à 45% voire 50%" | /c/subscribe/ + search |
| `modele_commercial.remise_note` | `"Subscribe & Save, remise très agressive"` (simple) | Version détaillée avec programme interne "Subscribe and Gain", variabilité, instabilité prix de base | /c/subscribe/ + homepage |
| `modele_commercial.engagement_min` | `"Aucun"` | Confirmé avec citation officielle | homepage |
| `modele_commercial.livraison_abo.offerte` | `null` | `true` (citation officielle "Livraison gratuite sur toutes les commandes récurrentes") | homepage |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `0` (pas de seuil) | homepage |
| `ux_page_produit.wording_cta` | `"Subscribe & Save"` | `"S'abonner (FR)"` (l'anglais n'est pas utilisé sur la version FR) | homepage |
| `ux_page_produit.dedicated_page` | `false` | `true` (page /c/subscribe/ existe + bannière homepage) | WebFetch |
| `ux_page_produit.dedicated_page_url` | — | ajouté | idem |
| `ux_page_produit.screenshots_files` | préfixe `myprotein_*` | nommage local | refacto |
| `evaluation.strengths` | 5 items | 9 items (ajouté : livraison gratuite sans seuil, page dédiée, engagement zéro, prix plancher bas, parrainage) | Vérifs live |
| `evaluation.weaknesses` | 4 items | 8 items (ajouté : instabilité prix référence, Trustpilot 3.1, SAV critiqué, UK warehouse, verbatims négatifs) | Vérifs live |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Remise exacte à l'instant T** : le -30% "standard" peut descendre à -45% ou monter temporairement. Impossible de fixer une valeur unique — c'est la nature du modèle MyProtein. Flaguer comme "variable".
- **Email pré-expédition** : non documenté. Verbatim client négatif suggère absence. À vérifier via parcours abonné.
- **Programme fidélité MyProtein** : pas documenté dans les sources secondaires. Existe-t-il ? À creuser si crucial pour le deck.
- **Vraie structure de la remise** : -30% "standard" est-il le pic ou le plancher ? Les promos permanentes rendent la lecture difficile. Pour une slide précise, il faudrait faire un test panier sur 3-5 SKUs et mesurer l'écart prix abo vs prix promo one-shot à l'instant T.
- **Notes /5** — propositions sparring : UX **3.5** (UX confuse avec prix qui changent, promos empilées, même si toggle clair et page dédiée) / Offre **4.0** (remise la plus agressive du panel mais illisible, livraison offerte, zéro engagement, 5 fréquences — offre théoriquement massue mais la confusion baisse la note) / Pertinence **1.5** (positionnement mass-market volume international **très éloigné** d'Impulse qui est premium FR — c'est un contre-modèle plus qu'une inspiration) / Global **3.0**. À trancher en fin de revue.

## Insight deck
MyProtein est **le contre-modèle "volume mass-market"** à amener pour illustrer ce qui arrive à l'échelle internationale quand la remise devient l'argument central.

**À copier (cadre général)** :
1. **Livraison gratuite sans seuil sur l'abo** — c'est le pattern qui marche le mieux pour convertir
2. **Engagement zéro** — flexibilité totale rassure le client
3. **Page dédiée /c/subscribe/ + bannière homepage** — visibilité maximale
4. **5 fréquences** — flexibilité large (1 à 5 mois)

**À éviter absolument** :
1. **Prix de base instables** — promos permanentes qui rendent la remise abo illisible. Impulse doit garder des prix one-shot stables pour que la remise abo soit claire.
2. **Rôle secondaire du SAV** — Trustpilot 3,1/5 sur 31 000 avis = risque reputational majeur. L'abo amplifie l'importance du SAV (un problème répétitif tue la confiance).
3. **Mass-market au détriment de la qualité perçue** — positionnement opposé à Impulse. Ne pas confondre "grosse remise" avec "grosse valeur".
4. **Remise affichée "jusqu'à X%"** — création d'attentes trompeuses. Impulse doit communiquer une remise flat claire, pas un "jusqu'à".

**Le verdict pour la reco Impulse** : MyProtein est le meilleur exemple de **ce qu'il ne faut pas devenir** — leader volume avec remise agressive mais Trustpilot catastrophique. Impulse doit jouer sur la **confiance premium** (comme Nutri&Co, Novoma, Aqeelab) plutôt que sur la **remise brute** (MyProtein, Decathlon).
