# Reference — Google Sheet Schema

**Spreadsheet ID** : `1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4`
**Audit date** : 2026-04-13
**Source of truth (code)** : [`common/google_sheets.py`](../common/google_sheets.py)

This doc describes every tab and every column we read or write. If the
sheet changes, update `common/google_sheets.py` and this doc together — the
scripts import the constants, so they stay in sync by construction.

> **Row layout for `Suivi_Amb`, `Suivi_Dot`, `Suivi_Paid`**:
> - Row 1 = section labels (`Contact`, `Info de base`, `Infos athlètes`)
> - Row 2 = metadata (`Not for LLM`)
> - **Row 3 = headers**
> - Row 4+ = data
>
> `VeilleConcu` is a flat tab: row 1 = headers, row 2+ = data.

---

## Tabs inventory

The spreadsheet has 22 tabs in total. Those we actively read/write:

| Tab | Role | Constants |
|---|---|---|
| `Suivi_Amb` | Pipeline ambassadeur entrée + affiliation pure | `SUIVI_AMB_COLS` |
| `Suivi_Dot` | Dotation mensuelle (S/M/L) | `SUIVI_DOT_COLS` |
| `Suivi_Paid` | Contrats rémunérés (fixe + variable) | `SUIVI_PAID_COLS` |
| `VeilleConcu` | Competitor tracking | `VEILLE_COLS` |
| `Analyses` | KPIs + top performers (formulas only) | — |
| `AdHoc` | Automation roadmap (P1/P2/P3) | — |
| `StratAmba` | Partnership tiers doc (static) | — |

The other tabs (`Dashboard`, `Calandrier_Paid`, `OneShot`, `DB`, `Archive`,
`Helper`, `DB_Product_All`, `HelperPrice`, `DB_Primelis`, `Tools`,
`Export_AMBA/PAID`, `Export_Code`, `Message_type`, `Message_type_hide`,
`Analyses (2)`) are not touched by any script. Treat as read-only legacy.

---

## `Suivi_Amb` (pipeline ambassadeur)

42 columns. Data starts at row 4.

| Col | Idx | Semantic key | Header |
|---|---|---|---|
| A | 0 | `type` | Type |
| B | 1 | `message` | Message |
| C | 2 | `premier_message` | Premier Message |
| D | 3 | `commandes` | Commandes |
| E | 4 | `relance` | Relance |
| F | 5 | `avis` | Avis |
| G | 6 | `mention_bio` | Mention Bio |
| H | 7 | `ig_link` | IG link |
| **I** | 8 | **`username`** | Compte @ |
| **J** | 9 | **`statut`** | Statut |
| **K** | 10 | **`action`** | Action/Commentaire |
| **L** | 11 | **`priorite`** | Priorités identifiées |
| **M** | 12 | **`campagne`** | Campagne |
| **N** | 13 | **`code_affilie`** | Code affiliation |
| O | 14 | `nb_utilisation` | Nb Utilsation |
| P | 15 | `code_credit` | Code crédit |
| Q | 16 | `nb_credit_used` | Nb Credit Used |
| R | 17 | `lien_affilie` | Lien affiliation |
| S | 18 | `taux_engagement` | Taux engagement |
| T | 19 | `affiliatly` | Affiliatly |
| U | 20 | `mail_amb` | Mail Ambassadeur |
| V | 21 | `bio` | Bio |
| W | 22 | `sport` | Sport |
| X | 23 | `sponsor` | Sponsor |
| Y | 24 | `followers_k` | Followers (k) |
| Z | 25 | `date_premier_contact` | Date |
| AA | 26 | `nb_story` | Nb Story |
| AB | 27 | `nb_post` | Nb post |
| AC | 28 | `colonne_32` | Column 32 |
| AD | 29 | `nom` | Nom |
| **AE** | 30 | **`prenom`** | Prenom |
| AF | 31 | `mail` | Mail |
| AG | 32 | `numero` | Numéro |
| AH | 33 | `adresse` | Adresse |
| AI | 34 | `info_contract` | Info contract |
| **AJ** | 35 | **`id_influ`** | ID Influ |
| AK | 36 | `contract` | Contract |
| AL | 37 | `date_1ere_commande` | Date 1ère commande |

### Drift notes (pre-refactor bugs)

Before the 2026-04-13 refactor, several scripts hardcoded incorrect indices:

| Script | Wrong | Fix |
|---|---|---|
| `run_campaign.py` | `row[27]` as `prenom` | `row[30]` (`SUIVI_AMB_COLS["prenom"]`) |
| `audit_ambassadors.py` | `row[32]` as `id_influ` | `row[35]` (`SUIVI_AMB_COLS["id_influ"]`) |
| `veille_concurrents.py` | `row[19]` as `sponsor` | `row[23]` (`SUIVI_AMB_COLS["sponsor"]`) |
| `update_priorities.py` | `row[32]` as `id_influ` | `row[35]` |

Scripts rewired in Phase 1.5 now import from `common/google_sheets.py`, so
there is only one place to update if the sheet changes.

---

## `Suivi_Dot` (dotation mensuelle S/M/L)

32 columns. Data starts at row 4.

| Col | Idx | Key | Header |
|---|---|---|---|
| A | 0 | `name` | Name |
| B | 1 | `management` | Management |
| C | 2 | `statut_deal` | Statut Deal |
| D | 3 | `type` | Type (S/M/L) |
| E | 4 | `action` | Action / Com |
| F | 5 | `mail` | Mail |
| G | 6 | `numero` | Numéro |
| H | 7 | `prenom` | Prénom |
| I | 8 | `nom` | Nom |
| J | 9 | `affiliatly` | Affiliatly |
| K | 10 | `code_dotation` | Code Dotation |
| L | 11 | `id_influ` | ID Influ |
| M | 12 | `insta` | Insta |
| N | 13 | `tiktok` | @TikTok |
| O | 14 | `youtube` | @YT |
| P | 15 | `strava` | @Strava |
| Q | 16 | — | — |
| R | 17 | `code` | Code |
| S | 18 | `util_ytd` | Util YTD |
| T | 19 | `kf_actual` | kF Actual |
| U | 20 | `evolution` | Evolution |
| V | 21 | `whitelisting` | Whitelisting |
| W | 22 | — | — |
| X | 23 | `followers_k_init` | (k)Insta Init |
| Y | 24 | `debut` | Début |
| Z | 25 | `fin` | Fin |
| AA | 26 | `duree` | Durée |
| AB | 27 | `dotation_eur` | Dotation (€) |
| AC | 28 | `seuil_renouvellement` | Seuil renouvellement |
| AD | 29 | `agreement` | Agreement |
| AE | 30 | `pdf` | PDF |
| AF | 31 | `adresse` | Adresse |

---

## `Suivi_Paid` (contrats rémunérés)

39 columns. Data starts at row 4.

| Col | Idx | Key | Header |
|---|---|---|---|
| A | 0 | `name` | Name |
| B | 1 | `management` | Management |
| C | 2 | `statut_deal` | Statut Deal |
| D | 3 | `type` | Type |
| E | 4 | `action` | Action / Com |
| F | 5 | `mail` | Mail |
| G | 6 | `prenom` | Prénom |
| H | 7 | `nom` | Nom |
| I | 8 | `affiliatly` | Affiliatly |
| J | 9 | `insta_name` | @InstaName |
| K | 10 | `insta_id` | @Insta ID |
| L | 11 | `tiktok` | @TikTok |
| M | 12 | `youtube` | @YT |
| N | 13 | `date_derniere_cmd` | Date dernière commande |
| O | 14 | — | — |
| P | 15 | `code` | Code |
| Q | 16 | `util` | Util |
| R | 17 | `kf_actual` | kF Actual |
| S | 18 | `evolution` | Evolution |
| T | 19 | `whitelisting` | Whitelisting |
| U | 20 | — | — |
| V | 21 | `followers_k_init` | (k)Insta Init |
| W | 22 | `fixe` | Fixe (€ HT) |
| X | 23 | `var_prov` | Var. prov. |
| Y | 24 | `budget_total` | Budget total |
| Z | 25 | `debut` | Début |
| AA | 26 | `fin` | Fin |
| AB | 27 | `duree` | Durée |
| AC | 28 | `eur_pct` | € / % |
| AD | 29 | `dotation_eur` | Dotation (€) |
| AE | 30 | `seuil_util` | Seuil util |
| AF | 31 | `bio_linkt` | Bio/LinkT |
| AG | 32 | `a_la_une` | à la une |
| AH | 33 | `reels_post` | Réels/post |
| AI | 34 | `stories` | Stories |
| AJ | 35 | `youtube_obl` | Youtube |
| AK | 36 | `strava_obl` | Strava |
| AL | 37 | `tiktok_obl` | Tiktok |
| AM | 38 | `pdf` | PDF |

---

## `VeilleConcu`

27 columns. Header row 1, data row 2+.

See `VEILLE_COLS` in `common/google_sheets.py`. Key columns used by
`veille_concurrents.py`:

| Col | Idx | Key |
|---|---|---|
| A | 0 | `marque` |
| B | 1 | `instagram` |
| C | 2 | `instagram_id` |
| F | 5 | `followers` |
| I | 8 | `engagement_pct` |
| X | 23 | `ambassadeurs_communs` |
| AA | 26 | `derniere_maj` |

---

## `StratAmba` (partnership tiers — static reference)

Static table describing the 4 partnership tiers. Not scripted against.

| Type | Dotation | Période | Util. min | Paiement par défaut |
|---|---|---|---|---|
| S | 80 € | 4 mois | 12 | Code utilisable 1×/mois |
| M | 100 € | 4 mois | 15 | Code utilisable 1×/mois |
| L | 150 € | 4 mois | 18 | Code utilisable 1×/mois |
| Affiliation | — | — | 2 (min) | 1 utilisation = 20 € |

Details and full contract models → [`reference_contract_types.md`](reference_contract_types.md).
