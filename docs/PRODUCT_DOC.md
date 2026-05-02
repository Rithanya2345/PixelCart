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

1. **Conversational UX Over Traditional Filters**: Full chat interface, no filter sidebar, no category navigation.
2. **Claude Sonnet 4 as the Core AI**: Excellent for extracting clean JSON intent and generating concise, non-generic product explanations.
3. **FAISS + Sentence-Transformers for Search**: Keyword search misses semantic matches. FAISS is fast, runs locally, and needs no external service.
4. **Mock Catalogue as Fallback**: App works without Shopify credentials for easy demoing.
5. **Shopify-First for Live Integration**: Support Shopify via Storefront GraphQL API (authenticated) and public REST API (no token needed).

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

### ❌ Out of Scope (Intentional)
- Add-to-cart / checkout (Focused on discovery)
- User authentication
- Multi-store comparison
- Payment processing

---

## 6. Success Metrics (If Deployed)
| Metric | Target | Measurement |
|---|---|---|
| **Query-to-result satisfaction** | 80%+ users find a relevant product in first response | User feedback/click-through |
| **Response latency** | < 5 seconds end-to-end | Backend timing |
| **Intent parse accuracy** | 90%+ correct field extraction | Manual evaluation on test set |
| **Session depth** | Average 2.5+ queries per session | Session analytics |
