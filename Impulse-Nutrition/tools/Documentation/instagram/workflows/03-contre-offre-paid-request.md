# Workflow 03 — Contre-offre dotation structurée (prospect demande paid)

> Le prospect accepte le pitch s2 mais demande explicitement une dimension financière / structurée. On ne promet **jamais** de paid, mais on propose une **dotation structurée** qui couvre ses besoins sur la saison. Template `s4b_dotation_contre_offre` créé le 17/04/2026 spécifiquement pour ce cas.

## Quand utiliser

- Prospect a répondu positivement au pitch s2
- Mais demande une dimension financière / "est-ce qu'il y a du rémunéré possible ?"
- Profil pro / structure ses partenariats pour financer sa saison
- Typique : pro athlètes (triathlète, coureur), profils avec communauté 10k+

## Principe

- **Acknowledge positive** de sa démarche de structuration (sans être défensif)
- **Pivot direct vers l'offre** (pas "on ne fait pas de paid" défensif)
- Proposer **dotation sur durée** (ex: 4 mois × 120€/mois) comme réponse à son besoin de structuration
- Demander contrepartie chiffrée : objectif d'utilisations code affilié (ex: 16 sur 4 mois)
- **Ouvrir la porte au call** pour en discuter de vive voix

## Template `s4b_dotation_contre_offre` (verbatim)

```
Merci pour ta réponse {prenom}, et pour ta transparence sur tes enjeux de saison, c'est vraiment appréciable 😊

On comprend tout à fait que tu cherches à structurer tes partenariats sur cette saison. Ce qu'on peut te proposer pour t'accompagner au mieux dans ta pratique, c'est une dotation sur {duree_mois} mois : {envelope_mensuelle} de produits offerts chaque mois (tu choisis librement selon tes besoins : boisson d'effort, gels, whey, électrolytes, ce que tu veux). En contrepartie, on te demande un objectif de {utilisations_min} utilisations de ton code affilié sur l'ensemble de la période.

Concrètement, ça te permet de couvrir tes besoins nutrition sur toute la saison sans rien avancer, et on peut faire un point ensemble à la fin pour voir comment on continue.

Qu'en penses-tu ? Et si tu préfères qu'on en parle de vive voix, dis-moi une date qui t'arrange la semaine prochaine, je m'adapte.

Sportivement,
Antoine
```

**Variables** : `{prenom}`, `{envelope_mensuelle}` (ex: 120€), `{duree_mois}` (ex: 4), `{utilisations_min}` (ex: 16).

## Exemple — Alexia Bailly (@alexia__bailly)

### Contexte

- **Pro Triathlète**, communauté 9 655 followers, Sports Marketing
- Connue pour apprécier Mathilde Gauthier (notre égérie)
- Pitché s2 le 14/04/2026
- A répondu 16/04 : intéressée mais demande explicitement "partenariat avec dimension financière"

### Son message (16/04)

```
Hello Antoine,

Merci beaucoup pour ton message et pour l'intérêt, ça me fait plaisir ! J'ai déjà entendu parler d'Impulse Nutrition, grâce à votre super égérie Mathilde Gauthier 😉 donc je vois bien votre univers et les produits ont l'air qualitatifs.

Je serais partante pour tester vos produits et à échanger sur une éventuelle collaboration ! Mais aujourd'hui, avec mon activité de triathlète professionnelle, j'essaie aussi de structurer mes partenariats de manière à pouvoir financer une partie de ma saison et mes déplacements sur le circuit international.
Du coup, je voulais savoir si vous envisagez parfois des collaborations avec une dimension financière, ou si c'est quelque chose qui pourrait se discuter ensemble ?

N'hésite pas à me dire ce qu'il en est. Je suis aussi disponible par téléphone : 0638417671
Bonne soirée
Alexia
```

### Draft envoyé (s4b rempli avec variables)

```
Merci pour ta réponse Alexia, et pour ta transparence sur tes enjeux de saison, c'est vraiment appréciable 😊

On comprend tout à fait que tu cherches à structurer tes partenariats sur cette saison. Ce qu'on peut te proposer pour t'accompagner au mieux dans ta pratique, c'est une dotation sur 4 mois : 120€ de produits offerts chaque mois (tu choisis librement selon tes besoins : boisson d'effort, gels, whey, électrolytes, ce que tu veux). En contrepartie, on te demande un objectif de 16 utilisations de ton code affilié sur l'ensemble de la période.

Concrètement, ça te permet de couvrir tes besoins nutrition sur toute la saison sans rien avancer, et on peut faire un point ensemble à la fin pour voir comment on continue.

Ça te parle comme base de départ ? Si tu préfères qu'on en parle de vive voix, dis-moi une date qui t'arrange la semaine prochaine, je m'adapte !

Sportivement,
Antoine
```

*(Remarque : "Ça te parle" a été banni **après** ce message — corrigé dans templates.yaml à "Qu'en penses-tu"). Le message actuellement envoyé à Alexia contient encore l'ancienne formulation.*

### Sheet update

```
Suivi_Amb L542:
  J = "In-hot"  (était "In-cold")
  K = "dotation 120€×4mois / 16 util proposée le 17/04 (pitch paid acknowledgé)"
  L = "high"
```

## Évolutions du draft (leçons session)

### v1 (initiale)
"Pour te répondre honnêtement : on ne propose pas de partenariat purement rémunéré, mais on a un système de dotation structuré..."

→ **Rejeté par Antoine** : trop défensif, phrase négative "on ne propose pas"

### v2 (finale — celle envoyée)
"On comprend tout à fait que tu cherches à structurer tes partenariats sur cette saison. Ce qu'on peut te proposer pour t'accompagner au mieux dans ta pratique, c'est..."

→ **Validé** : positive, acknowledge + pivot direct vers offre

### Leçon

**Ne jamais ouvrir sur "on ne propose pas X"**. Toujours acknowledge positivement le besoin du prospect + pivot vers ce qu'on peut proposer.

## Red flags

| Red flag | Conséquence |
|---|---|
| Promettre "on va voir si on peut faire du paid" | Faux espoir, Antoine ne peut pas engager sans Pierre |
| "On ne fait pas de paid" (défensif) | Fermeture de conversation trop abrupte |
| Oublier d'ouvrir la porte au call | Perte de l'engagement live qui est souvent crucial pour pros |
| Utiliser "Ça te parle ?" | **Banni** depuis 17/04/2026 |

## Follow-up si accepté

Si le prospect accepte la dotation structurée proposée :
→ Workflow [02-dotation-recurrente-4mois](./02-dotation-recurrente-4mois.md)
→ Call si elle choisit cette option, sinon envoi direct M1

## Source de vérité

- `knowledge/voice/templates.yaml::s4b_dotation_contre_offre` (ajouté 17/04/2026)
- Workflow suite : `02-dotation-recurrente-4mois.md`
