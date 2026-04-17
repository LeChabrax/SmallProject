# Workflow 05 — Parquage automatique prospects <2500 followers

> Les inbounds avec moins de 2500 followers sont systématiquement parqués : refus poli via template s3.4 + code welcome ACHAB25 + routage vers Archive sheet. **Envoi direct autorisé sans go ciblé** (memory feedback `feedback_auto_parquage_under_2k`). Session 17/04/2026 : **5 parqués** (Mickael, Aurélien, Charlotte, Thomas Lancia, Maël).

## Quand utiliser

- Inbound Instagram (Primary / Demandé / Spam)
- **Moins de 2500 followers**
- Pas de signal exceptionnel (rencontre IRL, cause caritative, athlète haut niveau reconnu)
- Convention validée par Antoine le 17/04/2026 (seuil remonté de 2000 à 2500)

## Règle clé : envoi direct autorisé

**Exception à la règle globale "draft + go explicite avant envoi"**.

Pour les prospects <2500 followers, je peux **drafter ET envoyer directement** le template s3.4 sans attendre un "go" ciblé d'Antoine. Raison : ces cas sont toujours traités de la même façon, les allers-retours ne créent pas de valeur.

**Exceptions où il faut quand même demander** :
- Compte ≥2500 followers (retour protocole normal avec go ciblé)
- Profil avec angle exceptionnel (rencontre IRL documentée, cause caritative, athlète haut niveau)
- Cas ambigu type "client récurrent qui redemande un code"
- Retard >10 jours (prepend s14b — voir plus bas)

## Template s3.4 (verbatim)

```
Merci pour ton message {prenom} et pour le partage de ton projet, {accroche} 🔥

Pour être transparent avec toi, on travaille avec des profils qui ont une communauté déjà bien établie sur les réseaux, et pour l'instant ton compte ne correspond pas encore aux critères qu'on recherche pour nos partenariats. Ce n'est absolument pas un jugement sur la qualité de ton contenu ou de ton projet, mais c'est notre critère actuel.

Ce qu'on peut faire en revanche : je te laisse un code perso ACHAB25 pour que tu puisses découvrir nos produits avec -25% sur ta commande. Et si dans le futur ta communauté se développe, n'hésite pas à revenir vers nous, ce sera avec plaisir !

Sportivement,
Antoine
```

**Variables** :
- `{prenom}` : prénom du prospect (extrait bio, handle, ou contexte thread)
- `{accroche}` : 1 phrase valorisant son projet/sport (basé sur faits réels — jamais inventé)

## Routage Archive

**Toujours router vers `Archive` sheet, jamais Suivi_Amb** (qui est réservé aux ambassadeurs actifs ou en cours d'onboarding).

### Structure Archive (ligne à créer)

| Col | Valeur |
|---|---|
| A (Compte @) | username |
| B (IG link) | URL Instagram |
| F (Statut) | `Out` |
| H (Action/Commentaire) | "s3.4+ACHAB25 envoyé <date> (inbound <canal>, <XX>k follow, <context>)" |
| I (type contrat) | `Amb-Crédit` |
| J (Sport) | niche (trail, running, athlé, UGC, etc.) |
| L (Followers k) | ex: "2,2" |
| M (Date) | DD/MM/YYYY |

## Flow step-by-step

```
1. Inbound reçu (Primary / Demandé / Spam)
2. get_user_info(username) → followers count
3. Si <2500 followers → engager parquage auto
4. Composer s3.4 avec {prenom}, {accroche}, {CODE25=ACHAB25}
5. Si retard >10j → prepend s14b
6. Envoi direct (pas de go ciblé)
7. Sheet: ajouter ligne Archive avec statut Out + détails
```

## 5 exemples session (17/04/2026)

### Cas 1 — Mickael Urbain (@runwithmikeii, 2 195 followers)

**Son message (16/04)** :
> "Bonjour, je me permets de vous contacter car je développe actuellement un compte autour du trail, de la discipline et de la performance. Je partage mon évolution sportive au quotidien avec une communauté engagée..."

**Accroche** : "ton univers trail/discipline/performance est solide"

**DM envoyé (sans modification)** :

```
Merci pour ton message Mickael et pour le partage de ton projet, ton univers trail/discipline/performance est solide 🔥

Pour être transparent avec toi, on travaille avec des profils qui ont une communauté déjà bien établie sur les réseaux, et pour l'instant ton compte ne correspond pas encore aux critères qu'on recherche pour nos partenariats. Ce n'est absolument pas un jugement sur la qualité de ton contenu ou de ton projet, mais c'est notre critère actuel.

Ce qu'on peut faire en revanche : je te laisse un code perso ACHAB25 pour que tu puisses découvrir nos produits avec -25% sur ta commande. Et si dans le futur ta communauté se développe, n'hésite pas à revenir vers nous, ce sera avec plaisir !

Sportivement,
Antoine
```

**Archive L895** créée.

### Cas 2 — Aurélien Escolano (@escoaurel, 800 followers)

**Profil** : compte privé, trail + athlétisme, 3 médailles nationales athlé par équipe, militaire

**Accroche** : "ton univers trail + ta discipline militaire c'est vraiment solide"

### Cas 3 — Charlotte (@charlottemugc, 647 followers)

**Profil** : UGC creator Montpellier, **pitch pour services UGC** (pas ambassadeur classique)

**Accroche** : "ta démarche UGC est très pro"

Note : cas un peu spécial (elle pitche des services UGC paid, pas un partenariat ambassadeur). Le s3.4 marche quand même car elle est <2500 ET son pitch ne rentre pas dans notre périmètre (pas de budget UGC paid actif).

### Cas 4 — Thomas Lancia (@toto_triathlon, 395 followers)

**Profil** : 23 ans, alternant, rêve d'Ironman

**Accroche** : "ton objectif Ironman full distance c'est une belle ambition"

### Cas 5 — Maël Larsonneur (@mael.larsonneur, 545 followers) — **cas Spam + retard**

**Canal** : boîte **Spam** (pas Primary)
**Message date** : 29/03/2026 → découvert le 17/04 = **19 jours de retard** → **prepend s14b obligatoire**

**Profil** : athlète athlétisme 9 ans, 3 médailles nationales par équipe, cross/1500m/3000m

**Accroche** : "9 ans d'athlétisme et 3 médailles nationales par équipe c'est vraiment solide"

**DM envoyé avec s14b prepend** :

```
Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !

Merci pour ton message Maël et pour le partage de ton projet, 9 ans d'athlétisme et 3 médailles nationales par équipe c'est vraiment solide 🔥

Pour être transparent avec toi, on travaille avec des profils qui ont une communauté déjà bien établie sur les réseaux, et pour l'instant ton compte ne correspond pas encore aux critères qu'on recherche pour nos partenariats. Ce n'est absolument pas un jugement sur la qualité de ton contenu ou de ton projet, mais c'est notre critère actuel.

Ce qu'on peut faire en revanche : je te laisse un code perso ACHAB25 pour que tu puisses découvrir nos produits avec -25% sur ta commande. Et si dans le futur ta communauté se développe, n'hésite pas à revenir vers nous, ce sera avec plaisir !

Sportivement,
Antoine
```

## Batch Archive routing (méthode efficace)

Utiliser `batch_update_cells` pour ajouter plusieurs parqués d'un coup :

```python
mcp__google_sheets__batch_update_cells(
    spreadsheet_id="1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4",
    sheet="Archive",
    ranges={
        "A895:M895": [["runwithmikeii", "https://...", "", "", "", "Out", "", "s3.4+ACHAB25 envoyé 17/04 (...)", "Amb-Crédit", "trail/performance", "", "2,2", "17/04/2026"]],
        "A896:M896": [["escoaurel", ...]],
        "A897:M897": [["charlottemugc", ...]],
        "A898:M898": [["toto_triathlon", ...]],
        "A899:M899": [["mael.larsonneur", ...]],
    }
)
```

Fait en 1 call API. Archive session : **lignes 895-899 créées** en batch pour les 5 parqués.

## Accroches recommandées (par niche)

| Niche | Template accroche |
|---|---|
| Trail | "ton univers trail/performance est solide" |
| Running | "ton approche running/{objectif} est top" |
| Triathlon | "ton objectif Ironman/70.3 c'est une belle ambition" |
| Athlétisme | "{N} ans d'athlétisme et {médailles} c'est vraiment solide" |
| UGC | "ta démarche UGC est très pro" |
| Bien-être / coaching | "ton approche {spécialité} résonne bien avec nos valeurs" |
| Multi-sport / hybrid | "ta polyvalence sur {sports} est cool" |

**Règle** : toujours baser l'accroche sur des **faits réels** du profil / message du prospect, jamais inventé.

## Red flags

| Red flag | Conséquence |
|---|---|
| Router vers Suivi_Amb au lieu d'Archive | Pollution pipeline ambassadeur actif |
| Oublier le tag `Out` dans col F | Non-identifiable comme parqué |
| Accroche inventée / générique ("super profil") | Message impersonnel, l'autre voit le copy-paste |
| Oublier s14b sur retard >10j | Pas professionnel |
| Envoyer s3.4 à un profil >2500 followers | Devait passer par go ciblé (cf feedback) |
| Utiliser autre code que ACHAB25 (ex: PGAU25) | ACHAB25 = défaut validé. PGAU25 legacy |

## Source de vérité

- `knowledge/voice/templates.yaml::s3_4_communaute_trop_petite` (template s3.4)
- Memory `feedback_auto_parquage_under_2k.md` (règle envoi direct <2500)
- Memory `reference_sheet_archive_vs_suivi_amb.md` (routing Archive vs Suivi_Amb)
- `knowledge/voice/templates.yaml::s14_retard_appuye` (prepend s14b >10j)
- `knowledge/voice/templates.yaml::s14_retard_leger` (prepend s14a >4j)
