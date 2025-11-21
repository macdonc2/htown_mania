# HOUSTON EVENT MANIA — Full Power 🎤💪🔥
Created by Cody *Macho Madness* MacDonald

**Multi-Agent AI System for Houston Event Discovery & Wrestling Promo Generation**

Mission: 7:00 AM CST daily — intelligent event discovery, deep research, wrestling-style promos, SMS/Email delivery.  
Ingress: https://events.macdoncml.com  
Arch: Hexagonal (ports/adapters), Multi-Agent AI (PydanticAI), FastAPI, PostgreSQL, Docker, K8s.

## 📚 Documentation

**→ [⚡ Quick Start Guide](./docs/QUICK_START.md)** - Get running in 5 minutes!  
**→ [Complete Documentation Index](./docs/README.md)** - All docs organized

Quick links:
- **[Quick Start](./docs/QUICK_START.md)** - ⚡ 5 minute setup
- **[Usage Guide](./docs/DEEP_RESEARCH_USAGE.md)** - All commands & flags
- **[Architecture](./docs/DEEP_RESEARCH_AGENT_DESIGN.md)** - System design
- **[Deployment](./docs/DEPLOYMENT_GUIDE.md)** - Production setup
- **[Changelog](./docs/CHANGELOG.md)** - What's new

## 🚀 Quick Start (Local - No Database)

```bash
# 1. Setup environment
cp .env.example .env  # Add your API keys (OpenAI, SerpAPI)

# 2. Install dependencies
uv sync

# 3. Run deep research system (no PostgreSQL needed!)
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

This will:
- ✅ Discover 20-30 Houston events
- ✅ Extract entities & generate research queries  
- ✅ Research events via web search
- ✅ Generate wrestling promo
- ✅ Send email with results
- ❌ Skip database (no setup required!)

## 🎛️ Command Modes

```bash
# Deep research with email (no database)
uv run python -m app.workers.run_daily_job --deep-research --no-db

# Include Reddit events (opt-in, can be noisy)
uv run python -m app.workers.run_daily_job --deep-research --no-db --reddit

# Full production mode (requires PostgreSQL)
uv run python -m app.workers.run_daily_job --deep-research

# Testing mode (no side effects)
uv run python -m app.workers.run_daily_job --deep-research --dry-run
```

See [DEEP_RESEARCH_USAGE.md](./docs/DEEP_RESEARCH_USAGE.md) for all flags and options.

## Quickstart (Local)
```bash
cp .env.example .env  # fill me
docker run --name hem-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=events -p 5432:5432 -d postgres:16
uv sync
uv run alembic upgrade head
uv run uvicorn app.api.main:app --reload
uv run python -m app.workers.run_daily_job
```

## Env (.env)
```
EVENTS_OPENAI_API_KEY=sk-...
EVENTS_OPENAI_MODEL=gpt-4o-mini
EVENTS_TWILIO_ACCOUNT_SID=AC...
EVENTS_TWILIO_AUTH_TOKEN=...
EVENTS_TWILIO_FROM_NUMBER=+1...
EVENTS_SMS_RECIPIENT=+1...
EVENTS_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/events
EVENTS_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
EVENTS_GOOGLE_CLIENT_SECRET=xxx
EVENTS_ALLOWED_EMAILS="you@gmail.com"
EVENTS_APP_BASE_URL=http://localhost:8000
EVENTS_SESSION_SECRET=<openssl rand -hex 32>
DEV_SMS_MUTE=0
FRONTEND_MODE=html
```

## Dev UX
- HTML front at `/` (Jinja+HTMX).  
- React Neon (stub) at `/neon` as static bundle placeholder (no build step required for dev).  
- Cron @ 7AM CST via K8s CronJob (timeZone=America/Chicago).

## AKS (raw manifests)
```bash
kubectl create ns events || true
kubectl -n events create secret generic houston-event-mania-secrets --from-env-file=.env
kubectl -n events apply -f infra/k8s/
```

## Helm
```bash
helm upgrade --install hem charts/houston-event-mania   --namespace events --create-namespace   --set image.repository=ghcr.io/<you>/houston-event-mania   --set image.tag=latest   --set ingress.host=events.macdoncml.com   --set envFromSecret=houston-event-mania-secrets
```

## Make
```
make dev      # api
make job      # run daily worker
make lint     # ruff
make format   # black
make k-port-forward
```

## 🏗️ Architecture

**Multi-Agent AI System** with Hexagonal (Ports & Adapters) architecture:

```
┌──────────────────────────────────────────────┐
│           PLANNING AGENT (GPT-4o)            │
│         Orchestrates REACT Loop              │
└──────────────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
SEARCHING        REVIEWING       RESEARCHING
                                 
• SerpAPI        • Relevance     • Entity Extract
• Ticketmaster   • Date Check    • Query Gen
• Reddit (opt)   • Web Enrich    • Web Research
                 • Content       • Synthesis
    │                ▼                │
    └────────────→ SYNTHESIZING ←────┘
                       │
                 Promo Generator
                 Email/SMS/DB
```

### Agent Stack

**Core Orchestration**: Planning Agent (GPT-4o) coordinates everything  
**Search**: 3 parallel agents (SerpAPI, Ticketmaster, Reddit optional)  
**Review**: 4 parallel agents validate and enrich events  
**Research**: 4 agents extract entities, generate queries, research, synthesize  
**Output**: Promo Generator creates wrestling-style event promos

**Framework**: [PydanticAI](https://ai.pydantic.dev/) for structured AI workflows

See [Architecture Docs](./docs/DEEP_RESEARCH_AGENT_DESIGN.md) for details.

## 🔬 Tech Stack

| Layer | Technology |
|-------|------------|
| **AI** | OpenAI GPT-4o/mini, PydanticAI |
| **APIs** | SerpAPI, Ticketmaster, NewsAPI |
| **Backend** | Python 3.12, FastAPI, Pydantic |
| **Database** | PostgreSQL, SQLAlchemy, Alembic |
| **Messaging** | Twilio SMS, Gmail SMTP |
| **Infra** | Docker, Kubernetes, Helm |

## 🎤 Sample Output

**Input**: 24 Houston events  
**Output**: Wrestling promo like:

> 🎤 OHHH YEAHHH! The CREAM of the Houston scene rises to the TOP this weekend, brother! 
> Mac Miller tribute with THUNDERCAT at White Oak Music Hall - the bass lines are GONNA 
> SNAP INTO A SLIM JIM! Houston Rockets SLAM the Magic at Toyota Center - nothing means 
> nothing if you ain't got the three-pointer, YEAH! Jazz at Lincoln Center with Wynton 
> Marsalis bringing the BRASS and the CLASS to Jones Hall! DIG IT! 💪🔥

## 📊 Stats

- **Events**: 20-30 per day (SerpAPI + Ticketmaster)
- **Agents**: 12 specialized AI agents
- **Models**: GPT-4o (orchestration), GPT-4o-mini (extraction/queries)
- **Latency**: 2-3 minutes end-to-end
- **Cost**: ~$0.10-0.20 per run (OpenAI + SerpAPI)

---

**OHHH YEAHHH, BROTHER! The cream rises to the top!** 🎤💪🔥
