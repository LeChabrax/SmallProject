# TikTok SAV — Système d'auto-réponse

Dossier racine du système de gestion automatique des messages SAV TikTok Shop. Son but : **maintenir le taux de réponse TikTok Shop ≥ 95%** en traitant automatiquement les nouveaux messages buyer toutes les 30 minutes.

## Architecture en 3 couches

1. **Layer 1 — ACK first-touch (auto-send)** : tout nouveau message buyer reçoit immédiatement un accusé de réception générique (« Merci pour votre message, nous revenons vers vous… »). Zéro engagement, zéro risque, mais sauve le compteur 24h.
2. **Layer 2 — Templates ciblés (auto-send)** : pour les cas clairs détectés par pattern matching (tracking, code promo, délai, question produit, remerciement), envoi automatique du template correspondant.
3. **Layer 3 — File d'attente (humain)** : les cas complexes (dommage, manquant, adresse, remboursement) sont stockés dans `queue.json` pour traitement humain.

## Fichiers

| Fichier | Rôle |
|---|---|
| `state.json` | Dedup : `{conversation_id: {last_acked_message_id, last_replied_at, last_category}}`. Évite de répondre 2× au même message. |
| `queue.json` | File d'attente des cas complexes à traiter manuellement. Array d'objets `QueueEntry`. |
| `templates.md` | Catalogue des 10 templates (T0 à T9) avec keywords, texte, et routing (auto-send vs queue). |
| `README.md` | Ce fichier. |

## Comment lancer le loop

### Run unique (manuel)
```
/tiktok-sav
```
Claude lit les convos, classe, envoie les ACK + templates, queue les cas complexes, affiche un rapport.

### Run périodique toutes les 30 min
```
/loop 30m /tiktok-sav
```
Le harness redéclenche le skill toutes les 30 minutes en autopilot.

### Stop le loop
Dans le terminal Claude, simplement interrompre la session ou dire « stop ».

## Persona de réponse

**Obligatoire** pour toutes les réponses SAV TikTok :
- Vouvoiement formel (service client, pas Antoine)
- Signature : « Le service client » ou « L'équipe Impulse Nutrition »
- Jamais de tirets em (`—`)
- Jamais de tutoiement
- Emojis interdits côté service client

Cf `docs/process_sav_unified.md` §0 pour la référence complète.

## Traiter la file d'attente

Quand tu as 5 min, lis `queue.json` ou demande à Claude « montre-moi la queue TikTok SAV ». Pour chaque entrée :
1. Lis le contexte (convo_id + buyer_last_message)
2. Applique le workflow suggéré (cf `suggested_action`)
3. Crée les ressources nécessaires (code SAV, ticket BigBlue, draft order, etc.)
4. Réponds au buyer via `mcp__tiktokshop__reply_to_conversation`
5. Supprime l'entrée de `queue.json` (ou passe `status: "resolved"`)

## Logs / debug

Le skill produit un rapport markdown à chaque run. Pour debug :
- Check `state.json` pour voir ce qui a été ACKé
- Check `queue.json` pour voir ce qui est en file
- Si un message est traité deux fois, c'est un bug de dedup — vérifier que `last_acked_message_id` matche bien le nouveau `latest_message.id`

## Extensions futures

- **Google Sheet mirror** : pour vue mobile/direction, créer manuellement le sheet `Suivi_TikTok_SAV`, le partager avec le service account, et ajouter un step de sync dans le skill.
- **Intégration BigBlue** : pour les tracking, lookup auto de l'order_id via BigBlue MCP et renvoi du vrai status en template.
- **Webhooks TikTok** : passer de polling 30 min à temps réel si TikTok ouvre un jour des webhooks pour les messages buyer.
- **Stats** : ajouter un compteur rolling 7j pour voir combien de cas ont été traités, par catégorie.
