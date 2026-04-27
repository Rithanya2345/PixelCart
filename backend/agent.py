"""
Claude-powered agent for:
  1. Intent extraction (structured JSON)
  2. Product re-ranking
  3. Per-product personalised explanation
  4. Follow-up question generation
"""

import os
import json
import anthropic

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
MODEL = "claude-sonnet-4-20250514"


def _call(system: str, user: str, max_tokens: int = 500) -> str:
    response = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def _parse_json(raw: str) -> dict | list:
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ─────────────────────────────────────────────
# 1. INTENT EXTRACTION
# ─────────────────────────────────────────────
def extract_intent(message: str, history: list) -> dict:
    """
    Parse the user's shopping query into structured intent.
    Returns a dict with category, budget, occasion, preferences, etc.
    """
    system = """You are a shopping intent parser for an Indian e-commerce store.
Extract structured intent from the user's query and return ONLY valid JSON:

{
  "category": null,
  "budget_max": null,
  "budget_min": null,
  "occasion": null,
  "preferences": [],
  "gender": null,
  "recipient": null,
  "keywords": []
}

Rules:
- budget values must be INR numbers (not strings)
- null for any field not mentioned
- preferences: list of product attributes like ["white", "lightweight", "leather"]
- recipient: who it's for — "mom", "dad", "friend", "partner", "self"
- Return ONLY the JSON object. No explanation, no markdown.
"""
    recent = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in history[-4:]
    )
    user = f"Conversation:\n{recent}\n\nLatest message: \"{message}\""

    try:
        raw = _call(system, user, max_tokens=300)
        return _parse_json(raw)
    except Exception as e:
        print(f"[Intent] Parse failed: {e}")
        return {
            "category": None, "budget_max": None, "budget_min": None,
            "occasion": None, "preferences": [], "gender": None,
            "recipient": None, "keywords": [],
        }


# ─────────────────────────────────────────────
# 2. PRODUCT RE-RANKING
# ─────────────────────────────────────────────
def rank_products(candidates: list, intent: dict, query: str) -> list:
    """
    Use Claude to re-rank FAISS candidates by relevance to the user's intent.
    Returns top-5 most relevant products.
    """
    if not candidates:
        return []

    product_list = "\n".join(
        f"{i}. \"{p['title']}\" | ₹{p['price']} | "
        f"Type:{p.get('type','')} | Tags:{','.join((p.get('tags') or [])[:5])}"
        for i, p in enumerate(candidates)
    )

    system = """You are a product ranking engine for an e-commerce AI agent.
Given a user's query and intent, return the indices of the top 5 most relevant products.
Return ONLY a JSON array of integer indices. Example: [2, 0, 4, 1, 3]
No explanation, no markdown, just the array."""

    user = f"""User query: "{query}"
Intent: {json.dumps(intent)}
Budget max: {intent.get("budget_max", "not specified")}

Products:
{product_list}

Return top 5 indices:"""

    try:
        raw = _call(system, user, max_tokens=100)
        indices = _parse_json(raw)

        budget = intent.get("budget_max")
        result = []
        for i in indices:
            if isinstance(i, int) and i < len(candidates):
                p = candidates[i]
                if budget is None or float(p.get("price", 0)) <= float(budget):
                    result.append(p)

        return result[:5] if result else candidates[:5]
    except Exception as e:
        print(f"[Rank] Failed: {e}")
        return candidates[:5]


# ─────────────────────────────────────────────
# 3. PER-PRODUCT EXPLANATION
# ─────────────────────────────────────────────
def generate_explanation(product: dict, query: str, intent: dict) -> str:
    """
    Generate a personalised 1-sentence explanation for why this product suits the user.
    """
    system = """You are Pixelcart, a warm and friendly AI shopping assistant.
Write exactly ONE sentence (max 20 words) explaining why this specific product suits the user's need.
Be specific — mention actual product details. Avoid filler phrases like "great choice" or "perfect for you"."""

    user = f"""Product: {product["title"]} at ₹{product["price"]}
Description: {product.get("description", "")[:150]}
Tags: {", ".join((product.get("tags") or [])[:5])}

User searched for: "{query}"
Their intent: {json.dumps(intent)}

Write the explanation sentence:"""

    try:
        return _call(system, user, max_tokens=80)
    except Exception as e:
        print(f"[Explain] Failed: {e}")
        return f"Matches your search for {query}."


# ─────────────────────────────────────────────
# 4. FOLLOW-UP QUESTION
# ─────────────────────────────────────────────
def build_followup(intent: dict, results: list) -> str:
    """
    Generate a smart follow-up question to help refine the user's search.
    """
    system = """You are Pixelcart, a friendly shopping assistant.
Ask ONE smart follow-up question (max 14 words) to help refine the user's product choice.
Be natural and conversational. Do not repeat intent already captured."""

    shown = [r["title"] for r in results]
    user = f"Captured intent: {json.dumps(intent)}\nProducts shown: {shown}"

    try:
        return _call(system, user, max_tokens=60)
    except Exception:
        return "Would you like me to narrow down these results further?"
