# Shopify tags — règle stricte (impact calcul CA HCS)

Chargé par `/gorgias` à l'Étape 8 quand une draft order est créée.

**Règle critique pour les rapports financiers.** Un mauvais tag fausse le calcul du CA HCS (Havea Commercial Services), propriétaire de la marque Impulse Nutrition.

## Les 2 tags qui sortent une commande du CA HCS

| Tag | Quand l'utiliser | Coût pour HCS |
|---|---|---|
| `Service client` | Replacement SAV, geste commercial, commande utilisant un code `[PRENOM]-SAV` (welcome ou SAV créé ad-hoc) | Coût **SAV** |
| `Dotation influenceur` | Envoi mensuel ambassadeur, commande utilisant un code dotation, commande utilisant un code crédit ambassadeur `(O−Q)×20€` | Coût **marketing influence** |

**Règle de discrimination** : la présence d'un de ces 2 tags = la commande **sort du CA réel HCS**. Sans tag = **vraie vente comptabilisée** dans le CA.

## Mapping détaillé par scénario

| Scénario | Tag |
|---|---|
| Replacement colis bloqué (§2.1 process_sav_unified) | `Service client` |
| Replacement returned-to-sender (§2.2) | `Service client` |
| Replacement produit cassé / manquant | `Service client` |
| Geste commercial post-bad-rating BigBlue (§2.4) | `Service client` |
| Commande utilisant code `[PRENOM]-SAV` côté client | `Service client` |
| Commande utilisant code welcome `ACHAB25`/`PGAU25`/`{NOM}25` | `Service client` |
| Envoi dotation mensuelle à un ambassadeur `Suivi_Dot` / `Suivi_Paid` | `Dotation influenceur` |
| Commande utilisant un code crédit ambassadeur (formule `(O−Q)×20€`) | `Dotation influenceur` |
| Vente normale e-commerce (client final lambda) | **aucun de ces 2 tags** |
| Commande d'un ambassadeur qui achète avec son propre argent (pas de code dotation / crédit utilisé) | **aucun de ces 2 tags** |

## Cas particulier — ambassadeur qui fait un SAV

Si la personne qui contacte le SAV est elle-même un ambassadeur (`Suivi_Amb`, `Suivi_Dot`, `Suivi_Paid`) :

- Le flow technique reste identique (draft + discount 100% + shipping 0€ + replacement via BigBlue).
- **Le tag de la commande de remplacement reste `Service client`** (c'est bien un SAV, pas une dotation).
- Ne PAS mettre `Dotation influenceur` sur un replacement SAV, même si le client est ambassadeur — ça faussa le calcul du coût marketing qui se retrouverait gonflé d'un coût SAV.

## Règles "Ne JAMAIS"

- ❌ **Oublier le tag `Service client`** sur un replacement SAV → la commande entre dans le CA alors qu'elle coûte à HCS → double comptabilisation erronée
- ❌ **Mettre `Service client`** sur une vraie vente e-commerce qui utilise un code promo normal → sort arbitrairement de la comptabilité
- ❌ **Mettre les 2 tags en même temps** sur une commande → cas indéterminé, comptabilisation incohérente
- ❌ **Inventer un 3e tag** (ex : `SAV`, `Geste commercial`, `Dotation`) — seuls ces 2 tags exacts sont reconnus par le calcul de CA
- ❌ **Omettre le tag** en pensant "c'est évident que c'est SAV" — le calcul est automatisé, il lit les tags Shopify, pas les notes

## Verification

Avant `complete_draft_order`, vérifier dans le payload :
- `tags` est bien présent
- La valeur est exactement `"Service client"` ou `"Dotation influenceur"` (case sensitive, espacement exact)
- Pas d'autre tag SAV/dotation parasite

Si on édite une draft existante pour lui ajouter/corriger un tag, `update_draft_order(tags=...)` fonctionne (c'est `line_items` qui est bloqué, pas les tags).

## Références

- Détails création des codes (affilié, dotation, crédit, SAV) : `knowledge/operations.md#créer-un-code-affilié-ambassadeur`
- Détails création des draft orders : `knowledge/operations.md#créer-un-draft-order-sav-ou-dotation`
- Règle officielle process : `knowledge/operations.md#sav--opérations-client` §4
