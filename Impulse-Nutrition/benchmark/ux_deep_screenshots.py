import asyncio
from playwright.async_api import async_playwright
import os, json

OUT_DIR = "/Users/antoinechabrat/Documents/SmallProject/Impulse-Nutrition/assets/screenshots/benchmark/ux_deep"
os.makedirs(OUT_DIR, exist_ok=True)

# Pages to screenshot per brand: (brand_key, page_type, url)
PAGES = [
    # Nutri&Co
    ("nutriandco", "homepage", "https://nutriandco.com/fr/"),
    ("nutriandco", "product_sub", "https://nutriandco.com/fr/complement-alimentaire-omega-3.html"),
    ("nutriandco", "collection", "https://nutriandco.com/fr/nos-complements-alimentaires.html"),
    # Nutrimuscle
    ("nutrimuscle", "homepage", "https://www.nutrimuscle.com/"),
    ("nutrimuscle", "product_sub", "https://www.nutrimuscle.com/products/creatine-creapure-en-gelules"),
    ("nutrimuscle", "abonnement_page", "https://www.nutrimuscle.com/pages/abonnement"),
    # Novoma
    ("novoma", "homepage", "https://novoma.com/"),
    ("novoma", "product_sub", "https://novoma.com/products/magnesium-bisglycinate"),
    ("novoma", "abonnement_page", "https://novoma.com/pages/abonnement"),
    # Aqeelab
    ("aqeelab", "homepage", "https://www.aqeelab-nutrition.fr/"),
    ("aqeelab", "product_sub", "https://www.aqeelab-nutrition.fr/products/creatine-monohydrate-gelules"),
    ("aqeelab", "collection", "https://www.aqeelab-nutrition.fr/collections/all"),
    # Cuure
    ("cuure", "homepage", "https://cuure.com/"),
    ("cuure", "quiz", "https://cuure.com/quiz"),
    ("cuure", "produits", "https://cuure.com/mycuure/produits"),
    # MyProtein
    ("myprotein", "homepage", "https://fr.myprotein.com/"),
    ("myprotein", "product_sub", "https://fr.myprotein.com/sports-nutrition/creatine-monohydrate-en-poudre/10530743.html"),
    # Decathlon
    ("decathlon", "abo_homepage", "https://abonnement.decathlon.fr/"),
    ("decathlon", "abo_proteines", "https://abonnement.decathlon.fr/proteines-et-complements"),
    ("decathlon", "abo_faq", "https://abonnement.decathlon.fr/faq"),
    # Nutripure (no sub, but product page for comparison)
    ("nutripure", "homepage", "https://www.nutripure.fr/"),
    ("nutripure", "product", "https://www.nutripure.fr/fr/proteines/whey-isolate-native-174.html"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="fr-FR",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        results = []
        for brand, page_type, url in PAGES:
            fname = f"{brand}_{page_type}.png"
            fpath = os.path.join(OUT_DIR, fname)
            try:
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(3000)
                # Try to dismiss cookie banners
                for sel in ["button:has-text('Accepter')", "button:has-text('Accept')", "#onetrust-accept-btn-handler", ".cc-accept", "[data-testid='cookie-accept']"]:
                    try:
                        btn = page.locator(sel).first
                        if await btn.is_visible(timeout=1000):
                            await btn.click()
                            await page.wait_for_timeout(500)
                            break
                    except:
                        pass
                await page.screenshot(path=fpath, full_page=True, timeout=15000)
                size = os.path.getsize(fpath)
                results.append({"brand": brand, "type": page_type, "file": fname, "status": "ok", "size": size})
                print(f"✅ {fname} ({size:,} bytes)")
                await page.close()
            except Exception as e:
                results.append({"brand": brand, "type": page_type, "file": fname, "status": "error", "error": str(e)[:100]})
                print(f"❌ {fname}: {str(e)[:80]}")
                try:
                    await page.close()
                except:
                    pass
        
        await browser.close()
        
        # Write results manifest
        manifest_path = os.path.join(OUT_DIR, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(results, f, indent=2)
        
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"\n🎯 {ok}/{len(PAGES)} screenshots captured")

asyncio.run(main())
