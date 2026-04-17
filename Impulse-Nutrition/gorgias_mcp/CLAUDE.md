# Gorgias MCP — Impulse Nutrition

> **Source de vérité pour TOUT travail service client** (tickets SAV email/chat/contact_form/Instagram/Facebook/WhatsApp-via-WAX) : **skill `/gorgias`** (niveau user). Protocole 8 étapes bloquant, loop-safe. Triggers : `/gorgias`, "check le SAV", "check les tickets", "SAV check", "passe SAV", etc.
>
> Référence humaine (scenarios détaillés, recette draft SAV, tags CA) : [`../knowledge/operations.md#sav--opérations-client`](../knowledge/operations.md#sav--opérations-client).
>
> Persona Antoine : [`personality.md`](./personality.md).
>
> ⚠️ **Persona côté SC = entité Impulse Nutrition**, vouvoiement formel, signature `Le service client Impulse Nutrition`. **JAMAIS signer "Antoine"** — même si c'est Antoine qui rédige. Le skill gère la règle automatiquement.

## Spécifique à ce sous-projet

### MCP Gorgias custom (refacto avril 2026)
- **Package modulaire** : `src/gorgias_mcp/` — entry point `python -m gorgias_mcp.server`
- **Auth** : variables d'env `GORGIAS_DOMAIN`, `GORGIAS_EMAIL`, `GORGIAS_API_KEY`
- **Base URL** : `https://{GORGIAS_DOMAIN}.gorgias.com/api`
- **HTTP client partagé** : `infra.common.http_mcp.MCPHttpClient` (retry 5xx, timeout, basic auth)
- **Tests** : `uv run pytest` (25 tests : views, slim, tools mockés via `responses`)
- **`search_tickets`** = lookup en cascade (id numérique → customer email → fallback substring sur view Inbox), pas un full-text search

### Filtrage par vues Gorgias
La V2 de l'API Gorgias **rejette `?status=` et `?channel=`** sur `/api/tickets` (400). Le filtrage natif passe par les vues serveur via `/api/views/{view_id}/items`.

`list_tickets` accepte 3 filtres équivalents :
- `status="open"|"closed"|"snoozed"|"unassigned"|"all"` → vue système (défaut : Inbox)
- `channel="email"|"contact_form"|"chat"|"help_center"` → vue canal
- `view_id=<int>` → override raw

Maps complètes dans `src/gorgias_mcp/views.py` (`SYSTEM_VIEWS`, `CHANNEL_VIEWS`, `USER_VIEWS`). Tool `list_views` les expose au runtime.

### Vues système principales
| Alias | view_id | Sens |
|---|---|---|
| `open` | 33360 | Inbox (ouverts non-spam non-snoozed) |
| `closed` | 33364 | Closed |
| `snoozed` | 33363 | Snoozed |
| `unassigned` | 33361 | Unassigned |
| `all` | 33362 | All (historique complet) |

### Vues canal
| Alias | view_id |
|---|---|
| `email` | 44348 |
| `contact_form` | 44386 |
| `chat` | 45597 |
| `help_center` | 44385 |

### Pull protocol
- Pass quotidien : `list_tickets(status="open", limit=50)` (Inbox).
- Recherche historique : `status="all"` ou `search_tickets(query)`.
- Jamais conclure "client pas trouvé" sans avoir essayé `search_tickets` puis `status="all"`.

> Note historique : avant le refacto, le filtrage était cassé côté API et il fallait pull 100 puis filtrer côté client. Incident 2026-04-13 (Amandine Laurent #52032892 ratée sur pull 30) à l'origine de l'ancienne règle "100 minimum" — levée depuis que les vues fonctionnent.

### Channels SAV (filtrage local après pull)
Tous les canaux SC convergent vers Gorgias :
- `email`, `chat`, `contact_form` (natifs)
- `instagram`, `facebook` (natifs)
- `WAX` tag = WhatsApp via l'outil WAX (push bidirectionnel automatique)
- `internal-note` = alertes BigBlue

### Tags prioritaires
`urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`

### Ignore
`[SPAM POSSIBLE]` subjects, `Réponse automatique` / `Automatic reply`, `closed` bounces.
