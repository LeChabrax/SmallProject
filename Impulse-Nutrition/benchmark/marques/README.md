# benchmark/marques — source de vérité du benchmark abonnement

Un dossier par marque concurrente, 8 marques dans le périmètre mission (Nutri&Co, Nutrimuscle, Novoma, Nutripure, Cuure, Decathlon, Aqeelab, MyProtein).

## Structure par marque

```
nutriandco/
├── data.json        # source de vérité — 4 rubriques du brief mission
├── notes.md         # verbatims, vérifs live, décisions, questions ouvertes
├── sources.md       # URLs citées avec date + phrase extraite
└── screenshots/
    ├── homepage.png
    ├── product_sub.png
    └── ...
```

## Règle de base

**`data.json` est la source de vérité. `../master_data.json` est un artefact régénéré.**

Ne jamais éditer `master_data.json` à la main — tes changements seront écrasés au prochain `python3 benchmark/build_master.py`.

## Schéma `data.json`

Aligné sur la structure exacte du brief mission (section "Structure du benchmark par marque") :

- `brand`, `slug`, `url`, `has_subscription`
- `modele_commercial` : `remise_pct`, `frequencies`, `flexibility`, `engagement_min`, **`livraison_abo`** (nouveau champ)
- `perimetre_produit` : `scope`, `exclusions`, `produits_sample`, `ticket_moyen_estime_eur`
- `ux_page_produit` : `wording_cta`, `wording_pitch`, `placement_module`, `dedicated_page`, `homepage_mention`, `navigation_mention`, `email_mention`, `screenshots_files`
- `evaluation` : `strengths`, `weaknesses`, `score_ux`, **`score_offre_commerciale`**, **`score_pertinence_vs_impulse`**, **`score_global`** (en gras = nouveaux /5 du brief)
- `logistique`, `tech`, `avis` : préservés tels quels depuis le master
- `_extras` : bucket lossless qui capture tous les champs du master historique non mappés dans le schéma canonique (ex: `note`, `unique_selling_point`, `loyalty_program`, `onboarding_flow`, `modify_note`). Réinjectés dans `master_data.json` par `build_master.py`.
- `_meta.audit_status` : `raw` (non vérifié) / `needs_review` (incohérences détectées) / `verified_live` (FAQ officielle consultée)

## Scripts associés

| Script | Rôle |
|---|---|
| `../build_master.py` | Lit les 8 `marques/<brand>/data.json` + `_transversal.json` → écrit `../master_data.json` au format historique. À lancer après toute modification manuelle. |
| `../scripts/split_master_to_brands.py` | Script de migration one-shot depuis `../master_data.json.backup`. **Idempotent** : skip les marques déjà en `audit_status=verified_live` ou `needs_review` pour protéger les corrections manuelles. |

## Workflow d'une revue marque

1. Ouvrir `marques/<brand>/data.json` et `notes.md`
2. Vérifier les champs en live (FAQ officielle, page abo, FAQ Zendesk, checkout abonné)
3. Ajouter les URLs + citations dans `sources.md`
4. Logger les corrections dans `notes.md` (tableau avant/après)
5. Corriger les valeurs dans `data.json`
6. Passer `_meta.audit_status` à `verified_live`
7. Lancer `python3 benchmark/build_master.py` pour régénérer le master agrégé
8. Vérifier que `python3 benchmark/generate_html_report.py` régénère sans erreur

## Workflow split ↔ build (round-trip)

Le split a été exécuté une fois depuis `master_data.json.backup` (l'original intact). Il n'est pas censé être rejoué en production — il sert uniquement de filet de sécurité si on veut repartir de zéro sur une ou plusieurs marques. Si besoin : `rm benchmark/marques/<brand>/{data.json,notes.md,sources.md}` puis `python3 benchmark/scripts/split_master_to_brands.py` (les screenshots ne sont pas touchés).

Le build (`build_master.py`) est au contraire lancé **à chaque modification manuelle** des `data.json`.

## Statut audit (au 2026-04-15)

| Marque | Status | Dernière vérif |
|---|---|---|
| Nutri&Co | ✅ verified_live | 2026-04-15 (FAQ Zendesk) |
| Nutrimuscle | ⚪ raw | — |
| Novoma | ⚪ raw | — |
| Nutripure | ⚪ raw | — |
| Cuure | ⚪ raw | — |
| Decathlon | ⚪ raw | — |
| Aqeelab | ⚪ raw | — |
| MyProtein | ⚪ raw | — |
