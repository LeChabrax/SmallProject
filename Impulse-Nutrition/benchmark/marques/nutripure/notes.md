# Nutripure — notes de revue

## Statut audit
- Audit status : `verified_live` (sources officielles croisées 2026-04-15 — homepage en 403 anti-bot, contournée via article programme fidélité + packs + parrainage + FAQ Zendesk)

## Rôle dans le panel
**Contrôle / contre-exemple**. Nutripure est la SEULE marque du périmètre qui n'a **pas** de système d'abonnement récurrent. Cela en fait un cas d'école précieux pour la reco Impulse : ça permet de valider la thèse "l'abo est nécessaire en nutrition premium FR" ou, au contraire, de la nuancer.

## Vérifs live (2026-04-15)

### Absence d'abonnement — confirmée
Aucune source officielle ni secondaire n'évoque un mécanisme d'abonnement récurrent chez Nutripure. La homepage directe est inaccessible (403 anti-bot), mais l'absence est confirmée **indirectement** par :
- Les articles officiels dédiés aux "programmes" de Nutripure parlent exclusivement de (1) fidélité, (2) parrainage, (3) packs permanents, (4) codes promo ponctuels. **Aucun article "abonnement".**
- Les sites de codes promo et les blogs affiliés ne référencent aucune offre d'abo Nutripure (alors qu'ils le font pour les 7 autres marques du panel).
- La tech stack (**PrestaShop**, pas Shopify) rend l'intégration d'un module abo coûteuse et non native.

### Modèle de récurrence alternatif — 3 leviers structurés

Nutripure n'a pas d'abo, mais ils ont construit un **triangle de fidélisation** qui approche l'effet d'un abo sans en porter les contraintes :

**Levier 1 : Packs multi-mois permanents**
- Chaque pack bénéficie de **-10% minimum** (jusqu'à **-25%** sur certains packs), **toute l'année**, sans code à entrer
- Format 6 mois ≈ **130€** vs 25€/mois × 6 = 150€ → **économie ~13%**
- L'économie client est **équivalente à un abo −15%** (comparable à Nutri&Co et Nutrimuscle), mais sans friction contractuelle
- Effet de lock-in implicite : un client qui achète 6 mois d'avance ne va pas racheter ailleurs pendant cette période

**Levier 2 : Programme fidélité "cashback produit"**
- 10% de chaque commande crédité sur un compte récompenses (valable 12 mois)
- Les points **ne sont pas déductibles du panier** — uniquement convertibles en **produits offerts**
- Pattern intéressant : cela force le client à **revenir** pour dépenser ses points (effet rétention), et il repart souvent avec une commande d'achat + un produit gratuit (effet panier élargi)
- Adhésion automatique gratuite à la création de compte

**Levier 3 : Parrainage cumulable**
- 10% des commandes du filleul ajoutées au compte fidélité du parrain
- Nombre de filleuls illimité
- Un client engagé peut théoriquement financer tout son prochain achat via ses filleuls

### Pourquoi ça marche pour Nutripure (et ce que ça dit à Impulse)

**Hypothèses sur le choix stratégique** :
1. **Positionnement ultra-premium** : le ticket moyen one-shot dépasse déjà 55€ (vs 30-45€ chez les concurrents) → le client franchit naturellement les seuils de livraison gratuite (49,90€ relais, 99€ domicile) sans avoir besoin d'un "trick" abo.
2. **Fidélisation par la qualité** : Trustpilot 4.75 / 2 000 (meilleur % du panel) signale un vrai fit produit/client. Nutripure se repose sur la qualité pour faire revenir le client, pas sur le lock-in.
3. **PrestaShop** : vraie friction technique pour intégrer un module abo moderne. Pas impossible, mais coûteux et risqué.
4. **Simplicité commerciale** : zéro mécanisme abo = zéro support client lié à "comment j'annule", zéro churn contractuel, zéro complexité opérationnelle (rupture de stock sur un abo est bien plus critique que sur un one-shot).

**Implications pour la reco Impulse** :
- Si Impulse lance un abo, il faut que **l'économie client soit clairement supérieure à -13%** (la valeur du pack 6 mois Nutripure). Sinon, on ne crée pas de vraie différenciation.
- Alternative stratégique à considérer : au lieu d'un abo classique, Impulse pourrait lancer **des packs multi-mois en permanent −10/−15%** qui captent l'économie récurrente sans les coûts techniques d'un vrai abo. C'est le modèle Nutripure.
- **Question critique** : Impulse a-t-il la même puissance qualité produit que Nutripure pour se reposer sur la qualité + formats larges ? Si oui, l'abo n'est **pas** une nécessité technique, c'est un choix stratégique parmi d'autres.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_note` | `"Aucun — achat one-shot uniquement"` | Note détaillée triangle de fidélisation (packs + fidélité + parrainage) | /info/10-programme-de-fidelite + /30-packs |
| `modele_commercial.livraison_abo.note` | `null` | `"N/A — pas d'abonnement (...)"` avec seuils standards et effet des formats longs | /info/29-code-promo-nutripure |
| `ux_page_produit.screenshots_files` | `["nutripure_homepage.png", "nutripure_product.png"]` | `["homepage.png", "product.png"]` (cohérence slug local) | refacto |
| `evaluation.strengths` | 3 items | 7 items (ajouté : économie 13% pack 6 mois, fidélité 10%, parrainage, Trustpilot 4.75, zéro friction) | Vérifs live |
| `evaluation.weaknesses` | 2 items | 5 items (ajouté : récompenses non cashable, pas de MRR, volume Trustpilot plus faible) | Vérifs live |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Confirmation directe homepage** : la homepage nutripure.fr renvoie un 403 anti-bot sur WebFetch. Si on veut un screenshot propre de la homepage en 2026 pour le deck, il faudra passer par Playwright (user-agent différent) ou accepter le screenshot du master_data initial (qui date de début avril mais reste pertinent).
- **Programme fidélité — seuil d'usage minimum** : pour convertir les 10% en produit gratuit, y a-t-il un seuil minimum de points ? Pas trouvé dans les sources. Bas priorité.
- **Volume business** : Nutripure a-t-il une meilleure MRR que les concurrents avec abo ? Impossible à savoir sans data business, mais c'est la vraie question stratégique que le deck devrait poser.
- **Notes /5** — propositions sparring : UX **N/A** (pas pertinent sans abo) / Offre **3.0** (pas d'abo = offre commerciale incomplète vs brief mission) / Pertinence **5.0** (positionnement ultra-premium = le plus proche d'Impulse santé/sport) / **rôle de contrôle** plutôt qu'une note "abo". À trancher en fin de revue.
