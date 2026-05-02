# Pixelcart — Decision Log

> Key decisions — "considered X, chose Y, because Z."

---

## Decision 01: Conversational UI vs. Filter-Based UI

| | |
|---|---|
| **Date** | April 27, 2026 |
| **Context** | Choosing the primary interaction model for product discovery |
| **Considered** | (A) Traditional filter sidebar + search bar, (B) Hybrid: filters + chat, (C) Full conversational chat |
| **Chose** | **(C) Full conversational chat** |
| **Because** | The entire thesis is that natural language is a better discovery interface. Adding filters would dilute the demo and add engineering surface without demonstrating the core AI value. Multi-turn conversation replaces refinement filters. |
| **Tradeoff** | Power users can't jump to an exact SKU. Acceptable — Pixelcart is a discovery tool, not an inventory search. |

---

## Decision 02: Claude Sonnet 4 as the AI Engine

| | |
|---|---|
| **Date** | April 27, 2026 |
| **Context** | Choosing which LLM to use for intent extraction, ranking, and explanations |
| **Considered** | (A) OpenAI GPT-4o, (B) Claude Sonnet 4, (C) Local LLM (e.g., Llama 3), (D) Google Gemini |
| **Chose** | **(B) Claude Sonnet 4** |
| **Because** | Claude's structured output reliability is excellent — it consistently returns valid JSON from intent extraction without extra validation layers. Sonnet 4 balances quality, cost (~$3/MTok input), and latency (~800ms per call). The Anthropic Python SDK is clean and well-documented. |
| **Tradeoff** | 4 LLM calls per query add 2–4s latency. Could be reduced by parallelising explanation generation. |

---

## Decision 03: FAISS over Shopify Search / Elasticsearch

| | |
|---|---|
| **Date** | April 28, 2026 |
| **Context** | How to search products given a natural language query |
| **Considered** | (A) Shopify's native search API, (B) Elasticsearch/OpenSearch, (C) FAISS with sentence-transformers, (D) Keyword matching only |
| **Chose** | **(C) FAISS with sentence-transformers** |
| **Because** | Semantic search understands meaning, not just keywords. "Gift for my mom" matches products tagged `gift, women, birthday` even without word overlap. FAISS runs locally with zero infrastructure cost. `all-MiniLM-L6-v2` produces good quality 384-dim embeddings with a 22MB model. |
| **Tradeoff** | General-purpose embeddings aren't optimised for e-commerce. At scale (10K+ products), we'd need IVF indexing or a managed vector DB. |

---

## Decision 04: Keyword Fallback for Search

| | |
|---|---|
| **Date** | April 28, 2026 |
| **Context** | What happens if FAISS/sentence-transformers can't be installed? |
| **Considered** | (A) Fail hard — require FAISS, (B) Keyword fallback with title-weighted scoring |
| **Chose** | **(B) Keyword fallback** |
| **Because** | Hackathon judges might run into dependency issues (FAISS installation can be finicky on some platforms). The app should always work. Keyword fallback gives reasonable results even without semantic understanding. |
| **Tradeoff** | Keyword search misses semantic matches. Explicitly documented as a degraded mode. |

---

## Decision 05: 25-Product Mock Catalogue

| | |
|---|---|
| **Date** | April 29, 2026 |
| **Context** | App needs demo data when no Shopify store is connected |
| **Considered** | (A) No mock data — require Shopify, (B) 5 placeholder products, (C) 25 curated products across 8 categories |
| **Chose** | **(C) 25 curated products across 8 categories** |
| **Because** | Judges need to see the AI handle diverse queries (footwear, electronics, gifts, beauty, etc.) without needing Shopify credentials. Real product descriptions and Unsplash images make it feel authentic. Real URLs (Amazon, Flipkart, Myntra) show purchase intent. |
| **Tradeoff** | 25 products is small — some queries won't find ideal matches. But it's enough to demonstrate intent parsing and semantic search working correctly. |

---

## Decision 06: Two Shopify Integration Paths (GQL + REST)

| | |
|---|---|
| **Date** | April 30, 2026 |
| **Context** | How to connect to a Shopify store |
| **Considered** | (A) Storefront GraphQL API only (requires token), (B) Public REST API only (no token), (C) Both, with automatic fallback |
| **Chose** | **(C) Both paths with fallback** |
| **Because** | Some stores have Storefront API tokens configured; some don't. The public REST API (`/products.json`) works without authentication on many Shopify stores. Supporting both maximises compatibility. |
| **Tradeoff** | Two code paths to maintain. Worth it for reliability. |

---

## Decision 07: In-Memory Sessions (No Database)

| | |
|---|---|
| **Date** | April 27, 2026 |
| **Context** | How to store conversation history and accumulated intent |
| **Considered** | (A) PostgreSQL/SQLite, (B) Redis, (C) In-memory Python dict |
| **Chose** | **(C) In-memory dict** |
| **Because** | For a hackathon demo, sessions are ephemeral. No one needs persistence across server restarts. Adding a database would complicate setup instructions without demonstrating AI value. |
| **Tradeoff** | Sessions lost on restart. Documented as a known limitation. |

---

## Decision 08: Glassmorphism Dark Mode UI

| | |
|---|---|
| **Date** | April 27, 2026 |
| **Context** | Visual design direction for the frontend |
| **Considered** | (A) Light mode with standard cards, (B) Dark mode with flat design, (C) Dark mode with glassmorphism |
| **Chose** | **(C) Dark mode with glassmorphism** |
| **Because** | Dark mode feels premium and modern for an AI product. Glassmorphism (frosted glass effects, subtle borders, gradient accents) creates visual depth without clutter. The purple-to-green gradient aligns with AI/tech branding. |
| **Tradeoff** | Slightly harder to read for users who prefer light mode. Acceptable for a demo focused on first impressions. |

---

## Decision 09: Budget Enforcement in Code, Not LLM

| | |
|---|---|
| **Date** | April 29, 2026 |
| **Context** | How to enforce budget constraints from user queries |
| **Considered** | (A) Trust Claude to filter by budget during re-ranking, (B) Enforce budget as a hard filter in Python after Claude ranks |
| **Chose** | **(B) Hard filter in Python** |
| **Because** | LLMs can hallucinate or ignore constraints. Budget is a hard business rule — if the user says "under ₹1500", showing a ₹3695 product is a trust violation. Enforcing in code guarantees correctness. |
| **Tradeoff** | Might return fewer than 5 results if budget is very tight. Better than showing wrong results. |

---

## Decision 10: Separate LLM Calls vs. Single Mega-Prompt

| | |
|---|---|
| **Date** | April 28, 2026 |
| **Context** | Whether to use one large Claude prompt or multiple focused calls |
| **Considered** | (A) One mega-prompt: "extract intent, search, rank, explain, and follow up", (B) Four separate, focused calls |
| **Chose** | **(B) Four separate calls** |
| **Because** | Single-purpose prompts produce more reliable output. Intent extraction needs strict JSON; explanations need creative copy; ranking needs ordered indices. Combining them leads to format drift and harder error handling. Each call can fail independently with its own fallback. |
| **Tradeoff** | 4 calls × ~800ms = ~3.2s latency. Explanation calls (5 products) could be parallelised to cut ~2s. Not implemented in MVP. |

---

## Decision 11: Vite + React Over Next.js

| | |
|---|---|
| **Date** | April 27, 2026 |
| **Context** | Frontend framework choice |
| **Considered** | (A) Next.js (SSR, file-based routing), (B) Vite + React (SPA, minimal config) |
| **Chose** | **(B) Vite + React** |
| **Because** | Pixelcart is a single-page chat application. No routing, no SSR, no SEO requirements (it's an internal tool, not a public website). Vite is faster to set up, faster to build, and has simpler config. Next.js would add unnecessary complexity. |
| **Tradeoff** | No SSR. Irrelevant for a chat-based tool. |

---

## Decision 12: No Cart / Checkout

| | |
|---|---|
| **Date** | April 27, 2026 |
| **Context** | Whether to implement add-to-cart and checkout flows |
| **Considered** | (A) Full cart + Shopify checkout, (B) "View on Shopify" link only |
| **Chose** | **(B) "View on Shopify" link** |
| **Because** | Pixelcart is a discovery agent, not a shopping cart. Building checkout would triple the scope without demonstrating AI capabilities. Linking to Shopify lets the native checkout handle payment/shipping. |
| **Tradeoff** | Users leave Pixelcart to complete purchase. Acceptable — the AI value is in discovery, not transaction. |

---

_End of decision log._
