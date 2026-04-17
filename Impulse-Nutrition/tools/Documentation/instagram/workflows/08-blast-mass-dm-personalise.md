# Blast mass DM personnalisé — Instagram + Email

> **Cas d'usage** : annoncer une nouveauté produit/site/programme à TOUS les ambassadeurs ayant un statut donné dans `Suivi_Amb` (ex : "Produits envoyés"), via DM Instagram + email Outlook en parallèle.
>
> **Session de référence** : 17/04/2026 — annonce de la nouvelle interface "Laisse ton avis depuis ton espace perso". 137 ambassadeurs ciblés, 126 DM ✅ + 1 ❌, 135 emails préparés Outlook CCI.
>
> **Dossier de travail type** : `tools/ContentInflu/{NomCampagne}-{DD-MM-YY}/` contient la vidéo + scripts + queue + logs.

---

## Quand utiliser ce workflow

| Trigger | Exemple |
|---|---|
| Lancement nouvelle feature site | "Avis depuis l'espace perso" |
| Annonce campagne saisonnière | Black Friday, Noël, lancement gamme |
| Rappel relationnel collectif | "Hello on pense à toi pour la rentrée" |
| Demande UGC / contenu groupé | "On lance le challenge X, t'es chaud ?" |

⚠️ **Pas pour le SAV individuel** (→ skill `/gorgias`) ni pour onboarding ambassadeur (→ skill `/instagram-dm`).

---

## Vue d'ensemble du flow

```
1. Préparer dossier mission       (tools/ContentInflu/{nom}-{date}/)
2. Pull cible depuis Sheet        (Suivi_Amb filtré sur Statut)
3. Récupérer emails               (Sheet col AF + DM + Shopify lookup)
4. Drafter DM Insta + email       (validation explicite avant envoi)
5. Tester DM sur compte perso     (le.chabrax = compte test Antoine)
6. Lancer blast Instagram         (script Python autonome)
7. Lancer blast Email Outlook     (CCI manuel copier-coller)
```

---

## Étape 1 — Dossier mission

Convention : `tools/ContentInflu/{NomCourtCampagne}-{DD-MM-AA}/`

Contenu type :
```
tools/ContentInflu/AvisVideo-17-04-26/
├── TutoAvisEspacePerso.mp4         # Vidéo source (si applicable)
├── MISSION.md                       # Brief + drafts validés
├── handles_instagram.md             # Liste handles à pinger
├── emails_outlook.md                # CCI + draft email + provenance
├── handle_to_prenom.json            # Map handle → prénom (Sheet col AE)
├── queue_remaining.json             # Queue à traiter
├── sent_log.json                    # Log envois (resume-safe)
├── blast_avis.py                    # Script Python d'envoi DM
└── blast.log                        # Log temps réel du script
```

---

## Étape 2 — Pull cible depuis Sheet `Suivi_Amb`

**Colonnes utiles** :
| Col | Nom | Usage |
|---|---|---|
| I | Compte @ | Handle Instagram (sans `@`) |
| J | Statut | Filtre cible (ex: `Produits envoyés`) |
| AE | Prenom | Personnalisation DM/email |
| AF | Mail | Email pour blast Outlook |

```python
# Pull via MCP google_sheets puis filtre Python
rows = get_sheet_data("Suivi_Amb", "I4:AF500")
target = [(r[0], r[22], r[23]) for r in rows
          if len(r) > 1 and r[1] == "Produits envoyés"]
# r[0]=handle, r[22]=prenom (col AE), r[23]=email (col AF)
```

---

## Étape 3 — Récupération emails (3 sources cumulatives)

Pour maximiser le taux email, croiser **3 sources** dans cet ordre :

### 3.1 Sheet `Suivi_Amb` col AF
Source primaire — souvent renseignée lors du draft order.

### 3.2 DMs Instagram (récupération sur les manquants)
Pour les handles sans email dans le Sheet, parser les threads DM existants — l'ambassadeur a souvent envoyé son email lors du flow shipping.

```python
# Pour chaque handle sans email :
user_id = cl.user_id_from_username(handle)
thread = mcp_get_thread_by_participants([user_id])
# → grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' dans les messages
```

### 3.3 Shopify customer lookup (dernier recours)
Pour les irréductibles, search par nom/prénom/téléphone.

```python
mcp_shopify_orders__search_customers(query="Justine Roux")
# → matche par first_name + last_name + phone
```

**Bilan session 17/04/2026** : 123 (Sheet) + 6 (DM récup) + 6 (Shopify) = **135 / 137 emails** récupérés.

Les 2 irréductibles (`fit.bylily`, `alexx_adamo`) n'ont aucune trace email cross-canal → contact Insta uniquement.

---

## Étape 4 — Drafter DM Insta + email

### Règles persona blast (différentes du SAV individuel)
| Canal | Persona | Tutoiement | Signature |
|---|---|---|---|
| **DM Instagram blast** | Antoine, ambassadeur | OUI | `Sportivement, Antoine` |
| **Email blast ambassadeur** | Antoine (relation directe) | OUI | `Sportivement, Antoine` |

> ⚠️ Différent du SAV : l'email blast à des ambassadeurs reste **tutoiement Antoine** car la relation est directe via DM. Vouvoiement marque uniquement pour SAV client final (Gorgias).

### Anatomie du message DM Insta

```
Hello {prenom} ! J'espère que tu vas bien.

[Hook nouveauté] : on est trop content de te présenter notre nouveauté : [feature en 1 phrase] !

[CTA + ressource] : On t'a préparé une petite vidéo tuto pour t'expliquer, y'a plus qu'à suivre les instructions 😉
👉 [URL Drive de la vidéo]

[Bénéfice mutuel] : N'hésite pas à y faire un tour pour [action]. Ça nous aide énormément 🙏

Sportivement,
Antoine
```

### Anatomie email
Identique au DM mais :
- Vidéo en **pièce jointe** + lien Drive en backup
- Mention URL site explicite (`impulse-nutrition.fr`) puisque l'email sort du contexte Insta
- 2-3 objets candidats, picker le plus parlant

### Personnalisation `{prenom}`
- **Source recommandée** : col AE du Sheet `Suivi_Amb` (134/137 dispo, fiable)
- **Source legacy** (déprécié) : extraction `cl.user_info().full_name` → bcp d'appels API + hangs
- **Fallback "Hello !"** si prénom vide ou exotique

### Iteration des drafts (validation user)
Pattern observé en session : le user veut **plusieurs allers-retours** sur le draft avant d'envoyer.

Exemples session 17/04 :
1. v1 "Petit message pour t'annoncer" → user : "soit plus en mode super nouvelle on est trop content"
2. v2 "Super nouvelle…" + URL inline → user : "ça fait deux 'sur', dis 'sur notre site'"
3. v3 final "depuis ton espace perso sur notre site !" + lien Drive séparé

Toujours **draft + go explicite** avant tout envoi (règle transversale).

---

## Étape 5 — Test sur compte perso

Tester sur **`@le.chabrax`** (compte personnel Antoine, identifié comme `Antoine` dans Insta).

```python
mcp_instagram_dms__send_message(username="le.chabrax", message=...)
```

→ Antoine vérifie le rendu (lien cliquable, ton, mise en page) avant le blast réel.

---

## Étape 6 — Blast Instagram (script Python)

⚠️ **L'envoi vidéo via DM API n'est plus supporté par Instagram** (constat 17/04/2026 : `cl.direct_send_video()` retourne `"This feature is no longer supported."`). On envoie donc **lien Drive en texte** dans le message.

### Pourquoi un script Python externe et pas le MCP ?
- Le harness Claude Code bloque les `sleep` standalone → impossible d'espacer 100+ envois proprement depuis Claude
- Le script tourne en background pendant que tu fais autre chose
- Reprend où ça s'était arrêté via `sent_log.json` (zéro doublon possible)

### Recette technique
Voir [`runbooks/blast-instagram-script.md`](../runbooks/blast-instagram-script.md) pour le code complet du `blast_avis.py`.

### Cadence observée
| Setup | Cadence | 137 ambassadeurs |
|---|---|---|
| Délai 5-10s + extraction `user_info` Insta | ~22s/msg | ~50 min |
| Délai 5-10s + prénom du Sheet (recommandé) | ~10s/msg | ~22 min |
| Délai 4-7s sans prénom | ~5s/msg | ~11 min |

### Lancement
```bash
cd tools/ContentInflu/AvisVideo-17-04-26
uv run python blast_avis.py >> blast.log 2>&1 &
```

### Monitoring
```bash
# Live status
grep -cE "✅" blast.log
grep -E "✅|❌|DONE" blast.log | tail -5
```

### Échecs typiques (à accepter, pas paniquer)
- `Target user not found` → handle changé/compte supprimé. Rare (1/137 en session 17/04).
- `JSONDecodeError public_request ?__a=1` → bruit instagrapi sur route publique dépréciée, l'envoi DM passe quand même via API privée.
- `Status 201` warning → idem bruit, pas un échec.

---

## Étape 7 — Blast Email Outlook

### Méthode CCI manuelle (recommandée pour un blast d'ambassadeurs)
Pourquoi pas un mailing automatisé : c'est un blast **relationnel** (135 personnes max), pas une campagne marketing. Outlook + CCI suffit, garde la main sur la perso.

```
1. Ouvrir Outlook → Nouveau message
2. À : ton email perso (pour avoir une copie en sent)
3. CCI : copier-coller toute la liste depuis emails_outlook.md (séparée par ;)
4. Objet + corps : copier depuis emails_outlook.md (variantes prêtes)
5. Joindre vidéo + envoyer
```

### Pourquoi CCI et pas À ?
- **Confidentialité** : aucun ambassadeur ne voit les emails des autres
- **Anti-spam** : 135 destinataires en À déclencherait les filtres Gmail/Outlook

---

## Mise à jour du Sheet après blast

Si on a récupéré des emails via DM Insta ou Shopify, les **rajouter dans col AF** du Sheet pour les futures campagnes :

```python
mcp_google_sheets__batch_update_cells(
    sheet="Suivi_Amb",
    ranges={"AF38": [["anais.roux69@outlook.fr"]], ...}
)
```

---

## Red flags / à éviter

| ❌ Ne pas faire | ✅ À la place |
|---|---|
| Envoyer la vidéo en attachement DM Instagram | Lien Drive (API DM video supprimée) |
| Login fresh `cl.login()` depuis script | Réutiliser session MCP `data/sessions/{user}_session.json` |
| `cl.user_info()` pour chaque handle dans une boucle | Lire prénoms depuis Sheet col AE en bulk |
| Délai < 4s entre envois | Garder min 4s (5-10s safe) sinon ban risk |
| Email vouvoiement / "L'équipe Impulse" | Tutoiement + signature Antoine (relation ambassadeur) |
| Mettre 135 emails en À | Toujours en CCI (confidentialité + anti-spam) |
| Forcer un `{prenom}` douteux ("Lol", "Le") | Fallback `Hello !` proprement |

---

## Cross-links

- Script complet : [`runbooks/blast-instagram-script.md`](../runbooks/blast-instagram-script.md)
- Conventions tone Antoine : [`conventions/tone-voice-rules.md`](../conventions/tone-voice-rules.md)
- Workflow individuel ambassadeur : skill `/instagram-dm` (NE PAS utiliser pour blast)
