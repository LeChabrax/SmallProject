# Process — Création des draft orders Shopify

Runbook procédural pour créer chaque type de **draft order** sur Shopify,
avec le **bon tag** (impact direct sur le calcul du CA HCS).

> Verrouillé en interview 2026-04-13. **Mal tagger une commande fausse les
> rapports financiers de HCS.** Cette règle est non-négociable.

---

## 0. La règle d'or des tags

**Il existe exactement 2 tags qui sortent une commande du calcul du CA :**

| Tag | Coût pour HCS | Utilisé pour |
|---|---|---|
| **`Service client`** | Coût SAV | Replacements, gestes commerciaux, codes `[PRENOM]-SAV` |
| **`Dotation influenceur`** | Coût marketing | Envois mensuels ambassadeurs, codes dotation, codes crédit `[PRENOM]-CREDIT` |

Toute autre commande (ou commande sans tag de cette liste) = **vraie vente
comptabilisée dans le CA**.

→ Ne jamais inventer un tag custom pour ces 2 cas. Ne jamais oublier le tag
sur une commande gratuite. Ne jamais utiliser ces tags sur une vraie vente.

---

## 1. Defaults obligatoires pour TOUTE commande gratuite

Que ce soit SAV ou dotation, dès qu'on a un draft order avec un total à 0 € :

```json
{
  "applied_discount": {
    "title": "<voir cas>",
    "value_type": "percentage",
    "value": "100.0",
    "description": "<voir cas>"
  },
  "shipping_line": {
    "title": "Expédition gratuite",
    "price": "0.00"
  },
  "tags": "<Service client OU Dotation influenceur>",
  "note": "<contexte court : ref originale + motif>"
}
```

Le `applied_discount.title` change selon le contexte (`SAV`, `Dotation`,
`Crédit ambassadeur`...). Le `tags` est ce qui compte pour la compta.

---

## 2. Mapping par scénario

### 2.1 Replacement SAV (colis bloqué, returned-to-sender, etc.)

```json
{
  "applied_discount": {
    "title": "SAV", "value_type": "percentage", "value": "100.0",
    "description": "SAV"
  },
  "shipping_line": {"title": "Expédition gratuite", "price": "0.00"},
  "tags": "Service client",
  "note": "Replacement IMP4938 — colis bloqué Chronopost"
}
```

→ Tag : **`Service client`**.

### 2.2 Envoi dotation ambassadeur (mensuel, contrat S/M/L ou Paid)

```json
{
  "line_items": [...selection produits selon dotation...],
  "applied_discount": {
    "title": "Dotation", "value_type": "percentage", "value": "100.0",
    "description": "Dotation influenceur — <nom>"
  },
  "shipping_line": {"title": "Expédition gratuite", "price": "0.00"},
  "tags": "Dotation influenceur",
  "note": "Dotation mois X/Y — contrat <nom>"
}
```

→ Tag : **`Dotation influenceur`**.

### 2.3 Commande utilisant un code crédit ambassadeur `[PRENOM]-CREDIT`

L'ambassadeur place lui-même la commande sur le site avec son code crédit.
La commande est créée automatiquement (pas de draft order côté nous), mais
**il faut taguer la commande** après création.

→ Tag : **`Dotation influenceur`** (le crédit est un dû lié à son contrat
ambassadeur, donc coût marketing, pas vente réelle).

**Procédure** :
1. Surveillance : repérer toute commande qui contient le discount code
   `[PRENOM]-CREDIT` (ex : `FLORINE-CREDIT`).
2. Tag : `tags: "Dotation influenceur"` via `update_order` ou Shopify UI.
3. Mise à jour `Suivi_Amb` col Q `nb_credit_used` : ajouter `(value_redeemed / 20)`.

### 2.4 Commande utilisant un code SAV `[PRENOM]-SAV`

Le client place lui-même la commande avec son code SAV (geste commercial).

→ Tag : **`Service client`** (geste commercial SAV, coût SAV pas vente).

**Procédure** :
1. Repérer la commande contenant `[PRENOM]-SAV`.
2. Tag `Service client` après création.
3. Fermer le ticket Gorgias correspondant si pas déjà fait.

### 2.5 Commande normale (vente e-commerce)

Aucun tag dans cette liste. La commande est comptée dans le CA.

---

## 3. Limitations techniques

### 3.1 `update_draft_order` ne touche pas aux line_items

Si on doit ajouter ou retirer un produit après la création du draft (ex :
ajouter un bidon en geste commercial) :

1. `delete_draft_order(draft_id)`
2. `create_draft_order(<full set of line_items>)`
3. Réappliquer `applied_discount`, `shipping_line`, `tags`, `note`

→ Toujours préparer la liste line_items complète AVANT le premier appel.

### 3.2 Pickup point pas reporté sur BigBlue

Quand on crée une draft order avec un point relais comme adresse, BigBlue
ne reçoit pas systématiquement l'info du pickup point. Après
`complete_draft_order` :

1. Aller sur l'UI BigBlue
2. Trouver la commande
3. Modifier manuellement le pickup point

C'est un quirk connu — pas de fix automatique côté MCP pour l'instant.

### 3.3 Refunds non implémentés côté MCP

Les remboursements (partiels ou totaux) doivent passer par l'UI Shopify
ou directement via API REST `/orders/{id}/refunds.json`. Le custom MCP
`shopify_mcp` n'expose pas encore d'outil refund.

---

## 4. Workflow complet — exemple SAV (canonical)

Prend Alexandre Damary `IMP4938`, draft `IMP6923` (cas réel 2026-04-13) :

```python
# 1. Lecture commande originale
order = get_order(order_id=4938)
line_items = [
    {"variant_id": v["variant_id"], "quantity": v["quantity"]}
    for v in order["line_items"]
]
# Ajout geste commercial : 1 bidon 750ml
line_items.append({"variant_id": 51956610367819, "quantity": 1})

# 2. Création draft
draft = create_draft_order(
    line_items=line_items,
    customer_email="alex@example.com",
    note="Replacement IMP4938 — colis bloqué Chronopost",
    tags="Service client",
)
draft_id = draft["draft_order"]["id"]

# 3. Application defaults SAV
update_draft_order(
    draft_order_id=draft_id,
    applied_discount={
        "title": "SAV", "value_type": "percentage",
        "value": "100.0", "description": "SAV",
    },
    shipping_line={"title": "Expédition gratuite", "price": "0.00"},
)

# 4. Complétion
result = complete_draft_order(draft_order_id=draft_id, payment_pending=False)
new_order_name = result["draft_order"]["order_id"]  # ex: IMP6923

# 5. Fix manuel sur BigBlue : reseter le pickup point pour livraison à domicile

# 6. Réponse Gorgias avec la nouvelle référence
```

---

## 5. Checklist avant `complete_draft_order`

Avant de basculer un draft en commande réelle, vérifier dans l'ordre :

- [ ] `tags` contient `Service client` OU `Dotation influenceur` (jamais les 2, jamais aucun pour une commande gratuite)
- [ ] `applied_discount` à 100% si commande gratuite
- [ ] `shipping_line` "Expédition gratuite" 0.00€ si commande gratuite
- [ ] `note` interne explicite (référence + motif)
- [ ] `line_items` complets (pas besoin d'`update_draft_order` après pour ajouter)
- [ ] Adresse de livraison correcte (domicile pour SAV retry, sinon préférence client)

Toute case non cochée = ne PAS compléter le draft. Corriger d'abord.

---

## 6. See also

- [`process_create_codes.md`](process_create_codes.md) — création des codes utilisés dans les line_items
- [`process_calculate_credits.md`](process_calculate_credits.md) — calcul `(O−Q)×20€`
- [`process_sav_unified.md`](process_sav_unified.md) — workflow SAV de bout en bout
- [`reference_mcps.md`](reference_mcps.md) — signatures des outils `shopify_mcp`
