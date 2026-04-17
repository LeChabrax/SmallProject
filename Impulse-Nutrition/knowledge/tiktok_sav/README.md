# TikTok SAV

Dossier du systeme de gestion des messages SAV TikTok Shop pour Impulse Nutrition.

## Architecture

Un seul point d'entree : le skill Claude `/tiktok-sav`. Il fait tout :
1. Pull les conversations via MCP TikTok
2. Detecte les nouveaux messages buyer (dedup via `state.json`)
3. Classifie avec intelligence LLM (pas du simple keyword matching)
4. Enrichit avec BigBlue/Shopify si besoin (tracking, statut commande, doc produit)
5. Envoie le bon template avec la bonne variante
6. Route les cas complexes vers `queue.json`

## Fichiers

| Fichier | Role |
|---|---|
| `state.json` | Dedup : `{conversation_id: {last_acked_message_id, last_replied_at, last_category}}` |
| `queue.json` | File d'attente des cas complexes a traiter manuellement |
| `templates.md` | Catalogue des templates (T0-T9) avec variantes, keywords et routing |
| `README.md` | Ce fichier |

## Lancer

### Run unique
```
/tiktok-sav
```

### Run periodique toutes les 30 min
```
/loop 30m /tiktok-sav
```

## Persona

- Vouvoiement formel (service client, pas Antoine)
- Signature : "Le service client"
- Jamais de tutoiement, jamais de tirets em, jamais d'emojis

## Traiter la file d'attente

Lire `queue.json` ou demander "montre-moi la queue TikTok SAV". Pour chaque entree :
1. Lire le contexte (conversation_id + buyer_last_message)
2. Appliquer le workflow suggere (cf `suggested_action`)
3. Creer les ressources necessaires (code SAV, ticket BigBlue, draft order, etc.)
4. Repondre au buyer via MCP
5. Passer `status: "resolved"` dans `queue.json`
