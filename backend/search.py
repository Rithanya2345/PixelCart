"""
Semantic search using FAISS + sentence-transformers.
Falls back to keyword matching if libraries are not installed.
"""

import numpy as np
import pickle
import os

INDEX_FILE = "faiss_index.pkl"

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    FAISS_AVAILABLE = True
    print("[Search] sentence-transformers + FAISS loaded [OK]")
except ImportError:
    FAISS_AVAILABLE = False
    print("[Search] FAISS not available — keyword fallback active.")


def _product_text(p: dict) -> str:
    """Combine product fields into a single searchable string."""
    parts = [
        p.get("title", ""),
        p.get("description", ""),
        p.get("type", ""),
        p.get("vendor", ""),
        " ".join(p.get("tags", [])),
    ]
    return " ".join(filter(None, parts)).lower()


def build_faiss_index(products: list):
    """Build and persist a FAISS flat L2 index from the product catalogue."""
    if not FAISS_AVAILABLE or not products:
        return

    texts = [_product_text(p) for p in products]
    embeddings = _model.encode(texts, show_progress_bar=False).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    with open(INDEX_FILE, "wb") as f:
        pickle.dump({"index": index, "count": len(products)}, f)

    print(f"[FAISS] Index built with {len(products)} products -> {INDEX_FILE}")


def _load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "rb") as f:
            return pickle.load(f)
    return None


def semantic_search(query: str, products: list, top_k: int = 10) -> list:
    """
    Search products by semantic similarity using FAISS.
    Falls back gracefully to keyword matching if FAISS is unavailable.
    """
    if not products:
        return []

    top_k = min(top_k, len(products))

    # ── FAISS path ──
    if FAISS_AVAILABLE:
        cached = _load_index()
        if cached is None:
            build_faiss_index(products)
            cached = _load_index()

        if cached and cached["count"] == len(products):
            q_vec = _model.encode([query]).astype("float32")
            distances, indices = cached["index"].search(q_vec, top_k)
            return [products[i] for i in indices[0] if i < len(products)]

    # ── Keyword fallback ──
    query_words = set(query.lower().split())
    scored = []
    for p in products:
        text = _product_text(p)
        score = sum(2 if w in p.get("title", "").lower() else 1
                    for w in query_words if w in text)
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_k]]
