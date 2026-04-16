# Impulse Nutrition — Factory Workspace

## Navigation rapide
> **Le savoir Impulse est réparti sur 3 fichiers sous `knowledge/`** :
>
> | Fichier | Pour quoi | Quand l'ouvrir |
> |---|---|---|
> | [`knowledge/impulse.md`](./knowledge/impulse.md) | **Onboarding** — identité, programme ambassadeur, pipeline, catalogue framework, glossaire, agences | Tu découvres Impulse / tu cherches un concept métier |
> | [`knowledge/operations.md`](./knowledge/operations.md) | **Operating** — SAV, voice & persona, runbooks (codes, orders, crédits), quirks | Tu traites un ticket SAV, tu draftes un DM, tu crées un code |
> | [`knowledge/catalog.yaml`](./knowledge/catalog.yaml) | **Catalogue structuré** — 78 SKUs actifs avec `variant_id`, `sku`, `price_eur`, `moment`, `category` (auto-généré) | Tu cherches un `variant_id` ou tu veux les produits par moment d'effort |
>
> Assets opérationnels :
> - [`knowledge/voice/templates.yaml`](./knowledge/voice/templates.yaml) — 20 templates DM (chargé par le skill `/instagram-dm`)
> - [`instagram_dm_mcp/personality.md`](./instagram_dm_mcp/personality.md) — tone guide Antoine (auto-régénéré)
>
> Refresh catalogue quand Shopify change : `python3 infra/scripts/refresh_catalog.py` (taxonomie dans `infra/scripts/catalog_taxonomy.yaml`).
>
> Architecture / carte codebase : [`LLM.md`](./LLM.md).

## Qui sommes-nous
**Impulse Nutrition** est une marque française de nutrition sportive (compléments alimentaires, boissons d'effort, whey, preworkout) distribuée via [impulse-nutrition.fr](https://impulse-nutrition.fr). Propriété de **HAVEA COMMERCIAL SERVICES (HCS)**, SAS basée à Montaigu-Vendée.

**Antoine Chabrat** — Influence Manager, gère le programme ambassadeur et les partenariats influenceurs.

---

## Persona — règle stricte (impact tone)

| Canal | Persona | Signature | Exemple |
|---|---|---|---|
| **Instagram DM** (ambassadeurs) | Antoine, humain, tutoiement | `Sportivement, Antoine` (sur messages ≥ 3 phrases) | "Hello {prenom}, je suis Antoine d'Impulse Nutrition…" |
| **Gorgias / WAX (WhatsApp) / SC TikTok** (clients finaux) | Entité Impulse Nutrition, vouvoiement formel | `Le service client` ou `L'équipe Impulse Nutrition` | "Bonjour, votre commande IMPxxxx…" |

→ **JAMAIS signer "Antoine" côté SC**, même si c'est lui qui rédige. Le client final achète à une marque, pas à une personne. Détails dans [`knowledge/operations.md#voice--persona-split`](./knowledge/operations.md#voice--persona-split).

---

## Workflows par plateforme — skills dédiés

Trois skills au niveau user, chacun est une bulle étanche pour son domaine. Ils sont loop-compatibles (ex : `/loop 30m /gorgias`).

### Instagram DM — ambassadeurs
**Skill : `/instagram-dm`** (protocole 9 étapes bloquant, auto-trigger sur "check les DMs", "draft pour {user}", "/instagram-dm", "relance {user}", etc.).

Absorbe tout ce qui était éparpillé : persona détaillé, pipeline ambassadeur, statuts, priorités, règles catégorisation voice_media/raven_media/club, pre-draft check welcome codes, format carte de décision, templates.

Référence humaine : [`knowledge/operations.md#voice--persona-split`](./knowledge/operations.md#voice--persona-split). Corpus ton : [`instagram_dm_mcp/personality.md`](./instagram_dm_mcp/personality.md).

### Gorgias — service client (tous canaux)
**Skill : `/gorgias`** (protocole 8 étapes bloquant, auto-trigger sur "check le SAV", "check les tickets", "passe SAV", "service client", "/gorgias", etc.).

Bulle complète pour tous les tickets SAV (email / chat / contact_form / Instagram / Facebook / WhatsApp via WAX). Absorbe : pull protocol 100+, filtrage par channels/tags, persona entité Impulse Nutrition (vouvoiement formel), style emails (structure, formules interdites), cross-links Shopify draft replacement + BigBlue claims, recette draft SAV (discount 100% + shipping 0€ + tag `Service client`), red flags (jamais signer "Antoine", jamais de délai chiffré, jamais `update_draft_order` sur line_items, etc.). Cas particulier ambassadeur qui contacte le SAV géré dans le skill.

Référence humaine : [`knowledge/operations.md#sav--opérations-client`](./knowledge/operations.md#sav--opérations-client). Persona : [`gorgias_mcp/personality.md`](./gorgias_mcp/personality.md).

### TikTok Shop SAV
**Skill : `/tiktok-sav`** (narrow, pipeline Python `tiktok_sav/sav.py` + ACK T0 auto + templates T1-T9 + queue.json pour cas complexes).

Reste intact comme aujourd'hui. Workflow SAV TikTok uniquement.

⚠️ Ne plus rédiger manuellement DM / ticket / message SAV. Toujours passer par le skill correspondant.

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
