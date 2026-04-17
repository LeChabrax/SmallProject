# Conventions — Nommage des codes Shopify

> Convention unifiée validée le 17/04/2026. Remplace l'ancien pattern `[PRENOM]-CREDIT` par `[CODE]DOTATION` pour tous les crédits ambassadeur.

## Tableau récap

| Type | Format | Pattern Shopify | Paramètres clés | Exemples session |
|---|---|---|---|---|
| **Affilié ambassadeur** | `[NAME]` | `create_affiliate_code(name)` (clone ALEXTV) | `-15%`, `once_per_customer=true`, `usage_limit=null`, combinesWith product+shipping | FITBYSIMON, ALTIZ, MAXIMEC, THOMASBNT |
| **Dotation one-shot** | `[NAME]DOTATION` | `create_discount_code` | `fixed_amount` `-N€`, `usage_limit=1`, `once_per_customer=true`, combinesWith product+shipping | KIKISPORTIVEDOTATION (-20€) |
| **Dotation récurrente** | `[NAME]DOTATION` | `create_discount_code` | `fixed_amount` `-M€/mois`, `usage_limit=D mois`, `once_per_customer=false`, `ends_at=fin contrat`, combinesWith product+shipping | ALTIZDOTATION (-120€ × 4) |
| **Affilié paid** | `[NAME]` | `create_paid_affiliate_code(name, percent)` (clone LRA20) | `-20%` par défaut, once_per_customer=true | — |
| **Welcome** | `ACHAB25` / `[PRENOM]25` | `create_discount_code` percentage `-25%` | `starts_at=now`, usage_limit=null | ACHAB25 (défaut), PGAU25 (legacy) |
| **SAV client** | `[PRENOM]-SAV` | `create_discount_code` | percentage `-100%`, `entitled_product_ids=[shaker, bidon]`, `usage_limit=1`, combinesWith tout=true | — |

## Pattern `[CODE]DOTATION` détaillé

### Variante A — One-shot (crédit ponctuel)

Usage : redeem crédits accumulés, geste commercial ponctuel, relance ambassadeur inactif.

```python
create_discount_code(
    title="KIKISPORTIVEDOTATION",
    code="KIKISPORTIVEDOTATION",
    value=-20.0,                          # montant crédit (solde × 20€ typiquement)
    value_type="fixed_amount",
    usage_limit=1,                        # utilisation unique
    once_per_customer=True,
    combines_order_discounts=False,
    combines_product_discounts=True,
    combines_shipping_discounts=True,
)
```

**Calcul crédit** depuis Suivi_Amb : `solde = col_O − col_Q`, puis `value = -(solde × 20)`.

**Mise à jour Sheet après usage** :
- Avant commande : col P (`code_credit`) ← `[CODE]DOTATION`
- Après commande : col Q (`nb_credit_used`) ← `Q + solde` (nouveau Q = O)

### Variante B — Récurrent mensuel (contrat Dotation négocié)

Usage : contrat Dotation structuré (Suivi_Dot), N mois × M €/mois.

```python
create_discount_code(
    title="ALTIZDOTATION",
    code="ALTIZDOTATION",
    value=-120.0,                         # montant mensuel
    value_type="fixed_amount",
    usage_limit=4,                        # nb de mois
    once_per_customer=False,              # utilisable chaque mois
    ends_at="2026-08-17T23:59:59+02:00",  # fin contrat
    combines_order_discounts=False,
    combines_product_discounts=True,
    combines_shipping_discounts=True,
)
```

**Règle** : pour un contrat D mois × M €/mois :
- `value = -M.0`
- `usage_limit = D`
- `ends_at` = date début + D mois

## Convention affilié — pourquoi ALEXTV pattern ?

`create_affiliate_code(name)` clone **ALEXTV** (code d'ALEX un de nos ambassadeurs). Pattern canonique Impulse :

- `-15%` percentage, tout le site
- `once_per_customer=true` (une utilisation par client, anti-fraude)
- `usage_limit=null` (illimité)
- `combinesWith`: order=false / product=true / shipping=true (empile avec promos produits et livraison mais pas autres codes order-level)
- Pas d'end date (actif tant qu'on ne le désactive pas)

## Cas particulier code paid

`create_paid_affiliate_code(name, percent=-20)` clone **LRA20**. Percent configurable (défaut -20%). Sinon identique à l'affilié classique.

Usage : contrats rémunérés (Suivi_Paid).

## ⚠️ Red flags

- **Jamais de code avec accents, espaces ou caractères spéciaux** (seul `-` toléré pour `[PRENOM]-SAV`)
- **Majuscules obligatoires** — les codes sont insensibles à la casse côté checkout mais conventionnellement uppercase
- **Jamais réutiliser un nom** déjà utilisé par un ambassadeur précédent
- Le **code dotation** (`[CODE]DOTATION`) est pour l'ambassadeur lui-même ; le **code affilié** (`[CODE]`) pour sa communauté. Ne pas confondre.

## Tag Shopify obligatoire sur commande générée

| Type de commande | Tag Shopify |
|---|---|
| Utilisation code `[NAME]DOTATION` | `Dotation influenceur` |
| Utilisation code `[PRENOM]-SAV` | `Service client` |
| Vente classique | aucun tag |

**Mal tagger = fausse les rapports financiers HCS**. Non négociable.

## Source de vérité

- `knowledge/operations.md#pattern-code-dotation-codedotation` (doc canonique)
- `infra/scripts/...` : scripts Shopify qui utilisent ces patterns
