# Deep Research Agent System - Usage Guide

## 🎯 Overview

The Deep Research Agent System enhances event discovery with intelligent research:

1. **Searches** multiple sources (SerpAPI, Ticketmaster, Reddit optional)
2. **Reviews** events with a validation swarm
3. **Researches** events by extracting entities and gathering context
4. **Synthesizes** insights into compelling wrestling promos

---

## 🚀 Quick Start

### Basic Usage (No Database Required!)

```bash
# Deep research with email, no database (recommended for testing)
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

This will:
- ✅ Find ~24 curated events (SerpAPI + Ticketmaster)
- ✅ Extract entities (artists, venues, genres)
- ✅ Generate intelligent research queries
- ✅ Research entities via web search
- ✅ Synthesize insights
- ✅ Send email with promo
- ❌ Skip database save (no PostgreSQL needed)

---

## 🎛️ Command Flags

### Core Modes

| Flag | Description | Events | DB Save | Email |
|------|-------------|--------|---------|-------|
| _(none)_ | Original service | Varies | ✅ | ✅ |
| `--agentic` | Multi-agent (no research) | 20-30 | ✅ | ✅ |
| `--deep-research` | Full research system | 20-30 | ✅ | ✅ |

### Testing Flags

| Flag | Description | Use Case |
|------|-------------|----------|
| `--no-db` | Skip database, send email | Local testing without PostgreSQL |
| `--dry-run` | Skip DB and email | Pure workflow testing |
| `--reddit` | Include Reddit events | Add /r/houston weekly threads (noisy) |

### Flag Combinations

```bash
# Production: Full system with database
uv run python -m app.workers.run_daily_job --deep-research

# Local Dev: Skip DB, get email
uv run python -m app.workers.run_daily_job --deep-research --no-db

# Testing: Skip everything
uv run python -m app.workers.run_daily_job --deep-research --dry-run

# More Events: Include Reddit (can be noisy)
uv run python -m app.workers.run_daily_job --deep-research --no-db --reddit
```

---

## 📊 Event Sources

### Default Sources (24 events typical)

1. **SerpAPI (Google Events)** - 10-15 events
   - Aggregates from Google's event knowledge graph
   - High quality, well-structured data

2. **Ticketmaster** - 10-15 events
   - Major concerts, sports, theater
   - Reliable dates and venues

### Optional: Reddit (--reddit flag)

3. **Reddit /r/houston** - 100+ events
   - Community-curated weekly threads
   - **Warning**: Can be noisy, duplicative
   - **Default**: OFF (opt-in only)

**Recommendation**: Start without `--reddit`, add only if you want more volume.

---

## 🔬 Research Pipeline

### Phase 1: Entity Extraction
- **Agent**: `EntityExtractionAgent` (GPT-4o-mini)
- **Extracts**: Artists, venues, organizers, topics, genres
- **Example**:
  ```
  Event: "Mac Miller Tribute with Thundercat"
  Entities:
    - Mac Miller (artist, confidence: 0.95)
    - Thundercat (artist, confidence: 0.92)
    - White Oak Music Hall (venue, confidence: 0.88)
    - Hip-hop (genre, confidence: 0.85)
  ```

### Phase 2: Query Generation
- **Agent**: `QueryGenerationAgent` (GPT-4o-mini)
- **Generates**: Intelligent, targeted research queries
- **Example**:
  ```
  Queries:
    1. "What are Mac Miller's most iconic albums and cultural impact?" (priority: 10)
    2. "What collaborations did Mac Miller and Thundercat do?" (priority: 9)
    3. "What is White Oak Music Hall known for in Houston?" (priority: 7)
  ```

### Phase 3: Web Research
- **Agent**: `WebSearchResearchAgent` (SerpAPI)
- **Searches**: Google for each query
- **Extracts**: Facts, sources, snippets
- **Rate Limit**: 100 searches/hour (free tier)

### Phase 4: Knowledge Synthesis
- **Agent**: `KnowledgeSynthesisAgent` (GPT-4o)
- **Creates**: Coherent narratives from research facts
- **Output**: Rich context for promo generation

---

## ⚠️ Common Issues

### SerpAPI Rate Limit (429 Error)

**Symptom**:
```
⚠️  SerpAPI Error (Status 429): Rate limit exceeded
Researched 24 events: 82 entities, 0 facts, conf=0.50
```

**Solution**:
1. Wait for rate limit reset (hourly/daily)
2. Check usage: https://serpapi.com/account
3. Use `--agentic` mode (no research) as fallback

### No Email Received

**Check**:
1. Are you using `--dry-run`? (This skips email!)
2. Is `DEV_SMS_MUTE=1` in your `.env`? (Check logs)
3. Gmail app password correctly configured?

**Debug**:
```bash
# Run with --no-db to see email attempt
uv run python -m app.workers.run_daily_job --deep-research --no-db 2>&1 | grep -i "email\|sms"
```

### PostgreSQL Connection Error

**Symptom**:
```
OSError: Connect call failed ('127.0.0.1', 5432)
```

**Solution**: Use `--no-db` flag:
```bash
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

---

## 📈 Expected Output

### Without Reddit (--no-db)
```
Events: 24
Entities: 80-100
Research Queries: 60-80 (3-4 per event)
Facts: 200-300 (depends on SerpAPI quota)
Time: 2-3 minutes
```

### With Reddit (--no-db --reddit)
```
Events: 150-200
Entities: 400-600
Research Queries: 400-600
Facts: 800-1200 (may hit rate limits)
Time: 8-15 minutes
```

---

## 🎤 Promo Output

The final email includes:

1. **Wrestling Promo** (GPT-4o, temp=0.9)
   - Energetic, over-the-top style
   - Incorporates research insights
   - Macho Man / Ultimate Warrior energy

2. **Event Listing**
   - Clean, structured format
   - Date, time, venue, description
   - URLs for tickets

3. **Scratchpad** (Transparent AI)
   - All agent thoughts and observations
   - REACT pattern trace
   - Confidence scores and decisions

---

## 🛠️ API Keys Required

### Essential
- `OPENAI_API_KEY` - GPT-4o/mini for all agents
- `SERPAPI_KEY` - Event search + research

### Optional
- `TICKETMASTER_API_KEY` - Major event discovery
- `NEWSAPI_KEY` - News research (not yet implemented)

Add to `.env`:
```bash
OPENAI_API_KEY=sk-...
SERPAPI_KEY=...
TICKETMASTER_API_KEY=...
```

---

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PLANNING AGENT                        │
│              (Orchestrates Everything)                  │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   SEARCHING          REVIEWING          RESEARCHING
   
   SerpAPI            4 Agents in         Entity Extract
   Ticketmaster       Parallel:           ↓
   [Reddit]           • Relevance         Query Gen
                      • Date Check        ↓
                      • Web Enrich        Web Search
                      • Content           ↓
                                         Synthesis
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    SYNTHESIZING
                    
                  Promo Generator
                  (GPT-4o, Jinja2)
```

---

## 🎯 Best Practices

### For Production
```bash
# Full system with all safeguards
uv run python -m app.workers.run_daily_job --deep-research
```

### For Local Development
```bash
# Fast iteration, no DB needed
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

### For Testing
```bash
# No side effects
uv run python -m app.workers.run_daily_job --deep-research --dry-run
```

### When SerpAPI is Limited
```bash
# Fallback: Use regular agentic mode
uv run python -m app.workers.run_daily_job --agentic --no-db
```

---

## 🔗 Related Docs

- [DEEP_RESEARCH_AGENT_DESIGN.md](./DEEP_RESEARCH_AGENT_DESIGN.md) - Architecture details
- [DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md](./DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md) - Build guide
- [AGENTIC_USAGE_GUIDE.md](./AGENTIC_USAGE_GUIDE.md) - Base agentic system
- [SERPAPI_SETUP.md](./SERPAPI_SETUP.md) - API key setup

---

## 💡 Pro Tips

1. **Start Small**: Use `--no-db` for testing
2. **Monitor Costs**: Check OpenAI and SerpAPI usage
3. **Rate Limits**: Free SerpAPI = 100 searches/hour
4. **Reddit Toggle**: Only use `--reddit` if you need volume
5. **Dry Run**: Use `--dry-run` to test changes safely

---

**OHHH YEAHHH! The Deep Research Agent System is CHAMPIONSHIP-READY, BROTHER!** 🎤💪🔥

