# Runbook — Créer et compléter un draft order dotation (Shopify)

> Recette complète copier-collable. Utilisée 5 fois le 17/04/2026 (Simon, Yannick, Thomas, Maxime, Alexia en attente). 100% de succès après intégration du patch customer.

## Quand utiliser

- Ambassadeur accepte une dotation → on prépare sa commande gratuite
- Redeem de crédit accumulé (→ utiliser `[CODE]DOTATION` one-shot)
- Envoi M1-M4 de dotation récurrente (→ utiliser `[CODE]DOTATION` récurrent)

## Flow en 6 étapes

### 1. Rechercher le customer existant

```python
mcp__shopify_orders__search_customers(query="email@exemple.com")
```

**2 branches** :

- **Customer existe** → récupérer `id`, passer `customer_id=<int>` à `create_draft_order`. Vérifier que `email`, `first_name`, `last_name`, `phone` sont set. Patch si manquants.
- **Customer n'existe pas** → passer `customer_email` à `create_draft_order` (crée un customer blank). **Patch immédiat obligatoire** après (étape 3) car `draft.email=null` sinon.

### 2. Créer le draft order

```python
mcp__shopify_orders__create_draft_order(
    line_items=[
        {"variant_id": 51857627742539, "quantity": 1},  # Maltodextrine
        {"variant_id": 51857627644235, "quantity": 1},  # Preworkout citron
        # ... etc
    ],
    customer_id=25731031269707,                         # OU customer_email si nouveau
    shipping_address={
        "first_name": "Yann",
        "last_name": "Clares",
        "address1": "5 Avenue Jacques Mollet",
        "city": "La Trinité",
        "zip": "06340",
        "country": "France",
        "country_code": "FR",
        "phone": "+33607330058",
    },
    note="Dotation M1/4 @atiz06 (Yannick Clares). Sélection: ... Bonus: ... Contrat 120€×4 mois.",
    tags="Dotation influenceur",                        # CRITIQUE
    use_customer_default_address=True,                  # si customer existe et adresse OK
)
```

**Retour** : `{"draft_order": {"id": 1655399514443, "name": "#D754", "email": "...", "total_price": "135.20", ...}}`

**Vérifier** : `draft.email` != `null`. Si null, patcher customer (étape 3).

### 3. Patch customer (si blank)

Si le draft a été créé avec `customer_email` (customer blank) :

```python
mcp__shopify__update-customer(
    id="25839325151563",                                # numeric, pas gid
    email="fitbysimon.contact@gmail.com",
    firstName="Simon",
    lastName="Gauthier",
    phone="+33678390039",
)
```

**⚠️ Incident connu** : après ce patch, `draft.email` peut **rester null** dans la réponse de `get_draft_order`, mais `draft.customer.email` est correct. L'email passe bien à la commande finale après `complete_draft_order`. Vérifiable post-complétion.

### 4. Appliquer discount 100% + shipping gratuit

```python
mcp__shopify_orders__update_draft_order(
    draft_order_id=1655399514443,
    applied_discount={
        "title": "Dotation",                            # ou "SAV" pour SAV
        "value_type": "percentage",
        "value": "100.0",
        "description": "Dotation ambassadeur M1",       # contextualiser
    },
    shipping_line={
        "title": "Expédition gratuite",
        "price": "0.00",
    },
)
```

**Retour** : `total_price: "0.00"` après update. ✅

### 5. Compléter le draft → vraie commande

```python
mcp__shopify_orders__complete_draft_order(
    draft_order_id=1655399514443,
    payment_pending=False,                              # marquée payée (total 0€)
)
```

**Retour** : `status: "completed"`, `order_id: 12576240730443`.

### 6. Créer le code affilié (parallèle possible dès étape 1)

```python
mcp__shopify_orders__create_affiliate_code(name="ALTIZ")  # clone ALEXTV -15%
```

Ou pour dotation récurrente, ajouter :

```python
mcp__shopify_orders__create_discount_code(
    title="ALTIZDOTATION",
    code="ALTIZDOTATION",
    value=-120.0,
    value_type="fixed_amount",
    usage_limit=4,
    once_per_customer=False,
    ends_at="2026-08-17T23:59:59+02:00",
    combines_order_discounts=False,
    combines_product_discounts=True,
    combines_shipping_discounts=True,
)
```

## Parallélisation recommandée

```
┌─ create_draft_order ────────┐
├─ create_affiliate_code ─────┤── puis update_draft_order → complete_draft_order
└─ create_discount_code DOT ──┘          (si nouveau customer : patch entre create et update)
```

3 premières actions **en parallèle** → gain de temps.

## Exemples réels (17/04/2026)

### Simon Gauthier (one-shot, France)

- Customer créé via email (blank) → patch immédiat
- Draft D753 → 132,20€ → 0€ avec discount 100% + shipping 0€
- Order #12574919229771
- Code `FITBYSIMON` (-15%)

### Yannick Clares (dotation récurrente, France)

- Customer existant id 25731031269707
- Draft D754 → 135,20€ → 0€
- Order #12576240730443
- Code `ALTIZ` (-15%) + Code `ALTIZDOTATION` (120€/mois × 4, ends 2026-08-17)
- Puis ajouté à **Suivi_Dot L31** (déplacé de Suivi_Amb L307)

### Thomas Bonnot (one-shot, France)

- Customer créé via email (blank) → patch immédiat
- Draft D755 → 157,30€ → 0€
- Order #12576584335691
- Code `THOMASBNT` (-15%)

### Maxime Croisé (one-shot, **Belgique**)

- Customer existant id 25834383180107 (email déjà là, mais first_name/last_name/phone null) → patch
- Draft D757 → 123,30€ → 0€
- TVA BE 6% (produits) + 21% (accessoires) reconnue automatiquement
- Order #12576626671947
- Code `MAXIMEC` (-15%)
- Shipping BigBlue vers Belgique OK

## Red flags

| Red flag | Conséquence | Mitigation |
|---|---|---|
| `draft.email = null` après création avec customer_email | emails Shopify pas envoyés, tracking BigBlue pas rattaché, Affiliatly peut ne pas se lier | Patcher customer immédiatement + re-vérifier via `get_draft_order` |
| Oublier `tags="Dotation influenceur"` | CA HCS faussé (commande compte comme vraie vente) | Tag obligatoire dès création draft |
| `use_customer_default_address=True` sans adresse customer | Shopify bloque ou met adresse vide | Passer `shipping_address={}` explicite ou patcher customer d'abord |
| Oublier `country_code` dans shipping_address | Shopify peut rejeter ou calculer TVA FR par défaut | Toujours inclure `country_code: "FR"` / `"BE"` / etc. |
| Utiliser `customer_email` sans patcher ensuite | Customer blank reste (incident Dylan 15/04/2026) | Post-création immédiate : `update-customer(email, firstName, lastName, phone)` |
| `combines_order_discounts=True` sur code affilié | Conflit avec promos ordre | Toujours `False` sur affilié ambassadeur (pattern ALEXTV) |

## Sheet updates après complétion

**Suivi_Amb** (col mapping) :
- `J` (statut) : `Ambassadeur` ou `In-hot`
- `K` (note) : description complète (order id, code, date)
- `L` (priorité) : `good` après commande
- `N` (code affilié) : nom du code créé

**Suivi_Dot** (si dotation récurrente) :
- `A` (name) : Prénom Nom
- `F` (mail), `G` (num), `H` (prénom), `I` (nom)
- `K` (Code Dotation) : `[CODE]DOTATION`
- `M` (Insta) : username
- `R` (Code affilié) : `[CODE]`
- `S` (Util YTD) : 0 au départ
- `Y` (Début) / `Z` (Fin) / `AA` (Durée) / `AB` (Dotation €) / `AC` (Seuil renouvellement)
- `AF` (Adresse complète)

## Source de vérité

- `knowledge/operations.md#créer-un-draft-order`
- `knowledge/operations.md#pattern-code-dotation-codedotation`
- Memory `feedback_draft_order_customer_id` (incident Dylan 15/04/2026)
- Memory `feedback_sav_draft_order_defaults` (règle discount 100% + shipping 0€)
