# Personalix OS — Deployment Guide

## Option 1: Docker Compose (Recommended)

### Prerequisites
- Docker Desktop 24+
- Docker Compose v2

### Steps

```bash
git clone https://github.com/anshspc/ansh-OS.git
cd ansh-OS

# Copy and configure environment
cp .env.example .env
# Edit .env — set JWT_SECRET at minimum. All others are optional.

# Start all services
docker compose up -d

# Verify all containers are healthy
docker compose ps

# Seed demo data
docker compose exec api python -c \
  "import asyncio; from app.db.seed import seed_demo_data; asyncio.run(seed_demo_data())"
```

Open **http://localhost:3000** and click **Try Demo Account**.

### Services

| Service | Port | Description |
|---|---|---|
| `web` | 3000 | Next.js frontend |
| `api` | 8000 | FastAPI backend |
| `db` | 5432 | PostgreSQL 16 + pgvector |
| `redis` | 6379 | Redis 7 (caching) |

---

## Option 2: Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env (JWT_SECRET is required; all AI keys are optional)

# Start API server
python -m uvicorn app.main:app --reload --port 8000

# Optional: seed demo data
python -c "import asyncio; from app.db.seed import seed_demo_data; asyncio.run(seed_demo_data())"
```

API docs: **http://localhost:8000/docs**

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev
# → http://localhost:3000

# Production build (verify before deploying)
npm run build
```

---

## Environment Variables

All variables with defaults work out of the box. Only `JWT_SECRET` is required for production.

```env
# ── Required ────────────────────────────────────────────────────
JWT_SECRET=change-this-in-production-use-a-long-random-string

# ── Database ─────────────────────────────────────────────────────
# Defaults to SQLite in development — set for PostgreSQL in production
DATABASE_URL=postgresql+asyncpg://personalix:personalix@localhost:5432/personalix

# ── Redis ────────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ── AI Providers (all optional — offline fallback works without any) ──
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
DEFAULT_AI_PROVIDER=fallback      # openai | anthropic | gemini | fallback

# ── App ──────────────────────────────────────────────────────────
APP_ENV=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

---

## Production Deployment (Cloud)

### nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","database":"connected","version":"1.0.0"}
```

### Running Tests

```bash
# Backend
cd backend
python -m pytest tests/ -v

# Expected: 17 passed
```
