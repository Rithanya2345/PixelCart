# Pixelcart — Product Document

> **AI Shopping Agent that replaces browse → filter → search with a single natural language conversation.**

---

## 1. What We Built

Pixelcart is a conversational AI shopping agent. Users describe what they want in plain English — _"white sneakers under ₹1500"_ or _"a gift for my mom's birthday"_ — and the system returns ranked, explained product recommendations in a chat-style interface.

It is **not** a chatbot that wraps a search bar. It is a multi-stage AI pipeline:

1. **Intent Extraction** — Claude AI parses the user's message into structured shopping intent (category, budget range, occasion, preferences, recipient, gender)
2. **Semantic Search** — FAISS vector index finds the closest products by meaning, not keywords
3. **LLM Re-Ranking** — Claude re-ranks the FAISS candidates against the user's specific intent
4. **Personalised Explanations** — Each product gets a 1-sentence explanation of _why_ it fits
5. **Follow-up Question** — The agent asks a smart refinement question to narrow down further

This pipeline runs per query in 2–5 seconds.

---

## 2. Who It's For

### Primary User: The Casual Online Shopper

- **Context**: Someone browsing on a phone or laptop who knows _roughly_ what they want but doesn't want to navigate filter trees
- **Behavior**: They think in natural language — "something nice for my friend's birthday under ₹800" — not in categories and sliders
- **Pain point**: Current e-commerce UX forces them to decompose their intent into discrete filter actions

### Secondary User: Store Owners (Shopify merchants)

- **Value**: Plug your Shopify store into Pixelcart and give customers a conversational shopping experience
- **Integration**: Enter your `.myshopify.com` URL → products auto-sync → FAISS index rebuilt → ready to go

---

## 3. Why We Built It

### The Insight

AI assistants (ChatGPT, Perplexity, Gemini) are increasingly where consumers _start_ product research. They ask in natural language. But when they click through to an e-commerce site, they're forced back into the old filter paradigm.

**Pixelcart bridges this gap**: it brings conversational AI _into_ the shopping experience itself, not as a layer on top of filters, but as a complete replacement for the discovery phase.

### Relevance to Kasparro

Kasparro builds AI commerce infrastructure — helping brands show up when consumers ask AI assistants for recommendations. Pixelcart demonstrates the same principle from the merchant side: what happens when the _store itself_ speaks the consumer's language?

---

## 4. Key Decisions

### 4.1 Conversational UX Over Traditional Filters

**Decision**: Full chat interface, no filter sidebar, no category navigation.

**Why**: The whole thesis is that natural language is a better interface for product discovery. Adding filters would undermine the demonstration. If someone needs to refine, they type a follow-up — the agent handles context through session history.

**Tradeoff**: Power users who know exactly what SKU they want might find it slower. Acceptable for a demo focused on discovery, not inventory lookup.

### 4.2 Claude Sonnet 4 as the Core AI

**Decision**: Use Claude for intent extraction, re-ranking, explanations, and follow-ups — four distinct LLM calls per query.

**Why**: Claude's structured output and instruction-following quality is excellent for extracting clean JSON intent and generating concise, non-generic product explanations. Sonnet 4 balances quality with cost and latency.

**Tradeoff**: 4 LLM calls per query adds ~2–4 seconds of latency. Acceptable for the quality of output. In production, intent extraction and explanation generation could be parallelised.

### 4.3 FAISS + Sentence-Transformers for Search

**Decision**: Use FAISS (Facebook AI Similarity Search) with `all-MiniLM-L6-v2` embeddings rather than Shopify's native search or keyword matching.

**Why**: Keyword search misses semantic matches — _"something for my mom"_ wouldn't match a product tagged `gift, women, birthday` via keywords. Semantic search understands meaning. FAISS is fast, runs locally, and needs no external service.

**Tradeoff**: The embedding model is general-purpose, not fine-tuned for e-commerce. Good enough for 25–250 products; would need re-evaluation at 10K+ scale.

### 4.4 Mock Catalogue as Fallback

**Decision**: Ship 25 curated mock products spanning 8 categories (footwear, clothing, electronics, accessories, beauty, books, kids, sports) with real product descriptions and Unsplash images.

**Why**: The app needs to be demo-able without Shopify credentials. The mock catalogue is intentionally diverse to showcase intent parsing across categories. Real product URLs (Amazon, Flipkart, Myntra) make it feel authentic.

**Tradeoff**: Mock data is static. But it's a feature, not a bug — judges can evaluate the AI pipeline without needing a Shopify account.

### 4.5 Shopify-First for Live Integration

**Decision**: Support Shopify via Storefront GraphQL API (authenticated) and public REST API (no token needed).

**Why**: Shopify is the most common merchant platform for the hackathon's target audience. Two integration paths (authenticated vs. public) maximize compatibility across store configurations.

---

## 5. Scope — What's In and What's Out

### ✅ In Scope (MVP)

- Natural language product search
- Multi-turn conversation with session context
- AI intent extraction with structured JSON output
- FAISS semantic search with embedding index
- LLM re-ranking with budget enforcement
- Per-product personalised explanations
- Smart follow-up questions
- Shopify store connection (optional)
- Glassmorphism dark-mode UI
- Demo mode with mock catalogue

### ❌ Out of Scope (Intentional)

| Feature | Why excluded |
|---|---|
| Add-to-cart / checkout | Not a shopping cart — focused on discovery |
| User authentication | Demo-first; no user accounts needed |
| Order tracking | Out of scope for a discovery agent |
| Multi-store comparison | Adds complexity without demonstrating the core insight |
| Payment processing | Deferred to native Shopify checkout |
| Product reviews | Would require additional data source |
| Mobile app | Web-first; responsive design covers mobile browsers |

---

## 6. Walkthrough

### Step 1: Setup Screen

The user lands on a split-panel setup screen:
- **Left panel**: Brand identity, "How it works" steps, example queries, tech stack badges
- **Right panel**: Optional Shopify URL input, backend health check, Launch/Demo buttons

### Step 2: Connect or Demo

- **With Shopify**: Enter `your-store.myshopify.com` → products fetch → FAISS index rebuilds → launch
- **Without Shopify**: Click "Demo" → 25 curated products loaded → immediate launch

### Step 3: Conversational Shopping

- The chat interface shows a welcome message with suggestion chips
- User types a query (e.g., _"Gift for my mom under ₹600"_)
- The AI processes: intent pills appear (category, budget, recipient)
- Product cards render in a grid with images, prices, ratings, explanations, and tags
- A follow-up question appears to help refine the search
- Response time is displayed (⚡ 2800ms)

### Step 4: Refinement

- User asks a follow-up (e.g., _"Something more festive"_)
- The agent remembers context (session-based) and adjusts recommendations
- New results appear with updated explanations

---

## 7. Success Metrics (If Deployed)

| Metric | Target | Measurement |
|---|---|---|
| **Query-to-result satisfaction** | 80%+ users find a relevant product in first response | User feedback/click-through |
| **Response latency** | < 5 seconds end-to-end | Backend timing |
| **Intent parse accuracy** | 90%+ correct field extraction | Manual evaluation on test set |
| **Session depth** | Average 2.5+ queries per session | Session analytics |
| **Shopify connection success** | 95%+ stores connect on first attempt | Error rate tracking |

---

## 8. Future Directions

1. **Streaming responses** — Show products as they're ranked, not all at once
2. **Voice input** — Natural language is even more natural when spoken
3. **Multi-store aggregation** — Search across Amazon, Flipkart, and Shopify simultaneously
4. **Personalisation memory** — Remember user preferences across sessions
5. **Checkout integration** — Add-to-cart directly from the chat interface
6. **Analytics dashboard** — Show merchants what customers are asking for
