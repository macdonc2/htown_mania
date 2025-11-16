# Houston Event Mania - Agentic System Overview

## System Description

The Houston Event Mania agentic system is a **State-of-the-Art (SOTA) multi-agent orchestration** for intelligent event discovery and wrestling promo generation. It implements the **REACT (Reasoning + Acting)** pattern with parallel agent execution, confidence scoring, and transparent decision-making.

## Core Components

### 1. **Planning Agent** (Orchestrator)
The "brain" of the system that coordinates the entire workflow.

**Technology**: PydanticAI with GPT-4o

**Key Features**:
- Implements REACT pattern (Thought → Action → Observation loop)
- Maintains a scratchpad of all observations for transparency
- Generates questions when data quality is uncertain
- Makes phase transition decisions based on confidence scores
- Provides full traceability of the decision-making process

**State Management**:
- Tracks current phase (Initializing → Searching → Reviewing → Synthesizing → Complete)
- Stores all observations with timestamps and confidence scores
- Maintains questions to investigate
- Records events found, reviewed, and final promo

**REACT Loop Example**:
```
[1] Thought: "Starting workflow. First step: search for events."
[2] Action: transition_to_search
[3] Observation: "Moving to SEARCHING phase"
[4] Thought: "Need to gather events. I have 3 search agents available."
[5] Action: invoke_parallel_search_agents
[6] Observation: "Found 45 events across 3 sources"
[7] Thought: "Some events lack venue details, need verification"
[8] Action: invoke_review_swarm
...
```

### 2. **Search Agents** (Parallel Data Collectors)
Specialized agents that fetch events from different data sources simultaneously.

#### **A. Ticketmaster Search Agent**
- **API**: Ticketmaster Discovery API v2
- **Coverage**: Events in Houston, TX (next 3 days)
- **Features**: 
  - Genre classification mapping
  - Venue extraction
  - Date normalization to Houston timezone
  - Rate limit handling
- **Confidence**: 0.9

#### **B. Meetup Search Agent**
- **API**: Meetup GraphQL API
- **Coverage**: Community events in Houston
- **Features**:
  - Handles sparse data gracefully
  - GraphQL query optimization
  - Category inference
- **Confidence**: 0.8

#### **C. SerpAPI Events Agent**
- **API**: SerpAPI Google Events engine
- **Coverage**: Aggregates from ALL sources (Eventbrite, Ticketmaster, Meetup, Facebook Events, etc.)
- **Features**:
  - Web-scale event discovery
  - Fuzzy date parsing
  - Address normalization
  - High recall
- **Confidence**: 0.95 (highest confidence due to aggregation)

**Parallel Execution**: All agents run simultaneously via `asyncio.gather()` for maximum speed.

### 3. **Review Agent Swarm** (Parallel Validators & Enrichers)
Independent agents that validate and enrich events with additional data.

#### **A. Web Search Enricher Agent**
- **Tool**: SerpAPI Google Search + GPT-4o-mini
- **Function**: 
  - Searches Google for event information
  - Extracts snippets from top 3 results
  - Uses LLM to synthesize verification info
  - Confirms event legitimacy
- **Checks**: Web presence, additional details, verification status

#### **B. Content Enricher Agent**
- **Tool**: Web scraping (httpx + BeautifulSoup) + GPT-4o-mini
- **Function**:
  - Fetches event webpage
  - Extracts HTML content
  - Uses LLM to extract structured data
  - Enriches descriptions with missing details
- **Checks**: URL validity, content extraction, description quality

#### **C. Relevance Score Agent**
- **Tool**: Domain-specific keyword matching
- **Function**:
  - Scores events based on user preferences
  - High priority: Cycling (10 pts), Couple activities (9 pts), Music (8 pts)
  - Medium priority: Dog-friendly (7 pts), Outdoor (5 pts)
  - Deprioritized: Kid-focused events (-5 pts)
- **Checks**: Category matching, preference alignment

#### **D. Date Verification Agent**
- **Tool**: Timezone-aware datetime validation
- **Function**:
  - Ensures events are within target window (next 7 days)
  - Normalizes timezones to Houston (America/Chicago)
  - Filters stale/past events
- **Checks**: Date validity, timezone correctness

**Swarm Execution**: All agents process all events in parallel with configurable concurrency (default: 5 concurrent). Results are aggregated using majority voting for verification and confidence averaging.

### 4. **Promo Generator Agent** (Synthesizer)
Creates the final high-energy wrestling promo.

**Technology**: PydanticAI with GPT-4o (temperature=0.9 for creativity)

**Features**:
- Uses Jinja2 template system
- Sorts events by relevance score
- Incorporates planning context and insights
- Channels Macho Man Randy Savage + Ultimate Warrior energy
- Ensures URL accuracy
- Maintains promo structure

**Input Context**:
- Enriched events with confidence scores
- Planning agent's scratchpad observations
- User preference weightings
- Verification notes

**Output**:
- High-energy promo text
- List of events included
- Generation metadata
- Confidence score

## Key Domain Models

### **PlanningState**
```python
class PlanningState:
    phase: AgentPhase                      # Current workflow phase
    scratchpad: List[Observation]          # REACT trace
    events_found: List[Event]              # Raw search results
    events_reviewed: List[EnrichedEvent]   # Validated events
    questions_to_investigate: List[Question]
    promo_generated: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
```

### **Observation** (REACT Trace)
```python
class Observation:
    timestamp: datetime
    agent: str                  # Which agent made this observation
    thought: str                # Reasoning
    action: Optional[str]       # Action taken
    result: Optional[str]       # Observation/result
    confidence: float          # 0.0 to 1.0
```

### **EnrichedEvent**
```python
class EnrichedEvent:
    event: Event                         # Original event
    verified: bool                       # Majority vote from agents
    verification_notes: List[str]        # All agent notes
    confidence_score: float              # Average confidence
    enriched_description: Optional[str]  # LLM-enhanced description
    url_working: bool
    venue_verified: bool
    additional_metadata: Dict[str, Any]  # Scores, etc.
```

## SOTA Patterns Implemented

### 1. **REACT (Reasoning + Acting)**
- Agent reasons about what to do next
- Takes actions using tools
- Observes results
- Updates understanding
- Iterates until goal achieved

### 2. **Agent State & Scratchpad**
- Working memory for transparent decision-making
- Tracks conversation history
- Stores intermediate results
- Enables debugging and explanation

### 3. **Parallel Agent Orchestration**
- **Vertical Parallelism**: Different agents for different data sources
- **Horizontal Parallelism**: Multiple agents processing same data type
- Enables faster execution and specialization

### 4. **Tool-Augmented Agents**
Agents have access to external tools:
- Web scraping (httpx, BeautifulSoup)
- API clients (Ticketmaster, Meetup, SerpAPI)
- LLM reasoning (GPT-4o, GPT-4o-mini)
- Data validators

### 5. **Chain-of-Thought (CoT) Prompting**
Agents show their reasoning step by step before acting.

### 6. **Confidence Scoring**
Every agent returns confidence scores; aggregated for final decisions.

### 7. **Graceful Degradation**
If an agent fails:
- Log the failure
- Use partial results
- Don't block the pipeline
- Continue with available data

## Data Flow

```
User Trigger
    ↓
AgenticEventService.run_daily_event_flow()
    ↓
Initialize PlanningState
    ↓
PlanningAgent.run_workflow()
    ↓
    ├─→ INITIALIZING Phase
    │   └─→ Reason: "Need to gather events"
    │
    ├─→ SEARCHING Phase
    │   ├─→ Ticketmaster Agent ──┐
    │   ├─→ Meetup Agent ─────────┼──→ Parallel Execution
    │   └─→ SerpAPI Agent ────────┘
    │   └─→ Deduplicate & aggregate results
    │
    ├─→ REVIEWING Phase
    │   ├─→ For each event:
    │   │   ├─→ Web Search Enricher ──┐
    │   │   ├─→ Content Enricher ──────┼──→ Parallel Processing
    │   │   ├─→ Relevance Scorer ──────┤    (5 concurrent)
    │   │   └─→ Date Verifier ─────────┘
    │   └─→ Aggregate via majority voting
    │
    ├─→ SYNTHESIZING Phase
    │   └─→ Promo Generator Agent
    │       ├─→ Sort by relevance
    │       ├─→ Apply template
    │       ├─→ Generate promo
    │       └─→ Return result
    │
    └─→ COMPLETE Phase
        ├─→ Save events to repository
        ├─→ Send SMS with promo
        └─→ Print scratchpad trace
```

## Benefits Over Traditional Approach

| Aspect | Traditional System | Agentic System |
|--------|-------------------|----------------|
| **Search** | Sequential API calls | Parallel agent execution |
| **Validation** | Basic filtering | Multi-agent review swarm |
| **Reasoning** | None (direct to LLM) | REACT pattern with scratchpad |
| **Transparency** | Black box | Full observation trail |
| **Adaptability** | Fixed pipeline | Adaptive based on data quality |
| **Error Handling** | Fail fast | Graceful degradation |
| **Execution Time** | ~15-20s | ~10-12s (parallelization) |
| **Debuggability** | Difficult | Complete trace available |
| **Extensibility** | Add to pipeline | Add new agents easily |

## Configuration

All agents are wired together in the dependency injection container (`app/core/di.py`):

```python
def build_agentic_event_service(settings: Settings):
    # Search agents
    search_agents = [
        TicketmasterSearchAgent(settings),
        MeetupSearchAgent(settings),
        SerpAPIEventsAgent(settings)
    ]
    
    # Review agents
    review_agents = [
        WebSearchEnricherAgent(settings.serpapi_key, settings.openai_api_key),
        ContentEnricherAgent(settings.openai_api_key),
        RelevanceScoreAgent(),
        DateVerificationAgent()
    ]
    
    # Promo agent
    promo_agent = PromoGeneratorAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=settings.openai_temperature
    )
    
    # Planning agent (orchestrator)
    planning_agent = PlanningAgent(
        openai_api_key=settings.openai_api_key,
        search_agents=search_agents,
        review_agents=review_agents,
        promo_agent=promo_agent
    )
    
    return AgenticEventService(
        planning_agent=planning_agent,
        sms=sms_adapter,
        repository=repository
    )
```

## Testing Strategy

### **Unit Tests** (`tests/unit/agents/`)
- Individual agent logic
- Domain models (PlanningState, Observation, EnrichedEvent)
- Scoring algorithms
- Date validation

### **Contract Tests** (`tests/contract/agents/`)
- Agent port conformance
- Ensure all adapters implement port interfaces correctly
- Verify method signatures and return types

### **Integration Tests** (`tests/integration/agents/`)
- Full workflow execution
- Agent coordination
- API integration (with VCR cassettes)
- State transitions

## Observability & Monitoring

### **Scratchpad Output**
Complete REACT trace showing:
- All thoughts and reasoning
- Actions taken
- Observations made
- Confidence scores
- Timestamps

### **Stats Summary**
```
📊 Stats:
  - Events found: 45
  - Events reviewed: 45
  - Search sources: SerpAPI, Ticketmaster, Meetup
  - Questions raised: 3
  - Observations logged: 12
  - Verified events: 38/45
  - Avg confidence: 0.87
```

### **Agent Voting Results**
```
✅ Houston Cycling Meetup                      | Votes: 4/4 | relevance_scorer:✅ date_verifier:✅ web_search:✅ content:✅
❌ Kid's Birthday Party Extravaganza          | Votes: 1/4 | relevance_scorer:❌ date_verifier:✅ web_search:✅ content:❌
```

## Architecture Principles

### **Hexagonal Architecture (Ports & Adapters)**
- **Domain Layer**: Models (Event, PlanningState, Observation)
- **Application Layer**: Service (AgenticEventService)
- **Adapters Layer**: Concrete agent implementations
- **Ports**: Abstract interfaces (PlanningAgentPort, SearchAgentPort, ReviewAgentPort)

### **Dependency Injection**
All dependencies are wired in a composition root, making testing and swapping implementations easy.

### **DDD (Domain-Driven Design)**
- Ubiquitous language: Agent, Observation, Scratchpad, REACT
- Value objects: Observation, Question
- Entities: Event, EnrichedEvent
- Aggregates: PlanningState

## Performance Characteristics

- **Search Phase**: 2-5 seconds (parallel)
- **Review Phase**: 5-8 seconds (depends on event count, parallel with concurrency limit)
- **Synthesis Phase**: 3-5 seconds (LLM generation)
- **Total**: ~10-15 seconds end-to-end

## Future Enhancements

1. **Self-Consistency**: Run multiple inference passes for critical decisions
2. **Reflection**: Agents review their own work and iterate
3. **Memory**: Long-term memory across runs for personalization
4. **Multi-modal**: Image analysis for event posters
5. **Feedback Loop**: Learn from user interactions with events
6. **Cost Optimization**: Cache LLM calls, use cheaper models for simple tasks

## Resources

- **PydanticAI**: https://ai.pydantic.dev
- **REACT Paper**: https://arxiv.org/abs/2210.03629
- **Agent Architectures**: https://lilianweng.github.io/posts/2023-06-23-agent/
- **ReAct Prompting Guide**: https://www.promptingguide.ai/techniques/react

