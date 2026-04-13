# Session SAV — 2026-04-13

Passe service client Gorgias menée avec Antoine. Ce document couvre les tickets traités, les actions techniques effectuées (draft orders, refunds, correctifs MCP) et les protocoles qui en ressortent.

---

## 1. Tickets traités

### 1.1. Jean-Baptiste Morand — IMP6586 (ticket `#51805887`)

**Contexte**
- Commande 08/04/2026, 125,51 €, livraison point relais **Carrefour Express Lyon Créqui** (69006).
- Adresse personnelle : 2 Rue Maria Casares, 69100 Villeurbanne.
- Tracking Chronopost `PE272105673TS` : trié au point relais 11/04 05:07, puis **"Shipment returned to sender"** 39 min plus tard (05:46).
- Historique : c'est la **deuxième tentative** pour ce client (un premier colis avait déjà été retourné par un **autre** point relais sur une commande précédente).

**Diagnostic**
- Pas une erreur d'adresse client : deux points relais différents refusent successivement les colis. Cas totalement inhabituel côté Impulse.
- Le client demande explicitement un remboursement.

**Action**
- Réponse envoyée via Gorgias proposant deux options :
  1. Remboursement intégral de 125,51 €.
  2. Réexpédition gratuite à domicile (livraison directe, sans point relais) + bidon et shaker en geste commercial.
- En attente de la réponse du client pour déclencher l'option choisie.

---

### 1.2. Alexandre Damary — IMP4938 (ticket `#51799108`)

**Contexte**
- Commande 09/03/2026, 46,12 €, 3 produits : électrolytes citron ×1 + électrolytes pêche ×2, livraison point relais Pickup Elancia Issoire (63500).
- Adresse domicile : 4 Rue de la Font de Montel, 63570 Saint-Martin-des-Plains.
- Tracking Chronopost `PE272086038TS` : **1 mois bloqué** en boucle.

**Diagnostic tracking**
- 12–13/03 : `Packaging unsuitable` + `Shipment misrouted by transit location` (×2 fois).
- 16/03 : nouvelle mention `misrouted`.
- Du 18/03 au 10/04 : allers-retours quotidiens `Held at location` → `Sorted at delivery location`, plusieurs `delivery postponed by 24hrs`.
- Côté BigBlue le statut reste figé à `SHIPPED`, jamais livré.
- Le colis tourne en rond depuis presque un mois.

**Action 1 — Création d'une commande de remplacement (Shopify)**
- Draft order créée puis complétée : **IMP6923** (order_id `12564101628235`).
- Line items :
  - Électrolytes saveur citron ×1
  - Électrolytes saveur pêche ×2
  - **Bidon 750ml ×1** (geste commercial)
- Discount `SAV` 100 % appliqué (–55,60 €).
- Shipping forcé à `Expédition gratuite` 0,00 €.
- Tag `Service client`.
- Note interne : historique du blocage Chronopost + motif SAV.
- Total final : **0,00 €**, financial_status `paid`, fulfillment à la charge de BigBlue.
- Adresse livraison : domicile du client (pas de point relais). Antoine configure le point relais manuellement sur BigBlue après coup.

**Action 2 — Réponse Gorgias**
- Mail envoyé au client annonçant la réexpédition sous référence IMP6923 + bidon en geste commercial. Pas de récap technique du tracking (inutile au client).

---

### 1.3. Maxime Lecomte — IMP6831 (ticket `#51793717`, chat)

**Contexte client**
- Le client demande via chat si les deux sachets de whey échantillons ont **remplacé** le shaker offert promis par la promo Instagram "shaker offert dès 59 € d'achat".

**Vérification Shopify**
- Commande IMP6831 du 11/04, 92,02 €, fulfilled le 13/04 (Mondial Relay tracking `65102566`).
- Le **Shaker 450ml** est bien présent dans les line items, avec un discount 100 % intitulé "Shaker 450ml offert" (variant `51956593230155`).
- Les deux sachets `Whey Isolate saveur vanille - portion individuelle` et `Whey Isolate saveur chocolat - portion individuelle` sont un **cadeau automatique séparé** (auto-add-to-cart avec discount "Produit offert").
- **Pas de substitution** : les deux cadeaux se cumulent.

**Action**
- Réponse Gorgias rassurant le client : shaker bien inclus, sachets de whey en cadeau séparé, colis parti du jour via Mondial Relay.

---

### 1.4. Amandine Laurent — IMP6036 (ticket `#52032892`)

**Contexte**
- Commande 29/03/2026, 148,14 €, 62210 Avion (point relais LE DEAUVILLE).
- Le 01/04 Amandine demande un remboursement après retour d'une partie de la commande.
- 02/04 : réponse SC "remboursement dès réception du retour".
- 13/04 08:52 : Amandine relance, n'a toujours rien reçu.

**Vérification Shopify**
- Statut BigBlue `RETURNED` (colis revenu au dépôt).
- Financial status `partially_refunded`.
- **Refund déjà processé le 13/04 à 12:49** (via PayPal, authorization `1S6505468W2301626`) :
  - Montant : **50,18 €**
  - Scope : 2× Collagène marin Peptan® saveur cacao (ligne `36592237936971`)
  - Transaction kind `refund`, status `success`
- Les autres produits de la commande restent payés (pas retournés).

**Action**
- Draft rédigé, Antoine a envoyé la réponse lui-même (hors automation). Message confirmant le déclenchement du refund PayPal 50,18 € + délai 3–5 jours ouvrés + ouverture à confirmation si un autre retour est attendu.

> Remarque : c'est ce ticket qui a déclenché la révision du protocole Gorgias (voir §2.1) : il était absent de ma première passe limitée à 30 tickets, Antoine a dû le pointer manuellement.

---

### 1.5. Autres tickets SAV ouverts identifiés mais non traités cette session

Ces tickets étaient absents de la première passe (pull limité à 30). Ils sont à traiter lors de la prochaine session :

| # | Ticket | Client | Sujet | Tags |
|---|---|---|---|---|
| 1 | `#52052754` | Damien Poujol | Demande de contact support | statut_commande, urgent |
| 2 | `#52008486` | Anne Gaëlle Lannic | Order IMP5986 — Issue at delivery | urgent, retour/echange |
| 3 | `#51473749` / `#51473752` | Renaud Claus | BigBlue bad rating WITH comment | bigblue-bad-rating-with-comment |
| 4 | `#51489575` | Thibault Laboria | Order blocked — invalid address | bigblue-action-required |
| 5 | `#51799476` / `#51799478` | Patrice Buzare | BigBlue bad rating (internal) | bigblue-bad-rating-no-comment |

---

## 2. Protocoles et leçons

### 2.1. Protocole pull Gorgias — ne jamais rater un ticket

Raison du renforcement : passe initiale à 30 tickets, j'ai manqué Amandine Laurent et quatre autres SAV actifs.

**Règles strictes :**

1. Pour toute passe SAV, démarrer par `list_tickets(limit=100, order_by="updated_datetime:desc")`. Jamais moins.
2. Filtrer localement pour garder uniquement les tickets actionnables :
   - **Channels retenus** : `email`, `chat`, `contact_form`, `instagram`, `facebook`, `internal-note`.
   - **Tags à prioriser** : `urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`.
   - **À ignorer** : sujets préfixés `[SPAM POSSIBLE]`, réponses automatiques (`Réponse automatique`, `Automatic reply`), tickets `closed` qui ne sont que des bounces.
3. Si aucun SAV détecté ou doute sur un client cité par Antoine : 2e passe avec `order_by="created_datetime:desc"` pour rattraper les tickets au vieux `updated_datetime` mais au contenu récent.
4. **Si Antoine cite un client ou une référence absente de la liste** : le pull est trop court. Élargir avant de conclure "pas trouvé".
5. `search_tickets` est désormais fonctionnel (voir §3.1) mais sa stratégie reste une recherche client + fallback substring, pas une recherche full-text. Le protocole pull large reste le filet de sécurité principal.

### 2.2. Draft orders SAV — défauts obligatoires

Pour toute draft order de **réexpédition SAV** (replacement, perte colis, retour expéditeur, avarie) :

1. `applied_discount` : `{"title": "SAV", "value_type": "percentage", "value": "100.0", "description": "SAV"}` — remise 100 % avec motif SAV.
2. `shipping_line` : `{"title": "Expédition gratuite", "price": "0.00"}` — shipping forcé à 0 € avec le libellé "Expédition gratuite".
3. `tags` : `Service client`.
4. `note` : contexte court (référence commande d'origine, motif, gestes commerciaux ajoutés).

**Limitation technique à connaître :** `update_draft_order` ne permet pas de modifier les `line_items`. Si on doit ajouter/retirer un produit après création (ex : bidon en geste commercial), il faut **supprimer la draft et la recréer** avec les bons line items, puis réappliquer discount + shipping.

**Exemple concret :** draft IMP6923 pour Damary — 3 produits d'origine + bidon ajouté, discount SAV 100 %, shipping gratuit, total 0,00 €.

---

## 3. Correctifs techniques

### 3.1. Fix MCP Gorgias `search_tickets` (erreur 405)

**Symptôme**
- Tout appel à `search_tickets(query=...)` retournait `405 Client Error: Method Not Allowed` sur l'URL `https://impulse-nutrition-vitavea.gorgias.com/api/search?type=ticket&query=...`.

**Cause**
- L'ancienne implémentation (`gorgias_mcp/src/mcp_server.py`) faisait un `GET /api/search` avec `type=ticket`. Cet endpoint ne supporte plus la méthode GET sur cette instance Gorgias (ou a été déprécié).

**Correctif appliqué**
- Fichier : `gorgias_mcp/src/mcp_server.py`
- Nouvelle stratégie `search_tickets` :
  1. **Lookup customer** via `GET /api/customers?email={query}` (endpoint connu pour fonctionner, déjà utilisé par `search_customers`).
  2. Pour chaque customer trouvé, récupérer ses tickets via `GET /api/tickets?customer_id={id}&order_by=updated_datetime:desc`.
  3. **Fallback substring** : si `< limit` résultats, pull `GET /api/tickets?limit=100&order_by=updated_datetime:desc` et matcher la query (lower-cased) contre `subject`, `customer.name`, `customer.email`.
- Logs `warning` en cas d'exception (plutôt que propager et casser le tool).
- Retour identique à avant : `{"tickets": [...], "total": N}`.

**Ce que `search_tickets` fait maintenant**
- Recherche par **email** : reconnaît le customer directement et remonte ses tickets.
- Recherche par **nom** : fallback substring sur les 100 tickets récents, match le nom client.
- Recherche par **référence commande** (ex : IMP6036) : match dans le sujet des tickets récents (Gorgias inclut souvent la ref dans le subject via "[External] Order IMPxxxx - ...").
- Recherche par **mot-clé** quelconque : fallback substring.

**Ce que `search_tickets` ne fait pas**
- Pas de recherche full-text dans le corps des messages. Si besoin, il faudra une seconde passe via `list_ticket_messages` sur les tickets candidats.

**À faire côté Claude Code pour activer le fix**
- **Redémarrer Claude Code** (ou reload du MCP `gorgias`). Le serveur MCP charge `mcp_server.py` au lancement, le patch n'est pas hot-reloadé.
- Vérifier ensuite avec un appel de test : `search_tickets(query="wzamandine@gmail.com")` doit maintenant renvoyer au moins le ticket `#52032892`.

---

## 4. Mémoires auto ajoutées à ce tour

Les règles ci-dessus ont été persistées dans la mémoire auto du workspace pour que les futures conversations en bénéficient sans avoir à relire ce document :

- `feedback_sav_draft_order_defaults.md` — draft order SAV : discount 100 % SAV + shipping "Expédition gratuite" par défaut.
- `feedback_gorgias_sav_coverage.md` — pull Gorgias à 100 tickets minimum, filtrage par tags, ne jamais conclure sur une liste trop courte.

---

## 5. Récap des actions externes

| Action | Cible | Ref | Status |
|---|---|---|---|
| Réponse Gorgias | Morand | `#51805887` | Envoyée |
| Réponse Gorgias | Damary | `#51799108` | Envoyée |
| Réponse Gorgias | Lecomte | `#51793717` | Envoyée |
| Réponse Gorgias | Amandine Laurent | `#52032892` | Envoyée par Antoine |
| Commande SAV créée | Damary | `IMP6923` (0,00 €) | Paid, en attente fulfillment BigBlue |
| Memory feedback | — | `feedback_sav_draft_order_defaults.md` | Créée |
| Memory feedback | — | `feedback_gorgias_sav_coverage.md` | Créée |
| Patch MCP | Gorgias | `gorgias_mcp/src/mcp_server.py` `search_tickets` | Appliqué, attend redémarrage Claude Code |
