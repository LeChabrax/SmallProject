# DM Decision Tree — Bibliothèque procédurale Instagram

Decision tree + bibliothèque de templates **réels** pour répondre aux DMs
Instagram en respectant le ton d'Antoine.

> Source de cette doc : combinaison de l'onglet `Message_type` du Sheet
> (templates curés à la main par Antoine) et du corpus de conversations
> téléchargé en 2026-04-13 dans `data/conversations/*.json`.
>
> À régénérer périodiquement avec `scripts/extract_response_templates.py`
> + revue manuelle pour fusionner avec les nouveaux templates Sheet.

---

## 0. Règles de tone (rappel)

- **Tutoiement systématique**. Toujours `tu`, jamais `vous`.
- **Signature** : `Sportivement, Antoine` (sur les longs messages ≥ 3 phrases) ou `Antoine` ou `Antoine - Impulse Nutrition`. Sur les micro-messages, pas de signature.
- **Emojis modérés** : 0 à 2 par message. Favoris (corpus 2026-04-13) : 😊 😍 ☺ 😉 🔥 😁 💪. Éviter 🙏 ✨ (ressentis comme mielleux).
- **Pas de tirets em** (`—`). Phrases courtes.
- **Pas d'attaque par "Bonjour"** dans une conversation déjà ouverte. Réserver à un premier contact.
- **Pas de re-listing exhaustif des produits** dans une conversation déjà avancée — info concrète, pas de surcharge.

Détails et stats : [`../instagram_dm_mcp/personality.md`](../instagram_dm_mcp/personality.md)
(auto-régénéré par `scripts/extract_tone.py`).

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

- ❌ Vouvoyer
- ❌ Signer "Antoine" ou "Sportivement, Antoine" sur un canal autre qu'Instagram
- ❌ Utiliser des tirets em (`—`)
- ❌ Re-coller le pitch ambassadeur dans une conversation déjà avancée
- ❌ Promettre des choses non confirmées (livraison J+1, gratuit illimité, etc.)
- ❌ Oublier d'inclure le `{prenom}` dans un premier message
- ❌ Inclure des emojis "mielleux" : 🙏 ✨ 💖
- ❌ Surcharger en 🔥 ou 💪 (max 1 par message)

---

## 11. See also

- [`../instagram_dm_mcp/personality.md`](../instagram_dm_mcp/personality.md) — guide auto-généré, stats détaillées
- [`../templates/dm_response_guide.md`](../templates/dm_response_guide.md) — guide manuel historique
- [`../templates/real_response_examples.md`](../templates/real_response_examples.md) — exemples anonymisés auto-générés
- [`process_calculate_credits.md`](process_calculate_credits.md) — calcul du solde crédit
- Onglet Sheet `Message_type` — source primaire des templates ci-dessus
