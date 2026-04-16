# Setup Onboarding -- Impulse Nutrition Workspace

Guide de setup complet pour un nouveau collaborateur. Couvre l'installation de Claude Code, le clonage du repo, la configuration des MCPs, et la mise en place des skills.

> Ce fichier est destine a etre lu par le LLM (Claude Code) du nouveau collaborateur. Il peut aussi etre lu par l'humain. Les deux y trouveront les infos necessaires.

---

## 1. Pre-requis

| Outil | Installation | Verification |
|---|---|---|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | `claude --version` |
| **uv** (Python) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `uv --version` |
| **Node.js** (v18+) | [nodejs.org](https://nodejs.org) ou `brew install node` | `node --version` |
| **Git** | Pre-installe sur macOS | `git --version` |

## 2. Cloner le repo

```bash
git clone https://github.com/LeChabrax/SmallProject.git
cd SmallProject/Impulse-Nutrition
```

Le repo est **prive**. Si tu n'as pas acces, demande a Antoine de t'ajouter comme collaborateur sur GitHub (Settings > Collaborators > Add people).

## 3. MCPs -- configuration automatique

Le fichier `.mcp.json` a la racine du projet contient la configuration de tous les MCPs (Instagram, Shopify, Gorgias, BigBlue, TikTok Shop, Google Sheets). **Il est committe dans le repo** avec les credentials reels.

Quand tu lances Claude Code depuis le dossier `Impulse-Nutrition/`, les 7 MCPs se connectent automatiquement.

### Ce qui marche out-of-the-box
- Instagram DM (`impulse_nutrition_fr`)
- Shopify Orders
- Gorgias
- BigBlue
- TikTok Shop
- Google Sheets (si service account en place, voir ci-dessous)

### Ce qui necessite une action manuelle

**A. Google Sheets service account**

Le MCP Google Sheets utilise un fichier de credentials JSON. Demande a Antoine le fichier `google-service-account.json` et place-le :

```bash
mkdir -p ~/.config
cp google-service-account.json ~/.config/google-service-account.json
```

**B. Instagram Veille (optionnel)**

Le compte `antman.lass` (veille concurrents) a un mot de passe masque dans `.mcp.json` (`"DEMANDER_A_ANTOINE"`). Si tu en as besoin, demande le mdp a Antoine et remplace dans `.mcp.json` :

```json
"INSTAGRAM_PASSWORD": "DEMANDER_A_ANTOINE"
```

**C. TikTok Shop MCP**

Le MCP TikTok Shop est un serveur Node.js dans un **repo separe** : `../Tiktok/MCP-TikTokShop/`. Tu dois cloner ce repo a cote :

```bash
cd ../..  # remonter a SmallProject/
git clone <url-repo-tiktok-mcp> Tiktok/MCP-TikTokShop
cd Tiktok/MCP-TikTokShop
npm install && npm run build
cd ../../Impulse-Nutrition
```

Si le repo TikTok MCP n'est pas dispo, le MCP tiktokshop ne se connectera pas. Les autres MCPs fonctionneront normalement.

**D. Session Instagram (premiere connexion)**

La premiere fois, Instagram necessite une authentification. Lance :

```bash
cd instagram_dm_mcp
uv run python create_session.py
```

Suivre les instructions (login + eventuel code 2FA). La session est sauvegardee dans `*_session.json` (gitignore). A refaire si la session expire (~30 jours).

## 4. Skills Claude Code

Les skills sont des protocoles de travail qui guident Claude sur chaque domaine. Ils vivent dans `~/.claude/skills/` (hors du repo). Tu dois les installer manuellement.

### Installation

Antoine doit te partager ses 3 dossiers de skills. Copie-les :

```bash
# Antoine te fournit les 3 dossiers (zip, airdrop, ou copie manuelle)
cp -r instagram-dm/ ~/.claude/skills/instagram-dm/
cp -r gorgias/ ~/.claude/skills/gorgias/
cp -r tiktok-sav/ ~/.claude/skills/tiktok-sav/
```

### Structure attendue apres install

```
~/.claude/skills/
  instagram-dm/
    SKILL.md
    reference/
      decision_tree.md
      format_carte.md
      red_flags.md
      welcome_codes.md
  gorgias/
    SKILL.md
    reference/
      categorization.md
      pull_protocol.md
      red_flags.md
      sav_recipe.md
      shopify_tags.md
  tiktok-sav/
    SKILL.md
```

### Verification

Lance Claude Code depuis le projet et tape `/instagram-dm` -- si le skill charge, c'est bon. Pareil pour `/gorgias` et `/tiktok-sav`.

## 5. Memory auto (optionnel mais recommande)

Antoine a un dossier `~/.claude/projects/-Users-antoinechabrat-Documents-SmallProject/memory/` avec des regles comportementales (draft+go explicite, no em dash, lire thread avant drafter, etc.). Ces regles sont chargees automatiquement a chaque session Claude Code dans le projet.

Si Antoine te partage ce dossier, copie-le dans TON equivalent :

```bash
# Le chemin depend de ton $HOME et de l'emplacement du projet
# Claude Code cree le dossier automatiquement quand tu ouvres le projet
# Copie juste les fichiers .md dedans
```

Sans la memory auto, les skills fonctionnent quand meme (les regles critiques sont aussi dans les SKILL.md), mais tu auras moins de garde-fous cross-domain.

## 6. Verification finale

| Test | Commande | Resultat attendu |
|---|---|---|
| MCPs connectes | Lance Claude Code, attends 30s | Les 7 MCPs apparaissent dans la liste des skills/tools |
| Instagram DM | Tape "check les DMs" | Le skill `/instagram-dm` se declenche, pull `list_chats` |
| Gorgias SAV | Tape "check le SAV" | Le skill `/gorgias` se declenche, pull 100 tickets |
| TikTok SAV | Tape "check tiktok sav" | Le skill `/tiktok-sav` se declenche, lit `pending.json` |
| Google Sheets | Tape "cherche alextv dans le Sheet" | `find_in_spreadsheet` retourne un resultat |
| Shopify | Tape "commande IMP6999" | `get_order` retourne les details |

## 7. En cas de probleme

| Symptome | Cause probable | Fix |
|---|---|---|
| MCP ne se connecte pas | `uv` ou `node` pas dans PATH | `which uv` / `which node` -- si vide, reinstaller et ajouter au PATH |
| "Session expired" sur Instagram | Session Instagram expiree | `cd instagram_dm_mcp && uv run python create_session.py` |
| `find_in_spreadsheet` echoue | Service account manquant | Verifier `~/.config/google-service-account.json` existe |
| TikTok MCP timeout | Repo TikTok MCP pas clone/build | Voir etape 3.C ci-dessus |
| `list_chats` retourne des messages anciens | MCP pas restart apres update mcp_server.py | Relancer Claude Code |
| Skill ne se declenche pas | Fichier SKILL.md pas au bon endroit | Verifier `ls ~/.claude/skills/{nom}/SKILL.md` |
