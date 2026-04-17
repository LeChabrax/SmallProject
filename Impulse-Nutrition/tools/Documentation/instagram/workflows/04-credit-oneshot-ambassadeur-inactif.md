# Workflow 04 — Crédit one-shot pour ambassadeur actif mais inactif commercialement

> L'ambassadeur partage activement du contenu (reel_mentions réguliers) mais son code affilié n'a pas encore été utilisé. On le soutient en créant un code dotation one-shot type 20€ pour qu'il puisse se réapprovisionner. Session 17/04/2026 : **1 cas** (Kiki / @une.patissiere.sportive).

## Quand utiliser

- Ambassadeur avec code affilié actif depuis quelques semaines/mois
- Partage régulier de contenu (reel_mentions, stories, posts) MAIS col O Suivi_Amb = 0 utilisations
- Moment opportun : événement sportif important à venir (course, marathon) ou besoin de réappro
- Geste commercial pour maintenir l'engagement

## Principe

- **Acknowledge positivement** le contenu partagé (pas de reproche sur les 0 utilisations)
- **Offrir un code dotation one-shot** de petite valeur (20€ typiquement)
- Message chaleureux centré sur le soutien, pas sur la performance
- Cumulable avec promos en cours

## Paramètres code

```python
create_discount_code(
    title="[HANDLE]DOTATION",
    code="[HANDLE]DOTATION",
    value=-20.0,                          # 20€ typique (négociable selon cas)
    value_type="fixed_amount",
    usage_limit=1,                        # one-shot
    once_per_customer=True,
    starts_at=None,                       # défaut now
    ends_at=None,                         # pas de date limite
    combines_order_discounts=False,
    combines_product_discounts=True,
    combines_shipping_discounts=True,
)
```

## Flow step-by-step

```
1. Identifier: Suivi_Amb col O = 0, mais contenu actif (reel_mentions, stories)
2. Déclencheur: événement sportif, période favorable, ou juste moment opportun
3. Shopify: create_discount_code([HANDLE]DOTATION, -20€, one-shot)
4. Sheet: update Suivi_Amb col P avec nom du code dotation
5. DM: message chaleureux + code + contexte sportif
```

## Exemple — Kiki / Christine Le Gagne (@une.patissiere.sportive)

### Contexte

- Ambassadrice active, code `KIKISPORTIVE` créé depuis plusieurs semaines
- **6 reel_mentions entre 20/03 et 10/04** (très active dans ses partages)
- Suivi_Amb L88 col O = **0 utilisations** (malgré son activité)
- Boston Marathon dans 4 jours (21/04/2026)
- Objectif personnel : 6⭐ Abbott World Marathon Majors (Boston + Berlin + Chicago + Tokyo + London + NYC)
- Après Boston : Cape Town + Sydney

### Déclencheur

Elle partage :
- "Je vais tester votre gel sur mon marathon de Boston" (reel_share 16/04)
- "Merci je vais chercher la 6⭐"
- "Je suis partie avec la maltodextrine et les électrolytes et les vitamines pour être en forme"
- "Et la whey pour les muscles pour la récup"

→ Occasion parfaite pour un geste commercial.

### Actions Shopify

```python
mcp__shopify_orders__create_discount_code(
    title="KIKISPORTIVEDOTATION",
    code="KIKISPORTIVEDOTATION",
    value=-20,
    value_type="fixed_amount",
    usage_limit=1,
    once_per_customer=True,
    combines_order_discounts=False,
    combines_product_discounts=True,
    combines_shipping_discounts=True,
)
```

Résultat : price_rule id `2218021290315`, code créé `KIKISPORTIVEDOTATION`.

### Sheet update

```
Suivi_Amb L88:
  P (code_credit) = "KIKISPORTIVEDOTATION"
  K (note) = "Ambassadrice très active (reel_mentions Mar-Apr 2026). Prépare Boston (21/04) + vise 6⭐ Abbott (Cape Town + Sydney à suivre). Code affilié KIKISPORTIVE = 0 utilisations. Code dotation KIKISPORTIVEDOTATION (-20€) créé 17/04 pour soutien saison."
```

### DM envoyé (verbatim)

```
Trop bien comme objectif la 6⭐, tu vas tout déchirer à Boston !! 🔥

De notre côté, on a envie de te soutenir à fond pour cette saison. Même si ton code n'a pas encore été utilisé, on a vraiment beaucoup apprécié tout le contenu que tu as partagé ces dernières semaines, c'est super cool.

Du coup, on t'a créé un code perso KIKISPORTIVEDOTATION qui te donne 20€ offerts sur ta prochaine commande (cumulable avec les promos et la livraison offerte), pour que tu puisses bien te préparer pour Boston et la suite.

Code : KIKISPORTIVEDOTATION
Lien : https://impulse-nutrition.fr/discount/KIKISPORTIVEDOTATION

Bonne course, et hâte d'entendre ton débrief !!

Sportivement,
Antoine
```

## Structure du message (généralisable)

```
[1. Acknowledge positif projet/événement sportif] + emoji 🔥

[2. Pivot "on te soutient" sans reproche sur 0 utilisations]
"Même si ton code n'a pas encore été utilisé, on a vraiment beaucoup apprécié tout le contenu que tu as partagé ces dernières semaines, c'est super cool."

[3. Offre concrète du code dotation one-shot]
"Du coup, on t'a créé un code perso [HANDLE]DOTATION qui te donne 20€ offerts sur ta prochaine commande (cumulable avec les promos et la livraison offerte), pour que tu puisses bien [contexte sportif]."

[4. Code + lien]
Code : [HANDLE]DOTATION
Lien : https://impulse-nutrition.fr/discount/[HANDLE]DOTATION

[5. Closing chaleureux + invitation retour]
"Bonne [course/saison/événement], et hâte d'entendre ton [débrief/retour] !!"

[Signature Sportivement, Antoine]
```

## Évolutions du draft (leçons session)

### v1 (initiale — rejetée)
"Petit point de mon côté : je vois que ton code KIKISPORTIVE n'a pas encore été utilisé par ta communauté..."

→ **Rejeté par Antoine** : commencer par "Petit point" + formulation directe "n'a pas été utilisé" = effet reproche

### v3 (finale — envoyée)
Ouverture par encouragement Boston → pivot soutien avec acknowledge contenu → offre code

→ **Leçon** : toujours ouvrir par la positivité / l'événement sportif. Les "0 utilisations" doivent être mentionnées mais pas dramatisées ("même si" est le bon connecteur).

## Red flags

| Red flag | Conséquence |
|---|---|
| Commencer par la notation des 0 utilisations | Effet reproche, désagréable |
| "Petit point" / "petite info" en ouverture | Ton trop pro / froid |
| Code > 20€ sans justification (cas spécifique) | Dérive budgétaire |
| Oublier de mentionner "cumulable avec les promos" | Cause friction à l'utilisation |
| Ne pas faire référence à son événement sportif | Message générique, perte d'impact |

## Variantes possibles

- **Cas ambassadeur ayant utilisé quelques fois mais pas assez** : même pattern mais ton peut être plus franc sur l'objectif
- **Cas solde accumulé (col O > col Q)** : au lieu d'un one-shot 20€, créer un code dotation avec montant = `(O-Q)×20€` (workflow différent, cf memory `reference_contract_types.md`)

## Source de vérité

- `knowledge/operations.md#pattern-code-dotation-codedotation` (variante A one-shot)
- `knowledge/operations.md#calculer-et-redeem-le-crédit-ambassadeur` (formule crédit si multiple uses)
- [conventions/code-naming.md](../conventions/code-naming.md) (pattern `[CODE]DOTATION`)
