# Process — SAV unifié

Consolidation of everything we know about Impulse Nutrition's customer-service
workflow : ticket triage in Gorgias, replacement orders in Shopify, pickup
point fixes in BigBlue, discount codes for goodwill gestures.

> Supersedes : the SAV section in `CLAUDE.md`, `process_sav_shaker_manquant.md`
> (still useful for the discount-code recipe), and the recent session notes
> `knowledge/archive/session_sav_2026-04-13.md`.

---

## 0. Behavioral rules

1. **Draft before submit.** Never send a Gorgias reply / create a Shopify draft / file a BigBlue claim without explicit "go" from Antoine. Applies to every tool call that has a side effect.
2. **Persona côté SC = entité Impulse Nutrition, JAMAIS Antoine.**
   - Gorgias / WAX (WhatsApp) / email SC → vouvoiement formel, signature `Le service client` ou `L'équipe Impulse Nutrition`.
   - **Ne JAMAIS signer "Antoine"** sur un canal client final, même si c'est lui qui rédige. Le client achète à une marque, pas à une personne.
   - Inversement, sur Instagram DM (canal ambassadeur) → tutoiement, signature `Sportivement, Antoine`. Voir `gorgias_mcp/personality.md` vs `instagram_dm_mcp/personality.md`.
3. **Messages to BigBlue helpdesk are in French** (their SOP).
4. **Read the thread first.** `list_ticket_messages` before drafting a reply — missing context leads to wrong promises.

---

## 1. Daily SAV pass — how to pull tickets

### 1.0 Channels couverts par Gorgias

Tous les SAV remontent dans Gorgias, peu importe le canal d'origine :

| Canal | Mécanisme | Tag Gorgias |
|---|---|---|
| **Email** | natif Gorgias | (selon contenu) |
| **Chat site** | natif Gorgias | (selon contenu) |
| **Contact form site** | natif Gorgias | (selon contenu) |
| **WhatsApp** | via outil **WAX** qui pousse les messages dans Gorgias | `WAX` |
| **Instagram (mention/DM cliente)** | natif Gorgias | (selon contenu) |
| **Facebook** | natif Gorgias | (selon contenu) |

Le tag `WAX` identifie spécifiquement les tickets venus de WhatsApp. La
réponse via Gorgias est repoussée automatiquement sur WhatsApp par WAX —
même flow de réponse que les autres canaux, mais le tone reste
**vouvoiement formel** comme pour les autres canaux SC.

### 1.1 Strict pull protocol

Learned the hard way on 2026-04-13 (see archive): a 30-ticket pull missed
`Amandine Laurent` (`#52032892`). Since then :

1. **Start with `list_tickets(limit=100, order_by="updated_datetime:desc")`**. Never less.
2. **Filter locally** to actionable tickets :
   - Keep channels : `email`, `chat`, `contact_form`, `instagram`, `facebook`, `internal-note`.
   - Prioritize tags : `urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`.
   - Ignore : subjects prefixed `[SPAM POSSIBLE]`, automatic replies (`Réponse automatique`, `Automatic reply`), `closed` tickets that are just bounces.
3. **If nothing flags or Antoine cites a client absent from the list** → second pass with `order_by="created_datetime:desc"` to catch tickets with old `updated_datetime` but recent content.
4. **Don't conclude "not found" from a short list.** Expand the pull first.
5. **`search_tickets`** is functional (custom implementation with email lookup + substring fallback, see `reference_mcps.md` §2) but it is not a full-text search. The pull protocol is the safety net.

---

## 2. SAV scenarios

> **Note 2026-04-13** : la promo historique « shaker offert dès 59 € » est
> obsolète. Si un client réclame un shaker manquant suite à une promo
> ancienne, vérifier d'abord que la promo était bien active à la date de
> sa commande. Le runbook archivé reste utile pour la mécanique du code
> `[PRENOM]-SAV` (voir [`archive/process_sav_shaker_manquant.md`](archive/process_sav_shaker_manquant.md)).

### 2.1 Colis bloqué / perdu en transit

Chronopost or Mondial Relay tracking stuck in a loop (`misrouted`,
`held at location`, `delivery postponed`), BigBlue status still `SHIPPED`.

**Flow** :

1. `get_order(order_id)` on Shopify to get line items and shipping address.
2. `get_tracking(bigblue_order_id)` to confirm the issue.
3. Create a **replacement draft** (see §3) containing the original line items + a goodwill gesture (bidon, shaker, or one product of the same range).
4. Ship to the **home address** — no pickup point on the retry.
5. Apply SAV discount 100 % + shipping 0 € defaults.
6. Complete the draft → Shopify creates the order → BigBlue picks it up.
7. **Manually set the pickup point on BigBlue** after the order is created (technical quirk : draft orders don't carry pickup point info into BigBlue's UI reliably).
8. Reply on Gorgias confirming the reshipment + goodwill gesture. Do not expose the tracking loop details to the customer.

**Reference case** : Alexandre Damary, `IMP4938` → draft `IMP6923`
(`12564101628235`), see archive session notes for the full trail.

### 2.2 Returned to sender (refusé par le point relais)

Two consecutive pickup points refuse the parcel — often not the customer's
fault. Offer :

- Refund (simplest)
- OR reship to home address + goodwill gesture.

Wait for customer response before triggering either.

**Reference case** : Jean-Baptiste Morand, `IMP6586` (2 pickups refused,
first at Carrefour Express Lyon Créqui). See archive.

### 2.3 Partial return / partial refund

Customer returns only part of the order. BigBlue marks status `RETURNED`,
Shopify `financial_status` goes `partially_refunded`.

**Flow** :

1. `get_order` to check `refunds` array.
2. If a refund has already been processed (transaction `refund`, status `success`), confirm to the customer (amount + PayPal/Stripe authorization id + 3-5 business days delay).
3. If not yet processed, trigger via Shopify admin UI (MCP refund tool is not implemented — manual step).

**Reference case** : Amandine Laurent, `IMP6036`, refund 50,18 € on line
`36592237936971` (Collagène marin Peptan®).

### 2.4 Bad rating BigBlue (1-2 stars)

Tagged `bigblue-bad-rating-no-comment` or `bigblue-bad-rating-with-comment`.

- Read the comment (if any) via `get_support_ticket`.
- Apology + ask what went wrong. Offer a discount code if the issue is
  service-side.
- Reply on the Gorgias ticket (not BigBlue), close when answered.

---

## 3. Creating a replacement draft order — canonical recipe

Used by scenarios 2.1, 2.2.

### 3.1 Mandatory defaults

```json
{
  "applied_discount": {
    "title": "SAV",
    "value_type": "percentage",
    "value": "100.0",
    "description": "SAV"
  },
  "shipping_line": {"title": "Expédition gratuite", "price": "0.00"},
  "tags": "Service client",
  "note": "<short context: original order ref + reason + goodwill gesture>"
}
```

### 3.2 Technical limitations

- **`update_draft_order` cannot modify `line_items`.** If you need to add or remove a product after creation (e.g. adding a bidon as a goodwill gesture), **delete the draft and recreate it** with the full set of line items + reapply discount + shipping.
- **Pickup point info is not reliably carried over.** After completing the draft, manually set the pickup point on BigBlue's UI.

### 3.3 Steps

1. `create_draft_order` with line items + defaults above.
2. If you need to patch line items → `delete_draft_order` + `create_draft_order` (don't use `update_draft_order`).
3. `complete_draft_order(draft_id)` → Shopify creates the real order, financial_status `paid`, total 0 €.
4. BigBlue picks it up, you fix the pickup point if needed.
5. Reply on Gorgias with the new order reference.

---

## 4. Tags Shopify — règle stricte (impacte le calcul du CA HCS)

**Il existe exactement 2 tags qui sortent une commande du calcul du CA :**

| Tag | Quand l'utiliser | Coût pour HCS |
|---|---|---|
| `Service client` | Replacement SAV, geste commercial, code `[PRENOM]-SAV` utilisé par un client | Coût SAV |
| `Dotation influenceur` | Envoi mensuel ambassadeur, code dotation utilisé, code crédit ambassadeur (`(O−Q)×20€`) utilisé | Coût marketing |

**Discriminant CA** : présence d'un de ces 2 tags = sort du CA réel HCS.
Sans tag = vraie vente comptabilisée. **Cette règle est cruciale** —
mal tagger une commande fausse les rapports financiers.

### Mapping par scénario

| Scénario | Tag |
|---|---|
| Replacement colis bloqué (§2.1) | `Service client` |
| Replacement returned-to-sender (§2.2) | `Service client` |
| Geste commercial post-bad-rating (§2.4) | `Service client` |
| Commande utilisant code `[PRENOM]-SAV` côté client | `Service client` |
| Envoi dotation mensuelle (`Suivi_Dot` / `Suivi_Paid`) | `Dotation influenceur` |
| Commande utilisant code crédit ambassadeur (`(O−Q)×20€`) | `Dotation influenceur` |
| Vente normale e-commerce | (aucun tag de cette liste) |

Détails de création des codes et des commandes : voir
[`process_create_codes.md`](process_create_codes.md) et
[`process_create_orders.md`](process_create_orders.md).

### Cas particulier ambassadeur qui fait un SAV

Si la personne qui contacte le SAV est elle-même un **ambassadeur**
(`Suivi_Amb` / `Suivi_Dot` / `Suivi_Paid`), le flow technique reste le même
mais :

- C'est probablement Antoine qui répond directement (pas via Gorgias / pas
  signé "Le service client") — il connaît la personne.
- Vérifier le statut côté Suivi avant de répondre pour adapter le ton.
- Le tag de la commande de remplacement reste **`Service client`** (c'est
  bien un SAV, pas une dotation).

---

## 5. Memory feedback referenced by this doc

Persisted in the auto-memory :

- `feedback_sav_workflow.md` — Gorgias → Shopify draft → BigBlue pickup → response.
- `feedback_sav_draft_order_defaults.md` — discount 100 % SAV + shipping gratuit défaults.
- `feedback_gorgias_vs_instagram_tone.md` — vouvoiement for Gorgias, tutoiement for Instagram.
- `feedback_read_thread_before_draft.md` — always list messages before drafting.

---

## 6. See also

- [`archive/process_sav_shaker_manquant.md`](archive/process_sav_shaker_manquant.md) — legacy (promo shaker obsolète) mais contient la recette complète du code `[PRENOM]-SAV` (price_rule REST + GraphQL `combinesWith`) qui reste valide.
- [`archive/session_sav_2026-04-13.md`](archive/session_sav_2026-04-13.md) — original source of the rules above, plus the `search_tickets` fix details.
- [`process_create_codes.md`](process_create_codes.md) — runbook codes Shopify (affilié, dotation, crédit, SAV).
- [`process_create_orders.md`](process_create_orders.md) — runbook draft orders avec tags.
- [`reference_mcps.md`](reference_mcps.md) — tool signatures for `gorgias_mcp` and `shopify_mcp`.
