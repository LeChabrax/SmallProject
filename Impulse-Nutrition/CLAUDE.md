# Impulse Nutrition — Factory Workspace

## Qui sommes-nous
**Impulse Nutrition** est une marque française de nutrition sportive (compléments alimentaires, boissons d'effort, whey, preworkout, etc.) distribuée via [impulse-nutrition.fr](https://impulse-nutrition.fr). La marque appartient à **HAVEA COMMERCIAL SERVICES (HCS)**, SAS basée à Montaigu-Vendée.

**Antoine Chabrat** — Influence Manager, gère le programme ambassadeur et les partenariats influenceurs.

## Ton de voix
- Tutoiement systématique avec les ambassadeurs
- Signature : "Sportivement, Antoine"
- Ton : enthousiaste mais pro, jamais pushy
- Emojis : modérés (😉🔥💪), pas de surcharge

---

## Pipeline Ambassadeur

### Statuts (col J du sheet)
```
In-cold → In-hot → A recontacter / A rediscuter → Contacter manager → Produits envoyés → Out
```

| Statut | Signification |
|---|---|
| In-cold | Identifié, pas encore contacté ou premier msg envoyé sans réponse |
| In-hot | A répondu positivement, en discussion active |
| A recontacter | À relancer plus tard (délai convenu, absence temporaire) |
| A rediscuter | Discussion en pause, nécessite relance |
| Contacter manager | Passer par une agence/manager (Puls, Versacom, etc.) |
| Produits envoyés | Commande validée, produits expédiés, code affilié créé |
| Out | Refus, déjà pris, ou conversation terminée |

### Priorités (col L)
| Priorité | Quand |
|---|---|
| high | Action urgente requise (répondre, appeler, corriger une erreur) |
| medium | En attente, surveiller, relancer si pas de retour |
| good | RAS, tout va bien, pas d'action immédiate |

### Règle générale statut (L)
- **Antoine est le dernier à avoir envoyé** → L = good
- **Antoine a liké le dernier message de l'autre** → L = good
- **L'autre a envoyé un message sans réponse ni like d'Antoine** → L = high (à signaler)
- **"En vue"** (message d'Antoine lu mais pas répondu) → L = medium

---

## Règles de catégorisation DMs

### Messages vocaux (`voice_media`)
- `item_type == "voice_media"` et `is_sent_by_viewer == False` → **L = high**
- Exception : si Antoine a liké le message → L = good (il a écouté)
- K = "message vocal non lu — à écouter manuellement"

### Messages éphémères (`raven_media`)
- `item_type == "raven_media"` → **L = medium/high** (contenu inaccessible via MCP)
- K = "raven media reçue [date] — contenu inaccessible"

### Réponse positive à relance
- Toute réponse positive à un message de relance → **J = In-hot, L = high**
- Formulations : "c'est intéressant", "je suis attentive", "ça me plairait", "pourquoi pas"

### Post annoncé
- Si ambassadeur dit "je vais poster ce soir/demain" → K = "a annoncé post le [date] — vérifier tag @impulse_nutrition"

### Clubs / organisations / contrats payants
- Messages contenant "nous" (pluriel = club/duo), "Head Coach", "je représente [club/asso]", projets events → **NE PAS ajouter au sheet Suivi_Amb**
- Signaler à Antoine dans le chat uniquement
- Ce sont des contrats payants, une catégorie différente

### xma_reel_mention
- Mention dans un reel = signal à vérifier au cas par cas
- Peut être une mention positive d'ambassadeur OU une mention spontanée d'un inconnu

---

## Spreadsheets

### Suivi_Amb (principal)
- **ID** : `1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4`
- **Onglet** : `Suivi_Amb`
- **Colonnes clés** :
  - I = username Instagram
  - J = statut (pipeline)
  - K = action/commentaire
  - L = priorité (high/medium/good)
  - V = date premier contact
  - AA = nom, AB = prénom, AC = mail, AD = numéro, AE = adresse
  - AF = commentaire, AG = ID Influ
  - H = lien Instagram
  - N = code affilié
  - P = lien affilié

### AdHoc (tâches et MCP roadmap)
- **Même spreadsheet**, onglet `AdHoc`
- Tableau de priorisation des tâches automation (P1/P2/P3)

---

## Scripts disponibles

### `generate_contract.py`
Génère un contrat PDF de partenariat Impulse Nutrition.
- 3 types : `dotation` (produits), `ambassadeur` (affiliation 20€/code), `paid` (budget fixe)
- Mode interactif ou CLI avec arguments
- Output : `contracts/Contract_Prenom_Nom_YYYY-MM-DD.pdf`
- Dépendance : `fpdf2`

Usage direct par Claude :
```bash
python3 generate_contract.py \
  --first-name "Florine" --last-name "Breysse" \
  --address "7 route de thones 74940 Annecy le vieux" \
  --date "26/03/2026" --duration 12 \
  --type ambassadeur --code FLORINE \
  --stories 3 --reels 1 --gender F
```

### `qualify_influencer.py`
Scoring automatique de profils Instagram pour qualification go/no-go.
- Analyse : followers, engagement rate, bio (sport/concurrent), ratio following/followers
- Score pondéré → verdict GO / MAYBE / NO-GO
- Écriture optionnelle dans l'onglet "Qualification" du Sheet

```bash
# Qualifier des usernames
python3 qualify_influencer.py user1 user2 user3 --write-sheet

# Depuis un fichier
python3 qualify_influencer.py --file prospects.txt --write-sheet

# Dry run
python3 qualify_influencer.py user1 user2 --dry-run
```

### `veille_concurrents.py`
Veille concurrentielle automatique via Instagram.
- Analyse les profils concurrents : followers, engagement, types de contenu
- Comparaison avec le compte Impulse Nutrition
- Écriture dans l'onglet "Veille" du Sheet

```bash
# Concurrents par défaut
python3 veille_concurrents.py

# Comptes spécifiques
python3 veille_concurrents.py --accounts ta.energy nutripure_fr

# Dry run
python3 veille_concurrents.py --dry-run
```

### `refresh_analyses.py`
Écrit les formules KPI dans l'onglet Analyses :
- Pipeline, actions, priorités, campagne, contenu
- Distribution engagement et followers
- Top performers (stories/posts)
- Sponsors concurrents détectés
- Distribution sports

```bash
python3 refresh_analyses.py [--dry-run]
```

---

## Process : Recheck DMs

### Étapes standard
1. `list_chats(100)` — récupérer les 100 threads les plus récents
2. Cross-ref avec le sheet (col I) — identifier qui est tracké, qui ne l'est pas
3. Pour chaque thread dans le sheet :
   - Vérifier qui a le dernier message (`is_sent_by_viewer`)
   - Appliquer les règles de priorité (voir section ci-dessus)
   - Mettre à jour K/L si nécessaire
4. Signaler les nouveaux inbound non trackés
5. Produire un brief : urgent / cette semaine / RAS

### Erreurs à éviter
- **Toujours vérifier les dates dans les DMs** — ne jamais se fier à une note "aujourd'hui/demain" dans K, fetcher le DM réel
- **Vérifier le thread_id** — avant d'analyser un thread, confirmer que le username correspond
- **Erreur réseau ≠ absence** — si `find_in_spreadsheet` échoue, ne pas conclure que le profil est absent
- **Ne jamais classifier sans lire le DM** — toujours croiser sheet + DM réel avant de conclure

### Timestamps Instagram
Les timestamps DM Instagram sont en **microsecondes** :
```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
date_str = dt.strftime("%d/%m/%Y")
```

---

## Contacts agences / managers
- **Puls Agency** : marie@puls-agency.com (Kelly, Marie Schoenenburg)
- **Versacom** : simon@versacom.eu (Arwen)
- **Fraich Touch** : gael@fraichtouch.com (Malo)
- **MyOpenComm** : yohann@myopencomm.com (Sacha)
- **HCS interne** : pgautier@havea.com (Pierre Gautier — commandes dotation)

---

## Templates messages

Les templates sont dans le dossier `templates/`. Variables disponibles :
- `{prenom}` — prénom de l'ambassadeur
- `{code}` — code affilié (ex: FLORINE)
- `{lien}` — lien affilié (https://impulse-nutrition.fr/discount/{code})
- `{produits}` — liste de produits sélectionnés
- `{adresse}` — adresse de livraison
