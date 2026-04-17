# Templates de réponse — Gorgias

Chargé par `/gorgias` à l'**Étape 5 (Classification + template)** et utilisé comme base du draft à l'**Étape 6 (Carte de décision)**.

**Persona** : entité **Impulse Nutrition**, vouvoiement formel, signature `Cordialement,\nLe service client Impulse Nutrition` (ou variante). **❌ Jamais** signer "Antoine" / "Sportivement" / humain.

**Règles transversales** (appliquées à tous les templates) :
- Vouvoiement systématique
- **Jamais** de tirets em (`—`)
- **Jamais** de délais chiffrés (`48-72h`, `sous 24h`) → `"dès que nous avons du nouveau"`, `"dans les plus brefs délais"`
- **Jamais** de formules creuses (`"nous vous remercions de votre confiance"`, `"votre satisfaction est notre priorité"`, `"nous vous avons bien reçu"`)
- Emojis rares — uniquement `😊` sur contexte positif
- Longueur medium : 4-8 lignes utiles

**Règle ouverture** : si ce n'est pas le premier échange sur le ticket et que le client a relancé, éviter "Bonjour {Prénom}," et ouvrir plus direct : `"{Prénom},"` ou aller au contenu.

**Excuse retard** : si le ticket date de plus de 4 jours sans réponse SC → excuse légère en tête (`"nous vous prions de nous excuser pour le délai de réponse"`). Plus de 10 jours → excuse appuyée.

**Placeholders courants** :
- `{prenom}` — prénom client (si vide → `Bonjour,`)
- `{order_id}` — ex : `IMP7077`
- `{point_relais}` — ex : `REFERENCE PARE BRISE` + code postal + ville
- `{tracking_url}` — URL suivi transporteur
- `{amount}` — montant remboursement / crédit
- `{produits}` — line items courts

---

## G0 — waiting_customer_reply (skip, pas de template)

**Tags déclencheurs** : N/A
**Règle** : `last_message.from_agent == true` ET `last_message.sender.address != "contact@impulse-nutrition.fr" avec body auto-ack`

**Action** : skip automatique, carte condensée 1 ligne, pas de draft.

---

## G1 — SAV colis bloqué

**Tags déclencheurs** : `statut_commande`, `urgent`, `retour commande`
**Keywords client** : "bloqué", "pas reçu", "disparu", "jamais arrivé", "en attente depuis", "aucun scan", tracking loop
**Enrichissement requis** : `mcp__bigblue__get_tracking(order_id)` + `mcp__bigblue__get_order(order_id)` + Shopify `get_order` pour shipping_address
**Action mécanique** : ligne `BigBlue_Actions` "A faire" via `add_rows` (topic = `Investigate a delayed order` ou `Investigate a delivery never received by the customer` selon statut)

### Variante A — Colis AVAILABLE_FOR_PICKUP (client pense pas reçu)

Cas : client a ouvert ticket mais le colis est en fait dispo au point relais (notif SMS/email pas vue).

```
Bonjour {prenom},

Merci pour votre message et désolés pour l'inquiétude.

Votre commande {order_id} a bien été livrée au point relais et vous y attend :

{point_relais}

Vous avez dû recevoir une notification par SMS ou email de la part du transporteur. Voici le lien de suivi pour confirmer : {tracking_url}

N'hésitez pas à nous recontacter si vous avez la moindre question.

Belle journée,
Le service client Impulse Nutrition
```

### Variante B — IN_TRANSIT sans scan depuis plus de 7 jours

Cas : tracking figé, transporteur muet. Action : claim BigBlue.

```
Bonjour {prenom},

Merci pour votre message et désolés pour l'attente subie sur votre commande {order_id}.

Après vérification, votre colis est bloqué chez le transporteur depuis le {date_dernier_scan}, sans nouveau scan depuis. Nous ouvrons aujourd'hui une enquête auprès du transporteur pour comprendre ce qui se passe.

Nous revenons vers vous dès que nous avons du nouveau.

Encore toutes nos excuses pour ce contretemps.

Cordialement,
Le service client Impulse Nutrition
```

### Variante C — LOST / aucun scan depuis l'expédition

Cas : colis perdu confirmé par enquête BigBlue. Proposer renvoi OU remboursement.

```
Bonjour {prenom},

Merci pour votre patience sur le suivi de votre commande {order_id}.

Malheureusement, après enquête auprès du transporteur, votre colis est considéré comme perdu. Nous vous présentons toutes nos excuses pour ce désagrément.

Deux options pour régler la situation :
- Un renvoi complet de votre commande à votre adresse en livraison directe (sans point relais), offert
- Un remboursement intégral sur votre moyen de paiement initial

Dites-nous ce que vous préférez et nous traitons la suite dès que nous avons votre retour.

Cordialement,
Le service client Impulse Nutrition
```

---

## G2 — SAV produit cassé / manquant

**Tags déclencheurs** : `retour commande`, `urgent`, `retour/echange`
**Keywords client** : "cassé", "abîmé", "endommagé", "manquant", "pas dans le colis", "fuite", "fondu", "moisi"
**Enrichissement requis** : Shopify `get_order` (line items, variant_ids) + photos si jointes au ticket
**Action mécanique** : BigBlue claim via ligne `BigBlue_Actions` (topic = `Report damaged products` ou `Report missing products`) + replacement draft Shopify (discount 100% SAV + shipping 0€ + tag `Service client`)

### Variante A — Produit cassé, photos jointes

```
Bonjour {prenom},

Merci pour votre message et désolés d'apprendre que votre {produit} vous est parvenu endommagé.

Nous avons bien reçu vos photos, votre demande est prise en charge. Nous lançons dès maintenant un renvoi du produit concerné à votre adresse, et vous le recevrez dans les plus brefs délais.

Toutes nos excuses pour ce désagrément.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Produit cassé, pas de photo

```
Bonjour {prenom},

Merci pour votre message et désolés d'apprendre que votre {produit} vous est parvenu endommagé.

Pour que nous puissions traiter votre demande au plus vite, pourriez-vous nous envoyer une ou deux photos du produit concerné ainsi que du colis à la réception ?

Dès réception, nous lançons un renvoi du produit à votre adresse.

Cordialement,
Le service client Impulse Nutrition
```

### Variante C — Produit manquant dans le colis

```
Bonjour {prenom},

Merci pour votre message et désolés pour cet oubli sur votre commande {order_id}.

Nous vérifions en interne avec notre entrepôt et lançons un renvoi du produit manquant à votre adresse. Vous le recevrez dans les plus brefs délais.

Toutes nos excuses pour ce désagrément.

Cordialement,
Le service client Impulse Nutrition
```

---

## G3 — SAV returned to sender (retour expéditeur)

**Tags déclencheurs** : `retour commande`, `bigblue-action-required`
**Keywords client** : "retourné", "point relais fermé", "refusé", "pas pu récupérer", Mondial Relay / Chronopost retour expéditeur
**Enrichissement requis** : BigBlue `get_order(order_id)` pour statut RETURNED + Shopify pour shipping_address
**Action mécanique** : attendre choix client entre refund et reship home (wait customer response)

### Variante A — Proposer refund OU reship home

```
Bonjour {prenom},

Merci pour votre message et désolés du désagrément sur la livraison de votre commande {order_id}.

Nous constatons que votre colis nous a été retourné par le transporteur. Deux options pour la suite :

- Un renvoi de votre commande à votre domicile en livraison directe (sans point relais), offert
- Un remboursement intégral sur votre moyen de paiement initial

Dites-nous ce que vous préférez et nous lançons la suite dès réception de votre retour.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Reship home confirmé + geste commercial

```
Bonjour {prenom},

Parfait, nous lançons la réexpédition de votre commande à votre adresse ({shipping_address}) en livraison directe, sans point relais. Pour le désagrément, nous ajoutons un petit geste commercial dans votre colis (bidon + shaker).

Vous recevrez un nouveau lien de suivi dès l'expédition.

Cordialement,
Le service client Impulse Nutrition
```

---

## G4 — SAV partial return (retour partiel / refund partiel)

**Tags déclencheurs** : `retour commande`, `retour/echange`
**Keywords client** : "retour d'un produit", "rembourser un article", Shopify `financial_status=partially_refunded`, BigBlue `RETURNED`
**Enrichissement requis** : Shopify `get_order` → vérifier `refunds` array
**Action mécanique** : si refund déjà processé côté Shopify → confirmer montant. Sinon → refund manuel via Shopify admin UI (MCP refund pas implémenté).

```
Bonjour {prenom},

Merci pour votre message concernant votre commande {order_id}.

Nous confirmons la réception de votre retour partiel. Le remboursement de {amount} € a été traité sur votre moyen de paiement initial et devrait apparaître sur votre compte dans les jours ouvrés qui suivent.

N'hésitez pas à nous recontacter si vous ne voyez pas le crédit apparaître.

Cordialement,
Le service client Impulse Nutrition
```

---

## G5 — SAV bad rating BigBlue

**Tags déclencheurs** : `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`
**Enrichissement requis** : `mcp__bigblue__get_support_ticket` pour lire le commentaire BigBlue (si tag `with-comment`)
**Action mécanique** : reply Gorgias (pas BigBlue), close quand répondu. Si le client a laissé un vrai motif → proposer un discount code.

### Variante A — Commentaire présent avec motif concret

```
Bonjour {prenom},

Nous avons pris connaissance de votre retour suite à la livraison de votre commande {order_id}, et nous vous en remercions.

{reformulation_courte_du_motif_en_1_phrase}

Nous sommes désolés que votre expérience ait été en-deçà de nos standards et nous prenons votre remarque en compte. En guise d'excuse, nous vous offrons le code **{code_promo}** qui vous donnera {montant_discount} sur votre prochaine commande.

N'hésitez pas à revenir vers nous si vous souhaitez nous en dire plus.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Pas de commentaire (rating sec)

```
Bonjour {prenom},

Nous avons bien vu votre retour suite à la livraison de votre commande {order_id}. Afin de comprendre ce qui n'a pas été et de progresser, pourriez-vous nous en dire un peu plus sur ce qui vous a déplu ?

Votre retour nous aide à améliorer notre service.

Cordialement,
Le service client Impulse Nutrition
```

---

## G6 — SAV remboursement demandé

**Tags déclencheurs** : `retour commande`, `retour/echange`, `annulation / remboursement`
**Keywords client** : "remboursement", "refund", "annulation après livraison", "je veux être remboursé"
**Enrichissement requis** : Shopify `get_order` (date commande, items, conditions retour 14 jours)
**Action mécanique** : si éligible → refund manuel Shopify admin UI + reply confirmation. Si hors conditions → expliquer + proposer échange/avoir.

### Variante A — Éligible (dans les 14 jours, produit renvoyé)

```
Bonjour {prenom},

Merci pour votre message.

Nous confirmons l'éligibilité de votre demande de remboursement pour la commande {order_id}. Nous procédons au remboursement intégral de {amount} € sur votre moyen de paiement initial.

Vous devriez voir le crédit apparaître sur votre compte dans les jours ouvrés qui suivent.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Hors conditions (au-delà de 14 jours ou produit entamé)

```
Bonjour {prenom},

Merci pour votre message concernant la commande {order_id}.

Malheureusement, votre demande sort de nos conditions de retour (14 jours à réception, produit non entamé). Nous ne sommes donc pas en mesure de procéder au remboursement sur cette commande.

Si cela peut vous aider, nous pouvons vous proposer un code de réduction sur votre prochaine commande. N'hésitez pas à nous dire ce que vous préférez.

Cordialement,
Le service client Impulse Nutrition
```

---

## G7 — Question statut commande

**Tags déclencheurs** : `statut_commande`
**Keywords client** : "où est ma commande", "tracking", "quand je reçois", "numéro de suivi", "pas reçu l'email de suivi"
**Enrichissement requis** : Shopify `get_order` pour `fulfillment_status` + BigBlue `get_tracking` pour statut détaillé
**Action mécanique** : reply seul. ❌ **Jamais** de délai chiffré.

### Variante A — Commande en préparation (pas encore expédiée)

```
Bonjour {prenom},

Merci pour votre patience sur votre commande {order_id}. Celle-ci est actuellement en préparation dans notre entrepôt et partira dès que possible.

Vous recevrez automatiquement un email de suivi avec le numéro de tracking dès l'expédition.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Commande expédiée, en transit

```
Bonjour {prenom},

Merci pour votre message. Votre commande {order_id} a bien été expédiée et est actuellement en transit chez le transporteur.

Voici le lien de suivi pour consulter l'état en temps réel : {tracking_url}

N'hésitez pas à nous recontacter si vous avez la moindre question.

Cordialement,
Le service client Impulse Nutrition
```

---

## G8 — Question produit / conseil routine

**Tags déclencheurs** : `Produit`
**Keywords client** : "dosage", "allergène", "goût", "composition", "compatible", "vegan", "sans gluten", "routine", "conseil", "que me conseillez-vous"
**Enrichissement requis** : `knowledge/catalog.yaml` pour composition + `knowledge/impulse.md#4-catalogue-produits`
**Action mécanique** : reply seul. Si doute technique → escalader à l'équipe produit.

```
Bonjour {prenom},

Merci pour votre message et pour l'intérêt que vous portez à nos produits.

{reponse_technique_produit}

N'hésitez pas si vous avez d'autres questions, nous sommes là pour vous orienter.

Belle journée,
Le service client Impulse Nutrition
```

---

## G9 — Question code affilié

**Tags déclencheurs** : `code promo`, `affiliatly`
**Keywords client** : "mon code ne marche pas", "mes crédits", "Affiliatly", "je suis ambassadeur", "20€ crédit"
**Enrichissement requis** : Étape 3 cross-check `find_in_spreadsheet` sur `Suivi_Amb`/`Suivi_Dot`/`Suivi_Paid`
**Action mécanique** : si ambassadeur → **STOP draft SC**, signaler à Antoine. Si non-ambassadeur → orienter vers conditions codes welcome.

### Variante A — Ambassadeur confirmé

**Pas de template. Signaler à Antoine via la carte de décision.**
```
### Action manuelle requise — Ambassadeur détecté
Ticket SAV de {prenom}, qui est ambassadeur ({tab}, statut {J}).
→ Décision Antoine : tu réponds toi-même ou j'envoie une réponse SC standard ?
```

### Variante B — Non-ambassadeur, pense l'être ou mélange

```
Bonjour {prenom},

Merci pour votre message.

Le programme ambassadeur Impulse Nutrition est réservé aux créateurs de contenu que nous avons invités à rejoindre le programme via Instagram. Si vous souhaitez postuler, vous pouvez nous envoyer un DM sur @impulse_nutrition_fr avec un aperçu de votre profil.

Pour les codes de réduction classiques, ils sont communiqués régulièrement via notre newsletter et sur nos réseaux sociaux.

Belle journée,
Le service client Impulse Nutrition
```

---

## G10 — Question frais de port / livraison

**Tags déclencheurs** : `statut_commande` (pré-achat)
**Keywords client** : "frais de port", "livraison gratuite", "Expédition gratuite dès 49€", "international", "Belgique", "Espagne", "Suisse"
**Enrichissement requis** : aucun (info fixe)
**Action mécanique** : reply seul.

### Variante A — France métropolitaine (seuil franco)

```
Bonjour {prenom},

Merci pour votre message.

La livraison gratuite s'applique à partir de 49€ d'achat en France métropolitaine. En dessous de ce montant, les frais de port standards s'appliquent en fonction du mode de livraison choisi (point relais ou domicile).

N'hésitez pas si vous avez d'autres questions.

Belle journée,
Le service client Impulse Nutrition
```

### Variante B — International (Belgique, Suisse, Espagne, autres)

```
Bonjour {prenom},

Merci pour votre message et désolés pour cette surprise au moment de finaliser votre commande.

L'offre de livraison gratuite à partir de 49€ s'applique uniquement aux commandes livrées en France métropolitaine. Pour les envois hors France, les frais de port correspondent au tarif standard de nos transporteurs vers la zone concernée.

Nous prenons bonne note de votre retour pour voir comment rendre cette information plus claire sur le site.

N'hésitez pas à nous recontacter si vous avez d'autres questions.

Cordialement,
Le service client Impulse Nutrition
```

---

## G11 — Modification d'adresse

**Tags déclencheurs** : `modifier adresse`, `changement commande`
**Keywords client** : "changer adresse", "je me suis trompé d'adresse", "mauvaise adresse"
**Enrichissement requis** : Shopify `get_order` pour `fulfillment_status` (null/partial = pre-ship, fulfilled = post-ship)
**Action mécanique** : pre-ship → `mcp__shopify__update-order`. Post-ship → `mcp__bigblue__update_order` pour re-routing.

### Variante A — Pré-expédition (commande pas encore partie)

```
Bonjour {prenom},

Merci pour votre message. Votre commande {order_id} n'étant pas encore expédiée, nous avons bien mis à jour votre adresse vers :

{nouvelle_adresse}

La commande partira vers cette nouvelle adresse dès la prochaine vague d'expéditions.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Post-expédition (déjà partie, tentative de re-routing)

```
Bonjour {prenom},

Merci pour votre message concernant la commande {order_id}.

Malheureusement, votre commande est déjà partie en livraison à l'ancienne adresse. Nous allons tenter un re-routing auprès du transporteur vers votre nouvelle adresse, mais cela dépend de l'avancement du colis.

Nous revenons vers vous dès que nous avons un retour du transporteur.

Cordialement,
Le service client Impulse Nutrition
```

---

## G12 — Annulation de commande

**Tags déclencheurs** : `annulation / remboursement`, `commande_annulee`
**Keywords client** : "annuler", "stop", "je voudrais annuler", "changement d'avis"
**Enrichissement requis** : Shopify `get_order` pour `fulfillment_status`
**Action mécanique** : pre-ship → `mcp__shopify__update-order` avec cancellation + refund. Post-ship → expliquer + retour à réception.

### Variante A — Pré-expédition (annulation possible)

```
Bonjour {prenom},

Merci pour votre message. Votre commande {order_id} n'étant pas encore expédiée, nous l'avons bien annulée et procédons au remboursement intégral de {amount} € sur votre moyen de paiement initial.

Vous devriez voir le crédit apparaître sur votre compte dans les jours ouvrés qui suivent.

Cordialement,
Le service client Impulse Nutrition
```

### Variante B — Post-expédition (trop tard)

```
Bonjour {prenom},

Merci pour votre message.

Malheureusement, votre commande {order_id} avait déjà été préparée et expédiée au moment où nous avons reçu votre demande d'annulation. Elle est donc en route vers votre point relais (ou adresse).

Nous vous demandons de ne pas aller la récupérer : elle nous sera automatiquement renvoyée passé le délai de mise en instance, et nous traiterons votre remboursement dès réception.

Pourriez-vous nous indiquer la raison de votre annulation ? Cela nous aide à mieux comprendre et à améliorer notre service.

Cordialement,
Le service client Impulse Nutrition
```

---

## G13 — Double charge / paiement

**Tags déclencheurs** : `paiement`
**Keywords client** : "débité deux fois", "fraude", "transactions multiples", "deux prélèvements"
**Enrichissement requis** : Shopify `get_order` → `transactions` array + nombre de commandes client
**Action mécanique** : **ESCALADE ANTOINE** — refund manuel via Shopify admin UI si vraie double charge.

```
### Action manuelle requise — Double charge suspectée
Ticket {ticket_id} de {prenom} : signale deux prélèvements.
Contexte Shopify : {nb_transactions} transaction(s), montant {amount} €, order {order_id}.
→ Décision Antoine : vérifier Shopify admin → transactions, refund manuel si double charge confirmée, ou expliquer autorisation bancaire normale.
```

(Pas de draft auto. Antoine traite au cas par cas.)

---

## G14 — Partenariat refus (small creator / sponsoring event petite marque)

**Tags déclencheurs** : `partenariats`
**Keywords client** : "collaboration", "UGC", "ambassadeur", "sponsoring", "goodies", "dotation", "partenariat", créateurs < 2k followers, invitations trail / événements locaux
**Enrichissement requis** : vérifier profil Insta si handle donné (`mcp__instagram_veille__get_user_info`) pour voir le follower_count
**Action mécanique** : refus poli + (option) code ACHAB25 pour qu'ils testent quand même.

### Variante A — UGC / petit créateur (refus + code ACHAB25)

```
Bonjour {prenom},

Merci pour votre message et pour l'intérêt que vous portez à Impulse Nutrition.

Nous recevons beaucoup de demandes de collaboration et ne sommes pas en mesure de donner suite à toutes. Nous gardons votre profil bien noté et nous reviendrons vers vous si une opportunité correspond à nos prochaines campagnes.

En attendant, nous serions ravis de vous faire découvrir notre gamme : voici le code **ACHAB25** qui vous donnera 25% de réduction sur votre première commande sur impulse-nutrition.fr.

Belle journée,
Le service client Impulse Nutrition
```

### Variante B — Sponsoring event petite marque (refus avec regret)

```
Bonjour {prenom},

Merci pour votre retour et pour l'intérêt que vous portez à Impulse Nutrition.

On aurait vraiment aimé pouvoir contribuer à votre événement, le projet nous plaît beaucoup. Malheureusement, nous sommes encore une petite marque et n'avons pas investi dans des goodies / budget sponsoring à ce jour, donc nous ne pouvons pas répondre favorablement pour cette édition.

Nous vous souhaitons une excellente édition et gardons votre projet en mémoire pour de futures collaborations si l'occasion se présente.

Belle journée,
Le service client Impulse Nutrition
```

---

## G15 — Partenariat redirect (Pierre ou équipe partenariats)

**Tags déclencheurs** : `partenariats`, `compte client`
**Keywords client** : "salon", "exposant", "festival", "distribution", "retail", "pharmacie", "B2B", "agence influence" avec gros profils
**Enrichissement requis** : taille de l'event / du profil (si > 2k followers ou event > 10k visiteurs → redirect Pierre)
**Action mécanique** : redirect Pierre Gautier (`pgautier@havea.com`) ou refus selon contexte.

### Variante A — Redirect Pierre (partenariat sponsoring / event / B2B)

```
Bonjour {prenom},

Merci pour votre message et pour cette proposition.

Pour ce type de partenariat, la bonne personne à contacter chez nous est Pierre Gautier : pgautier@havea.com. N'hésitez pas à lui renvoyer votre dossier directement, il pourra étudier votre proposition et revenir vers vous.

Belle journée,
Le service client Impulse Nutrition
```

### Variante B — Refus distribution pharmacie / B2B hors stratégie

```
Bonjour {prenom},

Merci pour votre message et pour l'intérêt que vous portez à Impulse Nutrition.

À date, nous ne prévoyons pas de développer notre distribution sur ce canal. Nous vous remercions néanmoins pour votre proposition et vous souhaitons une belle continuation.

Belle journée,
Le service client Impulse Nutrition
```

---

## G16 — Candidature RH / stage / emploi

**Tags déclencheurs** : `candidature`
**Keywords client** : "stage", "emploi", "recrutement", "CV", "candidature spontanée", "école d'ingénieur", "alternance", "apprentissage", "master", "AgroParisTech", "dev commercial", rôle pro mentionné
**Enrichissement requis** : ne pas escalader ambassadeur si keywords RH présents (priorité RH)
**Action mécanique** : **ESCALADE ANTOINE** par défaut. Selon décision Antoine : redirect RH / refus poli / clin d'œil personnalisé si école commune.

### Variante A — Redirect RH générique (décision Antoine = "forwarder")

```
Bonjour {prenom},

Merci pour votre message et pour l'intérêt que vous portez à Impulse Nutrition.

Impulse Nutrition fait partie du groupe Havea. Pour toute candidature, nous vous invitons à envoyer votre CV et lettre de motivation directement à l'adresse rh@havea.com, qui centralise les recrutements du groupe.

Nous vous souhaitons bonne chance dans votre recherche.

Belle journée,
Le service client Impulse Nutrition
```

### Variante B — Refus poli (décision Antoine = "pas de besoin ouvert")

```
Bonjour {prenom},

Merci pour votre message et pour l'intérêt que vous portez à Impulse Nutrition.

Votre profil est intéressant, mais nous n'avons pas de besoin ouvert correspondant à ce type de poste ou de mission pour le moment. Nous gardons votre candidature en mémoire et reviendrons vers vous si une opportunité se présente à l'avenir.

Nous vous souhaitons une belle continuation dans votre recherche.

Belle journée,
Le service client Impulse Nutrition
```

### Variante C — Clin d'œil personnalisé (même école / profil très pertinent)

Template 3e personne pour garder persona entité SC (pas de "je"/"moi" qui désignerait Antoine) :

```
Bonjour {prenom},

Merci pour votre message et pour l'intérêt que vous portez à Impulse Nutrition.

Impulse Nutrition fait partie du groupe Havea. Bonne nouvelle : {connexion_perso_3e_personne, ex: "notre Influence Manager, qui est également diplômé d'AgroParisTech"}, va transférer votre candidature aux RH avec un petit mot pour voir ce qui peut être envisagé côté stage.

Nous revenons vers vous dès que nous avons du nouveau. Bonne continuation à l'école 😊

Belle journée,
Le service client Impulse Nutrition
```

→ **Toujours créer un reminder** dans `tools/reminder/followups.md` pour que l'Influence Manager n'oublie pas de forwarder.

---

## G17 — Bascule Insta DM (ambassadeur qui pose questions)

**Tags déclencheurs** : `partenariats` + customer dans `Suivi_Amb` / `Suivi_Dot` / `Suivi_Paid` OU message explicite sur le programme ambassadeur après premier contact Gorgias signé "Antoine"
**Keywords client** : "fréquence de publication", "produits à mettre en avant", "objectifs code", continuation thread Antoine-signé
**Enrichissement requis** : profil Insta (`mcp__instagram_veille__get_user_info`) pour récupérer handle + follower_count
**Action mécanique** : reply Gorgias court + envoi DM Insta avec vraies réponses (passer par skill `/instagram-dm` pour la suite).

### Template Gorgias (bascule, ton tu/Antoine pour continuité)

Exception persona assumée : si le précédent reply du même thread est déjà signé "Antoine" / tutoiement, on garde la continuité.

```
Hello {prenom},

Super content que le programme te parle ! Pour aller plus loin et discuter plus simplement, je te bascule en DM Instagram dans la foulée : je te réponds à toutes tes questions directement là-bas.

À tout de suite,
Sportivement,
Antoine
```

→ Laisser ticket Gorgias **open** (pas de close), et envoyer ensuite le DM Insta via `mcp__instagram_dms__send_message` avec un contenu ambassadeur détaillé (voir skill `/instagram-dm` pour le protocole).

---

## Ordre d'application

À l'Étape 5 de `/gorgias`, choisir la catégorie G# en suivant **strictement** l'ordre de priorité défini dans `categorization.md#ordre-de-priorité`. Puis sélectionner la **variante** en fonction de l'enrichissement Étape 3-4 (profil ambassadeur, statut BigBlue, présence photo, conditions retour, etc.).

Si aucune variante ne match parfaitement → partir de la variante la plus proche et adapter dans la carte de décision à l'Étape 6 avec le contexte du ticket. Toujours garder le **squelette** (structure + signature + persona) et adapter uniquement le contenu métier.

**Règle finale** : même avec template prêt, **toujours wait "go" explicite** avant `reply_to_ticket`. Les templates sont des brouillons, pas des envois automatiques.
