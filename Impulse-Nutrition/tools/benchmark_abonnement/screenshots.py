"""
Screenshots automatisés des pages abonnement — Benchmark Impulse Nutrition
Utilise Playwright pour capturer la zone abonnement de chaque marque.
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("assets/screenshots/benchmark")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BRANDS = [
    {
        "name": "nutriandco",
        "label": "Nutri&Co",
        "url": "https://nutriandco.com/fr/pages/page-abonnement",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "nutrimuscle",
        "label": "Nutrimuscle",
        "url": "https://www.nutrimuscle.com/pages/abonnement",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "novoma",
        "label": "Novoma",
        "url": "https://novoma.com/pages/abonnement",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "nutripure",
        "label": "Nutripure",
        "url": "https://www.nutripure.fr/fr/info/10-programme-de-fidelite",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "cuure",
        "label": "Cuure",
        "url": "https://cuure.com/about/abonnement",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "decathlon",
        "label": "Decathlon",
        "url": "https://abonnement.decathlon.fr/proteines-et-complements",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "aqeelab",
        "label": "Aqeelab",
        "url": "https://www.aqeelab-nutrition.fr/collections/abonnement",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
    {
        "name": "myprotein",
        "label": "MyProtein",
        "url": "https://fr.myprotein.com/c/subscribe/",
        "wait_for": "body",
        "scroll_to": None,
        "full_page": True,
    },
]


async def screenshot_brand(playwright, brand):
    """Prend un screenshot de la page abonnement d'une marque."""
    output_path = OUTPUT_DIR / f"{brand['name']}.png"

    browser = await playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    )
    context = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="fr-FR",
    )
    page = await context.new_page()

    try:
        print(f"  📸 {brand['label']} → {brand['url']}")
        await page.goto(brand["url"], wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)  # Let dynamic content load

        # Dismiss cookie banners if present
        for selector in [
            "button[id*='accept']",
            "button[class*='accept']",
            "button[class*='cookie']",
            "#tarteaucitronPersonalize",
            ".js-cookie-consent-agree",
            "[data-testid='cookie-accept']",
        ]:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(500)
                    break
            except Exception:
                pass

        await page.wait_for_timeout(1000)

        # Take screenshot
        await page.screenshot(
            path=str(output_path),
            full_page=brand.get("full_page", True),
            type="png",
        )
        print(f"  ✅ {brand['label']} → {output_path}")

    except Exception as e:
        print(f"  ❌ {brand['label']} erreur: {e}")
        # Take fallback screenshot anyway
        try:
            await page.screenshot(path=str(output_path), full_page=False, type="png")
            print(f"  ⚠️  {brand['label']} → screenshot partiel enregistré")
        except Exception:
            # Create a placeholder
            print(f"  ❌ {brand['label']} → impossible de prendre le screenshot")

    finally:
        await context.close()
        await browser.close()


async def main():
    print("🎬 Lancement des screenshots Playwright...\n")
    async with async_playwright() as playwright:
        for brand in BRANDS:
            await screenshot_brand(playwright, brand)
            await asyncio.sleep(1)  # Petit délai entre chaque

    print(f"\n✅ Screenshots terminés → {OUTPUT_DIR}")

    # Vérifier les fichiers créés
    for brand in BRANDS:
        path = OUTPUT_DIR / f"{brand['name']}.png"
        if path.exists():
            size = path.stat().st_size
            print(f"  {brand['label']}: {size:,} bytes")
        else:
            print(f"  {brand['label']}: MANQUANT")


if __name__ == "__main__":
    asyncio.run(main())
