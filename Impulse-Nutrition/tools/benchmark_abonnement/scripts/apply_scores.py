"""
apply_scores.py — One-shot qui applique les notes /5 calibrées aux 8 marques.

Notes figées en fin de revue pass 1 (2026-04-15) après vérif live
homogène des 8 marques. Calibrage :
- UX /5 : toggle, prix, page dédiée, mention home/nav, email pré-exp, CTA, fréquences
- Offre /5 : remise %, livraison abo, engagement, stacking, catalogue, fidélité, lisibilité
- Pertinence /5 : positionnement vs Impulse (premium FR santé/sport, tech, catalogue, audience)
- Global = moyenne arithmétique des 3
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARQUES = ROOT / "marques"

SCORES = {
    "nutriandco": {
        "ux": 3.5,
        "offre_commerciale": 4.0,
        "pertinence_vs_impulse": 4.5,
        "global": 4.0,
        "rationale": {
            "ux": "Toggle clair + prix abonné visible + page dédiée + email pré-expédition avec fenêtre modif 48h. Mais pas de mention homepage, pas de mention navigation, seulement 2 fréquences (1/3 mois), CTA basique 'S'abonner'.",
            "offre": "−15% flat + livraison domicile offerte sans seuil + zéro engagement + programme fidélité cumulable. Pénalisé par seulement 2 fréquences et zéro stacking codes.",
            "pertinence": "LA référence à benchmarker pour Impulse. Positionnement premium FR santé quasiment identique, même tech Shopify (même agence Axome), même catalogue compléments gélules/capsules/poudres. Score maximal justifié.",
        },
    },
    "nutrimuscle": {
        "ux": 4.0,
        "offre_commerciale": 4.0,
        "pertinence_vs_impulse": 3.5,
        "global": 3.8,
        "rationale": {
            "ux": "Page dédiée complète + mention homepage + mention navigation + mention emails + 6 fréquences + toggle clair + badge remise. Pas d'affichage € économisé et email pré-expédition non confirmé.",
            "offre": "−15% flat + livraison domicile offerte + zéro engagement + 6 fréquences flexibles + stacking partiel sélectif (codes influenceurs OK) + Nm Club fidélité. Très solide.",
            "pertinence": "Positionnement muscu/perf plus que santé mix. Même tech (Shopify), catalogue 250+ SKUs. Bonne pertinence mais moins proche d'Impulse qui touche santé + sport.",
        },
    },
    "novoma": {
        "ux": 3.5,
        "offre_commerciale": 3.0,
        "pertinence_vs_impulse": 4.5,
        "global": 3.7,
        "rationale": {
            "ux": "Page dédiée très bien structurée (processus 3 étapes + 5 avantages + FAQ complète) + argumentation santé unique 'les compléments marchent mieux sur le long terme'. Mais pas de mention homepage/navigation.",
            "offre": "Remise −10% = la plus faible du panel pour les marques avec abo classique. Compensé partiellement par la livraison stepped (3,50€ + seuil 50€) et les points fidélité cumulables. Friction : points non dépensables sur abo, Colissimo domicile uniquement.",
            "pertinence": "Même positionnement premium FR santé, même tech Shopify (même agence Axome que Nutri&Co). Catalogue et ADN très proches d'Impulse. Score maximal justifié.",
        },
    },
    "nutripure": {
        "ux": None,
        "offre_commerciale": None,
        "pertinence_vs_impulse": 4.5,
        "global": None,
        "rationale": {
            "ux": "N/A — pas d'abonnement, pas de toggle, pas de page dédiée abo, pas de parcours abonné.",
            "offre": "N/A — pas d'abonnement. Mécanismes alternatifs (packs permanents -10 à -25%, programme fidélité 10% crédité, parrainage) approchent l'économie d'un abo -15% sans lock-in contractuel.",
            "pertinence": "Très pertinent POUR LE DECK comme contre-exemple : même positionnement premium FR santé/sport qu'Impulse, même taille catalogue, même exigence qualité. Rôle de contrôle : prouve qu'on peut fidéliser sans abo si on a des packs permanents + programme fidélité + ticket moyen élevé.",
            "note": "Pas de note globale — rôle de contrôle dans le panel, pas un modèle à scorer.",
        },
    },
    "cuure": {
        "ux": 4.0,
        "offre_commerciale": 3.0,
        "pertinence_vs_impulse": 2.0,
        "global": 3.0,
        "rationale": {
            "ux": "Parcours ultra fluide, quiz engageant ~5 min, app mobile pour suivi quotidien, site entier orienté abo (page dédiée = site complet), mention home/nav, sachets personnalisés avec prénom. Pénalisé par la friction résiliation en 2 temps (suspension self-serve vs email pour résilier).",
            "offre": "Modèle unique 100% abo mais pricing variable 18-40€/mois selon composition (lecture difficile), friction résiliation 2 temps, engagement psychologique fort mais pas d'économie facile à lire vs les concurrents qui affichent un % flat clair.",
            "pertinence": "Modèle 100% abo personnalisé avec quiz santé + comité scientifique + sachets quotidiens. Impulse est un e-commerce catalogue classique. Trop éloigné structurellement — Cuure est un service de bien-être, pas un retailer nutrition. Utile comme contre-modèle extrême mais pas comme inspiration directe.",
        },
    },
    "decathlon": {
        "ux": 2.5,
        "offre_commerciale": 3.0,
        "pertinence_vs_impulse": 2.0,
        "global": 2.5,
        "rationale": {
            "ux": "Sous-domaine séparé (friction redirect), 1 produit = 1 abo (mauvaise UX multi-abos), modification = résiliation + recréation (anti-pattern), UX basique. Compensé partiellement par la page dédiée + processus 4 étapes + mention homepage + prix plancher très bas 12,74€.",
            "offre": "−10 à −15% stepped par produit (pattern rare), livraison offerte en relais uniquement, programme fidélité Decat'Club cumulable (vrai atout, points sur compte global échangeables contre cartes cadeaux/services/livraison), engagement zéro. Pénalisé par modification = résiliation + recréation.",
            "pertinence": "Grande distribution omnicanale, positionnement opposé à Impulse (volume vs premium). Decathlon = contre-modèle UX à exposer dans le deck, pas une inspiration. Seul atout reproductible : le programme fidélité cumulable cross-canal.",
        },
    },
    "aqeelab": {
        "ux": 4.5,
        "offre_commerciale": 4.0,
        "pertinence_vs_impulse": 4.5,
        "global": 4.3,
        "rationale": {
            "ux": "Toggle clair + **montant économisé affiché en euros** (pattern persuasif unique dans le panel) + CTA explicite 'S'abonner & économiser' + page dédiée '20% A VIE' + mention homepage + mention navigation + affichage prix barré + prix abonné. Presque parfait, pénalisé uniquement par l'absence d'email pré-expédition documenté.",
            "offre": "Remise −20% flat à vie = la plus haute du panel pour les marques avec abo classique. Pénalisé par l'engagement 2 mois minimum (friction d'entrée + point vigilance Loi Chatel), l'ambiguïté sur la livraison abo, et le zéro stacking codes. L'offre massue est tempérée par les frictions.",
            "pertinence": "Même tech Shopify, même positionnement FR premium pur, taille catalogue comparable (23 SKUs = ordre de grandeur Impulse), prix premium cohérents, expédition Bordeaux 24-48h, éco-responsable. C'est LE miroir le plus ambitieux pour Impulse.",
        },
    },
    "myprotein": {
        "ux": 3.5,
        "offre_commerciale": 3.5,
        "pertinence_vs_impulse": 1.5,
        "global": 2.8,
        "rationale": {
            "ux": "Toggle clair, page dédiée /c/subscribe/, bannière homepage avec CTA 'Souscrire', mention navigation, 5 fréquences. Mais UX globale confuse à cause des prix volatils et des promos empilées. Verbatim client *'attention aux prix qui changent'* pénalise la note.",
            "offre": "Remise variable jusqu'à −45% (généreux en théorie, illisible en pratique) + livraison offerte sans seuil + zéro engagement + 5 fréquences + stacking partiel avec promos sitewide. MAIS remise affichée sur un prix-barré déjà volatil (promos permanentes sitewide) = vraie économie perçue difficile à lire. Trustpilot 3,1/5 sur 31k avis = signal de confiance faible.",
            "pertinence": "Mass-market volume international très éloigné d'Impulse FR premium. UK warehouse, SAV critiqué, catalogue 1000+ SKUs. Contre-modèle à afficher dans le deck, pas une inspiration. Pertinence la plus faible du panel.",
        },
    },
}


def main() -> None:
    for slug, scores in SCORES.items():
        brand_path = MARQUES / slug / "data.json"
        if not brand_path.exists():
            print(f"  [skip] {slug} — data.json missing")
            continue

        data = json.loads(brand_path.read_text(encoding="utf-8"))
        ev = data.get("evaluation", {})
        ev["score_ux"] = scores["ux"]
        ev["score_offre_commerciale"] = scores["offre_commerciale"]
        ev["score_pertinence_vs_impulse"] = scores["pertinence_vs_impulse"]
        ev["score_global"] = scores["global"]
        ev["rationale"] = scores["rationale"]
        ev["note"] = (
            "Scores calibrés en fin de revue pass 1 (2026-04-15) après vérif live homogène "
            "des 8 marques. Grille : UX / Offre / Pertinence vs Impulse + Global = moyenne arithmétique."
        )
        data["evaluation"] = ev

        brand_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        score_str = f"UX={scores['ux']} Offre={scores['offre_commerciale']} Pert={scores['pertinence_vs_impulse']} Global={scores['global']}"
        print(f"  [ok] {slug:12} {score_str}")

    print("\nDone. Run `python3 benchmark/build_master.py` to rebuild master_data.json.")


if __name__ == "__main__":
    main()
