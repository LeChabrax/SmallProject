# Guide Utilisation Skills -- Impulse Nutrition

Guide pratique pour utiliser les 3 skills au quotidien. Pas besoin de comprendre le code, juste savoir quoi taper et ce qu'il faut verifier avant de valider.

---

## Les 3 skills en 30 secondes

| Skill | Quand l'utiliser | Ce que tu tapes |
|---|---|---|
| `/instagram-dm` | Check/repondre aux DMs ambassadeurs Instagram | `check les DMs`, `draft pour @username`, `relance @username` |
| `/gorgias` | Traiter les tickets SAV (email, chat, WhatsApp, IG, FB) | `check le SAV`, `check les tickets`, `reponds au ticket #12345` |
| `/tiktok-sav` | SAV TikTok Shop (messages buyers) | `check tiktok sav`, `traite les messages tiktok` |

Les skills se declenchent automatiquement quand tu tapes ces commandes. Pas besoin de `/` devant (sauf si tu veux etre explicite).

---

## Comment ca marche (flow universel)

```
1. Tu tapes la commande ("check les DMs")
2. Claude lit les messages/tickets via les MCPs
3. Pour chaque cas, Claude produit une CARTE DE DECISION :
   - Resume du contexte (messages cites, stats, statut Sheet)
   - Categorisation (nouveau prospect, SAV, relance, etc.)
   - Draft de reponse propose
4. Tu lis la carte et tu decides :
   - "go" → Claude envoie le message
   - "corrige : [ta version]" → Claude ajuste et re-propose
   - "skip" → on passe au suivant
5. Claude envoie + met a jour le Sheet si besoin
```

**Regle d'or** : Claude ne fait JAMAIS d'envoi sans ton "go" explicite. "C'est bon", "ok", "ca marche" ne valident PAS l'envoi. Seuls **"go"**, **"envoie"**, **"c'est bon envoie"** comptent.

---

## Skill 1 : `/instagram-dm`

### Ce que ca fait
- Pull les 20 derniers threads DM Instagram du compte `impulse_nutrition_fr`
- Detecte les threads ou une action est requise (prospect qui a ecrit, relance a faire, vocal a ecouter)
- Produit une carte de decision par thread actionnable
- Draft le message selon le decision tree (pitch ambassadeur, relance, refus poli, etc.)

### Cas typiques

| Situation | Ce que Claude fait | Ce que tu valides |
|---|---|---|
| Nouveau prospect inbound (inconnu qui ecrit) | Check son profil (followers, niche), check le Sheet, draft un pitch ou un code welcome | Le draft est adapte au profil ? Le ton est bon ? |
| Prospect "parque" (a deja recu ACHAB25) | Detecte le code welcome dans l'historique, propose une relance contextualisee §16 (jamais un pitch d'entree) | L'acknowledgment du passe est correct ? |
| Voice media (vocal) | Signale "vocal a ecouter manuellement" sans drafter | Tu ecoutes dans l'app Instagram puis tu dis a Claude quoi repondre |
| Prospect < 2000 followers | Refus poli + code welcome ACHAB25 | Le refus est chaleureux ? Le code est ACHAB25 ? |
| Antoine a deja repondu | Auto-skip avec carte 1 ligne "en attente retour prospect" | Rien a faire, c'est normal |

### Persona Instagram
- **Tutoiement** systematique
- Signature `Sportivement, Antoine` uniquement si message >= 3 phrases
- Emojis moderes (0-2 max) : 😉 🔥 💪 😊 😍
- **Jamais** de tirets em, jamais de jargon marketing

---

## Skill 2 : `/gorgias`

### Ce que ca fait
- Pull 100 tickets Gorgias (minimum, jamais moins)
- Filtre les actionnables (email, chat, contact_form, WhatsApp-WAX, internal-note BigBlue)
- Exclut le spam, les auto-replies, les reviews Yotpo
- Produit une carte de decision par ticket

### Cas typiques

| Situation | Ce que Claude fait | Ce que tu valides |
|---|---|---|
| Colis bloque en transit | Lookup BigBlue/Shopify, propose un replacement draft (discount 100% + shipping 0€ + tag Service client) | Le produit est le bon ? L'adresse est correcte ? |
| Retour a l'expediteur | Propose 2 options au client : remboursement OU reexpedition domicile | Le montant est correct ? Le geste commercial est adapte ? |
| Bad rating BigBlue | Apology + demande contexte | Le ton est empathique sans etre servile ? |
| Candidature ambassadeur | Redirige vers Instagram DM @impulse_nutrition, close le ticket | OK |
| Candidature stage/emploi RH | Escalade a Antoine (pas de reponse auto) | Tu decides : forward RH ou close |
| SC a deja repondu | Auto-skip 1 ligne "en attente client" | Rien a faire |

### Persona Gorgias
- **Vouvoiement** formel, jamais de tutoiement
- Signature `Cordialement, Le service client Impulse Nutrition`
- **Jamais** signer "Antoine" cote service client
- **Jamais** de delais chiffres ("48-72h") -- utiliser "des que nous avons du nouveau"
- **Jamais** de formules creuses ("nous vous remercions de votre confiance")

---

## Skill 3 : `/tiktok-sav`

### Ce que ca fait
- Lit `pending.json` (peuple automatiquement par le script Python `sav.py` toutes les 30 min via cron)
- Classifie chaque message buyer en categories T1-T9
- Envoie automatiquement les reponses simples (T1 tracking, T3 promo, T6 delai, T7 produit, T9 merci)
- Route les cas complexes (T2 casse, T4 manquant, T5 adresse, T8 retour) vers `queue.json` pour traitement manuel

### Particularite
Ce skill est **partiellement autonome** : les categories simples (T1, T3, T6, T7, T9) sont envoyees SANS validation "go". Les categories complexes (T2, T4, T5, T8) sont toujours mises en queue pour toi.

### Persona TikTok
- **Vouvoiement** formel
- Signature `Le service client`
- Meme regles que Gorgias (persona marque, pas "Antoine")

---

## Regles transversales (valables partout)

Ces regles s'appliquent a TOUS les skills, automatiquement :

1. **Draft + go explicite** avant tout envoi. "Ok" ne vaut pas "go".
2. **Chaque draft = son propre go**. "Go un par un" ne valide pas le draft en cours. Tu dois valider chaque draft individuellement.
3. **Lire le thread/ticket complet** avant de drafter (Claude le fait automatiquement).
4. **Pas de tirets em** (`—`) dans aucun message redige.
5. **Excuses si retard** : > 4 jours = excuse legere, > 10 jours = excuse appuyee.
6. **Jamais confondre les personas** : Instagram = tutoiement Antoine, Gorgias/TikTok = vouvoiement marque.

---

## Raccourcis et combinaisons utiles

```
check les DMs                  → /instagram-dm global
draft pour @username           → /instagram-dm sur un thread specifique
relance @username              → /instagram-dm relance ciblee
check le SAV                   → /gorgias global (100 tickets)
reponds au ticket #12345       → /gorgias sur un ticket specifique
check tiktok sav               → /tiktok-sav (lit pending.json)
```

### Combiner avec /loop (polling automatique)

```
/loop 30m /gorgias             → check SAV toutes les 30 min
/loop 1h /instagram-dm         → check DMs toutes les heures
```

---

## FAQ

**Q: Claude propose un draft qui ne me convient pas, je fais quoi ?**
Tu dis "corrige : [ta version ou tes instructions]". Claude re-drafte. Tu ne valides que quand c'est bon.

**Q: Claude a envoye un message que je n'ai pas valide !**
Impossible (sauf /tiktok-sav T1/T3/T6/T7/T9 qui sont auto-send par design). Si ca arrive sur Instagram ou Gorgias, c'est un bug -- signale-le.

**Q: Un prospect m'ecrit mais Claude ne le trouve pas dans le Sheet**
C'est normal pour les nouveaux prospects. Claude signalera "absent du Sheet" et demandera ton avis avant de drafter (pour eviter de re-pitcher un prospect parque).

**Q: La session Instagram a expire**
Lance `cd instagram_dm_mcp && uv run python create_session.py` et suis les instructions (login + code 2FA si demande).

**Q: Claude met longtemps a check les DMs**
Normal, il fait 1 appel par thread (~3-8 secondes par thread avec le rate limit Instagram). 20 threads = 1-3 minutes.

**Q: Je veux que Claude ignore un thread/ticket**
Dis "skip" ou "next". Claude passera au suivant sans drafter.
