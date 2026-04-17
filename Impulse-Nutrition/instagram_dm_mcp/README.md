# Instagram DM MCP — Impulse Nutrition

Fork interne du MCP `trypeggy/instagram_dm_mcp`, spécialisé pour la gestion des DMs ambassadeurs Impulse Nutrition.

**Source de vérité pour toute utilisation** : [`CLAUDE.md`](./CLAUDE.md) (persona, rate limiting, sessions) et le skill user-level `/instagram-dm` (protocole bloquant 9 étapes).

## Structure

| Chemin | Rôle |
|---|---|
| `src/instagram_dm_mcp/` | Serveur FastMCP — 26 tools exposés à Claude (send, threads, users, posts, media, misc) |
| `scripts/<domain>/` | Jobs CLI batch : `kolsquare/`, `qualify/`, `veille/`, `ambassadors/`, `campaign/`, `debug/`, `setup/` |
| `data/` | Runtime (sessions, logs, progress, downloads, conversations) — gitignored |

> Tone guide Antoine : [`../knowledge/voice/personality.md`](../knowledge/voice/personality.md) (régénéré via `../infra/scripts/extract_tone.py`).

## Lancer

```bash
# Serveur MCP (lancé automatiquement via .mcp.json par Claude)
uv run python -m instagram_dm_mcp.server

# Un script batch
uv run python scripts/ambassadors/audit.py --limit 10
```

Première connexion : `uv run python scripts/setup/create_session.py`.
