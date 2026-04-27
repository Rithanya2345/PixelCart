# 🛍️ Pixelcart — AI Shopping Agent
### Kasparro Agentic Commerce Hackathon | Track 01: Discovery
**Team:** Pixelcart | **Members:** Sangathiyabhashini S D, Rithanya C

---

## 🎯 Problem
Modern e-commerce is broken. Users face overwhelming choices, complex filter systems, and zero personalisation.
> "I need a gift for my mom under ₹500" — no filter handles this. A conversation can.

**Pixelcart** replaces browse → filter → search with a single natural language conversation.

---

## 🏗️ Architecture

```
User Query
    ↓
React + Tailwind CSS (Frontend)
    ↓ HTTP (axios)
FastAPI Backend (Python)
    ↓
┌──────────────────────────────────────────┐
│  Claude Sonnet (Anthropic API)           │
│  1. Intent extraction  → structured JSON │
│  2. Product re-ranking → top 5 indices   │
│  3. Explanation per product              │
│  4. Follow-up question                   │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  FAISS + sentence-transformers           │
│  all-MiniLM-L6-v2 embeddings             │
│  Flat L2 index · keyword fallback        │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  Shopify Storefront API (GraphQL)        │
│  → Fetches up to 250 products            │
│  → Cached locally as product_cache.json  │
│  → Mock data fallback built-in           │
└──────────────────────────────────────────┘
    ↓
Top 3–5 ranked products + explanations + follow-up
```

---

## 🔄 End User Flow

```
1. User: "I need white casual sneakers under ₹1500"
2. Claude extracts: { category:"shoes", budget_max:1500, preferences:["white","casual"] }
3. FAISS finds top 10 semantic matches from catalogue
4. Claude re-ranks to top 5 by relevance to intent
5. Claude writes 1-sentence personalised explanation per product
6. UI shows product cards with image, price, explanation
7. Agent asks follow-up: "Do you prefer canvas or leather?"
8. User refines → cycle repeats (multi-turn)
```

---

## 🛠️ Tech Stack

| Layer | Tech | Reason |
|-------|------|--------|
| Frontend | React 18 + Vite | Fast, component-based |
| Styling | Tailwind CSS | Utility-first, rapid UI |
| HTTP Client | Axios | Clean API calls |
| Backend | FastAPI (Python) | Async, fast, typed |
| LLM | Claude Sonnet (Anthropic) | Best JSON output + nuanced language |
| Semantic Search | FAISS + sentence-transformers | Fast local vector search |
| Embeddings | all-MiniLM-L6-v2 | 384-dim, fast, accurate |
| Product Data | Shopify Storefront GraphQL API | Production-ready |
| Hosting | Vercel (frontend) + Render (backend) | Free tier |

---

## 📁 Project Structure

```
pixelcart/
├── backend/
│   ├── main.py              # FastAPI server + all routes
│   ├── agent.py             # Claude intent/rank/explain/followup
│   ├── search.py            # FAISS semantic search
│   ├── shopify_client.py    # Shopify GraphQL + mock data
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                      # Main app + chat UI
│   │   ├── main.jsx                     # React entry
│   │   ├── index.css                    # Tailwind + custom styles
│   │   ├── components/
│   │   │   ├── SetupScreen.jsx          # Onboarding + Shopify connect
│   │   │   ├── ChatMessage.jsx          # All message types
│   │   │   └── ProductCard.jsx          # Product display card
│   │   ├── hooks/
│   │   │   └── useChat.js               # Chat state + session management
│   │   └── utils/
│   │       └── api.js                   # Axios API service
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── .env.example
│
└── docs/
    └── README.md
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key (free at [console.anthropic.com](https://console.anthropic.com))

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
# Opens at http://localhost:5173
```

### (Optional) Connect Shopify

Open the app at `http://localhost:5173` → enter your Shopify store URL and Storefront token → click **Launch**.

Or via API directly:
```bash
curl -X POST http://localhost:8000/api/connect-shopify \
  -H "Content-Type: application/json" \
  -d '{"shopify_url":"your-store.myshopify.com","storefront_token":"YOUR_TOKEN"}'
```

---

## 🔑 Accounts Needed

| Service | Required | Free | How to get |
|---------|----------|------|------------|
| Anthropic API | ✅ Yes | ✅ $5 free | [console.anthropic.com](https://console.anthropic.com) |
| Shopify Partner | ❌ Optional | ✅ Free | [partners.shopify.com](https://partners.shopify.com) |
| Vercel | ❌ Deploy only | ✅ Free | [vercel.com](https://vercel.com) |
| Render | ❌ Deploy only | ✅ Free | [render.com](https://render.com) |

> **Without Shopify:** App works out of the box with 10 built-in mock products.

---

## 🌐 Deployment

### Frontend → Vercel
```bash
cd frontend
npm run build
# Push to GitHub → import in Vercel → set VITE_API_URL to your Render backend URL
```

### Backend → Render
- New Web Service → connect GitHub repo → set root to `backend/`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add env var: `ANTHROPIC_API_KEY`

---

## 📊 Scoring Alignment

| Criteria | How Pixelcart addresses it |
|----------|---------------------------|
| Product thinking | FAISS + LLM pipeline solves real discovery friction |
| Documentation | This README + inline code comments |
| Code quality | Modular: agent.py / search.py / shopify_client.py separated |
| Real problem | Replaces broken filter UX with conversation |
| Demo | Multi-turn, live Shopify or mock data |

---

## 🚧 Known Limitations & Future Work
- Session memory is in-memory (add Redis for production)
- FAISS index rebuilds on restart (persist to disk)
- No auth/user accounts (personalisation history)
- Voice input for hands-free shopping
- Multi-language support

---

## 📬 Submission
Team Pixelcart · Kasparro Agentic Commerce Hackathon 2026  
grandmaster@kasparro.com