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
│  ├── /api/health                                              │
│  ├── /api/products                                            │
│  └── /api/session/{id} (DELETE)                               │
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
│  ├── fetch_products_public()    ──→ No-auth REST              │
│  ├── load_products()            ──→ Cache → mock fallback     │
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

**Input**: User message + last 4 conversation turns
**Output**: Structured JSON with 8 fields

```json
{
  "category": "Shoes",
  "budget_max": 1500,
  "budget_min": null,
  "occasion": null,
  "preferences": ["white", "casual"],
  "gender": "men",
  "recipient": "self",
  "keywords": ["sneakers", "white"]
}
```

**Implementation details**:
- System prompt instructs Claude to return ONLY valid JSON (no markdown fences, no explanation)
- Conversation history (last 4 turns) is injected for multi-turn context
- Output is post-processed: `json.loads()` with fence-stripping for robustness
- Failure fallback: returns a default dict with all `null` fields — the pipeline continues gracefully

**Why structured intent matters**: Downstream components (FAISS search, re-ranking, explanations) all consume this intent dict. Structured > freeform because it enables:
- Budget enforcement (hard filter, not suggestion)
- Explainability (intent pills in the UI)
- Follow-up generation (knows what's already been captured)

### 2.2 Semantic Search (`search.py`)

**Model**: `all-MiniLM-L6-v2` (384-dim embeddings, ~22MB)

**Index**: FAISS `IndexFlatL2` — brute-force L2 distance

**Product encoding**: Each product is represented as a concatenation of:
```
title + description + type + vendor + " ".join(tags)
```
All lowercased.

**Search flow**:
1. On startup (or Shopify connection), all products are encoded → FAISS index built → persisted to `faiss_index.pkl`
2. On query, the user message is encoded → FAISS returns top-K nearest neighbours
3. If FAISS is unavailable (missing dependencies), keyword fallback activates:
   - Tokenize query → score each product by word overlap (2x weight for title matches)
   - Sort by score descending → return top-K

**Why FAISS + sentence-transformers**:
- _"Gift for my mom"_ semantically matches products tagged `gift, women, birthday` even without shared keywords
- Local execution — no external search API dependency
- Sub-millisecond search over 250 products

### 2.3 LLM Re-Ranking (`agent.py::rank_products`)

**Problem**: FAISS returns the 10 most semantically similar products, but similarity ≠ relevance. A product can be semantically close but wrong for the user's specific intent (e.g., wrong budget, wrong gender).

**Solution**: Claude receives the 10 FAISS candidates + the user's structured intent + the raw query, and returns an ordered array of top-5 indices.

**Budget enforcement**: After Claude's ranking, products exceeding `budget_max` are filtered out. This is a hard filter in code, not left to the LLM's judgment.

**Failure mode**: If Claude's response fails to parse, return the first 5 FAISS candidates as-is.

### 2.4 Explanation Generation (`agent.py::generate_explanation`)

**Constraint**: Exactly ONE sentence, max 20 words, mentioning actual product details.

**Anti-patterns avoided**:
- No "Great choice!" or "Perfect for you!" filler
- No generic descriptions — must reference the specific product's attributes
- Must connect the product to the user's stated need

**Example output**: _"Lightweight EVA sole and mesh upper keep you cool during long runs."_

### 2.5 Follow-up Question (`agent.py::build_followup`)

**Constraint**: ONE question, max 14 words, conversational tone.

**Logic**: Claude sees what intent has already been captured and what products were shown, then asks about a dimension not yet explored (e.g., _"Do you prefer matte or glossy finish?"_).

### 2.6 Shopify Integration (`shopify_client.py`)

**Two paths**:

| Path | Auth | API | When used |
|---|---|---|---|
| **GraphQL** | Storefront Access Token | `POST /api/2024-01/graphql.json` | Token provided in env or request |
| **Public REST** | None | `GET /products.json` | No token, uses public storefront |

**Data normalisation**: Both paths produce the same product dict schema:
```python
{
    "id", "title", "description", "tags", "vendor", "type",
    "price", "currency", "image", "url", "in_stock"
}
```

**Caching**: Products are written to `product_cache.json` after every fetch. On subsequent startups, the cache is loaded directly (unless Shopify env vars trigger a fresh fetch).

**Mock fallback**: If no cache exists and Shopify is not configured, `MOCK_PRODUCTS` (25 curated items) is returned.

---

## 3. API Specification

### `POST /api/chat`

**Request**:
```json
{
  "session_id": "px_abc123",
  "message": "White sneakers under ₹1500"
}
```

**Response**:
```json
{
  "message": "Here are my top picks for you! 🛍️",
  "products": [
    {
      "id": "amz_1",
      "title": "Nike Court Vision Low Sneakers — White",
      "price": 3695.0,
      "currency": "INR",
      "image": "https://...",
      "url": "https://www.amazon.in/dp/...",
      "tags": ["sneakers", "white", "nike"],
      "in_stock": true,
      "explanation": "Classic white leather upper with lightweight foam midsole for all-day comfort."
    }
  ],
  "followup": "Do you prefer a specific brand or style?",
  "intent": {
    "category": "Shoes",
    "budget_max": 1500,
    "preferences": ["white"]
  },
  "session_id": "px_abc123"
}
```

### `POST /api/connect-shopify`

**Request**: `{ "shopify_url": "store.myshopify.com", "storefront_token": "" }`
**Response**: `{ "success": true, "products_cached": 10, "message": "..." }`

### `GET /api/health`

**Response**: `{ "status": "healthy", "sessions_active": 3, "products": 25 }`

### `GET /api/products`

**Response**: `{ "count": 25, "sample": ["Nike Court Vision..."], "categories": ["Shoes", "Clothing"] }`

### `DELETE /api/session/{session_id}`

**Response**: `{ "cleared": true }`

---

## 4. Session Management

- Sessions are stored in-memory (`dict`) on the backend
- Each session tracks: `history` (list of role/content pairs) and `context` (merged intent dict)
- Session ID is generated client-side (`px_` + random string)
- Sessions are cleared on "New chat" click (frontend calls `DELETE /api/session/{id}`)

**Limitation**: In-memory sessions are lost on server restart. Acceptable for a demo; would need Redis or a database in production.

---

## 5. Failure Handling

| Failure | Handling | Impact |
|---|---|---|
| **Anthropic API down** | `extract_intent` returns default nulls; `rank_products` returns FAISS top-5 as-is; `generate_explanation` returns generic fallback | Degraded but functional |
| **FAISS not installed** | Automatic keyword fallback in `search.py` | Lower search quality, still works |
| **Shopify unreachable** | Auto-fetch fails → falls back to cached products or mock data | Users see demo products |
| **Invalid JSON from Claude** | `_parse_json` strips markdown fences, catches `json.loads` errors | Falls back to defaults |
| **No products loaded** | `POST /api/chat` returns HTTP 503 with clear message | Frontend shows error |
| **Frontend can't reach backend** | Health check on launch; status indicator shows error message | User told to start backend |
| **Product image broken** | `onError` handler in `ProductCard` shows 🛍️ emoji placeholder | UI stays clean |

**Design principle**: Every external dependency (Claude, FAISS, Shopify) has a graceful fallback. The app always works — quality degrades, but it never crashes.

---

## 6. Performance Characteristics

| Operation | Typical Latency | Notes |
|---|---|---|
| Intent extraction | 800–1200ms | Single Claude API call |
| FAISS search | < 5ms | Local in-memory index |
| LLM re-ranking | 600–1000ms | Single Claude API call |
| Explanation generation (×5) | 2000–3500ms | 5 sequential Claude calls |
| Follow-up generation | 400–600ms | Single Claude API call |
| **Total end-to-end** | **2500–5000ms** | Dominated by Claude calls |
| Shopify product fetch | 1–3s | One-time, cached after |
| FAISS index build | 2–5s | One-time on startup |

**Optimisation opportunities** (not implemented in MVP):
1. Parallelise the 5 explanation calls (biggest win: ~2s → ~0.5s)
2. Cache intent for identical queries
3. Batch Claude calls where possible
4. Stream partial results to the frontend

---

## 7. Security Considerations

| Risk | Mitigation |
|---|---|
| API key exposure | `.env` files gitignored; `.env.example` ships with placeholders |
| CORS | Wildcard (`*`) in dev; should be restricted in production |
| Prompt injection | Claude system prompts are isolated per function; user input is quoted |
| Shopify token leakage | Token is optional; public REST API works without it |
| Session hijacking | Session IDs are client-generated random strings; no auth state |

---

## 8. Limitations

1. **Sequential LLM calls**: 4+ Claude calls per query add up. Parallelisation would cut latency by ~50%.
2. **In-memory sessions**: Lost on restart. No persistence layer.
3. **No streaming**: User waits for full response. Streaming would improve perceived performance.
4. **Small catalogue optimised**: FAISS `IndexFlatL2` is brute-force. Fine for ≤1000 products; would need `IndexIVFFlat` at scale.
5. **No user authentication**: Anyone with the URL can use it. Fine for demo.
6. **Single-model embeddings**: `all-MiniLM-L6-v2` is general-purpose. An e-commerce-tuned model would improve search quality.
7. **INR-only pricing**: Hardcoded currency formatting. Would need i18n for global use.
8. **No product image generation**: Uses Unsplash URLs for mock products. Real images come from Shopify.

---

## 9. Dependencies

### Backend (Python)

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥0.115 | HTTP framework |
| `uvicorn` | ≥0.29 | ASGI server |
| `anthropic` | ≥0.25 | Claude API client |
| `requests` | ≥2.31 | Shopify HTTP calls |
| `pydantic` | ≥2.9 | Request/response validation |
| `sentence-transformers` | ≥2.7 | Product embedding model |
| `faiss-cpu` | ≥1.12 | Vector similarity search |
| `numpy` | ≥1.26 | Numerical operations |
| `python-dotenv` | ≥1.0 | Environment variable loading |

### Frontend (Node.js)

| Package | Version | Purpose |
|---|---|---|
| `react` | ^18.2 | UI framework |
| `react-dom` | ^18.2 | DOM rendering |
| `axios` | ^1.6 | HTTP client |
| `vite` | ^5.2 | Build tool / dev server |
| `tailwindcss` | ^3.4 | Utility CSS |
| `@vitejs/plugin-react` | ^4.2 | Vite React support |

---

## 10. Deployment Notes

### Local development (current)

- Backend: `uvicorn main:app --reload --port 8000`
- Frontend: `npm run dev` → `localhost:5173`

### Production deployment path

1. **Backend**: Deploy to Render / Railway / Fly.io with `requirements.txt`
2. **Frontend**: `npm run build` → deploy `dist/` to Vercel / Netlify
3. **Environment**: Set `ANTHROPIC_API_KEY`, `SHOPIFY_STORE_URL`, `VITE_API_URL` (production backend URL)
4. **CORS**: Restrict `allow_origins` to the frontend domain
