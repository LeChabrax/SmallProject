# Reference — Partnership Models

Impulse Nutrition runs **three partnership models** with influencers. They
have different contracts, different obligations, different Sheet tabs,
different Shopify tag conventions and different SAV flows.

This document is the single source of truth — kill any other description
elsewhere that contradicts it.

> Last audit : 2026-04-13 — confirmed in interview against the user.
> Note : the historic S/M/L dotation tiers from the `StratAmba` tab are
> **legacy**. Today's reality is *negotiated* dotation contracts (see §2).

---

## TL;DR — Which model is which?

| Model | Cash? | Free products? | Sheet tab | Contract type in `generate_contract.py` | Target profile |
|---|---|---|---|---|---|
| **Affiliation pure** | No | Initial kit only (~80-100 €) | `Suivi_Amb` | `ambassadeur` | First step for every prospect — tested via affiliate code |
| **Dotation négociée** | No | Recurring monthly value, negotiated | `Suivi_Dot` | `dotation` | Profile that refused affiliation OR that we want to upgrade |
| **Paid** | Yes (fixe HT + variable) | Products included in budget | `Suivi_Paid` | `paid` | Top-tier, SIREN required, full obligations |

### Routing rule (interview 2026-04-13)

```
Prospect →  ❶ propose AFFILIATION pure first  (20 €/utilisation, no cash)
              │
              ├─ Accepts                  →  Affiliation flow (Suivi_Amb)
              │
              └─ Refuses (wants more)     →  Negotiate DOTATION
                                            (€/mois × durée ↔ utilisations cibles)
                                                    │
                                                    └─ Suivi_Dot
```

`Paid` is rare — only for top-tier profiles that explicitly want a cash
contract and have a SIREN. Tripartite (agency-managed) deals also live in
`Suivi_Paid` with `management = <agency name>`.

The distinction matters because:
- **Sheet columns differ** per tab → see `reference_sheet_schema.md`.
- **Contract articles differ** (renewal, IP assignment, image rights, remuneration) → see below.
- **SAV flow differs** when a paid influencer has a shipping issue vs a dotation athlete.

---

## 1. Affiliation pure (Ambassadeur entrée)

Purpose : test a new influencer at low cost. **Default offer for every new
prospect**. No contract binding in time.

- **Terme** : ATHLETE / AMBASSADEUR (affiliate only).
- **Dotation initiale** : ~80–100 € de produits gratuits (one-shot welcome kit).
- **Code affilié** : personnel, configuré comme un **clone exact de `ALEXTV`**
  (canonical pattern — see [`process_create_codes.md`](process_create_codes.md)).
  `-15 %` on first order for their followers.
- **Crédit ambassadeur** : `1 utilisation = 20 €` (paid out as a code credit).
- **Code crédit calc** : quand l'ambassadeur veut redeem ses crédits accumulés,
  on crée un code unique d'une valeur de `(col O − col Q) × 20 €`, applicable
  sur une seule commande. Voir [`process_calculate_credits.md`](process_calculate_credits.md).
- **Minimum** : 2 utilisations avant de mériter un geste commercial.
- **Contenu demandé** : format libre (3 contenus global).
- **Evolution path** : si l'ambassadeur refuse l'affiliation pure (veut plus
  qu'un code) → bascule vers **Dotation négociée** (voir §2). Si traction
  exceptionnelle confirmée et SIREN dispo → discussion **Paid** (§3).
- **PDF contrat** : `generate_contract.py --type ambassadeur`.
- **Sheet** : `Suivi_Amb`.

### Colonnes Suivi_Amb pertinentes
`username` (I), `statut` (J), `action` (K), `priorite` (L), `campagne` (M), `code_affilie` (N), `nb_utilisation` (O), `code_credit` (P), `nb_credit_used` (Q), `lien_affilie` (R), `prenom` (AE), `mail` (AF).

---

## 2. Dotation négociée

Purpose : recurring product shipments for influencers who refused the
affiliation deal but still want to collaborate. **No cash, just product.**
Contract type ATHLETE.

### Format (interview 2026-04-13)

Pas de tiers fixes. Chaque dotation est **négociée au cas par cas** sur le
schéma :

```
montant €/mois  ×  durée (généralement 4 mois)  ↔  N utilisations cibles
```

Exemple type :
- **100 € / mois** × **4 mois** ↔ **14 utilisations** sur la période.
- **150 € / mois** × **4 mois** ↔ **18 utilisations** sur la période.
- **80 € / mois** × **4 mois** ↔ **12 utilisations** sur la période.

L'ambassadeur reçoit un **code dotation** lui permettant de redeem son envoi
chaque mois (`N` utilisations égales à `N` mois de contrat). Voir
[`process_create_codes.md`](process_create_codes.md) §2 pour le pattern
exact (clone des codes existants type `CREDITUSE` / `TRAILEURSDOTATION`).

> Les anciens tiers `S` (80 €), `M` (100 €), `L` (150 €) du `StratAmba` tab
> sont **legacy**. Ils donnent une idée des montants standards mais aucune
> nouvelle dotation ne suit ce format rigide. C'est toujours négocié.

- **Terme** : ATHLETE.
- **Art 3 — Dotation** : produits uniquement, valeur mensuelle négociée.
- **Art 4 — Obligations** : X stories + Y reels/mois selon négociation.
- **Art 2 — Renouvellement** : auto si le seuil d'utilisations négocié est atteint, sinon non-reconduction.
- **Art 5 — Propriété intellectuelle** : cession 2 ans après fin de contrat.
- **Art 6 — Droit à l'image** : durée contrat + 1 an.
- **Pas d'article rémunération** (dotation produits seule).
- **PDF contrat** : `generate_contract.py --type dotation`.
- **Shopify tag** pour l'envoi : `Dotation influenceur` (CRITIQUE — voir [`process_create_orders.md`](process_create_orders.md) pour le mapping CA).
- **Sheet** : `Suivi_Dot`.

### Colonnes Suivi_Dot pertinentes
`name` (A), `code_dotation` (K), `util_ytd` (S), `debut` (Y), `fin` (Z), `duree` (AA), `dotation_eur` (AB), `seuil_renouvellement` (AC), `agreement` (AD), `pdf` (AE).

---

## 3. Paid (contrat rémunéré)

Purpose : serious partnership with obligations détaillées et cash. Contract
type INFLUENCEUR. Requires SIREN or equivalent.

### Structure (ex : Les Traileurs 202602)

- **Terme** : INFLUENCEUR.
- **Art 3 — Dotation** : produits + code dotation spécifique (ex: `TRAILEURSDOTATION`).
- **Art 4 — Livrables détaillés** :
  - Posts/réels d'annonce de collaboration.
  - Réels/posts avec mise en avant (nombre spécifique sur la durée).
  - Sets de stories éducatives (3 écrans : pourquoi produit / pourquoi Impulse / utilisation + lien).
  - Stories organiques par mois.
  - Publications doivent rester actives 24 h minimum.
- **Art 2 — Renouvellement** : par avenant uniquement (pas auto).
- **Art 5 — PI** : cession = durée du contrat (pas 2 ans).
- **Art 6 — Droit à l'image** : = durée du contrat (pas +1 an).
- **Art 7 — Rémunération** :
  - Montant fixe brut HT (ex : 3 000 €).
  - Variable : 10 € HT par commande nouveau client avec le code affilié.
  - Calendrier de facturation (ex : février / avril / juillet).
  - Paiement virement, 60 j après émission facture.
- **Tripartite (agence)** : si management via Primelis / FraichTouch / Versacom, le contrat est géré par l'agence — colonne `management` (B) = nom de l'agence. Pas à générer dans notre outil.
- **PDF contrat** : `generate_contract.py --type paid`.
- **Sheet** : `Suivi_Paid`.

### Colonnes Suivi_Paid pertinentes
`name` (A), `management` (B), `statut_deal` (C), `insta_name` (J), `code` (P), `fixe` (W), `var_prov` (X), `budget_total` (Y), `debut` (Z), `fin` (AA), `duree` (AB), `dotation_eur` (AD), `bio_linkt` (AF), `a_la_une` (AG), `reels_post` (AH), `stories` (AI), `youtube_obl` (AJ), `strava_obl` (AK), `tiktok_obl` (AL), `pdf` (AM).

---

## 4. Decision flow — Which model for a new prospect?

```
Prospect identifié
      │
      ├─ < 5k followers ou < 2 % engagement      →  NO-GO
      │
      ├─ Pitch ❶ : AFFILIATION PURE              →  Suivi_Amb
      │    │
      │    ├─ Accepte                            →  ▶ Suivi_Amb (code clone ALEXTV)
      │    │
      │    └─ Refuse (veut plus qu'un code)
      │            │
      │            └─ Pitch ❷ : DOTATION négociée
      │                    │
      │                    ├─ Accepte un montant  →  ▶ Suivi_Dot
      │                    │  (€/mois × durée ↔
      │                    │   utilisations cibles)
      │                    │
      │                    └─ Veut cash + SIREN  →  ▶ Suivi_Paid
      │
      ├─ Demande cash d'emblée + SIREN            →  Suivi_Paid ou REFUS
      │
      └─ Vient d'une agence (Primelis…)           →  Suivi_Paid tripartite
```

Pas de pré-qualification automatique sur Affiliation → Dotation. C'est
**purement déclenché par le refus de l'ambassadeur** sur l'offre 1.

Scoring profil détaillé dans `instagram_dm_mcp/qualify_influencer.py`
(functions `score_followers`, `score_engagement`, `score_bio`, `score_ratio`)
pour décider GO / MAYBE / NO-GO en amont du pitch.

---

## 5. Contract generator usage (`generate_contract.py`)

All contract types are generated from the same Python script. The internal
classes are `ContractData` and `ContractPDF` (see `generate_contract.py`).

> **Note 2026-04-13** : le script accepte actuellement uniquement
> `--type dotation` ou `--type paid`. Pour un contrat ambassadeur affilié pur
> (sans cash, code -15%), il n'y a pas de PDF à signer dédié — l'engagement
> se fait via DM Instagram. À ajouter en `--type ambassadeur` dans une
> future itération si besoin.

### Génération PDF locale

```bash
# Dotation négociée (100 €/mois, 4 mois)
python3 generate_contract.py \
  --first-name "Florine" --last-name "Breysse" \
  --address "7 route de Thônes 74940 Annecy-le-Vieux" \
  --date "13/04/2026" --duration 4 \
  --type dotation --code FLORINE \
  --dotation-amount 100 \
  --stories 3 --reels 1 --gender F

# Paid (budget fixe HT + variable)
python3 generate_contract.py \
  --first-name "..." --last-name "..." \
  --type paid --code ... --duration 12 \
  --fixed-amount 3000 --variable-amount 10 \
  --billing-schedule "février / avril / juillet" \
  --reels 3 --stories 20 --gender F
```

Output → `contracts/Contract_Prenom_Nom_YYYY-MM-DD.pdf`.

### Upload automatique Drive + Sheet (depuis 2026-04-13)

```bash
# Génération + upload Drive InfluenceContract
python3 generate_contract.py ... --upload-drive

# Génération + upload Drive + écriture du lien dans le bon Sheet
python3 generate_contract.py ... --update-sheet
# → écrit le lien Drive dans Suivi_Dot AE pour --type dotation
# → écrit le lien Drive dans Suivi_Paid AM pour --type paid
```

Le fichier est nommé sur Drive selon la convention existante :
`YYYYMM - Contrat <Prénom Nom>.pdf`. Si un fichier du même nom existe déjà
dans le dossier, il est écrasé (mise à jour, garde le même `file_id`).

Workflow signature manuelle (v1) :
1. `--upload-drive --update-sheet` → PDF brut sur Drive + lien Sheet
2. Tu envoies le lien à l'ambassadeur, il signe à la main, te renvoie scanné
3. Tu déposes la version signée dans Drive (même nom de fichier) → le lien
   Sheet pointe automatiquement sur la nouvelle version (même `file_id`)

Voir `infra/common/google_drive.py` pour les helpers techniques (`upload_pdf_to_drive`,
`update_sheet_with_contract_link`).

---

## 6. Sponsor concurrent — comment réagir

Certains ambassadeurs sont déjà sponsorisés par un concurrent. Détection
automatique dans `audit_ambassadors.py` qui lit la bio → colonne
`sponsor` (X) de Suivi_Amb.

- **Sponsor exclusif détecté** (Nutripure, TA Energy, Overstim, etc.) → statut `Out`, priorité `good`, stop.
- **Sponsor historique mais contrat fini** → possible, à vérifier au cas par cas.
- **Pas de sponsor identifié** → go/maybe selon scoring.

---

## 7. Agences / managers

| Agence | Contact | Clients |
|---|---|---|
| **Puls Agency** | marie@puls-agency.com (Kelly, Marie Schoenenburg) | — |
| **Versacom** | simon@versacom.eu (Arwen) | — |
| **Fraich Touch** | gael@fraichtouch.com (Malo) | — |
| **MyOpenComm** | yohann@myopencomm.com (Sacha) | — |
| **Primelis** | (tripartite standard) | — |
| **HCS interne** | pgautier@havea.com (Pierre Gautier) | Commandes dotation |

Quand un influenceur mentionne son agent → statut `Contacter manager` en Suivi_Amb, et suivre le contact correspondant.
