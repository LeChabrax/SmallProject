# SAV recipe — draft order Shopify replacement

Chargé par `/gorgias` à l'Étape 8 quand une replacement draft est déclenchée (scenarios SAV §2.1, §2.2, §2.4, produit cassé, manquant).

## Defaults canoniques (à appliquer systématiquement)

```json
{
  "customer_id": <ID_NUMÉRIQUE_SHOPIFY>,
  "line_items": [
    {
      "variant_id": <variant_id_numérique>,
      "quantity": <qty>
    }
  ],
  "applied_discount": {
    "title": "SAV",
    "value_type": "percentage",
    "value": "100.0",
    "description": "SAV"
  },
  "shipping_line": {
    "title": "Expédition gratuite",
    "price": "0.00"
  },
  "tags": "Service client",
  "note": "<short context: original order ref + reason + goodwill gesture>"
}
```

## ⚠️ Règles critiques

### 1. Customer ID numérique, pas email
**Toujours passer `customer_id` (ID numérique Shopify), jamais `customer_email`.**

Passer `customer_email` à `create_draft_order` crée un doublon customer blank dans Shopify, ce qui pollue la base client.

Flow correct :
1. `mcp__gorgias__get_customer(customer_id=ticket.customer_id)` → récupère l'email
2. `mcp__shopify__get-customers(query=email=...)` → récupère le customer_id Shopify numérique
3. Passer ce customer_id au `create_draft_order`

### 2. `update_draft_order` ne peut PAS modifier `line_items`

Si tu as besoin d'ajouter ou retirer un produit après création (ex : ajouter un bidon comme geste commercial qui n'était pas prévu initialement), **ne PAS utiliser `update_draft_order`** sur les line_items — ça ne fonctionne pas.

Flow correct :
1. `delete_draft_order(draft_id)`
2. `create_draft_order(...)` avec la nouvelle liste complète de line_items + les mêmes defaults (discount, shipping, tag)

### 3. Pickup point BigBlue — à régler manuellement

**Après `complete_draft_order`**, le pickup point choisi dans Shopify **n'est pas reporté de façon fiable** vers l'UI BigBlue. Il faut :

1. `complete_draft_order(draft_id)` → crée la commande réelle à 0 €
2. Attendre que BigBlue attrape la commande (quelques minutes)
3. **Aller manuellement sur l'UI BigBlue** et régler le pickup point

Pour les scenarios §2.1 (colis bloqué en transit), la recommandation est de shipper **à l'adresse domicile** (pas pickup point) pour éviter de retomber sur le même problème. Dans ce cas, pas de pickup point à régler.

### 4. Tag `Service client` obligatoire

Tag manquant = commande comptée dans le CA HCS alors que c'est un coût SAV → fausse les rapports financiers.

**Vérifier avant `complete_draft_order`** que le tag est bien présent.

## Line items — sourcing

Pour récupérer les `variant_id` numériques des produits à mettre dans la replacement draft :

- **Catalogue complet** : `knowledge/impulse.md#4-catalogue-produits` (96 produits, variant_id, SKU, prix par catégorie)
- **Lookup rapide** : `mcp__shopify_orders__search_products(query="...")` ou `get_product_variants(product_id)`
- **Pour copier le contenu de la commande originale** : `get_order(order_id).line_items` → mapper chaque line item à un variant_id

## Geste commercial (goodwill gesture)

Sur les scenarios §2.1 et §2.2, ajouter un geste commercial pour contenir la frustration client :

| Produit geste | Variant ID (à confirmer via catalogue) | Quand |
|---|---|---|
| Bidon (500ml ou 1L) | Cf catalogue | Scenario §2.1 (colis bloqué, 1re récidive) |
| Shaker | Cf catalogue | Scenario §2.1 (2e récidive ou gros panier) |
| Un produit de la gamme effort (30-40€) | Cf catalogue | Scenario §2.2 (returned-to-sender, cas impactant) |

**Ne pas surpromettre le geste** dans le reply Gorgias avant d'avoir créé la draft — d'abord créer, confirmer que la draft passe en complete, PUIS reply.

## Note field — structure recommandée

```
Original order: IMP4938 / Jean Dupont
Reason: SAV §2.1 colis bloqué Chronopost misroute 12/04
Ship to: adresse domicile (pas pickup point)
Goodwill: +1 bidon 500ml
Antoine validated: 2026-04-15 par Claude via /gorgias skill
```

Clair et récupérable si un collègue reprend le dossier plus tard.

## Steps complets

1. Récupérer `customer_id` Shopify numérique (pas email)
2. Récupérer `line_items` avec `variant_id` numériques (catalogue ou get_order original)
3. Si geste commercial → ajouter les variants correspondants à la liste
4. `create_draft_order(...)` avec les defaults ci-dessus (discount 100% + shipping 0€ + tag + note)
5. Vérifier que la draft est bien créée (pas d'erreur)
6. `complete_draft_order(draft_id)` → Shopify crée la commande réelle, `financial_status=paid`, `total=0€`, BigBlue l'attrape
7. Si pickup point à régler → le faire manuellement sur UI BigBlue
8. Reply Gorgias au client avec la nouvelle référence `IMP####` et la confirmation du geste
9. Close le ticket (ou laisser open si on attend une confirmation de réception)

## Reference cases

- **§2.1** : Alexandre Damary, IMP4938 → draft IMP6923 (`12564101628235`). Archive session 2026-04-13.
- **§2.2** : Jean-Baptiste Morand, IMP6586 (2 points relais refusés, 1er au Carrefour Express Lyon Créqui). Archive.
- **§2.3** : Amandine Laurent, IMP6036, refund 50,18 € sur `36592237936971` (Collagène marin Peptan).
