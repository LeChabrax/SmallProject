# TikTok SAV -- Templates de reponse

Templates utilises par le skill `/tiktok-sav`. Persona : **service client Impulse Nutrition**, vouvoiement formel, signature "Le service client". **Jamais** de tutoiement. **Jamais** de tirets em dans les messages.

---

## T0 -- ACK first-touch (fallback)

**Declencheur** : message buyer non classifiable (aucun pattern matche, message ambigu/court). Sert de reponse generique quand le skill ne peut pas envoyer un template T1-T9 plus precis.

**Texte** :
```
Bonjour,

Merci pour votre message, nous revenons vers vous avec des solutions aussi rapidement que possible.

Belle journee,
Le service client
```

---

## T1 -- Tracking / ou est mon colis (auto-send)

**Keywords** : `tracking`, `colis`, `livraison`, `ou est`, `pas recu`, `suivi`, `livraison retard`, `n'est pas arrive`, `encore la`

**Texte** :
```
Bonjour,

Merci pour votre commande ! Voici le statut actuel de votre commande {{order_number}} :

{{tracking_status}}

N'hesitez pas si vous avez d'autres questions.

Belle journee,
Le service client
```

---

## T2 -- Produit endommage (auto-send + queue)

**Keywords** : `casse`, `abime`, `endommage`, `perce`, `ecrase`, `defectueux`, `explose`, `fuite`, `dechire`

**Action** : envoyer le message adapte (variante A ou B) puis ajouter a `queue.json` avec categorie `T2_DAMAGED`, priorite `high`.

### Variante A -- pas de photo jointe

```
Bonjour,

Merci pour votre commande. Nous sommes desoles d'apprendre que vous avez recu un produit endommage.

Pour que nous puissions traiter votre demande au plus vite, pourriez-vous nous envoyer une photo du produit concerne ?

Nous revenons vers vous rapidement avec une solution.

Belle journee,
Le service client
```

### Variante B -- photo deja jointe

```
Bonjour,

Merci pour votre commande. Nous sommes desoles d'apprendre que vous avez recu un produit endommage.

Nous avons bien recu votre photo et nous traitons votre demande. Nous revenons vers vous rapidement avec une solution.

Belle journee,
Le service client
```

**Workflow humain suggere** :
1. Lire le message + verifier la photo/video jointe
2. Suivre `knowledge/process/create_codes.md` pour creer un code SAV
3. Utiliser le template SAV bidon/barre selon choix client

---

## T3 -- Code promo ne marche pas (auto-send)

**Keywords** : `code`, `promo`, `marche pas`, `fonctionne pas`, `invalide`, `ne passe pas`, `rejete`, `expire`

**Texte** :
```
Bonjour,

Merci pour votre message. Pour que nous puissions verifier votre code, pourriez-vous nous indiquer le code exact que vous essayez d'utiliser ?

Nous verifions et revenons vers vous avec une solution des reception.

Belle journee,
Le service client
```

---

## T4 -- Produit manquant dans le colis (auto-send + queue)

**Keywords** : `manquant`, `manque`, `il manque`, `recu que`, `pas tout`, `incomplet`, `il y a pas`

**Action** : envoyer le message adapte (variante A ou B) puis ajouter a `queue.json` avec categorie `T4_MISSING`, priorite `high`.

### Variante A -- le client ne precise pas quel produit

```
Bonjour,

Merci pour votre commande. Nous sommes desoles d'apprendre qu'il manque un produit dans votre colis.

Pourriez-vous nous indiquer le produit manquant afin que nous puissions traiter votre demande ?

Belle journee,
Le service client
```

### Variante B -- le client a deja precise le produit

```
Bonjour,

Merci pour votre commande. Nous sommes desoles d'apprendre qu'il manque un produit dans votre colis.

Nous avons bien note votre demande et nous verifions de notre cote. Nous revenons vers vous rapidement avec une solution.

Belle journee,
Le service client
```

**Workflow humain suggere** :
1. Check la commande Shopify + BigBlue pour verifier ce qui a ete expedie
2. Creer un ticket BigBlue si c'est une erreur fulfillment
3. Envoyer un code SAV si c'est confirme

---

## T5 -- Adresse incorrecte a modifier (auto-send conditionnel + queue si modifiable)

**Keywords** : `adresse`, `modifier adresse`, `changer adresse`, `mauvaise adresse`, `je me suis trompe`, `faute de frappe`

**Action** : checker le statut BigBlue de la commande, puis envoyer la variante adaptee.

### Variante A -- commande pas encore en preparation (auto-send + queue)

```
Bonjour,

Merci pour votre message. Votre commande n'a pas encore ete prise en charge par notre entrepot, il est donc possible de modifier l'adresse.

Pourriez-vous nous indiquer la nouvelle adresse complete au plus vite afin que nous puissions faire la modification ?

Belle journee,
Le service client
```

Queue avec categorie `T5_ADDRESS`, priorite `high`. Attendre la reponse client puis `update_order` BigBlue.

### Variante B -- commande en preparation ou preparee (auto-send, pas de queue)

```
Bonjour,

Merci pour votre message. Malheureusement, votre commande est deja en cours de preparation dans notre entrepot et l'adresse ne peut plus etre modifiee.

Si le colis ne peut pas etre livre a l'adresse actuelle, il nous sera retourne et nous pourrons alors proceder a un renvoi a la bonne adresse.

N'hesitez pas si vous avez des questions.

Belle journee,
Le service client
```

### Variante C -- commande deja expediee (auto-send, pas de queue)

```
Bonjour,

Merci pour votre message. Votre commande a deja ete expediee et l'adresse ne peut plus etre modifiee.

Si le colis ne peut pas etre livre, il nous sera retourne et nous organiserons un renvoi a la bonne adresse.

Belle journee,
Le service client
```

---

## T6 -- Question delai de livraison (auto-send)

**Keywords** : `quand`, `delai`, `combien de temps`, `combien de jours`, `quand arriver`, `quand recevoir`, `expedition quand`

**Texte** :
```
Bonjour,

Merci pour votre commande ! Les commandes sont expediees depuis notre entrepot en France sous 24 a 48h, puis livrees en 2 a 5 jours ouvres via Colissimo.

Vous recevrez un email avec votre numero de suivi des l'expedition.

Belle journee,
Le service client
```

---

## T7 -- Question produit / utilisation (auto-send ou queue)

**Keywords** : `comment utiliser`, `dosage`, `combien prendre`, `compatible`, `allergie`, `allergene`, `ingredient`, `composition`, `vegan`, `sans gluten`, `lactose`

**Action** : le skill consulte la documentation produit (`knowledge/catalog/`) pour formuler la reponse. Si l'info est trouvable, auto-send. Sinon, queue.

### Variante A -- reponse trouvee dans la doc produit (auto-send)

```
Bonjour,

Merci pour votre interet pour nos produits !

{{product_answer}}

N'hesitez pas si vous avez d'autres questions.

Belle journee,
Le service client
```

### Variante B -- info non trouvable dans la doc (queue)

```
Bonjour,

Merci pour votre interet pour nos produits ! Nous prenons note de votre question et revenons vers vous avec les informations detaillees.

Belle journee,
Le service client
```

Queue avec categorie `T7_PRODUCT`, priorite `medium`.

---

## T8 -- Demande retour / remboursement (auto-send + queue)

**Keywords** : `retour`, `remboursement`, `rembourser`, `pas satisfait`, `annuler`, `changer d'avis`, `annulation`

**Action** : envoyer le message adapte (variante A ou B) puis ajouter a `queue.json` avec categorie `T8_REFUND`, priorite `medium`.

### Variante A -- le client ne precise pas la raison

```
Bonjour,

Merci pour votre message. Nous sommes desoles d'apprendre que votre experience n'a pas ete a la hauteur de vos attentes.

Pourriez-vous nous preciser la raison de votre demande afin que nous puissions vous proposer la meilleure solution ?

Belle journee,
Le service client
```

### Variante B -- le client a deja precise la raison

```
Bonjour,

Merci pour votre message. Nous sommes desoles d'apprendre que votre experience n'a pas ete a la hauteur de vos attentes.

Nous avons bien pris en compte votre demande et revenons vers vous rapidement avec une solution adaptee.

Belle journee,
Le service client
```

**Workflow humain suggere** :
1. Comprendre la raison precise (insatisfaction, erreur, etc.)
2. Verifier la commande (Shopify + BigBlue)
3. Decider : remboursement integral / partiel / remplacement / refus argumente
4. Executer via Shopify order update + BigBlue si retour physique

---

## T9 -- Merci / feedback positif (auto-send)

**Keywords** : `merci`, `super`, `top`, `parfait`, `genial`, `excellent`, `contente`, `content`, `bravo`, `j'adore`, `j'aime`

**Texte** :
```
Bonjour,

Merci beaucoup pour votre retour, cela nous fait tres plaisir !

Si vous avez un moment, un avis sur votre commande nous aiderait enormement. N'hesitez pas a revenir vers nous si vous avez la moindre question.

Belle journee,
Le service client
```

---

## T10 -- Produit perime / DLC courte (auto-send ou queue)

**Keywords** : `perime`, `périmé`, `DLC`, `dlc`, `date limite`, `date de peremption`, `date de péremption`, `depassee`, `dépassée`, `expire`, `expiré`, `date courte`, `bientot perime`, `bientôt périmé`

**Action** : discriminer entre DLC courte (variante A, auto-send seul) et produit vraiment périmé (variante B, message + queue).

### Variante A -- DLC courte mais produit encore valide

Client qui s'inquiète d'une DLC proche (1-3 mois restants) mais pas dépassée.

```
Bonjour,

Merci pour votre message. Nous comprenons votre inquietude concernant la date de peremption.

Nos complements alimentaires restent parfaitement consommables et efficaces jusqu'a la DLC indiquee sur le produit. C'est la limite de garantie de leur pleine efficacite, pas une date butoir brutale.

Si la date vous semble vraiment trop courte par rapport a votre rythme de consommation, nous pouvons regarder ensemble. Pourriez-vous nous indiquer la DLC exacte du produit concerne ?

Belle journee,
Le service client
```

### Variante B -- Produit reellement perime (DLC depassee a reception)

```
Bonjour,

Merci pour votre message. Nous sommes desoles qu'un produit avec une DLC depassee vous soit parvenu, ce n'est absolument pas normal de notre cote.

Pourriez-vous nous envoyer une photo de la DLC et du produit pour que nous puissions traiter votre dossier au plus vite ?

Nous revenons vers vous rapidement avec une solution.

Belle journee,
Le service client
```

Queue avec categorie `T10_EXPIRED`, priorite `high`.

**Workflow humain suggere (variante B)** :
1. Verifier la photo + croiser avec le numero de lot chez BigBlue (si un batch entier est concerne, remonter au fulfillment)
2. Creer un replacement Shopify avec les defaults SAV (tag `Service client`)
3. Noter le lot pour detecter une recurrence

---

## T11 -- Colis marque livre mais pas recu (T0 + queue)

**Keywords** : `livre mais pas recu`, `livré mais pas reçu`, `marque livre`, `marqué livré`, `deja livre`, `déjà livré`, `suivi dit livre`, `suivi dit livré`, `statut livre`, `statut livré`, `jamais recu`, `jamais reçu`, `rien recu`, `rien reçu`, `toujours pas arrive`, `toujours pas arrivé` (quand combines avec les mots-cles "livre" / "livré" dans le suivi)

**Discriminant vs T1** : T1 = tracking "en cours, en transit". T11 = tracking "livre" mais le client dit ne pas avoir recu.

**Action** : envoyer le T0 (ACK generique) puis ajouter a `queue.json` avec categorie `T11_LOST`, priorite `high`.

Pas de template dedie ici : chaque cas necessite une verification humaine (preuve de livraison BigBlue/Chronopost, discussion avec le transporteur, decision replacement vs refund). L'humain gere de bout en bout apres l'ACK.

**Workflow humain** :
1. Verifier la preuve de livraison (photo colis, signature) via BigBlue ou contact Chronopost
2. Si preuve claire (colis bien livre a l'adresse) : demander au client de verifier voisin/gardien ou ouvrir un litige transporteur
3. Si preuve absente ou contestee : replacement draft Shopify (tag `Service client`, livraison a domicile) OU refund selon preference client
4. Revenir vers le client avec la decision + delai estime

---

## T12 -- Effet secondaire / intolerance digestive (T0 + queue HIGH)

**Keywords** : `mal au ventre`, `ballonnement`, `ballonnements`, `diarrhee`, `diarrhée`, `nausee`, `nausée`, `vomi`, `vomissement`, `mal de tete`, `mal de tête`, `migraine`, `allergie`, `allergique`, `reaction`, `réaction`, `effet secondaire`, `effet indesirable`, `effet indésirable`, `tolere pas`, `tolère pas`, `intolerance`, `intolérance`, `digere pas`, `digère pas`

**Risque legal eleve** : ne JAMAIS donner de conseil medical, ne jamais minimiser le symptome, ne jamais diagnostiquer. Pas de template automatique -- chaque cas demande une reponse humaine sur mesure.

**Action** : envoyer le T0 (ACK generique) puis ajouter a `queue.json` avec categorie `T12_HEALTH`, priorite `high`. Antoine gere de bout en bout.

**Workflow humain (obligatoire)** :
1. Lire le message pour evaluer la gravite (leger inconfort vs reaction serieuse)
2. Si reaction serieuse (allergie violente, malaise, signalement pharmacovigilance) → escalade interne HCS (pgautier@havea.com) + documentation du lot produit
3. Sinon : reponse adaptee au cas (redirection medecin/pharmacien + proposition d'echange ou remboursement selon contexte)
4. Noter le numero de lot et le produit pour detecter une recurrence

**Ne JAMAIS ecrire dans la reponse humaine** :
- "c'est normal" / "ne vous inquietez pas" / "c'est juste votre premiere prise"
- Des dosages, diagnostics, ou contre-indications non documentees officiellement
- Une minimisation du symptome ou du vecu client

---

## T13 -- Demarchage ambassadeur / partenariat (auto-send)

**Keywords** : `ambassadeur`, `partenariat`, `collaboration`, `collab`, `travailler ensemble`, `travailler avec vous`, `representer la marque`, `représenter la marque`, `je suis createur`, `je suis créateur`, `influenceur`, `influenceuse`, `sponsoring`, `sponsor`, `offre de collab`, `proposition de collab`

**Discriminant vs T9 merci** : si le message contient les deux (ex : "j'adore vos produits et je serais interessee pour collaborer"), T13 prime -- le vrai besoin c'est la collab, le merci est contextuel.

**Action** : auto-send la redirection vers Antoine sur Instagram. Pas de queue -- c'est pas du SAV, pas d'action serveur necessaire.

**Texte** :
```
Bonjour,

Merci pour votre message et votre interet pour Impulse Nutrition !

Le programme ambassadeur est gere directement par Antoine, notre Influence Manager, sur Instagram. Envoyez-lui un message sur notre compte @impulse_nutrition_fr, il reviendra vers vous pour la suite.

Belle journee,
L'equipe Impulse Nutrition
```

---

## T14 -- Commande double / annulation (auto-send + queue HIGH)

**Keywords** : `commande deux fois`, `commande 2 fois`, `double commande`, `commandé deux fois`, `commandé 2 fois`, `par erreur`, `clique deux fois`, `cliqué deux fois`, `annuler`, `annulation`, `annule ma commande`, `annuler ma commande`, `me suis trompe`, `me suis trompé`, `mauvaise quantite`, `mauvaise quantité`, `mauvais produit`, `trop commande`, `trop commandé`

**Discriminant vs T5 (adresse)** : T5 = modif adresse sur commande a conserver. T14 = annulation pure ou reduction quantite/produit.

**Discriminant vs T8 (retour/remboursement)** : T8 = retour apres reception parce que pas satisfait. T14 = annulation AVANT expedition (time-sensitive : si pas encore partie chez BigBlue, annulable ; si deja expediee, ca bascule en T8).

**Action** : auto-send une demande du numero de commande (gain de temps), puis ajouter a `queue.json` avec categorie `T14_CANCEL`, priorite `high`. Chaque minute compte avant que BigBlue expedie.

**Texte** :
```
Bonjour,

Merci pour votre message. Pourriez-vous nous indiquer le numero de commande concerne (IMPxxxx) afin que nous puissions verifier le statut et traiter votre demande d'annulation ?

Belle journee,
Le service client
```

**Workflow humain** :
1. Attendre la reponse du client avec le numero de commande
2. Fetch le statut BigBlue de la commande
3. Si `PENDING` / pas encore pris : `cancel_order` BigBlue + refund Shopify complet
4. Si `PROCESSING` / en prep : tenter `cancel_order` BigBlue (parfois trop tard), sinon prevenir le client qu'on ne peut plus intervenir et basculer en retour a reception
5. Si `SHIPPED` : expliquer au client, lui dire de refuser le colis a reception (qui reviendra = refund auto) ou organiser un retour classique
6. Repondre au client avec la decision + mention du refund

---

## Fallback -- UNKNOWN (aucun pattern matche)

**Declencheur** : aucun keyword reconnu, ou message tres court/ambigu.

**Action** :
1. Envoyer le T0 (ACK generique)
2. Ajouter a `queue.json` avec categorie `UNKNOWN`, priorite `medium`

**Workflow humain suggere** : lire le message, decider au cas par cas.

---

## Regles de classification (ordre de priorite)

Quand plusieurs patterns matchent, appliquer dans cet ordre :

1. **T12 Effet secondaire / intolerance** (symptomes corporels — prioritaire pour raison legale)
2. **T2 Damaged** (mots-cles de degradation physique)
3. **T10 Perime** (mots-cles DLC / peremption)
4. **T4 Missing** (mots-cles d'absence produit)
5. **T11 Colis livre mais pas recu** (mots-cles "livre" + "pas recu" combines)
6. **T14 Commande double / annulation** (mots-cles annulation — time-sensitive, avant que BigBlue expedie)
7. **T5 Address** (mots-cles adresse)
8. **T8 Refund** (mots-cles remboursement retour apres reception)
9. **T3 Code promo** (mots-cles code/promo)
10. **T1 Tracking** (mots-cles suivi, tracking en cours)
11. **T6 Delai** (mots-cles temps)
12. **T7 Produit** (mots-cles utilisation/composition)
13. **T13 Demarchage ambassadeur** (mots-cles collab/partenariat — prime sur T9 si les deux matchent)
14. **T9 Merci** (mots-cles positifs)
15. **UNKNOWN** (fallback)

## Comportement par template

**Tous les templates envoient un message au client.** Le T0 (ACK) est envoye par `sav.py`. Les T1-T9 sont envoyes par le skill. Le fallback s'appuie sur le T0 deja envoye.

La queue sert uniquement au traitement de suivi (code SAV, modification BigBlue, remboursement...), pas a decider si on repond ou non.

| Template | Queue apres envoi | Variantes |
|----------|-------------------|-----------|
| T0 | non (utilise comme fallback) | - |
| T1 | non | - |
| T2 | oui | A (sans photo) / B (avec photo) |
| T3 | non | - |
| T4 | oui | A (produit non precise) / B (produit precise) |
| T5 | seulement variante A | A (modifiable) / B (en preparation) / C (expediee) |
| T6 | non | - |
| T7 | seulement variante B | A (doc trouvee) / B (doc pas trouvee) |
| T8 | oui | A (raison non precisee) / B (raison precisee) |
| T9 | non | - |
| T10 | seulement variante B | A (DLC courte) / B (perime) |
| T11 | oui (T0 envoye, humain gere) | - |
| T12 | oui (T0 envoye, humain gere, priorite HIGH) | - |
| T13 | non | - |
| T14 | oui (priorite HIGH, time-sensitive) | - |
| Fallback | oui | - (T0 deja envoye) |
