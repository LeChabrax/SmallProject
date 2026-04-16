# Deck formation interne — IA agentique & outillage Impulse

> **Public cible** : équipe HCS/Impulse novice en IA agentique.
> **Durée** : ≈50 min présentation + 10-15 min Q&A.
> **Format** : 18 slides, à importer dans Google Slides.
> **Auteur** : Antoine Chabrat, Influence Manager.
> **Version** : avril 2026.

---

## Table des matières

| Acte | Thème | Slides | Durée |
|---|---|---|---|
| 1 | Comment ça marche (concepts + GitHub central) | 1-5 | 12 min |
| 2 | Les MCPs qu'on utilise (tour par plateforme) | 6-11 | 12 min |
| 3 | Workflows en production | 12-15 | 15 min |
| 4 | Idées de création (prospective) | 16-17 | 8 min |
| 5 | Clôture | 18 | 3 min |
| — | Q&A | — | 10-15 min |

---

## ACTE 1 — Comment ça marche

### Slide 1 — Cover

**Titre principal** : L'IA chez Impulse
**Sous-titre** : Agents, GitHub, MCPs : le socle technique de l'influence
**Pied** : Formation interne · avril 2026 · Antoine Chabrat

**Visuel suggéré** : fond Impulse (vert/noir), logo au centre, en bas 3 pictos alignés (un cerveau = agent, un octocat = GitHub, une prise USB = MCP).

**Notes orateur** :
> Bienvenue. En 50 min, je veux vous montrer concrètement comment l'IA agentique change le travail d'un influence manager. On va d'abord poser les concepts, puis on va ouvrir le capot sur ce qu'on a branché chez Impulse, et enfin on regardera les prochains chantiers.

---

### Slide 2 — C'est quoi un "agent IA" en 2 min

**Titre** : Un agent = cerveau + mains + mémoire

**Bullets** :
- Le **cerveau** : un modèle (Claude Opus, GPT-5, Gemini…) qui raisonne en langage naturel.
- Les **mains** : des outils qu'il peut déclencher (lire un fichier, modifier un Sheet, appeler une API Shopify).
- La **mémoire** : des règles persistantes qu'il applique à chaque session (persona Antoine vs Service client, tone, process SAV).
- Différence avec ChatGPT web : **il agit**, il ne rédige pas juste. Plus de copier-coller.

**Visuel suggéré** : schéma minimaliste. Un rond central "Agent" avec 3 branches : Cerveau (ampoule), Mains (outils), Mémoire (livre ouvert).

**Notes orateur** :
> La friction de ChatGPT web, vous la connaissez : on copie l'export, on colle la question, on colle la réponse ailleurs. Un agent vit dans votre environnement de travail. Vous dites "fais ça", il fait, il lit le résultat, il corrige si besoin. C'est le shift conceptuel central.

---

### Slide 3 — Panorama rapide des agents CLI en 2026

**Titre** : 4 agents, 4 écosystèmes

| Agent | Cerveau | Éditeur | Pour qui |
|---|---|---|---|
| **Claude Code** | Claude Opus / Sonnet | Anthropic | Raisonnement long, contexte 1M tokens, écosystème MCP mature |
| **Codex CLI** | GPT-5 / o-series | OpenAI | Écosystème ChatGPT, grande communauté |
| **Gemini CLI** | Gemini 2.5 Pro | Google | Quota gratuit généreux, intégration Workspace |
| **GitHub Copilot CLI** | Mix (Claude, GPT) | GitHub / Microsoft | Intégration GitHub native, PR reviews |

**Bullets bas de slide** :
- Chez Impulse, on a choisi **Claude Code** pour 3 raisons : contexte long, qualité de raisonnement, écosystème MCP.
- Ce n'est pas une religion : on peut mixer plusieurs agents selon les tâches.

**Notes orateur** :
> Les 4 sont conceptuellement similaires : agent + outils + modèle. La vraie différence c'est "quel cerveau, quel écosystème". Je montre les 4 pour que vous sachiez situer quand vous entendrez les noms. On enchaîne maintenant sur LE point central : comment GitHub rentre dans l'histoire.

---

### Slide 4 — LE schéma central : GitHub au cœur du dispositif

**Titre** : Un seul socle, plusieurs utilisateurs

**Schéma principal** (occupe toute la slide) :

```
   ┌──────────┐      ┌──────────┐      ┌──────────────┐      ┌──────────┐
   │ Antoine  │      │ Collègue │      │ Prestataire  │      │  Futur   │
   │Claude Cod│      │Claude Cod│      │ Claude Code  │      │remplaçant│
   └─────┬────┘      └─────┬────┘      └──────┬───────┘      └────┬─────┘
         │                 │                  │                   │
         └─────────────────┴────────┬─────────┴───────────────────┘
                                    │
                             pull ▲ │ ▼ push
                                    │
                        ┌───────────▼────────────┐
                        │        GitHub          │
                        │   Impulse-Nutrition    │
                        │  (repo, historique,    │
                        │   docs, scripts, MCPs) │
                        └───────────┬────────────┘
                                    │
             ┌────────────┬─────────┼─────────┬─────────────┐
             ▼            ▼         ▼         ▼             ▼
         Shopify      Gorgias    BigBlue  Instagram    TikTok Shop
         Sheets       Drive      Canva    Gmail        …(65+)
```

**Bullets à côté du schéma** :
- GitHub = **le socle unique** où vivent le code, les docs, les règles métier, les MCPs.
- Chaque utilisateur (toi, un collègue, un prestataire, un futur remplaçant) lance son Claude Code, qui lit le même repo.
- `pull` = je récupère ce que les autres ont poussé. `push` = je partage ce que j'ai fait.
- **Résultat** : tout le monde bosse avec les mêmes outils, les mêmes règles, la même mémoire. Aucune perte de know-how.

**Notes orateur** :
> C'est LE slide à retenir. Avant, quand on construisait un outil, il restait sur le PC de celui qui l'avait fait. Si la personne partait, l'outil partait avec. Avec GitHub au centre, **l'outil est indépendant de la personne**. Un stagiaire arrive, il clone le repo, son Claude Code connaît déjà la persona, les règles, les process. C'est ça qui rend l'IA durable chez nous. Ce n'est pas "Antoine utilise l'IA", c'est "Impulse a un socle, et tout le monde s'y branche".

---

### Slide 5 — MCP : la prise USB entre l'agent et les plateformes

**Titre** : MCP = le standard ouvert qui connecte tout

**Schéma** :
```
              ┌───────────────┐
              │  Claude Code  │
              └───────┬───────┘
                      │ MCP (protocole standard)
     ┌────────┬───────┼────────┬──────────┐
     ▼        ▼       ▼        ▼          ▼
  Shopify  Gorgias BigBlue Instagram TikTok Shop
```

**Bullets** :
- **MCP** = Model Context Protocol. Standard ouvert lancé par Anthropic en **novembre 2024**.
- **Avant** : chaque outil avait son intégration maison, fragile, à maintenir une par une.
- **Après** : format standardisé. On branche un MCP, l'agent sait immédiatement s'en servir.
- **Analogie** : avant les prises USB, chaque appareil avait son connecteur. Maintenant, une seule prise pour tout. Le MCP fait la même chose entre l'IA et vos outils.

**Notes orateur** :
> Gardez cette analogie "prise USB". Chaque fois qu'on parlera de MCP dans la suite, ça veut dire "on a branché une nouvelle plateforme sur Claude Code". Et on a 65+ tools connectés aujourd'hui. On va en parcourir les principaux juste après.

---

## ACTE 2 — Les MCPs qu'on utilise

### Slide 6 — Panorama des MCPs branchés chez Impulse

**Titre** : 10 MCPs, 65+ tools, tous en production

**Visuel suggéré** : grille avec 10 logos (Shopify, Gorgias, BigBlue, Instagram DMs, Instagram Veille, TikTok Shop, Google Sheets, Google Drive, Canva, Gmail). Sous chaque logo, le nombre de tools exposés.

**Bullets** :
- 4 MCPs **custom** (codés en interne) : `shopify_orders`, `gorgias_mcp`, `bigblue_mcp`, `instagram_dms` + `instagram_veille`.
- 6 MCPs tiers branchés : Google Sheets, Google Drive, Canva, Gmail, TikTok Shop, Firebase.
- Certains MCPs officiels n'existent pas encore (ex : BigBlue n'a pas d'API publique), on construit le MCP nous-mêmes.

**Notes orateur** :
> Ce qui est intéressant, c'est qu'on n'est pas dépendants des plateformes qui livrent leurs propres MCPs. Quand BigBlue n'a pas d'API publique, on reverse-engineer leur back-office et on construit le MCP. C'est un investissement, mais c'est ce qui nous permet d'avoir un agent qui agit vraiment partout.

---

### Slide 7 — MCP Shopify

**Titre** : MCP Shopify — piloter la boutique depuis l'agent

**Ce que l'agent peut faire** :
- Créer et compléter des **draft orders** (SAV, dotation, replacement).
- Rechercher clients, commandes, produits.
- Appliquer des **remises et tags** (`Service client`, `Dotation influenceur`) pour sortir du CA HCS.
- Créer des **codes de réduction** (pour les codes crédit ambassadeurs).
- Lire les variants, les prix, le stock.

**Visuel suggéré** : capture Shopify admin + flèche MCP + capture du tool `create_draft_order` en cours d'exécution.

**Notes orateur** :
> C'est le MCP le plus sollicité au quotidien. Chaque SAV, chaque dotation, chaque code crédit passe par lui. Le MCP custom est conçu pour suivre **nos** règles (toujours passer `customer_id` et pas `email`, toujours taguer, toujours appliquer la remise SAV). Ces règles sont dans la mémoire de l'agent, donc il les applique sans qu'on ait à les répéter.

---

### Slide 8 — MCP Gorgias

**Titre** : MCP Gorgias — lire et répondre au service client

**Ce que l'agent peut faire** :
- Lire tous les tickets, filtrer par channel, status, tag.
- Lire le **thread complet** d'un ticket (obligatoire avant de rédiger une réponse).
- Rédiger et envoyer des réponses en **vouvoiement formel**, persona "Service client".
- Assigner, fermer, taguer.
- Chercher un client par email, téléphone, commande.

**Règle métier appliquée automatiquement** :
- Signature = `L'équipe Impulse Nutrition` ou `Le service client` (jamais "Antoine").
- Excuses automatiques si la réponse est > 4 jours de retard (légère) ou > 10 jours (appuyée).

**Notes orateur** :
> Point important sur la persona : Gorgias = vouvoiement, entité Impulse. Instagram DM = tutoiement, persona Antoine. L'agent applique la bonne persona selon le MCP utilisé, sans qu'on ait à le lui rappeler. C'est ça qui sort l'agent du "chatbot générique" pour en faire un vrai collègue.

---

### Slide 9 — MCP BigBlue (avec une limite à expliquer)

**Titre** : MCP BigBlue — fulfillment + une frontière claire

**Ce que l'agent peut faire** :
- Lister les commandes fulfillment (en préparation, expédiées, livrées).
- Consulter le **tracking** (Chronopost / Mondial Relay).
- Modifier un **pickup point** ou une adresse avant préparation.
- Annuler une commande avant fulfillment.
- Consulter les **stocks par SKU**.

**⚠️ Limite actuelle (slide encadré rouge clair)** :
- **Impossible d'ouvrir, lire ou répondre aux tickets helpdesk BigBlue via le MCP.**
- Pourquoi : BigBlue n'expose **pas d'API REST publique** pour les claims (missing, damaged, wrong item). Les tickets vivent uniquement dans leur back-office.
- Conséquence : l'ouverture de ticket BigBlue se fait **à la main dans l'interface web**. L'agent peut vous rappeler de le faire, vous guider sur le message, mais pas le soumettre.
- Contournement envisagé : Playwright (pilotage browser automatisé) ou MCP custom sur le flux gRPC-Web. À planifier.

**Notes orateur** :
> C'est important de poser cette limite clairement. L'IA agentique n'est pas magique. Quand une plateforme n'expose rien, on doit soit l'accepter, soit construire un contournement. BigBlue, on a fait le choix pragmatique : tout le reste tourne, sauf les tickets. Au prochain incident majeur, on pourra investir sur le contournement.

---

### Slide 10 — MCP Instagram (le plus riche)

**Titre** : MCP Instagram — le couteau suisse de l'influence

**Ce que l'agent peut faire** (catégories) :

**Conversation** :
- Lister les chats, threads, messages.
- **Lire** un thread complet avant de rédiger.
- **Envoyer** un message texte, photo, vidéo.
- Marquer comme lu, supprimer, muter.

**Qualification** :
- Récupérer les **infos profil** d'un user (followers, posts, bio).
- Lire ses **posts récents**, ses **stories**, ses likes.
- Voir qui **suit** et qui **est suivi**.
- Croiser ces signaux pour scoring go/no-go.

**Action produit** :
- Chercher un user par username, partir d'un thread et l'injecter dans le Sheet `Suivi_Amb`.
- Déclencher une **création de draft order Shopify** depuis une conversation (pour envoyer une dotation).
- Détecter les **silents** (pas de réponse après X jours) et envoyer une relance personnalisée.

**Visuel suggéré** : une slide en 3 colonnes avec les 3 catégories, pictos + une liste courte par colonne.

**Notes orateur** :
> C'est le MCP qui a le plus de tools. Il couvre **toute** la chaîne de valeur de l'influence : du premier contact à l'envoi de la dotation. On va voir dans l'acte 3 deux workflows concrets qui utilisent ce MCP de bout en bout.

---

### Slide 11 — MCP TikTok Shop

**Titre** : MCP TikTok Shop — le nouveau canal

**Ce que l'agent peut faire** :
- Lister et lire les **conversations** clients TikTok Shop.
- **Répondre** aux conversations (persona "Service client", français).
- Lister les **commandes** TikTok Shop, consulter le détail.
- Lire et répondre aux **reviews produits**.
- Consulter le catalogue TikTok Shop (produits publiés).

**Particularité** : les commandes TikTok Shop sont fulfillées par BigBlue (même entrepôt que Shopify). Donc le workflow SAV TikTok peut s'appuyer sur les deux autres MCPs (BigBlue + Shopify draft orders pour un replacement).

**Notes orateur** :
> TikTok Shop, c'est un canal qui monte fort. On y reçoit des questions SAV directement dans l'app TikTok, des reviews sur les produits, et les commandes sont livrées via le même entrepôt BigBlue. Ça veut dire qu'on peut traiter un SAV TikTok Shop exactement comme un SAV Gorgias, en branchant les 3 MCPs ensemble. On voit ça dans le prochain acte.

---

## ACTE 3 — Workflows en production

### Slide 12 — Workflow 1 : SAV Gorgias → Shopify → BigBlue

**Titre** : SAV email / chat : un seul fil, 3 plateformes orchestrées

**Flowchart horizontal** :
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Gorgias   │ ──► │   Lecture   │ ──► │   Shopify   │ ──► │   BigBlue   │
│  (ticket)   │     │   thread    │     │ draft order │     │pickup point │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                    ┌─────────────┐                                 │
                    │   Réponse   │ ◄───────────────────────────────┘
                    │    client   │
                    └─────────────┘
```

**Les étapes que l'agent fait en une seule conversation** :
1. Lit le ticket Gorgias et le **thread complet**.
2. Identifie le problème (produit manquant, cassé, mauvais item).
3. Crée un **draft order Shopify** avec remise 100% SAV + shipping gratuit + tag `Service client`.
4. **Complete** le draft pour en faire une vraie commande.
5. Règle le **pickup point sur BigBlue** (à ce jour, la seule étape encore manuelle côté UI BigBlue).
6. Rédige et envoie la **réponse client** en vouvoiement formel, avec excuses si retard.

**Notes orateur** :
> Ce workflow est en prod quotidien depuis plusieurs mois. Il est entièrement documenté dans `knowledge/process/sav_unified.md`. Le gain n'est pas tant le temps que la **fiabilité** : plus d'oubli de tag, de remise, de pickup point. Le process est verrouillé par la mémoire de l'agent.

---

### Slide 13 — Workflow 2 : SAV TikTok Shop → BigBlue → Shopify

**Titre** : SAV TikTok Shop : même process, entrée différente

**Flowchart horizontal** :
```
┌──────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│ TikTok Shop  │──►│   Lecture   │──►│   BigBlue   │──►│   Shopify   │──►│   Réponse    │
│ conversation │   │   thread    │   │  tracking + │   │ draft order │   │ TikTok Shop  │
└──────────────┘   └─────────────┘   │  stock SKU  │   │ (replacement│   │  français    │
                                     └─────────────┘   │ si besoin)  │   └──────────────┘
                                                       └─────────────┘
```

**Les étapes que l'agent fait** :
1. Liste les **conversations** TikTok Shop en attente.
2. Lit le thread complet d'un client (réclamation, question).
3. Vérifie la commande via `get_order_detail` TikTok Shop + **tracking BigBlue** si livraison en cause.
4. Si replacement nécessaire → crée un **draft order Shopify** avec tag `Service client`, remise 100%.
5. Complete + règle pickup point BigBlue.
6. **Répond au client dans TikTok Shop** en français, persona Service client.

**Point clé** : les commandes TikTok Shop étant fulfillées par BigBlue (même entrepôt que Shopify), on peut utiliser **le même pattern** que le SAV Gorgias. La seule différence = le canal d'entrée.

**Notes orateur** :
> C'est un cas d'usage qui illustre bien la force d'avoir tout branché au même endroit. Quand un canal nouveau arrive (ici TikTok Shop), on n'a pas à tout refaire : on réutilise les briques existantes (BigBlue, Shopify) et on ajoute le nouveau MCP au-dessus. En 1 journée de config, le SAV TikTok Shop était intégré au même process que le SAV Gorgias.

---

### Slide 14 — Workflow 3 : MCP Instagram en usage complet

**Titre** : De l'inconnu à l'ambassadeur : tout en une conversation

**Parcours en 5 étapes** (une slide visuelle en 5 cases horizontales) :

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│1.Qualification│  │    2. DM     │  │ 3. Update    │  │ 4. Création  │  │  5. Relance  │
│  KolSquare + │─►│   initial    │─►│    Sheet     │─►│   commande   │─►│   auto si    │
│  Instagram   │  │ (pitch ❶)    │  │  Suivi_Amb   │  │  (dotation)  │  │   silent >7j │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**Détail de ce que l'agent fait à chaque étape** :

1. **Qualification** : récupère `user_info`, `user_posts`, followers, engagement. Applique les règles de scoring (sport/nutrition/fitness, engagement > seuil, audience française).
2. **DM initial** : envoie le pitch ❶ (affiliation pure, -15% / 20€ par utilisation). Persona Antoine, tutoiement, pas de `—` ni de 🙏.
3. **Update Sheet** : ajoute la ligne dans `Suivi_Amb` avec statut `In-cold`, prio `good`, date du contact.
4. **Création commande dotation** (si réponse positive au pitch ❷ négociation) : draft order Shopify avec tag `Dotation influenceur`, produits sélectionnés, adresse récupérée.
5. **Relance auto** : détecte les `In-cold` sans réponse > 7 jours, envoie une relance personnalisée, met à jour la prio.

**Notes orateur** :
> Ce parcours, c'est le cœur de mon métier. Avant, chaque étape était manuelle : je qualifiais dans Excel, je drafts dans Notion, je copiais le message dans Insta, je mettais à jour le Sheet à la main, je créais la commande sur Shopify, je notais les dates de relance dans un agenda. Maintenant, tout vit dans une seule conversation avec Claude Code, qui orchestre les 4 MCPs. Le gain est massif en temps ET en fiabilité (plus d'oubli, plus de doublons).

---

### Slide 15 — Workflow 4 : Gestion quotidienne DMs + distribution codes crédit

**Titre** : La routine matin : 10 min au lieu d'une demi-journée

**Deux tâches combinées** :

**A. Check des réponses du jour**
1. L'agent liste les DMs reçus depuis hier (`list_messages` + filtre unread).
2. Pour chaque thread, il lit le dernier message, le catégorise (réponse positive, question, refus, silence).
3. Il met à jour la colonne priorité (L) du Sheet `Suivi_Amb` :
   - Message en attente de réponse → `high`
   - "En vue" (lu non répondu) → `medium`
   - Antoine a déjà répondu ou liké → `good`
4. Il draft les réponses nécessaires (jamais envoyées sans validation explicite).

**B. Distribution des codes crédit ambassadeurs**
1. L'agent lit la colonne O (utilisations du code) et Q (dernière redistribution) de chaque ambassadeur dans `Suivi_Amb`.
2. Il calcule **`(O − Q) × 20€`** = crédit à distribuer (formule dans [`process_calculate_credits.md`](./process_calculate_credits.md)).
3. Si crédit > 0, il crée un **code Shopify unique** (pattern `NOMAMB-CREDIT-YYYYMM`) du montant calculé.
4. Il envoie un DM Instagram à l'ambassadeur avec le code + explication ("ton code vaut X€, valable sur tout le site").
5. Il met à jour Q = O dans le Sheet pour clôturer la distribution.

**Visuel suggéré** : split vertical. Gauche = check matinal (capture Sheet prio high). Droite = formule `(O−Q)×20€` + capture code Shopify.

**Notes orateur** :
> Ces deux tâches cumulées, c'était une demi-journée de boulot avant. Maintenant 10 à 15 minutes. Et surtout **je n'oublie plus personne**. Avant, un ambassadeur qui avait accumulé du crédit pouvait attendre 3 mois avant que je m'en rende compte. Maintenant, la distribution tourne chaque semaine automatiquement. C'est un des gains qui se voit le plus côté satisfaction ambassadeur.

---

## ACTE 4 — Idées de création (prospective)

### Slide 16 — Idée #1 : Veille Instagram concurrents

**Titre** : Observer les concurrents comme un analyste

**Contexte** : on a déjà un **deuxième compte Instagram branché** (`instagram_veille`) qui sert à surveiller sans polluer le compte principal.

**Ce que le workflow ferait** :
1. Une liste de comptes concurrents est définie (ex : @nutripure, @foodspring, @myprotein, @esn.fr, @eafit_official…).
2. L'agent lance un scan hebdomadaire :
   - Nombre de **posts publiés** cette semaine.
   - **Engagement moyen** (likes + comments / followers).
   - Détection des **posts top-performers** (> 2x l'engagement moyen).
   - **Hashtags** récurrents, thèmes dominants, formats (reels / carrousels / stories).
   - Changements notables (nouveaux produits teasés, partenariats, pivots de tone).
3. L'agent compile un **rapport hebdo** en markdown avec screenshots des meilleurs posts.
4. Alertes sur changements stratégiques (lancement produit, campagne, activation influenceur majeur).

**Pourquoi ça change la donne** :
- Aujourd'hui, la veille sociale concurrente, on **ne la fait pas** (trop chronophage à la main).
- L'agent peut le faire en continu, sans effort humain, et nous alerter uniquement quand il y a quelque chose de marquant.
- On peut comparer notre propre engagement à celui des concurrents et **détecter nos angles morts**.

**Visuel suggéré** : mockup d'un rapport hebdo avec graphique d'engagement par concurrent + 3 posts top-performers en capture.

**Notes orateur** :
> Le MCP `instagram_veille` est déjà en place techniquement. Ce qui manque, c'est le **workflow automatisé** qui l'exploite de manière récurrente. C'est un chantier de quelques jours, pas de semaines. L'intérêt stratégique est énorme : on sait ce qui marche chez les concurrents sans jamais avoir à scroller soi-même.

---

### Slide 17 — Idée #2 : Scraping prix concurrents

**Titre** : Connaître les prix de tous les concurrents, en temps réel

**Ce que le workflow ferait** :
1. Une liste de **pages produits concurrents** est maintenue (ex : Nutripure Whey Native 1kg, Foodspring Whey Isolate, Myprotein Impact Whey…).
2. Un script lance un **scraping automatique** (quotidien ou hebdo) :
   - Prix courant
   - Promos en cours (barré vs actuel)
   - Compositions (proteine/100g, grammage)
   - Stock / disponibilité
3. Les données sont stockées dans un **historique horodaté** (pour voir l'évolution des prix dans le temps).
4. L'agent génère un **tableau comparatif actualisé** automatiquement.
5. **Alertes** quand un concurrent baisse son prix de > 10 % sur une gamme.

**Intégration avec l'existant** : ça vient nourrir le [`benchmark_whey_concurrent.xlsx`](../benchmark/concurrent/) qu'on a déjà, mais en **continu** au lieu d'en one-shot.

**Extensions possibles** :
- Étendre au-delà whey : preworkout, BCAA, isotonique, créatine.
- Ajouter la **disponibilité par distributeur** (Amazon, Decathlon, etc.).
- Corréler avec les données Instagram (post + promo = timing identifiable).

**Limites à connaître** :
- Le scraping peut être bloqué par certains sites (anti-bot, Cloudflare). Contournement : user-agent réaliste, délais, ou API officielle si elle existe.
- Ce n'est pas illégal tant qu'on respecte le robots.txt et qu'on ne réutilise pas les contenus commercialement.

**Notes orateur** :
> Cette idée, c'est celle qui a le plus de ROI potentiel à mes yeux. Nos décisions de pricing, de lancement, de promo sont aujourd'hui basées sur des impressions. Avec ce workflow, elles seraient basées sur de la donnée fraîche. C'est aussi un projet qui peut démarrer petit (5 produits, 3 concurrents) et grandir progressivement.

---

## ACTE 5 — Clôture

### Slide 18 — Bilan + Q&A

**Titre** : Le socle Impulse en une phrase

**Message central (grand format)** :
> L'IA agentique chez Impulse, ce n'est pas un outil qu'on achète.
> C'est un **socle technique** (GitHub + Claude Code + MCPs) qu'on construit.
> Et ce socle est vivant, partageable, et chaque nouvel outil qu'on y branche profite à tout le monde.

**Ce qu'on a parcouru** :
- Concepts : agent, CLI, GitHub central, MCPs.
- 5 MCPs clés : Shopify, Gorgias, BigBlue (avec sa limite), Instagram, TikTok Shop.
- 4 workflows en production : SAV Gorgias, SAV TikTok Shop, MCP Instagram complet, Quotidien + codes crédit.
- 2 idées de création : veille Instagram concurrents, scraping prix.

**Ressources** :
- Repo : `github.com/[org]/Impulse-Nutrition` (privé, accès sur demande)
- Doc d'entrée : [`CLAUDE.md`](../CLAUDE.md) + [`knowledge/INDEX.md`](./INDEX.md)
- Pour démarrer : installer Claude Code ([claude.com/code](https://claude.com/code)), cloner le repo, lire `CLAUDE.md`.
- Contact : Antoine Chabrat.

**Notes orateur** :
> Si vous retenez une chose : **le socle GitHub + Claude Code + MCPs**, c'est ce qui fait que l'IA chez Impulse ne dépend pas d'une personne. Que je sois là ou pas, le repo continue, les règles continuent, les outils continuent. C'est ça qui transforme un hack personnel en avantage compétitif durable. Des questions ?

---

## Annexes

### Captures écran à préparer en amont

| Slide | Capture à préparer |
|---|---|
| 4 | Schéma GitHub central (à redessiner proprement dans Google Slides ou Excalidraw) |
| 5 | Schéma MCP = prise USB (Excalidraw) |
| 6 | Grille logos des 10 MCPs |
| 7 | Shopify admin + tool `create_draft_order` en exécution |
| 8 | Gorgias ticket + réponse agent |
| 9 | BigBlue UI + zone ticket grisée (pour illustrer la limite) |
| 10 | Instagram : profil qualification + thread DM |
| 11 | TikTok Shop : liste conversations + thread |
| 12 | Flowchart SAV Gorgias |
| 13 | Flowchart SAV TikTok Shop |
| 14 | Parcours 5 étapes MCP Instagram |
| 15 | Sheet `Suivi_Amb` colonne L + formule `(O−Q)×20€` |
| 16 | Mockup rapport hebdo veille Instagram concurrents |
| 17 | Mockup tableau comparatif prix concurrents |

### Chiffres à vérifier avec Antoine avant la session

- Nombre exact de MCPs branchés (le deck dit 10, à recompter).
- Nombre exact de tools MCP (le deck dit 65+, à recompter via `knowledge/reference/mcps.md`).
- Liste des comptes concurrents pour la veille (à définir précisément avant la session).
- Liste des URLs produits à scraper (à définir pour le mockup slide 17).

### Tips de présentation

- **Slide 4 (schéma GitHub central) est LE slide à soigner visuellement**. C'est le concept pivot. Prends le temps de le rendre beau dans Google Slides, pas du monospace brut.
- **Démo live si possible** en fin d'acte 3 : ouvrir Claude Code et faire tourner un vrai workflow (ex : check DMs du matin). Un vrai tool call vaut 10 slides.
- **Ne pas lire les bullets** : les bullets sont pour le public, les notes orateur sont pour toi. Parle naturellement.
- **Timing** : ~3 min par slide en moyenne. Si tu sens que l'audience accroche, ralentis sur l'acte 3. Si tu sens qu'elle décroche, accélère sur l'acte 2.
- **Les limites que tu poses (slide 9 BigBlue) sont des atouts** pédagogiques : elles crédibilisent ton discours en montrant que tu ne vends pas du magique.
