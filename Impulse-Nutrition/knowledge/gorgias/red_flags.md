# Red flags — Gorgias (liste exhaustive)

Chargé par `/gorgias` sur demande quand il y a un doute sur une formulation ou une action.

Les 5 red flags critiques sont dans le SKILL.md principal. Cette liste est la version complète pour référence.

## À ne JAMAIS faire

### Pull protocol
- ❌ **Conclure "client pas trouvé" sans avoir essayé `search_tickets(query=email|nom|id)` puis `list_tickets(status="all", limit=100)`** — la vue Inbox par défaut ne contient que les tickets ouverts non-spam non-snoozed
- ❌ **Oublier de spécifier `status="all"` ou `view_id=X`** quand on cherche dans l'historique (closed, snoozed)
- ❌ **Pull 100+ aveugle sans filtre** alors que `list_tickets(channel="email", status="open")` filtre côté serveur — gaspille tokens et temps

### Pre-draft
- ❌ **Drafter sans `list_ticket_messages`** complet du ticket — tu peux contredire une réponse de collègue SC antérieure
- ❌ **Drafter sans avoir identifié la commande** (`order_id` = `IMP####`) quand le ticket parle d'une commande
- ❌ **Conclure "pas d'ambassadeur" sans avoir fait le cross-check Sheet** quand le ticket mentionne "code affilié" / "Affiliatly" / "mes crédits"

### Persona et ton
- ❌ **Signer "Antoine"** / "Sportivement, Antoine" — sur Gorgias, persona = entité Impulse Nutrition
- ❌ **Signature humaine** ("moi personnellement", "mon expérience perso")
- ❌ **Tutoyer** un client final (exception ambassadeur connu, voir §Cas particulier du SKILL.md)
- ❌ **Utiliser des tirets em** (`—`) — règle cross-domain en memory auto
- ❌ **Répondre en anglais au helpdesk BigBlue** — leur SOP impose le français

### Contenu des drafts
- ❌ **Délais chiffrés précis** (`48-72h`, `sous 24h`, `dans la semaine`) — toujours `"dès que nous avons du nouveau"`, `"dans les plus brefs délais"`, `"sous peu"`
- ❌ **Formules creuses** : `"nous vous remercions de votre confiance"`, `"nous vous avons bien reçu"`, `"votre satisfaction est notre priorité"`, `"nous mettons tout en œuvre"`
- ❌ **Redondances** (`"nous vous confirmons que nous avons bien pris en compte votre demande"` → `"C'est bien noté"`)
- ❌ **Promettre un remboursement** avant validation (le refund Shopify est manuel, si la promesse ne passe pas tu perds ta crédibilité)
- ❌ **Promettre un replacement** avant d'avoir vérifié le stock et créé la draft
- ❌ **Mentionner la promo historique `shaker offert dès 59 €`** — obsolète depuis avril 2026
- ❌ **Mentionner une dotation mensuelle ambassadeur** sans validation Antoine (même si le client est ambassadeur)
- ❌ **Critiquer Chronopost / Mondial Relay / autre transporteur** au client — même si c'est leur faute, rester neutre ("la livraison a rencontré un incident")

### Draft orders Shopify
- ❌ **Passer `customer_email`** au lieu de `customer_id` numérique → crée un doublon customer blank
- ❌ **Utiliser `update_draft_order` sur `line_items`** → ne fonctionne pas, utiliser `delete` + `recreate`
- ❌ **Oublier le tag `Service client`** sur un replacement SAV → fausse le CA HCS
- ❌ **Mettre `Dotation influenceur`** sur un replacement SAV même si le client est ambassadeur — le SAV reste un SAV
- ❌ **Inventer un autre tag** (`SAV`, `Geste commercial`) — seuls `Service client` et `Dotation influenceur` sont reconnus par le calcul de CA
- ❌ **Oublier le pickup point BigBlue manuel** après `complete_draft_order` (sauf si ship home)

### BigBlue
- ❌ **Écrire au helpdesk BigBlue en anglais**
- ❌ **Créer un claim BigBlue sans avoir les photos** (pour produit cassé) — demander au client d'abord

### Emojis et formulation
- ❌ **Emojis autres que `😊`** côté SC (et uniquement si contexte positif)
- ❌ **Zéro emoji sur un ticket SAV classique** (colis cassé, remboursement, problème technique)
- ❌ **Vocabulaire informel** : "franchement", "trop bien", "au top", "super" — c'est du registre Instagram DM, pas Gorgias

### Actions automatiques / mutations
- ❌ **`reply_to_ticket` sans "go" explicite**
- ❌ **`create_draft_order` sans "go" explicite**
- ❌ **`create_support_ticket` BigBlue sans "go" explicite**
- ❌ **`update_order` / `cancel_order` sans "go" explicite**
- ❌ **`close_ticket` prématurément** (si on attend une réponse du client, laisser `open`/`pending`)
- ❌ **Répondre à un ticket `[SPAM POSSIBLE]`** (close silencieusement)

### Cas particuliers
- ❌ **Drafter un ticket ambassadeur en vouvoiement SC sans demander à Antoine d'abord** (cas particulier §SKILL.md)
- ❌ **Drafter un ticket avec émotion forte** (menace avocat, mise en demeure, avis négatif public) sans escalader à Antoine
- ❌ **Drafter un ticket `candidature`** avec un pitch ambassadeur → rediriger vers Instagram DM et close
