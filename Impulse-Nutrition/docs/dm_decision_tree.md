# DM Decision Tree — Bibliothèque procédurale Instagram

Decision tree + bibliothèque de templates **réels** pour répondre aux DMs
Instagram en respectant le ton d'Antoine. Source unique pour drafter une
réponse DM.

> Sources combinées :
> - Onglet `Message_type` du Sheet (templates curés à la main par Antoine)
> - Corpus de conversations téléchargé 2026-04-13 dans `data/conversations/*.json`
> - Ancien `templates/dm_response_guide.md` (mergé ici 2026-04-13, l'original est dans `docs/archive/`)
>
> À régénérer périodiquement avec `scripts/extract_response_templates.py`
> + revue manuelle pour fusionner avec les nouveaux templates Sheet.

---

## 0. Règles de tone (rappel)

- **Mode opératoire** : Draft only — Claude rédige, Antoine valide TOUJOURS avant envoi. "C'est good" ou "bon raisonnement" ne sont **PAS** des validations d'envoi. Seul "envoie" / "go" / "c'est bon envoie" valide.
- **Tutoiement systématique**. Toujours `tu`, jamais `vous`. Si l'autre vouvoie → switcher vite au tu.
- **Signature** : `Sportivement, Antoine` (sur les longs messages ≥ 3 phrases) ou `Antoine` ou `Antoine - Impulse Nutrition`. Sur les micro-messages, **pas de signature**.
- **Double exclamation** sur les micro-messages : "Merci !!" pas "Merci !"
- **Pas de point final** sur les micro-messages.
- **Emojis modérés** : 0 à 2 par message max. Favoris (corpus 2026-04-13) : 😉 🔥 😄 😊 😍 ☺️ 💪. Éviter 🙏 ✨ 💖 (mielleux).
- **Pas de tirets em** (`—`). Phrases courtes.
- **Pas d'attaque par "Bonjour"** dans une conversation déjà ouverte. Réserver à un premier contact.
- **Pas de re-listing exhaustif des produits** dans une conversation déjà avancée — info concrète, pas de surcharge.
- **Pas de jargon** : ROI, KPI, conversion, collab (préférer "partenariat"), reach.
- **Ne JAMAIS critiquer la concurrence**.
- **Proposer un call** dès que la conversation se complexifie.
- **Reconnaître ses erreurs** avec "my bad" + correction immédiate.
- **Ne JAMAIS mentionner de dotation mensuelle sans validation d'Antoine**. Le parcours standard est : produits gratuits → code affilié → 20€ crédit par commande. Toute mention de dotation ou partenariat rémunéré doit être validée.

Détails et stats : [`../instagram_dm_mcp/personality.md`](../instagram_dm_mcp/personality.md)
(auto-régénéré par `scripts/extract_tone.py`).

---

## 0.5 Pre-draft check obligatoire (hard rule)

**Avant tout draft DM, exécuter DEUX checks bloquants. Aucune exception.**

### Check 1 — Thread history (toujours 50 messages minimum)

Récupérer au moins 50 messages du thread avec `list_messages(thread_id, amount=50)` (augmenter si le thread est plus long ou si les 50 ne remontent pas au premier message). Scanner l'historique pour détecter :

- **Codes welcome déjà donnés** : grep sur `"PGAU25"`, `"ACHAB25"`, `"-25%"`, `"code exclusif"`, `"code perso"`, `"{NOM}25"`. Un prospect qui a déjà reçu un code welcome a été **parqué** par un autre membre de l'équipe (pas rejeté définitivement, mais jugé pas prêt pour le programme ambassadeur). Traiter la suite comme une relance contextualisée (§16), JAMAIS comme un premier contact.
- **Échanges Impulse antérieurs** : si le thread contient déjà un message `is_sent_by_viewer=true` autre que ton action courante, ce n'est PAS un premier contact. Le pitch §2 est interdit sans acknowledger le passé.
- **Positions Impulse précédentes** : si Impulse a déjà refusé (`"nous privilégions +10k abonnés"`, `"nos partenariats actuels sont complets"`, `"taux d'engagement minimum de 4%"`), ne JAMAIS drafter une réponse qui contredit cette position sans reconnaître explicitement le changement de contexte.
- **Rencontres IRL** : mots-clés `"stand"`, `"salon"`, `"Run Expérience"`, `"marathon de Paris"`, `"nous avons échangé"`, `"nutritionniste en doctorat"`. Si oui, le contexte compte énormément et la réponse doit capitaliser dessus.

### Check 2 — Sheet check (3 tabs)

`find_in_spreadsheet(query=username, sheet="Suivi_Amb")` puis pareil sur `Suivi_Dot` et `Suivi_Paid`. Si la personne est déjà dans un pipeline, son statut col J dicte le template à utiliser (cf §11 routing par statut).

### Règle d'or

**Le thread Instagram est la source de vérité primaire. Le Sheet est secondaire** (beaucoup de prospects ne sont pas encore dans le Sheet, notamment les parqués avec welcome code). Ne jamais se baser UNIQUEMENT sur le Sheet pour juger qu'un prospect est "nouveau".

### Si l'un des deux checks remonte un hit

Ne pas drafter avant d'avoir compris le contexte complet. Signaler à Antoine avec :
1. Les éléments trouvés verbatim (dernier message Impulse, code donné, date, rencontre IRL, etc.)
2. Ta lecture de la situation
3. Une proposition de template de relance contextualisée (§16) OU une question de clarification

---

## 1. Decision tree principal

```
DM reçu
  │
  ├─ C'est un PREMIER contact (jamais parlé avant) ?
  │     │
  │     ├─ Oui → §2 Premier message ambassadeur
  │     │
  │     └─ Non → continuer
  │
  ├─ La personne dit qu'elle est DÉJÀ PRISE par un concurrent ?
  │     │
  │     ├─ Sponsor exclusif effort/perfo → §3.1 Refus poli stop
  │     ├─ Sponsor bien-être global       → §3.2 Refus poli + porte ouverte effort
  │     ├─ Sponsor effort secondaire      → §3.3 Refus poli + porte ouverte récup
  │     └─ Pas clair                       → §3.0 Refus poli neutre
  │
  ├─ La personne demande PLUS d'infos sur le programme ?
  │     │
  │     └─ §4 Présentation détaillée du programme ambassadeur
  │
  ├─ La personne ACCEPTE le programme ?
  │     │
  │     └─ §5 Acceptation : demande infos commande
  │
  ├─ La personne A REÇU sa commande ?
  │     │
  │     └─ §6 Message envoi commande
  │
  ├─ La personne a posté/storifié → §7 Réaction au contenu
  │
  ├─ La personne a un PROBLÈME sur sa commande → SAV (cf process_sav_unified.md)
  │
  ├─ La personne demande à utiliser ses CRÉDITS → §8 Demande utilisation code
  │
  └─ Autre → §9 Improviser dans le ton, courte réponse
```

---

## 2. Premier message ambassadeur

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

**Variante courte (impressionné par le profil)** :

> On est très impressionnés par ton parcours ! C'est très inspirant et tu
> partages vraiment les valeurs du sport et du dépassement de soi, donc
> déjà bravo !!
>
> Travailler avec toi sera un plaisir ! Ce que je te propose :
>
> Dans un premier temps, on t'envoie pour 80 € de produits, tu choisis ce
> que tu préfères ou on te fait un pack, c'est comme tu préfères, dans tous
> les cas c'est gratuit pour toi !
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

---

## 3. La personne est déjà prise

### 3.0 Refus poli neutre (sponsor non identifié)

> On comprend tout à fait, merci d'avoir pris le temps de nous répondre !
> On te souhaite une très belle continuation dans tes projets avec ta
> marque actuelle. Une future collaboration serait avec grand plaisir,
> n'hésite surtout pas à revenir vers nous si l'occasion se présente !
>
> Sportivement,
> Antoine

### 3.1 Sponsor exclusif effort/perfo (TA Energy, Nutripure, Overstim…)

→ Statut Suivi_Amb passe en `Out`, priorité `good`, on n'insiste plus.
Réponse identique à §3.0, courte.

### 3.2 Sponsor uniquement bien-être global

> Merci d'avoir pris le temps de nous répondre ! On comprend tout à fait
> et l'on te souhaite une très belle continuation dans tes projets avec
> ta marque actuelle. Si jamais tu cherches des compléments alimentaires
> plus axés sur l'effort, et vraiment spécialisés sur la performance, on
> pense vraiment qu'Impulse Nutrition pourrait te plaire. Si ça t'intéresse,
> n'hésite surtout pas, on reste disponibles pour une future collaboration !
>
> Sportivement,
> Antoine - Impulse Nutrition

### 3.4 Refus communauté trop petite (prospect entrant, compte < ~1k abonnés)

→ Statut `Out`, priorité `good`. On offre un code welcome -25% first-order pour qu'il puisse découvrir la marque.

**Codes welcome actifs** (format `{NOM}25`, chaque membre HCS a son propre code pour le tracking d'attribution Shopify) :

| Code | Owner | Contact | Notes |
|---|---|---|---|
| `ACHAB25` | Antoine Chabrat | toi-même | **Code préféré côté DM Instagram** — cohérent avec le ton tutoiement/Antoine |
| `PGAU25` | Pierre Gautier | pgautier@havea.com | Collègue HCS, gère aussi les commandes dotation. Ton SC vouvoiement |

Quand tu vois un de ces codes (ou toute variante `{NOM}25`) dans un thread, **ça veut dire que le prospect a déjà été parqué par un autre membre de l'équipe**. Il n'est pas rejeté définitivement, mais il faut traiter la suite comme une **relance contextualisée (§16)**, pas un pitch d'entrée.

> Merci pour ton message {prenom} et pour le partage de ton projet, {accroche projet} 🔥
>
> Pour être transparent avec toi, on travaille avec des profils qui ont une
> communauté déjà bien établie sur les réseaux, et pour l'instant ton compte
> ne correspond pas encore aux critères qu'on recherche pour nos partenariats.
> Ce n'est absolument pas un jugement sur la qualité de ton contenu ou de ton
> projet, mais c'est notre critère actuel.
>
> Ce qu'on peut faire en revanche : je te laisse un code perso {CODE25} pour
> que tu puisses découvrir nos produits avec -25% sur ta commande. Et si dans
> le futur ta communauté se développe, n'hésite pas à revenir vers nous, ce
> sera avec plaisir !
>
> Sportivement,
> Antoine

### 3.3 Sponsor axé effort mais ouverture sur la récup

> Merci d'avoir pris le temps de nous répondre ! On comprend tout à fait
> et l'on te souhaite une très belle continuation dans tes projets avec ta
> marque actuelle. Si jamais tu cherches à trouver des compléments
> alimentaires plus axés sur la récupération et les moments avant et après
> l'effort, on pense vraiment qu'Impulse Nutrition pourrait te plaire. On
> sait qu'il nous manque quelques produits pour la partie effort, mais on
> y travaille ! En revanche, on a vraiment de super produits pour la récup,
> donc si ça t'intéresse, n'hésite surtout pas, on reste disponibles pour
> une future collaboration !
>
> Sportivement,
> Antoine - Impulse Nutrition

---

## 4. Présentation détaillée du programme ambassadeur

> On est ravis !
>
> Pour t'expliquer plus en détails, l'objectif du programme ambassadeur est
> que tu représentes la marque en réalisant des posts, stories ou tout
> autre format de ton choix, afin que ton code d'affiliation soit utilisé
> un maximum. En tant qu'ambassadeur, tu reçois un crédit de 20€ à
> utiliser sur Impulse Nutrition à chaque fois qu'une commande est réalisée
> avec ton code. Ça te permet de commander autant de compléments
> alimentaires que nécessaire pour ta pratique !
>
> Par la suite, si tout se passe vraiment bien, on pourra naturellement
> évoluer vers un partenariat rémunéré.
>
> Si tu veux plus d'infos, n'hésite pas. En tout cas, ton profil nous
> intéresse beaucoup et on a des produits sympas à te faire tester !
>
> Sportivement,
> Antoine

---

## 5. Acceptation : demande infos commande

> C'est parfait pour nous aussi ! On te laisse choisir et revenir vers
> nous avec ta sélection. N'oublie pas de nous transmettre dans le même
> temps une adresse mail et postale. Si tu as besoin d'aide ou d'infos sur
> les produits n'hésite pas !
>
> Sportivement,
> Antoine - Impulse Nutrition

**Variante** :

> Trop bien, on est ravi ! 😄
>
> Pour tester les produits, est-ce que tu préfères sélectionner toi-même
> les produits qui t'intéressent sur notre site ou qu'on te concocte un
> pack personnalisé ? Dans les deux cas c'est gratuit pour toi ! Il me
> faudra également une adresse (avec nom + prénom), un email et un numéro,
> je te prépare la commande en suivant !
>
> Sportivement,
> Antoine

---

## 5.5 Commande validée + envoi du code affilié (CRITIQUE)

**Template canonique** à utiliser quand la draft Shopify est créée et qu'on
envoie le code affilié à l'ambassadeur. Ne JAMAIS omettre les 3 points clés
en gras ci-dessous : cumulabilité produits, cumulabilité expédition,
livraison gratuite dès 69 €.

> La commande est validée et sera expédiée très prochainement !
>
> Je t'ai créé un code affilié perso ({CODE}) qui permettra à ta communauté
> de bénéficier de -15% sur tout le site (sans minimum d'achat). **Le code
> est cumulable avec toutes les autres réductions sur les produits ET avec
> les réductions sur l'expédition. La livraison est également gratuite dès
> 69 € d'achat.**
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

### ❌ À NE PAS utiliser (obsolète depuis avril 2026)

- ~~« avec un shaker offert dès 59 € d'achats »~~ : promo historique supprimée.
- ~~« -15% sur leur première commande »~~ : le code marche sur TOUTES les commandes.
- Oublier la mention « cumulable avec les autres réductions produits ET expédition ».
- Oublier la mention « livraison gratuite dès 69 € ».

---

## 6. Message envoi commande

> Hâte d'avoir tes retours et bonne dégustation !!

Court, simple, pas de signature. Suit l'envoi du tracking ou la création
de la commande.

---

## 7. Réaction au contenu (post / story)

### 7.1 Stories manquées (réaction tardive)

> Hello ! J'ai pas eu le temps de voir tes stories, tu as été trop rapide
> pour moi !
> Les produits t'ont plu ? ☺️

### 7.2 Conseils pour optimiser le code (post-publication)

> Hello {prenom},
>
> J'espère que tu vas bien ! J'ai vu tes derniers contenus, c'est vraiment
> top !
>
> Petit retour de ce qui fonctionne bien chez nos ambassadeurs :
> - la mention d'Impulse et du code affilié en bio et Story à la une. Cela
>   permet aux sportifs qui te suivent de retrouver facilement le code
>   s'ils le cherchent 😉
> - le partage de ton lien affilié en story qui permet d'accéder
>   directement sur le site
>
> Encore merci pour ton travail et ta confiance, on est très heureux que
> les produits te plaisent 🙏
>
> Sportivement,
> Antoine

---

## 8. Demande utilisation de code crédit

Quand l'ambassadeur dit "je voudrais utiliser mes crédits" :

1. Vérifier dans `Suivi_Amb` les colonnes O (`nb_utilisation`) et Q
   (`nb_credit_used`).
2. Calculer le solde : `(O − Q) × 20 €` (cf
   [`process_calculate_credits.md`](process_calculate_credits.md)).
3. Proposer le montant disponible.

Réponse type :

> Avec plaisir {prenom} ! Tu as actuellement **{credit_value} €** de crédit
> disponible (soit {solde} utilisations × 20€). Tu veux que je te crée le
> code maintenant ? Tu pourras le passer en une seule commande sur le site.
>
> Sportivement,
> Antoine

Puis :
- Créer le code via [`process_create_codes.md`](process_create_codes.md) §3
- Mettre à jour col P du Sheet
- Envoyer le code à l'ambassadeur

---

## 9. Improvisation : règles d'or

Quand aucun template ne match exactement :

- **Reste court**. Si tu doutes, fais 1-2 phrases max.
- **Réponds à la dernière question** explicitement avant d'ajouter quoi que ce soit.
- **Pas de "Bonjour"** si la conversation est déjà ouverte. "Hello", "Hey", "Coucou", ou directement le contenu.
- **Pas de signature** si moins de 3 phrases.
- **Pas plus de 2 emojis** dans le message complet.
- **Si tu proposes une action** (envoi, code, call), confirme avec la personne avant de l'exécuter.

---

## 10. À ne JAMAIS faire (red flags)

- ❌ **Drafter sans avoir scanné l'historique complet du thread** (50 msgs min via `list_messages amount=50`, cf §0.5 pre-draft check)
- ❌ **Pitcher le programme ambassadeur à un prospect qui a déjà reçu `ACHAB25` / `PGAU25` / `{NOM}25`** — c'est un prospect parqué, traiter en relance contextualisée (§16)
- ❌ **Contredire une position d'Impulse précédemment établie** (refus → acceptation, ou l'inverse) sans acknowledger explicitement le changement de contexte
- ❌ **Ignorer une rencontre IRL** mentionnée dans le thread (stand salon, marathon, événement) — c'est toujours le levier principal de la relance
- ❌ Vouvoyer
- ❌ Signer "Antoine" ou "Sportivement, Antoine" sur un canal autre qu'Instagram
- ❌ Utiliser des tirets em (`—`)
- ❌ Re-coller le pitch ambassadeur dans une conversation déjà avancée
- ❌ Promettre des choses non confirmées (livraison J+1, gratuit illimité, etc.)
- ❌ Oublier d'inclure le `{prenom}` dans un premier message
- ❌ Inclure des emojis "mielleux" : 🙏 ✨ 💖
- ❌ Surcharger en 🔥 ou 💪 (max 1 par message)

---

## 11. Routing détaillé par type de message reçu

Table de routing exhaustive (source : ancien `templates/dm_response_guide.md`, mergé ici).

| Message reçu | Statut (J) | Draft à rédiger |
|---|---|---|
| Réponse positive au pitch ("oui ça m'intéresse") | In-cold → In-hot | Second message (explication programme — voir §4) |
| Questions sur le programme | In-hot | Réponse aux questions + proposition call |
| Envoi coordonnées (adresse/mail/tel) | In-hot | Accusé : "C'est noté je te dis comment je procède !" |
| Choix produits / panier | In-hot / A recontacter | Validation : "C'est bien noté !" / "Super choix !" |
| "Déjà pris par une autre marque" | In-cold → Out | Message adapté selon le sponsor (voir §3) |
| "Je ne prends pas de compléments" | In-cold | Argument doux + proposition call (voir corpus : ilana_slk) |
| "Voir avec mon manager" | → Contacter manager | "Bien sûr !" + noter le contact |
| Confirmation réception colis | Produits envoyés | "Hâte d'avoir tes retours !!" (voir §6) |
| Feedback positif sur produit | Produits envoyés | Enthousiasme court : "Trop content que ça te plaise !!" |
| Feedback négatif sur produit | Produits envoyés | Empathie + proposition alternative/call |
| Story/reel partagé mentionnant Impulse | Produits envoyés | Réaction courte enthousiaste : "Trop bien merci !! 🔥" |
| Story sans code visible | Produits envoyés | Nudge code doux (voir §7.2) |
| "Merci" (pour promo, info, etc.) | Tout statut | Micro-réponse : "Avec plaisir !!" / "Merci à toi !!" |
| Demande de réassort | Produits envoyés | "Tu veux me mettre ce que tu as besoin par message ? Sinon on s'appelle 😉" |
| Question sur les stats du code | Produits envoyés | Donner le chiffre exact : "[N] utilisation(s) de ton code, bien joué !!" |
| Problème technique (code, Affiliatly, mail) | Produits envoyés | "Je check ça !" puis résolution |
| Demande d'utilisation du crédit | Produits envoyés | Voir §8 (`process_calculate_credits.md`) |
| Résultat sportif / compétition | Tout statut | Félicitations courtes : "Bravo c'est énorme !! 🔥" |
| Excuse de retard / silence | Tout statut | Rassurer : "Aucun souci !" / "Prends ton temps" |
| Message vocal (`voice_media`) | Tout statut | ⚠️ NE PAS DRAFTER — signaler à Antoine, L=high |
| Media éphémère (`raven_media`) | Tout statut | ⚠️ NE PAS DRAFTER — signaler à Antoine, L=medium |

### Routing par statut pipeline

- **In-cold** : si pas de réponse après pitch + relance → proposer "réagir à story" (pas de nouveau DM). Si réponse positive → passer en In-hot, drafter second message.
- **In-hot** : adapter le second message selon enthousiasme. Si envoi coordonnées → drafter accusé + noter en col K.
- **A recontacter / A rediscuter** : si > 2 semaines depuis dernière interaction → drafter une relance douce. Si en attente d'info de leur part → attendre (L=medium).
- **Produits envoyés** : mode réactif, répondre aux messages + réagir aux stories. Proactif uniquement pour : promos, demande d'avis, nudge code. Si sponsor concurrent sur un segment (ex: Hydratis pour les électrolytes), ne pas proposer les produits concurrents — se concentrer sur les complémentaires.
- **Contacter manager** : ne pas drafter de DM, le contact passe par mail. Juste signaler si le manager a répondu/relancé.

---

## 12. Catalogue micro-messages

### Validation / Enthousiasme
- "Trop bien, on est ravi !!"
- "Au top !!"
- "Super !!"
- "Yes au top !"
- "C'est noté je te dis comment je procède !"

### Remerciement
- "Avec plaisir !!"
- "Merci à toi !!"
- "Merci beaucoup !!"

### Réaction contenu
- "Trop bien merci !! 🔥"
- "Au top, merci beaucoup !! 😍"
- "Trop cool merci à toi !! 🔥🔥"
- "Bravo c'est énorme !! 🔥"

### Accusé de réception
- "Bien reçu merci !"
- "C'est bien noté !"
- "Aucun soucis c'est bien noté !"
- "Entendu ! 😉"

### Rassurance
- "Aucun souci !"
- "Prends ton temps !"
- "All good"

### Post-commande
- "Hâte d'avoir tes retours et bonne dégustation !!"
- "Let's go c'est bon c'est modifié !"

### Clôture
- "Très bonne soirée !!"
- "Très bon weekend !!"
- "À très vite !"

---

## 13. FAQ — Réponses types extraites du corpus

### "Comment utiliser mon crédit ?"
> Tu m'envoies un message avec ce que tu veux commander, et je te fais un code du montant correspondant. Sinon on peut prévoir un call si tu préfères !

### "Combien de personnes ont utilisé mon code ?"
> [N] utilisation(s) de ton code, bien joué !!

### "Mon code/lien ne marche pas"
> Je check ça tout de suite ! [vérifier et corriger, puis] C'est réglé, tu peux réessayer !

### "Je peux dépasser un peu le budget de 80€ ?"
> Le budget c'est 80€ mais ça peut dépasser un petit peu, pas de souci !

### "Quand et comment prendre les produits ?"
> Whey : 30min-1h après l'entraînement. Magnésium : le soir. Créatine : dans ton shaker avec le collagène. [Adapter selon les produits commandés]

### "Le preworkout m'a donné des effets secondaires"
> C'est normal si c'est ta première prise ! Essaie avec 1/3 ou 1/2 scoop pour commencer, et augmente progressivement. N'hésite pas à me dire comment ça se passe !

### "Je suis libre sur le contenu ?"
> Oui totalement ! Le format est libre, c'est toi qui gères selon ce qui colle le mieux à ta façon de communiquer. L'essentiel c'est de glisser ton code et ton lien pour que tes abonnés puissent en profiter !

### "C'est un partenariat ponctuel ou long terme ?"
> L'idée c'est vraiment de bosser sur le long terme ! On commence par un envoi de produits, si les produits te plaisent on te crée un code affilié, et à chaque commande passée avec ton code tu reçois 20€ de crédit chez nous. Et si la collab fonctionne vraiment bien, on peut envisager d'aller plus loin ensemble.

### "J'arrive pas à me connecter à Affiliatly"
> Je check ça ! [Reset mot de passe ou renvoi du mail d'inscription]

### "Le mail d'avis n'est pas arrivé"
> Je vais voir si je peux te le renvoyer. Sinon, on travaille sur une solution pour laisser un avis directement depuis le site !

### "Quelle est la différence entre la Whey Isolate et la Whey Recovery ?"
> La Whey Recovery c'est une formule 3-en-1 : whey concentrate + créatine + collagène, pensée pour une récupération complète (musculaire, articulaire et performance). La Whey Isolate c'est de la protéine pure et plus concentrée, idéale si tu veux juste l'apport protéique. Les deux contiennent de la lactase donc pas de souci de digestion !

### "Vos produits contiennent du lactose ?"
> Nos whey contiennent de la lactase, une enzyme qui aide à digérer le lactose, donc pas de souci de digestion !

---

## 14. Gestion des retards de réponse

- **> 4 jours de retard** : excuse légère. Ex: "Excuse-moi pour le temps de réponse !"
- **> 10 jours de retard** : excuse appuyée. Ex: "Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !"

---

## 15. Points de friction technique récurrents

1. **Bug lien en double** : Le template génère parfois `discount/discount/CODE` — toujours vérifier le lien avant envoi.
2. **Affiliatly connexion** : Problèmes fréquents de login — proposer reset ou renvoi mail.
3. **Mail d'avis Judge.me** : Arrive souvent en spam ou pas du tout — problème connu.
4. **Erreurs de nom sur les colis** : Vérifier l'orthographe avant commande.

---

## 16. Relance d'un prospect parqué

Un prospect "parqué" = quelqu'un qui a déjà reçu un code welcome -25% (`ACHAB25`, `PGAU25`, ou variante `{NOM}25`) lors d'un échange antérieur. Ce n'est pas un nouveau contact. Il faut reprendre la conversation en acknowledgeant explicitement le passé.

### Détection

Déclenchée par le pre-draft check (§0.5). Symptômes dans le thread :
- Un message Impulse historique qui refuse le programme ambassadeur et donne un code welcome.
- Le prospect revient de lui-même (parfois plusieurs mois après) avec un nouveau contexte : audience qui a grandi, participation à un événement Impulse, actualité sportive concrète, etc.

### Règle impérative

**JAMAIS drafter un pitch d'entrée §2 dans ce cas**, même si la relance est ancienne. Le prospect a une mémoire précise de l'échange précédent. Contredire ou ignorer cette mémoire détruit la crédibilité d'Impulse et rend la marque incohérente.

### Trame de relance contextualisée

Adapter au cas par cas, mais respecter la structure :

> Salut {prenom}, merci de revenir vers nous !
>
> {Acknowledgment explicite du contexte nouveau : "tu as bien grandi depuis notre dernier échange", "c'était sympa d'échanger avec toi sur le stand du salon Run Expérience", "ta prépa pour l'Ultra Marin approche", "les stats que tu nous as partagées sont très solides", etc.}
>
> {Si le contexte le justifie vraiment} Ça fait tout à fait sens qu'on reprenne cette discussion maintenant. {Proposition adaptée — peut être le programme ambassadeur si le profil qualifie désormais, ou une autre piste (call, rencontre, offre ponctuelle)}.
>
> {Si pas sûr} Je regarde ça de près et je reviens vers toi très vite pour te proposer quelque chose qui ait du sens.
>
> Sportivement,
> Antoine

### Cas-types

| Situation | Réaction |
|---|---|
| Parqué à <1k qui revient à 10k+ avec stats concrètes | Drafter offre programme ambassadeur (cf §2/§4) **en reconnaissant l'échange précédent** et en actualisant le contexte |
| Parqué qui a rencontré l'équipe IRL (stand, salon) | Réponse chaleureuse qui capitalise sur la rencontre, mentionner les personnes croisées si connues, proposer un call ou une offre adaptée |
| Parqué qui relance sans nouvel élément | Réponse courte, réexpliquer poliment la position sans répéter le refus brut, garder la porte ouverte |
| Parqué qui n'a pas grandi mais est très actif | Rester sur la position "parqué", ne pas upgrade arbitraire. Acknowledgment + encouragements |

### Ne JAMAIS

- ❌ Utiliser le pitch §2 comme si c'était un premier contact
- ❌ Ignorer le code déjà donné (`ACHAB25`/`PGAU25`)
- ❌ Contredire une position d'Impulse sans explication
- ❌ Créer un 2e code welcome si le prospect en a déjà un actif

---

## 17. See also

- [`../instagram_dm_mcp/personality.md`](../instagram_dm_mcp/personality.md) — guide auto-généré, stats détaillées du corpus
- [`../templates/real_response_examples.md`](../templates/real_response_examples.md) — exemples anonymisés auto-générés
- [`process_calculate_credits.md`](process_calculate_credits.md) — calcul du solde crédit
- Onglet Sheet `Message_type` — source primaire des templates ci-dessus
- `archive/templates/dm_response_guide.md` — version manuelle historique (mergée ici)
