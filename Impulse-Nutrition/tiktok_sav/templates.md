# TikTok SAV — Templates de réponse

Templates utilisés par le skill `/tiktok-sav`. Persona : **service client Impulse Nutrition**, vouvoiement formel, signature « Le service client ». **Jamais** de tutoiement. **Jamais** de tirets em (—) dans les messages.

---

## T0 — ACK first-touch (auto-send, toujours)

**Déclencheur** : tout nouveau message buyer non encore ACKé dans `state.json`.

**Texte** :
```
Bonjour,

Merci pour votre message, nous revenons vers vous avec des solutions aussi rapidement que possible.

Belle journée,
Le service client
```

---

## T1 — Tracking / où est mon colis (auto-send)

**Keywords** : `tracking`, `colis`, `livraison`, `où est`, `pas reçu`, `suivi`, `livraison retard`, `n'est pas arrivé`, `encore là`

**Texte** :
```
Bonjour,

Pour suivre votre colis, pouvez-vous nous communiquer votre numéro de commande (format IMPxxxx) afin que nous puissions vous donner son statut exact ?

Dès réception, nous vérifions immédiatement l'avancement de votre livraison.

Belle journée,
Le service client
```

---

## T2 — Produit endommagé (COMPLEX → queue, pas d'auto-send)

**Keywords** : `cassé`, `abîmé`, `abimé`, `endommagé`, `percé`, `écrasé`, `défectueux`, `explosé`, `fuite`, `déchiré`

**Action** : ajouter à `queue.json` avec catégorie `T2_DAMAGED`, priorité `high`.

**Workflow humain suggéré** :
1. Lire le message + check s'il y a une photo/vidéo jointe
2. Suivre `docs/process_create_codes.md §4` pour créer un code `[PRENOM]-SAV`
3. Utiliser le template SAV bidon/barre selon choix client

---

## T3 — Code promo ne marche pas (auto-send, demande info)

**Keywords** : `code`, `promo`, `marche pas`, `fonctionne pas`, `invalide`, `ne passe pas`, `rejeté`, `expiré`

**Texte** :
```
Bonjour,

Pour qu'on puisse vérifier votre code, pouvez-vous nous indiquer :

1. Le code exact, écrit lettre par lettre avec un espace entre chaque caractère (par exemple : A B C 1 2 3)
2. L'endroit où vous l'avez trouvé (description d'une vidéo, story, profil d'un athlète…)

Dès votre réponse, nous vérifions et revenons vers vous avec une solution.

Belle journée,
Le service client
```

---

## T4 — Produit manquant dans le colis (COMPLEX → queue)

**Keywords** : `manquant`, `manque`, `il manque`, `reçu que`, `pas tout`, `incomplet`, `il y a pas`

**Action** : ajouter à `queue.json` avec catégorie `T4_MISSING`, priorité `high`.

**Workflow humain suggéré** :
1. Lire le message + identifier quel produit manque
2. Check la commande côté Shopify + BigBlue pour vérifier ce qui a été expédié
3. Créer un ticket BigBlue si c'est une erreur fulfillment
4. Envoyer un code SAV si c'est confirmé

---

## T5 — Adresse incorrecte à modifier (COMPLEX → queue)

**Keywords** : `adresse`, `modifier adresse`, `changer adresse`, `mauvaise adresse`, `je me suis trompé`, `faute de frappe`

**Action** : ajouter à `queue.json` avec catégorie `T5_ADDRESS`, priorité `high`.

**Workflow humain suggéré** :
1. Vérifier si la commande est déjà expédiée (check BigBlue)
2. Si pas encore expédiée : modifier l'adresse via BigBlue `update_order`
3. Si déjà expédiée : impossible, proposer un remboursement ou redirection

---

## T6 — Question délai de livraison (auto-send)

**Keywords** : `quand`, `délai`, `combien de temps`, `combien de jours`, `quand arriver`, `quand recevoir`, `expédition quand`

**Texte** :
```
Bonjour,

Votre commande est expédiée depuis notre entrepôt en France. Le délai standard est de 2 à 5 jours ouvrés via Colissimo après expédition.

Vous recevrez un email avec le numéro de suivi dès la prise en charge par le transporteur. Si vous souhaitez le statut exact de votre commande, n'hésitez pas à nous communiquer votre numéro de commande (format IMPxxxx).

Belle journée,
Le service client
```

---

## T7 — Question produit / utilisation (auto-send, demande info)

**Keywords** : `comment utiliser`, `dosage`, `combien prendre`, `compatible`, `allergie`, `allergène`, `ingrédient`, `composition`, `vegan`, `sans gluten`, `lactose`

**Texte** :
```
Bonjour,

Merci pour votre question. Pour vous donner les informations les plus précises, pouvez-vous nous préciser :

1. Le nom exact du produit concerné
2. Votre question précise (dosage, composition, allergènes, compatibilité...)

Nous revenons vers vous avec les détails.

Belle journée,
Le service client
```

---

## T8 — Demande retour / remboursement (COMPLEX → queue)

**Keywords** : `retour`, `remboursement`, `rembourser`, `pas satisfait`, `annuler`, `changer d'avis`, `annulation`

**Action** : ajouter à `queue.json` avec catégorie `T8_REFUND`, priorité `medium`.

**Workflow humain suggéré** :
1. Comprendre la raison précise (insatisfaction, erreur, etc.)
2. Vérifier la commande (Shopify + BigBlue)
3. Décider : remboursement intégral / partiel / remplacement / refus argumenté
4. Exécuter via Shopify order update + BigBlue si retour physique

---

## T9 — Merci / feedback positif (auto-send)

**Keywords** : `merci`, `super`, `top`, `parfait`, `génial`, `excellent`, `contente`, `content`, `bravo`, `j'adore`, `j'aime`

**Texte** :
```
Bonjour,

Merci beaucoup pour votre retour, cela nous fait très plaisir !

N'hésitez pas à nous tagguer @impulse_nutrition sur vos stories ou posts si vous appréciez nos produits, nous serons ravis de vous découvrir.

Très belle journée,
Le service client
```

---

## Fallback — COMPLEX (aucun pattern matché)

**Déclencheur** : aucun keyword reconnu, ou message très court/ambigu.

**Action** :
1. Envoyer le T0 ACK en Layer 1 (déjà fait en amont)
2. Ajouter à `queue.json` avec catégorie `UNKNOWN`, priorité `medium`.

**Workflow humain suggéré** : lire le message, décider au cas par cas.

---

## Règles de classification (ordre de priorité)

Quand plusieurs patterns matchent, appliquer dans cet ordre :

1. **T2 Damaged** (mots-clés de dégradation)
2. **T4 Missing** (mots-clés d'absence produit)
3. **T5 Address** (mots-clés adresse)
4. **T8 Refund** (mots-clés remboursement)
5. **T3 Code promo** (mots-clés code/promo)
6. **T1 Tracking** (mots-clés suivi)
7. **T6 Délai** (mots-clés temps)
8. **T7 Produit** (mots-clés utilisation/composition)
9. **T9 Merci** (mots-clés positifs)
10. **UNKNOWN** (fallback)

Les catégories T2/T4/T5/T8 sont **toujours** routées en Layer 3 (queue), jamais auto-send.
Les catégories T1/T3/T6/T7/T9 sont auto-send avec le template ci-dessus.
