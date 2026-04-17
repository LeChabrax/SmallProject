# Classification des tickets — Gorgias

Chargé par `/gorgias` à l'Étape 5 (classification).

Choisir **UNE** catégorie mutuellement exclusive. Si plusieurs pourraient matcher, utiliser l'ordre de priorité en bas de ce fichier.

## Mapping catégorie ↔ code template

Chaque catégorie ci-dessous pointe vers un template pré-rédigé dans **[templates.md](templates.md)** :

| Catégorie | Code template | Variantes |
|---|---|---|
| `waiting_customer_reply` | G0 | N/A (skip) |
| `SAV_colis_bloqué` | G1 | A (pickup) / B (in_transit) / C (lost) |
| `SAV_produit_cassé_manquant` | G2 | A (cassé + photo) / B (cassé sans photo) / C (manquant) |
| `SAV_returned_to_sender` | G3 | A (proposer refund/reship) / B (reship confirmé) |
| `SAV_partial_return` | G4 | unique |
| `SAV_bad_rating_bigblue` | G5 | A (avec commentaire) / B (sans commentaire) |
| `SAV_remboursement_demandé` | G6 | A (éligible) / B (hors conditions) |
| `question_commande_status` | G7 | A (en préparation) / B (expédié) |
| `question_produit_info` | G8 | unique |
| `question_affiliate_code` | G9 | A (ambassadeur) / B (non-ambassadeur) |
| `question_frais_port` | G10 | A (France métro) / B (international) |
| `modification_adresse_preexpé` | G11 | A (pre-ship) / B (post-ship) |
| `annulation_commande` | G12 | A (pre-ship) / B (post-ship) |
| `double_charge_paiement` | G13 | unique (escalade) |
| `partenariat_refus_small` (nouveau) | G14 | A (UGC + ACHAB25) / B (sponsoring petit event) |
| `partenariat_redirect` (nouveau, remplace `candidature_ambassadeur` pour partenariats hors influence) | G15 | A (redirect Pierre) / B (refus distribution) |
| `candidature_ambassadeur` (strict influence) | N/A — redirect IG @impulse_nutrition_fr | — |
| `candidature_recrutement_rh` | G16 | A (redirect RH) / B (refus poli) / C (clin d'œil école) |
| `bascule_insta_ambassadeur` (nouveau) | G17 | unique (ton tu/Antoine exceptionnel) |
| `spam_ou_hors_sujet` | — | close silencieux |
| `review_required` | — | escalade Antoine, pas de template |

**Note nouvelles catégories G14-G17** : extraites des patterns observés en avril 2026 (pass SAV du 17/04). Elles complètent les 17 catégories originelles ci-dessous avec une granularité plus fine sur les partenariats et la bascule cross-channel Insta.

---

## Table des 17 catégories (originelle)

| Catégorie | Keywords / signal | Action requise |
|---|---|---|
| `waiting_customer_reply` | **RÈGLE PRIORITAIRE** — `last_message.from_agent == true` (le SC a déjà répondu en dernier, on attend le retour client) | **SKIP automatique** → pas de draft, pas de carte complète. Produire une carte condensée 1 ligne : `## Ticket #{id} · ✅ en attente client (SC a répondu le {date}). Pas d'action.` et passer au ticket suivant. **Ne jamais relancer automatiquement** même après plusieurs jours, Antoine arbitre les relances manuellement. |
| `SAV_colis_bloqué` | Tracking loop, "jamais reçu", "bloqué en transit", Chronopost misrouted, pickup "held at location" | **Replacement draft Shopify** (reference/sav_recipe.md) avec geste commercial (bidon/shaker) + ship **home address** (pas pickup point) + pickup manuel BigBlue après complete_draft + reply Gorgias. Référence `process_sav_unified.md` §2.1. |
| `SAV_returned_to_sender` | 2 points relais refusés, retour expéditeur automatique | Proposer refund **OU** reship home + geste commercial. **Wait customer response** avant d'agir. Référence §2.2. |
| `SAV_partial_return` | Retour partiel, Shopify `financial_status=partially_refunded`, BigBlue `RETURNED` | Vérifier `refunds` array sur `get_order` : si processé → confirmer montant + 3-5 jours ouvrés. Sinon → refund manuel via Shopify admin UI (MCP refund pas implémenté). Référence §2.3. |
| `SAV_bad_rating_bigblue` | Tag `bigblue-bad-rating-no-comment` ou `bigblue-bad-rating-with-comment` | Lire le commentaire si présent via `get_support_ticket` BigBlue. Apology + demande contexte. Si issue côté service → proposer discount code. **Reply sur Gorgias** (pas BigBlue), close quand répondu. Référence §2.4. |
| `SAV_produit_cassé_manquant` | "cassé", "abîmé", "endommagé", "manquant", "pas dans le colis", "fuite" | 1. BigBlue claim via `create_support_ticket` (en français). 2. Replacement draft si produit remplaçable (reference/sav_recipe.md). 3. Reply confirmant au client. |
| `SAV_remboursement_demandé` | "remboursement", "refund", "annulation après livraison" | Vérifier éligibilité (conditions retour 14 jours article par article). Si éligible → refund manuel via Shopify admin UI + reply confirmation. Si hors conditions → expliquer + proposer alternative (échange, avoir). |
| `question_commande_status` | "où est ma commande", "tracking", "quand je reçois", "numéro de suivi" | `mcp__bigblue__get_tracking(order_id=...)` → reply avec statut réel. **❌ Jamais de délai chiffré** (`48-72h`), utiliser `"dès que nous avons du nouveau"`. |
| `question_produit_info` | Dosage, allergène, goût, composition, compatibilité, vegan, sans gluten | Reply avec info produit. Cross-ref `knowledge/impulse.md#4-catalogue-produits` pour composition. Si doute technique → escalader à l'équipe produit. |
| `question_affiliate_code` | "mon code ne marche pas", "mes crédits", "Affiliatly", "je suis ambassadeur" | Si customer dans `Suivi_Amb`/`Dot`/`Paid` → **STOP draft SC standard** → signaler à Antoine pour traitement direct (cas particulier ambassadeur). Cross-ref `knowledge/operations.md#calculer-et-redeem-le-crédit-ambassadeur`. |
| `modification_adresse_preexpé` | "changer adresse", "je me suis trompé d'adresse", **AVANT expédition** (Shopify `fulfillment_status=null` ou `partial`) | `mcp__shopify__update-order` pour modifier l'adresse + reply confirmant. Si déjà expédié (`fulfilled`) → `mcp__bigblue__update_order` pour re-router. |
| `annulation_commande` | "annuler", "stop", **AVANT expédition** | `mcp__shopify__update-order` avec cancellation. Si déjà fulfillment en cours → `mcp__bigblue__cancel_order`. Si trop tard → expliquer + retour quand reçu. |
| `double_charge_paiement` | "j'ai été débité deux fois", "fraude", transactions multiples | Vérifier Shopify `transactions` array. Si vraie double charge → escalade Antoine (refund à faire manuellement). Si autorisation bancaire normale → expliquer. |
| `candidature_ambassadeur` | **Programme influenceur uniquement** — tag `candidature` + "je voudrais être ambassadeur", "partenariat influence", "promotion de vos produits à ma communauté", SANS aucune mention de rôle pro (stage, emploi, CV, école, alternance, etc.) | **Ne pas drafter via Gorgias**. Rediriger gentiment : `"Pour toute demande de partenariat ambassadeur, nous vous invitons à nous contacter via nos DMs Instagram @impulse_nutrition où notre responsable partenariats vous répondra."`. Close le ticket. |
| `candidature_recrutement_rh` | **Recrutement / stage / emploi** (distinct de l'ambassadeur) — keywords : "stage", "emploi", "recrutement", "CV", "candidature spontanée", "école d'ingénieur", "apprentissage", "alternance", "master", "post-bac", "AgroParisTech", "je cherche un stage", "RH", + mention d'un rôle pro (ingénieur, marketing, commercial, RH, communication, etc.). **Edge case** : si la personne mentionne à la fois "stage" ET "partenariat ambassadeur" → **priorité à RH = escalade Antoine**, jamais rediriger vers Instagram DM. | **ESCALADE SYSTÉMATIQUE À ANTOINE** — pas de draft auto, pas de template, pas d'email RH par défaut. Carte non-draftable type : `### Action manuelle requise — ESCALADE ANTOINE` / `⚠️ Candidature recrutement RH reçue` / `Profil : {école/niveau}, rôle recherché : {type}, dispo : {dates}` / `→ Décision Antoine : forwarder à RH HCS / répondre soi-même / close sans réponse`. Ne jamais répondre automatiquement. Antoine arbitre au cas par cas. |
| `spam_ou_hors_sujet` | Pub B2B, prospection, newsletter, hors sujet manifeste | Close silencieusement sans reply. Ne pas engager. |
| `review_required` | Rien ne match clairement, cas complexe, émotion forte client | Classifier en `review_required` et demander l'arbitrage à Antoine avant draft. **Pas de draft automatique**. |

## Ordre de priorité (si plusieurs catégories matchent)

0. **`waiting_customer_reply`** (PRIORITÉ ABSOLUE — si `last_message.from_agent == true`, skip avant tout autre traitement, ne pas évaluer les autres catégories)
1. `spam_ou_hors_sujet` (si clairement spam, close avant tout)
2. **`candidature_recrutement_rh`** (si keywords RH présents, escalade Antoine — **même si la personne mentionne aussi "ambassadeur"** : priorité à RH)
3. `candidature_ambassadeur` (rediriger IG, close — **uniquement si AUCUN keyword RH**)
4. `SAV_bad_rating_bigblue` (tag spécifique, traitement prioritaire)
5. `SAV_colis_bloqué` / `SAV_returned_to_sender` (urgence livraison)
6. `SAV_produit_cassé_manquant` (SAV physique)
7. `SAV_partial_return` / `SAV_remboursement_demandé` (refund)
8. `double_charge_paiement` (sensibilité paiement)
9. `modification_adresse_preexpé` / `annulation_commande` (timing critique)
10. `question_commande_status` (info)
11. `question_produit_info` (info)
12. `question_affiliate_code` (ambassadeur, cas particulier)
13. `review_required` (fallback)

## Règles de décision

- **Si customer ambassadeur détecté à l'Étape 3** → override toute catégorisation → `review_required` + signaler à Antoine
- **Si 2 catégories SAV possibles** (ex : produit cassé ET remboursement demandé) → choisir celle qui a l'action la plus concrète (replacement > refund pur si le produit est remplaçable)
- **Si le client menace** (avocat, mise en demeure, avis négatif public) → `review_required` même si la catégorisation technique est claire
- **Si le ticket est vieux** (> 7 jours sans réponse SC) → ajouter automatiquement une excuse légère en tête du draft : `"Bonjour {Prénom}, nous vous prions de nous excuser pour le délai de réponse."`
