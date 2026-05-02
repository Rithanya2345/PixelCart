# Pixelcart — Decision Log

> Key decisions — "considered X, chose Y, because Z."

---

## Decision 01: Conversational UI vs. Filter-Based UI
**Considered**: (A) Traditional filter sidebar, (B) Hybrid: filters + chat, (C) Full conversational chat
**Chose**: (C) Full conversational chat
**Because**: Natural language is a better discovery interface. Adding filters would dilute the demo and add engineering surface without demonstrating the core AI value.

## Decision 02: Claude Sonnet 4 as the AI Engine
**Considered**: (A) OpenAI GPT-4o, (B) Claude Sonnet 4, (C) Local LLM
**Chose**: (B) Claude Sonnet 4
**Because**: Claude's structured output reliability is excellent — it consistently returns valid JSON from intent extraction. Sonnet 4 perfectly balances quality, cost, and latency.

## Decision 03: FAISS over Shopify Search / Elasticsearch
**Considered**: (A) Shopify's native search API, (B) Elasticsearch, (C) FAISS with sentence-transformers
**Chose**: (C) FAISS with sentence-transformers
**Because**: Semantic search understands meaning, not just keywords. "Gift for my mom" matches products tagged `gift, birthday` even without word overlap.

## Decision 04: Keyword Fallback for Search
**Considered**: (A) Fail hard without FAISS, (B) Keyword fallback
**Chose**: (B) Keyword fallback
**Because**: Hackathon judges might run into dependency issues. The app should always work, even if search quality degrades.

## Decision 05: 25-Product Mock Catalogue
**Considered**: (A) No mock data, (B) 25 curated products across 8 categories
**Chose**: (B) 25 curated products
**Because**: Judges need to see the AI handle diverse queries without needing to set up Shopify credentials. Real descriptions and images make it feel authentic.

## Decision 06: Two Shopify Integration Paths (GQL + REST)
**Considered**: (A) GraphQL only, (B) REST only, (C) Both with fallback
**Chose**: (C) Both paths with fallback
**Because**: Supporting both authenticated and unauthenticated paths maximizes compatibility across different store configurations.

## Decision 07: In-Memory Sessions (No Database)
**Considered**: (A) PostgreSQL, (B) Redis, (C) In-memory Python dict
**Chose**: (C) In-memory dict
**Because**: For a hackathon demo, sessions are ephemeral. Adding a database would overcomplicate the setup.

## Decision 08: Budget Enforcement in Code, Not LLM
**Considered**: (A) Trust Claude to filter by budget, (B) Enforce as hard filter in Python
**Chose**: (B) Hard filter in Python
**Because**: LLMs hallucinate. Budget is a hard business rule that must be strictly enforced.

## Decision 09: Separate LLM Calls vs. Single Mega-Prompt
**Considered**: (A) One mega-prompt, (B) Four separate focused calls
**Chose**: (B) Four separate calls
**Because**: Single-purpose prompts produce more reliable output. Each call can fail independently with its own fallback.

## Decision 10: Vite + React Over Next.js
**Considered**: (A) Next.js, (B) Vite + React
**Chose**: (B) Vite + React
**Because**: Pixelcart is a single-page chat application with no SEO or routing needs. Vite is faster to set up and build.
