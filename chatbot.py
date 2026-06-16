from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from vector_store import search_products
import os

BEAUTY_SYSTEM_PROMPT = """You are GlowBot, a warm, expert beauty advisor with deep knowledge in skincare, haircare, and makeup.

Your personality:
- Friendly, encouraging, never judgmental
- Ask ONE question at a time
- Give specific, actionable advice

Your job is to:
1. First understand the user's FOCUS: skin, hair, makeup or combination
2. Collect their profile step by step:
   - Skin type (oily / dry / combination / sensitive / normal) — if skincare
   - Hair type (straight / wavy / curly / coily) — if haircare
   - Main concern (acne, dark spots, frizz, dandruff, hair loss, etc.)
   - Budget range (under $10 / under $20 / $20-$50 / $50-$100 / no limit)
3. Once you have enough info, provide recommendations

RESPONSE FORMATTING RULES — FOLLOW STRICTLY:
- Always use short sentences. Never write long run-on sentences.
- Never use $ symbol inside bold text like **$price** — write price separately
- Always put each product on its own numbered line
- Format each product exactly like this:
  1. **Product Name** — $price — one sentence about why it's good
- After listing products, add a blank line before any follow-up text
- Keep all text inside the chat box — no very long lines

PRODUCT SUGGESTION ORDER:
- When user asks for a price RANGE (e.g. $20-$30): show premium/best-rated first, then mid-range
- When user asks "under $X": show best value first
- When no budget: show best rated first, then mention budget options exist
- ALWAYS suggest at least 3 products if available in database

Important rules:
- ONLY recommend products from the PRODUCT DATABASE given to you below
- NEVER invent products not in the database
- If NO products match budget, say EXACTLY:
  "I don't currently have [category] products in that price range.
  The closest options I have start from $[X]. Would you like those instead?"
- NEVER say "our database is limited"
- Remember everything the user tells you — never ask again
- If user asks anything NOT beauty related, say: "I'm only trained for beauty advice! Ask me about your skin, hair or makeup instead 🌸"
- For medical conditions, recommend seeing a dermatologist"""

def detect_focus(history: list, message: str) -> str:
    all_text = message.lower()
    for h in history:
        all_text += " " + h["content"].lower()

    hair_words = ["hair", "scalp", "frizz", "dandruff", "shampoo", "curly", "wavy", "coily", "hair loss", "conditioner", "dry shampoo"]
    skin_words = ["skin", "face", "acne", "pores", "moisturizer", "serum", "cleanser", "dark spots", "oily skin", "dry skin", "sunscreen", "spf"]
    makeup_words = ["blush", "foundation", "concealer", "mascara", "lipstick", "eyeshadow", "bronzer", "highlighter", "makeup", "powder", "lip gloss", "eyeliner", "primer", "brow"]

    is_hair = any(w in all_text for w in hair_words)
    is_skin = any(w in all_text for w in skin_words)
    is_makeup = any(w in all_text for w in makeup_words)

    if is_makeup and not is_hair and not is_skin:
        return "makeup"
    elif is_hair and not is_skin and not is_makeup:
        return "haircare"
    elif is_skin and not is_hair and not is_makeup:
        return "skincare"
    return None

def create_beauty_chatbot(api_key: str):
    os.environ["GROQ_API_KEY"] = api_key
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1500
    )

def chat(llm, message: str, history: list) -> str:
    product_type = detect_focus(history, message)
    results = search_products(query=message, product_type=product_type, k=6)

    if results:
        label = f"({product_type.upper()})" if product_type else "(ALL)"
        product_context = f"\n\n📦 PRODUCT DATABASE {label} — ONLY recommend from these:\n"
        product_context += "=" * 40 + "\n"
        for i, doc in enumerate(results, 1):
            product_context += f"\n{i}. {doc.page_content}\n"
        product_context += "=" * 40
    else:
        product_context = "\n\n📦 PRODUCT DATABASE: No products found matching this query and budget. Tell the user clearly and specifically what IS available."

    messages = [SystemMessage(content=BEAUTY_SYSTEM_PROMPT + product_context)]
    for h in history:
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        elif h["role"] == "assistant":
            messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)
    return response.content

def get_greeting() -> str:
    return """✨ Hi! I'm **GlowBot**, your personal beauty advisor.

I'm here to help you with:
- 🧴 **Skincare** — routines, products, ingredient advice
- 💇 **Haircare** — treatments, styling, scalp health
- 💄 **Makeup** — foundation, blush, lipstick, eyeshadow
- 💰 **Budget-friendly picks** — from $3 drugstore to luxury

Tell me — what are you looking to work on today?"""
