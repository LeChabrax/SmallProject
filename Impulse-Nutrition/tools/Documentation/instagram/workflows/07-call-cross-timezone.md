# Workflow 07 — Planifier un call (timezone / contraintes horaire)

> Quand le prospect veut qu'on se call, il faut caler le créneau précis + récupérer son numéro + noter ça proprement dans le Sheet pour ne pas louper le call. Session 17/04/2026 : **3 cas** (Pablo en Indonésie +6h, Delphée soirée, Sophia lundi 11h).

## Quand utiliser

- Le prospect demande un call
- Il faut caler créneau + récupérer numéro
- Contrainte : timezone différente / horaire spécifique / agenda Antoine

## Principe

- **Proposer un créneau précis** (pas juste "la semaine prochaine quand tu peux")
- **Adapter au timezone du prospect** (indiquer les 2 heures FR ↔ local)
- **Demander le numéro** dans le même message si pas déjà fourni
- **Mettre à jour Sheet** avec la date, heure, numéro → jamais oublier
- **Confirmer par micro-message** une fois calé

## Formulations validées

| Pour proposer un call | Utiliser | Éviter |
|---|---|---|
| Proposer un créneau | "Je suis dispo mercredi en matinée, genre 9h30-10h" | "Quand tu veux" |
| Demander numéro | "Tu peux m'envoyer ton numéro ?" | "Je te passe un coup de fil" (banni) |
| Confirmer RDV | "C'est noté à {jour} {heure} !" | "Ok pas de souci" |
| Confirmer call | "On s'appelle à ce moment-là 😊" | "Je te passe un coup de fil" |

## Flow step-by-step

```
1. Prospect demande un call
2. Check agenda Antoine (horaires occupés = sport, autres calls, etc.)
3. Proposer 1-2 créneaux PRÉCIS
   └─ Si timezone différente: indiquer heure prospect + heure FR
4. Si pas de numéro: le demander dans le même message
5. Prospect confirme → envoyer micro-confirmation
6. Sheet update: note K avec date + heure + numéro
7. (Post-call) Sheet update avec résumé + next steps
```

## Exemple 1 — Pablo (@pabloxdiscipline) — **Indonésie +6h**

### Contexte

- Parqué sept 2025, relancé janv 2026, re-pitché le 15/04 (18,4k followers)
- Il répond 16/04 04:49 (heure FR) : "Dispo pour s'en parler au téléphone ? **Je suis en Indonésie j'ai 6h de plus**, je te laisse me dire 🙏🏼"

### Proposition initiale (mercredi 9h30-10h FR)

```
Bien sûr, je suis partant pour un appel ! Je suis dispo mercredi en matinée, genre 9h30-10h côté France (soit 15h30-16h pour toi en Indonésie). Dis-moi ce qui te convient le mieux 😊

Sportivement,
Antoine
```

**Éléments clés** :
- Créneau précis "mercredi 9h30-10h"
- **Conversion timezone explicite** : "15h30-16h pour toi en Indonésie"
- "Dis-moi ce qui te convient" = laisse flexibilité micro

### Pablo répond : "10h possible ?"

### Confirmation (micro)

```
Parfait, c'est noté pour mercredi 10h !
```

*(1 phrase, pas de signature — micro-message)*

### Sheet update (Suivi_Amb L1021)

```
K = "Inbound initial Août 2025 (-10k follow, pas retenu à l'époque). Relancé Jan 2026 puis re-pitché 15/04 (18,4k follow, Ironman Vichy 70.3 à venir). Call confirmé mercredi 22/04 10h FR (16h Indonésie)."
```

**⚠️ Numéro pas encore demandé** — au besoin, suivre avec un DM de demande de numéro si appel téléphone (sinon call via Instagram audio OK).

## Exemple 2 — Delphée (@mapageblanche_) — **soirée**

### Contexte

- Ambassadrice active (marathon Paris), veut prolonger partenariat long terme
- Elle propose 12h30-14h semaine pro → Antoine dit "je vais au sport à cette heure là"
- Elle re-propose 18h30 → Antoine "je vais au sport à cette heure là aussi"
- Session 17/04 : Antoine dit **"on va s'adapter"** → accepter 18h30

### DM "on s'adapte" envoyé

```
Parfait, on dit mardi 18h30 alors ! Tu peux m'envoyer ton numéro ? 😊

Sportivement,
Antoine
```

### Elle répond

> "Super ! Oui c'est le +33 786 80 55 77 😊"

### Confirmation envoyée par Antoine directement (hors session Claude)

> "Super c'est noté ! à mardi ! Sportivement, Antoine"

### Sheet update (Suivi_Amb L16)

```
K = "Call calé mardi 21/04 18h30 au +33 786 80 55 77. Veut prolonger partenariat long terme post-marathon Paris. Confirmé par Antoine 17/04 16h21."
```

## Exemple 3 — Sophia (@sophia_bdbn) — **lundi 11h**

### Contexte

- Inbound mars avec dossier partenariat envoyé par mail
- Email relance compliquée → passage au DM
- Elle propose Lundi/Mardi/Mercredi — Antoine choisit lundi 11h
- Elle confirme + envoie numéro

### Son message

> "Lundi 11h parfait! ☺️ Le voici: 0627786582 Bonne journée À bientôt"

### DM confirmation

```
Super, c'est noté à lundi 11h !
```

*(micro-message, pas de signature)*

### Sheet update (Suivi_Amb L152)

```
K = "Call calé lundi 21/04 11h au 0627786582. Dossier partenariat envoyé par mail en mars > achabrat@havea.com."
```

## Template micro-confirmation

Quand le call est calé + numéro reçu :

```
Super, c'est noté à {jour} {heure} !
```

*(Pas de signature. Pas de "on s'appelle à ce moment-là" — c'est redondant vu qu'on a calé.)*

## Template proposition de créneau avec timezone

```
Bien sûr, je suis partant pour un appel ! Je suis dispo {jour} en {matinée/après-midi}, genre {heure_FR} côté France (soit {heure_locale_prospect} pour toi en {pays}). Dis-moi ce qui te convient le mieux 😊

Sportivement,
Antoine
```

**Variables** :
- `{jour}` : jour précis (mercredi, mardi...)
- `{heure_FR}` : créneau précis en heure FR (ex: "9h30-10h")
- `{heure_locale_prospect}` : conversion timezone (ex: "15h30-16h")
- `{pays}` : pays prospect (ex: "Indonésie")

## Template proposition + demande numéro (même message)

```
Parfait, on dit {jour} {heure} alors ! Tu peux m'envoyer ton numéro ? 😊

Sportivement,
Antoine
```

## Règles Sheet pour les calls

| Étape | Action Sheet |
|---|---|
| Créneau proposé | K += "Call proposé {date} {heure}" |
| Créneau confirmé + numéro reçu | K = "Call calé {date} {heure} au {numéro}. {context court}" |
| Post-call | K = "Call fait {date}. {résumé}. Next: {action}" |
| Call raté / report | K += "(reporté X, nouvelle date Y)" |

## Red flags

| Red flag | Conséquence |
|---|---|
| "Je te passe un coup de fil" | **Banni** (cf tone-voice-rules.md) |
| Proposer créneau sans conversion timezone (prospect à l'étranger) | Confusion, loupé potentiel |
| "Quand tu peux" / "dis-moi tes dispos" sans créneau concret | Ping-pong inutile |
| Oublier de demander le numéro si tel | Devra relancer pour l'obtenir |
| Ne pas noter dans le Sheet | Risque de louper l'appel |
| Proposer un créneau dans l'heure qui arrive (en attente d'une réponse) | Prospect peut ne pas voir à temps |

## Checklist avant envoi proposition call

- [ ] Créneau PRÉCIS (jour + heure)
- [ ] Si timezone différente : conversion indiquée
- [ ] Numéro demandé si pas déjà fourni
- [ ] Note Sheet préparée pour update post-confirmation

## Source de vérité

- [conventions/tone-voice-rules.md](../conventions/tone-voice-rules.md) (phrases bannies, formulations validées)
- Memory `feedback_waiting_customer_reply.md` (auto-skip si on attend retour)
