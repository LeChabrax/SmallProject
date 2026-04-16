# Process — Conversation Archive + Tone Extraction

Three scripts turn your Instagram DMs into a local corpus and auto-regenerate
the tone guide used by `instagram_dm_mcp/personality.md`.

> Created 2026-04-13 as part of the big docs/MCPs refactor. Scripts live in
> `../scripts/`.

---

## 1. What the archive is for

- **Offline source of truth** for every thread with a tracked ambassador.
- **Corpus for tone extraction** — how Antoine writes (emojis, length,
  opening lines, closing lines, vocabulary tics).
- **Regression safety net** — if we change a reply template and it doesn't
  match Antoine's real voice anymore, we notice immediately.

## 2. What it is **not**

- A CRM. Use `Suivi_Amb` / `Suivi_Dot` / `Suivi_Paid` for state.
- A backup. Meta owns the DMs — we only cache them locally.
- Shareable. `data/conversations/` is `.gitignore`'d. **Never commit**.

---

## 3. Running the pipeline

### 3.1 Bulk download

```bash
# Dry run — see which usernames would be downloaded
python3 scripts/download_conversations.py --dry-run

# Partial run — first 10 usernames, for testing
python3 scripts/download_conversations.py --limit 10

# Full run — all tracked ambassadors (skip Out, skip already DL'd)
python3 scripts/download_conversations.py

# Force re-download of everything
python3 scripts/download_conversations.py --force
```

**Output** :

```
data/conversations/
├── _index.json                        # index by username
├── _progress.json                     # resume-from state
├── <username_1>.json
├── <username_2>.json
└── ...
```

Each `<username>.json` has the schema :

```json
{
  "username": "justealextv",
  "user_id": "...",
  "thread_id": "...",
  "statut_at_download": "Produits envoyés",
  "downloaded_at": "2026-04-13T14:30:00Z",
  "messages": [
    {
      "id": "...",
      "ts": 1712345678000000,
      "date_iso": "2026-04-05T09:12:58Z",
      "is_sent_by_viewer": true,
      "item_type": "text",
      "text": "Salut ! Comment tu vas ?",
      "media_info": null
    }
  ]
}
```

Rate-limit defaults : `sleep_random(3, 8)` between threads, `sleep_random(15, 30)` every 10 threads.

### 3.2 Tone extraction

```bash
# Dry run — print corpus stats without touching personality.md
python3 scripts/extract_tone.py --dry-run

# Write generated file (safe mode — doesn't overwrite existing)
python3 scripts/extract_tone.py

# Overwrite personality.md (destructive — backs up the old one)
python3 scripts/extract_tone.py --overwrite
```

**Output** :

- Default : writes `instagram_dm_mcp/personality.md.generated`. You review
  and manually merge into `personality.md`.
- `--overwrite` : replaces `personality.md`, backs up as
  `personality.md.bak.YYYY-MM-DD`.

**Sections produced** :

1. Vue d'ensemble
2. Corpus analysé (N conversations, N messages envoyés, période)
3. Patterns statistiques (longueur, ponctuation, phrases/message, tutoiement %)
4. Top formules d'ouverture et de clôture
5. Top emojis
6. Exemples anonymisés par catégorie (première approche, réponse positive,
   négociation produits, envoi code, relance)

### 3.3 Response templates

```bash
python3 scripts/extract_response_templates.py
```

**Output** : `knowledge/archive/templates_racine/real_response_examples.md` enriched with 5
anonymized examples per category. Old version backed up as
`real_response_examples.md.bak.YYYY-MM-DD`.

---

## 4. When to refresh

| Trigger | Action |
|---|---|
| New batch of ≥ 20 ambassadors added to `Suivi_Amb` | `download_conversations.py` (incremental, no flag) |
| Every month | `download_conversations.py --force` (full refresh) |
| Big change in Antoine's tone (seasonal promo, new campaign) | `extract_tone.py --dry-run` first, review, then `--overwrite` if aligned |
| Weekly retro / audit | `extract_tone.py --dry-run` — stats only, no write |

---

## 5. Rollback

If regeneration produces a tone guide that drifts from Antoine's voice :

```bash
# restore backup
cp instagram_dm_mcp/personality.md.bak.<date> instagram_dm_mcp/personality.md

# or delete the generated file and keep the manual one
rm instagram_dm_mcp/personality.md.generated
```

---

## 6. Privacy

- `data/conversations/` is git-ignored.
- The generated `personality.md` is anonymized : real usernames → `{username}`, real first names → `{prenom}`.
- If you share the repo, double-check `git status` does not include any `data/conversations/*` file.

---

## 7. See also

- `../common/instagram_client.py` — the shared IG client used by the scripts.
- `../common/google_sheets.py` — the shared column constants for reading `Suivi_Amb` / `Suivi_Dot` / `Suivi_Paid`.
- `../instagram_dm_mcp/personality.md` — the current tone guide.
- `archive/templates_dm_legacy/dm_response_guide.md` — the manual decision tree (kept in parallel).
