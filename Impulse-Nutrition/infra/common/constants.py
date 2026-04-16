"""Shared domain constants used by qualification and filtering scripts.

Keeping these in infra/common/ ensures a single source of truth: when a new
competitor launches on the market, edit this file once and every script
that scores profiles picks up the update.
"""

from __future__ import annotations


# Competitor brands to detect in influencer bios / sponsor tags.
# Duplicates like "mule bar" + "mulebar" are intentional — matching is
# substring-based, so variations help catch different spellings.
COMPETITORS: list[str] = [
    "ta.energy", "ta energy", "nutripure", "cooknrun", "cook n run",
    "mule bar", "mulebar", "isostar", "overstim", "maurten", "gu energy",
    "science in sport", "sis", "baouw", "aptonia", "nduranz", "226ers",
    "namedsport", "named sport", "myprotein", "bulk", "foodspring",
    "prozis", "eric favre", "eafit", "olimp", "optimum nutrition",
]

# French sport-related keywords to detect in bios.
SPORT_KEYWORDS: list[str] = [
    "trail", "running", "course", "marathon", "triathlon", "hyrox",
    "crossfit", "cross fit", "musculation", "fitness", "cyclisme",
    "vélo", "natation", "ultra", "endurance", "sport", "athlète",
    "athlete", "coach", "entraîneur", "prépa physique", "strava",
]

# Nutrition-adjacent keywords (softer signal than sport).
NUTRITION_KEYWORDS: list[str] = [
    "nutrition", "diététique", "dieteticien", "santé", "bien-être",
    "healthy", "recette", "alimentation",
]
