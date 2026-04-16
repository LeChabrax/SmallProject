# Decathlon (Abonnement Nutrition) — notes de revue

## Statut audit
- Audit status : `verified_live` (abonnement.decathlon.fr en WebFetch direct + Decat'Club global + landing page decathlon.fr/lp/c/abonnement-decathlon + recherche catalogue packs, 2026-04-15)

## Rôle dans le panel
**Seul cas "grande distribution" du panel.** Toutes les autres marques sont spécialisées nutrition. Decathlon est un géant omnicanal (1700+ magasins, e-commerce massif, plusieurs marques propres) qui a ajouté un sous-domaine abo pour capter la récurrence sur sa catégorie nutrition sportive. Ça en fait un **cas d'école "minimum viable product"** : l'offre existe, fonctionne, mais n'a pas été optimisée comme chez les spécialistes.

## Vérifs live (2026-04-15)

### Sous-domaine `abonnement.decathlon.fr` persiste en 2026 ✅
Confirmé opérationnel. Le sous-site n'a PAS été mergé dans decathlon.fr principal. Il y a un pont : une landing page `decathlon.fr/lp/c/abonnement-decathlon` sur le site principal qui renvoie vers le sous-domaine. Pattern architecture "microservice isolé" clairement assumé.

### Remise 10-15% — **stepped par produit** (pattern rare)
Contrairement à mon hypothèse initiale "remise flat 10 ou 15%", Decathlon a une **remise variable par SKU** :
- **Créatine 300g** : 14,99€ → 12,74€ = **−15,1%**
- **Whey 900g** : 28,99€ → 25,99€ = **−10,3%**
- **Whey Isolate 2kg** : 79,99€ → 71,99€ = **−10,0%**
- **Packs combinés** : généralement −10%

C'est un pattern **unique dans le panel** — les 4 autres marques avec abo sont toutes en remise flat (−10% Novoma, −15% Nutri&Co/Nutrimuscle). Decathlon applique une remise par SKU, probablement calée sur les marges individuelles. **La créatine a la remise maximale car c'est le SKU avec la plus grosse marge** (ingrédient commoditisé, prix plancher bas).

**Implication Impulse** : pattern intéressant à considérer — remise différenciée par produit selon la marge, pas flat. Mais coût de communication client (il faut expliquer pourquoi telle créatine est à −15% et telle whey à −10%).

### Catalogue éligible plus large que prévu
Le master_data listait "whey, créatine, quelques compléments, croquettes". La vérif live révèle un **scope plus complet** :
- **Whey** (isolate, standard, concentré, protéines végétales)
- **Créatine** (monohydrate)
- **BCAA**
- **Gainers**
- **ISO drinks** (boissons isotoniques)
- **Électrolytes**
- **Gels énergétiques**
- **Compotes, barres, pâtes de fruits**
- **Préparations énergétiques**
- **Packs développement musculaire** (whey + créatine combinés, remise groupée)
- Catégorie à part : **croquettes pour chien** (à partir de 37,01€/mois)

C'est tout le spectre "nutrition sportive à consommation récurrente" — muscu + endurance. Logique : Decathlon a choisi les SKUs où la récurrence est naturelle (consommation quotidienne ou hebdomadaire). Les autres catégories (matériel, textile, accessoires) sont exclues car one-shot par nature.

### Packs "développement musculaire" — pattern intéressant
Decathlon propose des **packs multi-produits abonnables** (ex : Whey 900g + Créatine 300g en 1 pack). C'est une **alternative au "panier multi-produits à la carte"** qui est absent chez eux.

Le pack est un **SKU unique** dans leur système, donc compatible avec leur modèle "1 produit = 1 abonnement". Le client qui veut Whey + Créatine + BCAA doit soit : (a) prendre un pack pré-composé si ça existe, soit (b) créer 3 abos distincts.

**Implication Impulse** : les packs abonnables sont une **solution pragmatique** à la limitation "1 produit = 1 abo" — plus simple techniquement que le multi-produits à la carte, mais quand même flexible pour le client. À considérer dans la reco.

### Programme fidélité Decat'Club — cumulable
**10 points par euro dépensé en abo** → crédités sur le compte Decat'Club global du client (pas un compte fidélité abo isolé).

Echanges possibles :
- Cartes cadeaux Decathlon
- Services coaching nutrition / bien-être
- Livraison offerte sur une commande
- Dons à des associations
- Séances sportives en partenariat
- Magazines partenaires

Validité points : 12 mois. Crédités sous 48h après achat.

**Avec un abo à 40€/mois → 400 points/mois → 4 800 points/an**. Si la conversion est ~500 pts = 5€, c'est ~48€/an de bonus fidélité, soit **10% de cashback indirect** en plus des 10-15% de remise abo. Total économie réelle : **~20-25%** sur un abo Decathlon — **compétitif avec les -15% flat de Nutri&Co/Nutrimuscle**, mais contraint à la conversion en produits/services Decathlon.

### Livraison — modèle stepped (comme Novoma)
- **Relais (Mondial Relay)** : **offerte sans seuil** pour les abonnés ✅
- **Domicile** : **payante**, 3-4,50€ selon distance/poids
- Pas de livraison domicile offerte même pour les abonnés

C'est **le même pattern que Novoma** : relais inclus, domicile payant. Pattern "rentabilité prudente" vs "acquisition agressive" (Nutri&Co/Nutrimuscle qui offrent le domicile).

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_pct` | `"10-15%"` (vague) | `"10-15% (stepped par produit, pas flat)"` avec détail par SKU | abonnement.decathlon.fr + calculs |
| `modele_commercial.remise_note` | `"Abonnement par produit, 1 produit = 1 abonnement"` | Version complète avec pattern remise par SKU + packs | idem |
| `modele_commercial.livraison_abo.offerte` | `null` | `"relais uniquement"` | abonnement.decathlon.fr |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `0` (relais) | idem |
| `perimetre_produit.scope` | `"Sélection limitée : whey, créatine, quelques compléments, croquettes"` | Catalogue complet nutrition sportive (10+ catégories) + packs + croquettes | abonnement.decathlon.fr navigation |
| `perimetre_produit.exclusions` | `[]` | 2 entrées (one-shot/saisonniers, promos ponctuelles) | Structural |
| `ux_page_produit.screenshots_files` | préfixe `decathlon_abo_*` | nommage local | refacto |
| `evaluation.strengths` | 5 items | 7 items (ajouté : Decat'Club cumulable, catalogue plus large, prix plancher 12,74€, pouvoir omnicanal) | Vérifs live |
| `evaluation.weaknesses` | 5 items | 7 items (ajouté : domicile payant, pas de visibilité pause/skip, Trustpilot nuancé) | Vérifs live |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Équivalence économique Decat'Club + abo** : ma hypothèse "20-25% d'économie totale avec fidélité cumulable" mériterait d'être modélisée en détail pour le deck. À chiffrer si on veut faire une slide comparative "vraie valeur perçue par marque".
- **Catalogue croquettes chien** : hors sujet pour Impulse (pas de produits animaux), mais intéressant comme preuve que Decathlon étend son abo au-delà de la nutrition humaine. Bas priorité.
- **Taille réelle de l'offre abo dans le business Decathlon** : est-ce marginal ou stratégique ? Impossible à savoir sans data interne. Les verbatims faibles ("peu de retours spécifiques") suggèrent que c'est marginal.
- **Notes /5** — propositions sparring : UX **3.0** (sous-site isolé, basique, 1 produit = 1 abo, friction modification) / Offre **3.5** (remise stepped OK, Decat'Club cumulable +, mais domicile payant −) / Pertinence **2.0** (Decathlon est sur un positionnement grande distribution ≠ Impulse premium — c'est un contre-modèle UX plus qu'un modèle à copier) / Global **2.8**. À trancher en fin de revue.

## Insight deck
Decathlon est **le contre-modèle UX** à amener dans le deck pour illustrer ce qu'il **ne faut pas** faire architecturalement :
1. **Sous-domaine dédié = friction** — à ne pas reproduire chez Impulse (toggle intégré à chaque fiche produit, pas un site séparé)
2. **1 produit = 1 abo = mauvaise UX multi-abos** — Impulse doit permettre de combiner plusieurs produits dans un même panier abo, ou proposer des packs pré-composés à la Decathlon
3. **Modification = résiliation + recréation = anti-pattern majeur** — Impulse doit permettre de changer le SKU, la fréquence ou le produit sans casser l'abo
4. **Mais** : le programme fidélité cumulable Decat'Club est un **mécanisme puissant** à s'inspirer — Impulse pourrait coupler son abo à un programme fidélité global qui récompense aussi les achats one-shot.
