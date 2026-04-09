# Plan : Reverse-engineering API BigBlue Claims

## Context
BigBlue (3PL d'Impulse Nutrition) n'a pas d'API publique pour ouvrir des réclamations (colis perdu, endommagé, etc.). Aujourd'hui Antoine doit les ouvrir manuellement via le dashboard web. L'objectif est de reverse-engineer l'API interne utilisée par le dashboard pour reproduire les appels en Python, et ajouter un tool `open_claim` au MCP BigBlue existant.

## Auth BigBlue
- Système de **magic link** (passwordless) : on entre l'email, BigBlue envoie un lien par email (Outlook), on clique, ça crée une session
- Pas de mot de passe, pas de 2FA classique

## Étapes

### 1. Intercepter le flow d'auth
- Ouvrir BigBlue avec Playwright
- Antoine entre son email, clique le magic link
- Capturer les network requests pour comprendre le cookie/token de session et sa durée de vie

### 2. Intercepter le flow réclamation
- Naviguer vers une commande livrée
- Cliquer "Signaler un problème"
- Capturer toutes les requêtes réseau : URL endpoint, headers, body JSON
- Identifier les types de réclamation : damaged, missing, never_received, wrong_product

### 3. Reproduire en Python
- Tester l'appel avec `requests` + token de session
- Vérifier que ça fonctionne hors navigateur

### 4. Ajouter au MCP BigBlue
- Fichier : `bigblue_mcp/src/mcp_server.py`
- Nouveau tool : `open_claim(reference, claim_type, description)`
- Gestion auth : stocker le cookie, alerter quand il expire

### 5. Auth long terme
- **Option A** : Cookie longue durée dans `.env`, refresh manuel occasionnel
- **Option B** : Microsoft Graph API pour lire le magic link Outlook automatiquement
- **Option C** : Playwright en fallback pour le login
- Décision après avoir vu la durée de vie du cookie
