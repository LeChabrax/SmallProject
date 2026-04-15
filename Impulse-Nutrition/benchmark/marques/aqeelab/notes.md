# Aqeelab Nutrition — notes de revue

## Statut audit
- Audit status : `verified_live` (page abo officielle en WebFetch direct + programme fidélité + codes promo, 2026-04-15)

## Rôle dans le panel
**Pure player FR premium agressif** — remise la plus haute (-20%), catalogue petit (23 SKUs) mais 100% éligible, positionnement premium pur avec des prix one-shot élevés. Intéressant pour le deck comme **miroir ambitieux d'Impulse** (même tech Shopify, même positionnement FR premium).

## Vérifs live (2026-04-15)

### Remise -20% flat à vie — confirmée
Contrairement à Nutrimuscle où le "5%→15% progressif" était obsolète, ici le master_data disait juste et Aqeelab confirme officiellement :
- Page abo /collections/abonnement affiche **"20% A VIE"** et **"-20% TOUS LES MOIS"**
- Calcul vérifié sur 3 SKUs (Magnésium, Ashwagandha, Multivitamines) : prix abonné = exactement -20% du prix one-shot
- C'est **la remise la plus agressive du panel** : Aqeelab est à +5 points vs Nutri&Co/Nutrimuscle (-15%) et +10 points vs Novoma (-10%)

### Engagement 2 mois minimum — correction majeure
**Nouvelle découverte importante.** Le master_data disait `engagement_min: "Aucun"`, ce qui était faux. La page abo officielle précise textuellement : *"Engagement minimum : 2 mois requis pour débuter un abonnement."*

**Implication** :
- Un client qui souscrit à l'abo pour bénéficier du -20% sur sa première commande doit **impérativement rester au moins 2 mois** avant de pouvoir résilier
- C'est une friction d'entrée assumée par Aqeelab : ils protègent leur marge en forçant au moins 2 cycles de facturation
- **Point vigilance Loi Chatel** : la loi française exige que la résiliation soit aussi facile que la souscription. Un engagement minimum de 2 mois peut être légal si c'est explicitement communiqué au moment de la souscription (ce qui semble être le cas ici). Mais à vérifier avec un avocat si Impulse veut reproduire ce modèle.
- **Contraste avec les autres marques du panel** : Nutri&Co, Nutrimuscle, Novoma, Decathlon sont tous "sans engagement". Aqeelab est **le seul** à avoir un engagement explicite.

**À flaguer dans le deck** : est-ce que la friction d'engagement de 2 mois est compensée par la remise -20% (vs -15% flat ailleurs) ? Pour le client, la question est : *"est-ce que 2 × -20% = 2 cycles minimum d'économie justifie la perte de flexibilité ?"*.

### Stacking codes × abo — non cumulable
Citation officielle (/pages/des-conseils-des-infos-et-des-reductions) : règle "un seul code promo par commande" + *"Les codes promotionnels, codes de parrainage et programmes de fidélité ne sont pas cumulables entre eux."*

Pattern "zéro stacking" — équivalent à Nutri&Co. Le client doit choisir entre code welcome et abo à la souscription.

### Livraison abo — ambiguïté non résolue
Une source secondaire mentionne que les abonnés bénéficient de "reduced delivery shipping", mais la page /collections/abonnement officielle n'explicite **aucune** condition de livraison spécifique. Les seuils standards sont : relais gratuit dès 69€, domicile gratuit dès 100€.

Hypothèse : comme un abo Aqeelab moyen est autour de 30-40€/mois (prix abonné après -20%), la plupart des commandes sont **en-dessous du seuil de 69€**, donc la livraison est payante pour l'abonné sauf si l'abo est gros (2+ produits). Impact potentiel sur la vraie économie client.

**À flaguer dans le deck** : la remise -20% affichée d'Aqeelab est brute ; si on ajoute 3,95-6,95€ de frais de livraison, la remise réelle baisse sensiblement pour les petits paniers. Exemple : Magnésium 19,95€ → 15,96€ (économie 3,99€) + 4€ frais port = **économie réelle 0€** pour un client qui n'a que ce produit en abo. C'est un piège à surveiller.

### Programme fidélité RePoints / Club AqeeLab — opaque
Existence confirmée (page dédiée listée dans la navigation) mais les conditions ne sont pas accessibles via WebFetch. C'est un **signal de communication faible** : si le programme existait vraiment, il serait mieux mis en avant. À creuser si le deck veut comparer les programmes fidélité du panel.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_note` | `"Subscribe & save -20% sur chaque produit"` (simple) | Version détaillée avec citation page officielle + comparatif panel + non-cumul codes | /collections/abonnement |
| `modele_commercial.flexibility.cancel_anytime` | `true` | `"après 2 mois minimum"` | /collections/abonnement |
| `modele_commercial.engagement_min` | `"Aucun"` | **`"2 mois minimum requis"`** + note Loi Chatel | /collections/abonnement |
| `modele_commercial.livraison_abo.note` | `null` | Note détaillée : ambiguïté non résolue + seuils standards + piège pour petits paniers | /collections/abonnement + /homepage |
| `ux_page_produit.dedicated_page` | `false` | `true` (page /collections/abonnement existe) | Vérifs live |
| `ux_page_produit.dedicated_page_url` | — | ajouté | idem |
| `ux_page_produit.navigation_mention` | `false` | `true` (mentionné dans la nav principale "-20% chaque mois") | homepage |
| `ux_page_produit.screenshots_files` | préfixe `aqeelab_*` | nommage local | refacto |
| `evaluation.strengths` | 5 items | 9 items (ajouté : -20% à vie, page dédiée, expédition Bordeaux 24-48h, RePoints, Trustpilot 4.9, prix premium = marge soutenable) | Vérifs live |
| `evaluation.weaknesses` | 3 items | 5 items (ajouté : engagement 2 mois, non-cumul codes, livraison non-explicité, RePoints opaque) | Vérifs live |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Livraison abo — conditions réelles** : le WebFetch direct n'a pas tranché. Pour être 100% propre, il faudrait simuler un parcours abonné (Playwright + ajout au panier + arrivée au checkout). Bas priorité sauf si c'est critique pour le deck.
- **Programme RePoints — détails** : pas accessibles publiquement. Si on veut un vrai comparatif fidélité dans le deck, il faudra contacter le SAV Aqeelab ou créer un compte test.
- **Email pré-expédition** : Aqeelab a-t-il un mécanisme anti-churn comme Nutri&Co ? Non documenté, à vérifier.
- **Conformité Loi Chatel** : l'engagement de 2 mois est-il réellement légal en France ? À valider avec un juriste si Impulse veut reproduire ce mécanisme.
- **Notes /5** — propositions sparring : UX **4.5** (toggle clair, montant en € persuasif, mention home + nav, page dédiée) / Offre **4.5** (-20% le plus haut du panel, mais pénalisé par l'engagement 2 mois et l'ambiguïté livraison) / Pertinence **4.5** (même tech Shopify, même positionnement FR premium, taille catalogue comparable — c'est le miroir le plus proche pour Impulse) / Global **4.5**. À trancher en fin de revue.

## Insight deck
Aqeelab est le **modèle le plus inspirant pour la reco Impulse** (positionnement proche), mais **avec 2 écueils à ne pas reproduire** :

**À copier** :
1. **Wording "montant économisé en € affiché sur la fiche"** — le plus persuasif du panel, transforme l'abstraction -X% en bénéfice tangible
2. **CTA "S'abonner & économiser"** — plus explicite que le simple "S'abonner"
3. **Catalogue 100% abonnable** — simplicité de communication (pas d'exceptions à expliquer)
4. **Positionnement premium avec marge** — le -20% est soutenable parce que les prix one-shot sont élevés

**À éviter** :
1. **Engagement minimum 2 mois** — friction d'entrée qui peut tuer la conversion. Impulse doit rester sans engagement.
2. **Livraison abo non explicitée** — création d'ambiguïté qui peut décevoir le client. Impulse doit être transparent sur les conditions exactes.
3. **Programme fidélité opaque** — si Impulse lance un programme, il doit être parfaitement communiqué dès la page d'accueil.
