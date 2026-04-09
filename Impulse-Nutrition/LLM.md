# Impulse Nutrition — Codebase Index

## Structure

```
Impulse-Nutrition/
├── .mcp.json                  # MCP servers config (instagram_dms, instagram_veille, shopify_orders, google_sheets)
├── CLAUDE.md                  # Business context, pipeline, Sheet schema, workflows
├── LLM.md                     # This file — codebase map
├── generate_contract.py        # PDF contract generator (dotation/ambassadeur/paid)
│
├── instagram_dm_mcp/           # Instagram DM MCP server (instagrapi)
│   ├── src/mcp_server.py       # Tools: send_message, list_chats, list_messages, get_user_info, etc.
│   ├── CLAUDE.md               # Detailed Sheet schema + workflow docs
│   ├── personality.md          # Antoine's tone guide + message templates
│   ├── update_priorities.py    # Sync DM state → col L (high/medium/good)
│   ├── audit_ambassadors.py    # Update bio/story/post counts (cols R, X, Y)
│   ├── run_campaign.py         # Send campaign DMs (reads col M, sends, marks OK/SKIP)
│   ├── qualify_influencer.py   # Score Instagram profiles (GO/MAYBE/NO-GO)
│   ├── veille_concurrents.py   # Competitor intelligence via Instagram
│   ├── refresh_analyses.py     # Write KPI formulas to Analyses tab
│   └── create_session.py       # Create/refresh Instagram session
│
├── shopify_mcp/                # Shopify MCP server (REST API, OAuth client credentials)
│   └── src/mcp_server.py       # Tools: create/complete_draft_order, search_products/customers, create_discount_code
│
├── gorgias_mcp/                # Gorgias MCP server (customer support tickets)
│   └── src/mcp_server.py       # Tools: list/reply/close_ticket, search_customers
│
├── bigblue_mcp/                # BigBlue MCP server (fulfillment/logistics)
│   └── src/mcp_server.py       # Tools: get_order, list_orders, get_tracking, cancel_order
│
├── templates/                  # DM message templates
│   ├── pitch_initial.md        # First contact
│   ├── relance.md              # Follow-up
│   ├── commande_validee.md     # Order confirmation
│   ├── dm_response_guide.md    # Response decision tree
│   ├── message_types.json      # Structured message library
│   └── product_catalog.json    # Product list with prices
│
├── contracts/                  # Generated PDF contracts
│   └── drive/                  # Signed contracts from Google Drive (.pdf, .docx)
│
└── assets/
    └── logo_impulse.jpeg       # Brand logo
```

## MCP Servers

| Name | Type | Key Tools |
|------|------|-----------|
| `instagram_dms` | Custom (instagrapi) | send_message, list_chats, list_messages, get_user_info, search_users |
| `instagram_veille` | Same code, different account (antman.lass) | Same tools, monitoring account |
| `shopify_orders` | Custom (REST API) | create_draft_order, update_draft_order, complete_draft_order, search_products, search_customers |
| `gorgias` | Custom (REST API) | list_tickets, reply_to_ticket, close_ticket, search_tickets |
| `bigblue` | Custom (REST API) | get_order, list_orders, update_order, get_tracking, cancel_order |
| `google_sheets` | Third-party (uvx) | get_sheet_data, update_cells, batch_update_cells, find_in_spreadsheet |
| `shopify` (marketplace) | Built-in Claude Code | get-products, get-orders, get-customers (read-only, no draft orders) |

## Google Sheet — "InfluenceManager"

**ID** : `1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4`

### Key Tabs
- **Suivi_Amb** : Main ambassador tracking (~413 rows). Cols: I=username, J=statut, K=action, L=priorité, N=code, O=utilisations
- **Suivi_Paid** : Paid contracts. Data rows 4-44. Cols: W=fixe, AD=dotation, AH-AL=livrables
- **Suivi_Dot** : Dotation accounts (~20)
- **Analyses** : KPI formulas (written by refresh_analyses.py)

### Pipeline (col J)
```
In-cold → In-hot → A recontacter / A rediscuter → Contacter manager → Produits envoyés → Out
```

### Priorities (col L)
- **high** : Influencer's last message unanswered
- **medium** : Our last message, waiting for reply
- **good** : All OK, no action needed

## Key Workflows

### SAV (Gorgias → Shopify → BigBlue)
1. Read Gorgias ticket → identify missing/wrong products
2. Find original order on Shopify (shipping method, customer)
3. Create draft order (variant_ids + customer_id), tag "Service client"
4. Apply 100% discount + "Expédition gratuite"
5. Complete draft order (mark as paid)
6. Update BigBlue: set shipping_method + pickup_point if point relais
7. Reply on Gorgias

### DM Priority Check
1. list_chats(100) → cross-ref with Sheet col I
2. For each tracked thread: check last sender (is_sent_by_viewer)
3. Apply priority rules → update col L

### Campaign Send
1. Mark targets in col M with campaign name
2. run_campaign.py sends DMs, marks M = "OK" or "SKIP"

### Ambassador Onboarding
1. Qualify profile (qualify_influencer.py)
2. Pitch via DM → exchange → call
3. Create order (Shopify draft) + affiliate code (Affiliatly manual)
4. Send code + link via DM
5. Update Sheet: J=Produits envoyés, N=code

### BigBlue API -- endpoints disponibles
L'API BigBlue est purement logistique. Pas de tickets/claims/retours/support via API.
- Orders : CreateOrder, GetOrder, UpdateOrder, CancelOrder, ListOrders
- Tracking : ListTrackings
- Products : ListProducts, GetProduct, CreateProduct, UpdateProduct
- Inventory : ListInventories
- Bundles : ListBundles, CreateBundle

Pour ouvrir un ticket SAV BigBlue : passer par le dashboard web.

## Accounts & Auth

| Service | Auth Method |
|---------|-------------|
| Instagram (impulse_nutrition_fr) | Session JSON via instagrapi |
| Instagram (antman.lass) | Session JSON via instagrapi |
| Shopify | OAuth client credentials (token ~24h) |
| Gorgias | HTTPBasicAuth (email + API key) |
| BigBlue | Bearer token |
| Google Sheets | Service account JSON |

## Contacts
- **Puls Agency** : marie@puls-agency.com
- **Versacom** : simon@versacom.eu
- **Fraich Touch** : gael@fraichtouch.com
- **HCS interne** : pgautier@havea.com (commandes dotation)
