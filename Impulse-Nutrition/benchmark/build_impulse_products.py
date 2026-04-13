#!/usr/bin/env python3
"""
T1: Merge COGS (from image) + Shopify retail prices + stock → impulse_products.json
"""
import json

# ── COGS 2026 (Prix de Cession) from user's image ──
COGS_2026 = {
    # Barres
    "VSBARC":   0.89,  "VSBARCC":  0.90,
    "VSBARLC":  3.81,  "VSBARLCC": 3.67,
    # BCAA
    "VSBCAAC":  5.58,  "VSBCAAP":  5.58,
    # Boisson effort
    "VSBOISM":  5.57,  "VSBOISF":  5.58,
    # Collagène Bovin (Peptides)
    "VSCOLBN":  6.94,  "VSCOLBC":  6.84,  "VSCOLBE": 6.87,
    # Collagène Marin
    "VSCOLMN": 10.03,  "VSCOLMC":  9.81,  "VSCOLME": 9.82,
    # Créatine
    "VSCREAC":  3.66,
    # Curcumine
    "VSCUR":    3.10,
    # Électrolytes poudre
    "VSELECP":  3.86,  "VSELECC":  3.46,
    # Électrolytes effervescents (pas dans image COGS, estimation ~1.50€)
    "VSELEFC":  1.50,  "VSELEFCV": 1.50,  "VSELEFP": 1.50,
    # Fer
    "VSFER":    1.60,
    # Glycine
    "VSGLY":    3.11,
    # L-Glutamine
    "VSLGLU":   4.59,
    # Magnésium
    "VSMAG":    3.16,
    # Maltodextrine
    "VSMAL":    3.56,
    # Multivitamines
    "VSMVIT":   1.22,
    # Omega 3
    "VSOME":    6.71,
    # Pré-Probiotiques
    "VSPBIOT":  3.13,
    # Preworkout
    "VSPREWC": 10.36,
    # Recovery (Whey Recovery)
    "VSRECMC": 12.05,  "VSRECMV": 12.05,
    # Shakers & accessoires
    "VSSHAK450": 2.00, "VSSHAK750": 2.60, "VSGOURDE": 2.55,
    # Sommeil
    "VSSOM":    1.37,
    # Spiruline
    "VSSPI":    1.54,
    # Vitamine C
    "VSVITC":   1.46,
    # Vitamine D3
    "VSVITD":   2.16,
    # Whey Isolate
    "VSWHEYN": 24.30,  "VSWHEYC": 24.46,  "VSWHEYV": 25.73,
    # Whey portions individuelles
    "VSWHEYCECH": 1.20, "VSWHEYVECH": 1.20,
    # Flask / Flyers (accessoires, pas pertinents pour abo)
    "VSFLASK500": 3.50,
}

# ── Shopify data (parsed from MCP output) ──
SHOPIFY_PRODUCTS = {
    "VSBARLCC": {"title": "Barre protéinée crispy choco-coco", "price": 10.90, "stock": 319, "category": "snack"},
    "VSBARLC":  {"title": "Barre protéinée crispy chocolat", "price": 10.90, "stock": 485, "category": "snack"},
    "VSBCAAC":  {"title": "BCAA 2.1.1 citron", "price": 22.90, "stock": 343, "category": "sport"},
    "VSBCAAP":  {"title": "BCAA 2.1.1 pêche", "price": 22.90, "stock": 772, "category": "sport"},
    "VSGOURDE": {"title": "Bidon 750ml", "price": 7.90, "stock": 384, "category": "accessoire"},
    "VSBOISF":  {"title": "Boisson effort fruits rouges", "price": 21.90, "stock": 387, "category": "sport"},
    "VSBOISM":  {"title": "Boisson effort menthe", "price": 21.90, "stock": 385, "category": "sport"},
    "VSCOLMN":  {"title": "Collagène marin Peptan® nature", "price": 32.90, "stock": 208, "category": "sante"},
    "VSCOLMC":  {"title": "Collagène marin Peptan® cacao", "price": 36.90, "stock": 338, "category": "sante"},
    "VSCOLME":  {"title": "Collagène marin Peptan® exotique", "price": 36.90, "stock": 416, "category": "sante"},
    "VSCREAC":  {"title": "Créatine Creapure®", "price": 12.90, "stock": 633, "category": "sport"},
    "VSCUR":    {"title": "Curcumine", "price": 19.90, "stock": 120, "category": "sante"},
    "VSELEFC":  {"title": "Électrolytes efferv. cerise", "price": 9.90, "stock": 556, "category": "sport"},
    "VSELEFCV": {"title": "Électrolytes efferv. citron", "price": 9.90, "stock": 558, "category": "sport"},
    "VSELEFP":  {"title": "Électrolytes efferv. pêche", "price": 9.90, "stock": 554, "category": "sport"},
    "VSELECC":  {"title": "Électrolytes poudre citron", "price": 15.90, "stock": 438, "category": "sport"},
    "VSELECP":  {"title": "Électrolytes poudre pêche", "price": 15.90, "stock": 738, "category": "sport"},
    "VSFER":    {"title": "Fer Bisglycinate", "price": 16.90, "stock": 72, "category": "sante"},
    "VSGLY":    {"title": "Glycine cristallisée", "price": 10.90, "stock": 149, "category": "sante"},
    "VSLGLU":   {"title": "L-Glutamine Kyowa®", "price": 13.90, "stock": 492, "category": "sport"},
    "VSMAG":    {"title": "Magnésium Bisglycinate", "price": 15.90, "stock": 532, "category": "sante"},
    "VSMAL":    {"title": "Maltodextrine", "price": 11.90, "stock": 238, "category": "sport"},
    "VSMVIT":   {"title": "Multivitamines", "price": 18.90, "stock": 650, "category": "sante"},
    "VSOME":    {"title": "Omega 3 EPAX®", "price": 23.90, "stock": 421, "category": "sante"},
    "VSCOLBN":  {"title": "Peptides collagène Peptan® nature", "price": 21.90, "stock": 470, "category": "sante"},
    "VSCOLBC":  {"title": "Peptides collagène Peptan® cacao", "price": 25.90, "stock": 491, "category": "sante"},
    "VSCOLBE":  {"title": "Peptides collagène Peptan® exotique", "price": 25.90, "stock": 340, "category": "sante"},
    "VSPBIOT":  {"title": "Pré-Probiotiques", "price": 22.90, "stock": 143, "category": "sante"},
    "VSPREWC":  {"title": "Preworkout citron", "price": 37.90, "stock": 336, "category": "sport"},
    "VSSHAK450":{"title": "Shaker 450ml", "price": 6.90, "stock": 601, "category": "accessoire"},
    "VSSHAK750":{"title": "Shaker 750ml", "price": 7.90, "stock": 374, "category": "accessoire"},
    "VSSOM":    {"title": "Sommeil +", "price": 18.90, "stock": 377, "category": "sante"},
    "VSSPI":    {"title": "Spiruline Biologique", "price": 12.90, "stock": 198, "category": "sante"},
    "VSVITC":   {"title": "Vitamine C", "price": 12.90, "stock": 570, "category": "sante"},
    "VSVITD":   {"title": "Vitamine D3", "price": 15.90, "stock": 137, "category": "sante"},
    "VSWHEYN":  {"title": "Whey Isolate nature", "price": 37.90, "stock": 204, "category": "sport"},
    "VSWHEYC":  {"title": "Whey Isolate chocolat", "price": 39.90, "stock": 389, "category": "sport"},
    "VSWHEYV":  {"title": "Whey Isolate vanille", "price": 39.90, "stock": 435, "category": "sport"},
    "VSWHEYCECH":{"title": "Whey Isolate chocolat - portion", "price": 2.95, "stock": 726, "category": "sport"},
    "VSWHEYVECH":{"title": "Whey Isolate vanille - portion", "price": 2.95, "stock": 823, "category": "sport"},
    "VSRECMC":  {"title": "Whey Recovery chocolat", "price": 39.90, "stock": 178, "category": "sport"},
    "VSRECMV":  {"title": "Whey Recovery vanille", "price": 39.90, "stock": 300, "category": "sport"},
    "VSFLASK500":{"title": "Flasque 500ml", "price": 19.90, "stock": 1628, "category": "accessoire"},
}

# ── Consumption pattern & recurrence scoring ──
RECURRENCE = {
    # Daily supplements → highest recurrence
    "VSCREAC": 95,   # créatine = daily, 1 pot ~1 mois
    "VSMVIT": 95,     # multivit = daily
    "VSOME": 95,      # omega 3 = daily
    "VSMAG": 95,      # magnésium = daily
    "VSFER": 90,      # fer = daily (+ niche)
    "VSVITC": 90,     # vit C = daily
    "VSVITD": 90,     # vit D = daily
    "VSSOM": 85,      # sommeil = daily
    "VSSPI": 85,      # spiruline = daily
    "VSCUR": 85,      # curcumine = daily
    "VSPBIOT": 85,    # probiotiques = daily
    "VSGLY": 80,      # glycine = daily
    # Sport regular use
    "VSBCAAC": 75, "VSBCAAP": 75,    # BCAA = per workout, 3-5x/week
    "VSLGLU": 75,     # glutamine = per workout
    "VSELECC": 75, "VSELECP": 75,    # electrolytes = per workout
    "VSELEFC": 70, "VSELEFCV": 70, "VSELEFP": 70,  # efferv = per workout
    "VSBOISM": 70, "VSBOISF": 70,    # boisson effort = per workout
    "VSMAL": 65,      # maltodextrine = per workout
    "VSPREWC": 70,    # preworkout = per workout
    # Whey / Recovery = daily for builders
    "VSWHEYN": 80, "VSWHEYC": 80, "VSWHEYV": 80,
    "VSRECMC": 75, "VSRECMV": 75,
    # Collagène = daily
    "VSCOLMN": 85, "VSCOLMC": 85, "VSCOLME": 85,
    "VSCOLBN": 85, "VSCOLBC": 85, "VSCOLBE": 85,
    # Snacks = very irregular, impulse buy
    "VSBARLC": 30, "VSBARLCC": 30,
    # Portions individuelles = samples, not recurring
    "VSWHEYCECH": 10, "VSWHEYVECH": 10,
    # Accessories = one-time purchase
    "VSSHAK450": 0, "VSSHAK750": 0, "VSGOURDE": 0, "VSFLASK500": 0,
}

# ── SKU complexity (nb variants for same product line) ──
SKU_COMPLEXITY = {
    "VSCREAC": 1,     # 1 goût
    "VSMVIT": 1,      # 1 format
    "VSOME": 1,       # 1 format
    "VSMAG": 1,
    "VSFER": 1,
    "VSVITC": 1,
    "VSVITD": 1,
    "VSSOM": 1,
    "VSSPI": 1,
    "VSCUR": 1,
    "VSPBIOT": 1,
    "VSGLY": 1,
    "VSLGLU": 1,
    "VSMAL": 1,
    "VSPREWC": 1,     # 1 goût actuellement
    "VSBCAAC": 2, "VSBCAAP": 2,     # 2 goûts
    "VSELECC": 2, "VSELECP": 2,
    "VSELEFC": 3, "VSELEFCV": 3, "VSELEFP": 3,  # 3 goûts
    "VSBOISM": 2, "VSBOISF": 2,
    "VSWHEYN": 3, "VSWHEYC": 3, "VSWHEYV": 3,   # 3 goûts
    "VSRECMC": 2, "VSRECMV": 2,
    "VSCOLMN": 3, "VSCOLMC": 3, "VSCOLME": 3,
    "VSCOLBN": 3, "VSCOLBC": 3, "VSCOLBE": 3,
    "VSBARLC": 2, "VSBARLCC": 2,
    "VSWHEYCECH": 2, "VSWHEYVECH": 2,
    "VSSHAK450": 1, "VSSHAK750": 1, "VSGOURDE": 1, "VSFLASK500": 1,
}

# ── Competitor presence in subscription (from master_data.json analysis) ──
# Which product categories are offered as subscription by competitors
COMPETITOR_SUB = {
    "creatine": True,   # Nutrimuscle, MyProtein, Aqeelab
    "whey": True,       # Nutrimuscle, MyProtein, Aqeelab
    "bcaa": True,       # Nutrimuscle, MyProtein
    "multivitamines": True,  # Nutri&Co, Novoma, Cuure
    "omega3": True,     # Nutri&Co, Novoma, Cuure
    "magnesium": True,  # Nutri&Co, Novoma, Cuure
    "fer": True,        # Novoma, Cuure
    "vitc": True,       # Novoma, Cuure
    "vitd": True,       # Novoma, Cuure
    "collagene": True,  # Nutri&Co, Nutrimuscle
    "probiotiques": True,  # Nutri&Co, Novoma, Cuure
    "spiruline": True,  # Novoma
    "curcumine": True,  # Nutri&Co, Novoma
    "sommeil": True,    # Novoma
    "glycine": False,   # niche
    "glutamine": True,  # Nutrimuscle, MyProtein
    "electrolytes": True, # MyProtein
    "boisson_effort": False,  # rare en abo
    "maltodextrine": True,    # MyProtein, Nutrimuscle
    "preworkout": True,       # MyProtein, Aqeelab
    "recovery": True,         # MyProtein
    "barre": False,           # pas en abo
    "accessoire": False,
}

SKU_TO_CATEGORY = {
    "VSCREAC": "creatine",
    "VSMVIT": "multivitamines",
    "VSOME": "omega3",
    "VSMAG": "magnesium",
    "VSFER": "fer",
    "VSVITC": "vitc",
    "VSVITD": "vitd",
    "VSSOM": "sommeil",
    "VSSPI": "spiruline",
    "VSCUR": "curcumine",
    "VSPBIOT": "probiotiques",
    "VSGLY": "glycine",
    "VSLGLU": "glutamine",
    "VSMAL": "maltodextrine",
    "VSPREWC": "preworkout",
    "VSBCAAC": "bcaa", "VSBCAAP": "bcaa",
    "VSELECC": "electrolytes", "VSELECP": "electrolytes",
    "VSELEFC": "electrolytes", "VSELEFCV": "electrolytes", "VSELEFP": "electrolytes",
    "VSBOISM": "boisson_effort", "VSBOISF": "boisson_effort",
    "VSWHEYN": "whey", "VSWHEYC": "whey", "VSWHEYV": "whey",
    "VSRECMC": "recovery", "VSRECMV": "recovery",
    "VSCOLMN": "collagene", "VSCOLMC": "collagene", "VSCOLME": "collagene",
    "VSCOLBN": "collagene", "VSCOLBC": "collagene", "VSCOLBE": "collagene",
    "VSBARLC": "barre", "VSBARLCC": "barre",
    "VSWHEYCECH": "whey", "VSWHEYVECH": "whey",
    "VSSHAK450": "accessoire", "VSSHAK750": "accessoire",
    "VSGOURDE": "accessoire", "VSFLASK500": "accessoire",
}

# Duration (days) of one unit
CONSUMPTION_DAYS = {
    "VSCREAC": 30,    # 300g / 5g/day = 60 mais souvent 3g → ~100 days, mais 30 jours pour un pot petit
    "VSMVIT": 30,     # 60 gélules / 2/jour
    "VSOME": 30,      # 60 capsules / 2/jour
    "VSMAG": 30,      # 60 gélules / 2/jour
    "VSFER": 30,
    "VSVITC": 30,
    "VSVITD": 60,     # 120 gélules / 2/jour
    "VSSOM": 30,      # 60 gélules / 2/jour
    "VSSPI": 30,      # 60 gélules / 2/jour
    "VSCUR": 30,
    "VSPBIOT": 30,
    "VSGLY": 30,      # 300g / ~5g/day
    "VSLGLU": 30,     # 300g / 5g/day
    "VSMAL": 20,      # 500g, ~25g/use, ~20 uses
    "VSPREWC": 20,    # 300g / ~15g/dose
    "VSBCAAC": 30, "VSBCAAP": 30,
    "VSELECC": 20, "VSELECP": 20,  # ~20 doses
    "VSELEFC": 20, "VSELEFCV": 20, "VSELEFP": 20,
    "VSBOISM": 20, "VSBOISF": 20,
    "VSWHEYN": 20, "VSWHEYC": 20, "VSWHEYV": 20,  # 750g / ~30g = 25 doses
    "VSRECMC": 15, "VSRECMV": 15,  # 750g / 50g = 15 doses
    "VSCOLMN": 30, "VSCOLMC": 30, "VSCOLME": 30,
    "VSCOLBN": 30, "VSCOLBC": 30, "VSCOLBE": 30,
    "VSBARLC": 1, "VSBARLCC": 1,    # single serve
    "VSWHEYCECH": 1, "VSWHEYVECH": 1,
    "VSSHAK450": 730, "VSSHAK750": 730, "VSGOURDE": 730, "VSFLASK500": 730,
}

def build_products():
    products = []
    for sku, shop in SHOPIFY_PRODUCTS.items():
        cogs = COGS_2026.get(sku)
        if cogs is None:
            continue
        
        price = shop["price"]
        margin = round(price - cogs, 2)
        margin_pct = round((margin / price) * 100, 1) if price > 0 else 0
        cat_key = SKU_TO_CATEGORY.get(sku, "autre")
        
        product = {
            "sku": sku,
            "title": shop["title"],
            "retail_price": price,
            "cogs_2026": cogs,
            "gross_margin": margin,
            "gross_margin_pct": margin_pct,
            "stock": shop["stock"],
            "category": shop["category"],
            "product_category": cat_key,
            "recurrence_score": RECURRENCE.get(sku, 0),
            "sku_variants": SKU_COMPLEXITY.get(sku, 1),
            "competitor_has_sub": COMPETITOR_SUB.get(cat_key, False),
            "consumption_days": CONSUMPTION_DAYS.get(sku, 30),
            # Profitability by scenario (computed in T2)
            "scenarios": {}
        }
        products.append(product)
    
    # Sort by gross margin % descending
    products.sort(key=lambda p: p["gross_margin_pct"], reverse=True)
    return products

if __name__ == "__main__":
    products = build_products()
    
    output = {
        "meta": {
            "source_cogs": "Image Prix de Cession 2026 (fournie par Antoine)",
            "source_retail": "Shopify MCP API - impulse-nutrition.fr",
            "logistics_costs": {
                "point_relais": 3.90,
                "domicile": 5.90,
                "express": 10.90
            },
            "total_products": len(products),
            "excluded": ["Packs", "Duos", "Choose packs", "Flyers", "The Bradery packs", "TTS packs", "LRA packs"],
            "note_electrolytes_efferv": "COGS effervescents estimé à 1.50€ (absent de l'image, produit récent)"
        },
        "products": products
    }
    
    with open("benchmark/impulse_products.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(products)} products merged → benchmark/impulse_products.json")
    print(f"\nTop 10 margins:")
    for p in products[:10]:
        print(f"  {p['sku']:<15} {p['title'][:35]:<35} {p['retail_price']:>6.2f}€ - {p['cogs_2026']:>5.2f}€ = {p['gross_margin']:>5.2f}€ ({p['gross_margin_pct']}%)")
    print(f"\nBottom 5 margins:")
    for p in products[-5:]:
        print(f"  {p['sku']:<15} {p['title'][:35]:<35} {p['retail_price']:>6.2f}€ - {p['cogs_2026']:>5.2f}€ = {p['gross_margin']:>5.2f}€ ({p['gross_margin_pct']}%)")
