# Reference — MCP Servers

The project exposes 4 custom MCP servers + 3 third-party ones configured in
[`../.mcp.json`](../.mcp.json). This doc is the cheat-sheet — full signatures
and examples.

> Updated : 2026-04-13. Docstrings and setup instructions in Phase 2 will
> expand this doc.

---

## Setup (environment variables)

All credentials live in `.env` at the repo root (git-ignored). Copy
`.env.example` and fill in.

```bash
cp .env.example .env
# edit .env with your credentials
```

| Variable | Used by | Required |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_PATH` | `common.google_sheets` | ✓ (or default `~/.config/google-service-account.json`) |
| `INSTAGRAM_USERNAME` | `instagram_dm_mcp`, scripts | ✓ |
| `INSTAGRAM_PASSWORD` | `instagram_dm_mcp`, scripts | ✓ |
| `INSTAGRAM_VEILLE_USERNAME` | veille scripts | ✗ |
| `INSTAGRAM_VEILLE_PASSWORD` | veille scripts | ✗ |
| `GORGIAS_DOMAIN` | `gorgias_mcp` | ✓ |
| `GORGIAS_EMAIL` | `gorgias_mcp` | ✓ |
| `GORGIAS_API_KEY` | `gorgias_mcp` | ✓ |
| `SHOPIFY_DOMAIN` | `shopify_mcp`, scripts | ✓ |
| `SHOPIFY_CLIENT_ID` | `shopify_mcp` (OAuth) | ✓ |
| `SHOPIFY_CLIENT_SECRET` | `shopify_mcp` (OAuth) | ✓ |
| `BIGBLUE_EMAIL` | `bigblue_mcp` | ✓ |
| `BIGBLUE_PASSWORD` | `bigblue_mcp` | ✓ |
| `BIGBLUE_SESSION_TOKEN` | `bigblue_mcp` | ✓ (refresh via `trigger_token_refresh`) |
| `TIKTOK_SHOP_ACCESS_TOKEN` | `tiktokshop` | ✓ (rotates ~15 days) |

---

## 1. `bigblue_mcp` — Fulfillment

Custom Python MCP. gRPC-Web bridge to BigBlue's admin UI API. No public REST.

**12 tools**:

| Tool | Purpose |
|---|---|
| `list_orders` | List orders (paginated, by status) |
| `get_order` | Order detail (line items, shipping, tracking) |
| `update_order` | Mutate order state (pickup point, address) |
| `cancel_order` | Cancel before fulfillment |
| `get_tracking` | Tracking URL for customer (Chronopost / Mondial Relay) |
| `list_inventories` | Stock per SKU |
| `list_support_tickets` | Helpdesk ticket list — ⚠ **BROKEN** |
| `get_support_ticket` | Ticket detail — ⚠ **BROKEN** |
| `create_support_ticket` | File a claim — ⚠ **BROKEN** — **messages in French** |
| `reply_to_support_ticket` | Reply on a ticket — ⚠ **BROKEN** — **messages in French** |
| `trigger_token_refresh` | Force OAuth token refresh |
| `update_session_token` | Manual session token override |

### Known limitations
- ⚠ **Helpdesk tools (4) likely broken** (interview 2026-04-13). BigBlue does not expose a public REST API for claims; the current implementation reverse-engineers the gRPC-Web admin UI calls and parsing is fragile. **TODO** : debug avec `/debug` au prochain incident, ou fallback Playwright.
- Protobuf string extraction (`_extract_strings`) is a **regex over UTF-8 bytes**, fragile if BigBlue changes their schema.
- All support ticket messages must be **in French** per BigBlue SOP.

---

## 2. `gorgias_mcp` — Customer Support

Custom Python MCP. REST API to Gorgias.

**12 tools**:

| Tool | Purpose |
|---|---|
| `list_tickets` | List tickets (filter by channel/status/tag) |
| `get_ticket` | Ticket detail |
| `list_ticket_messages` | Full message thread for a ticket |
| `search_tickets` | Custom search (customer lookup + substring fallback — the native `/search` endpoint returns 405) |
| `reply_to_ticket` | Reply on a ticket — **vouvoiement formel** |
| `close_ticket` | Close ticket |
| `assign_ticket` | Reassign to a team member |
| `get_ticket_stats` | KPI summary |
| `list_tags` | All tags |
| `list_customers` | List customers |
| `get_customer` | Customer detail |
| `search_customers` | Search by email / name / phone |

### Known limitations
- Native `/api/search` returns `405 Method Not Allowed`. `search_tickets`
  uses a customer-lookup + substring fallback (see
  `knowledge/archive/session_sav_2026-04-13.md` §3.1).
- All reply text must be **vouvoiement formel** (see `gorgias_mcp/personality.md`).

---

## 3. `shopify_mcp` — Admin API

Custom Python MCP. REST + GraphQL via OAuth client_credentials. Used for
draft orders (SAV), customer lookup, product catalog.

**15 tools**:

| Tool | Purpose |
|---|---|
| `list_orders` | List orders |
| `search_orders` | Search orders by query string (e.g. `IMP6923`) |
| `get_order` | Order detail |
| `list_draft_orders` | List draft orders |
| `get_draft_order` | Draft detail |
| `create_draft_order` | **Create SAV draft** — see defaults below |
| `update_draft_order` | Update draft (note: cannot change `line_items`, delete+recreate instead) |
| `delete_draft_order` | Delete a draft |
| `complete_draft_order` | Convert draft to order |
| `create_discount_code` | Create `[PRENOM]-SAV` 100 % code on specific products |
| `get_customer` | Customer detail |
| `search_customers` | Search customers |
| `search_products` | Search products by query |
| `get_product` | Product detail |
| `get_product_variants` | Variants for a product |

### SAV draft order defaults (mandatory)

For **any replacement draft** (missing item, blocked delivery, returned-to-sender) :

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
  "note": "<brief context: original order ref + reason + goodwill additions>"
}
```

See [`process_sav_unified.md`](process_sav_unified.md) for the full flow.

---

## 4. `instagram_dm_mcp` — Instagram DMs

Custom Python MCP wrapping `instagrapi`. 26 tools — the largest.

### Session
Session stored in `instagram_dm_mcp/{username}_session.json` (gitignored).
Refresh via `python instagram_dm_mcp/create_session.py`.

Two accounts:
- **`impulse_nutrition_fr`** — main account (DMs, campaigns).
- **`antman.lass`** — veille account (competitor monitoring, read-only).

### Tool groups

**Chats / threads**
- `list_chats(amount=100, compact=True)` — list inbox.
- `list_pending_chats(amount=50, compact=True)` — pending/message requests.
- `list_messages(thread_id, amount=50, compact=True)` — thread messages.
- `list_media_messages(thread_id)` — media-only messages.
- `search_threads(query)` — search by participant.
- `get_thread_by_participants(user_ids)` — thread for a set of users.
- `get_thread_details(thread_id)` — full thread metadata.
- `mark_message_seen`, `mute_conversation`, `delete_message`.

**Messaging**
- `send_message(username, message)` — send DM.
- `send_photo_message(username, path)` — send image.
- `send_video_message(username, path)` — send video.

**Media**
- `get_media_info(media_pk)`.
- `download_media_from_message(thread_id, message_id)`.
- `download_shared_post_from_message(thread_id, message_id)`.
- `like_media(media_pk)`.

**Users**
- `get_user_info(username)`.
- `get_user_id_from_username(username)`.
- `get_username_from_user_id(user_id)`.
- `get_user_followers(user_id, amount=50)`.
- `get_user_following(user_id, amount=50)`.
- `get_user_posts(user_id, amount=12)`.
- `get_user_stories(user_id)`.
- `check_user_online_status(user_id)`.
- `search_users(query)`.

### Compact mode
By default, `list_messages`, `list_chats`, `list_pending_chats`,
`get_thread_details` return compact payloads :
`id`, `user_id`, `timestamp`, `text`, `item_type`, `is_sent_by_viewer`,
`shared_post_url`. Pass `compact=False` for full payload (debug, media
download).

### Item types observed
`text`, `voice_media`, `raven_media`, `media_share`, `xma_reel_mention`,
`link`, `placeholder`. See the `_compact_message` helper for the mapping.

### Rate limits
- Between read calls : 2–5 s.
- Between send calls : 5–10 s.
- Batch of 10 reads : +15–30 s.
Use `common.instagram_client.sleep_random(min, max)`.

---

## 5. Third-party MCPs configured in `.mcp.json`

| MCP | Purpose | Status |
|---|---|---|
| `google_sheets` | Read/write spreadsheet (also used by scripts via `gspread`) | ✓ OK |
| `tiktokshop` | TikTok Shop orders / products / customer service / reviews | ⚠ Partiel — voir détail ci-dessous |
| `shopify` | Official Shopify Storefront MCP (used for customer/order lookup with less auth friction) | ✓ OK |

### TikTok Shop — détail outils (smoke-tested + patched 2026-04-13)

| Tool | Status |
|---|---|
| `list_orders` / `get_order_detail` | ✓ OK (894 commandes en live, payload complet) |
| `list_products` / `get_product_detail` | ✓ OK (41 produits actifs avec stock par warehouse) |
| `list_conversations` / `read_conversation` | ✓ OK |
| `reply_to_conversation` | ✓ **OK après patch 2026-04-13** — voir détail ci-dessous |
| `list_reviews` / `reply_to_review` | ❌ **NOT SUPPORTED — pas d'endpoint public** |

#### Patch `reply_to_conversation` (2026-04-13) — 2 bugs enchaînés

Le MCP `sendMessage` dans `src/api/conversations.ts` avait **deux bugs
cumulés** qui ont été corrigés après test empirique direct contre l'API
live (POST HTTPS avec signature HMAC-SHA256 reconstituée en Python).

**Bug 1** — `45101003: invalid conv_short_id`
Le code passait `conversation_id` dans le body alors que TikTok l'attend
uniquement dans l'URL path. Le champ body était interprété comme un
*short* conv_id (format différent). **Fix** : supprimer le champ du body.

**Bug 2** — `45101001: input params err`
Une fois le bug 1 corrigé, le champ `content` envoyé comme texte brut
était rejeté. TikTok stocke les messages comme des *payloads typés*
(`TEXT` / `IMAGE` / `PRODUCT_CARD` / ...) où `content` est le payload
sérialisé du type choisi. Pour `type: "TEXT"`, `content` doit donc être
une JSON-string `{"content": "<texte>"}`. Observation tirée de la shape
des messages retournés par `read_conversation`, puis **confirmée par un
POST direct** qui a renvoyé `code:0, Success, message_id:7628369547846469142`.

**Fix final** (dans `sendMessage`) :
```typescript
client.post(
  `customer_service/202309/conversations/${conversationId}/messages`,
  {},
  {
    type: "TEXT",
    content: JSON.stringify({ content }),  // ← wrap obligatoire
  }
);
```

**Build** : `cd /Users/antoinechabrat/Documents/SmallProject/Tiktok/MCP-TikTokShop && npm run build`
**Activation** : restart Claude Code (les MCP servers sont chargés au lancement, pas hot-reloadés).
**Test réel** : 1er message delivered à `qsroyale` (conv `7626845579553653014`) via POST direct → `{code:0, message:"Success"}`. Visible dans `read_conversation`.

#### `list_reviews` / `reply_to_review` — NOT SUPPORTED

Retournent `36009009: Invalid path`. Après investigation (lecture du MCP
source + recherche docs TikTok Partner Center + cross-ref avec le client
de référence `EcomPHP/tiktokshop-php`) : **l'API publique TikTok Shop n'expose
pas d'endpoint de gestion des reviews**. EcomPHP, qui est le client PHP le
plus mature, n'implémente aucune ressource `Review` et n'a aucun endpoint
review dans `Product.php`. Le path `product/202309/reviews/search` utilisé
par le MCP a été inventé ou est obsolète.

**→ Les reviews TikTok se gèrent exclusivement dans le Seller Center web.**
Il n'existe pas de solution API à ce jour. Ne pas utiliser ces 2 outils
du MCP — à terme, les retirer du tool registry ou les remplacer par un
handler qui renvoie immédiatement un message clair.

**Volume TikTok Shop** : ~894 commandes total — **significatif**, à traiter au même niveau que Shopify côté SAV. Voir [`process_sav_unified.md`](process_sav_unified.md) pour le workflow Gorgias (channels) — TikTok messages devraient à terme remonter dans Gorgias via une intégration similaire à WAX, ou être traités directement via `tiktokshop` MCP.

Full MCP list and env vars are in `.mcp.json`.

---

## 6. Statut global des MCPs (interview 2026-04-13, smoke tests inclus)

| MCP | Status | Action |
|---|---|---|
| `bigblue_mcp` (orders, tracking, inventory) | ✓ OK | — |
| `bigblue_mcp` (helpdesk : `*_support_ticket`) | ⚠ BROKEN | TODO debug — endpoint gRPC-Web fragile |
| `gorgias_mcp` | ✓ OK (avec fallback `search_tickets`) | — |
| `shopify_mcp` (orders, draft orders, products) | ✓ OK + compact mode (Phase 2026-04-13) | — |
| `instagram_dm_mcp` | ✓ OK (rate limits à respecter) | — |
| `tiktokshop` (orders, products, conversations, reply_to_conversation) | ✓ OK (reply patché 2026-04-13) | — |
| `tiktokshop` (reviews : `list_reviews` / `reply_to_review`) | ❌ NOT SUPPORTED | Pas d'endpoint API public — Seller Center uniquement |
