# Guide de Réponse DM — Impulse Nutrition

## Mode opératoire
**Draft only** — Claude rédige, Antoine valide TOUJOURS avant envoi.

---

## Arbre de décision : quel draft rédiger ?

### 1. Par type de message reçu

| Message reçu | Statut (J) | Draft à rédiger | Template ref |
|---|---|---|---|
| Réponse positive au pitch ("oui ça m'intéresse") | In-cold → In-hot | Second message (explication programme) | `second_msg_program_detail` ou `second_msg_ravis` |
| Questions sur le programme | In-hot | Réponse aux questions + proposition call | Personnalisé (voir personality.md §5-6) |
| Envoi coordonnées (adresse/mail/tel) | In-hot | Accusé réception + "je prépare la commande" | Micro-message : "C'est noté je te dis comment je procède !" |
| Choix produits / panier | In-hot / A recontacter | Validation panier + accusé | "C'est bien noté !" / "Super choix !" |
| "Déjà pris par une autre marque" | In-cold → Out | Message adapté selon le sponsor | `already_taken_*` (4 variantes) |
| "Je ne prends pas de compléments" | In-cold | Argument doux + proposition call | Personnalisé (voir corpus : ilana_slk) |
| "Voir avec mon manager" | → Contacter manager | "Bien sûr !" + noter le contact | Micro-message |
| Confirmation réception colis | Produits envoyés | "Hâte d'avoir tes retours !!" | `post_shipment_excitement` |
| Feedback positif sur produit | Produits envoyés | Enthousiasme court | "Trop content que ça te plaise !!" / "Super on est ravi !!" |
| Feedback négatif sur produit | Produits envoyés | Empathie + proposition alternative/call | Personnalisé (voir personality.md §11) |
| Story/reel partagé mentionnant Impulse | Produits envoyés | Réaction courte enthousiaste | "Trop bien merci !! 🔥" / "Au top !!" |
| Story sans code visible | Produits envoyés | Nudge code doux | `nudge_code_usage` |
| "Merci" (pour promo, info, etc.) | Tout statut | Micro-réponse | "Avec plaisir !!" / "Merci à toi !!" |
| Demande de réassort | Produits envoyés | Proposer listing par message ou call | "Tu veux me mettre ce que tu as besoin par message ? Sinon on s'appelle 😉" |
| Question sur les stats du code | Produits envoyés | Donner le chiffre exact | "[N] utilisation(s) de ton code, bien joué !!" |
| Problème technique (code, Affiliatly, mail) | Produits envoyés | "Je check ça !" puis résolution | Personnalisé |
| Demande d'utilisation du crédit | Produits envoyés | Expliquer le process | "Tu m'envoies un message avec ce que tu veux, je te fais un code !" |
| Résultat sportif / compétition | Tout statut | Félicitations courtes | "Bravo c'est énorme !! 🔥" |
| Excuse de retard / silence | Tout statut | Rassurer | "Aucun souci !" / "Prends ton temps" |
| Message vocal (voice_media) | Tout statut | ⚠️ NE PAS DRAFTER — signaler à Antoine | L=high, "message vocal à écouter" |
| Media éphémère (raven_media) | Tout statut | ⚠️ NE PAS DRAFTER — signaler à Antoine | L=medium, "contenu inaccessible" |

### 2. Par statut pipeline (J)

#### In-cold (relance / warm-up)
- Si aucune réponse après pitch + relance → proposer "réagir à story" (pas de nouveau DM)
- Si réponse positive → passer en In-hot, drafter second message

#### In-hot (discussion active)
- Adapter le second message selon l'enthousiasme :
  - Fort → `second_msg_ravis` ou `second_msg_impressionnes`
  - Normal → `second_msg_program_detail`
  - Avec questions → réponse personnalisée + proposition call
- Si envoi coordonnées → drafter accusé + noter en col K

#### A recontacter / A rediscuter
- Vérifier la date de dernière interaction
- Si > 2 semaines → drafter une relance douce
- Si en attente d'info de leur part → attendre (L=medium)

#### Produits envoyés (ambassadeur actif)
- Mode réactif : répondre aux messages, réagir aux stories
- Proactif uniquement pour : promos, demande d'avis, nudge code
- Si l'ambassadeur a un sponsor concurrent sur un segment (ex: Hydratis pour les électrolytes), ne pas proposer les produits concurrents. Se concentrer sur les produits complémentaires.

#### Contacter manager
- Ne pas drafter de DM — le contact passe par mail
- Juste signaler si le manager a répondu/relancé

---

## Micro-messages — Catalogue complet

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

### Cloture
- "Très bonne soirée !!"
- "Très bon weekend !!"
- "À très vite !"

---

## Règles de rédaction

1. **Tutoiement** toujours (sauf si l'autre vouvoie — switcher vite au tu)
2. **Double exclamation** sur les micro-messages : "Merci !!" pas "Merci !"
3. **Pas de point final** sur les micro-messages
4. **1-2 emojis max** par message. Préférés : 😉 🔥 😄 ☺️
5. **Jamais** : 🙏 💪 🎯 ✨
6. **Signature "Sportivement, Antoine"** uniquement sur messages longs (pitch, onboarding, promo)
7. **Jamais de jargon** : ROI, KPI, conversion, collab (préférer "partenariat"), reach
8. **Ne jamais critiquer** la concurrence
9. **Proposer un call** dès que la conversation se complexifie
10. **Reconnaître ses erreurs** avec "my bad" + correction immédiate
11. **Ne JAMAIS utiliser de tiret cadratin (—)** dans les messages. Utiliser une virgule, un point, ou reformuler.
12. **Ne JAMAIS mentionner de dotation mensuelle** sans validation d'Antoine. La dotation est réservée à certains profils spécifiques. Le parcours standard est : produits gratuits → code affilié → 20€ crédit par commande. Toute mention de dotation ou partenariat rémunéré doit être validée.
13. **Toujours attendre une validation EXPLICITE** ('envoie', 'go', 'c'est bon envoie') avant d'envoyer un DM. 'C'est good' ou 'bon raisonnement' ne sont PAS des validations d'envoi.

---

## FAQ — Réponses types extraites du corpus

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

## Gestion des retards de réponse

- **> 4 jours de retard** : excuse légère. Ex: "Excuse-moi pour le temps de réponse !"
- **> 10 jours de retard** : excuse appuyée. Ex: "Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !"

---

## Points de friction technique récurrents

1. **Bug lien en double** : Le template génère parfois `discount/discount/CODE` — toujours vérifier le lien avant envoi
2. **Affiliatly connexion** : Problèmes fréquents de login — proposer reset ou renvoi mail
3. **Mail d'avis Judge.me** : Arrive souvent en spam ou pas du tout — problème connu
4. **Erreurs de nom sur les colis** : Vérifier l'orthographe avant commande
