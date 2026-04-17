# Workflow 02 — Dotation récurrente 4 mois structurée

> Contrat Dotation négocié après call avec un athlète pro / profil qualitatif. L'ambassadeur reçoit 2 codes : l'affilié (-15% pour sa communauté) + le dotation ([CODE]DOTATION utilisable une fois par mois pour redeem sa dotation). Session 17/04/2026 : **1 cas complet** (Yannick / @atiz06, ASICS Front Runner).

## Quand utiliser

- Call de négo préalable avec l'ambassadeur → accord sur contrat formel
- Profil qualitatif (pro athlète, communauté engagée, alignement fort)
- Enveloppe mensuelle typique : 100-150€ / mois sur 4 mois
- Cible d'utilisations du code affilié : ~4 par mois (= 16 sur 4 mois)
- Format libre côté partages (stories spontanées, pas de livrables contractuels stricts)

## Paramètres contrat standard

| Paramètre | Valeur typique | Négociable |
|---|---|---|
| Dotation mensuelle | 120€ | 80-200€ selon profil |
| Durée | 4 mois | 3-6 mois |
| Cible utilisations code affilié | 16 sur 4 mois (4/mois) | Proportionnel à durée |
| Format partages | Stories spontanées, format libre | Possibilité de spécifier stories/mois, reels/mois |
| Code affilié | `[HANDLE]` — -15% | Fixé |
| Code dotation | `[HANDLE]DOTATION` — fixed_amount €/mois | Fixé |

## Flow step-by-step

```
1. Call: discussion dotation, termes validés
2. DM récap: formaliser ce qu'on s'est dit (dotation M€ × D mois, cible N utilisations)
3. Ambassadeur confirme verbatim ("Exactement ! Validé")
4. [PARALLÈLE]
   ├─ Shopify: create_draft_order pour M1 (première dotation)
   ├─ Shopify: create_affiliate_code(HANDLE) → -15% ALEXTV pattern
   └─ Shopify: create_discount_code(HANDLEDOTATION) → dotation récurrente
5. Shopify: update_draft_order(discount 100% + shipping 0€)
6. Shopify: complete_draft_order → vraie commande M1
7. DM s5.5 adapté: commande validée + 2 codes (affilié + dotation) + mode d'emploi
8. Sheet: déplacer de Suivi_Amb → Suivi_Dot (nouvelle ligne avec toutes les colonnes contrat)
9. Sheet: marquer Suivi_Amb row comme "Déplacé Suivi_Dot"
```

## Paramètres techniques du code dotation

```python
create_discount_code(
    title="[HANDLE]DOTATION",
    code="[HANDLE]DOTATION",
    value=-120.0,                         # = enveloppe mensuelle en euros
    value_type="fixed_amount",
    usage_limit=4,                        # = nombre de mois
    once_per_customer=False,              # pour pouvoir utiliser chaque mois
    starts_at=None,                       # défaut = now
    ends_at="2026-08-17T23:59:59+02:00",  # début + D mois
    combines_order_discounts=False,
    combines_product_discounts=True,
    combines_shipping_discounts=True,
)
```

## Exemple — Yannick Clares (@atiz06, ASICS Front Runner)

### Contexte

- Triathlète (préparations Iron Man), stand Marathon Paris
- Call prévu 06/04 (loupé car férié), re-calé + eu lieu
- Ambassadeur de chez ASICS Front Runner
- Message récap envoyé par Antoine 15/04 21h05
- Validation reçue 15/04 21h54 : **"Exactement ! Validé"**
- Commande complétée 17/04

### Coordonnées

```
Yannick Clares
Cabinet dentaire, 5 avenue Jacques Mollet, 06340 La Trinité, France
Yannickclares@hotmail.fr
+33607330058
```

(Customer Shopify existait déjà id `25731031269707` avec email et phone. Juste adresse à vérifier.)

### Récap envoyé pendant le call (DM 15/04)

```
Yannick, my bad pour le retard sur la récap du call !

Pour formaliser ce qu'on s'est dit : on part sur une dotation de 120 € de produits par mois pendant 4 mois. De ton côté, on te crée un code perso et l'objectif commun c'est 16 utilisations du code sur les 4 mois, histoire qu'on ait un repère simple sur ce que ça génère.

Tu restes totalement libre sur le format des partages (stories spontanées comme tu préfères), et tu choisis tes produits chaque mois selon tes cycles prépa / course / récup.

Une fois que tu me valides tout ça, je te prépare ta commande direct et on lance la première dotation 😉

Sportivement,
Antoine
```

### Sélection M1 (Mois 1)

| Produit | Variant | Prix |
|---|---|---|
| Vitamine D3 | 51857627578699 | 15,90€ |
| Whey Isolate chocolat portion individuelle | 51857627775307 | 2,95€ |
| Whey Isolate vanille portion individuelle | 51860866761035 | 2,95€ |
| Whey Isolate nature | 51857627513163 | 37,90€ |
| Curcumine | 56072545272139 | 19,90€ |
| Oméga 3 EPAX® | 51887935258955 | 23,90€ |
| Magnésium Bisglycinate | 51870638997835 | 15,90€ |
| **Bonus** Shaker 750ml | 51956599652683 | 7,90€ |
| **Bonus** Bidon 750ml | 51956610367819 | 7,90€ |
| **Total** | | **135,20€ → 0€** |

### Actions Shopify (parallèles)

1. `create_draft_order(customer_id=25731031269707, line_items=[9 items], tag="Dotation influenceur")` → D754, 135,20€
2. `create_affiliate_code("ALTIZ")` → -15% ALEXTV pattern
3. `create_discount_code("ALTIZDOTATION", -120, fixed_amount, usage_limit=4, once_per_customer=False, ends_at="2026-08-17T23:59:59+02:00")`

Puis :
4. `update_draft_order(D754, discount 100%, shipping 0€)` → total 0€
5. `complete_draft_order(D754)` → order `#12576240730443`

### DM s5.5 adapté envoyé

```
Excuse-moi pour le temps de réponse !

Trop cool, on se lance ! 😊

Ta commande est validée avec ta sélection + un shaker 750ml et un bidon 750ml en bonus, elle sera expédiée très prochainement !

Je t'ai créé ton code affilié perso ALTIZ qui permettra à ta communauté de bénéficier de -15% sur tout le site (sans minimum, cumulable avec les promos). Pour ta dotation, tu auras ton code ALTIZDOTATION à utiliser une fois par mois pendant les 4 prochains mois pour tes 120€ de produits.

Code affilié : ALTIZ
Lien : https://impulse-nutrition.fr/discount/ALTIZ

Code dotation : ALTIZDOTATION
Lien : https://impulse-nutrition.fr/discount/ALTIZDOTATION

N'hésite pas si tu as des questions, à très vite !

Sportivement,
Antoine
```

### Sheet : migration vers Suivi_Dot

**Suivi_Dot ligne 31** (nouvelle) :

| Col | Valeur |
|---|---|
| A (Name) | Yann Clares |
| C (Statut Deal) | Actif |
| D (Type) | Dotation |
| E (Action/Com) | "Dotation 120€ × 4 mois validée 17/04. M1 envoyé order #12576240730443. Cible 16 utilisations ALTIZ sur période." |
| F (Mail) | Yannickclares@hotmail.fr |
| G (Numéro) | 0607330058 |
| H (Prénom) | Yann |
| I (Nom) | Clares |
| K (Code Dotation) | ALTIZDOTATION |
| M (Insta) | atiz06 |
| R (Code affilié) | ALTIZ |
| S (Util YTD) | 0 |
| Y (Début) | 17/04/2026 |
| Z (Fin) | 17/08/2026 |
| AA (Durée) | 4 mois |
| AB (Dotation €) | 120 |
| AC (Seuil renouvellement) | 16 |
| AF (Adresse) | Cabinet dentaire, 5 avenue Jacques Mollet, 06340 La Trinité |

**Suivi_Amb L307** (marquage) :
- J = "Déplacé Suivi_Dot"
- K = "Yannick Clares (ASICS Front Runner). Dotation 120€×4 mois validée 17/04 (call + récap). Déplacé en Suivi_Dot L31. Codes ALTIZ + ALTIZDOTATION créés."
- L = "good"

## Modalités d'utilisation du code dotation (à expliquer si demandé)

- Le code `[HANDLE]DOTATION` est à utiliser sur le site une fois par mois
- Il offre une réduction fixed_amount (ex: -120€) au panier
- Il suffit de mettre ~120€ de produits au panier et appliquer le code → panier à 0€
- Livraison gratuite appliquée automatiquement côté drafter (cumulable shipping)
- Renouvellement du contrat : par avenant si cible utilisations atteinte sur la période (non automatique)

## Red flags

- **Ne pas promettre la rémunération** — dotation = produits uniquement, pas de cash
- **Ne pas oublier `once_per_customer=False`** sur le code dotation (sinon utilisable qu'une fois)
- **`ends_at` bien fixé** = date fin contrat (évite qu'il utilise le code après la période négociée)
- **Tag `Dotation influenceur`** sur la commande M1 (comme pour toutes les commandes dotation)
- **Déplacer vers Suivi_Dot obligatoire** — sinon le prospect traîne en Suivi_Amb sans tracking contrat

## Cas d'évolution

- **Fin de contrat (mois 4)** : bilan utilisations. Si ≥ seuil (16) → proposer renouvellement, éventuellement upgrade Paid
- **Sous-performance** : si <16 utilisations en fin de contrat, non-reconduction ou discussion directe
- **Top performance** : ≥ 25-30 utilisations sur 4 mois → candidat Paid (`create_paid_affiliate_code`)

## Source de vérité

- `knowledge/voice/templates.yaml::s5_5_envoi_code` (base DM)
- `knowledge/operations.md#pattern-code-dotation-codedotation` (variante B récurrente)
- `knowledge/impulse.md#22-dotation-négociée` (contrat type Suivi_Dot)
