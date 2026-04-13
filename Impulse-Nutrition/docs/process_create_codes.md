# Process — Création des codes Shopify

Runbook procédural pour créer **chaque type de code** Shopify utilisé chez
Impulse Nutrition. Les configurations ci-dessous sont **fetchées de codes
réels en production** (audit 2026-04-13) — ne pas réinventer.

> Verrouillé en interview 2026-04-13. Toute modification de la convention
> doit passer par une décision explicite + mise à jour de ce doc.

---

## 0. Vue d'ensemble — 4 types de codes

| Type | Exemple réel | Pattern | Quand l'utiliser |
|---|---|---|---|
| **Affilié ambassadeur** | `ALEXTV`, `DODO` | -15% percentage, sans limite | Chaque ambassadeur en pipeline `Suivi_Amb` |
| **Affilié Paid** | `LRA20` | -20% percentage, sans limite, no `once_per_customer` | Contrats Paid avec négociation -20% |
| **Dotation négociée** | `TRAILEURSDOTATION` | -200€ fixed, usage_limit, période bornée | Contrat dotation `Suivi_Dot` ou `Suivi_Paid` |
| **Crédit ambassadeur** | (créé à la demande) | -X€ fixed, usage_limit=1, `once_per_customer` | Quand un ambassadeur veut redeem ses crédits (`(O−Q)×20€`) |
| **SAV client** | `[PRENOM]-SAV` | -100% percentage sur Shaker+Bidon, `once_per_customer` | Geste commercial SAV (cf legacy archive) |

---

## 1. Code affilié ambassadeur — clone de `ALEXTV`

**LE pattern canonique pour tous les codes affilié ambassadeur.** Toute
nouvelle création doit être une copie exacte de cette config (sauf le nom
du code et le `title`).

### Configuration price_rule (REST)

```json
{
  "price_rule": {
    "title": "FLORINE",
    "value_type": "percentage",
    "value": "-15.0",
    "customer_selection": "all",
    "target_type": "line_item",
    "target_selection": "all",
    "allocation_method": "across",
    "starts_at": "2026-04-13T00:00:00+02:00",
    "ends_at": null,
    "usage_limit": null,
    "once_per_customer": true,
    "entitled_product_ids": [],
    "entitled_variant_ids": [],
    "entitled_collection_ids": [],
    "prerequisite_subtotal_range": null
  }
}
```

### Discount code

```json
{
  "discount_code": {"code": "FLORINE"}
}
```

### Combinaisons (GraphQL — obligatoire post-création)

```graphql
mutation {
  discountCodeBasicUpdate(
    id: "gid://shopify/DiscountCodeNode/{PRICE_RULE_ID}",
    basicCodeDiscount: {
      combinesWith: {
        orderDiscounts: false
        productDiscounts: true
        shippingDiscounts: true
      }
    }
  ) {
    codeDiscountNode { id }
    userErrors { field message }
  }
}
```

### Recipe Python (utilise `_post` de `shopify_mcp/src/mcp_server.py`)

```python
import requests, os
from datetime import datetime, timezone

DOMAIN = os.environ["SHOPIFY_DOMAIN"]
TOKEN = "..."  # via _get_access_token()
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API = f"https://{DOMAIN}/admin/api/2024-10"

def create_affiliate_code(name: str) -> dict:
    """Clone exactly of ALEXTV — replace name only."""
    starts = datetime.now(timezone.utc).isoformat()
    pr = requests.post(
        f"{API}/price_rules.json",
        headers=HEADERS,
        json={
            "price_rule": {
                "title": name,
                "value_type": "percentage",
                "value": "-15.0",
                "customer_selection": "all",
                "target_type": "line_item",
                "target_selection": "all",
                "allocation_method": "across",
                "starts_at": starts,
                "ends_at": None,
                "usage_limit": None,
                "once_per_customer": True,
            }
        },
    ).json()
    pr_id = pr["price_rule"]["id"]

    requests.post(
        f"{API}/price_rules/{pr_id}/discount_codes.json",
        headers=HEADERS,
        json={"discount_code": {"code": name}},
    )

    # CRITICAL: combinesWith must be set via GraphQL.
    gql = """
    mutation($id: ID!) {
      discountCodeBasicUpdate(
        id: $id,
        basicCodeDiscount: {
          combinesWith: {
            orderDiscounts: false,
            productDiscounts: true,
            shippingDiscounts: true
          }
        }
      ) { userErrors { field message } }
    }
    """
    requests.post(
        f"{API}/graphql.json",
        headers=HEADERS,
        json={"query": gql, "variables": {"id": f"gid://shopify/DiscountCodeNode/{pr_id}"}},
    )
    return {"code": name, "price_rule_id": pr_id}
```

### Vérification post-création

Faire un fetch + comparaison avec ALEXTV pour s'assurer que tous les
champs matchent (sauf `title` et `id`). Toute différence = bug.

---

## 2. Code dotation négociée — pattern `TRAILEURSDOTATION`

Code utilisé par l'ambassadeur lui-même pour redeem sa dotation mensuelle
(≠ code affilié ci-dessus utilisé par ses followers).

### Pattern réel (TRAILEURSDOTATION)

```
title: TRAILEURSDOTATION
value_type: fixed_amount
value: -200.0           ← montant mensuel × usage_limit = budget total
customer_selection: all
target_type: line_item
target_selection: all
allocation_method: across
usage_limit: 6          ← 6 redemptions (1/mois pendant 6 mois)
once_per_customer: false
starts_at: <date début contrat>
ends_at: <date fin contrat>
```

### Règle de calcul (négocié au cas par cas)

```
Pour un contrat de durée D mois × montant mensuel M € :
- value      = -M.0   (le montant unitaire à appliquer par redemption)
- usage_limit = D      (1 redemption par mois)
- starts_at   = début contrat
- ends_at     = fin contrat (D mois plus tard)
```

**Attention** : ne pas confondre avec les *utilisations cibles* du code
**affilié** négociées dans le contrat. Exemple : un contrat de 4 mois × 100€
= 4 utilisations du code dotation, mais l'ambassadeur s'engage en parallèle
à atteindre par exemple 14 utilisations sur son code affilié (mesuré dans la
col `nb_utilisation` (O) du Sheet `Suivi_Amb`).

### Combinaisons

`combinesWith.orderDiscounts: false` — un code dotation ne se combine pas
avec d'autres codes globaux. À confirmer pour chaque cas exotique.

---

## 3. Code crédit ambassadeur — créé à la demande

Quand un ambassadeur dit "je veux utiliser mes crédits accumulés", on
crée un code à valeur cumulée applicable sur **une seule commande**.

### Calcul (interview 2026-04-13)

```
remaining_uses = SUIVI_AMB_COLS["nb_utilisation"]  (col O)
                - SUIVI_AMB_COLS["nb_credit_used"]  (col Q)

credit_value = remaining_uses × 20 €
```

Voir [`process_calculate_credits.md`](process_calculate_credits.md) pour le
workflow complet (lecture des cols, mise à jour de Q après usage).

### Pattern Shopify (à valider à la 1ère utilisation)

```
title: <PRENOM>-CREDIT
value_type: fixed_amount
value: -<credit_value>.0
customer_selection: all
target_type: line_item
target_selection: all
allocation_method: across
usage_limit: 1                  ← une seule commande
once_per_customer: true
starts_at: now
ends_at: null
```

Note : à la 1ère création réelle, fetch le code créé et figer le pattern
exact dans ce doc (suivre la convention `[PRENOM]-CREDIT` pour faciliter
le tracking).

---

## 4. Code SAV client — pattern `[PRENOM]-SAV`

Voir [`archive/process_sav_shaker_manquant.md`](archive/process_sav_shaker_manquant.md)
pour la recette complète (REST price_rule + GraphQL combinesWith). Le
pattern reste valide même si la promo "shaker offert" qui le motivait à
l'origine est obsolète.

Résumé :
- `value_type: percentage`, `value: -100.0`
- `entitled_product_ids: [shaker, bidon]`
- `usage_limit: 1`, `once_per_customer: true`
- `combinesWith.orderDiscounts: true, productDiscounts: true, shippingDiscounts: true`

---

## 5. Convention de nommage

| Type | Format | Exemple |
|---|---|---|
| Affilié ambassadeur | `<PRENOM>` ou `<HANDLE>` en majuscules | `FLORINE`, `ALEXTV`, `DODO`, `JBTRI` |
| Affilié Paid | idem mais variable | `LRA20` |
| Dotation | `<HANDLE>DOTATION` | `TRAILEURSDOTATION` |
| Crédit ambassadeur | `<PRENOM>-CREDIT` | `FLORINE-CREDIT` |
| SAV | `<PRENOM>-SAV` | `MARTIN-SAV` |

Pas de codes hors convention. Les noms passent en majuscules, sans accents
ni caractères spéciaux (sauf le `-` pour SAV/CREDIT).

---

## 6. Tables de référence (codes réels en production — audit 2026-04-13)

| Code | price_rule_id | value_type | value | usage_limit | starts_at | type |
|---|---|---|---|---|---|---|
| `ALEXTV` | 2205486154059 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `DODO` | 2199297753419 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `LRA20` | 2205436543307 | percentage | -20.0 | null | 2025-09-09 | Affilié Paid |
| `TRAILEURSDOTATION` | 2206068539723 | fixed_amount | -200.0 | 6 | 2026-01-15 → 2027-01-31 | Dotation |

`combinesWith` ALEXTV (vérifié via GraphQL) : `orderDiscounts:false,
productDiscounts:true, shippingDiscounts:true`. Identique pour tout code
affilié.

---

## 7. Refresh de cette doc

Quand un nouveau pattern de code apparaît (ex : nouveau type de partenariat,
changement de convention) :
1. Créer le code à la main une fois sur Shopify pour figer le pattern.
2. Fetch sa config via le script `shopify_mcp/.venv/bin/python` (cf
   commandes ci-dessus).
3. Ajouter le pattern dans ce doc + dans le script `create_*_code()`.
4. Mettre à jour la table §6.
