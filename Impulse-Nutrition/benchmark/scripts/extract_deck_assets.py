"""
extract_deck_assets.py — One-shot d'extraction des assets visuels
depuis le deck de référence Havea pour alimenter le build_deck.py.

Lit `/Users/antoinechabrat/Downloads/W15 - Business Performance Impulse Nutrition.pptx`
(read-only unzip, pas de modification du .pptx source) et copie les
assets identifiés manuellement dans benchmark/deck/assets/ :

  - leaf_mint.png         (image22) — logo feuille mint Havea signature
  - logo_impulse.png      (image29) — logo IMPULSE NUTRITION
  - hero_1.jpeg           (image21) — photo hero grand format
  - hero_2.jpeg           (image13) — photo 16:9 secondaire
  - hero_3.jpeg           (image15) — photo 16:9 secondaire
  - theme_colors.json     palette Havea extraite de theme1.xml

Le script est idempotent : si un asset existe déjà, il est écrasé.
"""
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DECK = Path("/Users/antoinechabrat/Downloads/W15 - Business Performance Impulse Nutrition.pptx")
OUT = ROOT / "deck" / "assets"

# Mapping source (chemin dans le zip) → nom cible (dans OUT/)
ASSETS = {
    "ppt/media/image22.png": "leaf_mint.png",
    "ppt/media/image29.png": "logo_impulse.png",
    "ppt/media/image21.jpeg": "hero_1.jpeg",
    "ppt/media/image13.jpeg": "hero_2.jpeg",
    "ppt/media/image15.jpeg": "hero_3.jpeg",
}


def extract_theme_colors(zip_ref: zipfile.ZipFile) -> dict:
    """Parse ppt/theme/theme1.xml et retourne le dict des couleurs signature."""
    theme = zip_ref.read("ppt/theme/theme1.xml").decode("utf-8")
    colors = re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', theme)
    # On ne garde que les couleurs uniques dans l'ordre d'apparition
    seen = []
    for c in colors:
        if c.upper() not in seen:
            seen.append(c.upper())
    return {
        "raw_theme_colors": seen,
        "palette": {
            "mint_primary": "#279989",
            "teal_dark": "#014F4F",
            "teal_deep": "#005555",
            "green_very_dark": "#07331D",
            "teal_clear": "#009CA0",
            "blue_soft": "#3E6F92",
            "blue_light": "#67A7C0",
            "beige_gold": "#FED992",
            "salmon": "#F08276",
            "violet_muted": "#675982",
            "ink": "#0A0F1E",
            "black": "#000000",
            "white": "#FFFFFF",
        },
    }


def main() -> None:
    if not SOURCE_DECK.exists():
        raise SystemExit(f"Source deck not found: {SOURCE_DECK}")

    OUT.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(SOURCE_DECK, "r") as z:
        available = set(z.namelist())
        for src, dst in ASSETS.items():
            if src not in available:
                print(f"  [warn] missing in source: {src}")
                continue
            out_path = OUT / dst
            out_path.write_bytes(z.read(src))
            kb = out_path.stat().st_size // 1024
            print(f"  [ok] {src:30} → {dst:20} ({kb} KB)")

        # Theme colors
        theme = extract_theme_colors(z)
        theme_path = OUT / "theme_colors.json"
        theme_path.write_text(
            json.dumps(theme, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"  [ok] theme_colors.json extracted ({len(theme['raw_theme_colors'])} raw colors)")

    print(f"\nDone. Assets in: {OUT.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
