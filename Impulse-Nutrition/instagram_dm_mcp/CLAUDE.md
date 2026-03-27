# CLAUDE.md — Impulse Nutrition Instagram DM Manager

## Contexte métier

**Impulse Nutrition** est une marque de nutrition sportive premium (groupe Havea / Vitavea). Produits fabriqués en France, conformes antidopage, ciblant les sportifs d'endurance (trail, running, triathlon) et de force.

**Antoine Chabrat** est Influence Manager. Il gère :
- ~413 ambassadeurs (onglet **Suivi_Amb** dans le Google Sheet "InfluenceManager")
- ~20 comptes dotation (onglet **Suivi_Dot**)
- Des partenariats payés ponctuels (onglet **Suivi_Paid**)

Le travail quotidien d'Antoine : prospecter des influenceurs sportifs sur Instagram, pitcher le programme ambassadeur, onboarder les nouveaux, envoyer des promos, relancer, et maintenir le suivi dans le Google Sheet.

---

## Programme ambassadeur

### Parcours type d'un ambassadeur

1. **Prospection** : Antoine identifie un profil cohérent (sport, engagement, contenu)
2. **Premier contact** : DM Instagram avec le pitch standard (voir `personality.md`)
3. **Échange** : Réponse aux questions, souvent suivi d'un appel téléphonique
4. **Onboarding** :
   - L'ambassadeur choisit des produits (~80-100 €) ou reçoit un pack personnalisé
   - Envoi de l'adresse + email
   - Création de la commande gratuite
   - Création du code affilié personnalisé sur Affiliatly
   - Envoi du code + lien affilié
5. **Vie du partenariat** :
   - L'ambassadeur partage du contenu (stories, posts, reels, Strava) avec son code
   - À chaque commande passée avec le code → 20 € de crédit pour l'ambassadeur
   - Suivi des performances, relances, promos ponctuelles

### Conditions standard

- **Envoi initial** : ~80 € de produits gratuits (100 € pour profils importants)
- **Code affilié** : -15% sur la première commande pour les abonnés de l'ambassadeur
- **Bonus** : Shaker offert dès 59 € d'achats
- **Crédit ambassadeur** : 20 € par commande réalisée avec le code
- **Contenu** : Format libre (stories, posts, reels, Strava)
- **Évolution** : Possibilité de partenariat rémunéré si très bons résultats

### Dotation (Suivi_Dot)

Pour les profils plus importants ou les demandes spécifiques :
- Envoi régulier de produits contre contenu
- Pas de code affilié systématique
- Négociation au cas par cas (souvent via l'agent/manager de l'influenceur)

---

## Google Sheet "InfluenceManager"

**Spreadsheet ID** : `1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4`

### Onglets

| Onglet | Rôle |
|--------|------|
| **Dashboard** | Todo perso d'Antoine (Kanban des missions). **Ne pas modifier** — usage interne Antoine uniquement |
| **Analyses** | Récap performance : nb commandes envoyées (124), nb utilisations codes, classement des meilleurs ambassadeurs. Mis à jour manuellement par Antoine. Consulté par Antoine + Pierre. Objectif futur : automatisation + dashboard visuel + suivi ROI |
| **StratAmba** | Définition des 3 niveaux du programme : Entrée ambassadeur → Discussion partenariat rému → Ambassadeur dotation |
| **Suivi_Amb** | Suivi principal des ~413 ambassadeurs — pipeline complet |
| **Suivi_Paid** | Partenariats rémunérés (Dorian/FraichTouch, Lestraileurs, Aubin Ferrari...) |
| **Suivi_Dot** | Comptes dotation (~20 : Augustin Cablant, Jordan Perrin, Mathilde Sénéchal...) |
| **Message_type** | Générateur de messages : sélectionner un influenceur → génère automatiquement premier message, second message, message commande |
| **Export_AMBA/PAID** | Export des contacts (mail, prénom, nom, code, lien IG) — sert à alimenter Shopify et Affiliatly |
| **Export_Code** | Liste consolidée de tous les codes affiliés actifs — sert à alimenter Shopify et Affiliatly |
| **OneShot** | Opérations ponctuelles (ex: Brunchclub, distribution événements) |
| **Archive** | Influenceurs archivés (refus, déjà pris, etc.) |
| **Feuille 20** | Calendrier de contenus (Date, Ambassadeur, Contenu, Thème) — **projet futur, pas encore actif** |
| **Message_type_hide** | Version masquée de Message_type |

---

### Suivi_Amb — Colonnes détaillées (A à AG, 33 colonnes)

**Bloc A-G — Templates de messages (Not for LLM — usage interne sheet)**

| Col | Nom | Description |
|-----|-----|-------------|
| **A** | Type | Type de message à envoyer : `Premier Message`, `Relance`, vide |
| **B** | Message | Message auto-généré à envoyer (basé sur Type + templates C-G) |
| **C** | Premier Message | Template du premier message |
| **D** | Commandes | Template du message d'envoi de commande |
| **E** | Relance | Template de relance |
| **F** | Avis | Template de demande d'avis (TRUE/FALSE) |
| **G** | Mention Bio | Template de rappel mention bio |

**Bloc H-M — Suivi quotidien (visible sans scroller)**

| Col | Nom | Description |
|-----|-----|-------------|
| **H** | IG link | Lien direct vers le profil Instagram |
| **I** | Compte @ | Username Instagram (sans @) |
| **J** | Statut | Pipeline : `In-cold` → `In-hot` → `A recontacter` / `A rediscuter` → `Contacter manager` → `Produits envoyés` → `Out` |
| **K** | Action/Commentaire | Texte libre — notes brèves sur la situation actuelle, brief rapide en synergie avec les autres colonnes |
| **L** | Priorités identifiées | `high` / `medium` / `good` (rempli auto par `update_priorities.py` ou MCP) |
| **M** | Campagne | Colonne qui change à chaque vague. Ex: `Promo-20% mars` → `Promo-20% mars OK` / `Promo-20% mars SKIP` |

**Bloc N-Q — Affiliation + contact**

| Col | Nom | Description |
|-----|-----|-------------|
| **N** | Code affiliation | Le code promo (ex: MANU, JESSD, NADIARUN, DELPHEE) |
| **O** | Lien affiliation | `https://impulse-nutrition.fr/discount/[CODE]` |
| **P** | Affiliatly | Si le compte Affiliatly est créé (`oui`/vide) |
| **Q** | Mail Ambassadeur | `oui`/vide — indique si le mail d'officialisation du statut ambassadeur a été envoyé |

**Bloc R-Y — Profil + contenu**

| Col | Nom | Description |
|-----|-----|-------------|
| **R** | Bio | `oui` / `Non` — présence de "impulse" ou du code affilié dans la bio Instagram |
| **S** | Sport | Discipline : Course à pied, Hyrox/hybrid, Cyclisme, Musculation... |
| **T** | Sponsor | Marque concurrente identifiée (ex: Ta.energy, Nutripure, CookNRUN, Mule Bar) |
| **U** | Followers (k) | Nombre de followers en milliers (ex: "6,4") |
| **V** | Date | Date de premier contact |
| **W** | Taux engagement | % d'engagement |
| **X** | Nb Story | Nombre de stories partagées en DM (rempli par `audit_ambassadors.py`) |
| **Y** | Nb post | Nombre de posts/reels partagés en DM (rempli par `audit_ambassadors.py`) |

**Col Z — Placeholder (inutilisé, à ignorer)**

**Bloc AA-AG — Infos personnelles**

| Col | Nom | Description |
|-----|-----|-------------|
| **AA** | Nom | Nom de famille |
| **AB** | Prenom | Prénom |
| **AC** | Mail | Email personnel |
| **AD** | Numéro | Téléphone |
| **AE** | Adresse | Adresse postale complète |
| **AF** | Commentaire | Notes libres (séparé de K Action/Commentaire) |
| **AG** | ID Influ | ID Instagram numérique |

---

### Valeurs possibles — Colonne J (Statut)

| Statut | Signification | Nb approx |
|--------|---------------|-----------|
| `In-cold` | **2 messages envoyés sans réponse.** Le pitch a déjà été fait. Prochaine action = réagir à une story (warm-up post-pitch pour relancer l'attention, pas pré-pitch) | ~200 |
| `In-hot` | **L'influenceur a répondu** (même un simple "je regarde"). Dès qu'il y a une réponse → passage en In-hot. Échange actif en cours | ~38 |
| `A recontacter` | A plus ou moins dit oui, est intéressé. On doit revenir vers lui pour finaliser (envoi adresse, choix produits, etc.) | ~14 |
| `A rediscuter` | A répondu MAIS : soit le profil n'est pas idéal, soit il demande quelque chose en retour (négo), soit il y a une raison spécifique de temporiser. Différent de "A recontacter" = ici il y a un frein | ~22 |
| `Contacter manager` | Doit passer par un agent/manager. Négo plus structurée : contrat, budget, livrables précis. Contact par mail via le manager (FraichTouch, Püls Agency, Versacom, Wild Summit) | ~3 |
| `Produits envoyés` | Ambassadeur actif, produits expédiés, code créé | ~124 |
| `Out` | Refusé, déjà pris, ou impossible à contacter | ~6 |

### Colonne K (Action/Commentaire) — texte libre

Anciennement une dropdown stricte (col D "Action"), maintenant un champ texte libre en col K. Notes brèves sur la situation actuelle, qui fonctionne en synergie avec les autres colonnes (Statut, Priorité, Campagne).

**Format standard** : `[verbe d'action] — [contexte]`

**Verbes d'action principaux** (par fréquence) :

| Verbe | Signification | Statuts concernés |
|-------|---------------|-------------------|
| `réagir à story` | Warm-up : réagir à une story pour maintenir le contact (post-pitch, pas pré-pitch) | In-cold |
| `à relancer` | Relance nécessaire, sans contexte spécifique | In-cold |
| `relancer` | Relance active avec contexte (ex: "relancer — pas de réponse au pitch") | A rediscuter, In-hot, Produits envoyés |
| `répondre` | L'influenceur attend une réponse de nous | In-hot, Produits envoyés |
| `appeler` | Call à planifier ou à passer, souvent avec numéro de tel | In-hot, A recontacter |
| `attendre` | On attend un retour de l'influenceur (sélection, panier, retour...) | In-hot, A recontacter |
| `préparer commande` / `préparer la commande` | Call fait, infos reçues, commande à créer | A recontacter, In-hot |
| `contacter manager` | Passer par l'agent/manager (avec email) | Contacter manager |
| `convenir call` | Trouver un créneau pour un appel | In-hot |
| `RAS` | Rien à signaler, tout est en ordre | Produits envoyés |

**Patterns par statut "Produits envoyés"** (ambassadeurs actifs) :

| Pattern col K | Signification |
|---------------|---------------|
| `RAS - promo envoyée` | Promo envoyée, ambassadeur n'a pas réagi, rien à faire |
| `promo envoyée, pas de retour — RAS` | Idem, formulation alternative |
| `relancer — promo envoyée, pas de réponse` | Promo envoyée mais devrait relancer |
| `commande + code envoyés — attendre premiers partages` | Nouvel ambassadeur, en attente de premiers contenus |
| `commande envoyée — attendre réception et premiers partages` | Idem |
| `partenariat actif — RAS` | Ambassadeur actif, tout roule |
| `a partagé un reel mention, réagir/remercier` | A mentionné Impulse dans un reel, répondre avec enthousiasme |
| `a partagé des stories — répondre pour féliciter` | A partagé des stories, idem |
| `a dit 'merci beaucoup' pour la promo` | A répondu à la promo, accuser réception |
| `attendre — a liké un message, pas d'action urgente` | Pas d'action requise |
| `répondre — retour négatif sur le goût...` | Feedback négatif, proposer alternative |

**Informations personnelles dans col K** :
Quand un influenceur donne ses coordonnées pendant un échange DM, Antoine les note directement dans col K en attendant de les reporter dans les colonnes dédiées (AC mail, AD numéro, AE adresse). Format typique : `préparer commande — tel (06XXXXXXXX), mail (xxx@xxx.com)`

### Colonne M (Campagne)

Colonne dédiée aux vagues de campagne. Format : `[Nom campagne]` → `[Nom campagne] OK` ou `[Nom campagne] SKIP`.
Exemples : `Promo-20% mars`, `Promo-20% mars OK`, `Promo-20% mars SKIP`.

Utilisée par `run_campaign.py` pour le tracking automatique.

**Backfill** : Si une campagne a été envoyée manuellement (ancien script ou envoi direct) sans écrire en col M, il faut backfiller en identifiant les ambassadeurs ayant reçu la promo via le contenu de col K (recherche de "promo envoyée", "-20% check", "pour la promo", etc.) et marquer `[Nom campagne] OK` pour tous. Ne pas se limiter à un sous-ensemble — scanner toutes les lignes "Produits envoyés".

---

### Onglets à ne pas modifier

| Onglet | Notes |
|--------|-------|
| **Dashboard** | Todo perso d'Antoine, ne pas modifier |
| **Feuille 20** | Projet futur (calendrier contenus), pas encore utilisé |
| **Suivi_Amb_OLD** | Ancien Suivi_Amb conservé comme backup, ne pas modifier |

---

### Processus manuels (hors sheet)

- **Création codes Affiliatly** : faite manuellement par Antoine sur la plateforme Affiliatly. Le nom du code est choisi au feeling (prénom, pseudo, combinaison). Pas d'automatisation.
- **Adaptation pitch si sponsor (col T)** : quand un concurrent est identifié, Antoine adapte le premier message (ex: "je vois que tu bosses avec X, on propose quelque chose de différent..."). Toujours vérifier col T avant de rédiger un premier message.
- **Négociation managers** : quand statut = "Contacter manager", la négo est différente — plus structurée avec contrat formel, budget, livrables précis. Le contact se fait par mail via le manager (FraichTouch, Püls Agency, Versacom, Wild Summit).
- **Followers** : pas de seuil minimum fixe. Tous les profils dans le tableau (sauf Out) sont qualifiés et ont été contactés au moins une fois.
- **Utilisateurs du sheet** : Antoine (principal, édite) + Pierre (consulte).

---

### Suivi_Dot — Colonnes clés

| Col | Nom | Description |
|-----|-----|-------------|
| **A** | Name | Nom complet |
| **B** | Management | Agence/manager (si applicable) |
| **C** | Statut Deal | `En cours`, etc. |
| **D** | Type | `Dot` (dotation) |
| **E** | Action / Com | Idem Suivi_Amb |
| **F** | Mail | Email |
| **G** | Numéro | Téléphone |
| **H-I** | Prénom / Nom | Identité |
| **J** | Affiliatly | `Yes` si compte créé |
| **K** | ID Influ | ID Instagram |
| **L** | Insta | Username |
| **Q** | Code | Code affilié |
| **R** | Util YTD | Utilisations année en cours |
| **S** | kF Actual | Followers actuels (k) |
| **W-AB** | Contrat | Followers init, Fixe, Variable, Budget total, Début/Fin, Durée, Dotation € |
| **AF-AK** | Livrables | Bio/LinkT, À la une, Réels, Stories, TikTok, PDF contrat |

---

### Suivi_Paid — Colonnes clés

Similaire à Suivi_Dot mais avec :
- **Type** : `%` (commission) ou `€` (fixe)
- **U** : Fixe (montant fixe du contrat)
- **V** : Var. prov. (variable provisoire)
- **W** : Budget total
- Ex: Dorian Louvet (FraichTouch) = 50k€ budget, 10% commission
- Ex: Lestraileurs = 3500€ fixe

---

### Message_type — Générateur de messages

Onglet utilitaire qui génère automatiquement les messages à partir du username sélectionné en B1 :
- **B3** : Prénom (récupéré auto de Suivi_Amb)
- **B4** : Sponsor (récupéré auto)
- **B5** : Code affiliation
- **B6** : Lien affiliation
- **F3** : Prénom expéditeur (Antoine)
- **F4** : Type de programme (Amb-Crédit)
- **B9** : Premier message généré
- **F9** : Second message (explication détaillée du programme)
- **J9** : Message envoi commande (avec code + lien)

Contient aussi des variantes :
- Message si déjà pris (refus poli)
- Message si déjà pris mais porte ouverte (mention produits récup)
- Message si déjà pris mais partenaire axé effort
- Demande d'utilisation de code
- Réponse stories manquées

---

### StratAmba — Niveaux du programme

| Niveau | Contenu min | Crédit | Dotation/mois | Rémunération |
|--------|-------------|--------|---------------|--------------|
| **Entrée ambassadeur** | 3 contenus global | 20€/utile | - | - |
| **Discussion partenariat rému** | 1 post/reel + 3 stories | 15 utiles en 3 mois | 100€ | 10€/utile |
| **Ambassadeur dotation** | 1 post/reel + 3 stories | - | Selon profil | - |

---

## Workflow : Priorités DM (colonne L)

Quand Antoine demande "check les DMs et mets à jour les priorités", appliquer ces règles :

| Priorité | Critères |
|----------|----------|
| **high** | Dernier message = de l'influenceur (non répondu par nous) OU col K contient "répondre" / "préparer commande" / "appeler" / "envoyer code" |
| **medium** | Dernier message = de nous (on attend une réponse) OU col K contient "relancer" / "réagir story" / "contacter manager" / "demander avis" |
| **good** | Partenariat actif, tout est en ordre (sauf si dernier msg de l'influenceur → passe en high) |

### Processus d'exécution

1. Lire Suivi_Amb colonnes I (usernames), K (Action/Commentaire), L (Priorité actuelle), AG (ID Influ)
2. Pour chaque username : `mcp__instagram_dms__get_thread_by_participants` → `mcp__instagram_dms__list_messages`
3. Analyser : dernier sender (nous vs eux), contenu du dernier message, date
4. Croiser avec col K (Action/Commentaire) pour affiner
5. Assigner priorité selon les règles ci-dessus
6. Mettre à jour col L via `mcp__google_sheets__update_cells`

Script : `update_priorities.py`

---

## Workflow : Campagne

Pour envoyer une campagne (ex: promo -20%) :

1. Écrire le nom de campagne dans col M pour les ambassadeurs ciblés (ex: `Promo-20% avril`)
2. Lancer `run_campaign.py --campaign "Promo-20% avril" --message-file promo.txt`
3. Le script qualifie chaque conversation (vérifie qu'on n'a pas de message en attente)
4. Envoie le message, marque col M = `Promo-20% avril OK` (ou `SKIP` si non qualifié)
5. Le suivi est visible dans Analyses > Campagne en cours

---

## Workflow : Audit ambassadeurs

Pour mettre à jour les colonnes R, X, Y (Bio, Nb Story, Nb post) :

1. Lancer `audit_ambassadors.py` (cible : Statut = "Produits envoyés")
2. Pour chaque ambassadeur :
   - `get_user_info` → check bio pour "impulse" ou code affilié → col R
   - `list_messages` → compte les item_type story_share → col X, post_share/reel_share → col Y
3. Résultats écrits automatiquement dans le sheet

---

## Workflow : Répondre comme Antoine

Quand on demande de rédiger un DM :
1. Consulter `personality.md` pour le style, le ton et les templates
2. Identifier le type de message (premier contact, relance, onboarding, promo, réponse)
3. Adapter le template avec les infos du contexte (prénom, code, produits, etc.)
4. Utiliser le vocabulaire et le ton d'Antoine
5. Ne JAMAIS vouvoyer, ne JAMAIS être trop marketing

---

## Outils MCP disponibles

### Instagram DM MCP (`mcp__instagram_dms__`)
- `list_chats` : Lister les conversations récentes
- `list_messages` : Messages d'un thread
- `send_message` : Envoyer un DM texte
- `send_photo_message` : Envoyer une photo en DM
- `send_video_message` : Envoyer une vidéo en DM
- `search_threads` : Chercher un thread par username/mot-clé
- `get_thread_by_participants` : Trouver un thread par user IDs
- `list_pending_chats` : Messages en attente (requests)
- `get_user_info` : Infos d'un profil
- `get_user_id_from_username` : Convertir username → user ID
- `search_users` : Rechercher des utilisateurs
- `mark_message_seen` : Marquer comme lu
- `delete_message` : Supprimer un message
- `mute_conversation` : Mettre en sourdine

### Google Sheets MCP (`mcp__google_sheets__`)
- `get_sheet_data` : Lire des données
- `update_cells` : Mettre à jour des cellules
- `find_in_spreadsheet` : Rechercher dans le sheet
- `list_sheets` : Lister les onglets
- `batch_update_cells` : Mise à jour en lot

---

## Vocabulaire / Lexique

| Terme | Signification |
|-------|---------------|
| **Affiliatly** | Plateforme de gestion des codes affiliés |
| **Code affilié** | Code promo personnalisé de l'ambassadeur (ex: MANU, JESSD, NADIARUN) |
| **Crédit** | 20 € débloqués par commande passée avec le code, utilisables sur impulse-nutrition.fr |
| **Dotation** | Envoi gratuit de produits contre contenu (pas de code affilié) |
| **Suivi_Amb** | Onglet principal du Google Sheet — tous les ambassadeurs |
| **Suivi_Dot** | Onglet dotation |
| **Suivi_Paid** | Onglet partenariats rémunérés |
| **Gamme Au Quotidien** | Gamme de produits bien-être/santé (vs gamme Sport) |
| **Enveloppe** | Budget produits alloué pour un ambassadeur (~80-100 €) |
| **RAS** | Rien à signaler — tout est en ordre |

---

## Fichiers du projet

| Fichier | Description |
|---------|-------------|
| `CLAUDE.md` | Ce fichier — contexte global du projet |
| `personality.md` | Style guide d'Antoine avec templates et exemples |
| `conversations/corpus.json` | ~50 conversations Instagram réelles (données personnelles, gitignored) |
| `src/mcp_server.py` | Code source du MCP server Instagram DM |
| `migrate_suivi_amb.py` | Migration one-shot ancien → nouveau sheet (déjà exécuté) |
| `run_campaign.py` | Envoi de campagne générique — remplace `send_promo_20pct.py` |
| `update_priorities.py` | Check DMs Instagram → remplit col L (Priorités identifiées) |
| `audit_ambassadors.py` | Audit bio + partages DM → remplit cols R, X, Y |
| `refresh_analyses.py` | Écrit les formules COUNTIF/SUM dans l'onglet Analyses |
| `qualify_conversations.py` | Script de qualification des conversations (logique réutilisée dans run_campaign.py) |
| `send_promo_20pct.py` | ⚠️ **Ancien** — remplacé par `run_campaign.py` |

---

## Notes importantes

- **Données personnelles** : `conversations/corpus.json` contient des adresses, emails, numéros de téléphone. Ne JAMAIS partager, committer, ou exposer ces données.
- **Rate limiting** : Les appels Instagram sont sensibles au rate limiting. Espacer les appels si nécessaire.
- **Session** : Le MCP utilise une session Instagram stockée dans `*_session.json`. Si la session expire, relancer `create_session.py`.
- **Ton** : Toujours se référer à `personality.md` avant de rédiger un message. Le style d'Antoine est son identité professionnelle.
