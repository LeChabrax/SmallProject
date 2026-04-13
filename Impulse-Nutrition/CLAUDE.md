# Impulse Nutrition — Factory Workspace

## Navigation rapide
> **[`docs/INDEX.md`](./docs/INDEX.md)** — point d'entrée unique pour tout (reference docs, process runbooks, templates, scripts).
>
> Références canoniques :
> - Pipeline ambassadeur / dotation / paid → [`docs/reference_contract_types.md`](./docs/reference_contract_types.md)
> - Colonnes Google Sheet (source de vérité) → [`docs/reference_sheet_schema.md`](./docs/reference_sheet_schema.md)
> - MCP tools (12 BigBlue + 12 Gorgias + 15 Shopify + 26 Instagram) → [`docs/reference_mcps.md`](./docs/reference_mcps.md)
> - Process SAV complet → [`docs/process_sav_unified.md`](./docs/process_sav_unified.md)
> - Architecture / carte codebase → [`LLM.md`](./LLM.md) (auto-généré par `/codebase-memory`)

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
| In-cold | Identifié, pas encore contacté OU premier msg envoyé **sans réponse + > 7 jours depuis le dernier message envoyé**. C'est la zone "à relancer" naturelle. |
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

## Programme ambassadeur

### Conditions standard
- **Envoi initial** : ~80-100 EUR de produits gratuits
- **Code affilié** : -15% sur la première commande pour les abonnés
- **Bonus** : Shaker offert dès 59 EUR
- **Crédit ambassadeur** : 20 EUR par commande réalisée avec le code
- **Contenu** : Format libre (stories, posts, reels, Strava)
- **Evolution** : Partenariat rémunéré si très bons résultats

### Niveaux (StratAmba)
| Niveau | Contenu min | Crédit | Dotation/mois |
|--------|-------------|--------|---------------|
| Entrée ambassadeur | 3 contenus global | 20EUR/utile | - |
| Discussion partenariat rému | 1 post/reel + 3 stories | 15 utiles en 3 mois | 100EUR |
| Ambassadeur dotation | 1 post/reel + 3 stories | - | Selon profil |

---

## Spreadsheets

### Suivi_Amb (principal)
- **ID** : `1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4`
- **Onglet** : `Suivi_Amb`
- **⚠️ Source canonique** : [`docs/reference_sheet_schema.md`](./docs/reference_sheet_schema.md) — certaines colonnes listées ci-dessous ont dérivé depuis la dernière mise à jour de ce fichier.
- **Colonnes clés** :
  - I = username Instagram
  - J = statut (pipeline)
  - K = action/commentaire
  - L = priorité (high/medium/good)
  - W = date premier contact
  - AA = nom, AB = prénom, AC = mail, AD = numéro, AE = adresse
  - AF = commentaire, AG = ID Influ
  - H = lien Instagram
  - N = code affilié
  - O = nb utilisations du code
  - P = code crédit (ex: CREDITUSE — code dotation utilisable sur le site)
  - Q = nb credit used (négatif, ex: -3 = 3 × 20€ consommés via code CREDITUSE)
  - R = lien affilié
  - S = bio (oui/Non, présence "impulse" ou code dans la bio)
  - T = sport (discipline)
  - U = sponsor concurrent identifié
  - V = followers (k)
  - W = date premier contact
  - X = taux engagement
  - Y = nb story partagées en DM
  - Z = nb post/reels partagés en DM

### Colonne K (Action/Commentaire) -- verbes d'action principaux
| Verbe | Signification | Statuts |
|-------|---------------|---------|
| réagir à story | Warm-up post-pitch | In-cold |
| à relancer | Relance sans contexte | In-cold |
| répondre | L'influenceur attend une réponse | In-hot, Produits envoyés |
| appeler | Call à planifier | In-hot, A recontacter |
| attendre | On attend un retour | In-hot, A recontacter |
| préparer commande | Infos reçues, commande à créer | A recontacter, In-hot |
| RAS | Tout en ordre | Produits envoyés |

### Colonne M (Campagne)
Format : `[Nom campagne]` puis `[Nom campagne] OK` ou `SKIP` après traitement.

### Suivi_Paid (contrats payants)
- **Même spreadsheet ID**, onglet `Suivi_Paid`
- 3 lignes header (rows 1-3), data commence row 4
- **Règle absolue : "la vérité vient toujours du contrat"** — toujours lire le PDF/docx Drive avant d'écrire

#### Colonnes clés
| Col | Contenu |
|---|---|
| W | Fixe (€ HT total sur durée) |
| X | Var. provisionnelle |
| Y | Budget total |
| Z | Début (date) |
| AA | Fin (date) |
| AB | Durée (ex: "12 mois") |
| AC | €/% |
| AD | Dotation mensuelle (€) |
| AE | Seuil utilisation |
| AF | Bio/LinkT (lien affilié en bio → "Bio") |
| AG | À la une (story highlight → "Oui") |
| AH | Réels/posts (total sur durée contrat) |
| AI | Stories (total sur durée contrat) |
| AJ | YouTube (total sur durée contrat) |
| AK | Strava ("Oui" si obligation) |
| AL | TikTok |
| AM | PDF (lien Drive) |

#### Mapping rows → ambassadeurs (état 2026-03)
| Rows | Ambassadeur |
|---|---|
| 4-5 | Dorian (codes DODO + LRA20) |
| 6 | Lestraileurs |
| 7 | Aubin |
| 8 | Aurelio |
| 9 | Bornes |
| 10 | Caroline |
| 11 | Charlotte Martin |
| 12 | Charlotte/Fred |
| 13 | Shirley |
| 14 | Marine |
| 15 | Gautier |
| 16 | Julia |
| 17 | JB Burbaud |
| 18 | Johann |
| 19 | Julie Ferrat |
| 20 | NTV |
| 21 | Loulouvavite |
| 22 | Lucas |
| 23 | Marie Oheix |
| 24 | Matthieu |
| 25 | Loréna |
| 26 | Alice |
| 27 | Nouchka |
| 28 | Pinaliste |
| 29 | Gedeon |
| 30 | Baptiste |
| 31 | Valentin |
| 37 | Tanguy |
| 39 | Paul Besson |
| 40-41 | Anna |
| 42 | Sarah |
| 43 | Stanley |
| 44 | Mathilde |

#### Bug connu : sériel Excel dans colonnes date
Si une colonne est formatée "date" et qu'on y entre un nombre (ex: dotation 150), Google Sheets l'affiche comme "29/05/1900" (serial 150). Fix : réécrire la valeur numérique correcte via `batch_update_cells`.

#### Bug connu : décalage colonnes rows 42-44
Les colonnes G-J de Sarah/Stanley/Mathilde étaient décalées d'une colonne (colonne G vide). Toujours vérifier G/H/I/J avant de modifier les dernières lignes.

### AdHoc (tâches et MCP roadmap)
- **Même spreadsheet**, onglet `AdHoc`
- Tableau de priorisation des tâches automation (P1/P2/P3)

---

## Process : Remplir Suivi_Paid depuis les contrats Drive

### Principe
Les contrats signés sont stockés dans Google Drive, dossier **InfluenceContract** (`1dxT2gSAm6tcnd8Ck6hXxPDS5yieMuj4x`). Ils existent en deux formats : PDF et .docx. La source de vérité est toujours le contrat, jamais le sheet.

### Accès Drive (service account)
```python
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io

creds = service_account.Credentials.from_service_account_file(
    '/Users/antoinechabrat/.config/google-service-account.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)
service = build('drive', 'v3', credentials=creds)

# Lister les fichiers du dossier
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name, mimeType)"
).execute()

# Télécharger un .docx (NE PAS utiliser export_media — réservé aux Google Docs natifs)
request = service.files().get_media(fileId=file_id)
buf = io.BytesIO()
dl = MediaIoBaseDownload(buf, request)
done = False
while not done:
    _, done = dl.next_chunk()
with open('out.docx', 'wb') as f:
    f.write(buf.getvalue())
```

### Extraction texte .docx
```python
from docx import Document
doc = Document('out.docx')
text = '\n'.join([p.text for p in doc.paragraphs])
# Chercher : DUREE, OBLIGATIONS, REMUNERATION
```

### Sections clés à lire dans chaque contrat
- **DURÉE** → Début, Fin, Durée (mois)
- **OBLIGATIONS / CONTREPARTIES** → AH (réels), AI (stories), AJ (YouTube), AK (Strava), AF (bio), AG (à la une)
- **RÉMUNÉRATION / BUDGET** → W (fixe HT), AD (dotation mensuelle)

### Erreur fréquente : `export_media()` interdit sur .docx
`HttpError 403 "Export only supports Docs Editors files."` → utiliser `get_media()` à la place.

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
- `{prenom}` -- prénom de l'ambassadeur
- `{code}` -- code affilié (ex: FLORINE)
- `{lien}` -- lien affilié (https://impulse-nutrition.fr/discount/{code})
- `{produits}` -- liste de produits sélectionnés
- `{adresse}` -- adresse de livraison

---

## MCP TikTok Shop

### Configuration
Le MCP TikTok Shop est configuré dans `.mcp.json` sous la clé `tiktokshop`. Il pointe vers le build du projet `/Users/antoinechabrat/Documents/SmallProject/Tiktok/MCP-TikTokShop/`.

- **App Key** : `6jg392kv2s7j7`
- **Shop** : Impulse Nutrition (FR), cipher `GCP_Gk8uhwAAAAC2CxX0AMBN6sG3U3fncQGS`
- **Scopes** : `seller.product.basic`, `seller.product.write`, `seller.order.info`, `seller.shop.info`, etc.

### Renouvellement du token
L'access token expire (~15 jours). Si les appels TikTok retournent une erreur 401/token invalide :
```bash
cd /Users/antoinechabrat/Documents/SmallProject/Tiktok/MCP-TikTokShop && npm run auth
```
Puis mettre à jour le `TIKTOK_SHOP_ACCESS_TOKEN` dans `.mcp.json` et relancer Claude Code.

### Tools disponibles
| Tool | Description | Status |
|------|-------------|--------|
| `list_products` | Liste les produits avec stock/inventaire par SKU | OK |
| `get_product_detail` | Détail complet d'un produit (SKUs, stock, prix, images) | OK |
| `list_orders` | Liste les commandes TikTok Shop | OK |
| `get_order_detail` | Détail d'une commande par ID | OK |
| `list_conversations` | Conversations SAV TikTok | Bloqué (scope `seller.customer_service` manquant) |
| `read_conversation` | Lire les messages d'une conversation | Bloqué (idem) |
| `reply_to_conversation` | Répondre à un client | Bloqué (idem) |
| `list_reviews` | Avis produits | Bloqué (endpoint pas dispo marché FR ?) |
| `reply_to_review` | Répondre à un avis | Bloqué (idem) |

> **En attente** : demande de scopes supplémentaires en cours auprès de TikTok (avril 2026).

---

## Vocabulaire

| Terme | Signification |
|-------|---------------|
| Affiliatly | Plateforme de gestion des codes affiliés |
| Code affilié | Code promo personnalisé (ex: MANU, JESSD, NADIARUN) |
| Crédit | 20 EUR débloqués par commande passée avec le code |
| Dotation | Envoi gratuit de produits contre contenu |
| Enveloppe | Budget produits alloué (~80-100 EUR) |
| RAS | Rien à signaler |
| Gamme Au Quotidien | Gamme bien-être/santé (vs gamme Sport) |
