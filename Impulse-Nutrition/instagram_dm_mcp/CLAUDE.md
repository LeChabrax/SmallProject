# Instagram DM MCP -- Impulse Nutrition

Voir le contexte complet dans le **CLAUDE.md à la racine** du projet (`../CLAUDE.md`).

## Spécifique à ce MCP

### Session Instagram
- Session stockée dans `*_session.json` (gitignored)
- Si expirée : relancer `python create_session.py`
- Deux comptes : `impulse_nutrition_fr` (principal) + `antman.lass` (veille)

### Rate limiting
Les appels Instagram sont sensibles au rate limiting. Espacer les appels si nécessaire.

### Compact mode (depuis avril 2026)
Les outils `list_messages`, `list_chats`, `get_thread_details` ont un param `compact=True` par défaut.
- Compact : retourne uniquement id, user_id, timestamp, text, item_type, is_sent_by_viewer, shared_post_url
- Full : `compact=False` pour le payload complet (debug, media download, etc.)

### Scripts dans ce dossier
| Script | Usage |
|--------|-------|
| update_priorities.py | Sync DM state vers col L du Sheet |
| audit_ambassadors.py | Update bio/story/post counts (cols R, X, Y) |
| run_campaign.py | Envoi campagne DMs (col M) |
| qualify_influencer.py | Score profils Instagram |
| veille_concurrents.py | Veille concurrentielle |
| refresh_analyses.py | Formules KPI dans Analyses |
| create_session.py | Créer/refresh session Instagram |

### Ton et style
Voir `personality.md` dans ce dossier pour le guide de style d'Antoine.
