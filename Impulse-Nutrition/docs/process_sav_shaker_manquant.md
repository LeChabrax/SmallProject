# Process SAV — Shaker / Accessoire manquant

## Cas traités
- **Elona Hamel** (ticket #50337802, commande IMP5977) — 08/04/2026
- **Sharleen Rosellini** (ticket #51091376, commande IMP6338) — 08/04/2026

## Contexte
Clients ayant reçu leur commande sans le shaker 450ml promis lors d'une promo (offert dès X€ d'achat). Ils contactent le SAV pour signaler l'oubli.

---

## Réponse standard (2 options à proposer)

> Bonjour [Prénom],
>
> Merci pour votre message. Nous avons vérifié votre commande [IMPXXX] et vous avez tout à fait raison, le shaker aurait dû être inclus. Nous nous excusons pour cet oubli.
>
> Afin de corriger cela, nous vous proposons deux options :
> 1. Nous procédons à un renvoi du shaker à votre adresse
> 2. Nous vous créons un code promotionnel utilisable sur votre prochaine commande, qui vous permettra de bénéficier d'un shaker ainsi qu'un bidon offerts
>
> N'hésitez pas à nous indiquer l'option qui vous convient le mieux, nous nous en occupons immédiatement.
>
> Belle journée,
> Le service client

---

## Si le client choisit l'option 2 (code promo)

### 1. Créer le code sur Shopify via l'API

```python
import requests

SHOPIFY_DOMAIN = "impulse-nutrition-vitavea.myshopify.com"
CLIENT_ID = "..."
CLIENT_SECRET = "..."

resp = requests.post(
    f"https://{SHOPIFY_DOMAIN}/admin/oauth/access_token",
    json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "client_credentials"}
)
token = resp.json()["access_token"]

# Étape 1 : créer la price rule
price_rule = requests.post(
    f"https://{SHOPIFY_DOMAIN}/admin/api/2024-01/price_rules.json",
    json={"price_rule": {
        "title": "[PRENOM]-SAV",
        "target_type": "line_item",
        "target_selection": "entitled",
        "allocation_method": "across",
        "value_type": "percentage",
        "value": "-100.0",
        "customer_selection": "all",
        "starts_at": "2026-01-01T00:00:00Z",
        "entitled_product_ids": [10651956379979, 10651959984459],  # Shaker 450ml + Bidon 750ml
        "usage_limit": 1,
        "once_per_customer": True
        # pas de ends_at = durée illimitée
    }},
    headers={"X-Shopify-Access-Token": token}
).json()

price_rule_id = price_rule["price_rule"]["id"]

# Étape 2 : créer le code
requests.post(
    f"https://{SHOPIFY_DOMAIN}/admin/api/2024-01/price_rules/{price_rule_id}/discount_codes.json",
    json={"discount_code": {"code": "[PRENOM]-SAV"}},
    headers={"X-Shopify-Access-Token": token}
)
```

### 2. Activer les combinaisons (via GraphQL — obligatoire, le REST ne supporte pas)

```python
mutation = """
mutation {
  discountCodeBasicUpdate(
    id: "gid://shopify/DiscountCodeNode/[PRICE_RULE_ID]",
    basicCodeDiscount: {
      combinesWith: {
        orderDiscounts: true,
        productDiscounts: true,
        shippingDiscounts: true
      }
    }
  ) {
    codeDiscountNode { id }
    userErrors { field message }
  }
}
"""

requests.post(
    f"https://{SHOPIFY_DOMAIN}/admin/api/2024-01/graphql.json",
    json={"query": mutation},
    headers={"X-Shopify-Access-Token": token}
)
```

> **Note** : Le champ `combines_with` n'est pas disponible via REST. Il faut obligatoirement passer par GraphQL avec `discountCodeBasicUpdate`.

### 3. Réponse au client

> Bonjour [Prénom],
>
> Voici votre code promotionnel : **[PRENOM]-SAV**
>
> Il vous permettra d'obtenir votre shaker 450ml et votre bidon offerts sur votre prochaine commande. Pas de date limite, utilisez-le quand vous serez prête 😊
>
> Belle journée,
> Le service client

Fermer le ticket après envoi.

---

## Produits concernés

| Produit | ID Shopify | Variant ID | Prix |
|---------|-----------|-----------|------|
| Shaker 450ml | 10651956379979 | 51956593230155 | 6.90€ |
| Bidon 750ml | 10651959984459 | 51956610367819 | 7.90€ |

---

## Convention de nommage des codes

`[PRENOM]-SAV` — ex : `ELONA-SAV`, `SHARLEEN-SAV`

Simple, identifiable dans Shopify, facile à retrouver en cas de litige.
