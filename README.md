# 🛍️ Pixelcart — AI Shopping Agent

> **Natural language in → personalised product picks out.**
> Replace browse → filter → search with a single conversation.

[![Track](https://img.shields.io/badge/Kasparro%20Hackathon-Track%2001-7c6fff?style=flat-square)](#)
[![Stack](https://img.shields.io/badge/Claude%20AI-Sonnet%204-00dfa8?style=flat-square)](#)

---

## 📌 Problem Statement

Modern e-commerce forces users through a rigid **browse → filter → sort → compare** loop. When a user thinks _"I need white sneakers under ₹1500 for casual outings"_, they must translate that thought into multiple discrete clicks across categories, price sliders, and keyword searches.

**Pixelcart eliminates this friction entirely.** Users type what they need in plain English, and an AI agent understands intent, searches semantically, and returns ranked product recommendations with personalised explanations — all in one conversation turn.

---

## 🎯 What It Does

| User says | Pixelcart does |
|---|---|
| _"White sneakers under ₹1500"_ | Extracts category=shoes, budget_max=1500, preferences=[white] → returns ranked picks |
| _"Gift for my mom under ₹600"_ | Detects recipient=mom, budget_max=600, occasion=gift → curates gifting options |
| _"Wireless earbuds with good bass"_ | Parses category=electronics, preferences=[wireless, bass] → surfaces best matches |

### Core Pipeline (per query)

```
User Message
    ↓
┌─────────────────────────┐
│  1. Intent Extraction    │  Claude AI parses → structured JSON
│     (category, budget,   │  (budget, occasion, preferences, etc.)
│      occasion, prefs)    │
└─────────┬───────────────┘
          ↓
┌─────────────────────────┐
│  2. Semantic Search      │  FAISS + sentence-transformers
│     (FAISS + embeddings) │  finds top-10 nearest products
└─────────┬───────────────┘
          ↓
┌─────────────────────────┐
│  3. LLM Re-Ranking      │  Claude re-ranks by intent fit
│     (Claude AI)          │  + budget enforcement
└─────────┬───────────────┘
          ↓
┌─────────────────────────┐
│  4. Explanation Gen      │  1-sentence per product:
│     (personalised)       │  "why this suits YOUR need"
└─────────┬───────────────┘
          ↓
┌─────────────────────────┐
│  5. Follow-up Question   │  Smart refinement prompt
│     (conversational)     │  to narrow results further
└─────────────────────────┘
          ↓
    Ranked Products + Cards + Follow-up
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│              Frontend (React + Vite)     │
│  SetupScreen → ChatUI → ProductCards    │
│  Tailwind CSS · Glassmorphism dark UI   │
└──────────────┬──────────────────────────┘
               │ HTTP (axios)
┌──────────────▼──────────────────────────┐
│          Backend (FastAPI + Python)      │
│                                         │
│  /api/chat  ─→ agent.py (Claude AI)     │
│              ─→ search.py (FAISS)       │
│              ─→ shopify_client.py       │
│                                         │
│  /api/connect-shopify ─→ Shopify API    │
│  /api/health, /api/products             │
└──────────────┬──────────────────────────┘
               │
    ┌──────────▼──────────┐
    │  Shopify Storefront  │
    │  GraphQL / REST API  │
    └─────────────────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| **AI Agent** | Claude Sonnet 4 (Anthropic) — intent, ranking, explanations |
| **Semantic Search** | FAISS + `all-MiniLM-L6-v2` (sentence-transformers) |
| **Product Source** | Shopify Storefront API (GraphQL + public REST) |
| **Backend** | FastAPI, Python 3.11+, Pydantic |
| **Frontend** | React 18, Vite 5, Tailwind CSS 3 |
| **HTTP Client** | Axios (frontend), Requests (backend) |

---

## 🖼️ Screenshots

> Screenshots are located in `docs/screenshots/`. See the [Product Walkthrough](docs/PRODUCT_DOC.md#-walkthrough) for a guided tour.

---

## 🎬 Demo Video

> **📹 [Watch the Demo (3–5 min)](YOUR_YOUTUBE_OR_DRIVE_LINK_HERE)**
>
> Screen recording with narration covering: setup flow, Shopify connection, natural language queries, AI-powered results, and the full conversation experience.

⚠️ _Replace the link above with your actual YouTube (unlisted) or Google Drive link before submitting._

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Anthropic API key** ([console.anthropic.com](https://console.anthropic.com) → API Keys)
- _(Optional)_ A Shopify development store

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/pixelcart.git
cd pixelcart
```

### 2. Backend setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
# (Optionally add SHOPIFY_STORE_URL and SHOPIFY_STOREFRONT_TOKEN)

# Start the backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You should see:
```
[Pixelcart] Starting up...
[Pixelcart] 25 products loaded. Building FAISS index...
[FAISS] Index built with 25 products -> faiss_index.pkl
[Pixelcart] FAISS index ready [OK]
```

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Default: VITE_API_URL=http://localhost:8000

# Start the dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

### 4. (Optional) Connect Shopify

You can connect a live Shopify store in two ways:

1. **Via the UI**: Enter your store URL (e.g., `pixelcart-dev.myshopify.com`) in the setup screen and click "Launch Pixelcart"
2. **Via environment**: Set `SHOPIFY_STORE_URL` and `SHOPIFY_STOREFRONT_TOKEN` in `backend/.env` — products auto-sync on startup

Without Shopify, the app runs with a curated 25-product mock catalogue spanning footwear, clothing, electronics, accessories, beauty, books, kids, and sports.

---

## 📂 Project Structure

```
pixelcart/
├── backend/
│   ├── main.py              # FastAPI app, endpoints, lifespan hooks
│   ├── agent.py             # Claude AI — intent, ranking, explanations, follow-ups
│   ├── search.py            # FAISS semantic search + keyword fallback
│   ├── shopify_client.py    # Shopify API client (GraphQL + REST) + mock catalogue
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main chat interface
│   │   ├── components/
│   │   │   ├── SetupScreen.jsx   # Shopify connection + launch screen
│   │   │   ├── ChatMessage.jsx   # Message rendering + intent pills
│   │   │   ├── ProductCard.jsx   # Product result cards with ratings
│   │   │   ├── SkeletonCard.jsx  # Loading skeleton
│   │   │   └── WelcomeBanner.jsx # Welcome header
│   │   ├── hooks/useChat.js      # Chat state management
│   │   └── utils/api.js          # Axios API client
│   ├── index.html
│   ├── package.json
│   └── .env.example
├── docs/
│   ├── PRODUCT_DOC.md       # Product document
│   ├── TECHNICAL_DOC.md     # Technical document
│   └── DECISION_LOG.md      # Decision log
└── README.md                # ← You are here
```

---

## 📄 Documentation

| Document | Description |
|---|---|
| [Product Document](docs/PRODUCT_DOC.md) | What we built, for whom, why. Key decisions and tradeoffs. |
| [Technical Document](docs/TECHNICAL_DOC.md) | Architecture, implementation details, failure handling, limitations. |
| [Decision Log](docs/DECISION_LOG.md) | Key decisions — "considered X, chose Y, because Z." |

---

## 👥 Contribution Note

**Team of 2 — [Member 1 Name] & [Member 2 Name]**

### [Member 1 Name] — Product & Design Lead

| Responsibility | What was delivered |
|---|---|
| **Problem framing** | Identified the gap between how users think ("gift for mom under ₹600") and how e-commerce makes them shop (filters, categories, sliders). Defined the core thesis: natural language should replace browse → filter → search. |
| **User journey design** | Designed the full end-to-end flow: setup screen (connect Shopify or try demo) → conversational chat → AI-ranked product cards with personalised explanations → follow-up refinement loop. |
| **Scope decisions** | Drew the line on what's in (discovery agent) vs. what's out (cart, checkout, auth, multi-store). Documented tradeoffs for each exclusion in the decision log. |
| **Prompt engineering** | Crafted the Claude system prompts for intent extraction, product explanations, and follow-up questions — iterated on tone, word limits, and output format to get reliable structured JSON. |
| **Documentation** | Wrote the Product Document, Decision Log (12 decisions), and README. |
| **UI/UX direction** | Chose glassmorphism dark-mode aesthetic, gradient accents (purple → green), Syne + DM Sans typography, and the split-panel setup screen layout. |

### [Member 2 Name] — Engineering Lead

| Responsibility | What was delivered |
|---|---|
| **Backend architecture** | Built the FastAPI backend with lifespan hooks, session management, and a 5-endpoint REST API (`/api/chat`, `/api/connect-shopify`, `/api/health`, `/api/products`, `/api/session/{id}`). |
| **AI pipeline** | Implemented the 4-stage Claude integration in `agent.py` — intent extraction → LLM re-ranking → per-product explanation generation → follow-up question building. Added budget enforcement as a hard code filter after Claude's ranking. |
| **Semantic search** | Set up FAISS with `all-MiniLM-L6-v2` sentence-transformers for vector similarity search. Built automatic index persistence (`faiss_index.pkl`) and a keyword-scoring fallback for environments where FAISS can't be installed. |
| **Shopify integration** | Wrote the dual-path Shopify client — Storefront GraphQL API (authenticated) and public REST API (no token). Implemented product caching (`product_cache.json`) and auto-sync on startup. |
| **Mock catalogue** | Curated the 25-product demo catalogue across 8 categories with real product descriptions, Unsplash images, and live retailer URLs (Amazon, Flipkart, Myntra). |
| **Error resilience** | Designed graceful fallbacks for every external dependency — Claude failures return safe defaults, FAISS falls back to keyword search, Shopify failures fall back to cached/mock data. |

### Joint Contributions

| Area | How both contributed |
|---|---|
| **React frontend** | [Member 1 Name] designed the component layout and styling (SetupScreen, ProductCard, ChatMessage). [Member 2 Name] wired the components to the backend via Axios, built the `useChat` hook for session state, and implemented real-time loading indicators. |
| **Architecture decisions** | Discussed and decided together: separate LLM calls vs. single mega-prompt, FAISS vs. Elasticsearch, in-memory sessions vs. database, budget enforcement in code vs. trusting the LLM. |
| **Testing & debugging** | Both ran end-to-end tests across query types (budget queries, gift queries, category searches). Iterated on Claude prompt wording based on observed output quality. |
| **Technical documentation** | [Member 2 Name] drafted the API spec and architecture diagrams. [Member 1 Name] wrote the failure handling section and limitations. Both reviewed and refined. |

### Time Split

| | [Member 1 Name] | [Member 2 Name] |
|---|---|---|
| **Product thinking** | 70% | 30% |
| **Engineering** | 30% | 70% |
| **Documentation** | 50% | 50% |