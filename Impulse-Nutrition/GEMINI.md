# Impulse Nutrition — Agent Guidelines (GEMINI.md)

Ce fichier sert de mémoire et de guide opérationnel pour l'agent Gemini CLI travaillant sur le projet Impulse Nutrition.

## 🎯 Objectif du Repo
Gérer le programme ambassadeur et l'influence d'Impulse Nutrition via Google Sheets et Instagram.

## 📊 Google Sheets (ID: 1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4)

### Onglet `Suivi_Amb` (Le cœur du réacteur)
- **Col I (8)** : Username Instagram (toujours nettoyer le '@' avant usage API).
- **Col L (11)** : Priorité (`high`, `medium`, `good`).
- **Col O (14)** : Nombre d'utilisations du code promo (Ventes).
- **Col AC (28)** : **PRÉNOM RÉEL** (C'est ici qu'il faut chercher pour personnaliser les messages).
- **Col AG (32)** : `ID Influ` (ID numérique Instagram). Si vide, il faut le résoudre via le username.

### ⚠️ Bonnes Pratiques Sheets
- **Batch Updates** : Ne jamais mettre à jour les cellules une par une (limite API 429). Toujours privilégier `ws.update('A1:B10', values)` ou `ws.batch_update()`.
- **Filtres** : Toujours filtrer les comptes avec `Statut != 'Out'` pour les opérations de masse.

## 📸 Instagram DM & MCP

### Outils & Scripts
- Les scripts doivent être lancés depuis le dossier `instagram_dm_mcp/` avec `uv run <script>.py`.
- **`update_priorities.py`** : Script principal pour synchroniser l'état des DMs avec la colonne L du Sheet.
- **`src/mcp_server.py`** : Serveur MCP pour envoyer des messages, lister les chats et messages.

### ⚠️ Stabilité Instagram
- La recherche par `user_id_from_username` peut échouer (JSONDecodeError).
- **Alternative robuste** : Lister les 100 derniers fils (`cl.direct_threads(100)`) et chercher le username dans les participants pour obtenir le `thread_id`.

## ✍️ Ton de Voix & Communication
- **Tutoiement** : Systématique avec les ambassadeurs.
- **Style** : Enthousiaste, pro, utilise des emojis (`🔥`, `🚀`, `💪`, `😉`).
- **Signature** : Toujours finir par "Sportivement, Antoine".
- **Variables** : Utiliser le prénom (Col AC) pour personnaliser l'accroche ("Hello [Prénom] !").

## 🛠 Workflows Standards

### Recheck des DMs & Priorités
1. Lancer `uv run update_priorities.py`.
2. Si l'update Sheet échoue (429), utiliser `recover_updates.py` pour un push groupé.

### Félicitations Ventes (2+ utilisations)
1. Identifier les cibles (Col O >= 2).
2. Récupérer l'historique (thread_id via `direct_threads`).
3. Drafter un message personnalisé citant le nombre de ventes.
4. Valider avec l'utilisateur avant envoi.

---
*Dernière mise à jour : Dimanche 29 Mars 2026*
