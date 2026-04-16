# LLM Context — Impulse Nutrition

> Refreshed 2026-04-16 (repo reorg: `tools/` + `knowledge/`).
> Stack: Python MCP servers + Google Sheets/Drive + Shopify/Gorgias/BigBlue/Instagram/TikTok APIs + Shopify Functions (TS)
> Refresh the codebase graph: `/codebase-memory`

---

## Purpose
Factory workspace (not an app) for the **Influence Manager** of Impulse Nutrition. Code = a collection of **MCP servers + CLI scripts + shared library** that automate the ambassador pipeline: Instagram DMs, Google Sheets tracking, Shopify SAV/draft orders, BigBlue fulfillment, Gorgias support tickets, contract generation, benchmarks, and — since 2026-04-13 — a local DM archive used to auto-regenerate the tone guide.

---

## File Tree (key paths)

```
Impulse-Nutrition/
├── CLAUDE.md                           # project rules + pointer to knowledge/INDEX.md
├── LLM.md                              # this file
├── .mcp.json                           # MCP server registry (committed, shared creds)
├── .env.example                        # env var template
│
├── bigblue_mcp/src/mcp_server.py       # BigBlue fulfillment MCP (gRPC-Web) — 12 tools
├── gorgias_mcp/src/mcp_server.py       # Gorgias support MCP (REST) — 12 tools
├── shopify_mcp/src/mcp_server.py       # Shopify admin MCP (REST + GraphQL) — 15 tools
├── instagram_dm_mcp/                   # Instagram DM MCP + ambassador pipeline scripts — 26 MCP tools
│   ├── src/mcp_server.py
│   ├── personality.md                  #   auto-regen by infra/scripts/extract_tone.py
│   ├── audit_ambassadors.py            #   uses infra/common/google_sheets
│   ├── qualify_conversations.py        #   uses infra/common/dm_classifier
│   ├── qualify_influencer.py           #   GO/MAYBE/NO-GO scoring
│   ├── run_campaign.py                 #   DM send campaign
│   ├── filter_kolsquare.py             #   KolSquare CSV → scored prospects (uses tools/veille_kolsquare/)
│   ├── kolsquare_to_sheet.py           #   Filtered prospects → Suivi_Amb tab
│   ├── kolsquare_send_batch.py         #   Batch DM pitch to KolSquare targets
│   ├── refresh_analyses.py             #   KPI formulas → Analyses tab
│   ├── resolve_usernames.py            #   brand → @handle resolver
│   ├── update_priorities.py
│   ├── veille_concurrents.py
│   ├── create_session.py               #   Instagram login + challenge handler
│   └── CLAUDE.md
│
├── tiktok_sav/                         # TikTok Shop SAV pipeline (sav.py + T0-T9 templates)
│
├── infra/                              # plumbing — shared library, scripts, private data
│   ├── common/                         #   Python package imported via `from infra.common.*`
│   │   ├── google_sheets.py            #     SUIVI_AMB_COLS / SUIVI_DOT_COLS / SUIVI_PAID_COLS / VEILLE_COLS
│   │   ├── google_drive.py             #     Drive client for contract sync
│   │   ├── instagram_client.py         #     get_ig_client() + sleep_random()
│   │   ├── dm_classifier.py            #     QUESTION_SIGNALS / OK_SIGNALS / classify_last_message
│   │   └── http_mcp.py                 #     MCPHttpClient base + error_payload() + safe_call()
│   ├── scripts/                        #   one-shot transverses (gitignored outputs go to infra/data)
│   │   ├── download_conversations.py   #     bulk DL tracked ambassador DMs → infra/data/conversations/
│   │   ├── extract_tone.py             #     regen instagram_dm_mcp/personality.md from corpus
│   │   ├── extract_response_templates.py
│   │   └── generate_contract.py        #     PDF contract generator (fpdf2)
│   ├── contracts/                      #   gitignored — PDFs signés + Drive sync (PII)
│   └── data/
│       └── conversations/              #   gitignored — private DM archive
│
├── knowledge/                          # "c'est quoi Impulse" — static business reference
│   ├── INDEX.md                        #   top-level navigation
│   ├── business/contract_types.md
│   ├── catalog/                        #   produits.md, shopify_catalog.md
│   ├── voice/                          #   templates.yaml (source of truth DM), dm_decision_tree.md
│   ├── process/                        #   sav_unified, create_codes, create_orders, calculate_credits, ...
│   ├── reference/                      #   mcps, sheet_schema, skills_usage, setup_onboarding
│   ├── archive/                        #   legacy templates + historic case studies
│   └── assets/                         #   images (logo, visuels, screenshots benchmark/bigblue)
│
└── tools/                              # workshop : one-off projects
    ├── benchmark_abonnement/           #   ex benchmark/ — decks v1..v5, rentability, marques
    ├── veille_kolsquare/               #   KolSquare CSV + filtering rules
    └── shaker_450ml/                   #   standalone Shopify app: free shaker gift (gitignored)
```

---

## Shared Library — `common/`

| Module | Key exports |
|---|---|
| `common.google_sheets` | `SHEET_ID`, `get_gspread_client()`, `get_worksheet(tab)`, `get_data_rows(ws)`, `SUIVI_AMB_COLS`, `SUIVI_DOT_COLS`, `SUIVI_PAID_COLS`, `VEILLE_COLS`, `col_letter_to_idx()`, `idx_to_col_letter()` |
| `common.instagram_client` | `get_ig_client(account="impulse"\|"veille")`, `sleep_random(min, max)` |
| `common.dm_classifier` | `QUESTION_SIGNALS`, `OK_SIGNALS`, `classify_last_message(text, is_from_us)` |
| `common.http_mcp` | `MCPHttpClient` class (base for REST MCPs), `error_payload(tool, exc, params)`, `safe_call(tool, fn, *a, **kw)` |

All scripts under `instagram_dm_mcp/` (the 8 still-active ones) now import from `common/` via the `sys.path.insert` bootstrap.

---

## MCP Servers

### `bigblue_mcp/src/mcp_server.py` — 12 tools
gRPC-Web bridge. New since refactor:
- `_err(tool, exc)` helper logs + returns `{error, error_type, tool}`.
- 6 silent swallows replaced with `_err(...)` calls.
- `BIGBLUE_EMAIL` and `AUTH0_CLIENT_ID` moved to env vars (with defaults).

### `gorgias_mcp/src/mcp_server.py` — 12 tools
Untouched in this refactor (the search_tickets fix from 2026-04-13 was preserved).

### `shopify_mcp/src/mcp_server.py` — 15 tools
`create_draft_order` docstring rewritten with the canonical SAV example (discount 100 % + shipping gratuit + tag `Service client`) and the `update_draft_order` line-item limitation noted. `search_orders` docstring clarified.

### `instagram_dm_mcp/src/mcp_server.py` — 26 tools
Bare `except:` on line 476 replaced with a logged `except Exception`. Other 27 `except Exception` blocks still return structured errors (unchanged).

---

## Scripts

### Ambassador pipeline (existing, rewired to `common/`)
| Script | Input | Sheet tab / cols touched |
|---|---|---|
| `audit_ambassadors.py` | tracked usernames | `Suivi_Amb` : `SUIVI_AMB_COLS["bio"]`, `followers_k`, `date_premier_contact`, `nb_story`, `nb_post` |
| `update_priorities.py` | DM threads | `Suivi_Amb` : `priorite` (L) |
| `run_campaign.py` | `Suivi_Amb` col M | `Suivi_Amb` : `campagne` (M) |
| `qualify_conversations.py` | DM threads | JSON progress file, uses `common.dm_classifier` |
| `qualify_influencer.py` | usernames | `Qualification` tab |
| `veille_concurrents.py` | competitors | `VeilleConcu` tab |
| `refresh_analyses.py` | — | `Analyses` tab (formulas only) |
| `resolve_usernames.py` | brand names | `VeilleConcu` col B |

### Conversation archive (new in `scripts/`)
| Script | Purpose | Writes |
|---|---|---|
| `infra/scripts/download_conversations.py` | Bulk DL DMs for every tracked ambassador | `infra/data/conversations/<user>.json` + `_index.json` + `_progress.json` |
| `infra/scripts/extract_tone.py` | Stat analysis → tone guide | `instagram_dm_mcp/personality.md.generated` (safe) or `personality.md` (--overwrite) |
| `infra/scripts/extract_response_templates.py` | Curated anonymized examples | `knowledge/archive/templates_racine/real_response_examples.md` |

Flags : `--dry-run` on all three, `--limit N` on download, `--force` on download, `--overwrite` on extract_tone.

---

## Shopify Extension — Free Shaker 450ml

Unchanged. `shaker-450ml-gratuit/` : two Shopify Functions + a cloud function webhook.

---

## Architecture Notes

- **No single app** — `bigblue_mcp`, `gorgias_mcp`, `shopify_mcp`, `instagram_dm_mcp` each have their own `pyproject.toml` with hatch build. Scripts at root use a bootstrapped `sys.path` to import from `common/`.
- **Google Sheets is the system of record**. Column semantics live in `infra/common/google_sheets.py` and are documented in `knowledge/reference/sheet_schema.md` — update both together.
- **Four partnership models** (Affiliation, Dotation S/M/L, Paid) — see `knowledge/business/contract_types.md`. Each routes to a different Sheet tab.
- **SAV draft order flow** : `knowledge/process/sav_unified.md` is the canonical runbook. Mandatory defaults on every replacement : `applied_discount` 100 % + `shipping_line` gratuit + `tags: Service client`.
- **Conversation archive is private** : `infra/data/conversations/` is gitignored. Scripts anonymize before writing anything to `personality.md` or `real_response_examples.md`.

---

## Recent Architectural Changes (2026-04-13 refactor)

- **`common/`** created (5 modules, replaces duplication across 8 scripts).
- **`docs/` reorganized** : INDEX + 3 reference docs + unified SAV process + archive.
- **`scripts/`** folder created for the new conversation-archive pipeline.
- **`.env.example`** template added; scripts use `os.getenv()` consistently.
- **4 dead files deleted** : `GEMINI.md`, `send_promo_20pct.py`, `migrate_suivi_amb.py`, `recover_updates.py`.
- **3 column bugs fixed** : `row[27]` → `prenom`, `row[32]` → `id_influ`, `row[19]` → `sponsor` (CLAUDE.md map had drifted).
- **BigBlue MCP** : 6 silent swallows now logged + structured; email/Auth0 ID moved to env.
- **Instagram MCP** : bare `except:` on line 476 fixed + logged.
- **Shopify MCP** : `create_draft_order` and `search_orders` docstrings rewritten with SAV examples.

---

## Pointers

- `knowledge/INDEX.md` — navigation entry point
- `knowledge/business/contract_types.md` — Affiliation / Dotation S/M/L / Paid models
- `knowledge/reference/sheet_schema.md` — canonical column map (mirrors `infra/common/google_sheets.py`)
- `knowledge/reference/mcps.md` — 65-tool cheat-sheet
- `knowledge/process/sav_unified.md` — SAV workflow
- `knowledge/process/conversation_archive.md` — archive + tone extraction runbook
- `gorgias_mcp/personality.md` — Gorgias tone (vouvoiement formel)
- `instagram_dm_mcp/personality.md` — Instagram tone (tutoiement, auto-regenerated)
