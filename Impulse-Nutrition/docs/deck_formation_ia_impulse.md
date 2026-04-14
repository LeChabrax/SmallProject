# Deck formation interne — IA, agents CLI & outillage Impulse

> **Public cible** : équipe HCS/Impulse novice en IA agentique.
> **Durée** : ≈55 min présentation + 10-15 min Q&A.
> **Format** : 22 slides, à importer dans Google Slides.
> **Auteur** : Antoine Chabrat, Influence Manager.
> **Version** : avril 2026.

---

## Table des matières

| Acte | Thème | Slides | Durée |
|---|---|---|---|
| 1 | Point de départ familier (ChatGPT) | 1-3 | 5 min |
| 2 | Le shift : l'agent IA | 4-8 | 12 min |
| 3 | Plomberie : GitHub & MCPs | 9-12 | 10 min |
| 4 | Démo Impulse (cœur) | 13-19 | 20 min |
| 5 | Perspective & clôture | 20-22 | 8 min |
| — | Q&A | — | 10-15 min |

---

## ACTE 1 — Point de départ familier

### Slide 1 — Cover

**Titre principal** : L'IA chez Impulse
**Sous-titre** : Comment ça marche concrètement
**Pied** : Formation interne · avril 2026 · Antoine Chabrat

**Visuel suggéré** : logo Impulse Nutrition au centre, en bas une ligne de 4 pictos (Claude, GitHub, Shopify, Instagram) pour signaler le périmètre.

**Notes orateur** :
> Bienvenue. En 55 min on va répondre à une seule question : "concrètement, qu'est-ce que l'IA change dans le travail d'un influence manager, et qu'est-ce qu'on a mis en place ici ?". On part de ce que tout le monde connaît (ChatGPT), on monte en abstraction (agents, CLI, MCPs), puis on redescend sur du très concret (nos workflows quotidiens). N'hésitez pas à couper à tout moment pour une question.

---

### Slide 2 — Ce que tout le monde connaît déjà : ChatGPT web

**Titre** : ChatGPT web : l'entrée dans l'IA pour 200M de personnes

**Bullets** :
- Un chat dans un navigateur. On pose une question, on obtient une réponse.
- Génial pour : rédiger un mail, résumer un texte, traduire, brainstormer.
- Modèle de conversation : question → réponse → question → réponse.

**Visuel suggéré** : capture écran de chatgpt.com avec une question type "Rédige-moi un DM de relance pour un influenceur".

**Notes orateur** :
> Qui utilise ChatGPT au moins une fois par semaine ? (Main levée). Voilà le point de départ. C'est déjà utile, c'est déjà un saut énorme par rapport à rien. Mais on va voir que ce n'est qu'une petite partie de ce que l'IA peut faire. En fait, ChatGPT web, c'est la pointe de l'iceberg visible.

---

### Slide 3 — Mais le chat web a 3 vraies limites

**Titre** : Les 3 murs du chat web

**Bullets** :
1. **Pas de contexte.** Il ne voit ni le Google Sheet, ni le ticket Gorgias, ni la fiche produit Shopify.
2. **Pas d'action.** Il rédige, vous copiez-collez, vous exécutez à la main.
3. **Pas de mémoire.** Nouvelle conversation, tout oublié : la persona de marque, les règles, les contacts.

**Visuel suggéré** : illustration simple avec 3 murs dessinés. Au-dessus de chaque mur, un pictogramme (œil barré, main barrée, cerveau barré).

**Notes orateur** :
> Ces 3 limites, vous les avez tous ressenties. Combien de fois vous avez copié un export Excel, collé dans ChatGPT, reformulé la question, recollé ailleurs ? C'est de la friction. Le problème n'est pas la qualité de la réponse, c'est **le copier-coller permanent**. Et c'est exactement ce que résolvent les agents CLI qu'on va voir maintenant.

---

## ACTE 2 — Le shift : l'agent IA

### Slide 4 — L'évolution : de "chat" à "agent"

**Titre** : L'agent = cerveau + mains + yeux + mémoire

**Bullets** :
- Même cerveau (le modèle LLM), mais avec **des mains** (il peut agir) et **des yeux** (il voit vos fichiers).
- Il lit votre repo, modifie un fichier, appelle une API, exécute un script, relit son propre résultat.
- Vous décrivez l'intention, il orchestre les étapes.

**Visuel suggéré** : schéma en deux colonnes.
- Gauche : "Chat web" = un cerveau tout seul dans une bulle.
- Droite : "Agent" = cerveau + mains + yeux + une petite boîte "mémoire" reliée.

**Notes orateur** :
> C'est le shift conceptuel clé. On passe d'un truc qui **parle** à un truc qui **fait**. C'est la différence entre un consultant qui vous dit quoi faire et un assistant qui le fait pour vous en vous expliquant. Et ça change tout : le copier-coller disparaît, parce que l'agent vit dans votre environnement de travail.

---

### Slide 5 — C'est quoi un "CLI" ?

**Titre** : CLI : la fenêtre noire où on tape au PC

**Bullets** :
- CLI = Command Line Interface. La fameuse "fenêtre noire" des développeurs.
- Les agents IA y vivent parce qu'ils ont besoin d'un accès direct : fichiers, git, scripts, terminaux.
- Ce n'est pas "plus compliqué", c'est **plus puissant** : l'agent fait ce que vous feriez au clavier, mais 100x plus vite.

**Visuel suggéré** : capture d'écran d'un terminal avec Claude Code ouvert, montrant une conversation réelle (floutée si besoin) avec un tool call Shopify ou Sheets.

**Notes orateur** :
> La fenêtre noire fait peur à beaucoup. Rassurez-vous : **vous n'avez pas besoin de taper des commandes techniques**. Vous ouvrez Claude Code, et vous écrivez en français : "crée-moi le contrat d'Audrey", ou "check les DMs de ce matin". Le CLI, c'est juste la maison de l'agent. Vous, vous parlez français.

---

### Slide 6 — Panorama des 4 gros agents en 2026

**Titre** : Les 4 agents CLI qui comptent en 2026

**Contenu tableau** :

| Agent | Modèle | Éditeur | Force principale |
|---|---|---|---|
| **Claude Code** | Claude Opus / Sonnet | Anthropic | Raisonnement long, écosystème MCP, contexte 1M tokens |
| **Codex CLI** | GPT-5 / o-series | OpenAI | Écosystème GPT, intégration ChatGPT |
| **Gemini CLI** | Gemini 2.5 Pro | Google | Quota gratuit généreux, Google Workspace |
| **GitHub Copilot CLI** | Mix (Claude, GPT) | GitHub / Microsoft | Intégration GitHub native, PR reviews |

**Visuel suggéré** : les 4 logos en carré, avec une barre de couleur par éditeur (orange Anthropic, noir/vert OpenAI, bleu Google, violet GitHub).

**Notes orateur** :
> Les 4 sont conceptuellement similaires : agent + outils + modèle qui raisonne. La vraie différence c'est "quel cerveau, quel écosystème". Attention à ne pas confondre GitHub Copilot "autocomplétion dans l'IDE" (un vieux produit qui complète votre code pendant que vous tapez) avec Copilot CLI (le vrai agent). On va maintenant voir pourquoi chez Impulse on a choisi Claude Code.

---

### Slide 7 — Pourquoi Claude Code chez Impulse

**Titre** : Claude Code = le bon outil pour nous

**Bullets** :
- **Contexte long (1M tokens)** : il charge toute la doc Impulse d'un coup, pas besoin de lui rappeler le contexte à chaque session.
- **Qualité de raisonnement** sur les tâches multi-étapes : SAV, qualification influenceur, décisions de dotation.
- **Écosystème MCP mature** : 65+ outils déjà connectés (Shopify, BigBlue, Gorgias, Instagram, Sheets, Canva, TikTok Shop).
- **Mémoire persistante** : il apprend et garde les règles métier (persona Antoine vs Service client, tags Shopify, tone Gorgias).

**Visuel suggéré** : 4 pictos en ligne, un par bullet, dans les couleurs Impulse.

**Notes orateur** :
> C'est un choix, pas une religion. On pourrait mixer plusieurs agents selon les tâches. Mais pour notre métier (influence + SAV + benchmark), Claude Code coche toutes les cases. Et les règles métier qu'on a patiemment documentées dans CLAUDE.md et les fichiers de mémoire, il les applique automatiquement à chaque session.

---

### Slide 8 — Anatomie d'un agent : les 4 briques

**Titre** : Comment un agent est construit

**Schéma** :
```
          ┌─────────────────────┐
          │   Le modèle (LLM)   │  ← le cerveau qui raisonne
          └─────────┬───────────┘
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
      ┌──────┐  ┌──────┐  ┌─────────┐
      │Outils│  │ Ctx  │  │ Mémoire │
      └──────┘  └──────┘  └─────────┘
        ↑         ↑           ↑
      agit      voit      se souvient
```

**Bullets explicatifs** :
1. **Le modèle** (Claude Opus, GPT-5…) : le cerveau qui raisonne.
2. **Les outils** (MCPs, Bash, Read, Write…) : les mains qui agissent.
3. **Le contexte** : tout ce que l'agent voit à l'instant T (repo, docs, résultats des tools).
4. **La mémoire** : règles persistantes entre les sessions (CLAUDE.md, fichiers memory).

**Notes orateur** :
> Gardez cette grille en tête. Chaque fois qu'on parle d'IA, vous pourrez répondre à la question : "de quoi parle-t-on exactement ? Du modèle ? Des outils ? Du contexte ? De la mémoire ?". 90% des discussions IA deviennent beaucoup plus claires avec cette grille.

---

## ACTE 3 — La plomberie : GitHub & MCPs

### Slide 9 — GitHub en une phrase

**Titre** : GitHub = Google Drive pour le code (mais en mieux)

**Bullets** :
- "Un Google Drive pour le code, avec historique complet de qui a changé quoi et quand."
- Chaque "dossier" = un **repo** (repository).
- Chaque modification = un **commit** (snapshot horodaté + message).
- Développé par des millions de dev, racheté par Microsoft en 2018.

**Visuel suggéré** : capture d'une page GitHub du repo Impulse-Nutrition avec la liste des commits visibles (dates + auteurs + messages).

**Notes orateur** :
> GitHub, c'est l'endroit où vivent les "repos". Un repo, c'est simplement un dossier de code versionné. Chaque modification est tracée : qui, quand, pourquoi. C'est ce qui permet de travailler à plusieurs sans s'écraser mutuellement, et de revenir en arrière si on casse quelque chose.

---

### Slide 10 — Les 4 verbes de base

**Titre** : 4 verbes à retenir : clone, pull, commit, push

**Bullets** :
- **clone** : je télécharge le repo sur mon poste (une seule fois, au début).
- **pull** : je récupère les dernières modifs des autres.
- **commit** : j'enregistre mes modifs localement avec un message explicatif.
- **push** : j'envoie mes modifs sur GitHub pour que les autres les récupèrent.

**Visuel suggéré** : 4 flèches en boucle entre "Mon poste" et "GitHub", chaque flèche étiquetée avec un verbe.

**Notes orateur** :
> Analogie Google Docs : pull = "recharger la page", push = "synchroniser votre version". Le git est juste plus explicite sur l'historique, parce que dans le code, une virgule au mauvais endroit peut tout casser. Vous n'avez même pas à taper ces commandes : Claude Code les exécute pour vous quand vous dites "commit ces changements".

---

### Slide 11 — Pourquoi partager du code importe ici

**Titre** : Pourquoi on a tout mis sur GitHub

**Bullets** :
- **Réutilisabilité** : le script qui génère les contrats peut servir à toute l'équipe, à tout moment.
- **Traçabilité** : qui a modifié quelle règle de SAV, quand, pourquoi. Plus d'ambiguïté.
- **Collaboration** : un stagiaire, un prestataire, un futur influence manager reprend la suite sans repartir de zéro.
- **L'agent lit et modifie le repo** : tout vit au même endroit, l'IA et le code.

**Visuel suggéré** : capture du repo Impulse-Nutrition avec les dossiers visibles (`instagram_dm_mcp/`, `contracts/`, `benchmark/`, `docs/`).

**Notes orateur** :
> Le vrai truc qui change : ce n'est pas juste du stockage. C'est que **l'agent lit et modifie le même repo que vous**. Vous et l'IA bossez sur les mêmes fichiers, avec le même historique. C'est ce qui fait de ce repo une **boîte à outils vivante**, pas un dossier mort.

---

### Slide 12 — MCP : la prise USB entre l'agent et les plateformes

**Titre** : MCP = la prise universelle

**Schéma central** :
```
                    ┌────────────────┐
                    │  Claude Code   │
                    └───────┬────────┘
                            │  (MCPs)
           ┌────────┬───────┼────────┬─────────┐
           │        │       │        │         │
           ▼        ▼       ▼        ▼         ▼
      ┌────────┐┌──────┐┌──────┐┌────────┐┌─────────┐
      │Shopify ││Gorgia││BigBlu││Instagra││ Sheets  │
      └────────┘└──────┘└──────┘└────────┘└─────────┘
           │        │       │        │         │
           ▼        ▼       ▼        ▼         ▼
        Canva    TikTok  Gmail    Drive     (65+)
```

**Bullets** :
- MCP = Model Context Protocol. Standard ouvert lancé par Anthropic en **novembre 2024**.
- **Avant** : chaque outil avait son intégration maison, fragile, à maintenir un par un.
- **Après** : format standardisé. On branche un MCP et l'agent sait immédiatement s'en servir.

**Analogie clé** :
> Avant les prises USB, chaque appareil avait son connecteur propriétaire. Après, une seule prise pour tout : clé, souris, disque dur, imprimante. Le MCP, c'est la prise USB entre l'IA et vos outils de travail.

**Notes orateur** :
> C'est **le** concept à retenir de cet acte. Quand vous entendrez "MCP", pensez "prise USB pour l'IA". Chez nous, on a **65+ tools MCP connectés** : Shopify, Gorgias, BigBlue, Instagram (x2), TikTok Shop, Sheets, Drive, Canva, Gmail, Firebase… Et certains sont **custom** (on les a codés nous-mêmes) parce que les plateformes n'avaient pas de MCP officiel. C'est un vrai investissement technique, c'est ce qui permet à Claude Code d'agir réellement au lieu de juste rédiger.

---

## ACTE 4 — Ce qu'on a mis en place chez Impulse (cœur du deck)

### Slide 13 — Vue d'ensemble : 7 chantiers en production

**Titre** : 7 chantiers, 100% en production

**Visuel principal** : grille 3×3 (avec 7 cases remplies, 2 vides pour l'espace), un picto + nom par chantier :
1. Gestion DMs Instagram
2. Contrats influenceurs
3. Reporting & benchmark
4. Qualification KolSquare
5. Veille concurrentielle
6. SAV Gorgias unifié
7. Outils custom & MCPs

**Notes orateur** :
> On va parcourir les 7 chantiers rapidement. Gardez en tête : tous les 7 sont **en production quotidienne**, pas des POC. Chacun a fait gagner du temps réel, mesurable. Je vous montrerai à la fin les chiffres concrets.

---

### Slide 14 — Workflow 1 : Gestion DMs Instagram

**Titre** : Check DMs automatisé : 10 min au lieu d'une demi-journée

**Bullets** :
- Check quotidien : lecture DMs, catégorisation, priorisation, relances automatiques.
- Sheet `Suivi_Amb` tenu à jour avec statuts (In-cold, In-hot, Produits envoyés, Out…).
- Decision tree formalisé ([`docs/dm_decision_tree.md`](./dm_decision_tree.md)), persona Antoine verrouillée (tutoiement, ton pro, pas de `—` ni de 🙏).
- Scripts opérationnels : `qualify_conversations.py`, `refresh_analyses.py`, `run_campaign.py`, `audit_ambassadors.py`.

**Visuel suggéré** : capture du Sheet `Suivi_Amb` avec les colonnes J (statut), K (contexte), L (priorité) remplies + à côté, un extrait de conversation Instagram.

**Notes orateur** :
> Avant : je passais une demi-journée à éplucher 200 DMs, classer, rédiger les relances. Maintenant : 10 min. L'agent lit tous les threads, propose des catégorisations, draft les relances. Je valide ou je corrige. C'est le workflow le plus mature du parc, c'est celui qui m'a convaincu que l'IA agentique changerait réellement mon job.

---

### Slide 15 — Workflow 2 : Contrats influenceurs

**Titre** : Contrat génré en 2 min au lieu d'1h

**Bullets** :
- Génération automatique de contrats PDF personnalisés : livrables, montants, dates, SIREN, signatures.
- Source : `generate_contract.py` + template dans `templates/pitch_initial_plain.txt`.
- Sync Google Drive automatique : dossier `contracts/drive/` poussé sur le Drive partagé.
- **9 contrats déjà générés et signés** (dossier `contracts/`) : Audrey Merle, Baptiste Mischler, Celia Merle, Dan Necol, Emmanuel Bonnier…
- 4 modèles supportés : Affiliation pure, Dotation négociée, Paid, Club (voir [`reference_contract_types.md`](./reference_contract_types.md)).

**Visuel suggéré** : capture d'un contrat PDF (page 1) + le dossier Google Drive à côté.

**Notes orateur** :
> Avant : 1h de Word + copier-coller + vérifications + sauvegarde. Maintenant : je dis "génère le contrat de Celia, dotation 150€/mois sur 6 mois, 2 posts + 3 stories par mois", l'agent récupère les infos dans le Sheet, génère le PDF, l'envoie sur le Drive, et me sort le lien. **La validation juridique finale du template reste à faire**, mais la mécanique est prête.

---

### Slide 16 — Workflow 3 : SAV unifié (Gorgias → Shopify → BigBlue)

**Titre** : SAV : un seul process, 3 plateformes orchestrées

**Flowchart à dessiner** :
```
   Ticket Gorgias
         │
         ▼
  Lecture thread complet
         │
         ▼
  Draft Shopify (remise 100% SAV)
         │
         ▼
  Complete draft → order
         │
         ▼
  Pickup point BigBlue (manuel)
         │
         ▼
  Réponse client (persona "Service client")
```

**Bullets** :
- Un seul process documenté : [`process_sav_unified.md`](./process_sav_unified.md).
- Persona **"Service client"** en vouvoiement formel, distincte de la persona Antoine des DMs.
- Tags Shopify spécifiques (`Service client`, `Dotation influenceur`) pour sortir du CA HCS.
- Checklist à chaque ticket : remise 100% appliquée, shipping gratuit, pickup point réglé, ton de marque validé.

**Visuel suggéré** : flowchart 3 plateformes en horizontal, avec les logos Gorgias / Shopify / BigBlue.

**Notes orateur** :
> Avant : 3 onglets, 3 interfaces, 3 logins, et un risque d'oublier une étape. Maintenant : un seul fil de conversation avec l'agent, qui fait les 3 étapes dans l'ordre. Le gain n'est pas tant le temps que **la fiabilité** : on n'oublie plus un tag, plus un pickup point, plus une remise.

---

### Slide 17 — Workflow 4 : Qualification KolSquare

**Titre** : Qualification de 1000 profils en 15 min

**Bullets** :
- Export CSV KolSquare (brut, 1000+ profils) → filtrage via règles formalisées ([`kolsquare_filtering_rules.md`](./kolsquare_filtering_rules.md)) → injection dans le Sheet `Suivi_Amb`.
- Scoring go/no-go sur engagement, audience, adéquation marque (fitness / sport / nutrition).
- Scripts : `instagram_dm_mcp/filter_kolsquare.py`, `kolsquare_to_sheet.py`, `qualify_influencer.py`.
- Dernier batch : **filtered_prospects_042026.csv** (avril 2026).

**Visuel suggéré** : vue avant/après. Gauche : CSV brut KolSquare (1000 lignes, colonnes obscures). Droite : Sheet `Suivi_Amb` propre, 150 profils retenus, colonnes structurées.

**Notes orateur** :
> Avant : 2 jours pour trier manuellement un export KolSquare. Maintenant : 15 min. Le gain, ce n'est pas juste la vitesse : c'est que je peux maintenant **exporter KolSquare toutes les 2 semaines** au lieu d'une fois par trimestre. Donc je détecte les profils en croissance bien plus tôt.

---

### Slide 18 — Workflow 5 : Benchmark & veille concurrentielle

**Titre** : Benchmark abonnement + veille whey : 3 jours au lieu de 3 semaines

**Bullets** :
- **Benchmark rentabilité abonnement** : scripts `rentabilite.py`, `generate_html_report.py`, rapport HTML interactif (`rapport_rentabilite_abonnement.html`).
- **Veille whey concurrents** : Nutripure, Foodspring, Myprotein, ESN. Prix, compo, positionnement, packshots.
- **Veille sociale** : `veille_concurrents.py` surveille les stratégies de contenu des concurrents sur Instagram.
- Sortie : `benchmark_whey_concurrent.xlsx` + `whey_catalog.json` + rapport HTML.

**Visuel suggéré** : capture du rapport HTML de rentabilité abonnement (avec les graphiques) + à côté, un extrait du `.xlsx` benchmark whey.

**Notes orateur** :
> Ce chantier illustre le point clé : **on a codé nos propres outils**. Pas un produit sur étagère. Le benchmark whey, personne ne le fait à notre place. L'agent a scrapé, enrichi, structuré, puis généré le rapport. 3 semaines de boulot manuel compressées en 3 jours. Et on peut le rejouer à volonté quand le marché bouge.

---

### Slide 19 — Workflow 6 : Outils custom à la demande

**Titre** : Le repo Impulse-Nutrition = boîte à outils vivante

**Bullets** :
- Principe : quand un besoin revient 3 fois, on le codifie.
- Exemples concrets : générateur de contrats, benchmark abonnement, pipeline DM check, scripts KolSquare, process SAV unifié.
- Ce n'est pas un POC ni un one-shot : c'est un **repo vivant**, documenté, testable, réutilisable.
- Philosophie : "un nouveau besoin = soit un MCP existant, soit un outil qu'on code en 1-2 jours".

**Visuel suggéré** : arborescence simplifiée du repo :
```
Impulse-Nutrition/
├── instagram_dm_mcp/       (DMs + qualification)
├── gorgias_mcp/            (SAV)
├── bigblue_mcp/            (fulfillment)
├── shopify_mcp/            (commandes, drafts)
├── benchmark/              (analyses, rapports)
├── KolSquare/              (qualification prospects)
├── contracts/              (contrats générés)
├── templates/              (modèles réutilisables)
└── docs/                   (process & références)
```

**Notes orateur** :
> C'est le point le plus important du deck. **L'agent + le repo = une usine à outils sur mesure.** On ne subit pas des SaaS génériques. Quand un besoin émerge, on construit l'outil. Et comme tout est versionné dans GitHub, chaque outil reste accessible, modifiable, auditable. C'est ça qui fait la différence entre "utiliser de l'IA" et "être équipé".

---

## ACTE 5 — Perspective & clôture

### Slide 20 — Ce que ça change concrètement

**Titre** : Les chiffres du gain

**Tableau** :

| Tâche | Avant | Après |
|---|---|---|
| Générer un contrat influenceur | 1h | 2 min |
| Trier les DMs quotidiens | ½ journée | 10 min |
| Benchmark concurrentiel (whey) | 3 semaines | 3 jours |
| Qualifier 1000 profils KolSquare | 2 jours | 15 min |
| Traiter un ticket SAV complet | 20 min + risque d'oubli | 5 min, process fiable |

**Message fort en bas** :
> Mais la vraie valeur n'est pas "automatiser". C'est **rendre faisables des choses qu'on ne faisait pas avant, par manque de temps.**

**Notes orateur** :
> Je veux insister sur le bas de cette slide. Le benchmark whey, on ne le faisait **pas** avant. Trop long, trop coûteux. La veille social concurrent, on ne la faisait **pas**. Trop chronophage. L'IA ne remplace pas des tâches qu'on faisait déjà, elle **débloque des tâches qu'on ne faisait pas**. C'est une expansion, pas un remplacement.

---

### Slide 21 — Prochains chantiers

**Titre** : Les 4 chantiers qui arrivent

**Bullets** :
1. **Fermer la boucle influence** : ROI par code, croisement Affiliatly × Shopify × KolSquare. Savoir qui rapporte quoi, vraiment.
2. **Voix client agrégée** : pipeline unique (avis Shopify + tickets Gorgias + reviews TikTok + mentions Insta) → tendances mensuelles actionnables.
3. **Veille étendue** : au-delà whey, étendre à preworkout, BCAA, isotonique.
4. **Industrialiser les apprentissages** : documenter ce qui convertit (quels profils, quels messages, quels produits).

**Visuel suggéré** : 4 pictos en ligne, chacun avec une icône (boucle ROI, micro/voix, loupe, livre ouvert).

**Notes orateur** :
> Ces 4 chantiers ne sont pas hypothétiques, ils sont sur la roadmap des 6 prochains mois. Le plus important à mes yeux : **fermer la boucle influence**. On exécute beaucoup, on ne mesure pas encore systématiquement. C'est la prochaine étape. Je suis ouvert à vos suggestions aussi : quels besoins vous voyez qu'on pourrait outiller ?

---

### Slide 22 — Q&A + ressources

**Titre** : Pour aller plus loin

**Bullets** :
- **Repo GitHub** : `github.com/[org]/Impulse-Nutrition` (privé, accès sur demande).
- **Doc d'entrée** : [`CLAUDE.md`](../CLAUDE.md) et [`docs/INDEX.md`](./INDEX.md) (cartographie complète).
- **Référent technique** : Antoine Chabrat.
- **Pour commencer côté équipe** : installer Claude Code ([claude.com/code](https://claude.com/code)) + cloner le repo + lire `CLAUDE.md`.

**Message final** :
> L'IA agentique n'est pas un produit qu'on achète. C'est un **socle technique** qu'on construit. Et on est déjà bien avancés.

**Notes orateur** :
> Des questions ? Sur n'importe quoi : les concepts, les chantiers, la roadmap, comment s'y mettre. Ceux qui veulent tester Claude Code, je peux vous aider à l'installer en 10 min après la session. Merci.

---

## Annexes

### Captures écran à préparer en amont

Liste des captures nécessaires pour l'import Google Slides. À faire **avant** la session.

| Slide | Capture à préparer |
|---|---|
| 2 | chatgpt.com avec prompt "Rédige un DM de relance" |
| 5 | Terminal avec Claude Code ouvert (session réelle, infos floutées) |
| 9 | Page GitHub du repo Impulse-Nutrition (liste commits) |
| 11 | Arborescence du repo (screenshot de `tree` ou finder) |
| 14 | Sheet `Suivi_Amb` + extrait conversation Instagram |
| 15 | Un contrat PDF (page 1) + dossier `contracts/drive/` |
| 16 | Flowchart Gorgias → Shopify → BigBlue (à dessiner) |
| 17 | CSV KolSquare brut vs Sheet `Suivi_Amb` propre |
| 18 | Rapport HTML rentabilité + extrait benchmark whey `.xlsx` |

### Chiffres à vérifier avec Antoine avant impression

- "200M utilisateurs ChatGPT" → à vérifier dernier chiffre public OpenAI.
- "65+ tools MCP" → à recompter via `docs/reference_mcps.md`.
- "9 contrats générés et signés" → à recompter dans `contracts/` au jour J.
- Tous les gains temporels (1h → 2 min, ½ journée → 10 min, 3 semaines → 3 jours, 2 jours → 15 min).

### Tips de présentation

- **Démo live si possible** : en fin d'acte 4, ouvrir Claude Code et faire une vraie manipulation (lire un ticket Gorgias, ou checker un DM). Un vrai tool call vaut 10 slides.
- **Ne pas lire les bullets** : les bullets sont pour le public, les notes orateur sont pour vous. Parlez naturellement.
- **1 minute par bullet max** sinon vous allez dépasser.
- **Couper si quelqu'un décroche** : signal visuel = plus de notes, personne ne regarde. Passez au slide suivant.
