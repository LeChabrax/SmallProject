# Process : Check DMs Instagram + Onboarding Ambassadeur

## 1. Check DMs - Process complet

### Étape 1 : Récupérer les chats récents
```
list_chats(100)
```
**ATTENTION :** `list_chats` montre un `last_message` qui peut être OBSOLÈTE. Ne JAMAIS se fier au `last_message` de `list_chats` pour rédiger un draft.

### Étape 2 : Cross-ref avec le sheet
Pour chaque thread, chercher le username dans Suivi_Amb ET Suivi_Dot :
```
find_in_spreadsheet(query=username, sheet="Suivi_Amb")
find_in_spreadsheet(query=username, sheet="Suivi_Dot")
```

### Étape 3 : Lire les vrais messages AVANT tout draft
**RÈGLE ABSOLUE :** Pour chaque thread qui nécessite une action, TOUJOURS fetcher les messages récents :
```
list_messages(thread_id=..., limit=10)
```
Seulement APRÈS avoir lu les messages, décider si un draft est nécessaire.

**Erreurs passées :**
- briannicklen : `list_chats` montrait son inbound du 31/03, mais en réalité Antoine avait déjà répondu ET Brian avait accepté le 07/04. On a failli drafter un message pour un truc déjà réglé.
- shadowwtri et frerotrun1997 : déjà refusés avec code PGAU25, pas vu sans lire le thread.

### Étape 4 : Classifier et prioriser
Pour chaque thread, produire un brief structuré :
- **URGENT** : commande à préparer, réponse attendue depuis longtemps
- **À RÉPONDRE** : inbounds non traités (vérifiés via list_messages)
- **À NOTER** : reel mentions, activité positive
- **RAS** : Antoine est le dernier à avoir écrit, pas d'action

---

## 2. Onboarding nouvel ambassadeur (dotation)

### Séquence complète

#### Phase 1 : Discussion DM
1. Antoine propose le programme (80-100€ dotation, code affilié -15%, seuil renouvellement)
2. L'ambassadeur accepte
3. Antoine demande : sélection produits + adresse + mail + téléphone

#### Phase 2 : Préparation commande
1. **Chercher les produits sur Shopify** via `get-products(searchTitle=...)` pour obtenir les variant_id
2. **Créer le draft order** :
   - `line_items` avec les variant_id + quantités
   - `shipping_address` avec les infos du client
   - `customer_email` si disponible
   - `tags` = "Dotation influenceur"
   - `note` = contexte (username, programme, montant)
   - **Tag client** = "Influenceur/Athlète" (à ajouter sur le customer Shopify)
   - **Ne créer un nouveau client** que si on est sûr qu'il n'existe pas déjà (vérifier via search_customers avant)
3. **Appliquer la réduction** via `update_draft_order` :
   - `applied_discount` = `{"title": "Test produits", "value_type": "percentage", "value": "100.0", "description": "Test produits"}`
   - `shipping_line` = `{"title": "Expédition gratuite", "price": "0.00"}` (**IMPORTANT** : titre exact "Expédition gratuite", pas "Livraison offerte")
4. **Présenter le récap à Antoine** avant de valider
5. **Compléter la commande** via `complete_draft_order`

#### Phase 3 : Création code affilié
1. **Créer le code** via `create_discount_code` :
   - `title` = "[CODE] - Code affilié ambassadeur"
   - `code` = le code choisi (ex: BRIANN)
   - `value` = -15
   - `value_type` = "percentage"
   - Pas de `usage_limit` (illimité)
2. **Valider le nom du code avec Antoine** avant création

#### Phase 4 : Mise à jour Google Sheet
Ajouter dans **Suivi_Dot** (prochaine ligne disponible) :
- A = Nom complet
- C = "En cours"
- D = "Dot"
- E = Contexte/notes
- F = Mail
- G = Numéro
- H = Prénom
- I = Nom
- J = "No" (Affiliatly, à setup plus tard)
- M = username Instagram
- R = Code affilié
- Y = Date début
- AA = Durée (ex: "4 mois")
- AB = Dotation mensuelle (€)
- AC = Seuil renouvellement
- AF = Adresse

#### Phase 5 : DM final
Envoyer le code affilié + lien + infos communauté.

---

## 3. Règles de rédaction DM

### Ton
- Tutoiement systématique
- Signature : "Sportivement, Antoine"
- Emojis modérés (😉🔥💪)
- JAMAIS de tiret cadratin (-)

### Flow naturel
- **Premier message ou silence > 2 semaines** : "Hello [prénom], j'espère que tu vas bien !"
- **En pleine conversation** : "Top !", "Parfait !", "Nickel !"
- **JAMAIS relister les produits** que le client vient de donner
- **JAMAIS dire "te compter dans l'équipe"** avant le premier envoi de produits
- **Ne pas mentionner le montant** de la dotation si c'est récurrent et inchangé
- **Un DM = une seule info ou demande**, pas de pavé qui mélange tout

### Infos utiles pour les DM code affilié
- Code : -15% sur la 1ère commande
- ~~Shaker 450ml offert dès 59€~~ (plus d'actualité depuis avril 2026)
- Livraison à domicile offerte dès 69€
- Lien : https://impulse-nutrition.fr/discount/[CODE]

### Validation
**TOUJOURS** montrer un draft et attendre "go" explicite avant d'envoyer.
Même si Antoine dit "dis lui que..." = rédiger un draft, PAS envoyer directement.

---

## 4. Process commande dotation mensuelle (ambassadeur existant)

Pour un ambassadeur déjà en place qui demande sa commande mensuelle :
1. Vérifier s'il a un **code dotation** (colonne K de Suivi_Dot, ex: MARTINDOTATION)
2. Si oui : lui communiquer le code pour qu'il commande lui-même
3. Si non : demander sa sélection produits et préparer la commande manuellement

---

## 5. Checklist Shopify - Points de vigilance

- [ ] **Tag** = "Dotation influenceur"
- [ ] **Réduction** = 100%, titre "Test produits", description "Test produits"
- [ ] **Livraison** = "Livraison offerte", prix 0.00
- [ ] **Adresse** complète avec country_code "FR"
- [ ] **Note** avec username Instagram + contexte
- [ ] **Vérifier les variant_id** via `get-products(searchTitle=...)` avant de créer le draft (les IDs peuvent changer)
