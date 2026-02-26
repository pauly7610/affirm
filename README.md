# Affirm Agentic Discovery

A mobile-first native app prototype demonstrating **agentic search** for financial product discovery. Built with Expo (React Native) + FastAPI + LangGraph + pgvector.

No chat UI. No chatbot. Just intelligent, ambient AI that answers: **"Can I afford this?"**

---

## Architecture

```
┌─────────────────┐       ┌──────────────────────────────────┐
│  Expo (RN) App  │──────▶│  FastAPI Backend (:8000)          │
│  iOS/Android/Web│       │                                    │
│  (:8081)        │       │  LangGraph Pipeline:               │
│                 │       │  ingress → intent → router →       │
│  Tabs:          │       │  retrieve (pgvector) → rerank →    │
│  Home / Search  │       │  rank (affordability) → summarize  │
│  / Profile      │       │                                    │
└─────────────────┘       └──────────┬───────────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Postgres + pgvector │
                          │  (Docker) or         │
                          │  In-memory mock       │
                          └───────────────────────┘
```

## How to Run

### Quick Start (no Docker, no DB)

```bash
# Backend
cd backend
pip install -r requirements.txt
set USE_MOCK_DB=true   # Windows
# export USE_MOCK_DB=true  # Mac/Linux
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npx expo start
```

Open Expo Go on your phone and scan the QR code, or press `w` for web.

### Full Stack (with Postgres + pgvector)

```bash
# Start Postgres
docker compose up -d postgres

# Backend
cd backend
pip install -r requirements.txt
set USE_MOCK_DB=false
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npx expo start
```

### Environment Variables

Copy `.env.example` to `.env` in the root. Key settings:

| Variable | Default | Description |
|---|---|---|
| `USE_MOCK_DB` | `true` | Skip Postgres, use in-memory store |
| `EMBEDDING_MODEL` | `none` | `BAAI/bge-small-en-v1.5` for real embeddings |
| `RERANKER_MODEL` | `none` | `BAAI/bge-reranker-base` for real reranking |
| `LLM_PROVIDER` | `none` | Template-based summaries (no LLM needed) |

---

## Screens

### Home — "Your Money Today"
- **Money Hero**: spending power with greeting + credit-safe microcopy
- **Signal Pills**: real-time financial signals (spending trends, eligibility, credit impact)
- **Opportunities**: personalized DecisionCards from the agentic search pipeline
- **Explore Chips**: tap to navigate to Search with pre-filled intent
- **Smart Reminders**: payment due dates + eligibility refresh

### Search — "Decision Search" (centerpiece)
- **Agentic, not chat**: search input + goal chips, no conversation thread
- **AI Summary**: short, calm summary of how results were prioritized
- **Refine Chips**: tap to re-rank results (lower monthly, 0% APR, cheaper total, shorter term)
- **Decision Cards**: 1 recommended + alternatives with monthly payment emphasis, APR, confidence meter
- **Monthly Impact**: small bar visualization comparing payment amounts

### Profile — "Financial Clarity"
- **Account Health**: avatar, stats, confidence meter
- **Spending Power**: eligibility estimate with explanation
- **Active Plans**: progress bars, remaining balance, next payment dates
- **Financial Insights**: Mint-energy insights with sparklines
- **Privacy & Control**: accordion explanation + toggles for personalization/data/notifications

---

## Agentic Search Pipeline (LangGraph)

The search pipeline is implemented as a **LangGraph StateGraph** with 7 nodes:

```
ingress → intent → router → retrieve → rerank → rank → summarize → END
```

### 1. Ingress
Sanitize query, strip PII (SSN, email, phone, card numbers), reject disallowed intents (e.g., "hack credit").

### 2. Intent Parse
Extract structured constraints from natural language:
- `"under $800"` → `max_price: 800`
- `"under $50/mo"` → `max_monthly: 50`
- `"0% APR"` → `only_zero_apr: true`
- `"laptop"` → `category: electronics`

### 3. Router
Classify query complexity (simple vs. complex based on constraint count). Complex queries could trigger multi-step retrieval in production.

### 4. Retrieve
- **Vector search**: cosine similarity on query embedding vs. 34 offer embeddings (384-dim)
- **SQL-like filters**: apply parsed constraints (category, price, monthly, APR)
- **Relaxation**: if filters are too aggressive (< 3 results), pad with vector-only results

### 5. Rerank (BGE)
- **Real mode** (`RERANKER_MODEL=BAAI/bge-reranker-base`): CrossEncoder scoring on query-passage pairs
- **Mock mode** (`RERANKER_MODEL=none`): keyword overlap + similarity score

### 6. Rank (Affordability)
Deterministic weighted scorer:
```
score = w1 * affordability + w2 * apr_score + w3 * confidence + w4 * rerank_score
```
Weights shift based on refine toggles (e.g., "Lower monthly" → affordability weight 0.5).

### 7. Summarize
Template-based output:
- **AI Summary**: "We prioritized options that fit your budget, minimize interest, and match your eligibility."
- **Per-item reasons**: "Recommended based on your spending profile." / "0% APR keeps your total cost low."
- **Monthly impact** chart data
- **Refine chips** for re-ranking
- **Disclaimers**

---

## Refine Logic

Refine chips re-run the pipeline with updated constraints:

| Chip | Effect |
|---|---|
| Lower monthly | Sort by `lowest_monthly` (affordability weight 0.5) |
| Only 0% APR | Filter `apr === 0` |
| Cheaper total | Sort by `lowest_total` |
| Shorter term | Sort by `shortest_term` |
| Compare brands | No filter change (future: diversify merchants) |

---

## Production Swap Points

| Prototype | Production |
|---|---|
| In-memory Python dicts | Postgres + pgvector |
| Deterministic hash embeddings | `BAAI/bge-small-en-v1.5` |
| Keyword reranker | `BAAI/bge-reranker-base` (CrossEncoder) |
| Template summaries | LLM (OpenAI / Ollama) |
| No auth | OAuth2 + JWT |
| Naive rate limiting (TODO) | Redis sliding window |

---

## Tech Stack

- **Frontend**: Expo (React Native) + Expo Router + NativeWind + react-native-svg
- **Backend**: FastAPI + LangGraph + numpy + Pydantic
- **Vector Store**: pgvector (Docker) or in-memory cosine similarity
- **Reranker**: BGE CrossEncoder (optional) or deterministic fallback
- **Shared Contract**: TypeScript types ↔ Pydantic models in `packages/shared/`

---

## Tests

```bash
# Backend
cd backend
python -m pytest tests/ -v

# Frontend typecheck
cd frontend
npx tsc --noEmit
```
