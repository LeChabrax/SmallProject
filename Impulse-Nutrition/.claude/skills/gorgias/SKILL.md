---
name: gorgias
description: >
  Gorgias Impulse Nutrition — bulle de travail complète pour le service client (tickets SAV email/chat/contact_form/Instagram/Facebook/WhatsApp-via-WAX). Protocole bloquant à la demande : pull view Inbox côté serveur (filtrage natif via vues Gorgias), lecture thread complet, classification, carte de décision vouvoiement formel, draft reply + wait go + send + tag/close. Persona entité Impulse Nutrition (JAMAIS Antoine). Cross-links vers Shopify (draft replacement) et BigBlue (claims) pour les SAV physiques. Loop-safe. Triggers on: "/gorgias", "check le SAV", "check les tickets", "check Gorgias", "traite les tickets", "SAV update", "SAV check", "service client", "tickets ouverts", "répondre au ticket {id}", "draft reply ticket {id}", "fais un pass SAV", "passe SAV".
---

# Gorgias — Impulse Nutrition (service client, protocole bloquant)

Source de vérité unique pour tout travail Gorgias (tickets SAV tous canaux : email, chat, contact_form, Instagram, Facebook, WhatsApp via WAX).

> **Règles transversales** déjà actives via memory auto (pas besoin de les répéter ici) : `draft + go explicite avant envoi`, `lire thread avant drafter` (ici = `list_ticket_messages` complet), `no em dash`, `persona SC vs humain` (`feedback_gorgias_vs_instagram_tone.md`). Elles s'appliquent automatiquement.
>
> **Persona obligatoire** : entité **Impulse Nutrition**, vouvoiement formel. **❌ JAMAIS signer "Antoine"** côté Gorgias, même si c'est Antoine qui rédige. Exception ambassadeur : voir §Cas particulier en bas de ce fichier.

---

## §0 — Règles de style SC (canal-spécifique)

### Signature obligatoire
Au choix selon contexte :
- `Cordialement,\nLe service client Impulse Nutrition`
- `Très belle journée,\nLe service client Impulse Nutrition`
- `Cordialement,\nL'équipe Impulse Nutrition`

**❌ JAMAIS** : signature humaine, "Antoine", "Sportivement", "moi personnellement".

### Structure d'une réponse email
1. `Bonjour {Prénom},` (si prénom connu, sinon `Bonjour,`)
2. **1-2 phrases** : empathie courte + situation réelle reformulée
3. **1 phrase** : action concrète prise OU prochaine étape
4. Signature

### Ton
- **Vouvoiement** systématique (`vous`, `votre commande`). Jamais de tutoiement (exception ambassadeur connu, voir §Cas particulier).
- **Formel mais humain**, pas corporate.
- **❌ Jamais de délais chiffrés précis** (`48-72h`, `sous 24h`). Utiliser `"dès que nous avons du nouveau"`, `"dans les plus brefs délais"`, `"sous peu"`.
- **❌ Jamais de formules creuses** : pas de `"nous vous remercions de votre confiance"`, pas de `"nous vous avons bien reçu"`, pas de `"votre satisfaction est notre priorité"`.
- **Longueur medium** : ni trop court (froid), ni trop long (corporate). 4-8 lignes utiles.
- **Emojis rares** : uniquement `😊` si contexte positif. Zéro emoji sur un ticket SAV classique.
- **Canal WAX = WhatsApp** : même vouvoiement formel. Message poussé vers WhatsApp automatiquement par WAX après `reply_to_ticket`.
- **Messages au helpdesk BigBlue** (pas aux clients) : en **français**, c'est leur SOP.

---

## Protocole 8 étapes bloquant

> **Règle d'or** : chaque étape citée explicitement dans la carte de décision. Si une étape manque → refuser de drafter.

### Étape 0 — Check BigBlue_Actions (priorité absolue, avant tout pull)

Avant le pull tickets, scanner l'onglet `BigBlue_Actions` du sheet SAV (`1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE`) :

```
mcp__google_sheets__get_sheet_data(spreadsheet_id="1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE", sheet="BigBlue_Actions")
```

**Schéma colonnes (référence) :**
`A=ID Ticket Gorgias | B=Date | C=Source | D=Client | E=N° Shopify | F=N° BigBlue | G=Motif | H=Résumé | I=Lien Gorgias | J=Lien BigBlue | K=Lien BigBlue nouvelle commande | L=Message BigBlue | M=Statut BB | N=Réponse BigBlue | O=Message envoyé Gorgias | P=Statut Gorgias | Q=Action Shopify | R=Draft Shopify ID | S=Lien draft Shopify | T=Statut Shopify`

**Statuts valides pour M :** `A faire` → `En cours` → `Réponse reçue` → `Traité`

Filtrer les lignes où **M = "Réponse reçue"** ET **N non vide** (réponse BigBlue collée par Antoine).

Pour chaque ligne trouvée :
1. Lire : D (Client), E (N° Shopify), G (Motif), H (Résumé), A (ID Ticket Gorgias), N (Réponse BigBlue)
2. Rédiger un draft de réponse client adapté au contenu de M :
   - BigBlue confirme perte/perdu → proposer renvoi ou remboursement (au choix client)
   - BigBlue enquête encore → informer le client, délai vague, excuses
   - BigBlue confirme livraison prochaine → rassurer avec date estimée
3. Présenter la carte condensée + draft → **wait "go"**
4. Déterminer **Action Shopify** depuis N (réponse BigBlue) → remplir Q :
   - "perdu" / "jamais livré" / "introuvable" → Q = "Draft replacement"
   - "remboursement accordé" → Q = "Remboursement manuel"
   - "enquête en cours" / "investigation" → Q = "Aucune (attente)"
5. Si Q = "Draft replacement" :
   - Récupérer customer_id Shopify depuis E (N° commande) via `mcp__shopify_orders__get_order`
   - Créer le draft : `mcp__shopify_orders__create_draft_order` (discount 100% SAV + shipping 0€ + tag `Service client` + customer_id numérique)
   - Remplir R = draft ID, S = lien admin Shopify, T = "A confirmer"
   - Après `complete_draft_order`, récupérer le nom de la nouvelle commande (ex: IMP7098) → remplir K = `https://app.bigblue.co/orders/IMPUS100{numéro}`
6. Présenter à Antoine : draft reply Gorgias + récap Shopify (R/S/T si applicable) → **wait "go"**
7. Après "go" :
   - `mcp__gorgias__reply_to_ticket(ticket_id=A, body=draft)`
   - Si T = "A confirmer" : `mcp__shopify_orders__complete_draft_order(draft_id=R)` → T = "Commande envoyée"
   - Vérifier le statut du ticket via `mcp__gorgias__get_ticket(id=A)` → récupérer `status`
   - Mettre à jour la ligne via `batch_update_cells` :
     - M = "Traité"
     - O = texte du message envoyé (le draft validé)
     - P = statut Gorgias réel (open / closed / snoozed)

Si aucune ligne "Réponse reçue" → passer à la partie WAX ci-dessous.

**Sortie citée** : `Étape 0a ✅ — BigBlue_Actions : {N} lignes "Réponse reçue" traitées` OU `Étape 0a ✅ — Aucune réponse BigBlue en attente`

#### Partie WAX — Drafts WhatsApp

Scanner l'onglet `WAX` du même sheet :

```
mcp__google_sheets__get_sheet_data(spreadsheet_id="1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE", sheet="WAX")
```

**Schéma colonnes WAX :**
`A=Date | B=Client | C=Lien chat WAX | D=Message client | E=Draft réponse | F=Lien BigBlue | G=Message BigBlue | H=Statut`

**Statuts valides pour H :** `A traiter` → `Draft prêt` → `Envoyé`

Filtrer les lignes où **H = "A traiter"** ET **D non vide**.

**Schéma colonnes WAX complet :**
`A=Date | B=Client | C=Lien chat WAX | D=Message client | E=Draft réponse | F=Lien BigBlue | G=Message BigBlue | H=Statut | I=Action Shopify | J=Draft Shopify ID | K=Lien draft Shopify | L=Statut Shopify`

**Statuts valides pour L (Shopify) :** `A confirmer` → `Confirmé` → `Commande envoyée` / `Annulé`

Pour chaque ligne trouvée (H = "A traiter") :
1. Lire D (message client) et B (nom client)
2. Rédiger E — **même persona que Gorgias** : vouvoiement formel, entité Impulse Nutrition, no em dash, no délais chiffrés, structure empathie + action + signature `Le service client Impulse Nutrition`
3. Si problème livraison/commande dans D → remplir F (lien BigBlue) + G (message FR pour BigBlue) si order_id identifiable
4. Déterminer Action Shopify → remplir I :
   - Antoine a déjà renseigné I = "Draft replacement" → créer le draft directement
   - Message indique clairement renvoi nécessaire → I = "Draft replacement"
   - Pas assez d'infos (pas de N° commande) → I = "Infos manquantes (N° commande ?)" et intégrer la demande dans E
   - Pas d'action Shopify → I = "Aucune"
5. Si I = "Draft replacement" ET N° commande identifiable :
   - `mcp__shopify_orders__get_order` pour récupérer customer_id + line_items
   - `mcp__shopify_orders__create_draft_order` (discount 100% SAV + shipping 0€ + tag `Service client` + customer_id numérique)
   - Remplir J = draft ID, K = lien admin Shopify, L = "A confirmer"
6. Mettre H = "Draft prêt" via `batch_update_cells`
7. Présenter à Antoine : draft E + récap Shopify (J/K/L si applicable). **Aucun envoi automatique WAX** (pas d'accès). Attendre "go" pour le draft Shopify uniquement.
8. Après "go" : `mcp__shopify_orders__complete_draft_order(draft_id=J)` → L = "Commande envoyée"

Antoine envoie manuellement E depuis WAX, puis passe H = "Envoyé".

**Sortie citée** : `Étape 0b ✅ — WAX : {N} drafts rédigés` OU `Étape 0b ✅ — Aucun message WAX en attente`

---

Si aucune ligne "Réponse reçue" ni "A traiter" → passer directement à l'Étape 1.

**Sortie citée globale** : `Étape 0 ✅ — BigBlue_Actions : {N} | WAX : {N} drafts`

---

### Étape 1 — Pull tickets (3 canaux en parallèle)
> ⚠️ **NE PAS utiliser la view système `open` (33360)** pour le pass quotidien : elle filtre implicitement sur `assignee = Antoine Chabrat` et exclut tous les tickets non-assignés (la majorité des tickets ouverts).

- Pass quotidien : **3 pulls par canal en parallèle** (couvre tous les tickets ouverts tous assignees, non-spam, non-snoozed) :
  - `mcp__gorgias__list_tickets(channel="email", limit=50, order_by="updated_datetime:desc")` (view 44348)
  - `mcp__gorgias__list_tickets(channel="contact_form", limit=50, order_by="updated_datetime:desc")` (view 44386)
  - `mcp__gorgias__list_tickets(channel="chat", limit=50, order_by="updated_datetime:desc")` (view 45597)
- Merger les 3 résultats, dédupliquer par `id` (overlap rare mais possible si un ticket a plusieurs canaux).
- Recherche historique (ticket fermé / ancien) : `list_tickets(status="all", limit=100)` ou `mcp__gorgias__search_tickets(query="email|nom|id_numérique")`.
- Ticket précis connu : `mcp__gorgias__get_ticket(id=...)` direct.

Tags à prioriser, exclusions, sortie citée → **[reference/pull_protocol.md](reference/pull_protocol.md)**

**Loop-safe** : si en `/loop`, filtrer `updated_datetime > last_run_timestamp` via state minimal `~/.claude/skills/gorgias/last_run.txt`.

**Sortie citée** : `Étape 1 ✅ — Pull 3 canaux (email {Ne} + contact_form {Ncf} + chat {Nc} = {N} tickets) → {M} actionnables après filtrage (tags {...})`

### Étape 2 — Lire le thread complet + auto-skip si SC a déjà répondu

`mcp__gorgias__list_ticket_messages(ticket_id=...)` — **tous** les messages, pas juste le dernier. Identifier les `order_id` format `IMP####` mentionnés.

**🚨 AUTO-SKIP bloquant** : règle transversale `feedback_waiting_customer_reply.md` en memory auto. Dès que les messages sont chargés, vérifier `last_message.from_agent`. Si `true` → **skip Étapes 3 à 8** pour ce ticket, produire carte condensée 1 ligne `## Ticket #{id} · ✅ en attente client. SC a répondu le {date}. Pas d'action.` puis passer au suivant.

**⚠️ Exception auto-ack Gorgias** : le SC humain envoie depuis la même adresse que l'auto-ack (`contact@impulse-nutrition.fr`), donc **`sender.address` seul ne suffit pas** à distinguer. Discriminer sur le **body du message** :

- Si `last_message.from_agent == true` ET `last_message.body_text` contient **l'une** des phrases suivantes (normalisées lowercase, sans accent si besoin) → c'est l'auto-ack :
  - `"nos équipes sont disponibles"`
  - `"nous vous répondrons dans les plus brefs délais"`
  - `"votre message a bien été reçu"`
  - `"nous avons bien reçu votre message"`

Dans ce cas → **ne pas skip**, continuer Étapes 3-8 comme si aucun SC humain n'avait répondu.

À l'inverse si `last_message.from_agent == true` ET body ne contient AUCUN marqueur d'auto-ack → c'est un vrai SC reply humain → **skip** (même si `sender.address == "contact@impulse-nutrition.fr"`).

Si `last_message.from_agent == false` (client a répondu en dernier ou aucun SC reply) → continuer Étapes 3-8.

**Sortie citée** : `Étape 2 ✅ — {N} messages lus (dernier client : {date}, dernier SC : {date ou "aucun"}, last_from_agent : true/false)`

### Étape 3 — Customer lookup

`mcp__gorgias__get_customer(customer_id=...)` ou `search_customers(email=...)`. Récupérer `firstname`, `lastname`, `email`, `orders_count`, `total_spent`.

**Cross-check ambassadeur via `find_in_spreadsheet`** — À appeler **UNIQUEMENT** si au moins une de ces conditions est remplie :
- **(a)** Le ticket mentionne `code affilié`, `Affiliatly`, `mes crédits`, `code personnalisé`, `20€ de crédit`, `mon code ne marche pas`
- **(b)** Le customer name/email ressemble à un pseudo Instagram (tag `@`, handle type `pseudo_insta`, nom manifestement non-civil)
- **(c)** Le ticket est catégorisé `question_affiliate_code` à l'Étape 5
- **(d)** Antoine exprime un doute explicite ("est-ce qu'il est ambassadeur ?")

Sinon → **skip le cross-check** et noter `"skip find_in_spreadsheet (non-ambassadeur probable)"` dans la sortie. Raison : 90% des tickets SC ne concernent pas les ambassadeurs, faire le cross-check systématique gaspille des appels Sheet et ajoute du bruit dans la carte de décision.

Si cross-check appelé ET match trouvé (`Suivi_Amb` / `Suivi_Dot` / `Suivi_Paid`) → **STOP draft automatique** et signaler à Antoine (voir §Cas particulier ambassadeur en bas de ce fichier).

**Sortie citée** : `Étape 3 ✅ — Customer : {Prénom Nom} ({email}) | {N} commandes | total {€} | ambassadeur : oui/non/skip`

### Étape 4 — Commande(s) liée(s) + lookup external
Si le ticket concerne une commande physique :
- `mcp__shopify__get-order-by-id` ou `mcp__shopify_orders__get_order` : `line_items`, `shipping_address`, `financial_status`, `fulfillment_status`, `tags`
- `mcp__bigblue__get_order` : `status` (SHIPPED / DELIVERED / RETURNED / CANCELLED)
- `mcp__bigblue__get_tracking` si livraison bloquée/en transit

**Sortie citée** : `Étape 4 ✅ — Commande {IMP####} : Shopify={status}/{fulfillment} BigBlue={status} | {line items courts}` OU `pas de commande liée`

### Étape 5 — Classification + template
Choisir UNE catégorie mutuellement exclusive (G0-G17) puis sélectionner la **variante** selon l'enrichissement Étape 3-4. Deux références obligatoires :
- Table des 17 catégories + mapping action → **[reference/categorization.md](reference/categorization.md)**
- Templates pré-rédigés par catégorie (fournissent le squelette du draft Étape 6) → **[reference/templates.md](reference/templates.md)**

Le draft à l'Étape 6 part **toujours** du template de la variante choisie (placeholders remplis avec contexte), puis adapté si besoin. **Règle intacte** : le template reste un brouillon, `reply_to_ticket` n'est envoyé qu'après `"go"` explicite (Étape 7).

**Sortie citée** : `Étape 5 ✅ — Catégorie : {cat} · Template : {G#-variante} → Action : {reply seul | reply + draft Shopify | reply + BigBlue claim | reply + code SAV | escalade Antoine}`

### Étape 6 — Carte de décision (format imposé)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Ticket #{ticket_id}  ·  {channel}  ·  Tag: {tag_principal}

{Prénom Nom}  ·  {email}  ·  {N} commandes  ·  {"ambassadeur" si oui}

### Checks
- Étape 1 ✅ Pull view Inbox → {N} actionnables
- Étape 2 ✅ {N} messages lus (dernier client : {date})
- Étape 3 ✅ Customer : {...}
- Étape 4 ✅ Commande {IMP####} : {...} (ou "pas de commande liée")
- Étape 5 ✅ Catégorie : `{cat}` · Template : `{G#-variante}` → Action : {...}

### Derniers messages (cités)
> [DATE] client : "{verbatim court}"
> [DATE] SC : "{verbatim dernière réponse interne}" (ou "aucune réponse SC précédente")

### Action mécanique (hors draft)
{liste : draft Shopify replacement, BigBlue claim, update adresse, refund manuel, etc. — oui/non par item}

### Draft reply
Bonjour {Prénom},

{corps selon §0 : empathie + situation + action}

Cordialement,
Le service client Impulse Nutrition

→ Tape **"go"** pour envoyer, ou corrige le draft.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Cas non-draftables** (ambassadeur détecté, classification incertaine, escalade) : carte **sans section Draft**, à la place `### Action manuelle requise` + raison + décision demandée à Antoine.

### Étape 7 — Wait "go" explicite
Règle en memory auto. Seuls `"go"`, `"envoie"`, `"c'est bon envoie"`, `"yes go"`, `"send"` valident. `"c'est good"`, `"bon raisonnement"` ne valident PAS. **Bloquant aussi pour les mutations Shopify / BigBlue** (create_draft_order, create_support_ticket, update_order).

### Étape 8 — Execute + tag + close
1. **Actions mécaniques préalables** (si listées Étape 6) :
   - Draft replacement Shopify → **[reference/sav_recipe.md](reference/sav_recipe.md)** pour defaults (discount 100% SAV + shipping 0€ + tag `Service client` + customer_id numérique) et quirks (update_draft_order sur line_items impossible, pickup point BigBlue manuel)
   - BigBlue claim (MCP cassé → log sheet obligatoire) :
     1. Récupérer `bigblue_order_id` via `mcp__bigblue__get_order(reference=IMP####)` si pas déjà fait à l'Étape 4
     2. Rédiger le message FR complet (topic + description : produits, quantités, problème détaillé)
     3. Écrire ligne dans l'onglet `BigBlue_Actions` du sheet SAV (`1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE`) via `mcp__google_sheets__add_rows` :
        - Date : aujourd'hui (format JJ/MM/AAAA)
        - Source : "Gorgias"
        - Client : nom du client (ticket customer)
        - N° Shopify : IMP#### (référence Shopify)
        - N° BigBlue : IMPUS1XXXXXX (depuis `get_order`)
        - Motif : "Produit manquant" | "Produit endommagé" | "Mauvaise livraison" | "Jamais reçu" | "Colis retardé/bloqué"
        - Résumé : 2-3 phrases du contexte (problème client + statut BigBlue + historique)
        - Lien Gorgias : `https://impulse-nutrition.gorgias.com/app/tickets/{ticket_id}`
        - Lien BigBlue : `https://app.bigblue.co/orders/{bigblue_order_id}`
        - Lien BigBlue nouvelle commande : (vide à ce stade — à remplir après `complete_draft_order` si renvoi accordé)
        - Message BigBlue : message FR complet prêt à coller dans l'UI BigBlue (topic + description)
        - Statut : "A faire"
     4. Confirmer à Antoine : "Ligne ajoutée dans BigBlue_Actions — à déposer manuellement sur l'UI BigBlue"
     
     Mapping motif → topic BigBlue : "Produit manquant" = `Report missing products` | "Produit endommagé" = `Report damaged products` | "Mauvaise livraison" = `Report the delivery of wrong products` | "Jamais reçu" = `Investigate a delivery never received by the customer` | "Colis retardé/bloqué" = `Investigate a delayed order`
   - Refund → **manuel via Shopify admin UI** (MCP refund pas implémenté)
   - Update adresse → `mcp__shopify__update-order` ou `mcp__bigblue__update_order` selon timing
2. **Reply** : `mcp__gorgias__reply_to_ticket(ticket_id, body=draft_validé)`
3. **Tag + close** :
   - Si besoin : `assign_ticket` à la bonne personne
   - `close_ticket` uniquement si la conversation est résolue. Laisser `open`/`pending` si on attend une réponse du client.
4. **Confirmer à Antoine** : récap 1 ligne "Ticket #{id} → reply envoyée + {actions annexes} + {close/laisser open}".
5. **Update state loop** si en `/loop` : écrire `last_run_timestamp`.

---

## Red flags critiques (5 qui comptent)

1. ❌ **Conclure "pas trouvé" sans avoir essayé `search_tickets` puis `status="all"`** — la vue Inbox ne contient que les ouverts ; un ticket fermé ou ancien doit être cherché explicitement.
2. ❌ **Signer "Antoine"** / signature humaine — toujours `Le service client Impulse Nutrition`
3. ❌ **Délais chiffrés** (`48-72h`, `sous 24h`) → `"dès que nous avons du nouveau"`
4. ❌ **Formules creuses** : "nous vous remercions de votre confiance", "votre satisfaction est notre priorité"
5. ❌ **Promettre un remboursement** avant validation de faisabilité (Shopify refund manuel)

Liste exhaustive (15+ items) → **[reference/red_flags.md](reference/red_flags.md)**

---

## §Cas particulier — Ambassadeur qui contacte le SAV

Si l'Étape 3 détecte que le customer est dans `Suivi_Amb` / `Suivi_Dot` / `Suivi_Paid` :

1. **STOP draft automatique** → signaler à Antoine : `"Ticket SAV de {nom}, qui est ambassadeur ({tab}, statut {J}). Tu réponds toi-même ou j'envoie une réponse SC standard ?"`
2. Si Antoine répond lui-même → il peut tutoyer / signer `Antoine`. Pas de draft SC.
3. Si Antoine dit "réponse SC standard" → drafter en vouvoiement formel comme n'importe quel client final, **SANS mentionner qu'il est ambassadeur** dans le message.
4. **Le tag de la commande de remplacement reste `Service client`** (c'est un SAV, pas une dotation, même pour un ambassadeur).

---

## Compatibilité /loop

Invocations possibles : `/loop 30m /gorgias`, `/loop 1h /gorgias`, `/loop /gorgias` (self-paced).

**État loop tracking** : `~/.claude/skills/gorgias/last_run.txt` avec timestamp ISO du dernier pull réussi. Au prochain run : filtrer `updated_datetime > last_run_timestamp`. Si le fichier n'existe pas → pull complet.

**Rien à traiter** : si après filtrage aucun ticket actionnable, renvoyer `"✅ Aucun ticket SAV actionnable (pull {N} → filtré à 0)"` et terminer proprement sans erreur.

---

## Références canoniques (docs projet)

- Process SAV unifié détaillé : [`/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#sav--opérations-client`](/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#sav--opérations-client)
- Création codes `[PRENOM]-SAV` : [`/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#créer-un-code-affilié-ambassadeur`](/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#créer-un-code-affilié-ambassadeur)
- Création draft orders : [`/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#créer-un-draft-order-sav-ou-dotation`](/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#créer-un-draft-order-sav-ou-dotation)
- Catalogue Shopify : [`/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/impulse.md#4-catalogue-produits`](/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/impulse.md#4-catalogue-produits)
- MCPs disponibles : [`/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#quirks-techniques-transverses`](/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/knowledge/operations.md#quirks-techniques-transverses)
- Persona Gorgias : [`/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/gorgias_mcp/personality.md`](/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/gorgias_mcp/personality.md)
