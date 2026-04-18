# Templates de reponse -- Gorgias

Charge par `/gorgias` a l'Etape 5 (Classification + template) et utilise comme base du draft a l'Etape 6 (Carte de decision).

**Persona** : entite **Impulse Nutrition**, vouvoiement formel, signature `Belle journee,\nLe service client`. **Jamais** signer "Antoine" / "Sportivement" / humain (sauf G17).

**Regles transversales** (appliquees a tous les templates) :
- Vouvoiement systematique
- **Jamais** de tirets em
- **Jamais** de "desoles" -> utiliser "navres" si excuse necessaire
- **Jamais** de delais chiffres (`48-72h`, `sous 24h`) -> `"des que nous avons du nouveau"`, `"dans les plus brefs delais"`
- **Jamais** de formules creuses (`"nous vous remercions de votre confiance"`, `"votre satisfaction est notre priorite"`)
- Signature : `Belle journee,\nLe service client` (sans "Impulse Nutrition")
- Longueur courte : aller droit au fait, pas d'emballage inutile

**Regle ouverture** : si ce n'est pas le premier echange et que le client a relance, ouvrir plus direct : `"{prenom},"` ou aller au contenu.

**Excuse retard** : si le ticket date de plus de 4 jours sans reponse SC -> excuse legere en tete. Plus de 10 jours -> excuse appuyee.

**Placeholders courants** :
- `{prenom}` -- prenom client (si vide -> `Bonjour,`)
- `{order_id}` -- ex : `IMP7077`
- `{point_relais}` -- ex : `REFERENCE PARE BRISE` + code postal + ville
- `{tracking_url}` -- URL suivi transporteur
- `{amount}` -- montant remboursement / credit
- `{produit}` -- nom du produit concerne
- `{adresse_livraison}` -- adresse complete (domicile ou point relais)
- `{nouvelle_adresse}` -- nouvelle adresse demandee par le client
- `{adresse_retour}` -- adresse de retour entrepot
- `{compliment_profil}` -- compliment personnalise genere par le skill
- `{compliment_event}` -- compliment sur l'evenement genere par le skill
- `{connexion_perso_3e_personne}` -- lien personnel 3e personne (ex: "Notre Influence Manager, egalement diplome de...")
- `{reponse_technique_produit}` -- reponse produit generee a partir de la doc
- `{reformulation_courte_du_motif_en_1_phrase}` -- reformulation du motif bad rating
- `{code_promo}` -- code promo genere
- `{montant_discount}` -- montant de la reduction
- `{date_dernier_scan}` -- date du dernier scan tracking

---

## G0 -- waiting_customer_reply (skip, pas de template)

**Regle** : `last_message.from_agent == true` ET `last_message.sender.address != "contact@impulse-nutrition.fr" avec body auto-ack`

**Action** : skip automatique, carte condensee 1 ligne, pas de draft.

---

## G1 -- SAV colis bloque

**Tags declencheurs** : `statut_commande`, `urgent`, `retour commande`
**Keywords client** : "bloque", "pas recu", "disparu", "jamais arrive", "en attente depuis", "aucun scan", tracking loop
**Enrichissement requis** : `mcp__bigblue__get_tracking(order_id)` + `mcp__bigblue__get_order(order_id)` + Shopify `get_order` pour shipping_address

### Variante A -- Colis AVAILABLE_FOR_PICKUP (client pense pas recu)

```
Bonjour {prenom},

Merci pour votre message.

Bonne nouvelle, votre commande {order_id} est arrivee et vous attend au point relais suivant :

{point_relais}

Voici le lien de suivi pour localiser votre colis : {tracking_url}

N'hesitez pas si vous avez la moindre question.

Belle journee,
Le service client
```

### Variante B -- IN_TRANSIT sans scan depuis plus de 7 jours

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Nous constatons que le suivi est bloque depuis le {date_dernier_scan}. Nous avons contacte le transporteur pour debloquer la situation et revenons vers vous des que nous avons du nouveau.

Belle journee,
Le service client
```

### Variante C1 -- LOST / colis perdu, renvoi d'office (defaut)

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Apres verification aupres du transporteur, votre colis est malheureusement considere comme perdu. Nous sommes vraiment navres pour cette situation.

Nous lancons immediatement un renvoi complet de votre commande a l'adresse suivante, offert :

{adresse_livraison}

Vous recevrez un nouveau lien de suivi des l'expedition.

Belle journee,
Le service client
```

### Variante C2 -- LOST / colis perdu, proposer le choix renvoi/remboursement

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Apres verification aupres du transporteur, votre colis est malheureusement considere comme perdu. Nous sommes vraiment navres pour cette situation.

Pour y remedier, nous vous proposons deux options :
- Un renvoi complet de votre commande a {adresse_livraison}, offert
- Un remboursement integral sur votre moyen de paiement initial

Dites-nous ce que vous preferez et nous traitons cela immediatement.

Belle journee,
Le service client
```

---

## G2 -- SAV produit casse / manquant

**Tags declencheurs** : `retour commande`, `urgent`, `retour/echange`
**Keywords client** : "casse", "abime", "endommage", "manquant", "pas dans le colis", "fuite", "fondu", "moisi"
**Enrichissement requis** : Shopify `get_order` (line items, variant_ids) + photos si jointes au ticket
**Action mecanique** : BigBlue claim via ligne `BigBlue_Actions` + replacement draft Shopify (discount 100% SAV + shipping 0€ + tag `Service client`)

### Variante A -- Produit casse, photos jointes

```
Bonjour {prenom},

Merci pour votre message. Nous sommes navres que votre {produit} vous soit parvenu en mauvais etat.

Nous avons bien recu vos photos et lancons un renvoi du produit a votre adresse, que vous recevrez dans les plus brefs delais.

Belle journee,
Le service client
```

### Variante B -- Produit casse, pas de photo

```
Bonjour {prenom},

Merci pour votre message. Nous sommes navres que votre {produit} vous soit parvenu en mauvais etat.

Pourriez-vous nous envoyer des photos du produit afin que nous puissions traiter votre demande ?

Belle journee,
Le service client
```

### Variante C -- Produit manquant dans le colis

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Nous verifions aupres de notre entrepot les produits expedies et revenons vers vous rapidement avec une solution.

Belle journee,
Le service client
```

---

## G3 -- SAV returned to sender (retour expediteur)

**Tags declencheurs** : `retour commande`, `bigblue-action-required`
**Keywords client** : "retourne", "point relais ferme", "refuse", "pas pu recuperer", Mondial Relay / Chronopost retour expediteur
**Enrichissement requis** : BigBlue `get_order(order_id)` pour statut RETURNED + Shopify pour shipping_address

### Variante A -- Proposer refund OU reship

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Votre colis nous a ete retourne par le transporteur. Pour la suite, nous vous proposons deux options :

- Un renvoi de votre commande a {adresse_livraison}, offert
- Un remboursement integral sur votre moyen de paiement initial

Dites-nous ce que vous preferez et nous traitons cela immediatement.

Belle journee,
Le service client
```

### Variante B -- Reship confirme + geste commercial

```
Bonjour {prenom},

C'est note, nous lancons le renvoi de votre commande a {adresse_livraison}.

Nous ajoutons egalement un petit cadeau dans votre colis pour nous faire pardonner. Vous recevrez un nouveau lien de suivi des l'expedition.

Belle journee,
Le service client
```

---

## G4 -- SAV partial return (retour partiel / refund partiel)

**Tags declencheurs** : `retour commande`, `retour/echange`
**Keywords client** : "retour d'un produit", "rembourser un article", Shopify `financial_status=partially_refunded`, BigBlue `RETURNED`
**Enrichissement requis** : Shopify `get_order` -> verifier `refunds` array

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Nous avons bien recu votre retour et le remboursement de {amount} € a ete traite sur votre moyen de paiement initial. Il apparaitra sur votre compte sous quelques jours ouvres.

N'hesitez pas si vous avez la moindre question.

Belle journee,
Le service client
```

---

## G5 -- SAV bad rating BigBlue

**Tags declencheurs** : `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`
**Enrichissement requis** : `mcp__bigblue__get_support_ticket` pour lire le commentaire BigBlue (si tag `with-comment`)

### Variante A -- Commentaire present avec motif concret

```
Bonjour {prenom},

Merci pour votre retour sur votre commande {order_id}.

{reformulation_courte_du_motif_en_1_phrase}

Nous prenons votre remarque en compte. En guise d'excuse, voici le code **{code_promo}** qui vous donnera {montant_discount} sur votre prochaine commande.

N'hesitez pas a nous en dire plus si vous le souhaitez.

Belle journee,
Le service client
```

### Variante B -- Pas de commentaire (rating sec)

```
Bonjour {prenom},

Merci pour votre retour sur votre commande {order_id}.

Nous avons bien note votre avis. Pourriez-vous nous en dire un peu plus sur ce qui ne vous a pas convenu ? Votre retour nous est precieux pour nous ameliorer.

Belle journee,
Le service client
```

---

## G6 -- SAV remboursement demande

**Tags declencheurs** : `retour commande`, `retour/echange`, `annulation / remboursement`
**Keywords client** : "remboursement", "refund", "annulation apres livraison", "je veux etre rembourse"
**Enrichissement requis** : Shopify `get_order` (date commande, items, conditions retour 14 jours)

### Variante A -- Eligible (dans les 14 jours, produit renvoye)

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Votre demande de remboursement est bien prise en charge. Le montant de {amount} € sera credite sur votre moyen de paiement initial sous quelques jours ouvres.

N'hesitez pas si vous avez la moindre question.

Belle journee,
Le service client
```

### Variante B -- Hors conditions (au-dela de 14 jours ou produit entame)

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Malheureusement, nous ne sommes pas en mesure de proceder au remboursement car la demande depasse le delai de retour de 14 jours a reception.

En revanche, nous pouvons vous proposer un code de reduction sur votre prochaine commande. Dites-nous si cela vous interesse.

Belle journee,
Le service client
```

---

## G7 -- Question statut commande

**Tags declencheurs** : `statut_commande`
**Keywords client** : "ou est ma commande", "tracking", "quand je recois", "numero de suivi", "pas recu l'email de suivi"
**Enrichissement requis** : Shopify `get_order` pour `fulfillment_status` + BigBlue `get_tracking` pour statut detaille

### Variante A -- Commande en preparation (pas encore expediee)

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Votre commande est actuellement en cours de preparation et sera expediee prochainement. Vous recevrez un email avec le numero de suivi des l'expedition.

Belle journee,
Le service client
```

### Variante B -- Commande expediee, en transit

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Votre commande a bien ete expediee. Voici le lien de suivi : {tracking_url}

N'hesitez pas si vous avez la moindre question.

Belle journee,
Le service client
```

---

## G8 -- Question produit / conseil routine

**Tags declencheurs** : `Produit`
**Keywords client** : "dosage", "allergene", "gout", "composition", "compatible", "vegan", "sans gluten", "routine", "conseil"
**Enrichissement requis** : `knowledge/catalog/` pour composition

```
Bonjour {prenom},

Merci pour votre message.

{reponse_technique_produit}

N'hesitez pas si vous avez d'autres questions.

Belle journee,
Le service client
```

---

## G9 -- Question code affilie

**Tags declencheurs** : `code promo`, `affiliatly`
**Keywords client** : "mon code ne marche pas", "mes credits", "Affiliatly", "je suis ambassadeur", "20€ credit"
**Enrichissement requis** : cross-check `find_in_spreadsheet` sur `Suivi_Amb`/`Suivi_Dot`/`Suivi_Paid`

### Variante A -- Ambassadeur confirme

**Escalade Antoine. Pas de template.**
```
### Action manuelle requise -- Ambassadeur detecte
Ticket SAV de {prenom}, qui est ambassadeur ({tab}, statut {J}).
-> Decision Antoine : tu reponds toi-meme ou j'envoie une reponse SC standard ?
```

### Variante B1 -- Non-ambassadeur, demande un code promo

```
Bonjour {prenom},

Merci pour votre message.

Nos ambassadeurs partagent leurs codes de reduction sur leurs reseaux sociaux. N'hesitez pas a consulter les comptes Instagram de nos athletes pour en trouver un.

Belle journee,
Le service client
```

### Variante B2 -- Non-ambassadeur, veut rejoindre le programme

```
Bonjour {prenom},

Merci pour votre message.

Pour toute demande concernant le programme ambassadeur, nous vous invitons a nous contacter directement en DM sur notre compte Instagram @impulse_nutrition_fr.

Belle journee,
Le service client
```

---

## G10 -- Question frais de port / livraison

**Tags declencheurs** : `statut_commande` (pre-achat)
**Keywords client** : "frais de port", "livraison gratuite", "international", "Belgique", "Espagne", "Suisse"

### Variante A -- France metropolitaine (seuil franco)

```
Bonjour {prenom},

Merci pour votre message.

La livraison est offerte a partir de 49€ d'achat en France metropolitaine. En dessous, les frais de port varient selon le mode de livraison choisi (point relais ou domicile).

N'hesitez pas si vous avez d'autres questions.

Belle journee,
Le service client
```

### Variante B -- International

```
Bonjour {prenom},

Merci pour votre message.

L'offre de livraison gratuite a partir de 49€ s'applique uniquement en France metropolitaine. Pour les envois hors France, les frais de port correspondent aux tarifs standard de nos transporteurs vers votre zone.

N'hesitez pas si vous avez d'autres questions.

Belle journee,
Le service client
```

---

## G11 -- Modification d'adresse

**Tags declencheurs** : `modifier adresse`, `changement commande`
**Keywords client** : "changer adresse", "je me suis trompe d'adresse", "mauvaise adresse"
**Enrichissement requis** : Shopify `get_order` pour `fulfillment_status`

### Variante A -- Pre-expedition (pas encore partie)

```
Bonjour {prenom},

Merci pour votre message. Votre commande {order_id} n'etant pas encore expediee, nous avons mis a jour l'adresse de livraison :

{nouvelle_adresse}

Vous recevrez un email de suivi des l'expedition.

Belle journee,
Le service client
```

### Variante B -- Post-expedition (deja partie)

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Votre commande est malheureusement deja en cours de livraison. Nous contactons le transporteur pour tenter de rediriger votre colis vers la nouvelle adresse.

Nous revenons vers vous des que nous avons un retour.

Belle journee,
Le service client
```

---

## G12 -- Annulation de commande

**Tags declencheurs** : `annulation / remboursement`, `commande_annulee`
**Keywords client** : "annuler", "stop", "je voudrais annuler", "changement d'avis"
**Enrichissement requis** : Shopify `get_order` pour `fulfillment_status`

### Variante A -- Pre-expedition (annulation possible)

```
Bonjour {prenom},

Merci pour votre message. Votre commande {order_id} a bien ete annulee et le remboursement de {amount} € sera credite sur votre moyen de paiement initial sous quelques jours ouvres.

N'hesitez pas si vous avez la moindre question.

Belle journee,
Le service client
```

### Variante B1 -- Post-expedition, point relais

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Malheureusement, votre commande a deja ete expediee. Si vous ne souhaitez plus la recevoir, vous pouvez simplement ne pas aller la recuperer au point relais. Le colis nous sera retourne automatiquement et nous procederons au remboursement des reception.

Belle journee,
Le service client
```

### Variante B2 -- Post-expedition, domicile

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Malheureusement, votre commande a deja ete expediee a votre domicile. Si vous souhaitez nous la retourner, confirmez-le nous et nous vous enverrons une etiquette de retour. Le remboursement sera effectue des reception du colis.

Belle journee,
Le service client
```

---

## G13 -- Double charge / paiement (escalade Antoine)

**Tags declencheurs** : `paiement`
**Keywords client** : "debite deux fois", "fraude", "transactions multiples", "deux prelevements"
**Enrichissement requis** : Shopify `get_order` -> `transactions` array

**Escalade Antoine. Pas de template.**
```
### Action manuelle requise -- Double charge suspectee
Ticket {ticket_id} de {prenom} : signale deux prelevements.
Contexte Shopify : {nb_transactions} transaction(s), montant {amount} €, order {order_id}.
-> Decision Antoine : verifier Shopify admin -> transactions, refund manuel si double charge confirmee.
```

---

## G14 -- Partenariat refus (small creator / sponsoring event)

**Tags declencheurs** : `partenariats`
**Keywords client** : "collaboration", "UGC", "ambassadeur", "sponsoring", "goodies", "dotation", "partenariat"
**Enrichissement requis** : verifier profil Insta si handle donne (`mcp__instagram_veille__get_user_info`)

### Variante A -- UGC / petit createur (refus + code ACHAB25)

```
Bonjour {prenom},

Merci pour votre message et pour votre interet pour Impulse Nutrition. {compliment_profil}

Nous ne sommes malheureusement pas en mesure de donner suite a votre demande pour le moment.

En revanche, voici le code **ACHAB25** qui vous donnera 25% de reduction sur votre premiere commande sur impulse-nutrition.fr. N'hesitez pas a nous faire vos retours si vous testez nos produits !

Belle journee,
Le service client
```

### Variante B -- Sponsoring event (refus)

```
Bonjour {prenom},

Merci pour votre message et pour cette proposition. {compliment_event}

Nous ne sommes malheureusement pas en mesure de participer pour le moment. Nous vous souhaitons une excellente edition.

Belle journee,
Le service client
```

---

## G15 -- Partenariat redirect (Pierre ou refus B2B)

**Tags declencheurs** : `partenariats`, `compte client`
**Keywords client** : "salon", "exposant", "festival", "distribution", "retail", "pharmacie", "B2B", "agence influence"

### Variante A -- Redirect Pierre (partenariat sponsoring / event / B2B)

```
Bonjour {prenom},

Merci pour votre message et pour cette proposition.

Pour ce type de partenariat, nous vous invitons a contacter directement Pierre Gautier a l'adresse pgautier@havea.com. Il pourra etudier votre proposition et revenir vers vous.

Belle journee,
Le service client
```

### Variante B -- Refus distribution / B2B hors strategie

```
Bonjour {prenom},

Merci pour votre message et pour votre interet pour Impulse Nutrition.

Nous ne prevoyons pas de developpement sur ce canal pour le moment. Merci neanmoins pour votre proposition et belle continuation.

Belle journee,
Le service client
```

---

## G16 -- Candidature RH / stage / emploi (escalade Antoine)

**Tags declencheurs** : `candidature`
**Keywords client** : "stage", "emploi", "recrutement", "CV", "candidature spontanee", "alternance", "apprentissage"

**Escalade Antoine. Pas de template.** Chaque candidature est traitee au cas par cas.

---

## G17 -- Bascule Insta DM / ambassadeur sur Gorgias (escalade Antoine)

**Tags declencheurs** : `partenariats` + customer dans `Suivi_Amb`/`Suivi_Dot`/`Suivi_Paid`
**Keywords client** : "frequence de publication", "produits a mettre en avant", "objectifs code"

**Escalade Antoine. Pas de template.** La bascule Gorgias -> Instagram depend du contexte.

---

## Ordre d'application

A l'Etape 5 de `/gorgias`, choisir la categorie G# en suivant l'ordre de priorite defini dans `categorization.md#ordre-de-priorite`. Puis selectionner la **variante** en fonction de l'enrichissement Etape 3-4 (profil ambassadeur, statut BigBlue, presence photo, conditions retour, etc.).

Si aucune variante ne match parfaitement -> partir de la variante la plus proche et adapter dans la carte de decision a l'Etape 6 avec le contexte du ticket. Toujours garder le **squelette** (structure + signature + persona) et adapter uniquement le contenu metier.

**Regle finale** : meme avec template pret, **toujours wait "go" explicite** avant `reply_to_ticket`. Les templates sont des brouillons, pas des envois automatiques.
