# Houston Event Mania - Documentation Index

**Complete documentation for the Houston Event Mania multi-agent AI system.**

---

## 🚀 Quick Start

**New User?** Start here:
1. [QUICK_START.md](./QUICK_START.md) - **⚡ Get running in 5 minutes!** (START HERE!)
2. [DEEP_RESEARCH_USAGE.md](./DEEP_RESEARCH_USAGE.md) - Complete usage guide
3. [SERPAPI_SETUP.md](./SERPAPI_SETUP.md) - Setup API keys
4. [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Deploy to production

---

## 📚 Documentation Categories

### 🎯 Usage & Operations

| Document | Purpose | Audience |
|----------|---------|----------|
| [QUICK_START.md](./QUICK_START.md) | **⚡ Get running in 5 minutes!** | **New Users** |
| [DEEP_RESEARCH_USAGE.md](./DEEP_RESEARCH_USAGE.md) | Complete usage guide with all flags | Everyone |
| [AGENTIC_USAGE_GUIDE.md](./AGENTIC_USAGE_GUIDE.md) | Base agentic system usage | Everyone |
| [AGENTIC_QUICK_REFERENCE.md](./AGENTIC_QUICK_REFERENCE.md) | Quick command reference | Everyone |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Production deployment (K8s, Docker) | DevOps |
| [CHANGELOG.md](./CHANGELOG.md) | Version history and changes | Everyone |

### 🏗️ Architecture & Design

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEEP_RESEARCH_AGENT_DESIGN.md](./DEEP_RESEARCH_AGENT_DESIGN.md) | Deep research system design | Developers |
| [AGENTIC_ARCHITECTURE.md](./AGENTIC_ARCHITECTURE.md) | Base agentic architecture | Developers |
| [AGENTIC_SYSTEM_OVERVIEW.md](./AGENTIC_SYSTEM_OVERVIEW.md) | System overview | Product/Tech Leads |

### 🔧 Implementation Guides

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md](./DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md) | How to build deep research | Developers |
| [SERPAPI_SETUP.md](./SERPAPI_SETUP.md) | SerpAPI configuration | Everyone |
| [SERPAPI_SOLUTION.md](./SERPAPI_SOLUTION.md) | SerpAPI technical details | Developers |

### 📊 Diagrams

| Diagram | Description | View |
|---------|-------------|------|
| [architecture_diagram.png](./architecture_diagram.png) | Full system architecture | High-level |
| [deep_research_architecture.png](./deep_research_architecture.png) | Deep research agents | Research system |
| [deep_research_flow.png](./deep_research_flow.png) | Research workflow | Process flow |
| [process_flow_diagram.png](./process_flow_diagram.png) | Base agentic flow | Base system |
| [AGENTIC_DIAGRAMS_README.md](./AGENTIC_DIAGRAMS_README.md) | How to generate diagrams | Maintainers |

### 🎤 Special Features

| Document | Purpose | Audience |
|----------|---------|----------|
| [WRESTLING_TTS_GUIDE.md](./WRESTLING_TTS_GUIDE.md) | Text-to-speech wrestling promos | Fun! |

---

## 🎯 Common Tasks

### "I want to run the system locally"
→ [DEEP_RESEARCH_USAGE.md](./DEEP_RESEARCH_USAGE.md)
```bash
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

### "I want to understand the architecture"
→ [DEEP_RESEARCH_AGENT_DESIGN.md](./DEEP_RESEARCH_AGENT_DESIGN.md) + [architecture_diagram.png](./architecture_diagram.png)

### "I want to deploy to production"
→ [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

### "I want to add a new agent"
→ [DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md](./DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md)

### "I need API keys"
→ [SERPAPI_SETUP.md](./SERPAPI_SETUP.md)

### "I hit a rate limit"
→ [DEEP_RESEARCH_USAGE.md#common-issues](./DEEP_RESEARCH_USAGE.md#common-issues)

---

## 🏛️ System Architecture

The Houston Event Mania system uses a **Hexagonal (Ports & Adapters)** architecture with a **multi-agent AI** orchestration layer:

```
┌──────────────────────────────────────────────────────────────┐
│                     PLANNING AGENT                           │
│            (Orchestrates REACT Loop)                         │
└──────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   SEARCHING              REVIEWING            RESEARCHING
   
   • SerpAPI              • Relevance          • Entity Extract
   • Ticketmaster         • Date Check         • Query Gen
   • Reddit (opt)         • Web Enrich         • Web Research
                          • Content            • Synthesis
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                       SYNTHESIZING
                       
                    • Promo Generator
                    • Email/SMS
                    • Database
```

---

## 🔬 Agent Types

### Core Agents

| Agent | Model | Purpose | Phase |
|-------|-------|---------|-------|
| Planning Agent | GPT-4o | Orchestrates workflow | All |
| Promo Generator | GPT-4o | Generates wrestling promos | Synthesizing |

### Search Agents (Parallel)

| Agent | API | Events | Default |
|-------|-----|--------|---------|
| SerpAPI Events | SerpAPI | 10-15 | ✅ |
| Ticketmaster | Ticketmaster | 10-15 | ✅ |
| Reddit Events | Scraping | 100+ | ❌ (opt-in) |

### Review Agents (Parallel Swarm)

| Agent | Purpose | Model/API |
|-------|---------|-----------|
| Relevance Scorer | Check Houston relevance | Heuristics |
| Date Verifier | Validate dates | Heuristics |
| Web Search Enricher | Add context from web | SerpAPI + GPT |
| Content Enricher | Enhance descriptions | GPT-4o |

### Research Agents (Deep Research)

| Agent | Model | Purpose |
|-------|-------|---------|
| Entity Extractor | GPT-4o-mini | Extract artists, venues, etc |
| Query Generator | GPT-4o-mini | Generate research queries |
| Web Search Researcher | SerpAPI | Find facts via Google |
| Knowledge Synthesizer | GPT-4o | Create narratives |

---

## 🎛️ Command Reference

```bash
# Basic modes
uv run python -m app.workers.run_daily_job                    # Original
uv run python -m app.workers.run_daily_job --agentic         # Multi-agent
uv run python -m app.workers.run_daily_job --deep-research   # Full research

# Testing flags
uv run python -m app.workers.run_daily_job --deep-research --no-db     # Skip DB
uv run python -m app.workers.run_daily_job --deep-research --dry-run   # Skip all
uv run python -m app.workers.run_daily_job --deep-research --reddit    # Add Reddit
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| **AI/ML** | OpenAI GPT-4o, GPT-4o-mini, PydanticAI |
| **APIs** | SerpAPI, Ticketmaster, NewsAPI |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy, Pydantic |
| **Database** | PostgreSQL, Alembic migrations |
| **Messaging** | Twilio SMS, Gmail SMTP |
| **Orchestration** | asyncio, httpx |
| **Infrastructure** | Docker, Kubernetes, Helm |
| **Observability** | Structured logging, scratchpad traces |

---

## 🧪 Testing Philosophy

- **Contract Tests**: Port interfaces
- **Integration Tests**: Agent workflows
- **Unit Tests**: Domain logic
- **E2E Tests**: Full pipeline

See: [Test rules in user rules](../README.md)

---

## 🔗 External Resources

- [PydanticAI Docs](https://ai.pydantic.dev/)
- [SerpAPI Docs](https://serpapi.com/docs)
- [Ticketmaster API](https://developer.ticketmaster.com/)
- [OpenAI API](https://platform.openai.com/docs)

---

## 📝 Contributing

When adding documentation:

1. **Usage guides** → `DEEP_RESEARCH_USAGE.md` or `AGENTIC_USAGE_GUIDE.md`
2. **Architecture** → `DEEP_RESEARCH_AGENT_DESIGN.md` or `AGENTIC_ARCHITECTURE.md`
3. **Implementation** → `DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md`
4. **Diagrams** → Use Mermaid (`.mmd` files), generate PNG with `mmdc`
5. **Update this index** → Add new docs to the tables above

---

## 🎤 Final Word

**OHHH YEAHHH, BROTHER!** The cream rises to the top, and this documentation is CHAMPIONSHIP MATERIAL! 💪🔥

**DIG IT!**

---

*Last Updated: 2025-11-16*

