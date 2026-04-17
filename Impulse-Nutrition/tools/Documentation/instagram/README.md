# Workflows Instagram DM — Documentation opérationnelle

> Workflows éprouvés lors de la session Instagram du **17/04/2026**. Chaque fichier documente un cas réel traité de A à Z avec le prospect + les actions Shopify/Sheet + les DM verbatim envoyés. Source de vérité pour reproduire ces flows en confiance.

## Comment utiliser cette doc

1. Identifier ta situation dans le **tableau de routage** ci-dessous → ouvrir le workflow correspondant
2. Le workflow détaille : déclencheur / flow technique / exemple verbatim / red flags
3. Les `conventions/` cristallisent les règles transversales (code naming, tone)
4. Les `runbooks/` = recettes techniques copier-collables (Shopify, etc.)

## Tableau de routage

| Situation prospect                                         | → Workflow                                          | Exemple session |
|------------------------------------------------------------|-----------------------------------------------------|-----------------|
| Accepte le pitch s2/s4, <20k followers, demande dotation   | [01-onboarding-oneshot-80-100e](./workflows/01-onboarding-oneshot-80-100e.md) | Simon, Thomas Bonnot, Maxime Croisé |
| Pro athlète / call valide dotation récurrente              | [02-dotation-recurrente-4mois](./workflows/02-dotation-recurrente-4mois.md) | Yannick (ALTIZ + ALTIZDOTATION) |
| Accepte le pitch mais demande dimension financière/paid    | [03-contre-offre-paid-request](./workflows/03-contre-offre-paid-request.md) | Alexia Bailly (pro triathlète) |
| Ambassadeur actif mais 0 utilisation code                   | [04-credit-oneshot-ambassadeur-inactif](./workflows/04-credit-oneshot-ambassadeur-inactif.md) | Kiki (KIKISPORTIVEDOTATION 20€) |
| Inbound <2500 followers                                     | [05-parquage-auto-under-2500](./workflows/05-parquage-auto-under-2500.md) | 5 parqués : Mickael, Aurélien, Charlotte, Thomas L, Maël |
| Thread silencieux >10j, acceptation passée                  | [06-relance-long-silence](./workflows/06-relance-long-silence.md) | Donavan Grondin 28j, Pierre Berdat 7 mois |
| Call à caler (timezone / soir / midi)                       | [07-call-cross-timezone](./workflows/07-call-cross-timezone.md) | Pablo Indonésie, Delphée, Sophia |

## Conventions

- [**code-naming.md**](./conventions/code-naming.md) — `[NAME]`, `[CODE]DOTATION`, `[NAME]-PAID`, `[PRENOM]-SAV`, welcome codes
- [**tone-voice-rules.md**](./conventions/tone-voice-rules.md) — phrases bannies, seuils, emojis, formulations validées

## Runbooks

- [**shopify-draft-order-complete.md**](./runbooks/shopify-draft-order-complete.md) — recette draft order complète (create → customer patch → discount → shipping → complete)

## Historique des évolutions du tooling (17/04/2026)

Cette session a consolidé plusieurs changements :

- **Template `s4b_dotation_contre_offre`** ajouté (`knowledge/voice/templates.yaml`) — réponse type au prospect qui demande paid
- **Pattern code unifié** `[CODE]DOTATION` (fusion `[PRENOM]-CREDIT` + `[NOM]DOTATION`) avec 2 variantes : one-shot et récurrent
- **Seuil parquage** remonté de `<2000` → `<2500` followers
- **`banned_phrases`** introduites dans templates.yaml : "Ça te parle", "je te passe un coup de fil"

## Stats de la session

- **22 threads actionnés** (5 HIGH + 5 parqués + 4 retards + 8 reel_mentions/remerciements)
- **5 orders Shopify complétées** (Simon D753, Yannick D754, Thomas D755, Maxime D757, draft Alexia en attente)
- **7 codes créés** : FITBYSIMON, KIKISPORTIVEDOTATION, ALTIZ, ALTIZDOTATION, THOMASBNT, MAXIMEC, + affiliate pour Kléden (existant)
- **3 customers Shopify** créés/patchés
- **20+ lignes Sheet** Suivi_Amb/Suivi_Dot/Suivi_Paid/Archive modifiées
