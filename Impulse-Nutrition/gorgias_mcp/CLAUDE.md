# Gorgias MCP — Impulse Nutrition

> **Source de vérité pour TOUT travail service client** (tickets SAV email/chat/contact_form/Instagram/Facebook/WhatsApp-via-WAX) : **skill `/gorgias`** (niveau user). Protocole 8 étapes bloquant, loop-safe. Triggers : `/gorgias`, "check le SAV", "check les tickets", "SAV check", "passe SAV", etc.
>
> Référence humaine (scenarios détaillés, recette draft SAV, tags CA) : [`../knowledge/impulse.md#5-sav--opérations-client`](../knowledge/impulse.md#5-sav--opérations-client).
>
> Persona Antoine : [`personality.md`](./personality.md).
>
> ⚠️ **Persona côté SC = entité Impulse Nutrition**, vouvoiement formel, signature `Le service client Impulse Nutrition`. **JAMAIS signer "Antoine"** — même si c'est Antoine qui rédige. Le skill gère la règle automatiquement.

## Spécifique à ce sous-projet

### MCP Gorgias custom
- Auth : variables d'env `GORGIAS_DOMAIN`, `GORGIAS_USERNAME`, `GORGIAS_API_KEY`
- Base URL : `https://impulse-nutrition.gorgias.com/api`
- `search_tickets` fonctionne via custom implementation (email lookup + substring fallback) — n'est **pas** un full-text search. Utiliser le pull protocol 100+ comme filet de sécurité.

### Pull protocol (appris à la dure 2026-04-13)
Toujours `list_tickets(limit=100, order_by="updated_datetime:desc")` minimum. Un pull de 30 a raté Amandine Laurent #52032892. Jamais conclure "pas trouvé" sur un pull court.

### Channels
Tous les canaux SC convergent vers Gorgias :
- `email`, `chat`, `contact_form` (natifs)
- `instagram`, `facebook` (natifs)
- `WAX` tag = WhatsApp via l'outil WAX (push bidirectionnel automatique)
- `internal-note` = alertes BigBlue

### Tags prioritaires
`urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`

### Ignore
`[SPAM POSSIBLE]` subjects, `Réponse automatique` / `Automatic reply`, `closed` bounces.
