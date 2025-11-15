# Agentic Architecture - SOTA Patterns & Implementation

## Overview

This document explains the State-of-the-Art (SOTA) agentic patterns used in Houston Event Mania's multi-agent system.

## Core Concepts

### 1. **REACT (Reasoning + Acting)**

REACT is a prompting pattern where agents:
- **Reason** about the current state and what to do next
- **Act** by executing tools or making decisions
- **Observe** the results and update their understanding
- **Iterate** until the goal is achieved

**Pattern Structure:**
```
Thought: [Agent reasons about what to do]
Action: [Agent takes an action using a tool]
Observation: [Result of the action]
Thought: [Agent reasons about the observation]
... (repeat until done)
```

### 2. **Agent State & Scratchpad**

**State Management:**
- Track the current phase of execution
- Maintain conversation history
- Store intermediate results
- Manage dependencies between steps

**Scratchpad:**
- Working memory for the agent
- Stores observations, intermediate calculations
- Allows the agent to "show its work"
- Critical for transparent decision-making

### 3. **Parallel Agent Orchestration**

**Agent Swarms:**
- Multiple agents work simultaneously
- Each agent has a specific responsibility
- Results are aggregated by the orchestrator
- Enables faster execution and specialization

**Types:**
- **Vertical Parallelism**: Different agents for different data sources
- **Horizontal Parallelism**: Multiple agents processing the same type of task

### 4. **Tool-Augmented Agents**

Agents have access to tools (functions) they can call:
- Web scraping tools
- API clients
- Data validators
- Information synthesizers

## Our Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Planning Agent (REACT)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ State: Current phase, scratchpad, observations         │ │
│  │ Tools: Question generator, decision maker              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   Phase 1: Parallel Search Agents    │
        ├──────────────┬───────────┬───────────┤
        │  Eventbrite  │Ticketmaster│  Meetup  │
        │    Agent     │   Agent    │  Agent   │
        └──────────────┴───────────┴───────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   Phase 2: Review Agent Swarm        │
        ├──────────────┬───────────┬───────────┤
        │  Validator   │ Enricher  │ Verifier │
        │   Agent 1    │  Agent 2  │ Agent 3  │
        │      ...     │    ...    │   ...    │
        └──────────────┴───────────┴───────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │      Phase 3: Synthesis              │
        │         Promo Generator Agent        │
        └──────────────────────────────────────┘
```

## Agent Details

### Planning Agent

**Responsibility:** Orchestrate the entire workflow using REACT

**State:**
```python
class PlanningState:
    phase: Literal["search", "review", "synthesize", "complete"]
    scratchpad: List[str]  # REACT observations
    events_found: List[Event]
    events_reviewed: List[EnrichedEvent]
    questions_to_investigate: List[str]
    confidence_scores: Dict[str, float]
```

**Tools:**
- `generate_questions`: Create follow-up questions based on current data
- `evaluate_confidence`: Assess data quality
- `decide_next_phase`: Determine if ready to move forward

**REACT Loop:**
1. Thought: "I need to gather events from multiple sources"
2. Action: Invoke parallel search agents
3. Observation: "Found 45 events across 3 sources"
4. Thought: "Some events lack venue details, need verification"
5. Action: Generate questions for review agents
6. Observation: "10 events need website verification"
7. Action: Invoke review swarm
8. Observation: "All events validated and enriched"
9. Thought: "Data is complete and confident, ready for promo"
10. Action: Invoke promo generator

### Search Agents (Parallel)

**Eventbrite Agent:**
- Specialized in Eventbrite API
- Handles auth, pagination, error recovery
- Returns structured Event objects

**Ticketmaster Agent:**
- Specialized in Ticketmaster Discovery API
- Maps classifications to our categories
- Handles rate limits

**Meetup Agent:**
- Handles GraphQL queries
- Processes community events
- Deals with sparse data

**Execution:** All run in parallel via `asyncio.gather()`

### Review Agent Swarm

**Purpose:** Validate and enrich event data

**Agent Types:**

1. **Validator Agent:** Checks if URLs are valid, venues exist
2. **Enricher Agent:** Scrapes event pages for missing details
3. **Verifier Agent:** Cross-checks dates, locations, pricing

**Execution:** Parallel processing with configurable batch size

**Tools:**
- `fetch_url`: Async HTTP client
- `extract_structured_data`: Parse event pages
- `verify_location`: Check address validity
- `assess_relevance`: Score events for user preferences

### Promo Generator Agent

**Responsibility:** Create the final wrestling promo

**Inputs:**
- Prioritized, validated, enriched events
- Planning agent's scratchpad (context)
- User preferences

**Process:**
1. Analyze event priorities
2. Generate character-appropriate content
3. Weave in event details with promo energy
4. Ensure URL accuracy

## SOTA Techniques Used

### 1. **Chain-of-Thought (CoT) Prompting**

Make agents show their reasoning:
```
"Before acting, explain your reasoning step by step..."
```

### 2. **Self-Consistency**

For critical decisions, run multiple inference passes and use consensus.

### 3. **Reflection**

Agents review their own work:
```
"Review the events found. Are there gaps? What questions remain?"
```

### 4. **Tool Use with Function Calling**

PydanticAI's structured tool definitions ensure type safety:
```python
@agent.tool
async def fetch_event_details(url: HttpUrl) -> EventDetails:
    """Fetch and parse event details from a URL."""
    ...
```

### 5. **State Persistence**

State is versioned and can be resumed if interrupted:
```python
state = await agent.run(state=previous_state)
```

### 6. **Confidence Scoring**

Each agent returns confidence scores:
```python
class AgentResult:
    data: T
    confidence: float  # 0.0 to 1.0
    reasoning: str
```

### 7. **Graceful Degradation**

If an agent fails:
- Log the failure
- Use partial results
- Don't block the entire pipeline

## Benefits

1. **Transparency**: REACT scratchpad shows reasoning
2. **Reliability**: Parallel execution with fallbacks
3. **Accuracy**: Multiple validation stages
4. **Flexibility**: Easy to add new agents or tools
5. **Maintainability**: Clear separation of concerns

## Testing Strategy

1. **Unit Tests**: Individual agent logic
2. **Contract Tests**: Agent interfaces
3. **Integration Tests**: Full agentic flow
4. **Property Tests**: State transitions are valid

## Resources

- PydanticAI Docs: https://ai.pydantic.dev
- REACT Paper: https://arxiv.org/abs/2210.03629
- ReAct Prompting: https://www.promptingguide.ai/techniques/react
- Agent Architectures: https://lilianweng.github.io/posts/2023-06-23-agent/

