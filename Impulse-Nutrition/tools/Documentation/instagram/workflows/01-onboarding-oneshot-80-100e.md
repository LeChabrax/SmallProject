# Workflow 01 — Onboarding ambassadeur one-shot 80-100€

> Le flow le plus fréquent. Ambassadeur accepte le pitch s2/s4, envoie sa sélection + coordonnées, on lui prépare une commande gratuite one-shot + son code affilié. Session 17/04/2026 : **3 cas complétés** (Simon, Thomas Bonnot, Maxime Croisé).

## Quand utiliser

- Le prospect a accepté le pitch s2/s4 et veut tester les produits
- Communauté <20k followers (→ enveloppe 80€) ou entre 20k-30k (→ enveloppe 100€)
- Pas de négociation paid / pas de dotation récurrente demandée
- Flux standard "découverte" avant potentielle évolution vers dotation structurée

## Flow step-by-step

```
1. DM: acceptation reçue
2. DM s5v: demande sélection + adresse + email + tel
3. Prospect envoie sélection + coordonnées
4. [PARALLÈLE]
   ├─ Shopify: search_customers → create_draft_order → (patch customer si blank)
   └─ Shopify: create_affiliate_code(name=HANDLE) → code -15% type ALEXTV
5. Shopify: update_draft_order(discount 100% + shipping gratuite)
6. Shopify: complete_draft_order → vraie commande #IMPxxxx
7. DM s5.5: commande validée + code affilié + lien
8. Sheet: update Suivi_Amb L<row>: J=Ambassadeur, N=<CODE>, note K complète
```

## Exemple 1 — Simon Gauthier (@fitby.simon)

### Contexte
- Parqué PGAU25 en novembre 2025 (<10k follow à l'époque)
- Re-engagé suite à rencontre au stand Run Expérience 13/04/2026
- Upgradé en vrai ambassadeur 15/04 après échange salon
- Adresse/email/tel donnés le 15/04
- Sélection envoyée le 16/04 matin
- Commande complétée **17/04**

### Coordonnées récupérées du thread

```
Simon Gauthier
5b rue Antoine Chantin, 75014 Paris, France
fitbysimon.contact@gmail.com
+33678390039
```

### Sélection prospect

> "Je pense partir sur ces produits : Avant : maltodextrine + preworkout / Pendant : Boisson d'effort fruit rouge / Après : Créatine"

### Sélection finale (avec bonus)

| Produit | Variant | Prix |
|---|---|---|
| Maltodextrine | 51857627742539 | 11,90€ |
| Preworkout citron | 51857627644235 | 37,90€ |
| Boisson d'effort fruits rouges | 51857625481547 | 21,90€ |
| Créatine Creapure® | 51857627808075 | 12,90€ |
| **Bonus** Shaker 750ml | 51956599652683 | 7,90€ |
| **Bonus** Bidon 750ml | 51956610367819 | 7,90€ |
| **Bonus** Multivitamines | 51857627480395 | 18,90€ |
| **Bonus** Vitamine C | 51794418106699 | 12,90€ |
| **Total** | | **132,20€ → 0€** |

### Actions Shopify

1. `search_customers("fitbysimon.contact@gmail.com")` → aucun résultat
2. `create_draft_order(customer_email=...)` → D753, customer blank créé id `25839325151563`
3. `update-customer(id=25839325151563, email, firstName="Simon", lastName="Gauthier", phone)` → patch blank
4. `update_draft_order(D753, discount 100%, shipping 0€)` → total 0€
5. `complete_draft_order(D753)` → order `#12574919229771`, status completed
6. `create_affiliate_code("FITBYSIMON")` → code -15% actif

### DM s5.5 envoyé (verbatim)

```
La commande est validée et sera expédiée très prochainement !

Je t'ai créé un code affilié perso (FITBYSIMON) qui permettra à ta communauté de bénéficier de -15% sur tout le site (sans minimum d'achat). Le code est cumulable avec toutes les autres réductions sur les produits.

Si les produits te plaisent et que tu en parles autour de toi, tu cumuleras 20€ de crédit à chaque commande passée avec ton code, utilisables pour renouveler tes stocks quand tu veux.

Code : FITBYSIMON
Lien : https://impulse-nutrition.fr/discount/FITBYSIMON

N'hésite pas si tu as des questions, à très vite !

Sportivement,
Antoine
```

### DM de confirmation (avant s5.5, en réponse à sa sélection)

```
Yes c'est parfait Simon, ta sélection est top et bien pensée !

Pour les gélules, pas de souci, tu pourras totalement les tester dans un second temps avec les crédits que tu débloqueras sur tes futures commandes (20€ à chaque commande passée avec ton code). Et on va te rajouter quelques produits en bonus sur cette première commande pour que tu puisses déjà découvrir un peu plus la gamme 😉

Je lance la préparation de ton côté, tu devrais recevoir ça très prochainement !

Sportivement,
Antoine
```

### Sheet update post-commande

```
Suivi_Amb L1018:
  J (statut) = "Ambassadeur"
  K (note) = "Dotation validée + commande complétée 17/04. Order Shopify #12574919229771 (ex-D753, 132,20€ > 0€). Code FITBYSIMON créé (-15%). Customer Simon Gauthier (id 25839325151563). Code envoyé en DM 17/04."
  L (priorité) = "good"
```

---

## Exemple 2 — Thomas Bonnot (@thms_bnnt)

### Contexte
- Athlète équipe France athlétisme, 1 sélection EDF
- Pitché 06/09/2025 → refusé plusieurs fois (communauté trop petite)
- Objectif fixé fin février 2026 : atteindre 3000 abonnés d'ici fin mai + plus actif
- **A dépassé l'objectif plus tôt que prévu** (14/04/2026)
- Accepté le programme le 14/04
- Sélection + coordonnées envoyées 15/04
- Commande complétée 17/04

### Coordonnées (du link message qu'il a envoyé)

```
Bonnot Thomas
41 rue de la Galopaz, 73000 Chambéry, France
thomasbonnot73@gmail.com
+33762890125
```

### Sélection finale

| Produit | Variant | Prix | Note |
|---|---|---|---|
| Peptides de collagène Peptan® exotique | 51857628004683 | 25,90€ | Sa demande |
| Whey Isolate chocolat | 51887753003339 | 39,90€ | Sa demande |
| Preworkout citron | 51857627644235 | 37,90€ | Sa demande |
| Boisson d'effort fruits rouges | 51857625481547 | 21,90€ | Sa demande |
| Électrolytes pêche | 51870634475851 | 15,90€ | Bonus (il avait demandé whey recovery mais Antoine a switch) |
| Shaker 750ml | 51956599652683 | 7,90€ | Bonus |
| Bidon 750ml | 51956610367819 | 7,90€ | Bonus |
| **Total** | | **157,30€ → 0€** | |

### Actions Shopify

- `search_customers` → aucun résultat
- Draft D755 → 157,30€
- Patch customer id `25841117200715` (firstName, lastName, email, phone)
- Discount 100% + shipping 0€
- Complete → order `#12576584335691`
- `create_affiliate_code("THOMASBNT")`

### Sheet update

Nouvelle ligne **Suivi_Amb L1023** créée (n'existait pas auparavant) : username + URL + statut Ambassadeur + note complète + nom/prénom/email + 3,0 k followers + date 17/04/2026.

---

## Exemple 3 — Maxime Croisé (@maximecroise) — **cas Belgique**

### Contexte
- Magicien + triathlète Iron Man 70.3 Vichy + Malaga 2026
- Inbound via Gorgias 15/04
- Passage stand Marathon Paris vendredi 11/04
- Accepté le programme 15/04 après call
- Sélection proposée par nous 17/04 → il valide immédiatement + envoie ses coordonnées

### Coordonnées (Belgique !)

```
Maxime Croisé
Avenue des perdrix 42, 1410 Waterloo, Belgique
events@maximecroise.com
+32478787785
```

### Sélection finale (proposée par nous, validée par lui)

| Produit | Variant | Prix |
|---|---|---|
| Whey Recovery chocolat | 51870639489355 | 39,90€ |
| Électrolytes pêche | 51870634475851 | 15,90€ |
| Boisson d'effort fruits rouges | 51857625481547 | 21,90€ |
| Multivitamines | 51857627480395 | 18,90€ |
| Barre protéinée chocolat | 51870635032907 | 10,90€ |
| Shaker 750ml (bonus) | 51956599652683 | 7,90€ |
| Bidon 750ml (bonus) | 51956610367819 | 7,90€ |
| **Total** | | **123,30€ → 0€** |

### Spécificités Belgique

- Customer existant Shopify (id `25834383180107`, tag `swell_vip_athlete`) mais first_name/last_name/phone null → patch immédiat
- `country_code: "BE"` dans shipping_address → Shopify calcule TVA BE correctement (6% produits compléments, 21% accessoires)
- Fulfillment BigBlue : vérifié OK pour la Belgique (non testé encore mais Shopify accepte)

### Actions Shopify

- `search_customers("events@maximecroise.com")` → customer existe, id récupéré
- `update-customer(firstName, lastName, phone)` → patch meta
- `create_draft_order(customer_id=..., shipping_address=BE...)` → D757 123,30€
- Discount 100% + shipping 0€
- Complete → order `#12576626671947`
- `create_affiliate_code("MAXIMEC")`

### DM s5.5 envoyé

```
La commande est validée et sera expédiée très prochainement !

Je t'ai créé ton code affilié perso (MAXIMEC) qui permettra à ta communauté de bénéficier de -15% sur tout le site (sans minimum d'achat). Le code est cumulable avec toutes les autres réductions sur les produits.

Si les produits te plaisent et que tu en parles autour de toi, tu cumuleras 20€ de crédit à chaque commande passée avec ton code, utilisables pour renouveler tes stocks quand tu veux.

Code : MAXIMEC
Lien : https://impulse-nutrition.fr/discount/MAXIMEC

N'hésite pas si tu as des questions, à très vite !

Sportivement,
Antoine
```

### Sheet update

```
Suivi_Amb L1019:
  J = "Ambassadeur"
  K = "Magicien + triathlète IM 70.3 Vichy+Malaga, Belgique (Waterloo). Lead Gorgias 15/04 > stand salon Marathon Paris. Sélection validée 17/04 (...). Order #12576626671947. Code MAXIMEC envoyé."
  L = "good"
  N = "MAXIMEC"
  AD (Nom) = "Croisé"
  AE (Prénom) = "Maxime"
  AF (Email) = "events@maximecroise.com"
```

---

## Template DM s5.5 verbatim (source : `knowledge/voice/templates.yaml::s5_5_envoi_code`)

```
La commande est validée et sera expédiée très prochainement !

Je t'ai créé un code affilié perso ({CODE}) qui permettra à ta communauté de bénéficier de -15% sur tout le site (sans minimum d'achat). Le code est cumulable avec toutes les autres réductions sur les produits.

Si les produits te plaisent et que tu en parles autour de toi, tu cumuleras 20€ de crédit à chaque commande passée avec ton code, utilisables pour renouveler tes stocks quand tu veux.

Code : {CODE}
Lien : https://impulse-nutrition.fr/discount/{CODE}

N'hésite pas si tu as des questions, à très vite !

Sportivement,
Antoine
```

**Variables** : `{CODE}` = code affilié créé (ex: FITBYSIMON, MAXIMEC, THOMASBNT).

## Red flags

- **Oublier le tag `Dotation influenceur`** sur le draft → CA faussé HCS
- **Créer le customer via `customer_email` sans patcher ensuite** → `draft.email=null` permanent, emails Shopify pas envoyés (incident Dylan 15/04/2026)
- **Bonus sans validation** : par défaut shaker + bidon OK ; au-delà demander à Antoine
- **Enveloppe dépassée** : 132-157€ au lieu de 80-100€ acceptable si bonus justifiés, au-delà flag
- **Belgique / hors FR** : vérifier `country_code` ET que BigBlue peut ship dans ce pays
- **Saveurs non précisées** : par défaut chocolat (whey recovery, barre), fruits rouges (boisson), pêche (électrolytes), citron (preworkout)

## Source de vérité

- `knowledge/voice/templates.yaml::s5_5_envoi_code`
- `knowledge/operations.md#créer-un-draft-order`
- Memory `feedback_sav_draft_order_defaults` (règle discount 100% + shipping 0€)
- Memory `feedback_draft_order_customer_id` (incident Dylan)
