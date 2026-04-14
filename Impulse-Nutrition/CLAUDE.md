# Impulse Nutrition — Factory Workspace

## Navigation rapide
> **[`docs/INDEX.md`](./docs/INDEX.md)** — point d'entrée unique pour tout (reference docs, process runbooks, templates, scripts).
>
> Références canoniques :
> - 4 modèles de partenariat (Affiliation / Dotation négociée / Paid) → [`docs/reference_contract_types.md`](./docs/reference_contract_types.md)
> - Colonnes Google Sheet (source de vérité, mirror de `common/google_sheets.py`) → [`docs/reference_sheet_schema.md`](./docs/reference_sheet_schema.md)
> - 65+ tools MCP (BigBlue / Gorgias / Shopify / Instagram / TikTok) → [`docs/reference_mcps.md`](./docs/reference_mcps.md)
> - Catalogue Shopify (96 produits, variant_id, SKU, prix) → [`docs/reference_shopify_catalog.md`](./docs/reference_shopify_catalog.md)
> - SAV complet (Gorgias → Shopify → BigBlue, channels, persona) → [`docs/process_sav_unified.md`](./docs/process_sav_unified.md)
> - Création des codes Shopify (4 patterns) → [`docs/process_create_codes.md`](./docs/process_create_codes.md)
> - Création des draft orders + tags (impact CA) → [`docs/process_create_orders.md`](./docs/process_create_orders.md)
> - Calcul du crédit ambassadeur `(O−Q)×20€` → [`docs/process_calculate_credits.md`](./docs/process_calculate_credits.md)
> - Decision tree DM Instagram (templates réels) → [`docs/dm_decision_tree.md`](./docs/dm_decision_tree.md)
> - Architecture / carte codebase → [`LLM.md`](./LLM.md)

## Qui sommes-nous
**Impulse Nutrition** est une marque française de nutrition sportive (compléments alimentaires, boissons d'effort, whey, preworkout) distribuée via [impulse-nutrition.fr](https://impulse-nutrition.fr). Propriété de **HAVEA COMMERCIAL SERVICES (HCS)**, SAS basée à Montaigu-Vendée.

**Antoine Chabrat** — Influence Manager, gère le programme ambassadeur et les partenariats influenceurs.

---

## Persona — règle stricte (impact tone)

| Canal | Persona | Signature | Exemple |
|---|---|---|---|
| **Instagram DM** (ambassadeurs) | Antoine, humain, tutoiement | `Sportivement, Antoine` (sur messages ≥ 3 phrases) | "Hello {prenom}, je suis Antoine d'Impulse Nutrition…" |
| **Gorgias / WAX (WhatsApp) / SC TikTok** (clients finaux) | Entité Impulse Nutrition, vouvoiement formel | `Le service client` ou `L'équipe Impulse Nutrition` | "Bonjour, votre commande IMPxxxx…" |

→ **JAMAIS signer "Antoine" côté SC**, même si c'est lui qui rédige. Le client final achète à une marque, pas à une personne. Détails dans [`docs/process_sav_unified.md`](./docs/process_sav_unified.md) §0.

### Tone Instagram (détaillé)
- Tutoiement systématique avec les ambassadeurs
- Ton enthousiaste mais pro, jamais pushy
- Emojis modérés (😉🔥💪😊😍) — 0 à 2 par message, max
- ❌ Jamais : 🙏 ✨ 💖 (mielleux)
- ❌ **Jamais de tirets em (`—`)** dans les messages rédigés (utiliser virgule, point, ou reformuler)
- Decision tree complet + templates : [`docs/dm_decision_tree.md`](./docs/dm_decision_tree.md)
- Personality auto-régénérée : [`instagram_dm_mcp/personality.md`](./instagram_dm_mcp/personality.md)

---

## Pipeline ambassadeur

### Statuts (col J du Sheet `Suivi_Amb`)
```
In-cold → In-hot → A recontacter / A rediscuter → Contacter manager → Produits envoyés → Out
```

| Statut | Signification |
|---|---|
| **In-cold** | Identifié, pas encore contacté OU premier msg envoyé **sans réponse + > 7 jours depuis le dernier message envoyé**. Zone "à relancer" naturelle. |
| **In-hot** | A répondu positivement, en discussion active |
| **A recontacter** | À relancer plus tard (délai convenu, absence temporaire) |
| **A rediscuter** | Discussion en pause, nécessite relance sans contexte précis |
| **Contacter manager** | Passer par une agence/manager (Puls, Versacom, etc.) |
| **Produits envoyés** | Commande validée, produits expédiés, code affilié créé |
| **Out** | Refus, déjà pris, ou conversation terminée |

### Priorités (col L)
| Priorité | Quand |
|---|---|
| **high** | Action urgente requise (répondre, appeler, corriger une erreur) |
| **medium** | En attente, surveiller, relancer si pas de retour |
| **good** | RAS, tout va bien, pas d'action immédiate |

### Règle générale L (priorité)
- **Antoine est le dernier à avoir envoyé** → L = good
- **Antoine a liké le dernier message de l'autre** → L = good
- **L'autre a envoyé un message sans réponse ni like d'Antoine** → L = high (à signaler)
- **"En vue"** (message d'Antoine lu mais pas répondu) → L = medium

### Routing par modèle de partenariat
1. Pitch ❶ : **Affiliation pure** (20€/utilisation, code affilié -15%) — défaut pour tout prospect
2. Si refus → Pitch ❷ : **Dotation négociée** (`€/mois × durée ↔ utilisations cibles`)
3. Si veut cash + SIREN → **Paid** (rare, top-tier)

Détails et structure des contrats : [`docs/reference_contract_types.md`](./docs/reference_contract_types.md).

---

## Règles de catégorisation DMs (cas spéciaux)

### Messages vocaux (`voice_media`)
- `item_type == "voice_media"` et `is_sent_by_viewer == False` → **L = high**
- Exception : si Antoine a liké le message → L = good (il a écouté)
- K = "message vocal non lu — à écouter manuellement"

### Messages éphémères (`raven_media`)
- `item_type == "raven_media"` → **L = medium/high** (contenu inaccessible via MCP)
- K = "raven media reçue [date] — contenu inaccessible"

### Réponse positive à une relance
- Toute réponse positive → **J = In-hot, L = high**
- Formulations : "c'est intéressant", "je suis attentive", "ça me plairait", "pourquoi pas"

### Post annoncé
- Si ambassadeur dit "je vais poster ce soir/demain" → K = "a annoncé post le [date] — vérifier tag @impulse_nutrition"

### Clubs / organisations / contrats payants
- Messages contenant "nous" (pluriel = club/duo), "Head Coach", "je représente [club/asso]", projets events → **NE PAS ajouter au Sheet `Suivi_Amb`**
- Signaler à Antoine dans le chat uniquement
- Ce sont des contrats payants, une catégorie différente (Suivi_Paid)

### `xma_reel_mention`
- Mention dans un reel = signal à vérifier au cas par cas
- Peut être une mention positive d'ambassadeur OU une mention spontanée d'un inconnu

---

## Quirks techniques connus

### Timestamps Instagram = microsecondes
```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
date_str = dt.strftime("%d/%m/%Y")
```

### Bug Excel "sériel" dans colonnes date du Sheet
Si une colonne est formatée "date" et qu'on y entre un nombre (ex: dotation `150`), Google Sheets l'affiche comme `29/05/1900` (serial 150). Fix : réécrire la valeur numérique correcte via `batch_update_cells`.

### Limitation `update_draft_order`
Ne permet pas de modifier les `line_items` d'un draft Shopify. Si on doit ajouter/retirer un produit après création (ex : bidon en geste commercial), il faut **supprimer la draft et la recréer**. Détails dans [`docs/process_create_orders.md`](./docs/process_create_orders.md).

### Pickup point BigBlue pas reporté depuis Shopify draft
Après `complete_draft_order`, il faut manuellement régler le pickup point sur l'UI BigBlue.

### Service account Google Drive
- Path : `~/.config/google-service-account.json`
- A read+write sur le folder `InfluenceContract` (`1dxT2gSAm6tcnd8Ck6hXxPDS5yieMuj4x`)
- Utilisé par `common/google_sheets.py` (Sheets) et `common/google_drive.py` (Drive contracts)

---

## Contacts agences / managers

| Agence | Contact |
|---|---|
| **Puls Agency** | marie@puls-agency.com (Kelly, Marie Schoenenburg) |
| **Versacom** | simon@versacom.eu (Arwen) |
| **Fraich Touch** | gael@fraichtouch.com (Malo) |
| **MyOpenComm** | yohann@myopencomm.com (Sacha) |
| **Primelis** | (tripartite standard) |
| **HCS interne** | pgautier@havea.com (Pierre Gautier — commandes dotation) |

Quand un influenceur mentionne son agent → statut `Contacter manager` en `Suivi_Amb`.

---

## Vocabulaire

| Terme | Signification |
|---|---|
| Affiliatly | Plateforme de gestion des codes affiliés |
| Code affilié | Code promo personnalisé (ex: ALEXTV, FLORINE, NADIARUN) |
| Crédit | 20 € débloqués par commande passée avec le code affilié |
| Code crédit | Code Shopify ad-hoc créé pour redeem les crédits accumulés (formule `(O−Q)×20€`) |
| Dotation | Envoi gratuit de produits contre contenu (négocié au cas par cas) |
| Enveloppe | Budget produits alloué (~80-100 €) |
| Tag `Service client` | Commande SAV/replacement — sort du CA HCS |
| Tag `Dotation influenceur` | Envoi gratuit ambassadeur — sort du CA HCS |
| RAS | Rien à signaler |
| Gamme Au Quotidien | Gamme bien-être/santé (vs gamme Sport) |

---

## Règles transversales (mémoire auto)

Persistées dans la mémoire auto, donc actives sans relire ce fichier :
- **Draft + go explicite avant tout envoi** (DM, Gorgias, BigBlue, Shopify mutation)
- **Lire le thread complet avant de drafter une réponse** (`list_ticket_messages` ou `read_conversation`)
- **Excuses si retard de réponse** : > 4j (légère), > 10j (appuyée)
- **MCP = tout accès plateforme** — natif ou API, jamais dire "j'ai pas de MCP"

Carte complète dans la mémoire auto à `~/.claude/projects/-Users-antoinechabrat-Documents-SmallProject/memory/MEMORY.md`.
