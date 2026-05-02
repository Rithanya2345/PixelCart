# Pixelcart — Technical Document

> Architecture, implementation decisions, failure handling, and limitations.

---

## 1. System Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                          │
│  React 18 · Vite 5 · Tailwind CSS 3 · Axios                 │
│                                                               │
│  SetupScreen ──→ App (Chat UI) ──→ ChatMessage               │
│       │                                    │                  │
│       │ POST /api/connect-shopify          │ POST /api/chat   │
│       ▼                                    ▼                  │
└───────────────────────┬───────────────────────────────────────┘
                        │ HTTP / JSON
┌───────────────────────▼───────────────────────────────────────┐
│                  BACKEND (FastAPI · Python)                    │
│                                                               │
│  main.py                                                      │
│  ├── lifespan() ────→ Auto-fetch Shopify on startup           │
│  ├── /api/chat ─────→ agent.py + search.py                    │
│  ├── /api/connect-shopify ──→ shopify_client.py               │
│                                                               │
│  agent.py (Claude AI)                                         │
│  ├── extract_intent()  ──→ Structured JSON intent             │
│  ├── rank_products()   ──→ Re-rank by intent fit              │
│  ├── generate_explanation() ──→ Per-product sentence           │
│  └── build_followup()  ──→ Refinement question                │
│                                                               │
│  search.py (FAISS)                                            │
│  ├── build_faiss_index() ──→ Encode + index products          │
│  └── semantic_search()   ──→ Query → top-K neighbours         │
│                                                               │
│  shopify_client.py                                            │
│  ├── fetch_and_cache_products() ──→ GQL or REST               │
│  └── MOCK_PRODUCTS (25 items)   ──→ Built-in catalogue        │
│                                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │ Anthropic │  │  FAISS   │  │   Shopify    │
    │ Claude    │  │  Index   │  │  Storefront  │
    │ API       │  │ (local)  │  │  API         │
    └──────────┘  └──────────┘  └──────────────┘
```

---

## 2. Component Deep-Dives

### 2.1 Intent Extraction (`agent.py::extract_intent`)
**Output**: Structured JSON with 8 fields (category, budget_max, preferences, gender, recipient, etc).
**Implementation**: System prompt instructs Claude to return ONLY valid JSON. Output is post-processed and provides the foundation for budget enforcement and search.

### 2.2 Semantic Search (`search.py`)
**Model**: `all-MiniLM-L6-v2` (384-dim embeddings, ~22MB)
**Index**: FAISS `IndexFlatL2` — brute-force L2 distance
**Fallback**: If FAISS is unavailable, gracefully falls back to keyword matching (title-weighted).

### 2.3 LLM Re-Ranking (`agent.py::rank_products`)
**Problem**: FAISS returns semantically similar items, but similarity ≠ relevance. 
**Solution**: Claude re-ranks the top 10 FAISS candidates against the user's specific intent. Products exceeding `budget_max` are filtered out entirely in Python code.

### 2.4 Explanation Generation
Each product receives a 1-sentence, max 20-word explanation detailing exactly why it matches the user's intent.

### 2.5 Shopify Integration
Two paths supported:
- **GraphQL**: Requires Storefront Access Token.
- **Public REST**: Requires no auth, works out-of-the-box for many stores.

---

## 3. Failure Handling

| Failure | Handling | Impact |
|---|---|---|
| **Anthropic API down** | `extract_intent` returns default nulls; `rank_products` returns FAISS top-5 | Degraded but functional |
| **FAISS not installed** | Automatic keyword fallback in `search.py` | Lower search quality |
| **Shopify unreachable** | Auto-fetch fails → falls back to cached products or mock data | Users see demo products |
| **Invalid JSON from Claude** | `_parse_json` strips markdown fences, catches errors | Falls back to defaults |

---

## 4. Performance & Limitations

**End-to-end latency**: 2500–5000ms. Dominated by sequential Claude API calls.
**Limitations**: 
- In-memory sessions (lost on restart)
- No streaming responses
- Uses generic embedding model rather than e-commerce-tuned model
