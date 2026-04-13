# LLM Context — Impulse Nutrition
> Generated: 2026-04-09 | Stack: Python MCP servers + Google Sheets + Shopify/Gorgias/BigBlue/Instagram/TikTok APIs
> To refresh: /codebase-index

---

## Stack
Python 3.10-3.12 (fastmcp/httpx) + TypeScript (TikTok MCP) + Google Sheets (service account)
Key deps: instagrapi, fpdf2, fastmcp, python-docx

---

## Directory Map

```
Impulse-Nutrition/
  .mcp.json                    — MCP server configs + credentials
  CLAUDE.md                    — Business context, pipeline, Sheet schema, all workflows
  LLM.md                       — This file
  generate_contract.py         — PDF contract generator (dotation/ambassadeur/paid)

  instagram_dm_mcp/            — Instagram DM MCP server + batch scripts
    src/mcp_server.py          — MCP tools (send_message, list_chats, etc.)
    src/logger.py              — Logging helper
    personality.md             — Antoine's tone guide
    CLAUDE.md                  — Detailed Sheet schema + DM workflow docs
    update_priorities.py       — Sync DM state -> col L
    audit_ambassadors.py       — Update bio/story/post counts (R, X, Y)
    run_campaign.py            — Send campaign DMs (col M)
    qualify_influencer.py      — Score profiles (GO/MAYBE/NO-GO)
    qualify_conversations.py   — Classify DM conversations
    veille_concurrents.py      — Competitor intelligence
    refresh_analyses.py        — Write KPI formulas to Analyses tab
    create_session.py          — Create/refresh Instagram session
    recover_updates.py         — Recover failed sheet updates
    send_promo_20pct.py        — Send promo messages
    migrate_suivi_amb.py       — One-time sheet migration
    resolve_usernames.py       — Resolve user IDs to usernames

  shopify_mcp/                 — Shopify MCP server (REST Admin API)
    src/mcp_server.py          — Draft orders, discounts, customer/product search

  gorgias_mcp/                 — Gorgias MCP server (customer support)
    src/mcp_server.py          — Tickets, messages, customers
    personality.md             — Customer service tone guide

  bigblue_mcp/                 — BigBlue MCP server (fulfillment/logistics)
    src/mcp_server.py          — Orders, tracking, inventory, support tickets

  templates/                   — DM message templates
    pitch_initial.md           — First contact
    relance.md                 — Follow-up
    commande_validee.md        — Order confirmation
    demande_infos.md           — Info request
    promo.md                   — Promo messages
    dm_response_guide.md       — Response decision tree
    real_response_examples.md  — Real conversation examples
    message_types.json         — Structured message library
    product_catalog.json       — Product list with prices

  docs/                        — Process documentation
    process_dm_check_and_onboarding.md
    process_sav_shaker_manquant.md
    plan_bigblue_claims_api.md
    produits.md

  KolSquare/                   — KolSquare API research (Firecrawl scrapes)
```

---

## MCP Servers

```
instagram_dms     Python (instagrapi)    send/list DMs, user info, media
instagram_veille  Same code, antman.lass Monitoring account
shopify_orders    Python (REST API)      Draft orders, discounts, search
gorgias           Python (REST API)      Tickets, messages, customers
bigblue           Python (REST API)      Orders, tracking, inventory, claims
google_sheets     Third-party (uvx)      Read/write spreadsheet cells
tiktokshop        TypeScript (Node)      Orders, products, CS conversations
shopify           Built-in Claude Code   Read-only products/orders/customers
```

---

## External: TikTok MCP (separate git repo)

Path: `/Users/antoinechabrat/Documents/SmallProject/Tiktok/MCP-TikTokShop/`
Stack: TypeScript + @modelcontextprotocol/sdk + HMAC-SHA256 signing
Tools: list_orders, get_order_detail, list_products, get_product_detail,
       list_conversations, read_conversation, reply_to_conversation

API endpoints:
  order/202309/orders/search             POST  (query params)
  order/202309/orders                    GET   (ids in query)
  product/202309/products/search         POST  (query params)
  product/202309/products                GET   (ids in query)
  customer_service/202309/conversations  GET   (page_size, page_token)
  customer_service/202309/conversations/{id}/messages  GET/POST

---

## Google Sheet — "InfluenceManager"

ID: 1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4

Tabs:
  Suivi_Amb   Main ambassador tracking (~413 rows)
  Suivi_Paid  Paid contracts (rows 4-44)
  Suivi_Dot   Dotation accounts (~20)
  Analyses    KPI formulas (refresh_analyses.py)

### Suivi_Amb key columns
  I=username  J=statut  K=action  L=priorite
  N=code  O=utilisations  P=credit_used  Q=lien_affilie
  R=bio  S=sport  T=sponsor_concurrent  U=followers  W=engagement
  X=nb_stories  Y=nb_posts  AA=nom  AB=prenom  AC=mail  AD=tel  AE=adresse

### Pipeline (col J)
  In-cold -> In-hot -> A recontacter / A rediscuter -> Contacter manager -> Produits envoyes -> Out

### Priorities (col L)
  high    Influencer's last message unanswered
  medium  Our last message read, waiting for reply
  good    All OK, no action needed

---

## Key Workflows

### SAV (Gorgias -> Shopify -> BigBlue)
  1. Read Gorgias ticket -> identify issue
  2. Find original order on Shopify
  3. Create draft order (variants + customer), tag "Service client"
  4. Apply 100% discount + free shipping
  5. Complete draft order
  6. Update BigBlue shipping_method + pickup_point if needed
  7. Reply on Gorgias

### DM Priority Check
  1. list_chats(100) -> cross-ref Sheet col I
  2. Check last sender per thread (is_sent_by_viewer)
  3. Apply priority rules -> update col L

### Ambassador Onboarding
  1. Qualify profile (qualify_influencer.py)
  2. Pitch via DM -> exchange -> call
  3. Create Shopify draft order + affiliate code
  4. Send code + link via DM
  5. Update Sheet: J=Produits envoyes, N=code

---

## Auth Methods

  Instagram      Session JSON via instagrapi
  Shopify        OAuth client credentials (~24h token)
  Gorgias        HTTPBasicAuth (email + API key)
  BigBlue        Bearer token
  Google Sheets  Service account JSON
  TikTok Shop    HMAC-SHA256 signed requests + access token

---

## Conventions
- Tutoiement with ambassadors, vouvoiement on Gorgias
- Signature: "Sportivement, Antoine"
- All DM drafts require explicit "go" before sending
- All external submissions (tickets, forms) require explicit "go"
- Timestamps Instagram: microseconds (divide by 1_000_000)
- Sheet dates: always absolute, never relative
- Clubs/orgs/paid contracts -> never add to Suivi_Amb, flag to Antoine
