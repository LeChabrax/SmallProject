# Plan : Filtrage KolSquare + dédoublonnage + check MCP

## Contexte
Antoine a un export KolSquare de 969 profils. On veut :
1. Filtrer par métier (règles dans `tools/veille_kolsquare/filtering_rules.md`)
2. Dédoublonner avec les profils déjà dans les sheets (Suivi_Amb, Suivi_Dot, Suivi_Paid)
3. Sortir une liste propre de profils a checker ensuite via MCP Instagram

Le check MCP (5 derniers posts + bio) viendra dans un second temps.

## Phase 1 : Script de filtrage CSV + dédoublonnage

### Fichier a créer
`filter_kolsquare.py`

### Etapes du script

#### 1. Charger le CSV KolSquare
- Fichier : `tools/veille_kolsquare/09-04-2026_IMPULSE - 09_04_26_Casting_fr-FR.csv`
- Séparateur : `;`
- Extraire : username Instagram (colonne `Pseudo 1`, index 11), followers (col `Taille de communauté 1`, index 13), engagement (col `Taux d'engagement 1`, index 14), métier (col `Métier(s)`, index 4), nom/pseudo, emails

#### 2. Filtrer par métier
- Appliquer les règles de `tools/veille_kolsquare/filtering_rules.md`
- Liste des métiers exclus codée en dur dans le script
- Profils sans métier ("-") : gardés
- Profils multi-métiers (séparés par virgule) : garder si au moins un métier est dans la liste d'inclusion

#### 3. Fetch des usernames existants dans Google Sheets
- Via Google Sheets API (service account `/Users/antoinechabrat/.config/google-service-account.json`)
- **Suivi_Amb** : colonne I (username Instagram), spreadsheet `1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4`
- **Suivi_Dot** : colonne M (username Instagram), même spreadsheet
- **Suivi_Paid** : identifier les usernames (a vérifier quelle colonne)
- Constituer un set de tous les usernames déjà connus

#### 4. Dédoublonner
- Retirer du CSV filtré tous les profils dont le username Instagram est déjà dans un des sheets
- Normaliser les usernames (lowercase, strip @)

#### 5. Output
- Écrire un CSV filtré : `tools/veille_kolsquare/filtered_prospects.csv`
- Colonnes : username, nom, métier, followers, engagement, emails, statut (P1/P2/P3)
- Priorisation :
  - P1 : métier sport/fitness + engagement > 1% + 5k-50k followers
  - P2 : métier sport/fitness + engagement > 0.5% + 2k-100k followers
  - P3 : sans métier ou lifestyle, a vérifier
- Afficher un résumé : nb total, nb exclus par métier, nb doublons, nb par priorité

---

## Phase 2 (futur) : Check MCP Instagram

A faire après la phase 1, sur la liste filtrée :
- Pour chaque profil restant, via MCP `instagram_veille` :
  - `get_user_info(username)` → bio, followers, following, is_private, media_count
  - `get_user_posts(username, limit=5)` → engagement des 5 derniers posts
- Scoring : bio keywords sport/nutrition, sponsors concurrents, engagement, ratio following/followers
- Output : liste scorée avec verdict GO / MAYBE / NO-GO

---

## Vérification
- Lancer le script sur le CSV
- Vérifier le nb de profils exclus par métier
- Vérifier que les doublons sont bien retirés (croiser avec un username connu du sheet)
- Vérifier le CSV de sortie
