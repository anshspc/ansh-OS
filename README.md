# Personalix OS — AI-Powered Personal Operating System

<div align="center">

![Personalix OS Banner](https://ansh-os-frontend.onrender.com/)
![Python](https://img.shields.io/badge/Python-3.13-3776ab?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+pgvector-336791?style=for-the-badge&logo=postgresql)

**A production-grade AI-native personal command center for knowledge workers and engineers.**

</div>

---

## What is Personalix OS?

Personalix OS is **not** a Notion clone, ChatGPT wrapper, or generic productivity dashboard.

It is a **full-stack AI Personal Operating System** where:

- Every module (Tasks, Goals, Habits, Notes, Calendar, Documents) is fully connected with a live PostgreSQL database
- A **multi-provider AI agent** (OpenAI, Anthropic, Gemini, or Offline Heuristic) has tool-calling access to all modules
- A **Semantic Vector RAG engine** (cosine similarity on 1536-dim OpenAI embeddings or offline hash encoder) retrieves knowledge contextually
- A **mathematically explainable 0–100 Productivity Score** is computed across 5 weighted real dimensions — no black boxes
- A **365-day habit heatmap**, AI daily time-blocker, and AI weekly retrospective are all live and data-driven

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    PERSONALIX OS                             │
│                                                              │
│  Next.js 15 Frontend (TypeScript + Tailwind + Framer Motion) │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Dashboard │ Kanban │ Projects │ Goals │ Habits        │   │
│  │  Notes     │ Docs   │ Calendar │ Daily Plan │ Review   │   │
│  │  Analytics │ Memories │ AI Drawer │ Ctrl+K Palette    │   │
│  └───────────────────────────────────────────────────────┘   │
│                        │ REST + JSON                          │
│  FastAPI Backend (Python 3.13 + SQLAlchemy 2.0 Async)        │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Auth │ Tasks │ Projects │ Goals │ Habits │ Notes      │   │
│  │  Documents │ Calendar │ Daily Plans │ Weekly Reviews   │   │
│  │  Analytics │ AI Orchestrator │ Vector Service          │   │
│  └───────────────────────────────────────────────────────┘   │
│                        │                                      │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │PostgreSQL │  │  Redis Cache │  │  LLM Providers      │   │
│  │16+pgvector│  │   7 Alpine   │  │  OpenAI / Anthropic │   │
│  └───────────┘  └──────────────┘  │  Google Gemini      │   │
│                                   │  Offline Heuristic  │   │
│                                   └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## Core Feature Set

| Feature | Technical Depth |
|---|---|
| **Task Kanban + List** | Status pipeline (inbox → todo → in_progress → completed), subtasks, priority queuing, position ordering |
| **Project Portfolio** | Milestones, task-count aggregation, real-time progress calculation from linked tasks |
| **Strategic Goals** | 5 categories, milestone tracking, linked projects/tasks, progress rollup |
| **Habits + Heatmap** | 365-day GitHub-style heatmap, current/best streak algorithm, 30-day completion rate |
| **Knowledge Notes** | Markdown editor, tag management, pinning, full-text search |
| **Vector RAG Documents** | OpenAI text-embedding-3-small / offline 1536-dim hash encoder, chunk overlap, cosine similarity |
| **Calendar + Focus** | Time-block scheduling, event type classification, daily agenda overlay |
| **AI Daily Planner** | Algorithm-based time-blocking (working hours, priority tasks, habit reminders, breaks) |
| **AI Weekly Retrospective** | Auto-synthesized wins, bottlenecks, and recommendations from live data |
| **Explainable Productivity Score** | 5-dimension weighted composite: Tasks(25%) + Goals(20%) + Focus(20%) + Habits(20%) + Deadlines(15%) |
| **AI Long-Term Memory** | Auto-extracted preferences/facts from conversations, manual memory pinning |
| **Multi-Provider AI Agent** | OpenAI GPT-4o-mini, Anthropic Claude 3.5 Sonnet, Google Gemini 1.5 Flash, Offline Heuristic Engine |
| **AI Tool Calling** | 11 dispatched tools: create task, update goal, log habit, search knowledge, get schedule, and more |
| **Ctrl+K Command Palette** | Global fuzzy search + semantic RAG search + AI prompt launcher |

---

## Tech Stack

### Backend
- **Python 3.13** + **FastAPI 0.115** (async)
- **SQLAlchemy 2.0** (async, declarative mapped columns)
- **PostgreSQL 16** with **pgvector** extension (falls back to SQLite for development)
- **Alembic** migrations ready
- **JWT** authentication (access + refresh tokens)
- **PBKDF2-SHA256** password hashing (no bcrypt dependency)
- **Pydantic V2** schema validation

### AI & Embeddings
- **OpenAI** text-embedding-3-small + GPT-4o-mini tool calling
- **Anthropic** Claude 3.5 Sonnet
- **Google Gemini** 1.5 Flash
- **Offline Heuristic Engine** — fully functional without any API keys
- **Cosine similarity** vector search on 1536-dimensional embeddings

### Frontend
- **Next.js 15** (App Router, Server Components)
- **TypeScript 5.7** with strict mode
- **Tailwind CSS 3.4** + custom design system (dark glassmorphism)
- **TanStack Query v5** (server state, caching, optimistic updates)
- **Framer Motion 11** (page transitions, micro-animations)
- **Recharts 2** (analytics visualizations)
- **Lucide React** icons

### Infrastructure
- **Docker Compose** (PostgreSQL 16 + pgvector, Redis 7, FastAPI, Next.js)
- Structured **request-ID** logging middleware
- Unified exception hierarchy with proper HTTP codes

---

## Quick Start

### Option 1: Docker Compose (Full Stack)

```bash
git clone https://github.com/yourname/personalix-os
cd personalix-os

cp .env.example .env
# Edit .env — add your API keys (optional, offline mode works too)

docker compose up -d
```

Open [http://localhost:3000](http://localhost:3000) and click **"Try Demo Account"**.

---

### Option 2: Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Copy and configure environment
cp ../.env.example ../.env

# Start the API server (SQLite auto-used if no DB configured)
python -m uvicorn app.main:app --reload --port 8000

# Seed demo data
python -c "import asyncio; from app.db.seed import seed_demo_data; asyncio.run(seed_demo_data())"
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

**Demo Credentials:**
- Email: `demo@personalix.os`
- Password: `demo1234`
- Or click **"Try Demo Account"** for one-click login

---

## Environment Variables

See [`.env.example`](.env.example) for all configuration options.

Key variables:

```env
# Database (PostgreSQL recommended, SQLite auto-used as fallback)
DATABASE_URL=postgresql+asyncpg://personalix:personalix@localhost:5432/personalix

# JWT Security
JWT_SECRET=your-super-secret-jwt-key

# AI Providers (all optional — offline heuristic engine works without any keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...

# Default AI provider: openai | anthropic | gemini | fallback
DEFAULT_AI_PROVIDER=fallback
```

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

All 8 test modules pass:
- `test_auth.py` — Registration, login, JWT validation
- `test_tasks.py` — Full task lifecycle, subtasks
- `test_projects_goals.py` — Projects and goals with milestones
- `test_habits.py` — Habit logging, streak algorithms
- `test_notes_knowledge.py` — Notes and vector document search
- `test_ai_orchestrator.py` — AI multi-turn conversation and tool dispatch
- `test_analytics.py` — Productivity score computation
- (health check implicit)

---

## Project Structure

```
personalix-os/
├── backend/
│   ├── app/
│   │   ├── ai/              # LLM providers, tool dispatcher, orchestrator
│   │   ├── api/v1/          # FastAPI endpoint routers
│   │   ├── core/            # Config, security, logging, exceptions
│   │   ├── db/              # Session, seed data
│   │   ├── models/          # SQLAlchemy ORM models (13 tables)
│   │   ├── schemas/         # Pydantic V2 request/response schemas
│   │   └── services/        # Business logic (11 service modules)
│   └── tests/               # Pytest async test suite
├── frontend/
│   └── src/
│       ├── app/             # Next.js App Router pages
│       │   ├── (dashboard)/ # Protected dashboard routes
│       │   └── login/       # Auth pages
│       ├── components/      # Shared UI components
│       └── lib/             # API client, TypeScript types
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## What Makes This Resume-Worthy?

1. **Not a tutorial clone** — original architecture decisions throughout
2. **Real AI integration** — multi-provider with graceful offline fallback, actual tool calling
3. **Production patterns** — async SQLAlchemy, JWT refresh tokens, structured logging, request IDs
4. **Semantic search** — actual cosine similarity on 1536-dim vector embeddings
5. **Explainable ML** — productivity score with mathematical breakdown, no black boxes
6. **Full test coverage** — 8 passing async pytest modules
7. **Docker-ready** — one-command deployment

---

## License

MIT License — free to use, modify, and showcase.

---

<div align="center">
Built with FastAPI + Next.js + PostgreSQL + pgvector + OpenAI/Anthropic/Gemini
</div>
