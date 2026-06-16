import json
import os
import re
from langchain_core.documents import Document

PRODUCTS_PATH = "products.json"

BRAND_ALIASES = {
    "ordinary": "the ordinary",
    "the ordinary": "the ordinary",
    "cerave": "cerave",
    "cera ve": "cerave",
    "la roche": "la roche-posay",
    "laroche": "la roche-posay",
    "la roche posay": "la roche-posay",
    "lrp": "la roche-posay",
    "aveeno": "aveeno",
    "loreal": "l'oreal",
    "l'oreal": "l'oreal",
    "ouai": "ouai",
    "kerastase": "kerastase",
    "kérastase": "kerastase",
    "moroccanoil": "moroccanoil",
    "moroccan oil": "moroccanoil",
    "k18": "k18",
    "redken": "redken",
    "amika": "amika",
    "mielle": "mielle",
    "tresemme": "tresemme",
    "wow": "wow",
    "dove": "dove",
    "pantene": "pantene",
    "garnier": "garnier",
    "maybelline": "maybelline",
    "nyx": "nyx",
    "elf": "e.l.f.",
    "e.l.f": "e.l.f.",
    "wet n wild": "wet n wild",
    "milani": "milani",
    "revlon": "revlon",
    "physicians formula": "physicians formula",
    "cantu": "cantu",
    "batiste": "batiste",
    "head shoulders": "head & shoulders",
    "head and shoulders": "head & shoulders",
    "suave": "suave",
    "ogx": "ogx",
    "not your mothers": "not your mother's",
    "bare anatomy": "bare anatomy",
    "crown affair": "crown affair",
    "living proof": "living proof",
    "briogeo": "briogeo",
    "ghd": "ghd",
    "bare anatomy": "bare anatomy",
    "mielle": "mielle",
}

# ── Cache — load products ONCE into memory ──────────────────
_PRODUCTS_CACHE = None

def load_products(filepath=PRODUCTS_PATH):
    global _PRODUCTS_CACHE
    if _PRODUCTS_CACHE is None:
        with open(filepath, "r") as f:
            _PRODUCTS_CACHE = json.load(f)
    return _PRODUCTS_CACHE

def normalize_brand(query: str):
    """Case-insensitive brand detection."""
    query_lower = query.lower().strip()
    for alias, brand in BRAND_ALIASES.items():
        if alias in query_lower:
            return brand
    return None

def detect_budget(query: str):
    """Detect min and max budget from query."""
    query_lower = query.lower()

    # Range: between $X and $Y or $X-$Y or $X to $Y
    range_match = re.search(r'between\s*\$?(\d+)\s*(?:and|-|to)\s*\$?(\d+)', query_lower)
    if range_match:
        return float(range_match.group(1)), float(range_match.group(2))

    dash_match = re.search(r'\$(\d+)\s*-\s*\$?(\d+)', query_lower)
    if dash_match:
        return float(dash_match.group(1)), float(dash_match.group(2))

    # Under/below $X
    under_match = re.search(r'(?:under|below|less than|upto|up to)\s*\$?(\d+)', query_lower)
    if under_match:
        return 0, float(under_match.group(1))

    # Just a dollar amount
    dollar_match = re.search(r'\$(\d+)', query_lower)
    if dollar_match:
        return 0, float(dollar_match.group(1))

    return None, None

def search_products(query: str, product_type: str = None, k: int = 6):
    """Smart keyword search — case insensitive, cached, with budget range."""
    products = load_products()

    # Lowercase everything for comparison
    query_lower = query.lower().strip()
    query_words = set(query_lower.split())

    # Detect budget and brand
    min_price, max_price = detect_budget(query_lower)
    detected_brand = normalize_brand(query_lower)

    scored = []
    for p in products:
        # Filter by type
        if product_type and p.get("type") != product_type:
            continue

        price = p.get("price", 999)

        # Filter by budget
        if max_price is not None and price > max_price:
            continue
        if min_price is not None and min_price > 0 and price < min_price:
            continue

        score = 0

        # Lowercase ALL product fields for comparison
        brand_lower = p.get("brand", "").lower()
        name_lower = p.get("name", "").lower()
        cat_lower = p.get("category", "").lower()
        desc_lower = p.get("description", "").lower()
        concerns_text = " ".join(p.get("concerns", [])).lower()
        ingredients_text = " ".join(p.get("ingredients", [])).lower()
        skin_hair = " ".join(p.get("skin_type", p.get("hair_type", []))).lower()

        # Brand match — highest priority
        if detected_brand and detected_brand.lower() in brand_lower:
            score += 10

        # Category match
        if cat_lower in query_lower or query_lower in cat_lower:
            score += 5

        # Word matches
        for word in query_words:
            if len(word) > 2:
                if word in brand_lower:    score += 4
                if word in name_lower:     score += 3
                if word in cat_lower:      score += 3
                if word in concerns_text:  score += 2
                if word in ingredients_text: score += 2
                if word in skin_hair:      score += 2
                if word in desc_lower:     score += 1

        # Rating boost
        rating = p.get("rating", 3.0)
        score += (rating - 3.0) * 0.5

        if score > 0:
            scored.append((score, p))

    # Sort by relevance score
    scored.sort(key=lambda x: x[0], reverse=True)

    # If price range — also sort premium first within top results
    if min_price and min_price > 0:
        scored.sort(key=lambda x: x[1].get("price", 0), reverse=True)

    top = scored[:k]

    results = []
    for score, p in top:
        content = f"""Product: {p['name']}
Brand: {p['brand']}
Type: {p['type']}
Category: {p['category']}
Price: ${p['price']}
Concerns: {', '.join(p.get('concerns', []))}
Key ingredients: {', '.join(p.get('ingredients', []))}
Description: {p['description']}"""
        results.append(Document(page_content=content, metadata=p))

    return results
