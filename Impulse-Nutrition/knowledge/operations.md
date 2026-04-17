# Impulse Nutrition — Operations

> **Ce doc = comment faire**. Ce que tu ouvres quand tu traites un ticket SAV, draftes un DM, crées un code ou un draft order.
> Pour le **qui/quoi** (identité, programme, catalogue, glossaire) → [`impulse.md`](./impulse.md).
> Source machine-readable des templates DM : [`voice/templates.yaml`](./voice/templates.yaml).

## Sommaire

1. [SAV & opérations client](#sav--opérations-client)
2. [Voice & persona](#voice--persona)
3. [Runbooks opérationnels](#runbooks-opérationnels)
4. [Quirks techniques transverses](#quirks-techniques-transverses)

---

## SAV & opérations client

### Canaux convergents

**Tous les SAV remontent dans Gorgias**, peu importe le canal :

| Canal | Mécanisme | Tag Gorgias |
|---|---|---|
| Email | natif Gorgias | selon contenu |
| Chat site | natif Gorgias | selon contenu |
| Contact form site | natif Gorgias | selon contenu |
| **WhatsApp via WAX** | outil tiers qui pousse dans Gorgias | `WAX` |
| Instagram (mention/DM cliente) | natif Gorgias | selon contenu |
| Facebook | natif Gorgias | selon contenu |
| BigBlue internal-note | alertes stock/livraison | selon contenu |
| TikTok Shop | skill `/tiktok-sav` (templates dans `knowledge/tiktok_sav/`) | — |

WAX pousse auto la réponse Gorgias sur WhatsApp. Tone SC vouvoiement formel identique.

### Pull protocol (filtrage natif via vues Gorgias)

Depuis le refacto MCP avril 2026, le filtrage par statut/canal passe par les vues serveur Gorgias (`/api/views/{view_id}/items`). Plus besoin de tout pull pour filtrer ensuite.

1. **Pass quotidien** : `list_tickets(status="open", limit=50)` → vue Inbox (33360), uniquement les ouverts non-spam non-snoozed.
2. **Pass par canal** : `list_tickets(channel="email"|"contact_form"|"chat"|"help_center", limit=50)` → vue canal côté serveur.
3. **Recherche historique** (ticket fermé / ancien) : `list_tickets(status="all", limit=100)` ou directement `search_tickets(query="email|nom|id_numérique")`.
4. **Filtrer localement** ce qui reste :
   - Keep : channels `email`, `chat`, `contact_form`, `instagram`, `facebook`, `internal-note`
   - Prioriser tags : `urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`
   - Ignorer : subjects `[SPAM POSSIBLE]`, `Réponse automatique`, `Automatic reply`, `closed` bounces
5. **Jamais conclure "not found"** sans avoir essayé `search_tickets` puis `status="all"`.

`list_views()` expose les view_id complets. Maps source : `gorgias_mcp/src/gorgias_mcp/views.py`.

> Note historique : avant le refacto, le filtrage était cassé (V2 rejetait `?status=` avec un 400). L'incident 2026-04-13 (Amandine Laurent #52032892 ratée sur pull 30) avait imposé la règle "100 minimum" — levée depuis que les vues fonctionnent.

### Sheet SAV — onglets BigBlue

Le Google Sheet `1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE` (doc `SAV`) sert de hub partagé entre Gorgias et TikTok pour les claims/actions BigBlue (le MCP BigBlue helpdesk étant fragile, on log la ligne dans la sheet et un humain dépose manuellement le message dans l'UI BigBlue, puis colle la réponse dans la sheet pour que le skill enchaîne).

| Onglet | Source | Skill responsable | Cycle retour |
|---|---|---|---|
| `BigBlue_Actions` | Gorgias (tickets SAV email/chat/contact_form/IG/FB/WAX) | `/gorgias` Étape 0 + Étape 8 | Lit `Statut BB = "Réponse reçue"` → reply Gorgias |
| `TTS BB Actions` | TikTok Shop (conversations buyer) | `/tiktok-sav` Étape 0 + Étape 3 | Lit `Statut BB = "Réponse reçue"` → reply TikTok via `reply_to_conversation` |

Les 2 onglets suivent le même protocole : push initial avec `Message BigBlue` FR pré-rédigé prêt à coller, statut `A faire` → humain traite côté BigBlue → met `Statut BB = "Réponse reçue"` + colle la réponse → au run suivant le skill responsable détecte, répond au client final, et passe la ligne en `Traité`.

### Recette draft SAV canonique

**Defaults OBLIGATOIRES pour TOUTE commande gratuite** (SAV ou dotation, total 0€) :

```json
{
  "applied_discount": {
    "title": "SAV",
    "value_type": "percentage",
    "value": "100.0",
    "description": "SAV"
  },
  "shipping_line": {
    "title": "Expédition gratuite",
    "price": "0.00"
  },
  "tags": "Service client",
  "note": "<contexte court : ref originale + raison + geste>"
}
```

Le `applied_discount.title` change selon contexte (`SAV`, `Dotation`, `Crédit ambassadeur`). Le `tags` est ce qui compte pour la compta.

### Règle d'or des tags Shopify

**Il existe exactement 2 tags qui sortent une commande du calcul du CA HCS :**

| Tag | Coût HCS | Utilisé pour |
|---|---|---|
| `Service client` | Coût SAV | Replacements, gestes commerciaux, codes `[PRENOM]-SAV` |
| `Dotation influenceur` | Coût marketing | Envois mensuels ambassadeurs, codes dotation, codes crédit `[CODE]DOTATION` |

Toute autre commande = **vraie vente dans le CA**. **Mal tagger une commande fausse les rapports financiers HCS.** Non négociable.

Mapping par scénario :

| Scénario | Tag |
|---|---|
| Replacement colis bloqué / perdu | `Service client` |
| Replacement returned-to-sender | `Service client` |
| Geste commercial post-bad-rating | `Service client` |
| Commande client utilisant code `[PRENOM]-SAV` | `Service client` |
| Envoi dotation mensuelle (Suivi_Dot / Suivi_Paid) | `Dotation influenceur` |
| Commande utilisant code crédit `[CODE]DOTATION` | `Dotation influenceur` |
| Vente normale e-commerce | (aucun tag de cette liste) |

### Scénarios SAV typiques

**Colis bloqué / perdu en transit** (Chronopost loop, Mondial Relay misrouted)

1. `get_order(order_id)` Shopify → line items + shipping address
2. `get_tracking(bigblue_order_id)` pour confirmer
3. **Créer replacement draft** avec line items originaux + geste commercial (bidon, shaker, ou 1 produit même range)
4. Ship to **home address** — pas de pickup point sur le retry
5. Apply defaults SAV (100% discount + shipping 0 + tag `Service client`)
6. `complete_draft_order` → Shopify crée la commande → BigBlue la prend
7. **Régler manuellement le pickup point sur BigBlue UI** (quirk connu)
8. Répondre Gorgias : confirmer reshipment + geste. Ne pas exposer les détails du tracking loop

Cas réf : Alexandre Damary, IMP4938 → draft IMP6923.

**Returned to sender** (refusé par pickup point, 2× consécutifs)

Proposer :
- Refund (simple)
- OU reship to home + geste commercial

Attendre la réponse du client avant trigger.

Cas réf : Jean-Baptiste Morand, IMP6586.

**Partial refund**

Client retourne partie de la commande. BigBlue `RETURNED`, Shopify `partially_refunded`.

1. `get_order` → check `refunds` array
2. Si refund déjà traité (transaction `refund`, status `success`) → confirmer au client (montant + PayPal/Stripe auth id + délai 3-5 j ouvrés)
3. Si pas encore traité → trigger via Shopify admin UI (MCP refund non implémenté)

Cas réf : Amandine Laurent, IMP6036, refund 50,18€ sur ligne `36592237936971`.

**Bad rating BigBlue (1-2 étoiles)** — tagged `bigblue-bad-rating-*`

- Lire le commentaire (si présent) via `get_support_ticket`
- Apology + demander ce qui a mal tourné. Offrir code discount si issue côté service
- Répondre sur le ticket Gorgias (pas BigBlue), fermer quand répondu

**Cas particulier ambassadeur qui fait un SAV**

Si la personne qui contacte le SAV est un ambassadeur (Suivi_Amb / Suivi_Dot / Suivi_Paid) :
- Antoine répond probablement directement (pas via Gorgias / pas signé "Le service client") — il connaît la personne
- Vérifier le statut Suivi avant réponse pour adapter le ton
- Le tag de la commande de remplacement reste **`Service client`** (c'est un SAV, pas une dotation)

### Style emails Gorgias

- **Pas de formules pompeuses** : éviter "Nous avons bien pris note", "Nous vous remercions de nous avoir contacté", "N'hésitez pas à revenir vers nous"
- **Phrases courtes**, directes, factuelles
- **Jamais promettre un délai chiffré** (livraison J+1, traitement 48h…) — partenaires logistiques variables
- **Jamais signer "Antoine"** côté SC — `Le service client` ou `L'équipe Impulse Nutrition`
- **Vouvoiement strict**
- **Pas d'emoji** sur canal SC

### Excuses retard réponse

- **> 4 jours** : excuse légère ("Excuse-moi pour le temps de réponse !")
- **> 10 jours** : excuse appuyée ("Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !")

---

## Voice & persona

**Règles complètes** : [`voice/rules.md`](./voice/rules.md) — persona split, tone rules Instagram DM (tutoiement, emojis, red flags), templates DM humains, routing par type de message reçu, relance des prospects parqués.

**Templates machine-readable** : [`voice/templates.yaml`](./voice/templates.yaml).

**Tone stats auto-générées** : [`voice/personality.md`](./voice/personality.md) (via `infra/scripts/extract_tone.py`).

**TL;DR** :
- Instagram DM (ambassadeurs) → **Antoine**, tutoiement, signature `Sportivement, Antoine`
- Gorgias / WAX / email SC (clients finaux) → **entité Impulse Nutrition**, vouvoiement, signature `Le service client`
- **JAMAIS signer "Antoine" côté SC**

---

## Runbooks opérationnels

### Créer un code affilié ambassadeur

**Utiliser le tool MCP** `create_affiliate_code(name="florine")` → clone exact ALEXTV :
- `-15%` percentage
- `once_per_customer=true`
- `starts=now`, `ends=null`
- `usage_limit=null`
- `combinesWith { order:false, product:true, shipping:true }`

Pour Paid (-20% type LRA20) : `create_paid_affiliate_code(name="...")`.

**Convention nommage** : `<PRENOM>` ou `<HANDLE>` en majuscules, sans accents ni caractères spéciaux. Ex : `FLORINE`, `ALEXTV`, `DODO`, `JBTRI`, `LRA20`.

**Codes réels en prod (audit 2026-04-13)** :

| Code | price_rule_id | value_type | value | usage_limit | starts_at | type |
|---|---|---|---|---|---|---|
| `ALEXTV` | 2205486154059 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `DODO` | 2199297753419 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `LRA20` | 2205436543307 | percentage | -20.0 | null | 2025-09-09 | Affilié Paid |
| `TRAILEURSDOTATION` | 2206068539723 | fixed_amount | -200.0 | 6 | 2026-01-15 → 2027-01-31 | Dotation |

### Créer un draft order (SAV ou dotation)

**Hard rule : email client OBLIGATOIRE.** Sans email → Shopify confirmation + BigBlue tracking + Affiliatly mapping cassent.

Checklist avant `create_draft_order` :
1. Récupérer l'email (DM Instagram, Gorgias, thread)
2. `search_customers(query=email)` :
   - Existe → passer `customer_id=<integer>` (JAMAIS `customer_email=`)
   - N'existe pas → créer le customer d'abord via `mcp__shopify__create-customer` (firstName, lastName, email, adresse), puis `customer_id`
3. Après création, vérifier `get_draft_order(draft_id)` → `draft_order.email ≠ null`

**Fallback** si draft créé sans email (blank customer auto) :
```python
mcp__shopify__update_customer(id=<blank_id>, email="<vrai>", firstName="...", lastName="...")
```

**Recette canonique SAV** :
```python
draft = create_draft_order(
    line_items=[{"variant_id": ..., "quantity": ...}, ...],
    customer_id=<id>,
    note="Replacement IMPxxxx — motif",
    tags="Service client",
)
update_draft_order(
    draft_order_id=draft["id"],
    applied_discount={"title":"SAV","value_type":"percentage","value":"100.0","description":"SAV"},
    shipping_line={"title":"Expédition gratuite","price":"0.00"},
)
complete_draft_order(draft_order_id=draft["id"], payment_pending=False)
# → Puis fix manuel BigBlue pickup point
```

**Checklist avant `complete_draft_order`** :
- [ ] `tags` = `Service client` OU `Dotation influenceur` (jamais les 2, jamais aucun sur commande gratuite)
- [ ] `applied_discount` 100% si gratuit
- [ ] `shipping_line` "Expédition gratuite" 0.00 si gratuit
- [ ] `note` interne explicite (ref + motif)
- [ ] `line_items` complets (pas d'`update_draft_order` pour ajouter après)
- [ ] Adresse correcte (domicile pour SAV retry)

### Calculer et redeem le crédit ambassadeur

**Formule** : `solde = col O (nb_utilisation) − col Q (nb_credit_used)` · `credit_value = solde × 20€`

**Garde-fou** : si `Q > O` → incohérence. Stopper, vérifier le Sheet manuellement, **ne PAS créer de code**.

**Workflow** :

```python
from infra.common.google_sheets import SUIVI_AMB_COLS, get_worksheet, DATA_START_ROW

ws = get_worksheet("Suivi_Amb")
rows = ws.get_all_values()[DATA_START_ROW - 1:]

def find_ambassador(username):
    for i, row in enumerate(rows, start=DATA_START_ROW):
        if len(row) > SUIVI_AMB_COLS["username"] and \
           row[SUIVI_AMB_COLS["username"]].strip().lower() == username.lower():
            return i, row
    return None, None

row_idx, row = find_ambassador("florinebreysse")
nb_total = int(row[SUIVI_AMB_COLS["nb_utilisation"]] or 0)
nb_used = int(row[SUIVI_AMB_COLS["nb_credit_used"]] or 0)
prenom = row[SUIVI_AMB_COLS["prenom"]] or "X"

solde = nb_total - nb_used
if solde <= 0:
    raise SystemExit(f"solde invalide : {solde}")
credit_value = solde * 20
```

### Pattern code dotation `[CODE]DOTATION`

**Convention unique** (validée Antoine 17/04/2026) : tous les codes que l'ambassadeur utilise lui-même pour encaisser un crédit ou redeem sa dotation suivent le pattern `[CODE]DOTATION` où `[CODE]` = code affilié (col N de Suivi_Amb). L'ancien pattern `[PRENOM]-CREDIT` est abandonné.

⚠️ Ne pas confondre avec le code **affilié** (col N, utilisé par les followers pour acheter avec -15%). Le code dotation/crédit est utilisé par l'ambassadeur pour sa propre commande.

**2 variantes selon le besoin** :

#### Variante A — One-shot (crédit ponctuel à redeem)

Pour un crédit unique déblocable (ambassadeur qui redeem ses crédits accumulés, geste commercial ponctuel, etc.).

```
title: FITBYSIMONDOTATION
value_type: fixed_amount
value: -140.0          ← valeur du crédit (= solde × 20€ typiquement)
customer_selection: all
target_type: line_item
target_selection: all
allocation_method: across
usage_limit: 1         ← utilisation unique
once_per_customer: true
starts_at: <now>
ends_at: null
combinesWith: productDiscounts:true, shippingDiscounts:true, orderDiscounts:false
```

**Calcul crédit** : `solde = col_O − col_Q`, puis `value = -(solde × 20)`.

**Mise à jour Sheet** :
- Avant commande : col P (`code_credit`) ← `[CODE]DOTATION`
- Après commande : col Q (`nb_credit_used`) ← `Q + solde` (nouveau Q = O)

#### Variante B — Récurrent mensuel (contrat Dotation négocié)

Pour un contrat Dotation structuré (ex : 4 mois × 120€/mois).

```
title: TRAILEURSDOTATION
value_type: fixed_amount
value: -200.0          ← montant mensuel
customer_selection: all
target_type: line_item
target_selection: all
allocation_method: across
usage_limit: 6         ← nombre de mois (1 redemption/mois)
once_per_customer: false
starts_at: <début contrat>
ends_at: <fin contrat>
combinesWith: productDiscounts:true, shippingDiscounts:true, orderDiscounts:false
```

Règle pour un contrat D mois × M €/mois :
- `value = -M.0`
- `usage_limit = D`
- `starts_at` = début contrat, `ends_at` = fin

**Tag de la commande générée** (variantes A et B) : `Dotation influenceur`.

**Audit mensuel** : pour tout ambassadeur avec `solde > 5` (≥100€) qui n'a pas redeem depuis ≥3 mois → DM proposant le redeem.

`combinesWith.orderDiscounts: false`.

### Pattern code SAV `[PRENOM]-SAV`

Geste commercial SAV — code qui offre produit gratuit sur panier client :

- `value_type: percentage`, `value: -100.0`
- `entitled_product_ids: [shaker, bidon]` (restreint aux produits gratuits)
- `usage_limit: 1`, `once_per_customer: true`
- `combinesWith.orderDiscounts: true, productDiscounts: true, shippingDiscounts: true`

Le client place sa commande avec ce code → tagguer la commande **`Service client`**.

### DM check + onboarding condensé

**Check DMs** :
1. `list_chats(100)` — ⚠️ le `last_message` peut être obsolète, **ne jamais s'y fier pour drafter**
2. Cross-ref avec Suivi_Amb + Suivi_Dot + Suivi_Paid
3. `list_messages(thread_id=..., limit=10)` pour chaque thread actionnable — **règle absolue avant tout draft**
4. Classifier : URGENT / À RÉPONDRE / À NOTER / RAS (auto-skip si notre côté dernier à écrire)

**Pre-draft check bloquant** (avant tout draft DM, §0.5 du decision tree) :

- **Check 1 — Thread history** : `list_messages(thread_id, amount=50)` minimum. Scanner pour :
  - Codes welcome déjà donnés (`ACHAB25`, `PGAU25`, `-25%`, `{NOM}25`)
  - Échanges Impulse antérieurs (`is_sent_by_viewer=true` autre que l'action courante)
  - Positions Impulse précédentes (refus, acceptation, conditions)
  - Rencontres IRL (`stand`, `salon`, `Run Expérience`, `marathon de Paris`)
- **Check 2 — Sheet check** : `find_in_spreadsheet(query=username)` sur les 3 tabs.

**Règle d'or** : le thread Instagram est la source de vérité primaire. Le Sheet est secondaire.

**Onboarding nouveau ambassadeur (dotation)** :
1. Phase DM : proposer (80-100€ dotation + code affilié -15% + seuil renouvellement) → accepte → demander les 4 infos en 1 message
2. Phase commande : `get-products(searchTitle=...)` pour variant_id → `create_draft_order` avec tag `Dotation influenceur` + discount 100% + shipping 0€ → présenter récap à Antoine → `complete_draft_order`
3. Phase code : `create_affiliate_code(name="prenom")` (clone ALEXTV)
4. Phase Sheet : ajouter ligne Suivi_Dot (Name, Statut, Type, Mail, Numéro, Prénom, Nom, Insta, Code, Date début, Durée, Dotation €, Seuil renouvellement, Adresse)
5. Phase DM final : envoyer code + lien + infos

---

## Quirks techniques transverses

### Bug Excel "sériel" dans colonnes date du Sheet

Si une colonne est formatée "date" et qu'on y entre un nombre (ex : dotation `150`), Google Sheets l'affiche comme `29/05/1900` (serial 150). **Fix** : réécrire la valeur numérique correcte via `batch_update_cells`.

### Limitation `update_draft_order` Shopify

Ne permet **pas** de modifier les `line_items` d'un draft. Si on doit ajouter/retirer un produit après création (ex : bidon en geste commercial) :

1. `delete_draft_order(draft_id)`
2. `create_draft_order(<full set of line_items>)`
3. Réappliquer `applied_discount`, `shipping_line`, `tags`, `note`

→ Toujours préparer la liste line_items complète AVANT le premier appel.

### Pickup point BigBlue non reporté

Après `complete_draft_order`, BigBlue ne reçoit pas systématiquement l'info du pickup point. **Fix** : aller sur l'UI BigBlue, trouver la commande, régler manuellement le pickup point.

Pas de fix automatique côté MCP.

### Refunds non implémentés côté MCP

Les remboursements (partiels ou totaux) passent par l'UI Shopify ou directement via API REST `/orders/{id}/refunds.json`. Le MCP `shopify_orders` n'expose pas d'outil refund.

### Service account Google Drive

- Path : `~/.config/google-service-account.json`
- A read+write sur le folder `InfluenceContract` (ID `1dxT2gSAm6tcnd8Ck6hXxPDS5yieMuj4x`)
- Utilisé par `infra/common/google_sheets.py` (Sheets) et `infra/common/google_drive.py` (Drive contracts)

### Timestamps Instagram en microsecondes

Pour les scripts CLI `instagram_dm_mcp/*.py` :

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
date_str = dt.strftime("%d/%m/%Y")
```

### Helpdesk BigBlue fragile

4 tools du MCP BigBlue (list/get/create/reply support tickets) sont fragiles — reverse-engineering du gRPC-Web de l'admin UI. Messages **obligatoirement en français** (leur SOP). Fallback Playwright si API cassée.

### Filtrage Gorgias par view_id

L'API V2 Gorgias rejette `?status=` / `?channel=` directement sur `/api/tickets` (400). Le filtrage natif passe par les vues serveur (`/api/views/{view_id}/items`). Le wrapper MCP `list_tickets(status=, channel=, view_id=)` fait la résolution automatique. Maps complètes dans `gorgias_mcp/src/gorgias_mcp/views.py` ; `mcp__gorgias__list_views()` les expose au runtime.

`search_tickets` (custom) = lookup en cascade (id numérique → customer email → fallback substring sur view Inbox). Le natif `/api/search` n'existe pas.

### Col O / Q incohérentes (Q > O)

Crédit invalide. Stopper, vérifier manuellement, **ne PAS créer de code**.

### Rate limiting Instagram

Dans `infra.common.instagram_client.sleep_random(min, max)` :
- Reads inter-thread : `sleep_random(3, 8)`
- Cooldown tous les 10 reads : `sleep_random(15, 30)`
- Sends : `sleep_random(5, 10)`

### Draft order email obligatoire

Sans email client, Shopify confirmation + BigBlue tracking + Affiliatly mapping cassent. Voir "Créer un draft order" plus haut.

### `list_chats` last_message obsolète

`list_chats` (MCP Instagram) montre un `last_message` qui peut être périmé. **Ne JAMAIS se fier** au `last_message` pour drafter. Toujours `list_messages(thread_id, limit≥10)` avant draft.

### Sessions Instagram

- Sessions stockées dans `instagram_dm_mcp/*_session.json` (gitignored)
- Si expirée → `python instagram_dm_mcp/create_session.py`
- 2 comptes :
  - `impulse_nutrition_fr` — principal (DMs ambassadeurs, campaigns)
  - `antman.lass` — veille (lecture concurrents, dormant)
- Helper unique : `infra.common.instagram_client.get_ig_client(account="impulse"|"veille")`

### Nommage codes Shopify

Majuscules sans accents ni caractères spéciaux (sauf `-` pour les codes SAV `[PRENOM]-SAV`).

| Type | Format | Exemple |
|---|---|---|
| Affilié ambassadeur | `<PRENOM>` ou `<HANDLE>` | `FLORINE`, `ALEXTV`, `DODO`, `JBTRI` |
| Affilié Paid | variable | `LRA20` |
| Dotation | `<HANDLE>DOTATION` | `TRAILEURSDOTATION` |
| Crédit / Dotation ambassadeur | `<CODE>DOTATION` | `KIKISPORTIVEDOTATION`, `TRAILEURSDOTATION` |
| SAV client | `<PRENOM>-SAV` | `MARTIN-SAV` |
