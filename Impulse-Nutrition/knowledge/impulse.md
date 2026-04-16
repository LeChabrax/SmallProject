# Impulse Nutrition — Connaissance métier

> Source unique de vérité pour tout ce qui concerne Impulse Nutrition : identité, programme ambassadeur, catalogue, SAV, voice, process, quirks, glossaire. Ce doc remplace les 15 fichiers éparpillés de l'ancien `knowledge/`.

## Sommaire

1. [Marque & propriétaire](#1-marque--propriétaire)
2. [Programme ambassadeur — les 3 modèles](#2-programme-ambassadeur--les-3-modèles)
3. [Pipeline ambassadeur](#3-pipeline-ambassadeur)
4. [Catalogue produits](#4-catalogue-produits)
5. [SAV & opérations client](#5-sav--opérations-client)
6. [Voice & persona split](#6-voice--persona-split)
7. [Runbooks opérationnels condensés](#7-runbooks-opérationnels-condensés)
8. [Glossaire métier](#8-glossaire-métier)
9. [Quirks techniques transverses](#9-quirks-techniques-transverses)

---

## 1. Marque & propriétaire

**Impulse Nutrition** est une marque française de nutrition sportive premium (compléments alimentaires, whey, électrolytes, preworkout, collagène, magnésium, boissons d'effort) distribuée via [impulse-nutrition.fr](https://impulse-nutrition.fr).

Propriétaire : **HAVEA COMMERCIAL SERVICES (HCS)**, SAS basée à Montaigu-Vendée (85).

**Antoine Chabrat** est l'Influence Manager. Il gère le programme ambassadeur et les partenariats influenceurs. Sur Instagram DM il parle en son nom (tutoiement). Sur les canaux client final (SC) il ne signe jamais "Antoine" — la persona SC est l'entité Impulse Nutrition (voir §6).

Positionnement : produits fabriqués en France, haute qualité, pensés par et pour les besoins réels des sportifs.

### Gammes

- **Performance** — Protéines & Musculation (Whey Isolate, Whey Recovery, BCAA, Créatine Creapure®, preworkout)
- **Effort & Énergie** — Boissons isotoniques, électrolytes (comprimés et poudre), maltodextrine
- **Récupération / Au Quotidien** — Collagène Peptan®, Magnésium bisglycinate, Glycine, L-Glutamine, Vitamine C
- **Accessoires** — Shaker 450ml/750ml, Bidon 750ml, Flasque 500ml

Les fiches produits détaillées (composition, dosage, usage) sont collectées au fil du SAV et des DMs. La source de vérité SKU / variant_id / prix reste **Shopify via MCP** (`shopify_orders`).

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
- **Code affilié** : personnel, **clone exact de `ALEXTV`** (voir §7). -15% pour les followers, sans limite
- **Crédit ambassadeur** : `1 utilisation = 20 €` (payé via code crédit à la demande)
- **Code crédit** : quand l'ambassadeur veut redeem, on crée un code unique valant `(col O − col Q) × 20 €`, applicable sur 1 seule commande (voir §7.3)
- **Minimum** : 2 utilisations avant tout geste commercial
- **Contenu demandé** : format libre (3 contenus)
- **Upgrade path** : refus affiliation → Dotation. Traction exceptionnelle + SIREN → discussion Paid
- **Sheet** : `Suivi_Amb` (pipeline entrée)

Colonnes Suivi_Amb utiles : `username` (I), `statut` (J), `action` (K), `priorite` (L), `campagne` (M), `code_affilie` (N), `nb_utilisation` (O), `code_credit` (P), `nb_credit_used` (Q), `lien_affilie` (R), `prenom` (AE), `mail` (AF).

### 2.2 Dotation négociée

Pour les influenceurs qui refusent l'affiliation seule mais veulent collaborer. **Pas de cash, que du produit récurrent.**

**Format** — négocié au cas par cas sur le schéma :

```
montant €/mois  ×  durée (généralement 4 mois)  ↔  N utilisations cibles
```

Exemples :
- **100 €/mois** × **4 mois** ↔ **14 utilisations**
- **150 €/mois** × **4 mois** ↔ **18 utilisations**
- **80 €/mois** × **4 mois** ↔ **12 utilisations**

L'ambassadeur reçoit un **code dotation** type `[NOM]DOTATION` lui permettant de redeem son envoi mensuel (`N` utilisations = `N` mois de contrat). Pattern : clone `TRAILEURSDOTATION` (voir §7.2).

> Les anciens tiers `S` (80€), `M` (100€), `L` (150€) du `StratAmba` tab sont **legacy**. Ils donnent une idée des montants standards mais aucune nouvelle dotation ne suit ce format rigide.

- **Terme** : ATHLETE
- **Art 3 — Dotation** : produits uniquement, valeur mensuelle négociée
- **Art 4 — Obligations** : X stories + Y reels/mois selon négociation
- **Art 2 — Renouvellement** : auto si seuil utilisations atteint, sinon non-reconduction
- **Art 5 — PI** : cession 2 ans après fin de contrat
- **Art 6 — Droit à l'image** : durée contrat + 1 an
- Pas d'article rémunération (dotation produits seule)
- **Shopify tag envoi** : `Dotation influenceur` (CRITIQUE — voir §5 et §7)
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

Certains ambassadeurs sont déjà sponsorisés par un concurrent. Détection automatique dans `audit_ambassadors.py` qui lit la bio → `sponsor` (X) de Suivi_Amb.

- **Sponsor exclusif** (Nutripure, TA Energy, Overstim…) → statut `Out`, priorité `good`, stop
- **Sponsor historique mais contrat fini** → possible, à vérifier cas par cas
- **Pas de sponsor identifié** → go/maybe selon scoring

### 2.5 Agences partenaires

| Agence | Contact | Rôle |
|---|---|---|
| **Puls Agency** | marie@puls-agency.com (Kelly, Marie Schoenenburg) | Tripartite |
| **Versacom** | simon@versacom.eu (Arwen) | Tripartite |
| **Fraich Touch** | gael@fraichtouch.com (Malo) | Tripartite |
| **MyOpenComm** | yohann@myopencomm.com (Sacha) | Tripartite |
| **Primelis** | (standard tripartite) | Tripartite |
| **HCS interne** | pgautier@havea.com (Pierre Gautier) | Commandes dotation |

Quand un influenceur mentionne son agent → statut `Contacter manager` en Suivi_Amb, contact par mail.

### 2.6 Génération de contrats PDF

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

**Upload Drive + Sheet** (depuis 2026-04-13) :
- `--upload-drive` : push sur Drive folder `InfluenceContract`
- `--update-sheet` : push Drive + écrit le lien dans Suivi_Dot AE (dotation) ou Suivi_Paid AM (paid)
- Convention nom : `YYYYMM - Contrat <Prénom Nom>.pdf`. Si fichier existe → écrasé (même `file_id`)

Signature manuelle : ambassadeur signe à la main, renvoie scanné, tu remplaces le PDF sur Drive (même nom, le lien Sheet se met à jour).

Helpers techniques : `infra/common/google_drive.py` (`upload_pdf_to_drive`, `update_sheet_with_contract_link`).

> **Note 2026-04-13** : `--type ambassadeur` n'existe pas encore (affiliation pure = engagement via DM, pas de PDF à signer).

---

## 3. Pipeline ambassadeur

### 3.1 Étapes du flow complet

```
Prospection → Scoring (GO/MAYBE/NO-GO) → Pitch DM → Onboarding
   → Draft order Shopify → Création code affilié → Suivi utilisations
   → Redeem crédits → Relance long terme
```

**Détail** :

1. **Prospection** : audit Instagram (followers, engagement %, sponsor), scoring via `instagram_dm_mcp/qualify_influencer.py` (fonctions `score_followers`, `score_engagement`, `score_bio`, `score_ratio`) → verdict GO/MAYBE/NO-GO
2. **Pitch DM** via skill `/instagram-dm` (premier message §6.2 de ce doc)
3. **Réponse positive** → deuxième message explicatif (§6.4)
4. **Acceptation** → demande coordonnées (sélection produits + adresse + mail + téléphone — les **4 infos en 1 seul message**, pas en plusieurs tours)
5. **Draft order Shopify** avec tag `Dotation influenceur` + discount 100% + shipping 0€ (voir §7.2)
6. **Création code affilié** via `create_affiliate_code(name="prenom")` (clone ALEXTV exact)
7. **Suivi utilisations** col O (`nb_utilisation`) Suivi_Amb — sync manuel Affiliatly, futur script automatisé
8. **Redeem crédit** : formule `(O − Q) × 20€`, code crédit unique `[PRENOM]-CREDIT` (§7.3)
9. **Relance long terme** : si silence > 2 semaines, DM contextualisé. Si traction → upgrade dotation. Si top-tier → Paid

### 3.2 Statuts Suivi_Amb (col J)

| Statut | Quand | Action typique |
|---|---|---|
| `In-cold` | Pitch initial envoyé, pas de réponse | Relance douce après 7-14j |
| `In-hot` | Prospect a répondu positivement | Drafter second message / enchaînement |
| `A rediscuter` / `A recontacter` | Prospect dit "recontacte-moi plus tard" | Relance programmée |
| `Produits envoyés` | Draft complétée, colis parti | Mode réactif, nudge code, réagir stories |
| `Contacter manager` | Prospect mentionne un agent | Contact par mail (pas DM) |
| `Out` | Sponsor exclusif concurrent, ou refus définitif | Stop, priorité `good` |

### 3.3 Prospect "parqué"

Un prospect qui a reçu un **code welcome -25%** (`ACHAB25`, `PGAU25`, ou variante `{NOM}25`) lors d'un échange antérieur est **parqué** (pas rejeté définitivement, mais jugé pas prêt pour l'ambassadeur).

**JAMAIS pitcher un prospect parqué comme un premier contact.** Il a une mémoire précise de l'échange précédent. Contredire ou ignorer cette mémoire détruit la crédibilité d'Impulse.

Cas typiques de relance :
- Parqué à <1k qui revient à 10k+ avec stats concrètes → offre ambassadeur **en acknowledgeant l'échange précédent**
- Parqué croisé en IRL (stand, salon) → capitaliser sur la rencontre
- Parqué qui relance sans nouveauté → réponse courte, porte ouverte

Codes welcome actifs :

| Code | Owner | Notes |
|---|---|---|
| `ACHAB25` | Antoine Chabrat | **Code préféré côté DM Instagram** |
| `PGAU25` | Pierre Gautier | Collègue HCS, gère aussi commandes dotation |

Règle auto-parquage : **< 2000 followers = parquage auto avec ACHAB25 sans go ciblé** (traitement batch après les importants).

### 3.4 Pre-draft check obligatoire (skill `/instagram-dm`)

Avant tout draft DM, deux checks bloquants :

**Check 1 — Thread history** : `list_messages(thread_id, amount=50)` minimum. Scanner pour :
- Codes welcome déjà donnés (grep `ACHAB25`, `PGAU25`, `-25%`, `code exclusif`, `{NOM}25`)
- Échanges Impulse antérieurs (`is_sent_by_viewer=true` autre que l'action courante)
- Positions Impulse précédentes (refus, acceptation, conditions)
- Rencontres IRL (`stand`, `salon`, `Run Expérience`, `marathon de Paris`, `nutritionniste en doctorat`)

**Check 2 — Sheet check** : `find_in_spreadsheet(query=username)` sur Suivi_Amb, Suivi_Dot, Suivi_Paid.

**Règle d'or** : le thread Instagram est la source de vérité primaire. Le Sheet est secondaire.

Si hit → signaler à Antoine avec éléments trouvés verbatim, lecture de la situation, proposition de template adapté.

---

## 4. Catalogue produits

**96 SKUs** (83 actifs) en catalogue Shopify. La source de vérité (variant_id, SKU, prix) est Shopify via MCP `shopify_orders` (`get-products`, `get-product-by-id`).

### 4.1 Framework gammes

| Gamme | Sous-catégorie | Exemples |
|---|---|---|
| **Performance** | Protéines & Musculation | Whey Isolate (chocolat/vanille/nature) 39,90€ · Whey Recovery 39,90€ · BCAA 2.1.1 22,90€ · Créatine Creapure® 12,90€ · Preworkout 37,90€ |
| **Effort & Énergie** | Boissons & électrolytes | Électrolytes comprimés 9,90€ · Électrolytes poudre citron/pêche 15,90€ · Boisson isotonique 21,90€ · Maltodextrine 11,90€ |
| **Récupération / Au Quotidien** | Bien-être | Collagène Peptan® 32,90€-36,90€ · Magnésium bisglycinate 15,90€ · Glycine 10,90€ · L-Glutamine 13,90€ · Vitamine C 1000mg |
| **Accessoires** | — | Shaker 450ml 6,90€ · Shaker 750ml 7,90€ · Bidon 750ml 7,90€ · Flasque 500ml 19,90€ |

### 4.2 Fiches produits détaillées (collectées au fil du SAV/DM)

**Whey Isolate (saveur chocolat et autres)**
- Dose par cuillère : 10g
- Page : https://impulse-nutrition.fr/products/whey-isolate-saveur-chocolat
- Contient de la **lactase** → pas de souci digestion lactose

**Whey Recovery**
- Formule 3-en-1 : whey concentrate + créatine + collagène
- Positionnée récupération complète (musculaire, articulaire, performance)
- Différence vs Isolate : Isolate = protéine pure plus concentrée, Recovery = formule combinée
- Contient aussi de la lactase

**Électrolytes (citron / pêche)**
- Vitamine C par comprimé : 24,75mg
- Format : comprimés et poudre
- Minéraux : sodium, potassium, magnésium, calcium, zinc
- Page : https://impulse-nutrition.fr/products/electrolytes-saveur-citron

**Vitamine C**
- 1000mg par comprimé
- Page : https://impulse-nutrition.fr/products/vitamine-c

### 4.3 Règles dosage / usage

- **Whey** : 10g/scoop, 30min-1h après l'entraînement
- **Magnésium** : le soir
- **Créatine** : cumulable dans le shaker avec le collagène
- **Preworkout** : 1/3 à 1/2 scoop en première prise, augmenter progressivement
- **Électrolytes comprimés** : à prendre sur effort

### 4.4 Produits-phares pour SAV / dotation

Utilisés en geste commercial ou comme base de dotation :
- Whey Isolate (39,90€) — pilier protéique
- Shaker 450ml / 750ml (6,90€ / 7,90€) — geste standard
- Bidon 750ml (7,90€) — geste standard
- Électrolytes (15,90€) — dépannage

---

## 5. SAV & opérations client

### 5.1 Canaux convergents

**Tous les SAV remontent dans Gorgias**, peu importe le canal d'origine :

| Canal | Mécanisme | Tag Gorgias |
|---|---|---|
| Email | natif Gorgias | selon contenu |
| Chat site | natif Gorgias | selon contenu |
| Contact form site | natif Gorgias | selon contenu |
| **WhatsApp via WAX** | outil tiers qui pousse dans Gorgias | `WAX` |
| Instagram (mention/DM cliente) | natif Gorgias | selon contenu |
| Facebook | natif Gorgias | selon contenu |
| BigBlue internal-note | alertes stock/livraison | selon contenu |
| TikTok Shop | pipeline custom (`tiktok_sav/sav.py`) | — |

La réponse Gorgias sur un ticket WAX est repoussée automatiquement sur WhatsApp par WAX. Même tone que les autres canaux SC.

### 5.2 Pull protocol strict (leçon 2026-04-13)

Un pull de 30 tickets a loupé `Amandine Laurent` (#52032892). Depuis :

1. **`list_tickets(limit=100, order_by="updated_datetime:desc")` minimum.** Jamais moins.
2. **Filtrer localement** :
   - Keep : channels `email`, `chat`, `contact_form`, `instagram`, `facebook`, `internal-note`
   - Prioriser tags : `urgent`, `statut_commande`, `retour commande`, `retour/echange`, `candidature`, `bigblue-bad-rating-no-comment`, `bigblue-bad-rating-with-comment`, `bigblue-action-required`, `WAX`
   - Ignorer : subjects `[SPAM POSSIBLE]`, `Réponse automatique`, `Automatic reply`, `closed` bounces
3. Si rien ne flag ou Antoine cite un client absent → **deuxième pass** avec `order_by="created_datetime:desc"` pour attraper les tickets avec old `updated_datetime` mais recent content
4. **Ne jamais conclure "not found" sur une liste courte.** Étendre le pull d'abord.
5. `search_tickets` (custom MCP, email lookup + substring fallback) marche mais n'est pas full-text search — le pull protocol est le filet de sécurité.

### 5.3 Recette draft SAV canonique

**Defaults OBLIGATOIRES pour TOUTE commande gratuite** (SAV ou dotation, total 0€) :

```json
{
  "applied_discount": {
    "title": "SAV",
    "value_type": "percentage",
    "value": "100.0",
    "description": "SAV"
  },
  "shipping_line": {
    "title": "Expédition gratuite",
    "price": "0.00"
  },
  "tags": "Service client",
  "note": "<contexte court : ref originale + raison + geste>"
}
```

Le `applied_discount.title` change selon contexte (`SAV`, `Dotation`, `Crédit ambassadeur`). Le `tags` est ce qui compte pour la compta.

### 5.4 Règle d'or des tags Shopify (impact CA HCS)

**Il existe exactement 2 tags qui sortent une commande du calcul du CA :**

| Tag | Coût HCS | Utilisé pour |
|---|---|---|
| `Service client` | Coût SAV | Replacements, gestes commerciaux, codes `[PRENOM]-SAV` |
| `Dotation influenceur` | Coût marketing | Envois mensuels ambassadeurs, codes dotation, codes crédit `[PRENOM]-CREDIT` |

Toute autre commande = **vraie vente dans le CA**. **Mal tagger une commande fausse les rapports financiers HCS.** Non négociable.

Mapping par scénario :

| Scénario | Tag |
|---|---|
| Replacement colis bloqué / perdu | `Service client` |
| Replacement returned-to-sender | `Service client` |
| Geste commercial post-bad-rating | `Service client` |
| Commande client utilisant code `[PRENOM]-SAV` | `Service client` |
| Envoi dotation mensuelle (Suivi_Dot / Suivi_Paid) | `Dotation influenceur` |
| Commande utilisant code crédit `[PRENOM]-CREDIT` | `Dotation influenceur` |
| Vente normale e-commerce | (aucun tag de cette liste) |

### 5.5 Scénarios SAV typiques

**5.5.1 Colis bloqué / perdu en transit (Chronopost loop, Mondial Relay misrouted)**

1. `get_order(order_id)` Shopify → line items + shipping address
2. `get_tracking(bigblue_order_id)` pour confirmer
3. **Créer replacement draft** avec line items originaux + geste commercial (bidon, shaker, ou 1 produit même range)
4. Ship to **home address** — pas de pickup point sur le retry
5. Apply defaults SAV (100% discount + shipping 0 + tag `Service client`)
6. `complete_draft_order` → Shopify crée la commande réelle → BigBlue la prend
7. **Régler manuellement le pickup point sur BigBlue UI** (quirk : draft ne porte pas le pickup point de façon fiable)
8. Répondre Gorgias : confirmer reshipment + geste. Ne pas exposer les détails du tracking loop

Cas réf : Alexandre Damary, IMP4938 → draft IMP6923.

**5.5.2 Returned to sender (refusé par pickup point)**

Deux pickup points consécutifs refusent le colis — souvent pas la faute du client. Proposer :
- Refund (simple)
- OU reship to home + geste commercial

Attendre la réponse du client avant de trigger.

Cas réf : Jean-Baptiste Morand, IMP6586.

**5.5.3 Partial refund**

Client retourne partie de la commande. BigBlue `RETURNED`, Shopify `partially_refunded`.

1. `get_order` → check `refunds` array
2. Si refund déjà traité (transaction `refund`, status `success`) → confirmer au client (montant + PayPal/Stripe auth id + délai 3-5 j ouvrés)
3. Si pas encore traité → trigger via Shopify admin UI (MCP refund non implémenté — étape manuelle)

Cas réf : Amandine Laurent, IMP6036, refund 50,18€ sur ligne `36592237936971` (Collagène marin Peptan®).

**5.5.4 Bad rating BigBlue (1-2 étoiles)**

Tagged `bigblue-bad-rating-no-comment` ou `bigblue-bad-rating-with-comment`.

- Lire le commentaire (si présent) via `get_support_ticket`
- Apology + demander ce qui a mal tourné. Offrir code discount si issue côté service
- Répondre sur le ticket Gorgias (pas BigBlue), fermer quand répondu

**5.5.5 Cas particulier ambassadeur qui fait un SAV**

Si la personne qui contacte le SAV est un ambassadeur (Suivi_Amb / Suivi_Dot / Suivi_Paid) :
- Antoine répond probablement directement (pas via Gorgias / pas signé "Le service client") — il connaît la personne
- Vérifier le statut Suivi avant réponse pour adapter le ton
- Le tag de la commande de remplacement reste **`Service client`** (c'est un SAV, pas une dotation)

### 5.6 Style emails Gorgias

- **Pas de formules pompeuses** : éviter "Nous avons bien pris note", "Nous vous remercions de nous avoir contacté", "N'hésitez pas à revenir vers nous"
- **Phrases courtes**, directes, factuelles
- **Jamais promettre un délai chiffré** (livraison J+1, traitement 48h…) — les partenaires logistiques peuvent varier
- **Jamais signer "Antoine"** côté SC — `Le service client` ou `L'équipe Impulse Nutrition`
- **Vouvoiement strict**
- **Pas d'emoji** sur canal SC

### 5.7 Excuses retard réponse

- **> 4 jours** : excuse légère ("Excuse-moi pour le temps de réponse !")
- **> 10 jours** : excuse appuyée ("Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !")

---

## 6. Voice & persona split

**RÈGLE STRICTE — DEUX PERSONAS ISOLÉS. JAMAIS MÉLANGER.**

| Canal | Persona | Tutoiement | Signature | Exemple |
|---|---|---|---|---|
| **Instagram DM** (ambassadeurs) | **Antoine** (humain) | TU | `Sportivement, Antoine` OU `Antoine` (≥3 phrases) / rien (micro-messages) | "Hello Florine, je suis Antoine d'Impulse Nutrition…" |
| **Gorgias / WAX / email SC** (clients finaux) | **Impulse Nutrition** (entité) | VOUS formel | `Le service client` / `L'équipe Impulse Nutrition` | "Bonjour, votre commande IMP6923…" |

Si Antoine croise un ambassadeur qui contacte SC → **bulle SC** (vouvoiement) jusqu'à résolution, puis revenir au tutoiement.

### 6.1 Tone rules Instagram DM

- **Tutoiement systématique**. Si l'autre vouvoie → switcher vite au `tu`
- **Double exclamation** sur micro-messages ("Merci !!" pas "Merci !")
- **Pas de point final** sur micro-messages
- **Emojis modérés** : 0 à 2 par message max. Favoris : 😉 🔥 😄 😊 😍 ☺️ 💪. **Éviter** 🙏 ✨ 💖 (mielleux)
- **Pas de tirets em (`—`)**. Phrases courtes.
- **Pas de "Bonjour"** dans une conversation déjà ouverte. Réserver au premier contact
- **Pas de jargon** : ROI, KPI, conversion, collab (préférer "partenariat"), reach
- **Ne JAMAIS critiquer la concurrence**
- **Proposer un call** dès que la conversation se complexifie
- **"My bad"** + correction immédiate si on se trompe
- **Ne JAMAIS mentionner de dotation mensuelle** sans validation d'Antoine — le parcours standard est : produits gratuits → code affilié → 20€ crédit/commande
- **Ne jamais re-lister les produits** dans une conversation déjà avancée

### 6.2 Templates DM principaux

> La source machine-readable des templates est **[`knowledge/voice/templates.yaml`](voice/templates.yaml)** (20 templates, 3 modes : verbatim, pick_from_list, semi_structured) — chargée par le skill `/instagram-dm`. Les extraits ci-dessous sont la version humaine lisible.

**Premier message ambassadeur (§2 decision tree)**

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

**Variante courte (impressionné par le profil)**

> On est très impressionnés par ton parcours ! C'est très inspirant et tu
> partages vraiment les valeurs du sport et du dépassement de soi, donc
> déjà bravo !!
>
> Travailler avec toi sera un plaisir ! Ce que je te propose :
>
> Dans un premier temps, on t'envoie pour 80 € de produits, tu choisis ce
> que tu préfères ou on te fait un pack, c'est comme tu préfères, dans
> tous les cas c'est gratuit pour toi !
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

**Refus poli neutre (sponsor non identifié)**

> On comprend tout à fait, merci d'avoir pris le temps de nous répondre !
> On te souhaite une très belle continuation dans tes projets avec ta
> marque actuelle. Une future collaboration serait avec grand plaisir,
> n'hésite surtout pas à revenir vers nous si l'occasion se présente !
>
> Sportivement,
> Antoine

**Refus communauté trop petite (prospect <~1k) — code welcome**

> Merci pour ton message {prenom} et pour le partage de ton projet, {accroche projet} 🔥
>
> Pour être transparent avec toi, on travaille avec des profils qui ont
> une communauté déjà bien établie sur les réseaux, et pour l'instant ton
> compte ne correspond pas encore aux critères qu'on recherche pour nos
> partenariats. Ce n'est absolument pas un jugement sur la qualité de ton
> contenu ou de ton projet, mais c'est notre critère actuel.
>
> Ce qu'on peut faire en revanche : je te laisse un code perso {CODE25}
> pour que tu puisses découvrir nos produits avec -25% sur ta commande.
> Et si dans le futur ta communauté se développe, n'hésite pas à revenir
> vers nous, ce sera avec plaisir !
>
> Sportivement,
> Antoine

**Présentation détaillée du programme (§4)**

> On est ravis !
>
> Pour t'expliquer plus en détails, l'objectif du programme ambassadeur
> est que tu représentes la marque en réalisant des posts, stories ou
> tout autre format de ton choix, afin que ton code d'affiliation soit
> utilisé un maximum. En tant qu'ambassadeur, tu reçois un crédit de 20€
> à utiliser sur Impulse Nutrition à chaque fois qu'une commande est
> réalisée avec ton code. Ça te permet de commander autant de
> compléments alimentaires que nécessaire pour ta pratique !
>
> Par la suite, si tout se passe vraiment bien, on pourra naturellement
> évoluer vers un partenariat rémunéré.
>
> Si tu veux plus d'infos, n'hésite pas. En tout cas, ton profil nous
> intéresse beaucoup et on a des produits sympas à te faire tester !
>
> Sportivement,
> Antoine

**Acceptation — demande infos commande (§5)**

Demander **les 4 infos en 1 seul message** (sélection + adresse + mail + téléphone) :

> Trop bien, on est ravi ! 😄
>
> Pour tester les produits, est-ce que tu préfères sélectionner toi-même
> les produits qui t'intéressent sur notre site ou qu'on te concocte un
> pack personnalisé ? Dans les deux cas c'est gratuit pour toi ! Il me
> faudra également une adresse (avec nom + prénom), un email et un
> numéro, je te prépare la commande en suivant !
>
> Sportivement,
> Antoine

**Commande validée + envoi du code affilié (§5.5 — CRITIQUE)**

> La commande est validée et sera expédiée très prochainement !
>
> Je t'ai créé un code affilié perso ({CODE}) qui permettra à ta
> communauté de bénéficier de -15% sur tout le site (sans minimum
> d'achat). **Le code est cumulable avec toutes les autres réductions
> sur les produits.**
>
> Si les produits te plaisent et que tu en parles autour de toi, tu
> cumuleras 20€ de crédit à chaque commande passée avec ton code,
> utilisables pour renouveler tes stocks quand tu veux.
>
> Code : {CODE}
> Lien : https://impulse-nutrition.fr/discount/{CODE}
>
> N'hésite pas si tu as des questions, à très vite !
>
> Sportivement,
> Antoine

**Envoi commande (court, pas de signature)**

> Hâte d'avoir tes retours et bonne dégustation !!

**Demande redeem crédits (§8)**

> Avec plaisir {prenom} ! Tu as actuellement **{credit_value} €** de
> crédit disponible (soit {solde} utilisations × 20€). Tu veux que je
> te crée le code maintenant ? Tu pourras le passer en une seule
> commande sur le site.
>
> Sportivement,
> Antoine

### 6.3 Catalogue micro-messages (Instagram)

**Validation / Enthousiasme** : "Trop bien, on est ravi !!" · "Au top !!" · "Super !!" · "Yes au top !" · "C'est noté je te dis comment je procède !"

**Remerciement** : "Avec plaisir !!" · "Merci à toi !!" · "Merci beaucoup !!"

**Réaction contenu** : "Trop bien merci !! 🔥" · "Au top, merci beaucoup !! 😍" · "Trop cool merci à toi !! 🔥🔥" · "Bravo c'est énorme !! 🔥"

**Accusé de réception** : "Bien reçu merci !" · "C'est bien noté !" · "Aucun soucis c'est bien noté !" · "Entendu ! 😉"

**Rassurance** : "Aucun souci !" · "Prends ton temps !" · "All good"

**Post-commande** : "Hâte d'avoir tes retours et bonne dégustation !!" · "Let's go c'est bon c'est modifié !"

**Clôture** : "Très bonne soirée !!" · "Très bon weekend !!" · "À très vite !"

### 6.4 FAQ — réponses types

**"Comment utiliser mon crédit ?"**
> Tu m'envoies un message avec ce que tu veux commander, et je te fais un code du montant correspondant. Sinon on peut prévoir un call si tu préfères !

**"Combien de personnes ont utilisé mon code ?"**
> [N] utilisation(s) de ton code, bien joué !!

**"Mon code/lien ne marche pas"**
> Je check ça tout de suite ! [vérifier et corriger, puis] C'est réglé, tu peux réessayer !

**"Je peux dépasser un peu le budget de 80€ ?"**
> Le budget c'est 80€ mais ça peut dépasser un petit peu, pas de souci !

**"Le preworkout m'a donné des effets secondaires"**
> C'est normal si c'est ta première prise ! Essaie avec 1/3 ou 1/2 scoop pour commencer, et augmente progressivement. N'hésite pas à me dire comment ça se passe !

**"Je suis libre sur le contenu ?"**
> Oui totalement ! Le format est libre, c'est toi qui gères selon ce qui colle le mieux à ta façon de communiquer. L'essentiel c'est de glisser ton code et ton lien pour que tes abonnés puissent en profiter !

**"C'est un partenariat ponctuel ou long terme ?"**
> L'idée c'est vraiment de bosser sur le long terme ! On commence par un envoi de produits, si les produits te plaisent on te crée un code affilié, et à chaque commande passée avec ton code tu reçois 20€ de crédit chez nous. Et si la collab fonctionne vraiment bien, on peut envisager d'aller plus loin ensemble.

**"Quelle différence entre Whey Isolate et Whey Recovery ?"**
> La Whey Recovery c'est une formule 3-en-1 : whey concentrate + créatine + collagène, pensée pour une récupération complète (musculaire, articulaire et performance). La Whey Isolate c'est de la protéine pure et plus concentrée, idéale si tu veux juste l'apport protéique. Les deux contiennent de la lactase donc pas de souci de digestion !

**"Vos produits contiennent du lactose ?"**
> Nos whey contiennent de la lactase, une enzyme qui aide à digérer le lactose, donc pas de souci de digestion !

### 6.5 Red flags DM (à NE JAMAIS faire)

- ❌ **Drafter sans avoir scanné l'historique complet du thread** (50 msgs min)
- ❌ **Pitcher le programme ambassadeur à un prospect parqué** (code `ACHAB25`/`PGAU25`/`{NOM}25` déjà donné)
- ❌ **Contredire une position d'Impulse précédemment établie** sans acknowledger le changement
- ❌ **Ignorer une rencontre IRL** mentionnée dans le thread
- ❌ **Vouvoyer**
- ❌ **Signer "Antoine"** sur un canal SC
- ❌ **Utiliser des tirets em (`—`)**
- ❌ **Re-coller le pitch ambassadeur** dans une conversation déjà avancée
- ❌ **Promettre** des choses non confirmées (livraison J+1, gratuit illimité)
- ❌ **Oublier `{prenom}`** dans un premier message
- ❌ **Emojis mielleux** : 🙏 ✨ 💖
- ❌ **Surcharger** en 🔥 ou 💪 (max 1 par message)

### 6.6 Draft + go explicite

Mode opératoire strict : **Claude rédige, Antoine valide TOUJOURS avant envoi**. "C'est good" ou "bon raisonnement" ne sont **PAS** des validations d'envoi. Seul "envoie" / "go" / "c'est bon envoie" valide.

Un go global ("go un par un", "on y va") ≠ validation du draft courant. Chaque draft = son propre go ciblé.

### 6.7 Routing par type de message reçu

| Message reçu | Statut (J) | Draft à rédiger |
|---|---|---|
| Réponse positive au pitch | In-cold → In-hot | Second message explication programme |
| Questions sur le programme | In-hot | Réponse + proposition call |
| Envoi coordonnées | In-hot | "C'est noté je te dis comment je procède !" |
| Choix produits / panier | In-hot | Validation : "C'est bien noté !" / "Super choix !" |
| "Déjà pris par une autre marque" | In-cold → Out | Adapter selon sponsor (§3 refus) |
| "Je ne prends pas de compléments" | In-cold | Argument doux + proposition call |
| "Voir avec mon manager" | → Contacter manager | "Bien sûr !" + noter contact |
| Confirmation réception colis | Produits envoyés | "Hâte d'avoir tes retours !!" |
| Feedback positif | Produits envoyés | Enthousiasme court |
| Feedback négatif | Produits envoyés | Empathie + alternative/call |
| Story mentionnant Impulse | Produits envoyés | Réaction courte |
| Story sans code visible | Produits envoyés | Nudge code doux |
| "Merci" (promo/info) | Tout | Micro : "Avec plaisir !!" |
| Demande réassort | Produits envoyés | "Tu veux me mettre ce que tu as besoin par message ? Sinon on s'appelle 😉" |
| Question stats code | Produits envoyés | Chiffre exact : "[N] utilisations, bien joué !!" |
| Problème technique code | Produits envoyés | "Je check ça !" + résolution |
| Demande redeem crédit | Produits envoyés | Voir §7.3 |
| Résultat sportif | Tout | "Bravo c'est énorme !! 🔥" |
| Excuse retard | Tout | "Aucun souci !" / "Prends ton temps" |
| Message vocal (`voice_media`) | Tout | ⚠️ NE PAS DRAFTER — signaler Antoine, L=high |
| Media éphémère (`raven_media`) | Tout | ⚠️ NE PAS DRAFTER — signaler Antoine, L=medium |

### 6.8 Auto-skip si notre côté a répondu en dernier

Si le dernier message du thread est `is_sent_by_viewer=true` (Antoine/Pierre/SC a répondu en dernier), **auto-skip** avec carte condensée 1 ligne. Pas de draft.

### 6.9 Points de friction technique récurrents DM

1. **Bug lien en double** : le template génère parfois `discount/discount/CODE` — toujours vérifier avant envoi
2. **Affiliatly connexion** : problèmes fréquents de login — proposer reset ou renvoi mail
3. **Mail d'avis Judge.me** : arrive souvent en spam ou pas du tout
4. **Erreurs de nom sur les colis** : vérifier l'orthographe avant commande

---

## 7. Runbooks opérationnels condensés

Les runbooks complets ont été distillés ici. Format : recette + gotcha principal.

### 7.1 Créer un code affilié ambassadeur

**Utiliser le tool MCP** `create_affiliate_code(name="florine")` → clone exact ALEXTV :
- `-15%` percentage
- `once_per_customer=true`
- `starts=now`, `ends=null`
- `usage_limit=null`
- `combinesWith { order:false, product:true, shipping:true }`

Pour Paid (-20% type LRA20) : `create_paid_affiliate_code(name="...")`.

**Convention nommage** : `<PRENOM>` ou `<HANDLE>` en majuscules, sans accents ni caractères spéciaux. Ex : `FLORINE`, `ALEXTV`, `DODO`, `JBTRI`, `LRA20`.

**Codes réels en prod (audit 2026-04-13)** :

| Code | price_rule_id | value_type | value | usage_limit | starts_at | type |
|---|---|---|---|---|---|---|
| `ALEXTV` | 2205486154059 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `DODO` | 2199297753419 | percentage | -15.0 | null | 2025-07-22 | Affilié ambassadeur |
| `LRA20` | 2205436543307 | percentage | -20.0 | null | 2025-09-09 | Affilié Paid |
| `TRAILEURSDOTATION` | 2206068539723 | fixed_amount | -200.0 | 6 | 2026-01-15 → 2027-01-31 | Dotation |

### 7.2 Créer un draft order (SAV ou dotation)

**Hard rule : email client OBLIGATOIRE.** Sans email → Shopify confirmation + BigBlue tracking + Affiliatly mapping cassent.

Checklist avant `create_draft_order` :
1. Récupérer l'email (DM Instagram, Gorgias, thread)
2. `search_customers(query=email)` :
   - Existe → passer `customer_id=<integer>` (JAMAIS `customer_email=`)
   - N'existe pas → créer le customer d'abord via `mcp__shopify__create-customer` (firstName, lastName, email, adresse), puis `customer_id`
3. Après création, vérifier `get_draft_order(draft_id)` → `draft_order.email ≠ null` et `draft_order.customer.email` OK

**Fallback** si draft créé sans email (blank customer auto) :
```python
mcp__shopify__update_customer(id=<blank_id>, email="<vrai>", firstName="...", lastName="...")
```
Draft récupère auto l'email au prochain `get_draft_order`.

**Recette canonique SAV** (total 0€) :
```python
draft = create_draft_order(
    line_items=[{"variant_id": ..., "quantity": ...}, ...],
    customer_id=<id>,
    note="Replacement IMPxxxx — motif",
    tags="Service client",
)
update_draft_order(
    draft_order_id=draft["id"],
    applied_discount={"title":"SAV","value_type":"percentage","value":"100.0","description":"SAV"},
    shipping_line={"title":"Expédition gratuite","price":"0.00"},
)
complete_draft_order(draft_order_id=draft["id"], payment_pending=False)
# → Puis fix manuel BigBlue pickup point
```

**Checklist avant `complete_draft_order`** :
- [ ] `tags` = `Service client` OU `Dotation influenceur` (jamais les 2, jamais aucun sur commande gratuite)
- [ ] `applied_discount` 100% si gratuit
- [ ] `shipping_line` "Expédition gratuite" 0.00 si gratuit
- [ ] `note` interne explicite (ref + motif)
- [ ] `line_items` complets (pas d'`update_draft_order` pour ajouter après)
- [ ] Adresse correcte (domicile pour SAV retry)

### 7.3 Calculer et redeem le crédit ambassadeur

**Formule** : `solde = col O (nb_utilisation) − col Q (nb_credit_used)` · `credit_value = solde × 20€`

**Garde-fou** : si `Q > O` → incohérence. Stopper, vérifier le Sheet manuellement, **ne PAS créer de code**.

**Workflow** :

```python
from infra.common.google_sheets import SUIVI_AMB_COLS, get_worksheet, DATA_START_ROW

ws = get_worksheet("Suivi_Amb")
rows = ws.get_all_values()[DATA_START_ROW - 1:]

def find_ambassador(username):
    for i, row in enumerate(rows, start=DATA_START_ROW):
        if len(row) > SUIVI_AMB_COLS["username"] and \
           row[SUIVI_AMB_COLS["username"]].strip().lower() == username.lower():
            return i, row
    return None, None

row_idx, row = find_ambassador("florinebreysse")
nb_total = int(row[SUIVI_AMB_COLS["nb_utilisation"]] or 0)
nb_used = int(row[SUIVI_AMB_COLS["nb_credit_used"]] or 0)
prenom = row[SUIVI_AMB_COLS["prenom"]] or "X"

solde = nb_total - nb_used
if solde <= 0:
    raise SystemExit(f"solde invalide : {solde}")
credit_value = solde * 20
```

**Pattern Shopify du code crédit** (convention `[PRENOM]-CREDIT`) :

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

`combinesWith` GraphQL : probablement `productDiscounts:true, shippingDiscounts:true, orderDiscounts:false` (cohérent ALEXTV).

**Mise à jour Sheet** :
- Avant commande : col P (`code_credit`) ← `FLORINE-CREDIT`
- Après commande : col Q (`nb_credit_used`) ← `Q + solde` (nouveau Q = O)

**Tag de la commande générée** : `Dotation influenceur` (voir §5.4).

**Audit régulier** : mensuellement, pour tout ambassadeur avec `solde > 5` (≥100€) qui n'a pas redeem depuis ≥3 mois → DM proposant le redeem.

### 7.4 Pattern code dotation `[NOM]DOTATION`

Utilisé par l'ambassadeur lui-même pour redeem sa dotation mensuelle (≠ code affilié ci-dessus utilisé par ses followers).

```
title: TRAILEURSDOTATION
value_type: fixed_amount
value: -200.0           ← montant mensuel
customer_selection: all
target_type: line_item
target_selection: all
allocation_method: across
usage_limit: 6          ← nombre de mois (1 redemption/mois)
once_per_customer: false
starts_at: <début contrat>
ends_at: <fin contrat>
```

Règle de calcul pour un contrat D mois × M €/mois :
- `value = -M.0`
- `usage_limit = D`
- `starts_at` = début contrat, `ends_at` = fin (D mois plus tard)

⚠️ Ne pas confondre avec les utilisations cibles du code **affilié** (mesuré dans col O de Suivi_Amb).

`combinesWith.orderDiscounts: false`.

### 7.5 Pattern code SAV `[PRENOM]-SAV`

Geste commercial SAV — code qui offre produit gratuit sur panier client :

- `value_type: percentage`, `value: -100.0`
- `entitled_product_ids: [shaker, bidon]` (restreint aux produits gratuits)
- `usage_limit: 1`, `once_per_customer: true`
- `combinesWith.orderDiscounts: true, productDiscounts: true, shippingDiscounts: true`

Le client place sa commande avec ce code → tagguer la commande **`Service client`**.

### 7.6 DM check + onboarding condensé

**Check DMs** :
1. `list_chats(100)` — ⚠️ le `last_message` peut être obsolète, **ne jamais s'y fier pour drafter**
2. Cross-ref avec Suivi_Amb + Suivi_Dot + Suivi_Paid
3. `list_messages(thread_id=..., limit=10)` pour chaque thread actionnable — **règle absolue avant tout draft**
4. Classifier : URGENT / À RÉPONDRE / À NOTER / RAS (auto-skip si notre côté dernier à écrire)

**Erreurs passées (apprentissage)** :
- briannicklen : `list_chats` montrait inbound du 31/03 mais Antoine avait déjà répondu ET Brian avait accepté le 07/04. On a failli drafter pour un truc réglé.
- shadowwtri, frerotrun1997 : déjà refusés avec code PGAU25, pas vu sans lire le thread.

**Onboarding nouveau ambassadeur (dotation)** :
1. Phase DM : proposer (80-100€ dotation + code affilié -15% + seuil renouvellement) → accepte → demander les 4 infos en 1 message
2. Phase commande : `get-products(searchTitle=...)` pour variant_id → `create_draft_order` avec tag `Dotation influenceur` + discount 100% + shipping 0€ → présenter récap à Antoine → `complete_draft_order`
3. Phase code : `create_affiliate_code(name="prenom")` (clone ALEXTV)
4. Phase Sheet : ajouter ligne Suivi_Dot (Name, Statut, Type, Mail, Numéro, Prénom, Nom, Insta, Code, Date début, Durée, Dotation €, Seuil renouvellement, Adresse)
5. Phase DM final : envoyer code + lien + infos

---

## 8. Glossaire métier

| Terme | Signification |
|---|---|
| **Affiliatly** | Plateforme de suivi codes affiliés + utilisations. Sync manuel vers col O Suivi_Amb (`nb_utilisation`) |
| **Code affilié** | Code -15% personnel (ex : `FLORINE`, `ALEXTV`). Col N Suivi_Amb. Redeemable ∞ times, `once_per_customer` |
| **Crédit** | 20€ débloqués par utilisation du code affilié |
| **Code crédit** | Code Shopify unique `-X€` fixe, 1 utilisation max. Créé à la demande via formule `(O−Q)×20€`. Col P Suivi_Amb |
| **Code welcome** | Code `-25%` first-order. `ACHAB25` (Antoine), `PGAU25` (Pierre Gautier). Format `{NOM}25`. Donné aux prospects trop petits = **parqués** |
| **Prospect parqué** | Prospect qui a reçu un code welcome dans un échange antérieur. Jamais re-pitch comme nouveau contact → relance contextualisée (§3.3) |
| **Dotation** | Envoi gratuit de produits (€/mois × durée ↔ N utilisations cibles). Contrat Suivi_Dot |
| **Code dotation** | Code `[NOM]DOTATION` utilisé par l'ambassadeur pour redeem sa dotation mensuelle (ex `TRAILEURSDOTATION`) |
| **Enveloppe** | Budget produits alloué (~80-100€ initial) |
| **Tag `Service client`** | Commande SAV/replacement. Sort du CA HCS (coût SAV) |
| **Tag `Dotation influenceur`** | Envoi gratuit ambassadeur / commande avec code crédit. Sort du CA HCS (coût marketing) |
| **Seuil renouvellement** | Utilisations à atteindre pour renouveler la dotation. Col AC Suivi_Dot. Ex : 14 util sur 4 mois = 14€/mois |
| **Contacter manager** | Prospect qui mentionne un agent. Statut col J Suivi_Amb. Contact par mail |
| **In-cold** | Prospect pitch envoyé, pas de réponse. Progression vers In-hot si répond |
| **In-hot** | Prospect qui a répondu positivement. En discussion |
| **Produits envoyés** | Draft complétée, colis expédié. Mode réactif |
| **Formule crédit** | `(O − Q) × 20€` où O = total utilisations, Q = utilisations consommées |
| **RAS** | Rien à signaler |
| **Gamme Au Quotidien** | Gamme bien-être/santé (collagène, magnésium, glycine, glutamine, vit C) |
| **Gamme Sport / Performance** | Protéines, effort, électrolytes, preworkout (whey, BCAA, créatine, isotoniques) |
| **WAX** | Outil WhatsApp qui pousse les messages dans Gorgias avec tag `WAX`. Tone SC vouvoiement formel |

---

## 9. Quirks techniques transverses

### 9.1 Bug Excel "sériel" dans colonnes date du Sheet

Si une colonne est formatée "date" et qu'on y entre un nombre (ex : dotation `150`), Google Sheets l'affiche comme `29/05/1900` (serial 150). **Fix** : réécrire la valeur numérique correcte via `batch_update_cells`.

### 9.2 Limitation `update_draft_order` Shopify

Ne permet **pas** de modifier les `line_items` d'un draft. Si on doit ajouter/retirer un produit après création (ex : bidon en geste commercial) :

1. `delete_draft_order(draft_id)`
2. `create_draft_order(<full set of line_items>)`
3. Réappliquer `applied_discount`, `shipping_line`, `tags`, `note`

→ Toujours préparer la liste line_items complète AVANT le premier appel.

### 9.3 Pickup point BigBlue non reporté

Après `complete_draft_order`, BigBlue ne reçoit pas systématiquement l'info du pickup point. **Fix** : aller sur l'UI BigBlue, trouver la commande, régler manuellement le pickup point.

Pas de fix automatique côté MCP.

### 9.4 Refunds non implémentés côté MCP

Les remboursements (partiels ou totaux) passent par l'UI Shopify ou directement via API REST `/orders/{id}/refunds.json`. Le MCP `shopify_orders` n'expose pas d'outil refund.

### 9.5 Service account Google Drive

- Path : `~/.config/google-service-account.json`
- A read+write sur le folder `InfluenceContract` (ID `1dxT2gSAm6tcnd8Ck6hXxPDS5yieMuj4x`)
- Utilisé par `infra/common/google_sheets.py` (Sheets) et `infra/common/google_drive.py` (Drive contracts)

### 9.6 Timestamps Instagram en microsecondes

Pour les scripts CLI `instagram_dm_mcp/*.py` :

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
date_str = dt.strftime("%d/%m/%Y")
```

### 9.7 Helpdesk BigBlue fragile

4 tools du MCP BigBlue (list/get/create/reply support tickets) sont fragiles — reverse-engineering du gRPC-Web de l'admin UI. Messages **obligatoirement en français** (leur SOP). Fallback Playwright si API cassée.

### 9.8 Search Gorgias retourne 405

Le native `/api/search` n'existe pas. `search_tickets` (MCP custom) = email lookup + substring fallback. Le pull protocol 100+ est le filet de sécurité (voir §5.2).

### 9.9 Col O / Q incohérentes (Q > O)

Crédit invalide. Stopper, vérifier manuellement, **ne PAS créer de code**.

### 9.10 Rate limiting Instagram

Dans `infra/common/instagram_client.sleep_random(min, max)` :
- Reads inter-thread : `sleep_random(3, 8)`
- Cooldown tous les 10 reads : `sleep_random(15, 30)`
- Sends : `sleep_random(5, 10)`

### 9.11 Draft order email obligatoire

Sans email client, Shopify confirmation + BigBlue tracking + Affiliatly mapping cassent. **Checklist** : voir §7.2.

### 9.12 `list_chats` last_message obsolète

`list_chats` (MCP Instagram) montre un `last_message` qui peut être périmé. **Ne JAMAIS se fier** au `last_message` pour drafter. Toujours `list_messages(thread_id, limit≥10)` avant draft.

### 9.13 Sessions Instagram

- Sessions stockées dans `instagram_dm_mcp/*_session.json` (gitignored)
- Si expirée → `python instagram_dm_mcp/create_session.py`
- 2 comptes :
  - `impulse_nutrition_fr` — principal (DMs ambassadeurs, campaigns)
  - `antman.lass` — veille (lecture concurrents, dormant)
- Helper unique : `infra.common.instagram_client.get_ig_client(account="impulse"|"veille")`

### 9.14 Nommage codes Shopify

Pas de codes hors convention. Majuscules sans accents ni caractères spéciaux (sauf `-` pour SAV/CREDIT).

| Type | Format | Exemple |
|---|---|---|
| Affilié ambassadeur | `<PRENOM>` ou `<HANDLE>` | `FLORINE`, `ALEXTV`, `DODO`, `JBTRI` |
| Affilié Paid | variable | `LRA20` |
| Dotation | `<HANDLE>DOTATION` | `TRAILEURSDOTATION` |
| Crédit ambassadeur | `<PRENOM>-CREDIT` | `FLORINE-CREDIT` |
| SAV client | `<PRENOM>-SAV` | `MARTIN-SAV` |
