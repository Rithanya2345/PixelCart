# 🚀 Pixelcart - AI Shopping Agent

> **Natural language in → personalised product picks out.**
> Replace browse → filter → search with a single conversation.

[![Track](https://img.shields.io/badge/Kasparro%20Hackathon-Track%2001-7c6fff)](#)
[![AI Stack](https://img.shields.io/badge/AI%20Stack-Claude%20Sonnet%204-cc8855)](#)

---

## 🎯 Problem Statement

Modern e-commerce platforms force users through a rigid **browse → filter → sort → compare** loop. 
When a user thinks: 
*"I need white sneakers under ₹1500 for casual outings"* 
they must manually translate that into:
- category selection
- price filters
- keyword searches

**Pixelcart eliminates this friction entirely.** 
Users type what they need in plain English, and an AI agent:
- understands intent
- performs semantic search
- ranks results
- provides personalised explanations
—all in a single conversational step.

---

## ✨ What It Does

| User Input | Pixelcart Action |
|---|---|
| *"White sneakers under ₹1500"* | Extracts `category=shoes`, `budget_max=1500`, `preferences=[white]` → returns ranked products |
| *"Gift for my mom under ₹600"* | Detects `recipient=mom`, `budget=600` → suggests gift items |
| *"Wireless earbuds with good bass"* | Identifies `electronics` + preferences → returns relevant matches |

---

## 🧠 Core Pipeline (Per Query)

```
User Message
    ↓
1. Intent Extraction (Claude AI)
   → Converts input into structured JSON
   → Extracts category, budget, preferences, occasion
    ↓
2. Semantic Search (FAISS + embeddings)
   → Finds top-10 similar products
    ↓
3. LLM Re-Ranking (Claude AI)
   → Reorders results based on intent
   → Applies strict budget filtering
    ↓
4. Explanation Generation
   → One-line personalised reason per product
    ↓
5. Follow-up Question
   → Refines user intent for next step
    ↓
Final Output: 
Ranked products + explanations + follow-up
```

---

## 🏗 Architecture

### Tech Stack
| Layer | Technology |
|---|---|
| **AI Agent** | Claude Sonnet 4 (Anthropic) |
| **Semantic Search** | FAISS + `all-MiniLM-L6-v2` |
| **Product Source** | Shopify Storefront API |
| **Backend** | FastAPI, Python 3.11+, Pydantic |
| **Frontend** | React 18, Vite 5, Tailwind CSS 3 |
| **HTTP** | Axios (frontend), Requests (backend) |

---

## 📸 Screenshots

Screenshots are located in: `docs/screenshots/`

---

## 🎬 Demo Video

Watch the Demo (3–5 minutes):
👉 [YOUR_YOUTUBE_OR_DRIVE_LINK_HERE](#)

Video includes:
- Setup flow
- Shopify connection
- Natural language queries
- AI-generated product results
- Full conversational experience

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Anthropic API key**
- _(Optional)_ A Shopify development store

### 1. Clone the repo

```bash
git clone https://github.com/Rithanya2345/PixelCart.git
cd pixelcart
```

### 2. Backend setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add ANTHROPIC_API_KEY

# Start the backend
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
The API will be available at http://localhost:8000.
[Pixelcart] Starting up...
[Pixelcart] 25 products loaded. Building FAISS index...
[FAISS] Index built with 25 products
[Pixelcart] FAISS index ready [OK]
```

### 3. Frontend setup

```bash
cd frontend

npm install
cp .env.example .env
# Default: VITE_API_URL=http://localhost:8000

npm run dev
```

Open: 
- Local: http://localhost:5173
- Deployed: https://pixelcart-m6xu93a3r-rithanya2345s-projects.vercel.app/

### 4. Connect Shopify (Optional)

**Option 1 (UI):**
- Enter store URL → Launch Pixelcart

**Option 2 (Environment):**
- Add in backend `.env`:
  - `SHOPIFY_STORE_URL`
  - `SHOPIFY_STOREFRONT_TOKEN`

**Without Shopify:**
Runs with 25 mock products across: Footwear, Clothing, Electronics, Accessories, Beauty, Books, Kids, Sports.

---

## 📁 Project Structure

```
pixelcart/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── agent.py             # Claude AI pipeline
│   ├── search.py            # FAISS vector search
│   ├── shopify_client.py    # Shopify API integration
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (Chat, Cards)
│   │   ├── hooks/           # useChat custom hook
│   │   ├── App.jsx          # Main UI layout
│   │   └── index.css        # Tailwind styles
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

Team of 2 — **Sangathiyabhashini S D** & **Rithanya C**

### Sangathiyabhashini S D — Engineering Lead
**Key Responsibilities and Deliverables**

| Responsibility | What Was Delivered |
|---|---|
| **Backend architecture** | Built FastAPI backend with lifecycle hooks, session management, and 5 REST endpoints. |
| **AI pipeline** | Implemented 4-stage Claude pipeline in `agent.py`. Enforced budget filtering in backend logic. |
| **Semantic search** | Integrated FAISS with `all-MiniLM-L6-v2` embeddings for vector search. Implemented index persistence. |
| **Shopify integration** | Developed dual integration: GraphQL (authenticated) and REST (public). Added product caching and auto-sync. |
| **Mock catalogue** | Created a 25-product demo dataset across 8 categories with real descriptions and images. |
| **Error resilience** | Implemented fallback mechanisms: Claude failures → safe defaults, FAISS issues → keyword search, Shopify failures → cached/mock data. |

### Rithanya C — Product & Design Lead
**Key Responsibilities and Deliverables**

| Responsibility | What Was Delivered |
|---|---|
| **Problem framing** | Identified the gap between how users think and how e-commerce forces interaction. Defined the core thesis: natural language should replace browse → filter → search. |
| **User journey design** | Designed the full end-to-end experience: setup screen → conversational chat → AI-ranked product cards with personalised explanations → follow-up loop. |
| **Scope decisions** | Defined clear boundaries: what's included (discovery agent) vs. excluded (cart, checkout). Documented all tradeoffs. |
| **Prompt engineering** | Designed Claude system prompts for intent extraction, product explanations, and follow-up questions. |
| **Documentation** | Authored the Product Document, Decision Log (12 decisions), and README. |
| **UI/UX direction** | Selected glassmorphism dark-mode design, gradient accents, typography, and split-panel layout. |

### Joint Contributions

| Area | Collaboration Details |
|---|---|
| **React frontend** | Rithanya C designed UI components. Sangathiyabhashini S D integrated backend via Axios and implemented `useChat` hook. |
| **Architecture decisions**| Jointly decided on: multi-call LLM pipeline vs. single prompt, FAISS vs. Elasticsearch, in-memory sessions vs. database. |
| **Testing & debugging** | Conducted end-to-end testing across multiple query types. Iterated on Claude prompts based on output quality. |
| **Technical documentation**| Sangathiyabhashini S D created API specs and architecture diagrams. Rithanya C wrote failure handling and limitations. Both reviewed and refined content. |

### Time Split
| Area | Sangathiyabhashini S D | Rithanya C |
|---|---|---|
| **Engineering** | 70% | 30% |
| **Product Thinking** | 30% | 70% |
| **Documentation** | 50% | 50% |

**Key Highlights**
- Product-first approach
- Conversational UX over filters
- AI pipeline-driven architecture
- Documentation written alongside development