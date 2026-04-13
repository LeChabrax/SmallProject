# Tri influenceurs KolSquare - Règles de filtrage

## Objectif

Filtrer un export KolSquare pour identifier les profils éligibles au **programme ambassadeur dotation** Impulse Nutrition (~80€ de produits gratuits + code affilié -15%).

Cible : créateurs de contenu sport / fitness / bien-être avec une communauté engagée, alignés avec l'univers Impulse Nutrition.

---

## 1. Règles d'exclusion par métier

Exclure tout profil dont le métier principal n'a aucun lien avec le sport, le fitness ou le lifestyle actif.

### Métiers exclus

| Métier | Raison |
|--------|--------|
| `politics` | Hors cible |
| `actor`, `fim_actor` | Hors cible |
| `singer`, `musician`, `dj` | Hors cible |
| `artist`, `illustrator`, `photographer` | Hors cible |
| `humorist`, `animator` | Hors cible |
| `journalist`, `speaker` | Hors cible |
| `chef`, `food_critic`, `oenologist` | Hors cible (alimentation mais pas sport) |
| `doctor` | Hors cible (sauf si profil sport, a vérifier au cas par cas) |
| `ceo`, `management`, `marketing_and_communication` | Hors cible |
| `fashion_designer`, `hairdresser`, `makeup_artist`, `interior_designer` | Hors cible |
| `dancer` | Hors cible (sauf si contenu fitness, rare) |
| `producer` | Hors cible |
| `tatooist` | Hors cible |

---

## 2. Règles d'inclusion par métier

### Inclus automatiquement (sport / fitness)

| Catégorie | Métiers |
|-----------|---------|
| **Fitness** | `fitness`, `fitness_athlete`, `fitness_coach`, `coach`, `weight_lifting` |
| **Running / Athlétisme** | `running`, `cross_country_running`, `athletics`, `other_athletics`, `track_race`, `long_jump`, `pole_vaulting` |
| **Endurance** | `triathlon`, `cycling`, `mountain_biking`, `swimming`, `canoeying`, `ski_mountaineering` |
| **Sports de combat** | `boxing`, `english_boxing`, `fighting`, `kickboxer`, `judo` |
| **Sports collectifs** | `rugby`, `football`, `basketball`, `badminton` |
| **Sports outdoor** | `adventurer`, `climbing`, `surfing`, `skiing`, `snowboard`, `skateboard`, `horse_riding`, `windsurfing` |
| **Sports mécaniques** | `moto_cross`, `motocycling`, `match_racing` |
| **Autres** | `gymnastics`, `artistic_gymnastics`, `ice_sports`, `tennis`, `disabilities_*` |

### Inclus sous condition (contenu / lifestyle)

| Métier | Condition |
|--------|-----------|
| `blogger` | A garder si contenu sport/fitness/nutrition (vérifier le profil) |
| `influencer_global` | A garder si contenu sport/fitness/nutrition (vérifier le profil) |
| `youtuber` | A garder si contenu sport/fitness/nutrition (vérifier le profil) |
| `creator` | A garder si contenu sport/fitness/nutrition (vérifier le profil) |
| `model` | Garder (souvent crossover fitness/lifestyle, audience réceptive) |

### Sans métier renseigné ("-")

**A garder** et évaluer sur les critères complémentaires (followers, engagement, etc.).

---

## 3. Critères complémentaires

Après le tri par métier, appliquer ces critères sur les profils restants.

### Taux d'engagement (Instagram)

| Engagement | Verdict |
|-----------|---------|
| < 0.5% | Exclure (audience inactive ou achetée) |
| 0.5% - 1% | Basse priorité |
| 1% - 3% | Bon (sweet spot micro-influenceurs) |
| 3% - 5% | Très bon |
| > 5% | Excellent (vérifier que ce n'est pas artificiel si > 20%) |

### Taille de communauté Instagram

| Followers | Verdict |
|-----------|---------|
| < 1 000 | Exclure (trop petit) |
| 1k - 2k | Micro, basse priorité |
| 2k - 100k | Sweet spot ambassadeur dotation |
| 100k - 500k | Garder, potentiel paid a terme |
| > 500k | Trop gros pour du dotation pur, potentiel paid |

### Signaux d'alerte

| Signal | Action |
|--------|--------|
| Sponsor concurrent en bio (MyProtein, Bulk, Foodspring, etc.) | Exclure ou noter comme conflit |
| Compte privé | Exclure |
| Ratio following/followers > 2.0 | Suspect, a vérifier |
| Moins de 50 posts | Peu actif, basse priorité |

### Liste des marques concurrentes a surveiller
ta.energy, nutripure, cooknrun, mule bar, isostar, overstim, maurten, gu energy, science in sport, baouw, aptonia, myprotein, bulk, foodspring, prozis, eric favre, eafit, olimp, optimum nutrition

---

## 4. Process de tri

### Etape 1 : Tri automatique par métier
Appliquer les règles d'exclusion (section 1). Retirer tous les profils dont le métier est dans la liste d'exclusion.

### Etape 2 : Vérification des profils "sous condition"
Pour les `blogger`, `influencer_global`, `youtuber`, `creator` : vérifier manuellement si le contenu est sport/fitness.

### Etape 3 : Scoring des profils restants
Appliquer les critères complémentaires (section 3) : engagement, followers, signaux d'alerte.

### Etape 4 : Priorisation

| Priorité | Critères |
|----------|----------|
| **P1 - Go direct** | Métier sport/fitness + engagement > 1% + 5k-50k followers |
| **P2 - A contacter** | Métier sport/fitness + engagement > 0.5% + 2k-100k followers |
| **P3 - A vérifier** | Sans métier ou lifestyle + bon engagement, a checker le profil |
| **Exclu** | Métier hors cible OU engagement < 0.5% OU < 1k followers |

---

## 5. Colonnes utiles de l'export KolSquare

| Colonne | Usage |
|---------|-------|
| `Métier(s)` | Tri inclusion/exclusion |
| `Pseudo 1` (Instagram) | Username pour le DM |
| `Taille de communauté 1` | Nb followers Instagram |
| `Taux d'engagement 1` | Engagement rate Instagram |
| `E-mail kolsquare` | Contact direct si besoin |
| `Nom de l'agent` | Si agence, process différent (contrat payant) |

> **Note** : si le profil a un agent renseigné, c'est probablement un profil géré par une agence. Ces profils sont souvent dans la catégorie contrat payant, pas dotation. Signaler a Antoine.
