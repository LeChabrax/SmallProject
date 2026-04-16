# Impulse Nutrition — Operations

> **Ce doc = comment faire**. Ce que tu ouvres quand tu traites un ticket SAV, draftes un DM, crées un code ou un draft order.
> Pour le **qui/quoi** (identité, programme, catalogue, glossaire) → [`impulse.md`](./impulse.md).
> Source machine-readable des templates DM : [`voice/templates.yaml`](./voice/templates.yaml).

## Sommaire

1. [SAV & opérations client](#sav--opérations-client)
2. [Voice & persona split](#voice--persona-split)
3. [Runbooks opérationnels](#runbooks-opérationnels)
4. [Quirks techniques transverses](#quirks-techniques-transverses)

---

## SAV & opérations client

### Canaux convergents

**Tous les SAV remontent dans Gorgias**, peu importe le canal :

| Canal | Mécanisme | Tag Gorgias |
|---|---|---|
| Email | natif Gorgias | selon contenu |
| Chat site | natif Gorgias | selon contenu |
| Contact form site | natif Gorgias | selon contenu |
| **WhatsApp via WAX** | outil tiers qui pousse dans Gorgias | `WAX` |
| Instagram (mention/DM cliente) | natif Gorgias | selon contenu |
| Facebook | natif Gorgias | selon contenu |
| BigBlue internal-note | alertes stock/livraison | selon contenu |
| TikTok Shop | pipeline custom (`tiktok_sav/sav.py`) | — |

WAX pousse auto la réponse Gorgias sur WhatsApp. Tone SC vouvoiement formel identique.

### Pull protocol strict (leçon 2026-04-13)

Un pull de 30 tickets a loupé `Amandine Laurent` (#52032892). Depuis :

1. **`list_tickets(limit=100, order_by="updated_datetime:desc")` minimum.** Jamais moins.
2. **Filtrer localement** :
   - Keep : channels `email`, `chat`, `contact_form`, `instagram`, `facebook`, `internal-note`
   - Prioriser tags : `urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`
   - Ignorer : subjects `[SPAM POSSIBLE]`, `Réponse automatique`, `Automatic reply`, `closed` bounces
3. Si rien ne flag → **deuxième pass** avec `order_by="created_datetime:desc"`
4. **Ne jamais conclure "not found" sur une liste courte.** Étendre le pull d'abord.
5. `search_tickets` (custom MCP) n'est pas full-text search — pull protocol = filet de sécurité.

### Recette draft SAV canonique

**Defaults OBLIGATOIRES pour TOUTE commande gratuite** (SAV ou dotation, total 0€) :

```json
{
  "applied_discount": {
    "title": "SAV",
    "value_type": "percentage",
    "value": "100.0",
    "description": "SAV"
  },
  "shipping_line": {
    "title": "Expédition gratuite",
    "price": "0.00"
  },
  "tags": "Service client",
  "note": "<contexte court : ref originale + raison + geste>"
}
```

Le `applied_discount.title` change selon contexte (`SAV`, `Dotation`, `Crédit ambassadeur`). Le `tags` est ce qui compte pour la compta.

### Règle d'or des tags Shopify

**Il existe exactement 2 tags qui sortent une commande du calcul du CA HCS :**

| Tag | Coût HCS | Utilisé pour |
|---|---|---|
| `Service client` | Coût SAV | Replacements, gestes commerciaux, codes `[PRENOM]-SAV` |
| `Dotation influenceur` | Coût marketing | Envois mensuels ambassadeurs, codes dotation, codes crédit `[PRENOM]-CREDIT` |

Toute autre commande = **vraie vente dans le CA**. **Mal tagger une commande fausse les rapports financiers HCS.** Non négociable.

Mapping par scénario :

| Scénario | Tag |
|---|---|
| Replacement colis bloqué / perdu | `Service client` |
| Replacement returned-to-sender | `Service client` |
| Geste commercial post-bad-rating | `Service client` |
| Commande client utilisant code `[PRENOM]-SAV` | `Service client` |
| Envoi dotation mensuelle (Suivi_Dot / Suivi_Paid) | `Dotation influenceur` |
| Commande utilisant code crédit `[PRENOM]-CREDIT` | `Dotation influenceur` |
| Vente normale e-commerce | (aucun tag de cette liste) |

### Scénarios SAV typiques

**Colis bloqué / perdu en transit** (Chronopost loop, Mondial Relay misrouted)

1. `get_order(order_id)` Shopify → line items + shipping address
2. `get_tracking(bigblue_order_id)` pour confirmer
3. **Créer replacement draft** avec line items originaux + geste commercial (bidon, shaker, ou 1 produit même range)
4. Ship to **home address** — pas de pickup point sur le retry
5. Apply defaults SAV (100% discount + shipping 0 + tag `Service client`)
6. `complete_draft_order` → Shopify crée la commande → BigBlue la prend
7. **Régler manuellement le pickup point sur BigBlue UI** (quirk connu)
8. Répondre Gorgias : confirmer reshipment + geste. Ne pas exposer les détails du tracking loop

Cas réf : Alexandre Damary, IMP4938 → draft IMP6923.

**Returned to sender** (refusé par pickup point, 2× consécutifs)

Proposer :
- Refund (simple)
- OU reship to home + geste commercial

Attendre la réponse du client avant trigger.

Cas réf : Jean-Baptiste Morand, IMP6586.

**Partial refund**

Client retourne partie de la commande. BigBlue `RETURNED`, Shopify `partially_refunded`.

1. `get_order` → check `refunds` array
2. Si refund déjà traité (transaction `refund`, status `success`) → confirmer au client (montant + PayPal/Stripe auth id + délai 3-5 j ouvrés)
3. Si pas encore traité → trigger via Shopify admin UI (MCP refund non implémenté)

Cas réf : Amandine Laurent, IMP6036, refund 50,18€ sur ligne `36592237936971`.

**Bad rating BigBlue (1-2 étoiles)** — tagged `bigblue-bad-rating-*`

- Lire le commentaire (si présent) via `get_support_ticket`
- Apology + demander ce qui a mal tourné. Offrir code discount si issue côté service
- Répondre sur le ticket Gorgias (pas BigBlue), fermer quand répondu

**Cas particulier ambassadeur qui fait un SAV**

Si la personne qui contacte le SAV est un ambassadeur (Suivi_Amb / Suivi_Dot / Suivi_Paid) :
- Antoine répond probablement directement (pas via Gorgias / pas signé "Le service client") — il connaît la personne
- Vérifier le statut Suivi avant réponse pour adapter le ton
- Le tag de la commande de remplacement reste **`Service client`** (c'est un SAV, pas une dotation)

### Style emails Gorgias

- **Pas de formules pompeuses** : éviter "Nous avons bien pris note", "Nous vous remercions de nous avoir contacté", "N'hésitez pas à revenir vers nous"
- **Phrases courtes**, directes, factuelles
- **Jamais promettre un délai chiffré** (livraison J+1, traitement 48h…) — partenaires logistiques variables
- **Jamais signer "Antoine"** côté SC — `Le service client` ou `L'équipe Impulse Nutrition`
- **Vouvoiement strict**
- **Pas d'emoji** sur canal SC

### Excuses retard réponse

- **> 4 jours** : excuse légère ("Excuse-moi pour le temps de réponse !")
- **> 10 jours** : excuse appuyée ("Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !")

---

## Voice & persona split

**RÈGLE STRICTE — DEUX PERSONAS ISOLÉS. JAMAIS MÉLANGER.**

| Canal | Persona | Tutoiement | Signature | Exemple |
|---|---|---|---|---|
| **Instagram DM** (ambassadeurs) | **Antoine** (humain) | TU | `Sportivement, Antoine` OU `Antoine` (≥3 phrases) / rien (micro-messages) | "Hello Florine, je suis Antoine d'Impulse Nutrition…" |
| **Gorgias / WAX / email SC** (clients finaux) | **Impulse Nutrition** (entité) | VOUS formel | `Le service client` / `L'équipe Impulse Nutrition` | "Bonjour, votre commande IMP6923…" |

Si Antoine croise un ambassadeur qui contacte SC → **bulle SC** (vouvoiement) jusqu'à résolution, puis revenir au tutoiement.

### Tone rules Instagram DM

- **Tutoiement systématique**. Si l'autre vouvoie → switcher vite au `tu`
- **Double exclamation** sur micro-messages ("Merci !!" pas "Merci !")
- **Pas de point final** sur micro-messages
- **Emojis modérés** : 0 à 2 par message max. Favoris : 😉 🔥 😄 😊 😍 ☺️ 💪. **Éviter** 🙏 ✨ 💖 (mielleux)
- **Pas de tirets em (`—`)**. Phrases courtes.
- **Pas de "Bonjour"** dans une conversation déjà ouverte. Réserver au premier contact
- **Pas de jargon** : ROI, KPI, conversion, collab (préférer "partenariat"), reach
- **Ne JAMAIS critiquer la concurrence**
- **Proposer un call** dès que la conversation se complexifie
- **"My bad"** + correction immédiate si on se trompe
- **Ne JAMAIS mentionner de dotation mensuelle** sans validation d'Antoine — le parcours standard est : produits gratuits → code affilié → 20€ crédit/commande
- **Ne jamais re-lister les produits** dans une conversation déjà avancée

### Templates DM principaux

> La source machine-readable (chargée par le skill `/instagram-dm`) est **[`voice/templates.yaml`](./voice/templates.yaml)** (20 templates, 3 modes : verbatim, pick_from_list, semi_structured). Les extraits ci-dessous sont la version humaine lisible.

**Premier message ambassadeur**

> Hello {prenom},
>
> Je suis Antoine d'Impulse Nutrition, une marque de nutrition sportive
> premium qui développe des produits fabriqués en France de très grande
> qualité, pensés par et pour les besoins réels des sportifs.
>
> Nous lançons un programme ambassadeur et recherchons des athlètes qui
> souhaitent tester nos produits. Ton profil nous a semblé particulièrement
> cohérent, tant pour ton approche du sport que pour la qualité de ton
> contenu ainsi que crédibilité et l'engagement que tu dégages.
>
> Je voulais donc savoir si ça t'intéresserait de recevoir des produits à
> tester, et, s'ils te plaisent, de faire partie de notre programme
> ambassadeur ? Je peux te donner plus de détails si tu veux !
>
> Sportivement,
> Antoine

**Variante courte (impressionné par le profil)**

> On est très impressionnés par ton parcours ! C'est très inspirant et tu
> partages vraiment les valeurs du sport et du dépassement de soi, donc
> déjà bravo !!
>
> Travailler avec toi sera un plaisir ! Ce que je te propose :
>
> Dans un premier temps, on t'envoie pour 80 € de produits, tu choisis ce
> que tu préfères ou on te fait un pack, c'est comme tu préfères, dans
> tous les cas c'est gratuit pour toi !
>
> Dans un deuxième temps, si les produits te plaisent, on te crée un code
> affiliation que tu pourras partager en story avec ta review des produits.
>
> Et dans un troisième temps, si ton code affiliation fonctionne bien, on
> te passera dans le programme ambassadeur et à chaque fois qu'une commande
> sera passée avec ton code, tu recevras 20 € de crédit à utiliser sur
> notre site, comme ça tu pourras avoir autant de compléments que
> nécessaire pour ta pratique !
>
> Je le redis, encore bravo, ton profil est vraiment impressionnant !
>
> N'hésite pas si tu as des questions,
> Antoine

**Refus poli neutre (sponsor non identifié)**

> On comprend tout à fait, merci d'avoir pris le temps de nous répondre !
> On te souhaite une très belle continuation dans tes projets avec ta
> marque actuelle. Une future collaboration serait avec grand plaisir,
> n'hésite surtout pas à revenir vers nous si l'occasion se présente !
>
> Sportivement,
> Antoine

**Refus communauté trop petite — code welcome**

> Merci pour ton message {prenom} et pour le partage de ton projet, {accroche projet} 🔥
>
> Pour être transparent avec toi, on travaille avec des profils qui ont
> une communauté déjà bien établie sur les réseaux, et pour l'instant ton
> compte ne correspond pas encore aux critères qu'on recherche pour nos
> partenariats. Ce n'est absolument pas un jugement sur la qualité de ton
> contenu ou de ton projet, mais c'est notre critère actuel.
>
> Ce qu'on peut faire en revanche : je te laisse un code perso {CODE25}
> pour que tu puisses découvrir nos produits avec -25% sur ta commande.
> Et si dans le futur ta communauté se développe, n'hésite pas à revenir
> vers nous, ce sera avec plaisir !
>
> Sportivement,
> Antoine

**Acceptation — demande infos commande (4 infos en 1 message)**

> Trop bien, on est ravi ! 😄
>
> Pour tester les produits, est-ce que tu préfères sélectionner toi-même
> les produits qui t'intéressent sur notre site ou qu'on te concocte un
> pack personnalisé ? Dans les deux cas c'est gratuit pour toi ! Il me
> faudra également une adresse (avec nom + prénom), un email et un
> numéro, je te prépare la commande en suivant !
>
> Sportivement,
> Antoine

**Commande validée + envoi du code affilié (CRITIQUE)**

> La commande est validée et sera expédiée très prochainement !
>
> Je t'ai créé un code affilié perso ({CODE}) qui permettra à ta
> communauté de bénéficier de -15% sur tout le site (sans minimum
> d'achat). **Le code est cumulable avec toutes les autres réductions
> sur les produits.**
>
> Si les produits te plaisent et que tu en parles autour de toi, tu
> cumuleras 20€ de crédit à chaque commande passée avec ton code,
> utilisables pour renouveler tes stocks quand tu veux.
>
> Code : {CODE}
> Lien : https://impulse-nutrition.fr/discount/{CODE}
>
> N'hésite pas si tu as des questions, à très vite !
>
> Sportivement,
> Antoine

**Envoi commande (court, pas de signature)**

> Hâte d'avoir tes retours et bonne dégustation !!

**Demande redeem crédits**

> Avec plaisir {prenom} ! Tu as actuellement **{credit_value} €** de
> crédit disponible (soit {solde} utilisations × 20€). Tu veux que je
> te crée le code maintenant ? Tu pourras le passer en une seule
> commande sur le site.
>
> Sportivement,
> Antoine

### Catalogue micro-messages

**Validation / Enthousiasme** : "Trop bien, on est ravi !!" · "Au top !!" · "Super !!" · "Yes au top !" · "C'est noté je te dis comment je procède !"

**Remerciement** : "Avec plaisir !!" · "Merci à toi !!" · "Merci beaucoup !!"

**Réaction contenu** : "Trop bien merci !! 🔥" · "Au top, merci beaucoup !! 😍" · "Trop cool merci à toi !! 🔥🔥" · "Bravo c'est énorme !! 🔥"

**Accusé de réception** : "Bien reçu merci !" · "C'est bien noté !" · "Aucun soucis c'est bien noté !" · "Entendu ! 😉"

**Rassurance** : "Aucun souci !" · "Prends ton temps !" · "All good"

**Post-commande** : "Hâte d'avoir tes retours et bonne dégustation !!" · "Let's go c'est bon c'est modifié !"

**Clôture** : "Très bonne soirée !!" · "Très bon weekend !!" · "À très vite !"

### FAQ — réponses types

**"Comment utiliser mon crédit ?"**
> Tu m'envoies un message avec ce que tu veux commander, et je te fais un code du montant correspondant. Sinon on peut prévoir un call si tu préfères !

**"Combien de personnes ont utilisé mon code ?"**
> [N] utilisation(s) de ton code, bien joué !!

**"Mon code/lien ne marche pas"**
> Je check ça tout de suite ! [vérifier et corriger, puis] C'est réglé, tu peux réessayer !

**"Je peux dépasser un peu le budget de 80€ ?"**
> Le budget c'est 80€ mais ça peut dépasser un petit peu, pas de souci !

**"Le preworkout m'a donné des effets secondaires"**
> C'est normal si c'est ta première prise ! Essaie avec 1/3 ou 1/2 scoop pour commencer, et augmente progressivement. N'hésite pas à me dire comment ça se passe !

**"Je suis libre sur le contenu ?"**
> Oui totalement ! Le format est libre, c'est toi qui gères selon ce qui colle le mieux à ta façon de communiquer. L'essentiel c'est de glisser ton code et ton lien pour que tes abonnés puissent en profiter !

**"C'est un partenariat ponctuel ou long terme ?"**
> L'idée c'est vraiment de bosser sur le long terme ! On commence par un envoi de produits, si les produits te plaisent on te crée un code affilié, et à chaque commande passée avec ton code tu reçois 20€ de crédit chez nous. Et si la collab fonctionne vraiment bien, on peut envisager d'aller plus loin ensemble.

**"Quelle différence entre Whey Isolate et Whey Recovery ?"**
> La Whey Recovery c'est une formule 3-en-1 : whey concentrate + créatine + collagène, pensée pour une récupération complète (musculaire, articulaire et performance). La Whey Isolate c'est de la protéine pure et plus concentrée, idéale si tu veux juste l'apport protéique. Les deux contiennent de la lactase donc pas de souci de digestion !

**"Vos produits contiennent du lactose ?"**
> Nos whey contiennent de la lactase, une enzyme qui aide à digérer le lactose, donc pas de souci de digestion !

### Red flags DM (à NE JAMAIS faire)

- ❌ **Drafter sans avoir scanné l'historique complet du thread** (50 msgs min)
- ❌ **Pitcher le programme ambassadeur à un prospect parqué** (code `ACHAB25`/`PGAU25`/`{NOM}25` déjà donné)
- ❌ **Contredire une position d'Impulse précédemment établie** sans acknowledger le changement
- ❌ **Ignorer une rencontre IRL** mentionnée dans le thread
- ❌ **Vouvoyer**
- ❌ **Signer "Antoine"** sur un canal SC
- ❌ **Utiliser des tirets em (`—`)**
- ❌ **Re-coller le pitch ambassadeur** dans une conversation déjà avancée
- ❌ **Promettre** des choses non confirmées (livraison J+1, gratuit illimité)
- ❌ **Oublier `{prenom}`** dans un premier message
- ❌ **Emojis mielleux** : 🙏 ✨ 💖
- ❌ **Surcharger** en 🔥 ou 💪 (max 1 par message)

### Draft + go explicite

**Claude rédige, Antoine valide TOUJOURS avant envoi.** "C'est good" / "bon raisonnement" ne sont **PAS** des validations d'envoi. Seul "envoie" / "go" / "c'est bon envoie" valide.

Un go global ("go un par un", "on y va") ≠ validation du draft courant. Chaque draft = son propre go ciblé.

### Routing par type de message reçu

| Message reçu | Statut (J) | Draft à rédiger |
|---|---|---|
| Réponse positive au pitch | In-cold → In-hot | Second message explication programme |
| Questions sur le programme | In-hot | Réponse + proposition call |
| Envoi coordonnées | In-hot | "C'est noté je te dis comment je procède !" |
| Choix produits / panier | In-hot | Validation : "C'est bien noté !" / "Super choix !" |
| "Déjà pris par une autre marque" | In-cold → Out | Adapter selon sponsor |
| "Je ne prends pas de compléments" | In-cold | Argument doux + proposition call |
| "Voir avec mon manager" | → Contacter manager | "Bien sûr !" + noter contact |
| Confirmation réception colis | Produits envoyés | "Hâte d'avoir tes retours !!" |
| Feedback positif | Produits envoyés | Enthousiasme court |
| Feedback négatif | Produits envoyés | Empathie + alternative/call |
| Story mentionnant Impulse | Produits envoyés | Réaction courte |
| Story sans code visible | Produits envoyés | Nudge code doux |
| "Merci" (promo/info) | Tout | Micro : "Avec plaisir !!" |
| Demande réassort | Produits envoyés | "Tu veux me mettre ce que tu as besoin par message ? Sinon on s'appelle 😉" |
| Question stats code | Produits envoyés | Chiffre exact : "[N] utilisations, bien joué !!" |
| Problème technique code | Produits envoyés | "Je check ça !" + résolution |
| Demande redeem crédit | Produits envoyés | Voir "Calculer et redeem le crédit" |
| Résultat sportif | Tout | "Bravo c'est énorme !! 🔥" |
| Excuse retard | Tout | "Aucun souci !" / "Prends ton temps" |
| Message vocal (`voice_media`) | Tout | ⚠️ NE PAS DRAFTER — signaler Antoine, L=high |
| Media éphémère (`raven_media`) | Tout | ⚠️ NE PAS DRAFTER — signaler Antoine, L=medium |

### Auto-skip si notre côté a répondu en dernier

Si le dernier message du thread est `is_sent_by_viewer=true` (Antoine/Pierre/SC a répondu en dernier), **auto-skip** avec carte condensée 1 ligne. Pas de draft.

### Relance d'un prospect parqué

Trame contextualisée (JAMAIS un pitch d'entrée) :

> Salut {prenom}, merci de revenir vers nous !
>
> {Acknowledgment explicite du nouveau contexte : "tu as bien grandi depuis notre dernier échange", "c'était sympa d'échanger avec toi sur le stand du salon Run Expérience", "ta prépa pour l'Ultra Marin approche", etc.}
>
> {Si le contexte le justifie vraiment} Ça fait tout à fait sens qu'on reprenne cette discussion maintenant. {Proposition adaptée — peut être le programme ambassadeur si le profil qualifie désormais, ou une autre piste (call, rencontre, offre ponctuelle)}.
>
> {Si pas sûr} Je regarde ça de près et je reviens vers toi très vite pour te proposer quelque chose qui ait du sens.
>
> Sportivement,
> Antoine

Cas-types :

| Situation | Réaction |
|---|---|
| Parqué à <1k qui revient à 10k+ avec stats concrètes | Drafter offre programme ambassadeur **en reconnaissant l'échange précédent** |
| Parqué rencontré IRL (stand, salon) | Réponse chaleureuse qui capitalise sur la rencontre, proposer un call ou une offre adaptée |
| Parqué qui relance sans nouvel élément | Réponse courte, réexpliquer poliment la position, garder la porte ouverte |
| Parqué qui n'a pas grandi mais est très actif | Rester sur la position "parqué", acknowledgment + encouragements |

---

## Runbooks opérationnels

### Créer un code affilié ambassadeur

**Utiliser le tool MCP** `create_affiliate_code(name="florine")` → clone exact ALEXTV :
- `-15%` percentage
- `once_per_customer=true`
- `starts=now`, `ends=null`
- `usage_limit=null`
- `combinesWith { order:false, product:true, shipping:true }`

Pour Paid (-20% type LRA20) : `create_paid_affiliate_code(name="...")`.

**Convention nommage** : `<PRENOM>` ou `<HANDLE>` en majuscules, sans accents ni caractères spéciaux. Ex : `FLORINE`, `ALEXTV`, `DODO`, `JBTRI`, `LRA20`.

**Codes réels en prod (audit 2026-04-13)** :

| Code | price_rule_id | value_type | value | usage_limit | starts_at | type |
|---|---|---|---|---|---|---|
| `ALEXTV` | 2205486154059 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `DODO` | 2199297753419 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `LRA20` | 2205436543307 | percentage | -20.0 | null | 2025-09-09 | Affilié Paid |
| `TRAILEURSDOTATION` | 2206068539723 | fixed_amount | -200.0 | 6 | 2026-01-15 → 2027-01-31 | Dotation |

### Créer un draft order (SAV ou dotation)

**Hard rule : email client OBLIGATOIRE.** Sans email → Shopify confirmation + BigBlue tracking + Affiliatly mapping cassent.

Checklist avant `create_draft_order` :
1. Récupérer l'email (DM Instagram, Gorgias, thread)
2. `search_customers(query=email)` :
   - Existe → passer `customer_id=<integer>` (JAMAIS `customer_email=`)
   - N'existe pas → créer le customer d'abord via `mcp__shopify__create-customer` (firstName, lastName, email, adresse), puis `customer_id`
3. Après création, vérifier `get_draft_order(draft_id)` → `draft_order.email ≠ null`

**Fallback** si draft créé sans email (blank customer auto) :
```python
mcp__shopify__update_customer(id=<blank_id>, email="<vrai>", firstName="...", lastName="...")
```

**Recette canonique SAV** :
```python
draft = create_draft_order(
    line_items=[{"variant_id": ..., "quantity": ...}, ...],
    customer_id=<id>,
    note="Replacement IMPxxxx — motif",
    tags="Service client",
)
update_draft_order(
    draft_order_id=draft["id"],
    applied_discount={"title":"SAV","value_type":"percentage","value":"100.0","description":"SAV"},
    shipping_line={"title":"Expédition gratuite","price":"0.00"},
)
complete_draft_order(draft_order_id=draft["id"], payment_pending=False)
# → Puis fix manuel BigBlue pickup point
```

**Checklist avant `complete_draft_order`** :
- [ ] `tags` = `Service client` OU `Dotation influenceur` (jamais les 2, jamais aucun sur commande gratuite)
- [ ] `applied_discount` 100% si gratuit
- [ ] `shipping_line` "Expédition gratuite" 0.00 si gratuit
- [ ] `note` interne explicite (ref + motif)
- [ ] `line_items` complets (pas d'`update_draft_order` pour ajouter après)
- [ ] Adresse correcte (domicile pour SAV retry)

### Calculer et redeem le crédit ambassadeur

**Formule** : `solde = col O (nb_utilisation) − col Q (nb_credit_used)` · `credit_value = solde × 20€`

**Garde-fou** : si `Q > O` → incohérence. Stopper, vérifier le Sheet manuellement, **ne PAS créer de code**.

**Workflow** :

```python
from infra.common.google_sheets import SUIVI_AMB_COLS, get_worksheet, DATA_START_ROW

ws = get_worksheet("Suivi_Amb")
rows = ws.get_all_values()[DATA_START_ROW - 1:]

def find_ambassador(username):
    for i, row in enumerate(rows, start=DATA_START_ROW):
        if len(row) > SUIVI_AMB_COLS["username"] and \
           row[SUIVI_AMB_COLS["username"]].strip().lower() == username.lower():
            return i, row
    return None, None

row_idx, row = find_ambassador("florinebreysse")
nb_total = int(row[SUIVI_AMB_COLS["nb_utilisation"]] or 0)
nb_used = int(row[SUIVI_AMB_COLS["nb_credit_used"]] or 0)
prenom = row[SUIVI_AMB_COLS["prenom"]] or "X"

solde = nb_total - nb_used
if solde <= 0:
    raise SystemExit(f"solde invalide : {solde}")
credit_value = solde * 20
```

**Pattern Shopify du code crédit** (convention `[PRENOM]-CREDIT`) :

```json
{
  "price_rule": {
    "title": "FLORINE-CREDIT",
    "value_type": "fixed_amount",
    "value": "-140.0",
    "customer_selection": "all",
    "target_type": "line_item",
    "target_selection": "all",
    "allocation_method": "across",
    "starts_at": "<now>",
    "ends_at": null,
    "usage_limit": 1,
    "once_per_customer": true
  }
}
```

`combinesWith` GraphQL : `productDiscounts:true, shippingDiscounts:true, orderDiscounts:false`.

**Mise à jour Sheet** :
- Avant commande : col P (`code_credit`) ← `FLORINE-CREDIT`
- Après commande : col Q (`nb_credit_used`) ← `Q + solde` (nouveau Q = O)

**Tag de la commande générée** : `Dotation influenceur`.

**Audit mensuel** : pour tout ambassadeur avec `solde > 5` (≥100€) qui n'a pas redeem depuis ≥3 mois → DM proposant le redeem.

### Pattern code dotation `[NOM]DOTATION`

Utilisé par l'ambassadeur lui-même pour redeem sa dotation mensuelle (≠ code affilié utilisé par ses followers).

```
title: TRAILEURSDOTATION
value_type: fixed_amount
value: -200.0           ← montant mensuel
customer_selection: all
target_type: line_item
target_selection: all
allocation_method: across
usage_limit: 6          ← nombre de mois (1 redemption/mois)
once_per_customer: false
starts_at: <début contrat>
ends_at: <fin contrat>
```

Règle pour un contrat D mois × M €/mois :
- `value = -M.0`
- `usage_limit = D`
- `starts_at` = début contrat, `ends_at` = fin

⚠️ Ne pas confondre avec les utilisations cibles du code **affilié** (mesuré dans col O de Suivi_Amb).

`combinesWith.orderDiscounts: false`.

### Pattern code SAV `[PRENOM]-SAV`

Geste commercial SAV — code qui offre produit gratuit sur panier client :

- `value_type: percentage`, `value: -100.0`
- `entitled_product_ids: [shaker, bidon]` (restreint aux produits gratuits)
- `usage_limit: 1`, `once_per_customer: true`
- `combinesWith.orderDiscounts: true, productDiscounts: true, shippingDiscounts: true`

Le client place sa commande avec ce code → tagguer la commande **`Service client`**.

### DM check + onboarding condensé

**Check DMs** :
1. `list_chats(100)` — ⚠️ le `last_message` peut être obsolète, **ne jamais s'y fier pour drafter**
2. Cross-ref avec Suivi_Amb + Suivi_Dot + Suivi_Paid
3. `list_messages(thread_id=..., limit=10)` pour chaque thread actionnable — **règle absolue avant tout draft**
4. Classifier : URGENT / À RÉPONDRE / À NOTER / RAS (auto-skip si notre côté dernier à écrire)

**Pre-draft check bloquant** (avant tout draft DM, §0.5 du decision tree) :

- **Check 1 — Thread history** : `list_messages(thread_id, amount=50)` minimum. Scanner pour :
  - Codes welcome déjà donnés (`ACHAB25`, `PGAU25`, `-25%`, `{NOM}25`)
  - Échanges Impulse antérieurs (`is_sent_by_viewer=true` autre que l'action courante)
  - Positions Impulse précédentes (refus, acceptation, conditions)
  - Rencontres IRL (`stand`, `salon`, `Run Expérience`, `marathon de Paris`)
- **Check 2 — Sheet check** : `find_in_spreadsheet(query=username)` sur les 3 tabs.

**Règle d'or** : le thread Instagram est la source de vérité primaire. Le Sheet est secondaire.

**Onboarding nouveau ambassadeur (dotation)** :
1. Phase DM : proposer (80-100€ dotation + code affilié -15% + seuil renouvellement) → accepte → demander les 4 infos en 1 message
2. Phase commande : `get-products(searchTitle=...)` pour variant_id → `create_draft_order` avec tag `Dotation influenceur` + discount 100% + shipping 0€ → présenter récap à Antoine → `complete_draft_order`
3. Phase code : `create_affiliate_code(name="prenom")` (clone ALEXTV)
4. Phase Sheet : ajouter ligne Suivi_Dot (Name, Statut, Type, Mail, Numéro, Prénom, Nom, Insta, Code, Date début, Durée, Dotation €, Seuil renouvellement, Adresse)
5. Phase DM final : envoyer code + lien + infos

---

## Quirks techniques transverses

### Bug Excel "sériel" dans colonnes date du Sheet

Si une colonne est formatée "date" et qu'on y entre un nombre (ex : dotation `150`), Google Sheets l'affiche comme `29/05/1900` (serial 150). **Fix** : réécrire la valeur numérique correcte via `batch_update_cells`.

### Limitation `update_draft_order` Shopify

Ne permet **pas** de modifier les `line_items` d'un draft. Si on doit ajouter/retirer un produit après création (ex : bidon en geste commercial) :

1. `delete_draft_order(draft_id)`
2. `create_draft_order(<full set of line_items>)`
3. Réappliquer `applied_discount`, `shipping_line`, `tags`, `note`

→ Toujours préparer la liste line_items complète AVANT le premier appel.

### Pickup point BigBlue non reporté

Après `complete_draft_order`, BigBlue ne reçoit pas systématiquement l'info du pickup point. **Fix** : aller sur l'UI BigBlue, trouver la commande, régler manuellement le pickup point.

Pas de fix automatique côté MCP.

### Refunds non implémentés côté MCP

Les remboursements (partiels ou totaux) passent par l'UI Shopify ou directement via API REST `/orders/{id}/refunds.json`. Le MCP `shopify_orders` n'expose pas d'outil refund.

### Service account Google Drive

- Path : `~/.config/google-service-account.json`
- A read+write sur le folder `InfluenceContract` (ID `1dxT2gSAm6tcnd8Ck6hXxPDS5yieMuj4x`)
- Utilisé par `infra/common/google_sheets.py` (Sheets) et `infra/common/google_drive.py` (Drive contracts)

### Timestamps Instagram en microsecondes

Pour les scripts CLI `instagram_dm_mcp/*.py` :

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
date_str = dt.strftime("%d/%m/%Y")
```

### Helpdesk BigBlue fragile

4 tools du MCP BigBlue (list/get/create/reply support tickets) sont fragiles — reverse-engineering du gRPC-Web de l'admin UI. Messages **obligatoirement en français** (leur SOP). Fallback Playwright si API cassée.

### Search Gorgias retourne 405

Le native `/api/search` n'existe pas. `search_tickets` (MCP custom) = email lookup + substring fallback. Le pull protocol 100+ est le filet de sécurité.

### Col O / Q incohérentes (Q > O)

Crédit invalide. Stopper, vérifier manuellement, **ne PAS créer de code**.

### Rate limiting Instagram

Dans `infra.common.instagram_client.sleep_random(min, max)` :
- Reads inter-thread : `sleep_random(3, 8)`
- Cooldown tous les 10 reads : `sleep_random(15, 30)`
- Sends : `sleep_random(5, 10)`

### Draft order email obligatoire

Sans email client, Shopify confirmation + BigBlue tracking + Affiliatly mapping cassent. Voir "Créer un draft order" plus haut.

### `list_chats` last_message obsolète

`list_chats` (MCP Instagram) montre un `last_message` qui peut être périmé. **Ne JAMAIS se fier** au `last_message` pour drafter. Toujours `list_messages(thread_id, limit≥10)` avant draft.

### Sessions Instagram

- Sessions stockées dans `instagram_dm_mcp/*_session.json` (gitignored)
- Si expirée → `python instagram_dm_mcp/create_session.py`
- 2 comptes :
  - `impulse_nutrition_fr` — principal (DMs ambassadeurs, campaigns)
  - `antman.lass` — veille (lecture concurrents, dormant)
- Helper unique : `infra.common.instagram_client.get_ig_client(account="impulse"|"veille")`

### Nommage codes Shopify

Majuscules sans accents ni caractères spéciaux (sauf `-` pour SAV/CREDIT).

| Type | Format | Exemple |
|---|---|---|
| Affilié ambassadeur | `<PRENOM>` ou `<HANDLE>` | `FLORINE`, `ALEXTV`, `DODO`, `JBTRI` |
| Affilié Paid | variable | `LRA20` |
| Dotation | `<HANDLE>DOTATION` | `TRAILEURSDOTATION` |
| Crédit ambassadeur | `<PRENOM>-CREDIT` | `FLORINE-CREDIT` |
| SAV client | `<PRENOM>-SAV` | `MARTIN-SAV` |
