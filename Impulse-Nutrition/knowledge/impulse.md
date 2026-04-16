# Impulse Nutrition — Onboarding

> **Ce doc = qui/quoi**. Ce que tu lis pour comprendre Impulse en 5 min.
> Pour le **comment faire** (SAV, voice, runbooks, quirks techniques) → [`operations.md`](./operations.md).
> Pour le **catalogue structuré** (78 SKUs, variant_id, prix, moments) → [`catalog.yaml`](./catalog.yaml) (auto-généré, refresh via `infra/scripts/refresh_catalog.py`).

## Sommaire

1. [Marque & propriétaire](#1-marque--propriétaire)
2. [Programme ambassadeur — les 3 modèles](#2-programme-ambassadeur--les-3-modèles)
3. [Pipeline ambassadeur](#3-pipeline-ambassadeur)
4. [Catalogue produits](#4-catalogue-produits)
5. [Glossaire métier](#5-glossaire-métier)
6. [Agences partenaires](#6-agences-partenaires)

---

## 1. Marque & propriétaire

**Impulse Nutrition** est une marque française de nutrition sportive premium (compléments alimentaires, whey, électrolytes, preworkout, collagène, magnésium, boissons d'effort) distribuée via [impulse-nutrition.fr](https://impulse-nutrition.fr).

Propriétaire : **HAVEA COMMERCIAL SERVICES (HCS)**, SAS basée à Montaigu-Vendée (85).

**Antoine Chabrat** est l'Influence Manager. Il gère le programme ambassadeur et les partenariats influenceurs. Sur Instagram DM il parle en son nom (tutoiement). Sur les canaux client final (SC) il ne signe jamais "Antoine" — la persona SC est l'entité Impulse Nutrition (voir [`operations.md#voice--persona-split`](./operations.md#voice--persona-split)).

Positionnement : produits fabriqués en France, haute qualité, pensés par et pour les besoins réels des sportifs.

---

## 2. Programme ambassadeur — les 3 modèles

Impulse gère **trois modèles de partenariat** avec des contrats, obligations, Sheet tabs, tags Shopify et flows SAV distincts.

### TL;DR

| Modèle | Cash ? | Produits ? | Sheet | `generate_contract --type` | Cible |
|---|---|---|---|---|---|
| **Affiliation pure** | Non | Kit initial ~80-100 € | `Suivi_Amb` | `ambassadeur` | **Offre par défaut** — tous les prospects |
| **Dotation négociée** | Non | Récurrent mensuel négocié | `Suivi_Dot` | `dotation` | Refus affiliation OU upgrade d'un affilié |
| **Paid** | Oui (fixe HT + variable) | Inclus dans budget | `Suivi_Paid` | `paid` | Top-tier, SIREN requis |

### Routing rule

```
Prospect →  ❶ propose AFFILIATION pure d'abord  (20€/utilisation, no cash)
              │
              ├─ Accepte                  →  Suivi_Amb (code clone ALEXTV)
              │
              └─ Refuse (veut plus)        →  ❷ Négocier DOTATION
                                              (€/mois × durée ↔ utilisations cibles)
                                                      │
                                                      ├─ Accepte               →  Suivi_Dot
                                                      └─ Veut cash + SIREN     →  Suivi_Paid
```

`Paid` est rare — uniquement top-tier qui veulent cash + SIREN, ou tripartite agence (Primelis, FraichTouch, Versacom, Puls, MyOpenComm).

### 2.1 Affiliation pure (Ambassadeur)

**Offre par défaut pour tout nouveau prospect.** Pas de contrat dans le temps.

- **Terme** : ATHLETE / AMBASSADEUR (affiliate only)
- **Dotation initiale** : ~80–100 € de produits gratuits (welcome kit one-shot)
- **Code affilié** : personnel, **clone exact de `ALEXTV`**. -15% pour les followers, sans limite (voir [`operations.md#créer-un-code-affilié-ambassadeur`](./operations.md#créer-un-code-affilié-ambassadeur))
- **Crédit ambassadeur** : `1 utilisation = 20 €` (payé via code crédit à la demande)
- **Code crédit** : quand l'ambassadeur veut redeem, on crée un code unique valant `(col O − col Q) × 20 €`, applicable sur 1 seule commande
- **Minimum** : 2 utilisations avant tout geste commercial
- **Contenu demandé** : format libre (3 contenus)
- **Upgrade path** : refus affiliation → Dotation. Traction exceptionnelle + SIREN → discussion Paid
- **Sheet** : `Suivi_Amb` (pipeline entrée)

Colonnes Suivi_Amb utiles : `username` (I), `statut` (J), `action` (K), `priorite` (L), `campagne` (M), `code_affilie` (N), `nb_utilisation` (O), `code_credit` (P), `nb_credit_used` (Q), `lien_affilie` (R), `prenom` (AE), `mail` (AF).

### 2.2 Dotation négociée

Pour les influenceurs qui refusent l'affiliation seule mais veulent collaborer. **Pas de cash, que du produit récurrent.**

**Format** — négocié au cas par cas :

```
montant €/mois  ×  durée (généralement 4 mois)  ↔  N utilisations cibles
```

Exemples :
- **100 €/mois** × **4 mois** ↔ **14 utilisations**
- **150 €/mois** × **4 mois** ↔ **18 utilisations**
- **80 €/mois** × **4 mois** ↔ **12 utilisations**

L'ambassadeur reçoit un **code dotation** type `[NOM]DOTATION` lui permettant de redeem son envoi mensuel (`N` utilisations = `N` mois de contrat). Pattern : clone `TRAILEURSDOTATION` (voir [`operations.md#pattern-code-dotation-nomdotation`](./operations.md#pattern-code-dotation-nomdotation)).

> Les anciens tiers `S` (80€), `M` (100€), `L` (150€) du `StratAmba` tab sont **legacy**.

- **Terme** : ATHLETE
- **Art 3 — Dotation** : produits uniquement, valeur mensuelle négociée
- **Art 4 — Obligations** : X stories + Y reels/mois selon négociation
- **Art 2 — Renouvellement** : auto si seuil utilisations atteint, sinon non-reconduction
- **Art 5 — PI** : cession 2 ans après fin de contrat
- **Art 6 — Droit à l'image** : durée contrat + 1 an
- Pas d'article rémunération (dotation produits seule)
- **Shopify tag envoi** : `Dotation influenceur` (CRITIQUE — voir [`operations.md#règle-dor-des-tags-shopify`](./operations.md#règle-dor-des-tags-shopify))
- **Sheet** : `Suivi_Dot`

Colonnes Suivi_Dot utiles : `name` (A), `code_dotation` (K), `util_ytd` (S), `debut` (Y), `fin` (Z), `duree` (AA), `dotation_eur` (AB), `seuil_renouvellement` (AC), `agreement` (AD), `pdf` (AE).

### 2.3 Paid (contrat rémunéré)

Partenariat sérieux avec obligations détaillées et cash. Requiert SIREN.

**Structure type (ex : Les Traileurs 202602)** :

- **Terme** : INFLUENCEUR
- **Art 3 — Dotation** : produits + code dotation spécifique (ex `TRAILEURSDOTATION`)
- **Art 4 — Livrables détaillés** :
  - Posts/reels d'annonce de collaboration
  - Reels/posts avec mise en avant (nombre spécifique sur la durée)
  - Sets de stories éducatives (3 écrans : pourquoi produit / pourquoi Impulse / utilisation + lien)
  - Stories organiques par mois
  - Publications doivent rester actives 24h min
- **Art 2 — Renouvellement** : par avenant uniquement (pas auto)
- **Art 5 — PI** : cession = durée du contrat (pas 2 ans)
- **Art 6 — Droit à l'image** : = durée du contrat (pas +1 an)
- **Art 7 — Rémunération** :
  - Montant fixe brut HT (ex : 3 000 €)
  - Variable : 10 € HT par commande nouveau client avec le code affilié
  - Calendrier facturation (ex : février / avril / juillet)
  - Virement 60j après facture
- **Tripartite (agence)** : si management via Primelis / FraichTouch / Versacom, contrat géré par l'agence — colonne `management` (B) = nom agence. Pas à générer localement.
- **Sheet** : `Suivi_Paid`

Colonnes Suivi_Paid utiles : `name` (A), `management` (B), `statut_deal` (C), `insta_name` (J), `code` (P), `fixe` (W), `var_prov` (X), `budget_total` (Y), `debut` (Z), `fin` (AA), `duree` (AB), `dotation_eur` (AD), `bio_linkt` (AF), `a_la_une` (AG), `reels_post` (AH), `stories` (AI), `youtube_obl` (AJ), `strava_obl` (AK), `tiktok_obl` (AL), `pdf` (AM).

### 2.4 Sponsor concurrent

Certains ambassadeurs sont déjà sponsorisés par un concurrent. Détection auto dans `audit_ambassadors.py` → `sponsor` (X) de Suivi_Amb.

- **Sponsor exclusif** (Nutripure, TA Energy, Overstim…) → statut `Out`, priorité `good`, stop
- **Sponsor historique mais contrat fini** → possible, à vérifier cas par cas
- **Pas de sponsor identifié** → go/maybe selon scoring

### 2.5 Génération de contrats PDF

Script `infra/scripts/generate_contract.py`. Exemples :

```bash
# Dotation négociée (100€/mois, 4 mois)
python3 infra/scripts/generate_contract.py \
  --first-name "Florine" --last-name "Breysse" \
  --address "7 route de Thônes 74940 Annecy-le-Vieux" \
  --date "13/04/2026" --duration 4 \
  --type dotation --code FLORINE \
  --dotation-amount 100 --stories 3 --reels 1 --gender F

# Paid (budget fixe HT + variable)
python3 infra/scripts/generate_contract.py \
  --type paid --first-name "..." --last-name "..." \
  --code ... --duration 12 \
  --fixed-amount 3000 --variable-amount 10 \
  --billing-schedule "février / avril / juillet" \
  --reels 3 --stories 20 --gender F
```

Output → `infra/contracts/Contract_Prenom_Nom_YYYY-MM-DD.pdf`.

**Upload Drive + Sheet** (2026-04-13) :
- `--upload-drive` : push sur Drive folder `InfluenceContract`
- `--update-sheet` : push Drive + écrit le lien dans Suivi_Dot AE (dotation) ou Suivi_Paid AM (paid)
- Convention nom : `YYYYMM - Contrat <Prénom Nom>.pdf`. Si existe → écrasé (même `file_id`)

Signature manuelle : ambassadeur signe à la main, renvoie scanné, tu remplaces le PDF sur Drive (même nom, le lien Sheet se met à jour).

> `--type ambassadeur` n'existe pas encore (affiliation pure = engagement via DM, pas de PDF à signer).

---

## 3. Pipeline ambassadeur

### 3.1 Étapes du flow complet

```
Prospection → Scoring (GO/MAYBE/NO-GO) → Pitch DM → Onboarding
   → Draft order Shopify → Création code affilié → Suivi utilisations
   → Redeem crédits → Relance long terme
```

1. **Prospection** : audit Instagram (followers, engagement %, sponsor), scoring via `instagram_dm_mcp/qualify_influencer.py` → GO/MAYBE/NO-GO
2. **Pitch DM** via skill `/instagram-dm` (templates dans [`voice/templates.yaml`](./voice/templates.yaml))
3. **Réponse positive** → deuxième message explicatif
4. **Acceptation** → demande coordonnées (sélection produits + adresse + mail + téléphone — les **4 infos en 1 seul message**)
5. **Draft order Shopify** avec tag `Dotation influenceur` + discount 100% + shipping 0€ (voir [`operations.md#créer-un-draft-order`](./operations.md#créer-un-draft-order))
6. **Création code affilié** via `create_affiliate_code(name="prenom")` (clone ALEXTV)
7. **Suivi utilisations** col O Suivi_Amb — sync manuel Affiliatly
8. **Redeem crédit** : formule `(O − Q) × 20€`, code `[PRENOM]-CREDIT` (voir [`operations.md#calculer-et-redeem-le-crédit-ambassadeur`](./operations.md#calculer-et-redeem-le-crédit-ambassadeur))
9. **Relance long terme** : si silence > 2 semaines, DM contextualisé. Si traction → upgrade dotation. Si top-tier → Paid

### 3.2 Statuts Suivi_Amb (col J)

| Statut | Quand | Action typique |
|---|---|---|
| `In-cold` | Pitch initial envoyé, pas de réponse | Relance douce après 7-14j |
| `In-hot` | Prospect a répondu positivement | Drafter second message / enchaînement |
| `A rediscuter` / `A recontacter` | "Recontacte-moi plus tard" | Relance programmée |
| `Produits envoyés` | Draft complétée, colis parti | Mode réactif, nudge code |
| `Contacter manager` | Prospect mentionne un agent | Contact par mail (pas DM) |
| `Out` | Sponsor exclusif, ou refus définitif | Stop, priorité `good` |

### 3.3 Prospect "parqué"

Un prospect qui a reçu un **code welcome -25%** (`ACHAB25`, `PGAU25`, ou variante `{NOM}25`) lors d'un échange antérieur est **parqué** — pas rejeté définitivement, mais jugé pas prêt.

**JAMAIS pitcher un prospect parqué comme un premier contact.** Il a une mémoire précise de l'échange précédent. Contredire cette mémoire détruit la crédibilité d'Impulse.

Codes welcome actifs :

| Code | Owner | Notes |
|---|---|---|
| `ACHAB25` | Antoine Chabrat | **Code préféré DM Instagram** |
| `PGAU25` | Pierre Gautier | Collègue HCS |

Règle auto-parquage : **< 2000 followers = parquage auto avec ACHAB25 sans go ciblé** (traitement batch après les importants).

Le routing de relance des parqués vit dans [`operations.md#relance-dun-prospect-parqué`](./operations.md#relance-dun-prospect-parqué).

---

## 4. Catalogue produits

**78 SKUs actifs** (source de vérité : Shopify Admin API via MCP `shopify_orders`).

→ **Fichier structuré : [`catalog.yaml`](./catalog.yaml)** — YAML auto-généré, 78 entrées avec `title`, `variant_id`, `sku`, `price_eur`, `moment`, `category`, `page_url`. Refresh via `python3 infra/scripts/refresh_catalog.py`.

### 4.1 Taxonomie "moment de consommation" (règle métier)

Chaque complément est rangé dans **exactement 1 moment** :

| Moment | Produits (résumé) |
|---|---|
| **`avant_effort`** | Preworkout, barres protéinées, maltodextrine |
| **`pendant_effort`** | Électrolytes (comprimés et poudre), boissons d'effort isotoniques, BCAA |
| **`apres_effort`** | Whey Isolate, Whey Recovery, créatine, glycine |
| **`au_quotidien`** | Collagène, L-glutamine, magnésium, vitamines, multivitamines, fer, omega 3, spiruline, curcumine, pré-probiotiques, sommeil+ |

Les **accessoires** (shaker 450/750, bidon 750ml, flasque 500ml) sont en `category: accessoire` sans moment.

Les **bundles** (Duo/Pack/TTS) héritent d'un moment dérivé du nom (`Duo Avant` → avant_effort, `Duo Après` → apres_effort, etc.).

### 4.2 Comment ça marche

- **Ajouter un produit sur Shopify** → `python3 infra/scripts/refresh_catalog.py` → `catalog.yaml` est à jour
- **Produit non reconnu** (pattern manquant) → ajoute le mot-clé dans `infra/scripts/catalog_taxonomy.yaml` sous le bon `moment`, re-run le script
- **Règle métier change** (ex: un produit change de moment) → édite `catalog_taxonomy.yaml`, re-run

### 4.3 Règles d'usage / dosage (collectées en SAV)

Complément au catalog structuré, infos non-Shopify collectées au fil des échanges clients :

| Produit | Info |
|---|---|
| Whey Isolate | 10g par cuillère. Prise 30min-1h après entraînement. Contient de la **lactase** → pas de souci digestion lactose |
| Whey Recovery | Formule 3-en-1 : whey concentrate + créatine + collagène. Récup complète (musculaire, articulaire, performance). Contient lactase |
| Électrolytes citron/pêche | 24,75mg vitamine C par comprimé. Minéraux : sodium, potassium, magnésium, calcium, zinc |
| Vitamine C | 1000mg par comprimé |
| Magnésium bisglycinate | À prendre le soir |
| Créatine Creapure® | Cumulable avec le collagène dans le shaker |
| Preworkout | Première prise : 1/3 à 1/2 scoop, augmenter progressivement |

### 4.4 Produits-phares pour SAV / dotation

Utilisés en geste commercial ou base de dotation :

- **Whey Isolate** (39,90€) — pilier protéique
- **Shaker 450ml / 750ml** (6,90€ / 7,90€) — geste standard
- **Bidon 750ml** (7,90€) — geste standard
- **Électrolytes** (15,90€) — dépannage

---

## 5. Glossaire métier

| Terme | Signification |
|---|---|
| **Affiliatly** | Plateforme de suivi codes affiliés + utilisations. Sync manuel vers col O Suivi_Amb (`nb_utilisation`) |
| **Code affilié** | Code -15% personnel (ex : `FLORINE`, `ALEXTV`). Col N Suivi_Amb. Redeemable ∞ times, `once_per_customer` |
| **Crédit** | 20€ débloqués par utilisation du code affilié |
| **Code crédit** | Code Shopify unique `-X€` fixe, 1 utilisation max. Créé à la demande via formule `(O−Q)×20€`. Col P Suivi_Amb |
| **Code welcome** | Code `-25%` first-order. `ACHAB25` (Antoine), `PGAU25` (Pierre Gautier). Format `{NOM}25`. Donné aux prospects trop petits = **parqués** |
| **Prospect parqué** | Prospect qui a reçu un code welcome dans un échange antérieur. Jamais re-pitch comme nouveau contact → relance contextualisée |
| **Dotation** | Envoi gratuit de produits (€/mois × durée ↔ N utilisations cibles). Contrat Suivi_Dot |
| **Code dotation** | Code `[NOM]DOTATION` utilisé par l'ambassadeur pour redeem sa dotation mensuelle (ex `TRAILEURSDOTATION`) |
| **Enveloppe** | Budget produits alloué (~80-100€ initial) |
| **Tag `Service client`** | Commande SAV/replacement. Sort du CA HCS (coût SAV) |
| **Tag `Dotation influenceur`** | Envoi gratuit ambassadeur / commande avec code crédit. Sort du CA HCS (coût marketing) |
| **Seuil renouvellement** | Utilisations à atteindre pour renouveler la dotation. Col AC Suivi_Dot |
| **Contacter manager** | Prospect qui mentionne un agent. Statut col J Suivi_Amb. Contact par mail |
| **In-cold** | Prospect pitch envoyé, pas de réponse |
| **In-hot** | Prospect qui a répondu positivement. En discussion |
| **Produits envoyés** | Draft complétée, colis expédié. Mode réactif |
| **Formule crédit** | `(O − Q) × 20€` où O = total utilisations, Q = utilisations consommées |
| **RAS** | Rien à signaler |
| **Au Quotidien** | Moment de consommation = gélules santé (magnésium, vitamines, etc.) et collagène/L-glutamine |
| **Avant / Pendant / Après effort** | Moments de consommation structurés, cf [catalog.yaml](./catalog.yaml) |
| **WAX** | Outil WhatsApp qui pousse les messages dans Gorgias avec tag `WAX` |

---

## 6. Agences partenaires

| Agence | Contact | Rôle |
|---|---|---|
| **Puls Agency** | marie@puls-agency.com (Kelly, Marie Schoenenburg) | Tripartite |
| **Versacom** | simon@versacom.eu (Arwen) | Tripartite |
| **Fraich Touch** | gael@fraichtouch.com (Malo) | Tripartite |
| **MyOpenComm** | yohann@myopencomm.com (Sacha) | Tripartite |
| **Primelis** | (standard tripartite) | Tripartite |
| **HCS interne** | pgautier@havea.com (Pierre Gautier) | Commandes dotation |

Quand un influenceur mentionne son agent → statut `Contacter manager` en Suivi_Amb, contact par mail.
