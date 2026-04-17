# Pull protocol — Gorgias tickets

Chargé par `/gorgias` à l'Étape 1 (pull + filtrage).

Depuis le refacto MCP (avril 2026), le filtrage par statut/canal est **natif côté serveur** via les vues Gorgias. Plus besoin de tout pull pour filtrer ensuite — on demande directement la vue qui nous intéresse.

## Protocole

1. **Pull la vue Inbox par défaut** : `mcp__gorgias__list_tickets(status="open", limit=50, order_by="updated_datetime:desc")` → vue 33360, ne renvoie que les tickets ouverts non-spam non-snoozed.
2. **Pour un canal précis** : `list_tickets(channel="email"|"contact_form"|"chat"|"help_center", limit=50)` → renvoie tous statuts pour ce canal.
3. **Pour recherche historique** (ticket fermé, ancien, ou client non présent dans Inbox) : `list_tickets(status="all", limit=100)` ou directement `search_tickets(query="email|nom|id_numérique")`.
4. **Filtrer localement** ce qui reste (priorité tags, exclusions). Voir tables ci-dessous.
5. **Jamais conclure "pas trouvé"** sans avoir essayé `search_tickets` puis `status="all"` au minimum.

## Vues Gorgias disponibles

`mcp__gorgias__list_views()` retourne les maps complètes. Aliases utiles :

| `status=` | view_id | Sens |
|---|---|---|
| `open` | 33360 | Inbox (défaut) |
| `closed` | 33364 | Closed |
| `snoozed` | 33363 | Snoozed |
| `unassigned` | 33361 | Unassigned |
| `all` | 33362 | All (historique complet) |

| `channel=` | view_id | Sens |
|---|---|---|
| `email` | 44348 | contact@impulse-nutrition.fr |
| `contact_form` | 44386 | Formulaire site |
| `chat` | 45597 | Widget chat site |
| `help_center` | 44385 | Help center |

Pour un filtre custom : passer directement `view_id=<int>` (override).

## Channels à garder (filtrage local après pull)

| Channel | Mécanisme |
|---|---|
| `email` | natif Gorgias |
| `chat` | natif Gorgias (widget site) |
| `contact_form` | natif Gorgias (formulaire site) |
| `instagram` | mentions / DMs clientes venant d'Instagram (pas les ambassadeurs — eux c'est `/instagram-dm`) |
| `facebook` | mentions / messages Facebook |
| `internal-note` | alertes BigBlue automatiques (bad ratings, actions required) |
| `WAX` (tag) | WhatsApp via WAX push bidirectionnel |

## Tags à prioriser

Dans l'ordre d'importance :

- `urgent`
- `statut_commande`
- `retour commande`
- `retour/echange`
- `candidature`
- `bigblue-bad-rating-no-comment`
- `bigblue-bad-rating-with-comment`
- `bigblue-action-required`
- `WAX` (tickets WhatsApp via WAX)

Un ticket avec plusieurs tags : utiliser le premier dans l'ordre ci-dessus comme "tag_principal" dans la carte de décision.

## Exclusions

À **ignorer** (ne pas drafter, potentiellement close silencieusement) :

| Type | Signal |
|---|---|
| Spam | Subject préfixé `[SPAM POSSIBLE]` |
| Auto-reply | Subject `Réponse automatique`, `Automatic reply`, `Out of office` |
| Closed bounces | Tickets déjà `closed` qui sont juste des bounces email |
| Newsletters / promos reçues | Sender = mailing list |
| Messages sans texte (vide, emoji seul) | Exception : si contexte urgent via ticket ouvert, réponse `"Bonjour, nous n'avons pas reçu votre message. Pouvez-vous nous renvoyer votre demande ?"` |

## Priorisation par `messages_count` (optimisation)

Après filtrage et avant `list_ticket_messages`, **prioriser l'ordre de traitement** selon le champ `messages_count` :

| `messages_count` | Interprétation | Priorité |
|---|---|---|
| **1** | Un seul message dans le ticket (souvent un internal-note BigBlue auto-généré : bad rating, bigblue-action-required) OU un message client sans bot auto-reply | **Prioritaire** → fetch messages Étape 2 en premier |
| **2** | Client + bot auto-reply Gorgias (bot "Nos équipes sont disponibles..."). **Aucun vrai SC reply encore**, ticket vraiment à traiter. | **Très haute priorité** → fetch messages Étape 2 |
| **≥ 3** | Possiblement déjà traité (client + bot + au moins 1 SC reply). **Fetch quand même** (safety net : le client peut être revenu sur le ticket après une réponse SC), mais Étape 2 déclenchera le plus souvent l'auto-skip `waiting_customer_reply` (Fix #1) si le dernier message est du SC. | **Priorité basse** → fetch en dernier |

**Important** : cette règle ne supprime jamais l'appel `list_ticket_messages`. La règle "lire thread complet avant drafter" reste critique. La priorisation change juste l'ordre de traitement pour : (a) voir rapidement les cas vraiment à drafter, (b) éviter de drafter par-dessus des réponses SC récentes.

**En mode `/loop`** : la priorisation est encore plus utile pour limiter le bruit visuel — les tickets `messages_count >= 3` qui tomberont en `waiting_customer_reply` auront une carte condensée 1 ligne, pas une carte complète.

## `search_tickets` (lookup ciblé)

Réécrit en avril 2026 pour utiliser les views + lookup customer en cascade :

1. Si `query` numérique → `get_ticket(id)` direct
2. Lookup customer par email exact → tire ses tickets
3. Fallback : scan view Inbox + substring match sur subject/customer

Usage normal :
- Email connu : `search_tickets(query="email@domain.com")`
- Numéro ticket : `search_tickets(query="52867862")`
- Substring nom : `search_tickets(query="amandine")`

Pour ticket historique non dans Inbox : combiner `list_tickets(status="all", limit=100)` puis filtre local, ou `search_customers(query=email) → get_customer(id) → tickets`.

## Loop-safe filtering

Si le skill tourne en `/loop 30m /gorgias` :

1. Lire `~/.claude/skills/gorgias/last_run.txt` (timestamp ISO du dernier run réussi)
2. Pull `list_tickets(status="open", limit=50)` (Inbox view)
3. Filtrer localement : ne garder que les tickets où `updated_datetime > last_run_timestamp`
4. Si après filtrage 0 ticket → renvoyer `"✅ Aucun ticket SAV actionnable depuis {last_run}"` et terminer
5. Sinon → continuer le protocole normal sur les tickets retenus
6. À la fin du run : écrire le nouveau timestamp dans `last_run.txt`

Si `last_run.txt` n'existe pas (premier run) → pull complet sans filtre temporal, puis créer le fichier.

## Sortie citée attendue

```
Étape 1 ✅ — Pull view Inbox (status=open, limit=50)
  → Filtrage local : channels {email, chat, WAX} + tags prioritaires {urgent, statut_commande, bigblue-bad-rating-*}
  → Exclus : 3 [SPAM POSSIBLE], 2 auto-replies
  → {N} tickets actionnables retenus
  (Si loop : depuis last_run {timestamp})
```

---

> **Note historique** : Avant le refacto MCP (avril 2026), le filtrage par statut renvoyait 400 et il fallait pull 100 puis filtrer côté client. L'incident Amandine Laurent (`#52032892`, 2026-04-13) avait été causé par un pull de 30 trop court. La règle "100 minimum" est levée depuis que les vues fonctionnent — mais la règle "jamais conclure 'pas trouvé' sans `search_tickets` + `status='all'`" reste critique.
