# Agentic System Usage Guide

## Overview

The Houston Event Mania agentic system uses **PydanticAI** to orchestrate a multi-agent workflow for intelligent event discovery and promo generation.

## Quick Start

### Run the Agentic Workflow

```bash
# Run with the agentic system
uv run python -m app.workers.run_daily_job --agentic

# Run with the original system (for comparison)
uv run python -m app.workers.run_daily_job
```

### Trigger via API

```bash
# Start the API server
uv run uvicorn app.api.main:app --reload

# Trigger the agentic workflow
curl -X POST http://localhost:8000/api/events/trigger-agentic-flow
```

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Planning Agent (REACT)                      │
│  • Reasons about what to do next                        │
│  • Takes actions (invokes other agents)                 │
│  • Observes results                                      │
│  • Maintains scratchpad for transparency                │
└──────────────────┬───────────────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │ Phase 1: Parallel Search    │
    ├─────────────────────────────┤
    │ • Eventbrite Agent          │
    │ • Ticketmaster Agent        │
    │ • Meetup Agent              │
    │ All run in parallel         │
    └──────────────┬──────────────┘
                   │
    ┌──────────────┴──────────────┐
    │ Phase 2: Review Swarm       │
    ├─────────────────────────────┤
    │ • URL Validator             │
    │ • Content Enricher (LLM)    │
    │ • Relevance Scorer          │
    │ • Date Verifier             │
    │ All run in parallel         │
    └──────────────┬──────────────┘
                   │
    ┌──────────────┴──────────────┐
    │ Phase 3: Synthesis          │
    ├─────────────────────────────┤
    │ • Promo Generator Agent     │
    │   (Creates wrestling promo) │
    └─────────────────────────────┘
```

## Agents Explained

### Planning Agent

**Purpose:** Orchestrates the entire workflow using REACT pattern.

**REACT Loop:**
1. **Thought:** "I need to gather events from multiple sources"
2. **Action:** Invoke parallel search agents
3. **Observation:** "Found 45 events across 3 sources"
4. **Thought:** "Some events lack details, need verification"
5. **Action:** Generate questions and invoke review swarm
6. **Observation:** "All events validated"
7. **Thought:** "Ready to generate promo"
8. **Action:** Invoke promo generator
9. **Result:** Complete!

**Key Features:**
- Maintains a scratchpad of all observations
- Generates questions when data is uncertain
- Tracks confidence scores
- Decides when to move to next phase

### Search Agents (Parallel)

Each search agent specializes in one data source:

**Eventbrite Agent:**
- Queries Eventbrite API
- Filters to Houston area (50 mile radius)
- Extracts venue, date, categories
- Returns structured Event objects

**Ticketmaster Agent:**
- Queries Ticketmaster Discovery API
- Focuses on Houston, TX events
- Maps genre classifications
- Handles rate limits gracefully

**Meetup Agent:**
- Uses GraphQL API
- Searches for Houston community events
- Deals with sparse/incomplete data

**Execution:** All run in parallel via `asyncio.gather()` for speed.

### Review Agent Swarm

Each review agent validates/enriches events independently:

**URL Validator:**
- Checks if event URLs are working
- Performs HEAD requests
- Marks events with broken links

**Content Enricher:**
- Scrapes event pages with BeautifulSoup
- Uses LLM to extract structured data
- Enriches descriptions with missing details

**Relevance Scorer:**
- Scores events based on user preferences
- High priority: Cycling (10 pts), Couple activities (9 pts), Music (8 pts)
- Deprioritizes: Kid-focused events (-5 pts)

**Date Verifier:**
- Ensures events are within target window (next 3 days)
- Filters out stale/past events
- Normalizes timezones to Houston time

**Execution:** All run in parallel with configurable concurrency (default: 5 concurrent).

### Promo Generator Agent

**Purpose:** Creates the final wrestling promo.

**Process:**
1. Receives enriched events with confidence scores
2. Sorts by relevance score
3. Uses the wrestling promo template
4. Incorporates planning context (scratchpad insights)
5. Generates character-appropriate content (Macho Man + Ultimate Warrior)
6. Ensures URL accuracy

**Output:** High-energy promo + event listing ready for SMS.

## REACT Pattern Explained

REACT (Reasoning + Acting) is a SOTA prompting technique:

```python
# Traditional approach
result = llm.query("Find events and generate promo")  # Black box

# REACT approach
thought = "I need to find events"
action = invoke_search_agents()
observation = "Found 45 events"

thought = "Some events need verification"  
action = invoke_review_swarm()
observation = "35 verified, 10 need attention"

thought = "Data quality is good, can generate promo"
action = invoke_promo_generator()
observation = "Promo generated successfully"
```

**Benefits:**
- **Transparency:** See the agent's reasoning
- **Debuggability:** Track exactly what happened
- **Adaptability:** Agent can adjust based on observations
- **Quality:** Multiple validation steps ensure accuracy

## Configuration

All agents use settings from your `.env` file:

```bash
# LLM Configuration
EVENTS_OPENAI_API_KEY=sk-...
EVENTS_OPENAI_MODEL=gpt-4o        # Used by Planning & Promo agents
EVENTS_OPENAI_TEMPERATURE=0.9

# API Keys for Search Agents
EVENTS_EVENTBRITE_API_KEY=...
EVENTS_TICKETMASTER_API_KEY=...
EVENTS_MEETUP_API_KEY=...

# SMS Configuration
EVENTS_TWILIO_ACCOUNT_SID=...
EVENTS_TWILIO_AUTH_TOKEN=...
EVENTS_TWILIO_FROM_NUMBER=+1...
EVENTS_SMS_RECIPIENT=+1...
```

## Testing

Run tests for the agentic system:

```bash
# All agentic tests
uv run pytest tests/unit/agents tests/contract/agents tests/integration/agents

# Unit tests only (fast)
uv run pytest tests/unit/agents -m unit

# Contract tests (verify port conformance)
uv run pytest tests/contract/agents -m contract

# Integration tests (slower, may need API keys)
uv run pytest tests/integration/agents -m integration
```

## Monitoring & Observability

The agentic system provides detailed logging:

### Scratchpad Output

After running, you'll see the complete REACT trace:

```
📝 PLANNING AGENT SCRATCHPAD (REACT TRACE)
================================================================================

[1] PlanningAgent @ 09:15:32
    💭 Thought: Starting workflow. First step: search for events.
    🎯 Action: transition_to_search
    👁️  Observation: Moving to SEARCHING phase
    📊 Confidence: 1.00

[2] SearchAgent:Eventbrite @ 09:15:35
    💭 Thought: Searching Eventbrite API
    🎯 Action: search_events
    👁️  Observation: Found 18 events in 2.3s
    📊 Confidence: 0.90

[3] PlanningAgent @ 09:15:38
    💭 Thought: Search phase complete. Found 45 unique events.
    🎯 Action: analyze_search_results
    👁️  Observation: Total: 45 unique events
    📊 Confidence: 0.90

...
```

### Stats Summary

```
📊 Stats:
  - Events found: 45
  - Events reviewed: 45
  - Search sources: Eventbrite, Ticketmaster, Meetup
  - Questions raised: 3
  - Observations logged: 12
  - Verified events: 38/45
  - Avg confidence: 0.87
```

## Comparing Original vs Agentic

| Aspect | Original System | Agentic System |
|--------|----------------|----------------|
| **Search** | Sequential API calls | Parallel agent execution |
| **Validation** | Basic filtering | Multi-agent review swarm |
| **Reasoning** | None (direct to LLM) | REACT pattern with scratchpad |
| **Transparency** | Black box | Full observation trail |
| **Adaptability** | Fixed pipeline | Adaptive based on data quality |
| **Error Handling** | Fail fast | Graceful degradation |
| **Execution Time** | ~15-20s | ~10-12s (parallelization) |

## Troubleshooting

### Issue: "No API key configured"

**Solution:** Ensure your `.env` file has the required API keys. The system gracefully handles missing keys by skipping those agents.

### Issue: Low confidence scores

**Solution:** Check the scratchpad output to see which agents reported low confidence. Often due to:
- Broken event URLs
- Missing venue information
- Stale data

### Issue: Slow execution

**Solution:**
1. Reduce concurrency in review swarm: `run_review_swarm(events, agents, max_concurrent=3)`
2. Disable ContentEnricherAgent (slowest due to LLM calls)
3. Check network latency to APIs

## Advanced Customization

### Add a New Review Agent

```python
class MyCustomAgent(ReviewAgentPort):
    async def review_event(self, event: Event) -> ReviewAgentResult:
        # Your custom validation logic
        enriched = EnrichedEvent(
            event=event,
            verified=True,
            confidence_score=0.95
        )
        return ReviewAgentResult(
            agent_id="my_custom_agent",
            enriched_event=enriched,
            success=True
        )
```

Register in `app/core/di.py`:

```python
review_agents = [
    URLValidatorAgent(),
    RelevanceScoreAgent(),
    MyCustomAgent(),  # Add here
    ...
]
```

### Modify Planning Logic

Edit `app/adapters/agents/planning_agent.py` to customize:
- Phase transition logic
- Question generation
- Confidence thresholds

### Change Concurrency

In `build_agentic_event_service()`:

```python
# In planning_agent.py _review_phase()
enriched_events = await run_review_swarm(
    events=state.events_found,
    agents=self.review_agents,
    max_concurrent=10  # Increase for faster execution
)
```

## Resources

- **PydanticAI Docs:** https://ai.pydantic.dev
- **REACT Paper:** https://arxiv.org/abs/2210.03629
- **Architecture Doc:** `docs/AGENTIC_ARCHITECTURE.md`
- **Agent Patterns:** https://lilianweng.github.io/posts/2023-06-23-agent/

## Next Steps

1. ✅ Run the agentic workflow: `uv run python -m app.workers.run_daily_job --agentic`
2. ✅ Review the scratchpad output to understand the REACT loop
3. ✅ Compare results with the original system
4. ✅ Customize agents for your specific needs
5. ✅ Add monitoring/alerting based on confidence scores

**Welcome to the future of event discovery! 🤖🎤💪**

