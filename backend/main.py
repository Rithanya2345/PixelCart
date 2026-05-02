import os
from dotenv import load_dotenv
load_dotenv()  # Must be first — loads ANTHROPIC_API_KEY from .env

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from shopify_client import fetch_and_cache_products, load_products
from agent import extract_intent, rank_products, generate_explanation, build_followup
from search import semantic_search, build_faiss_index

sessions: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Pixelcart] Starting up...")

    # Auto-fetch from Shopify on startup if store URL is configured
    shop_url = os.getenv("SHOPIFY_STORE_URL", "")
    shop_token = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
    if shop_url and shop_url != "your-store.myshopify.com":
        try:
            print(f"[Shopify] Auto-fetching products from {shop_url}...")
            count = fetch_and_cache_products(shop_url, shop_token)
            print(f"[Shopify] {count} products fetched and cached [OK]")
        except Exception as e:
            print(f"[Shopify] Auto-fetch failed: {e} — falling back to mock/cache")

    prods = load_products()
    print(f"[Pixelcart] {len(prods)} products loaded. Building FAISS index...")
    build_faiss_index(prods)
    print("[Pixelcart] FAISS index ready [OK]")
    yield
    print("[Pixelcart] Shutdown.")

app = FastAPI(title="Pixelcart API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ShopifyConnectRequest(BaseModel):
    shopify_url: str
    storefront_token: str = ""  # optional — works without token via public REST API

@app.get("/")
def root():
    return {"status": "ok", "app": "Pixelcart AI Shopping Agent", "products_loaded": len(load_products())}

@app.get("/api/health")
def health():
    return {"status": "healthy", "sessions_active": len(sessions), "products": len(load_products())}

@app.post("/api/connect-shopify")
def connect_shopify(req: ShopifyConnectRequest):
    """Fetch from Shopify, cache locally, rebuild FAISS index."""
    try:
        token = req.storefront_token if req.storefront_token else os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
        count = fetch_and_cache_products(req.shopify_url, token)
        prods = load_products()
        build_faiss_index(prods)
        return {"success": True, "products_cached": count, "message": f"Loaded {count} products from Shopify [OK]"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Main AI Shopping Agent endpoint.
    intent extraction → FAISS search → LLM rank → explanations → follow-up
    """
    prods = load_products()
    if not prods:
        raise HTTPException(status_code=503, detail="No products loaded. POST /api/connect-shopify first.")

    if req.session_id not in sessions:
        sessions[req.session_id] = {"history": [], "context": {}}
    session = sessions[req.session_id]
    session["history"].append({"role": "user", "content": req.message})

    intent    = extract_intent(req.message, session["history"])
    session["context"].update(intent)

    candidates = semantic_search(req.message, prods, top_k=10)
    ranked     = rank_products(candidates, session["context"], req.message)

    results = []
    for p in ranked[:5]:
        expl = generate_explanation(p, req.message, session["context"])
        results.append({
            "id":          p.get("id"),
            "title":       p.get("title"),
            "price":       p.get("price"),
            "currency":    p.get("currency", "INR"),
            "image":       p.get("image", ""),
            "url":         p.get("url", "#"),
            "tags":        p.get("tags", []),
            "in_stock":    p.get("in_stock", True),
            "explanation": expl,
        })

    followup    = build_followup(session["context"], results)
    reply_text  = "Here are my top picks for you! 🛍️" if results else "No exact matches found — try rephrasing."
    session["history"].append({"role": "assistant", "content": reply_text})

    return {"message": reply_text, "products": results, "followup": followup,
            "intent": intent, "session_id": req.session_id}

@app.get("/api/products")
def list_products():
    """Return catalogue stats + sample titles (used by frontend badge)."""
    prods = load_products()
    return {
        "count": len(prods),
        "sample": [p["title"] for p in prods[:5]],
        "categories": list({p.get("type", "Other") for p in prods}),
    }

@app.delete("/api/session/{session_id}")
def clear_session(session_id: str):
    sessions.pop(session_id, None)
    return {"cleared": True}
