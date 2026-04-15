# Cas SAV — Nouika_0724 (TikTok Shop)

**Canal** : TikTok Shop (chat client)
**Buyer** : `nouika_0724`
**Période** : 13 → 15 avril 2026
**Statut final** : ✅ Résolu — code de remplacement envoyé

---

## 1. Contexte

La cliente `nouika_0724` a reçu sa commande TikTok Shop le 13 avril 2026.
À la réception, elle a constaté qu'**un produit de sa commande était
endommagé**. Elle a ouvert un chat avec le service client TikTok Shop pour
signaler le problème.

Gestion du cas : service client Impulse Nutrition (via le MCP TikTok Shop
pour la lecture/réponse, et via le MCP Shopify pour la création du code
de remplacement).

---

## 2. Timeline complète des messages

### 13 avril 2026

**16:02 — nouika_0724** (envoi d'une vidéo du produit endommagé)
> *[Vidéo jointe]*

**16:02 — nouika_0724**
> « J'ai reçu le colis avec un petit problème, bon voilà »

**18:27 — Service client Impulse Nutrition**
> « Bonjour Nouika,
>
> Merci pour votre message, nous sommes navrés d'apprendre que certains
> produits de votre commande ont été endommagés. Pourriez-vous nous
> indiquer combien de produits ont été endommagés et quelle option vous
> préférez ?
>
> Vous conservez votre produit et nous vous offrons un coupon à utiliser
> sur notre site Impulse Nutrition pour bénéficier d'une barre protéinée
> gratuite ou d'un bidon, selon votre choix.
>
> Vous nous renvoyez le produit et nous vous réexpédions un nouveau
> produit.
>
> N'hésitez pas à nous indiquer votre choix.
>
> Très belle journée,
> Le service client »

**19:25 — nouika_0724**
> « J'ai qu'un produit qui a été endommagé »

**21:06 — nouika_0724**
> « D'accord, je garde le produit et je choisis un produit. Dans votre
> site avec le coupon que vous me donnerez »

➡️ Elle choisit l'**option 1** (garder le produit + recevoir un coupon
pour un produit offert sur le site).

---

### 14 avril 2026

**12:09 — Service client Impulse Nutrition**
> « Bonjour Nouika,
>
> Merci pour votre retour. Pour qu'on puisse vous préparer le coupon,
> pouvez-vous nous indiquer votre choix :
>
> 1. Une barre protéinée offerte
> 2. Un bidon offert
>
> Dès votre réponse, on vous envoie le code à utiliser sur
> impulse-nutrition.fr.
>
> Belle journée,
> Le service client »

**12:41 — nouika_0724**
> « Ça sera le choix numéro deux s'il vous plait, merci »

➡️ Elle choisit le **bidon offert**.

---

### 15 avril 2026

Création du code promotionnel Shopify (cf section 3), puis envoi du
message final contenant le code.

**~09:40 — Service client Impulse Nutrition**
> « Bonjour Nouika,
>
> Voici votre code : **NOUIKA-SAV**
>
> Il vous permet d'obtenir 1 bidon 750ml Impulse Nutrition offert
> (valeur 7,90€) sur impulse-nutrition.fr.
>
> Comment l'utiliser :
> 1. Ajoutez le bidon 750ml à votre panier
> 2. Entrez le code `NOUIKA-SAV` au moment du paiement
> 3. Le bidon passera à 0€ (seuls les frais de livraison restent à
>    votre charge)
>
> Le code est à usage unique et valable uniquement sur votre compte.
>
> Encore toutes nos excuses pour le désagrément, nous vous souhaitons
> une belle journée.
>
> Sportivement,
> Le service client »

---

## 3. Opération Shopify — Création du code `NOUIKA-SAV`

Le code a été créé via l'API Shopify Admin REST + GraphQL en suivant le
runbook interne `docs/process_create_codes.md` §4 (pattern canonique
« Code SAV client » `[PRENOM]-SAV`).

### Configuration `price_rule`

| Champ | Valeur |
|---|---|
| `title` | `NOUIKA-SAV` |
| `value_type` | `percentage` |
| `value` | `-100.0` |
| `customer_selection` | `all` |
| `target_type` | `line_item` |
| `target_selection` | `entitled` |
| `allocation_method` | `each` |
| `entitled_product_ids` | `[10651959984459]` (Bidon 750ml — SKU `VSGOURDE`) |
| `starts_at` | `2026-04-15T09:33:15+02:00` |
| `ends_at` | `null` (pas d'expiration) |
| `usage_limit` | `1` (usage unique) |
| `once_per_customer` | `true` |

### Discount code associé

| Champ | Valeur |
|---|---|
| `code` | `NOUIKA-SAV` |
| `price_rule_id` | `2217667428683` |

### Combinaisons (`combinesWith`) — configuré via GraphQL

```json
{
  "orderDiscounts":    true,
  "productDiscounts":  true,
  "shippingDiscounts": true
}
```

### Portée exacte du code

- **Produit ciblé** : Bidon 750ml Impulse Nutrition uniquement
  (product_id `10651959984459`).
- **Réduction** : 100% sur ce produit uniquement.
- **Frais de livraison** : non couverts par le code (à la charge de la
  cliente).
- **Nombre d'utilisations** : 1.

Cette configuration garantit qu'une utilisation du code ne peut
**pas** être détournée pour obtenir d'autres produits gratuits : la
restriction `entitled_product_ids` limite la remise au seul SKU
`VSGOURDE`.

### Vérification post-création

Un fetch REST sur `GET /admin/api/2024-10/price_rules/2217667428683.json`
a confirmé que tous les champs correspondent au pattern attendu, et la
mutation GraphQL `discountCodeBasicUpdate` a retourné `userErrors: []`
(succès).

---

## 4. Résumé exécutif

| Élément | Valeur |
|---|---|
| **Problème signalé** | 1 produit endommagé à la réception |
| **Option retenue** | Geste commercial — bidon offert sur site |
| **Coût pour Impulse** | 7,90€ (valeur catalogue du bidon 750ml) |
| **Retour produit** | Non (cliente garde le produit endommagé) |
| **Délai de résolution** | 2 jours (13 avril → 15 avril) |
| **Nombre d'échanges** | 6 messages buyer, 3 messages SC |
| **Code créé** | `NOUIKA-SAV` (price_rule `2217667428683`) |
| **Usage du code** | 1 fois max, sur compte cliente uniquement |
| **Statut actuel** | Code envoyé, en attente d'utilisation par la cliente |

---

## 5. Conformité au process interne

Cette gestion respecte le process documenté dans :

- [`docs/process_sav_unified.md`](./process_sav_unified.md) — Process
  SAV unifié Gorgias / TikTok / Shopify / BigBlue
- [`docs/process_create_codes.md`](./process_create_codes.md) §4 —
  Pattern canonique « Code SAV client `[PRENOM]-SAV` »
- [`CLAUDE.md`](../CLAUDE.md) — Règle de persona (vouvoiement formel
  côté service client, signature « Le service client »)

Aucune dérogation au pattern standard.
