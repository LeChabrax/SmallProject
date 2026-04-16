# Instagram DM MCP — Impulse Nutrition

> **Source de vérité pour TOUT travail DM** (check, draft, relance, onboarding, catégorisation, templates) : **skill `/instagram-dm`** (niveau user). Protocole 9 étapes bloquant. Triggers : `/instagram-dm`, "check les DMs", "draft pour {user}", "relance {user}", etc.
>
> Référence humaine (templates complets, voice, red flags) : [`../knowledge/impulse.md#6-voice--persona-split`](../knowledge/impulse.md#6-voice--persona-split). Source machine-readable des templates : [`../knowledge/voice/templates.yaml`](../knowledge/voice/templates.yaml).
>
> ⚠️ **Ne jamais rédiger un DM sans invoquer le skill.** Les règles éparpillées dans les feedback memory files ont toutes été absorbées dans le SKILL.md.

## Spécifique à ce sous-projet

### Sessions Instagram
- Sessions stockées dans `*_session.json` (gitignored)
- Si expirée → `python create_session.py`
- 2 comptes :
  - `impulse_nutrition_fr` — principal (DMs ambassadeurs, campaigns)
  - `antman.lass` — veille (lecture concurrents, dormant)
- Helper unique : `infra.common.instagram_client.get_ig_client(account="impulse"|"veille")`

### Rate limiting
Instagram est sensible au rate limit. Helper : `infra.common.instagram_client.sleep_random(min, max)`.
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
python3 ../infra/scripts/extract_tone.py --dry-run    # voir les stats
python3 ../infra/scripts/extract_tone.py              # mode safe (sidecar .generated)
python3 ../infra/scripts/extract_tone.py --overwrite  # remplace + backup .bak.YYYY-MM-DD
```

### Scripts CLI locaux
13 scripts CLI one-shot dans ce dossier (audit_ambassadors, qualify_*, filter_kolsquare, kolsquare_*, refresh_analyses, resolve_usernames, update_priorities, veille_concurrents, run_campaign). Tous importent depuis `../infra/common/` (gspread + IG client + dm_classifier shared).
