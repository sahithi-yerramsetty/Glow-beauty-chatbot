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
    """Case-insensitive brand detection with word boundaries."""
    query_lower = query.lower().strip()
    if not query_lower:
        return None

    for alias, brand in BRAND_ALIASES.items():
        alias_lower = alias.lower()
        pattern = r"(?<![a-z0-9])" + re.escape(alias_lower) + r"(?![a-z0-9])"
        if re.search(pattern, query_lower):
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

def _normalize_term(term: str) -> str:
    term = term.lower().strip()
    if not term:
        return term
    if len(term) > 5 and term.endswith("ies"):
        return term[:-3] + "y"
    if len(term) > 3 and term.endswith("s") and not term.endswith("ss"):
        return term[:-1]
    return term


def search_products(query: str, product_type: str = None, k: int = 6):
    """Smart keyword search — case insensitive, cached, with budget range and relevance filtering."""
    products = load_products()

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    beauty_terms = {
        "skin", "skincare", "face", "serum", "serums", "moisturizer", "cleanser", "sunscreen",
        "spf", "hair", "shampoo", "conditioner", "frizz", "dandruff", "makeup", "foundation",
        "blush", "lipstick", "lip", "mascara", "eyeshadow", "concealer", "primer", "acne",
        "redness", "dark", "spots", "hydration", "dryness", "oily", "dry", "sensitive",
        "curly", "wavy", "coily", "scalp", "retinol", "niacinamide", "vitamin", "cream"
    }

    query_tokens = {
        _normalize_term(word)
        for word in re.findall(r"[a-z0-9']+", query_lower)
        if len(word) > 2
    }
    query_tokens -= {"what", "when", "where", "why", "how", "which", "that", "this", "with", "from", "under", "between", "any", "thing", "there", "today", "anything", "cheaper", "price", "budget", "products", "product"}

    if not (query_tokens & beauty_terms) and not normalize_brand(query_lower):
        return []

    min_price, max_price = detect_budget(query_lower)
    detected_brand = normalize_brand(query_lower)

    scored = []
    for p in products:
        if product_type and p.get("type") != product_type:
            continue

        price = p.get("price", 999)
        if max_price is not None and price > max_price:
            continue
        if min_price is not None and min_price > 0 and price < min_price:
            continue

        brand_lower = str(p.get("brand", "")).lower()
        name_lower = str(p.get("name", "")).lower()
        cat_lower = str(p.get("category", "")).lower()
        desc_lower = str(p.get("description", "")).lower()
        concerns_text = " ".join(p.get("concerns", [])).lower()
        ingredients_text = " ".join(p.get("ingredients", [])).lower()
        skin_hair = " ".join(p.get("skin_type", []) + p.get("hair_type", [])).lower()

        normalized_text = " ".join([
            brand_lower, name_lower, cat_lower, desc_lower, concerns_text, ingredients_text, skin_hair
        ])

        matched_words = []
        for word in query_tokens:
            normalized_word = word
            if normalized_word in normalized_text:
                matched_words.append(normalized_word)

        if not matched_words and not detected_brand:
            continue

        score = 0
        if detected_brand and detected_brand.lower() in brand_lower:
            score += 25

        if product_type and p.get("category", "").lower() == product_type:
            score += 10

        if "serum" in query_tokens and "serum" in cat_lower:
            score += 25
        if "serum" in query_tokens and "serum" in name_lower:
            score += 15
        if "moisturizer" in query_tokens and "moisturizer" in cat_lower:
            score += 20
        if "sunscreen" in query_tokens and "sunscreen" in cat_lower:
            score += 20

        for word in matched_words:
            if word in brand_lower:
                score += 12
            if word in name_lower:
                score += 10
            if word in cat_lower:
                score += 9
            if word in concerns_text:
                score += 5
            if word in ingredients_text:
                score += 5
            if word in skin_hair:
                score += 5
            if word in desc_lower:
                score += 2

        rating = float(p.get("rating", 0) or 0)
        score += max(0.0, (rating - 3.0)) * 1.5

        if score <= 0:
            continue

        scored.append((score, price, p))

    scored.sort(key=lambda x: (-x[0], x[1]))

    results = []
    for score, price, p in scored[:k]:
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
