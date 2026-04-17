# TikTok SAV — workflow automatique

## TL;DR

Le skill `/tiktok-sav` pull les conversations TikTok Shop toutes les 10 min (cron), classifie chaque message buyer dans 1 des 10 catégories (T0-T9), envoie le bon template de réponse sans validation, et escalade vers une queue humaine pour les cas complexes. Zéro tutoiement, zéro invention hors template, 100% des SAV physiques (T2/T4/T5_A/T10/T11/T14) loggés dans la Google Sheet `TTS BB Actions` pour action BigBlue.

## Le concept

Pipeline à 6 étapes : **pull → dedup → classify → enrich → respond → queue**.

Pourquoi ça marche bien :
- **Templates figés** (fichier `knowledge/tiktok_sav/templates.md`) : la rédaction n'est jamais improvisée. Claude ne fait que classifier + remplir des variables. Zéro risque d'hallucination de ton ou de politique SAV.
- **Intelligence LLM réservée à la classification** : comprendre l'intention d'un message buyer (dosage ? plainte ? question livraison ?) est le seul endroit où on utilise le jugement. La réponse elle-même reste mécanique.
- **Queue humaine comme filet** : si le template demande une donnée manquante (produit pas dans le catalogue, raison de remboursement absente), le skill envoie un ACK poli + crée une entrée dans `queue.json`. Jamais de blocage, jamais de faux positif.
- **Dedup via state.json** : garantit qu'on ne répond jamais deux fois au même message, même si le cron fire pendant qu'on édite.

## Runtime (6 étapes)

### Étape 0 — Cycle retour BigBlue

Lit l'onglet `TTS BB Actions` du sheet SAV (`1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE`). Pour toute ligne où la colonne L = `Reponse recue` et la colonne N (Message envoyé TikTok) est vide, construit un message FR à partir de la réponse BigBlue et l'envoie au buyer. Marque la ligne comme `Traite`.

Si l'onglet est vide, skip silencieusement.

### Étape 1 — Pull

`mcp__tiktokshop__list_conversations(page_size=20)` récupère les conversations récentes triées par `latest_message.create_time`.

### Étape 2 — Dedup

Pour chaque conversation, lit `infra/data/tiktok_sav/state.json`. Clé = `conversation_id`, valeur = `{last_acked_message_id, last_replied_at, last_category}`.

Skip si :
- le dernier message buyer a déjà été acké (`last_acked_message_id` match)
- ou un message CUSTOMER_SERVICE arrive après le dernier buyer (notre côté a répondu en dernier)

### Étape 3 — Classify + enrich

Chaque message buyer est classifié par LLM dans une catégorie T0-T9 (voir tableau ci-dessous). Selon la catégorie, un enrichissement est effectué :

| Catégorie | Enrichissement |
|---|---|
| T1_TRACKING | lookup BigBlue pour vrai tracking |
| T2_DAMAGED | détection photo jointe |
| T4_MISSING | détection produit précisé |
| T5_ADDRESS | statut BigBlue (modifiable / en prépa / expédiée) |
| T7_PRODUCT | consultation `knowledge/catalog.yaml` |
| T8_REFUND | détection raison précisée |
| Autres | aucun |

### Étape 4 — Envoi + state

Template chargé, variables substituées, envoyé via `mcp__tiktokshop__reply_to_conversation`. Puis écriture de `state.json` avec le `buyer_msg_id` traité.

### Étape 5 — Queue + sheet BigBlue

Si la catégorie exige un suivi humain (T2, T4, T5_A, T7_B, T8, T10_B, T11, T14, UNKNOWN), création d'une entrée dans `infra/data/tiktok_sav/queue.json` avec order_id, statut, action suggérée.

Si la catégorie exige une action BigBlue physique (T2, T4, T5_A, T10_B, T11, T14), écriture d'une ligne dans le sheet `TTS BB Actions` (14 colonnes) avec message BigBlue FR pré-rédigé. L'humain copie-colle dans le helpdesk BigBlue, puis reporte la réponse dans le sheet → l'étape 0 du cycle suivant ferme la boucle côté buyer.

#### Pourquoi le Google Sheet `TTS BB Actions` est critique

Le sheet n'est pas un simple log : c'est **la colonne vertébrale du cycle retour BigBlue**. Il résout 3 problèmes :

1. **Ouverture de ticket BigBlue en 10 secondes.** Sans le sheet, pour chaque produit endommagé / manquant / colis perdu, il faudrait : aller dans BigBlue helpdesk → retrouver la commande IMPUS1XXXX → choisir le bon topic (`Report damaged products` / `Report missing products` / `Investigate a delivery never received`) → rédiger une description en FR avec les refs produit correctes. Avec le sheet, le skill pré-remplit tout (col K = message BigBlue complet prêt à coller, col J = lien direct vers la commande). L'humain ouvre, copie, colle, envoie. Gain : ~2 min par ticket, zéro erreur de formulation.

2. **Boucle asynchrone buyer ↔ BigBlue fermée automatiquement.** BigBlue répond parfois en 1h, parfois en 48h. Sans le sheet, il faudrait guetter la réponse manuellement puis re-contextualiser le cas côté buyer. Avec le sheet, l'humain copie la réponse BigBlue dans la col M + passe la col L à `Reponse recue` → au prochain cycle cron, l'étape 0 détecte ces lignes, construit un message FR pour le buyer à partir de la réponse BigBlue + contexte commande, l'envoie via TikTok, et marque `Traite`. Le buyer reçoit la bonne info sans qu'Antoine ait à rouvrir la conversation.

3. **Registre unique et auditable des SAV physiques.** Toutes les actions BigBlue (TikTok + Gorgias via un second onglet) atterrissent dans un seul sheet. On peut à tout moment : voir quelles commandes ont un problème en cours, exporter pour une review hebdo, mesurer la latence BigBlue par motif, identifier les SKUs qui génèrent le plus de réclamations. Impossible à faire proprement si chaque cas dort dans une conversation TikTok ou un thread Gorgias.

**Schéma de la boucle** :

```
Buyer TikTok → skill classifie T2/T4/T5_A/T10/T11/T14
            → ligne ajoutée au sheet (statut "A faire", message BigBlue pré-rédigé)
            → Antoine copie/envoie dans BigBlue helpdesk (~10s)
            → BigBlue répond (async, 1-48h)
            → Antoine colle réponse dans col M + passe col L à "Reponse recue"
            → skill détecte au prochain cycle (étape 0)
            → message FR envoyé au buyer TikTok
            → col L = "Traite", col N = message envoyé
```

Le sheet transforme un SAV physique multi-acteurs (buyer, seller, fulfillment) en un pipeline linéaire traçable, sans qu'aucune étape ne tombe entre deux chaises.

### Étape 6 — Rapport

Markdown avec : messages traités, cas queués, skips. Permet à Antoine de scanner rapidement ce qui s'est passé.

## Templates T0-T9 (aperçu)

| Tag | Sujet | Auto-send ? | Queue ? | Sheet BigBlue ? |
|---|---|---|---|---|
| T0 | ACK générique / UNKNOWN | Oui | Oui | Non |
| T1 | Question tracking | Oui (avec enrichissement BigBlue) | Non | Non |
| T2 | Produit endommagé | Oui | Oui | Oui |
| T3 | Code promo | Oui | Non | Non |
| T4 | Produit manquant | Oui | Oui | Oui |
| T5 | Modification adresse | Oui (3 variantes A/B/C) | Oui (variante A seulement) | Oui (variante A seulement) |
| T6 | Délai livraison | Oui | Non | Non |
| T7 | Question produit / dosage | Oui (A si doc trouvée, B sinon) | Oui (variante B) | Non |
| T8 | Retour / remboursement | Oui | Oui | Non |
| T9 | Merci / feedback positif | Oui | Non | Non |
| T10 | Produit périmé | Oui | Oui | Oui (10_B) |
| T11 | Colis perdu | Oui | Oui | Oui |
| T14 | Annulation commande | Oui | Oui | Oui (audit only) |

## Règles d'or

- **Persona service client** : vouvoiement, signature `Le service client` ou `L'equipe Impulse Nutrition`. Jamais signer "Antoine" côté TikTok Shop.
- **Jamais de tirets em** (`—`) dans aucun message, tous canaux.
- **Jamais inventer hors template** : si aucune variante ne correspond, fallback T0 + queue.
- **State.json mis à jour uniquement si un vrai message buyer a été traité**. Pas sur les chats ouverts côté seller center sans contenu buyer.

## Exemples réels — session du 17/04/2026

### Exemple 1 — sekouu224 (T8_REFUND, variante A)

**Contexte** : buyer clique sur "Je voudrais me faire rembourser" dans le menu chatbot TikTok. Le message apparaît avec `role=ROBOT` mais contient en réalité la sélection du buyer à la fin du prompt chatbot.

**Trace** :
- conv_id : `7623277830857048342`
- buyer_msg_id : `7629777123481815062`
- order_id : `576883946159577845` (livrée le 30/03/2026)

**Classification** : T8_REFUND, raison non précisée → variante A.

**Message envoyé** :
```
Bonjour,

Merci pour votre message. Nous sommes desoles d'apprendre que votre
experience n'a pas ete a la hauteur de vos attentes.

Pourriez-vous nous preciser la raison de votre demande afin que nous
puissions vous proposer la meilleure solution ?

Belle journee,
Le service client
```

**Queue** : entrée créée avec `priority=medium`, `suggested_action="Attendre la raison, puis vérifier Shopify + BigBlue, trancher sur remboursement intégral / partiel / remplacement"`.

**Pourquoi ça a bien marché** : le LLM a correctement inféré que le ROBOT-préfixé contenait la vraie intention buyer, malgré le masquage par le chatbot TikTok. Template envoyé à la seconde, queue en attente.

### Exemple 2 — usrwwxww (T7_PRODUCT, variante B → follow-up résolu)

**Contexte** : buyer demande le dosage d'un scoop de Créatine Creapure.

**Trace** :
- conv_id : `7628355799487840534`
- buyer_msg_id : `7629831117738460694`
- buyer_message : "bonjour j'ai une question un scop c'est combien de g?"
- order_id : `576883090355624402` (Créatine Creapure 102g, SKU VSCREAC)

**Classification** : T7_PRODUCT. Grep sur `knowledge/catalog.yaml` et `knowledge/**/*scoop*` : aucun résultat explicite pour la taille du scoop de cette SKU. Choix de la variante B (pas d'invention, ACK).

**Premier message envoyé** (variante B) :
```
Bonjour,

Merci pour votre interet pour nos produits ! Nous prenons note de votre
question et revenons vers vous avec les informations detaillees.

Belle journee,
Le service client
```

**Follow-up après validation Antoine** (3g confirmé) :
```
Bonjour,

Pour repondre a votre question : un scoop de notre Creatine Creapure
correspond a 3g.

N'hesitez pas si vous avez d'autres questions.

Belle journee,
Le service client
```

**Queue** : `status=resolved` une fois le follow-up envoyé.

**Pourquoi ça a bien marché** : le skill a refusé d'inventer (3g est un standard raisonnable mais pas sourcé dans le knowledge base), il a ACK rapidement pour rassurer le buyer, puis Antoine a validé la donnée en 1 instruction, suivi d'un send automatique. 2 messages, ~10 secondes, zéro risque de réponse inexacte.

### Exemple 3 — Détection correcte de non-message (aasly3, amayas_95, vithino73, etc.)

**Contexte** : TikTok affiche dans la liste des conversations des entrées avec `latest_message.sender.role=ROBOT` quand le shop envoie des notifications automatiques (commande reçue, colis expédié, livré, confirmation adresse). Ces conversations n'ont **aucun message texte buyer**, mais elles apparaissent dans `list_conversations`.

**Comportement du skill** : lit la conversation via `read_conversation`, scanne la liste des messages, trouve que tous ont `role=ROBOT` ou `role=SYSTEM`. Aucun `role=BUYER` → skip sans écrire state (pas besoin de marquer comme acké, aucun buyer message n'existe).

**Exemples de la session** : 8+ conversations ignorées correctement au cycle 1 (amayas_95, saan801, rachid.ben972, swaggynappy, fadoua_kimo, vithino73, usrwwxww avant son vrai message, md.isma_), puis aasly3 et riiri956 aux cycles suivants.

**Pourquoi ça a bien marché** : le filtre sur `role=BUYER` évite de traiter du bruit. Le skill reste idle tant qu'il n'y a pas de vrai input humain, ce qui garantit qu'il ne génère jamais de message non demandé.

## Pitfalls connus

- **Dedup par `conversation_id`, pas par `message_id`**. Une conversation peut accumuler plusieurs messages buyer ; seul le dernier traité est acké. Si un buyer envoie 2 messages successifs avant que le cron tourne, les 2 seront lus mais seul le plus récent sera répondu (les templates sont conçus pour couvrir le contexte cumulé).
- **"Chat started by CS"** = `role=SYSTEM`, pas un message buyer. Antoine peut ouvrir un chat côté seller center sans envoyer de message ; ne pas confondre.
- **Messages ROBOT contenant la sélection chatbot du buyer** : voir exemple 1 (sekouu224). Le format est un prompt chatbot + une ligne séparée par `\n\n` qui est la sélection buyer. À lire attentivement quand `role=ROBOT` mais contenu évoque une demande client.
- **MCP Google Sheets instable** : erreurs intermittentes `Can't assign requested address` (épuisement de ports locaux après un run long). Non bloquant pour TikTok lui-même mais bloque l'étape 0 ; reset du MCP suffit.
- **page_size limité à 10** pour `read_conversation` et 20 pour `list_conversations` (validation stricte côté TikTok API).

## Où trouver quoi

- **Skill** : `~/.claude/skills/tiktok-sav/SKILL.md`
- **Templates (source de vérité messages)** : `knowledge/tiktok_sav/templates.md`
- **Catalogue produit** : `knowledge/catalog.yaml`
- **Queue** (cas à traiter) : `infra/data/tiktok_sav/queue.json`
- **State** (dedup) : `infra/data/tiktok_sav/state.json`
- **Sheet SAV BigBlue** : `1O7zmLS8OTrYegIzZf7biKVisQo-knfPlR2xzeb1JnCE`, onglet `TTS BB Actions`
- **MCP tiktokshop** : `mcp__tiktokshop__list_conversations`, `read_conversation`, `reply_to_conversation`, `get_order_detail`
