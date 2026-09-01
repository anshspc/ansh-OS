# Personalix OS — System Architecture

## Overview

Personalix OS is a full-stack AI-native personal operating system. It uses a clean separation between a FastAPI async backend and a Next.js 15 frontend, communicating via a versioned REST API.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                            │
│                                                                  │
│  Next.js 15 (App Router)  ·  TypeScript 5.7  ·  Tailwind CSS    │
│  TanStack Query  ·  Framer Motion  ·  Web Speech API            │
│                                                                  │
│  Pages: Dashboard · Tasks · Projects · Goals · Habits            │
│         Notes · Documents · Calendar · Daily Plan                │
│         Weekly Review · Analytics · AI Memory · Voice            │
└──────────────────────┬───────────────────────────────────────────┘
                       │  REST JSON  (HTTP / HTTPS)
                       │  Next.js API proxy → http://localhost:8000
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                            │
│                                                                  │
│  Python 3.13 · FastAPI 0.115 · SQLAlchemy 2.0 (async)           │
│  Pydantic V2 · JWT Auth · Structured Logging                     │
│                                                                  │
│  Routers                                                         │
│  ├── /auth          JWT login, register, demo, refresh           │
│  ├── /tasks         CRUD + subtasks + ordering                   │
│  ├── /projects      Portfolio + milestones                       │
│  ├── /goals         Strategic goals + milestone tracking         │
│  ├── /habits        Logging + streak algorithm                   │
│  ├── /notes         Markdown notes + tag management              │
│  ├── /documents     RAG ingestion + chunk management             │
│  ├── /calendar      Events + time-block scheduling               │
│  ├── /daily-plans   AI-generated time blocks                     │
│  ├── /weekly-reviews AI retrospectives                           │
│  ├── /ai            Chat · Conversations · Memory                │
│  ├── /analytics     Productivity score + activity feed           │
│  └── /voice         Voice chat · Settings · History              │
└──────────────────────┬───────────────────────────────────────────┘
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
   ┌─────────────┐  ┌──────┐  ┌──────────────┐
   │ PostgreSQL  │  │Redis │  │  LLM APIs    │
   │ 16+pgvector │  │  7   │  │  OpenAI      │
   │             │  │      │  │  Anthropic   │
   │ 13 tables   │  │Cache │  │  Gemini      │
   └─────────────┘  └──────┘  │  Fallback    │
                               └──────────────┘
```

## Backend Layer Design

### API Layer (`app/api/v1/`)
- Versioned routing under `/api/v1/`
- Per-router files, each owning one domain
- Dependency injection via `Depends()` for auth and DB session

### Service Layer (`app/services/`)
- Business logic isolated from HTTP concerns
- Async-first: all service methods are `async def`
- No direct ORM access from routers

### Model Layer (`app/models/`)
- SQLAlchemy 2.0 `DeclarativeBase` + `Mapped[T]` typed columns
- 13 tables covering the full data model
- `selectinload()` used for relationship loading (avoids `MissingGreenlet` in async context)

### AI Layer (`app/ai/`)
- `llm_provider.py`: Provider abstraction (OpenAI / Anthropic / Gemini / Fallback)
- `tools.py`: 11 structured tool definitions + async dispatcher
- `orchestrator.py`: Multi-turn conversation manager with tool loop

### Voice Layer (`app/voice/`)
- `voice_router.py`: Transcript → context enrichment → AI → clean TTS reply
- `voice_config.py`: Per-user voice settings schema
- `voice_session.py`: Session state tracking

## Frontend Layer Design

### Routing
- Next.js 15 App Router
- `(dashboard)` route group wraps all authenticated pages
- `layout.tsx` composes: Sidebar + Header + CommandPalette + AIDrawer + VoiceProvider

### State Management
- **Server state**: TanStack Query v5 (`staleTime: 30s`, `refetchOnWindowFocus: false`)
- **UI state**: React `useState` / `useReducer` in component scope
- **Voice state**: React Context (`VoiceContext`) with Web Speech API

### API Communication
- `src/lib/api.ts`: Singleton `ApiClient` class
- All requests include `Authorization: Bearer <token>` header
- Token stored in `localStorage` as `personalix_token`

## Data Flow Examples

### Voice Command → Database Update
```
User speaks → SpeechRecognition → transcript string
  → POST /api/v1/voice/chat { transcript, screen_context }
    → voice_router.py enriches with page context
    → AIOrchestrator.process_chat()
      → LLM generates tool call: { name: "create_task", args: {...} }
      → ToolDispatcher.execute("create_task", args)
        → TaskService.create_task(db, user, payload)
          → INSERT INTO tasks ...
      → LLM generates reply: "Done. Task created for tomorrow."
      → _strip_markdown_for_tts(reply)
    → VoiceChatResponse { reply, tool_calls, conversation_id }
  → Browser SpeechSynthesis.speak(reply)
User hears spoken confirmation
```

### Vector Search → Knowledge Answer
```
User types query → POST /api/v1/documents/search { query }
  → VectorService.search(db, user, query)
    → Embed query (OpenAI text-embedding-3-small OR offline hash encoder)
    → SELECT chunks ORDER BY cosine_similarity DESC LIMIT 5
    → Return top-5 chunks with scores
  → Display results with similarity percentage
```

## Security Design

- Passwords: PBKDF2-SHA256 with salt (no bcrypt dependency)
- JWT: RS256 compatible, includes `jti` (UUID4) per token → prevents UNIQUE constraint on refresh tokens
- Sessions: Refresh tokens stored in `user_sessions` table with expiry
- CORS: Configured for `localhost:3000` in dev; env-configurable for production
- No secrets in code: all via environment variables

## Deployment Topology

```
Internet → Nginx (SSL termination)
              ├── /         → Next.js (port 3000)
              └── /api/v1/  → FastAPI (port 8000)

FastAPI → PostgreSQL (port 5432)
FastAPI → Redis (port 6379)
FastAPI → External LLM APIs (optional)
```
