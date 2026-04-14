# Benchmark concurrents — Whey

Benchmark prix des concurrents whey d'Impulse Nutrition. Dataset brut, sourcé et reproductible, qui étend le format `benchmark_whey_vitavea.xlsx` avec une couche discount (codes influenceurs / promos permanentes) pour comparer les prix effectifs et pas seulement les prix catalogue.

## Fichiers

| Fichier | Contenu |
|---|---|
| `whey_catalog.json` | Source de vérité — un objet par SKU whey (14 marques, ~55 SKUs). Champs bruts uniquement, pas de dérivés. |
| `discounts.json` | Politique de discount par marque (1ère commande, codes influenceurs, fréquence promo). |
| `agent_collected.json` | Dump intermédiaire produit par l'agent de collecte Playwright — gardé pour audit et re-merge si besoin. |
| `seed_from_xlsx.py` | Parse `../benchmark_whey_vitavea.xlsx` + hardcode Impulse → seed initial de `whey_catalog.json`. |
| `merge_collected.py` | Merge idempotent de `agent_collected.json` dans `whey_catalog.json`. |
| `build_whey_xlsx.py` | Génère `benchmark_whey_concurrent.xlsx` (4 onglets) depuis `whey_catalog.json` + `discounts.json`. |
| `benchmark_whey_concurrent.xlsx` | Export final, lisible humain. Regénérable à tout moment. |

## Schéma `whey_catalog.json`

Chaque SKU = un objet dans `products[]`. Les prix dérivés (€/kg, €/portion, €/g protéine, prix effectif) **ne sont pas stockés** — ils sont recalculés au build depuis les champs bruts.

Champs obligatoires : `brand`, `product_id`, `product_name`, `type`, `format_g`, `flavor`, `price_catalog_ttc_eur`, `source_url`, `snapshot_date`.

Champs nutritionnels (peuvent être `null` si le site ne les publie pas clairement) : `protein_pct_100g`, `protein_per_serving_g`, `serving_size_g`, `servings_per_pack`, `bcaa_per_serving_g`, `carbs_per_serving_g`, `fat_per_serving_g`, `lactose_level`.

Type autorisés : `isolat_natif`, `isolat_fromagere`, `concentrat_natif`, `concentrat_fromagere`, `mix_concentrat_isolat`, `clear_hydrolysat`.

## Schéma `discounts.json`

```json
{
  "discounts": {
    "<brand>": {
      "first_order_code_pct": int | null,
      "first_order_code_example": "NEW15" | null,
      "influencer_code_typical_pct": int | null,
      "influencer_code_examples": [
        {"code": "XYZ", "influencer": "@handle", "pct": 30, "source_url": "...", "seen_at": "YYYY-MM-DD"}
      ],
      "permanent_promo_frequency": "quasi-permanent" | "ponctuel" | "aucun",
      "stacking_rules": "...",
      "source_urls": ["..."],
      "snapshot_date": "YYYY-MM-DD",
      "note": "..."
    }
  }
}
```

## Règles de calcul

- **TVA FR 20 %** : les prix sont TTC (côté client). Conversion TTC → HT via `benchmark/constants.py::retail_ht()` si besoin.
- **Prix / kg** : `prix_catalog / (format_g / 1000)`.
- **Prix / g protéine** : `prix_catalog / (servings_per_pack × protein_per_serving_g)` — métrique de vraie value-for-money.
- **Prix effectif P50** : `prix_catalog × (1 − P50 / 100)` où P50 = remise médiane de la marque (50e percentile sur la distribution des codes actifs).
- **Prix effectif P90** : idem avec le P90 (90e percentile = remise habituelle chez un client averti).
- **Arôme pivot** : chocolat par défaut. Si une marque ne publie pas sa whey en chocolat, on prend l'arôme par défaut de la page.

## Formules Excel dynamiques (live)

Les onglets **Benchmark détaillé** et **Synthèse prix** contiennent des **formules Excel** (pas des valeurs figées). Si tu modifies un prix catalogue, un format, un nombre de portions, ou une remise dans l'onglet `Discounts par marque`, **tous les dérivés se recalculent live** à l'ouverture du fichier.

- Onglet 1 : 715 formules (13 par SKU × 55 SKUs) — prix/kg, prix/portion, prix/g prot, remises P10/P50/P90/Max (via VLOOKUP sur l'onglet Discounts), prix effectif P50/P90/max, prix effectif /kg et /g prot.
- Onglet 2 : 550 formules (10 par SKU × 55 SKUs) — mêmes dérivés, format ligne par SKU.
- Onglet 3 Discounts par marque = **source de vérité** pour les remises. Si tu changes le P50 de MyProtein ici, tous les prix effectifs MyProtein dans les 2 autres onglets se mettent à jour.
- Onglet 4 Classement = **SNAPSHOT figé** au build. L'ordre du tri (€/g prot P50 croissant) est calculé une seule fois. Pour rafraîchir après modification, lancer `python3 build_whey_xlsx.py`.

## Sources

- **Impulse Nutrition** : Shopify MCP + `impulse-nutrition.fr` (navigation manuelle pour le grammage).
- **Nutripure, Nutrimuscle, MyProtein, Bulk, Decathlon** : backport depuis `../benchmark_whey_vitavea.xlsx` (dataset HAVEA interne, avril 2026).
- **Eric Favre, EAFIT, Aqeelab, Nutri&Co, Prozis, Foodspring, ESN, BiotechUSA** : collecte Playwright via agent — voir `agent_collected.json` pour audit.
- **Discounts** : collecte via Dealabs, Reddit, Google, Instagram (bios d'ambassadeurs partenaires). Chaque code documenté a une `source_url` et une date.

## 2e passe — enrichissements round 2 (2026-04-14)

Les trous nutrition et le prix Prozis 2kg ont été comblés via sources alternatives :

- **Prozis 100% Real Whey 2000g** — prix réel **62,99 €** confirmé (WebFetch direct prozis.com), remplace l'estimation 69,99 €.
- **Nutrition Prozis (5 SKUs)** — source principale Open Food Facts + pages marketing Prozis (Real Whey concentrate = 71% protéines, Real Whey Isolate = 86%, Hydro Isolate ≈ 88%, Zero Diet ≈ 80%).
- **Aqeelab Whey Native** — 94% protéines (nom produit explicite), BCAA calculé depuis le claim "22g BCAA / 100g protéines" sourcé nabfit.fr.
- **Foodspring Whey Protein 750g** — 81% protéines (fddb.info mirror shop-apotheke.com), serving 30g = 24,3g protéines.
- **EAFIT Mega Whey** — formule muscle-mass, portion 60g = 44g protéines + 1,5g créatine (eafit.com officiel).

**Discounts recalibrés** — l'agent research (Dealabs contourné via influenceur.promo, kotag.co, influencercodes.de, suppwiser.de) a démontré que mes valeurs initiales sous-estimaient lourdement les mastodontes :

| Marque | Avant (typical) | Après P50 / P90 / Max | Commentaire |
|---|---|---|---|
| MyProtein | 35 % | **42 % / 50 % / 55 %** | Catalogue fictif. Client averti paye 50 % du catalogue. |
| Bulk | 30 % | **45 % / 45 % / 45 %** | Programme monolithique à 45 %, 20+ ambassadeurs au même taux. |
| EAFIT | 20 % | **32 % / 32 % / 35 %** | Programme upgradé (suffixe *32 sur 8+ codes récents). |
| Prozis | 15 % | **10 % / 20 % / 50 %** | P50 bas (10 % dominant) mais flash sales 19YEARS/MADNESS → 50 %. |
| Foodspring | 15 % | **15 % / 20 % / 30 %** | Confirmé, très homogène (60+ codes suffixe *FSG à 15 %). |
| ESN | 20 % | **20 % / 25 % / 30 %** | Confirmé, codes DE uniformes. |
| BiotechUSA | 15 % | **15 % / 20 % / 30 %** | Confirmé, programme TRND 15 % standard. |
| Eric Favre | 10 % | **10 % / 15 % / 20 %** | Confirmé, programme ambassadeur modeste. |

Nouveau champ `effective_price_pct` dans `discounts.json` = `100 − P50`, soit le % du prix catalogue réellement payé par un client averti. Pour MyProtein c'est **52 %**, pour Bulk **55 %**, pour Nutripure **100 %** (aucun discount).

## Cas particuliers encore à auditer

- **Prozis Zero Diet Whey**, **Prozis Hydro Isolate**, **Prozis Real Whey Isolate** — valeurs nutritionnelles sont des **estimations cohérentes avec la formule** (isolat / hydrolysat = 80-88 % protéines) mais sans packaging scan direct. À vérifier si usage stratégique.
- **BCAA non documenté** : 10 SKUs sans BCAA/portion (Prozis concentrate + Bulk Whey Protein + Eric Favre Whey Zero + Foodspring). Probablement disponible sur les labels mais pas dans les DB publiques scrapables.
- **Couverture lactose** : 42/55 SKUs (76 %) — les 13 restants sont principalement des concentrates dont le label ne précise pas.

## Workflow

```bash
# 1. Seed initial (une seule fois après le setup)
python3 seed_from_xlsx.py

# 2. Collecter les marques manquantes → écrit agent_collected.json
#    (fait par l'agent de collecte Playwright dispatché depuis Claude)

# 3. Merger dans le catalog (idempotent)
python3 merge_collected.py

# 4. Générer l'xlsx final
python3 build_whey_xlsx.py
```

## Hors scope phase 1

- Autres catégories Impulse (créatine, BCAA, preworkout, électrolytes, santé, snack, accessoire).
- Reviews clients / notes Trustpilot.
- Historique des prix (un seul snapshot).
- Marques non-whey (Mule Bar, Meltonic, TA Energy, Nutrimea, Cuure… — voir plan pour la liste complète d'exclusions).
