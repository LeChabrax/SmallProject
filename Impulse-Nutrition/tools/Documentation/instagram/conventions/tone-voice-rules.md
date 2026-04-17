# Conventions — Tone & Voice Antoine (Instagram DM)

> Règles consolidées au fil des sessions. Source machine-readable : `knowledge/voice/templates.yaml::personality`. Source humaine : `knowledge/voice/rules.md` + `knowledge/voice/personality.md`.

## Règles structurelles

| Règle | Valeur | Note |
|---|---|---|
| Tutoiement | toujours | Jamais vouvoiement sur Instagram DM (vouvoiement = canal SC/Gorgias) |
| Signature longue (≥3 phrases) | `Sportivement,\nAntoine` | Défaut |
| Signature courte | `Antoine` | Facultatif |
| Signature alt | `Antoine - Impulse Nutrition` | Pour nouveaux prospects formels |
| Signature threshold | 3 phrases | <3 phrases = pas de signature |
| Emoji max par message | 2 | Au-delà = clinquant |
| Em dash (`—`) | **INTERDIT** | Tous canaux, zéro tolérance |
| Point final sur micro-message | **INTERDIT** | Ex: "Super" pas "Super." |
| Double `!!` sur micro | Préférer | "Merci !!" > "Merci !" |
| `Hello {prenom}` en conv active | **INTERDIT** | OK seulement en 1er contact |

## Emojis

**Favoris** (à utiliser librement) : `😉` `🔥` `😊` `😍` `😄`

**Bannis** (sonnent mielleux / pas Antoine) : `🙏` `✨` `💖`

**Usage** :
- `🔥` : performance / contenu réussi (max 1 par message)
- `💪` : encouragement (max 1 par message)
- `😉` `😊` `😄` : légèreté, fin de phrase
- `😍` : reaction_contenu (super content)

## Termes bannis

| Terme banni | Remplacement |
|---|---|
| `ROI` | (reformuler métier) |
| `KPI` | (reformuler métier) |
| `reach` | "portée" |
| `conversion` | (reformuler business) |
| `collab` | `partenariat` |

## Phrases bannies (`banned_phrases`)

| Phrase bannie | Remplacement | Raison |
|---|---|---|
| "Ça te parle ?" | "Qu'en penses-tu ?" | Trop marketing, validé banni 17/04/2026 |
| "Je te passe un coup de fil" | "On s'appelle" / "Je t'appelle" | Pas naturel pour Antoine, validé banni 17/04/2026 |

## Formulations validées (préférées)

| Situation | Formulation validée | Formulation à éviter |
|---|---|---|
| Acceptation enthousiaste | "Trop bien que ça t'intéresse, on est ravi !" | "Trop bien on est ravi !" (trop vague) |
| Proposer call | "On s'appelle à ce moment-là" | "Je te passe un coup de fil" |
| Validation mutuelle | "On se cale ça" / "C'est noté" | — |
| Validation rapide | "Yes", "Top", "Au top" | — |
| Acknowledge retard >4j | "Excuse-moi pour le temps de réponse !" (s14a) | — |
| Acknowledge retard >10j | "Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !" (s14b) | — |
| Acknowledge 7+ mois | s14b + "Le dossier a malheureusement glissé entre les mailles" | — |

## Seuils numériques

| Seuil | Valeur | Action |
|---|---|---|
| Parquage auto (community_too_small) | **<2500 followers** | s3.4 + ACHAB25, envoi direct sans go ciblé (memory feedback) |
| Enveloppe dotation standard | 80€ | <20k followers |
| Enveloppe dotation impressionné | 100€ | ≥20k followers |
| Dotation structurée mensuelle défaut | 120€ | Pro / cas spéciaux (Yannick, Alexia proposition) |
| Durée dotation défaut | 4 mois | Négociable |
| Cible utilisations code (dotation structurée) | 16 uses sur 4 mois | = 4 uses/mois |
| Valeur crédit par utilisation | 20€ | Col O - Col Q × 20€ |
| Seuil `rien_a_faire` (remerciement final) | <20 mots, pas de question, mots-clés "merci"/"parfait"/"nickel"/"top"/"compris" | skip auto |

## Excuse retards (templates s14)

| Délai | Template | Body |
|---|---|---|
| >4 jours | s14a | "Excuse-moi pour le temps de réponse !" (prepend) |
| >10 jours | s14b | "Je suis vraiment désolé pour ce temps de réponse, c'est inadmissible de mon côté, c'était un peu la course !" (prepend) |

**Règle** : prepend au début du message principal, ligne séparée.

## Règle "auto-skip si notre côté a déjà répondu en dernier"

Memory feedback `feedback_waiting_customer_reply`. Si `last_msg_is_from_viewer == true` dans le scan du thread → carte condensée 1 ligne : `@{username} · en attente retour prospect. Notre côté a répondu le {date}.` Pas de nouveau draft.

## Règle "rien à faire" sur remerciement final

Si le dernier message du prospect est un simple remerciement (<20 mots, pas de question, contient "merci"/"parfait"/"ok"/"nickel"/"top"/"compris"/"ça marche") ET qu'on a répondu juste avant → `L=good`, pas d'action requise.

**Exception** : si remerciement contient aussi une question → traiter normalement.

## Red flags

- ❌ Dire "collab" au lieu de "partenariat"
- ❌ Signer `Antoine` côté SC/Gorgias (vouvoiement obligatoire côté client final)
- ❌ Utiliser "Ça te parle ?" ou "Je te passe un coup de fil"
- ❌ >2 emojis dans un message
- ❌ `🙏`, `✨`, `💖` (bannis)
- ❌ Em dash `—` n'importe où
- ❌ "Hello {prenom}" dans une conv active (seulement premier contact)
- ❌ Drafter sur voice_media ou raven_media non écouté (inaccessible via API, action manuelle Antoine)

## Source de vérité machine

`knowledge/voice/templates.yaml::personality` :

```yaml
personality:
  tutoiement: true
  signature_long: "Sportivement,\nAntoine"
  signature_threshold: 3
  emoji_max: 2
  emoji_favorites: ["😉", "🔥", "😊", "😍"]
  emoji_banned: ["🙏", "✨", "💖"]
  no_em_dash: true
  no_final_period_micro: true
  double_exclamation_micro: true
  no_hello_active_conv: true
  banned_terms: ["ROI", "KPI", "reach", "conversion", "collab"]
  banned_phrases:
    - "Ca te parle"
    - "je te passe un coup de fil"
  preferred_terms:
    collab: "partenariat"
```
