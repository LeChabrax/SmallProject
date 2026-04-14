# Instagram DM MCP — Impulse Nutrition

> **Pointer** : règles globales projet, pipeline, persona, ton, decision tree DM → voir [`../CLAUDE.md`](../CLAUDE.md) et [`../docs/INDEX.md`](../docs/INDEX.md).

## Spécifique à ce sous-projet

### Sessions Instagram
- Sessions stockées dans `*_session.json` (gitignored)
- Si expirée → `python create_session.py`
- 2 comptes :
  - `impulse_nutrition_fr` — principal (DMs ambassadeurs, campaigns)
  - `antman.lass` — veille (lecture concurrents, dormant)
- Helper unique : `common.instagram_client.get_ig_client(account="impulse"|"veille")`

### Rate limiting
Instagram est sensible au rate limit. Helper : `common.instagram_client.sleep_random(min, max)`.
- Reads inter-thread : `sleep_random(3, 8)`
- Cooldown tous les 10 reads : `sleep_random(15, 30)`
- Sends : `sleep_random(5, 10)`

### Compact mode (par défaut)
`list_messages`, `list_chats`, `list_pending_chats`, `get_thread_details` ont `compact=True` par défaut.
- Compact : `id, user_id, timestamp, text, item_type, is_sent_by_viewer, shared_post_url`
- Full : `compact=False` pour debug ou download de media

### Personality (auto-régénérée)
Tone guide d'Antoine dans `personality.md`. Régénération depuis le corpus :
```bash
python3 ../scripts/extract_tone.py --dry-run    # voir les stats
python3 ../scripts/extract_tone.py              # mode safe (sidecar .generated)
python3 ../scripts/extract_tone.py --overwrite  # remplace + backup .bak.YYYY-MM-DD
```

### Scripts CLI locaux
Liste à jour dans [`../docs/INDEX.md`](../docs/INDEX.md) §5 (Scripts CLI). Tous importent depuis `../common/` (gspread + IG client + dm_classifier shared).
