---
description: Repo root tree and design reference
---

# Repo Root Tree

```
windsurf-project/
├── apps/                              # Frontend (Expo / React Native)
│   ├── app/
│   │   ├── (tabs)/
│   │   │   ├── _layout.tsx            # Tab navigator layout
│   │   │   ├── index.tsx              # Home tab
│   │   │   ├── profile.tsx            # Profile tab
│   │   │   └── search.tsx             # Search tab
│   │   └── _layout.tsx                # Root layout
│   ├── assets/
│   │   ├── favicon.png
│   │   └── icon.png
│   ├── components/
│   │   ├── ConfidenceMeter.tsx        # Confidence score gauge
│   │   ├── DecisionCard.tsx           # Search result decision card
│   │   ├── MoneyHero.tsx              # Hero banner for money context
│   │   ├── PlanModal.tsx              # Plan details modal
│   │   ├── SignalPills.tsx            # Tag-style signal indicators
│   │   ├── Skeleton.tsx              # Loading skeleton placeholders
│   │   ├── Sparkline.tsx             # Inline mini chart
│   │   └── Surface.tsx               # Reusable card surface wrapper
│   ├── context/
│   │   └── SearchContext.tsx           # Global search state provider
│   ├── lib/
│   │   └── api.ts                     # API client / fetch helpers
│   ├── app.json                       # Expo config
│   ├── babel.config.js
│   ├── global.css                     # Tailwind base styles
│   ├── metro.config.js
│   ├── package.json
│   ├── tailwind.config.js             # NativeWind / Tailwind config
│   ├── tsconfig.json
│   └── types.ts                       # Frontend-local type defs
│
├── api/                               # Backend (FastAPI / Python)
│   ├── app/
│   │   ├── pipeline/
│   │   │   ├── ingress.py             # Inbound data normalization
│   │   │   ├── intent.py              # Query intent classification
│   │   │   ├── orchestrator.py        # Pipeline flow controller
│   │   │   ├── rank.py                # Initial ranking pass
│   │   │   ├── rerank.py              # Re-ranking / boosting
│   │   │   ├── retrieve.py            # Document retrieval layer
│   │   │   ├── state.py               # Pipeline state model
│   │   │   └── summarize.py           # LLM summarization step
│   │   ├── routes/
│   │   │   ├── health.py              # GET /health
│   │   │   ├── profile.py             # Profile endpoints
│   │   │   └── search.py              # POST /search
│   │   ├── __init__.py
│   │   ├── config.py                  # Env / settings loader
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── middleware.py              # CORS, logging, etc.
│   │   ├── schemas.py                # Pydantic request/response models
│   │   ├── seed.py                   # Dev seed data
│   │   └── store.py                  # Data store abstraction
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_search.py
│   ├── static/
│   ├── Procfile                       # Railway deploy command
│   ├── requirements.txt
│   └── requirements-full.txt
│
├── packages/                          # Shared code across apps & api
│   └── shared/
│       ├── models.py                  # Shared Pydantic models
│       └── types.ts                   # Shared TypeScript types
│
├── .env.example                       # Environment variable template
├── .gitignore
├── docker-compose.yml                 # Local dev orchestration
├── Makefile                           # Dev task runner
└── README.md
```

# Design Elements

## Color Palette
- **Background** — `#0F172A` (slate-900) deep navy base
- **Surface** — `#1E293B` (slate-800) card & panel bg
- **Border** — `#334155` (slate-700) subtle dividers
- **Primary** — `#3B82F6` (blue-500) interactive / CTA
- **Accent** — `#22D3EE` (cyan-400) sparklines, highlights
- **Success** — `#10B981` (emerald-500) positive signals
- **Warning** — `#F59E0B` (amber-500) caution indicators
- **Danger** — `#EF4444` (red-500) negative signals
- **Text Primary** — `#F8FAFC` (slate-50)
- **Text Secondary** — `#94A3B8` (slate-400)

## Typography
- **Font** — System default (San Francisco / Roboto)
- **Headings** — `font-bold`, size scaled per hierarchy
- **Body** — `text-sm` / `text-base`, `text-slate-200`
- **Caption** — `text-xs`, `text-slate-400`

## Component Patterns
- **Surface** — Rounded (`rounded-2xl`), `bg-slate-800`, `border border-slate-700`, `p-4`
- **DecisionCard** — Surface + confidence meter + signal pills + sparkline
- **ConfidenceMeter** — Circular gauge, color-coded (green/amber/red)
- **SignalPills** — Rounded-full tags, muted bg, colored text
- **Sparkline** — Inline SVG mini-chart, `stroke-cyan-400`
- **Skeleton** — Pulsing `bg-slate-700` placeholder blocks
- **PlanModal** — Bottom sheet, `bg-slate-900`, drag handle

## Layout
- **Tab bar** — 3 tabs: Home, Search, Profile
- **Spacing** — `gap-4` between cards, `px-4` horizontal padding
- **Safe areas** — Respected via `SafeAreaView` / Expo
- **Scrolling** — `ScrollView` with `pb-24` bottom padding for tab bar clearance