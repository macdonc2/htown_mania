# Agentic System Quick Reference

**Houston Event Mania - AI-Powered Event Discovery with Multi-Agent Orchestration**

---

## 🎯 What Is This?

A **State-of-the-Art multi-agent system** that discovers Houston events, validates them, and generates high-energy wrestling promos. Uses the **REACT pattern** (Reasoning + Acting) for transparent, adaptive decision-making.

---

## 📊 System Architecture

![Architecture Diagram](./architecture_diagram.png)

**Key Components**:

```
Planning Agent (Brain)
    ↓
├─ Search Agents (Parallel)
│  ├─ Ticketmaster
│  ├─ Meetup
│  └─ SerpAPI (Google Events)
│
├─ Review Swarm (Parallel)
│  ├─ Web Search Enricher
│  ├─ Content Enricher
│  ├─ Relevance Scorer
│  └─ Date Verifier
│
└─ Promo Generator
```

---

## 🔄 Process Flow

![Process Flow Diagram](./process_flow_diagram.png)

**Execution Phases**:

1. **INITIALIZING** → Setup state
2. **SEARCHING** → Parallel search (3 agents simultaneously)
3. **REVIEWING** → Parallel validation (4 agents per event, 5 concurrent)
4. **SYNTHESIZING** → Promo generation with GPT-4o
5. **COMPLETE** → Save to DB, send SMS

**Total Time**: 10-15 seconds end-to-end

---

## 🤖 Agents Overview

| Agent | Role | Technology | Confidence |
|-------|------|------------|-----------|
| **Planning Agent** | Orchestrator | PydanticAI + GPT-4o | Variable |
| **Ticketmaster Agent** | Search | Ticketmaster API | 0.9 |
| **Meetup Agent** | Search | Meetup GraphQL | 0.8 |
| **SerpAPI Agent** | Search | Google Events | 0.95 |
| **Web Search Enricher** | Validation | SerpAPI + GPT-4o-mini | 0.85 |
| **Content Enricher** | Enrichment | Scraping + GPT-4o-mini | 0.9 |
| **Relevance Scorer** | Scoring | Domain Keywords | 1.0 |
| **Date Verifier** | Validation | Timezone Logic | 1.0 |
| **Promo Generator** | Synthesis | PydanticAI + GPT-4o | 0.95 |

---

## 🧠 REACT Pattern Explained

**R**eason → **A**ct → **C**heck → **T**rack

```
[1] Thought: "Need to search for events"
[2] Action: invoke_parallel_search_agents
[3] Observation: "Found 45 events from 3 sources"
[4] Thought: "Some events need verification"
[5] Action: invoke_review_swarm
[6] Observation: "38/45 verified with avg confidence 0.87"
[7] Thought: "Ready to generate promo"
[8] Action: invoke_promo_agent
[9] Observation: "Promo generated successfully"
```

Every decision is **logged** in the scratchpad for full transparency.

---

## 🚀 Running the System

```bash
# Run agentic workflow
uv run python -m app.workers.run_daily_job --agentic

# Or via API
curl -X POST http://localhost:8000/api/events/trigger-agentic-flow
```

---

## 📈 Example Output

```
🤖 STARTING AGENTIC EVENT WORKFLOW
================================================================================

🔍 Running search agents in parallel...
  ✅ SerpAPI: 30 events in 2.8s (conf: 0.95)
  ✅ Ticketmaster: 18 events in 2.1s (conf: 0.90)
  ✅ Meetup: 12 events in 1.9s (conf: 0.80)
  
📊 Found 45 unique events

🔬 Running review swarm on 45 events...
  ✅ Houston Cycling Meetup | 4/4 | relevance:✅ date:✅ web:✅ content:✅
  ✅ Live Music at White Oak | 4/4 | relevance:✅ date:✅ web:✅ content:✅
  ❌ Kids Birthday Party    | 1/4 | relevance:❌ date:✅ web:✅ content:❌
  ...

📊 Verified: 38/45 events (avg confidence: 0.87)

🎤 Generating wrestling promo...

✅ AGENTIC WORKFLOW COMPLETE
================================================================================
📊 Stats:
  - Events found: 45
  - Events reviewed: 45
  - Search sources: SerpAPI, Ticketmaster, Meetup
  - Verified events: 38/45
  - Avg confidence: 0.87
  - Observations logged: 12
================================================================================
```

---

## 🎨 Key Features

### ⚡ Speed
- **Parallel search**: All sources queried simultaneously
- **Concurrent review**: 5 events processed at once
- **Total time**: 10-15 seconds

### 🔍 Accuracy
- **Multi-agent validation**: 4 independent agents per event
- **Majority voting**: Consensus-based verification
- **Confidence scoring**: Every decision has a score

### 🪟 Transparency
- **Complete REACT trace**: Every thought, action, observation logged
- **Scratchpad**: Full decision-making history
- **Agent voting**: See which agents verified which events

### 🛡️ Resilience
- **Graceful degradation**: Continues if agents fail
- **Partial results**: Uses what's available
- **Error logging**: Clear failure tracking

### 🔧 Extensibility
- **Add agents**: Simply implement the port interface
- **Swap implementations**: DI makes it easy
- **Configure concurrency**: Tune for your needs

---

## 🏗️ Architecture Principles

### Hexagonal Architecture
```
Domain (Core)
    ↓
Ports (Interfaces)
    ↓
Adapters (Implementations)
```

### SOTA Patterns
- ✅ REACT (Reasoning + Acting)
- ✅ Chain-of-Thought prompting
- ✅ Parallel agent orchestration
- ✅ Tool-augmented agents
- ✅ Confidence scoring
- ✅ Graceful degradation

### Design Patterns
- ✅ Dependency Injection
- ✅ Repository Pattern
- ✅ Strategy Pattern (agents)
- ✅ Observer Pattern (scratchpad)

---

## 📚 Full Documentation

| Document | Description |
|----------|-------------|
| [AGENTIC_SYSTEM_OVERVIEW.md](./AGENTIC_SYSTEM_OVERVIEW.md) | Complete technical documentation |
| [AGENTIC_ARCHITECTURE.md](./AGENTIC_ARCHITECTURE.md) | Architecture deep dive |
| [AGENTIC_USAGE_GUIDE.md](./AGENTIC_USAGE_GUIDE.md) | How-to guide |
| [AGENTIC_DIAGRAMS_README.md](./AGENTIC_DIAGRAMS_README.md) | Diagram reference |

---

## 🧪 Testing

```bash
# All agentic tests
pytest tests/unit/agents tests/contract/agents tests/integration/agents

# By type
pytest tests/unit/agents -m unit
pytest tests/contract/agents -m contract
pytest tests/integration/agents -m integration
```

---

## 🎯 Benefits Over Traditional Approach

| Aspect | Traditional | Agentic |
|--------|------------|---------|
| **Search** | Sequential (slow) | Parallel (fast) |
| **Validation** | Basic filters | Multi-agent swarm |
| **Reasoning** | None (black box) | REACT with scratchpad |
| **Transparency** | No trace | Complete trace |
| **Adaptability** | Fixed pipeline | Adaptive decisions |
| **Error Handling** | Fail fast | Graceful degradation |
| **Execution Time** | 15-20s | 10-12s |

---

## 🔑 Key Metrics

- **Events Discovered**: 30-50 per run
- **Search Time**: 2-5 seconds (parallel)
- **Review Time**: 5-8 seconds (concurrent)
- **Synthesis Time**: 3-5 seconds
- **Total Time**: 10-15 seconds
- **Verification Rate**: ~80-90%
- **Avg Confidence**: 0.85-0.90

---

## 🌟 Why This Is SOTA

1. **REACT Pattern**: Transparent reasoning and decision-making
2. **Parallel Execution**: Maximum speed through concurrency
3. **Multi-Agent Validation**: Consensus-based verification
4. **Confidence Scoring**: Quantified certainty for all decisions
5. **Complete Observability**: Full trace of all actions
6. **Graceful Degradation**: Resilient to failures
7. **Hexagonal Architecture**: Clean separation of concerns
8. **Tool-Augmented**: Agents use external tools effectively

---

## 🔮 Future Enhancements

- [ ] Self-consistency (multiple inference passes)
- [ ] Reflection (agents review their own work)
- [ ] Long-term memory across runs
- [ ] Multi-modal (image analysis)
- [ ] User feedback loop
- [ ] Cost optimization (LLM call caching)

---

## 📞 Quick Help

**Need to add a new search agent?**
1. Implement `SearchAgentPort`
2. Add to `search_agents` list in DI
3. Done!

**Need to add a new review agent?**
1. Implement `ReviewAgentPort`
2. Add to `review_agents` list in DI
3. Done!

**Adjust concurrency?**
```python
enriched_events = await run_review_swarm(
    events=state.events_found,
    agents=self.review_agents,
    max_concurrent=10  # Increase for speed
)
```

---

**For detailed architecture, see:**
- [Architecture Diagram](./architecture_diagram.png)
- [Process Flow Diagram](./process_flow_diagram.png)
- [Complete Documentation](./AGENTIC_SYSTEM_OVERVIEW.md)

