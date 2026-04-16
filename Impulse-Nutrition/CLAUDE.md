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
> - **Instagram DM workflow (protocole 9 etapes bloquant)** -> skill `/instagram-dm`
> - **Bibliotheque de templates DM (YAML structure, 20 templates, 3 modes)** -> [`docs/templates.yaml`](./docs/templates.yaml)
> - Decision tree DM Instagram (reference humaine) -> [`docs/dm_decision_tree.md`](./docs/dm_decision_tree.md)
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

---

## Workflows par plateforme — skills dédiés

Trois skills au niveau user, chacun est une bulle étanche pour son domaine. Ils sont loop-compatibles (ex : `/loop 30m /gorgias`).

### Instagram DM — ambassadeurs
**Skill : `/instagram-dm`** (protocole 9 étapes bloquant, auto-trigger sur "check les DMs", "draft pour {user}", "/instagram-dm", "relance {user}", etc.).

Absorbe tout ce qui était éparpillé : persona détaillé, pipeline ambassadeur, statuts, priorités, règles catégorisation voice_media/raven_media/club, pre-draft check welcome codes, format carte de décision, templates.

Référence humaine : [`docs/dm_decision_tree.md`](./docs/dm_decision_tree.md). Corpus ton : [`instagram_dm_mcp/personality.md`](./instagram_dm_mcp/personality.md).

### Gorgias — service client (tous canaux)
**Skill : `/gorgias`** (protocole 8 étapes bloquant, auto-trigger sur "check le SAV", "check les tickets", "passe SAV", "service client", "/gorgias", etc.).

Bulle complète pour tous les tickets SAV (email / chat / contact_form / Instagram / Facebook / WhatsApp via WAX). Absorbe : pull protocol 100+, filtrage par channels/tags, persona entité Impulse Nutrition (vouvoiement formel), style emails (structure, formules interdites), cross-links Shopify draft replacement + BigBlue claims, recette draft SAV (discount 100% + shipping 0€ + tag `Service client`), red flags (jamais signer "Antoine", jamais de délai chiffré, jamais `update_draft_order` sur line_items, etc.). Cas particulier ambassadeur qui contacte le SAV géré dans le skill.

Référence humaine : [`docs/process_sav_unified.md`](./docs/process_sav_unified.md). Persona : [`gorgias_mcp/personality.md`](./gorgias_mcp/personality.md).

### TikTok Shop SAV
**Skill : `/tiktok-sav`** (narrow, pipeline Python `tiktok_sav/sav.py` + ACK T0 auto + templates T1-T9 + queue.json pour cas complexes).

Reste intact comme aujourd'hui. Workflow SAV TikTok uniquement.

⚠️ Ne plus rédiger manuellement DM / ticket / message SAV. Toujours passer par le skill correspondant.

---

## Quirks techniques connus (cross-domain)

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

### Timestamps Instagram = microsecondes
```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
date_str = dt.strftime("%d/%m/%Y")
```
Quirk Python pour les scripts CLI `instagram_dm_mcp/*.py`.

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

Quand un influenceur mentionne son agent → le skill `/instagram-dm` gère le routing "Contacter manager".

---

## Vocabulaire

| Terme | Signification |
|---|---|
| Affiliatly | Plateforme de gestion des codes affiliés |
| Code affilié | Code promo personnalisé (ex: ALEXTV, FLORINE, NADIARUN) |
| Crédit | 20 € débloqués par commande passée avec le code affilié |
| Code crédit | Code Shopify ad-hoc créé pour redeem les crédits accumulés (formule `(O−Q)×20€`) |
| Code welcome | Code -25% first-order Shopify. `ACHAB25` (Antoine), `PGAU25` (Pierre Gautier), format `{NOM}25`. Donné aux prospects trop petits = **parqués** |
| Prospect parqué | Prospect qui a déjà reçu un code welcome dans un échange antérieur. Jamais re-pitcher comme un nouveau contact → skill `/instagram-dm` gère via §16 relance contextualisée |
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
- **Instagram DM** : toujours passer par le skill `/instagram-dm` (protocole bloquant), jamais rédiger depuis les règles éparpillées
- **Gorgias = vouvoiement service client**, Instagram DM = tutoiement ambassadeur (jamais mélanger)

Carte complète dans la mémoire auto à `~/.claude/projects/-Users-antoinechabrat-Documents-SmallProject/memory/MEMORY.md`.
