# Process — Calcul du crédit ambassadeur

Runbook procédural pour calculer et redeem les crédits accumulés par un
ambassadeur (code affilié `1 utilisation = 20 €`).

> Verrouillé en interview 2026-04-13.

---

## 0. Concept

Chaque utilisation du code affilié d'un ambassadeur par un de ses followers
lui rapporte **20 € de crédit** à dépenser sur le site Impulse Nutrition.

Quand l'ambassadeur veut redeem son crédit accumulé :
1. On calcule le **solde restant** (`utilisations totales − utilisations déjà consommées`).
2. On crée **un code unique** d'une valeur de `solde × 20 €`, applicable sur **UNE seule commande**.
3. L'ambassadeur place sa commande avec ce code → il bénéficie du discount.
4. On met à jour le Sheet pour refléter la consommation.

---

## 1. Sources de vérité (Sheet `Suivi_Amb`)

| Col | Idx | Constante | Rôle |
|---|---|---|---|
| **N** | 13 | `code_affilie` | Le code affilié de l'ambassadeur (ex `FLORINE`) |
| **O** | 14 | `nb_utilisation` | Nombre total de fois que le code a été utilisé par les followers |
| **P** | 15 | `code_credit` | Le code crédit créé pour le redeem (ex `FLORINE-CREDIT`) |
| **Q** | 16 | `nb_credit_used` | Nombre d'utilisations déjà redeem par l'ambassadeur |

Source canonique : voir [`reference_sheet_schema.md`](reference_sheet_schema.md).

> Les colonnes **O** et **Q** doivent toujours être à jour pour que le
> calcul soit correct. La col O est mise à jour soit manuellement après
> consultation Affiliatly, soit (à terme) automatiquement par un script
> `sync_affiliatly_uses.py` à venir.

---

## 2. Formule

```
solde         = O - Q
credit_value  = solde × 20 €
```

### Exemples

| O (total uses) | Q (already used) | Solde | Crédit value |
|---|---|---|---|
| 5 | 0 | 5 | 100 € |
| 10 | 3 | 7 | 140 € |
| 25 | 20 | 5 | 100 € |
| 3 | 5 | -2 | **invalide** — vérifier données |

**Garde-fou** : si `Q > O`, c'est une incohérence. Stopper, vérifier le
Sheet manuellement, NE PAS créer de code.

---

## 3. Workflow complet

### 3.1 Validation des données

```python
from common.google_sheets import SUIVI_AMB_COLS, get_worksheet, DATA_START_ROW

ws = get_worksheet("Suivi_Amb")
rows = ws.get_all_values()[DATA_START_ROW - 1:]

def find_ambassador(username):
    for i, row in enumerate(rows, start=DATA_START_ROW):
        if len(row) > SUIVI_AMB_COLS["username"] and \
           row[SUIVI_AMB_COLS["username"]].strip().lower() == username.lower():
            return i, row
    return None, None

row_idx, row = find_ambassador("florinebreysse")
if not row:
    raise SystemExit("ambassadeur introuvable")

nb_total = int(row[SUIVI_AMB_COLS["nb_utilisation"]] or 0)
nb_used = int(row[SUIVI_AMB_COLS["nb_credit_used"]] or 0)
prenom = row[SUIVI_AMB_COLS["prenom"]] or "X"

solde = nb_total - nb_used
if solde <= 0:
    raise SystemExit(f"solde invalide ou nul : {solde}")
credit_value = solde * 20
```

### 3.2 Création du code

Voir [`process_create_codes.md`](process_create_codes.md) §3.

```python
from datetime import datetime, timezone

code_name = f"{prenom.upper()}-CREDIT"
# create_credit_code(code_name, credit_value)  → cf process_create_codes §3
```

Pattern Shopify recommandé (à valider à la 1ère création) :

```json
{
  "price_rule": {
    "title": "FLORINE-CREDIT",
    "value_type": "fixed_amount",
    "value": "-140.0",
    "customer_selection": "all",
    "target_type": "line_item",
    "target_selection": "all",
    "allocation_method": "across",
    "starts_at": "<now>",
    "ends_at": null,
    "usage_limit": 1,
    "once_per_customer": true
  }
}
```

`combinesWith` GraphQL : à valider — probablement `productDiscounts: true,
shippingDiscounts: true, orderDiscounts: false` (cohérent avec ALEXTV).

### 3.3 Mise à jour du Sheet

**Avant que l'ambassadeur ne place la commande** :
- Col P (`code_credit`) ← `FLORINE-CREDIT` (le nom du code créé)

**Après que l'ambassadeur ait placé la commande utilisant le code** :
- Col Q (`nb_credit_used`) ← `Q + solde` (donc nouveau Q = O ; les crédits sont consommés)
- Optionnel : col P (`code_credit`) ← clear ou marquer `[CONSUMED]`

> Note : si l'ambassadeur n'utilise PAS le code dans un délai raisonnable
> (ex : 30 jours), il faut décider du sort du code (le laisser actif ou le
> supprimer). Pas de règle stricte aujourd'hui.

### 3.4 Tag de la commande

La commande générée via le code crédit doit être taguée `Dotation influenceur`
sur Shopify pour exclusion du CA. Voir
[`process_create_orders.md`](process_create_orders.md) §2.3.

---

## 4. Cas particuliers

### 4.1 L'ambassadeur veut redeem moins que son solde

Variante : il veut juste 60€ (par ex. pour une seule whey) alors qu'il a
140€ de solde. Deux options :

- **Créer un code à 60€** + ne consommer que 3 utilisations dans Q (Q ← Q+3). Le solde restant est 80€ et reste disponible pour plus tard.
- **Refuser** et créer pour le full solde (politique : "le crédit s'use d'un coup"). Plus simple à tracker.

→ Décision actuelle : pas de règle figée, à confirmer au cas par cas. À
trancher dans une future itération de cette doc.

### 4.2 Un ancien code crédit existe encore

Si col P contient déjà un code (ex : `FLORINE-CREDIT` créé il y a 2 mois,
non utilisé), avant d'en créer un nouveau :

1. Vérifier sur Shopify si l'ancien code existe encore et s'il a été utilisé.
2. Si non utilisé → le **désactiver** (delete via `discount_codes/{id}.json`
   DELETE) ou réutiliser le même nom avec une nouvelle valeur.
3. Créer le nouveau code seulement après cleanup.

### 4.3 L'ambassadeur a quitté le programme (statut `Out`)

Politique standard : on honore les crédits accumulés AVANT son départ. Si
col O > col Q et qu'il demande à redeem, on créer le code normalement.

---

## 5. Audit régulier

À faire **mensuellement** : pour chaque ambassadeur dans `Suivi_Amb` avec
`solde > 5` (≥ 100€ disponibles) qui n'a pas redeem depuis ≥ 3 mois,
envoyer un message DM proposant le redeem.

Pas de script automatique aujourd'hui — à ajouter dans le backlog (cf
`knowledge/INDEX.md` § AdHoc).

---

## 6. See also

- [`reference_sheet_schema.md`](reference_sheet_schema.md) — colonnes Suivi_Amb
- [`process_create_codes.md`](process_create_codes.md) — création du code Shopify
- [`process_create_orders.md`](process_create_orders.md) — tagging de la commande qui en résulte
