# Novoma — notes de revue

## Statut audit
- Audit status : `verified_live` (page abo officielle WebFetch 2026-04-15 + croisée avec 2 sources externes)

## Vérifs live (2026-04-15)

### Modèle livraison stepped — confirmé ✅ (différenciation majeure vs Nutri&Co et Nutrimuscle)
Contrairement aux 2 marques précédentes qui offrent la livraison **100% flat sans seuil**, Novoma propose un modèle **intermédiaire** :
- Frais réduits : **3,50€** en Colissimo domicile (vs 4,90€ standard) → économie de 1,40€
- Seuil gratuit abaissé : **gratuit dès 50€** d'achat (vs 90€ standard) → seuil 44% plus bas
- **Contrainte forte** : Colissimo domicile uniquement. Pas de point relais ni DPD disponibles pour une commande 100% abo (sauf si mélange avec des produits en achat simple)
- 2 jours ouvrés

C'est un **positionnement plus prudent côté marge** : Novoma préserve une marge sur la livraison des petits paniers (15-30€) que Nutri&Co/Nutrimuscle sacrifient totalement. À mettre en perspective : Novoma n'offre que -10% de remise vs -15% chez les 2 autres, donc le combo "faible remise + livraison partiellement subventionnée" = **positionnement rentabilité** vs le combo "forte remise + livraison gratuite = positionnement acquisition" des concurrents.

**Implication Impulse** : on a maintenant 2 modèles antagonistes dans le panel (−10% + livraison partielle vs −15% + livraison offerte). Ça donne une matrice de décision claire pour la reco finale.

### Stacking codes × abo — confirmé ✅
Citation officielle : *"valable uniquement sur la 1ère livraison"* pour les codes promo en mode abo. C'est une règle intermédiaire entre :
- Nutri&Co : zéro stacking (le code et l'abo s'excluent mutuellement)
- Nutrimuscle : stacking partiel sélectif (codes influenceurs OK, codes génériques bloqués)
- **Novoma : stacking limité temporellement** (codes OK mais uniquement sur la 1ère commande de l'abo, pas sur les renouvellements)

Pattern intéressant : Novoma **récompense l'acquisition via code + abo combinés** mais **coupe le cumul dès le 2e renouvellement** pour protéger la marge long terme.

### Points fidélité — anti-pattern intentionnel ⚠️
Citation officielle : *"les points de fidélité ne sont pas utilisables pour une commande par abonnement"* mais *"vous collectez quand même vos points"*.

**C'est un mécanisme anti-pattern surprenant mais potentiellement génial** :
- Le pure subscriber accumule des points sans jamais pouvoir les dépenser sur ses renouvellements
- Pour convertir ses points, il **doit faire au moins 1 commande one-shot** (packs, nouvelles lignes, cadeaux)
- → force des ventes incrémentales sur la base abo
- → mais c'est aussi une friction potentielle perçue par le client ("je collectionne pour rien")

**Implication Impulse** : mécanisme à double tranchant. Si Impulse a un programme fidélité, la question se pose : cumulable OU utilisable sur l'abo ? Chaque choix a ses arguments.

### Produits exclus — aucun listé explicitement
La page abo officielle ne liste **aucune exclusion**. Tous les produits individuels semblent éligibles. Les packs probablement exclus (cohérent avec le modèle "1 produit = 1 abonnement" des 2 autres marques FR) mais à confirmer navigation live si crucial. Priorité basse.

## Décisions / corrections

| Champ | Avant | Après | Source |
|---|---|---|---|
| `modele_commercial.remise_note` | `"Abonnement -10% + avantages livraison"` | Version détaillée avec contexte marché | /pages/abonnement |
| `modele_commercial.engagement_min` | `"Aucun"` | `"Aucun (annulation jusqu'à la veille du renouvellement)"` | FAQ abo |
| `modele_commercial.livraison_abo.offerte` | `null` | `false` (stepped, pas flat) | /pages/abonnement |
| `modele_commercial.livraison_abo.seuil_eur` | `null` | `50` (vs 90€ standard) | /pages/abonnement |
| `modele_commercial.livraison_abo.note` | `null` | Note détaillée modèle stepped Colissimo domicile uniquement | /pages/abonnement |
| `perimetre_produit.scope` | `"Tous les produits du catalogue"` | `"Tous les produits individuels du catalogue (...) modèle '1 produit = 1 abonnement'"` | /pages/abonnement |
| `perimetre_produit.exclusions` | `[]` | 1 entrée conjecture (packs à confirmer) | Analogie + pattern marché |
| `ux_page_produit.dedicated_page_url` | — | `https://novoma.com/pages/abonnement` ajouté | Confirmed live |
| `evaluation.strengths` | 5 items | 7 items (ajouté : points cumulés, Trustpilot 4.6) | Vérifs live |
| `evaluation.weaknesses` | 3 items | 5 items (ajouté : points non dépensables, codes 1ère livraison only) | Vérifs live |
| `_meta.audit_status` | `raw` | `verified_live` | — |

## Questions ouvertes
- **Packs abonnables ou pas ?** Pas explicitement confirmé. Conjecture cohérente avec le pattern marché. Bas priorité.
- **Email pré-expédition** avec fenêtre de modification ? Non documenté. À vérifier via parcours abonné live (pas trivial sans créer un compte test).
- **Mise en avant homepage/nav** : master_data dit non. À re-vérifier car c'est un gap important vs Nutrimuscle qui a ✅✅. Si effectivement pas mis en avant, c'est une faiblesse UX notable.
- **Notes /5** — propositions sparring : UX 4.0 (page dédiée complète mais pas de mention home/nav) / Offre 3.5 (−10% modeste, stepped livraison intelligent mais moins sexy) / Pertinence 4.5 (santé/conviction très proche Impulse, même positionnement premium France) / Global 4.0. **À trancher avec les 4 autres marques.**
