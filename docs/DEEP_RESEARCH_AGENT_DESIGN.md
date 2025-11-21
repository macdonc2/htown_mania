# Deep Research Agent System - Design Document

## 🎯 Vision

Transform the agentic system into a **deep research orchestrator** that:
1. **Analyzes** event descriptions to extract entities (artists, venues, organizers, topics)
2. **Generates** intelligent research queries about those entities
3. **Researches** using multi-source web intelligence
4. **Synthesizes** findings into rich context
5. **Enriches** the promo with compelling insights and storytelling

---

## 🏗️ Architecture Enhancement

### New Phase: RESEARCHING

Add a new phase between `REVIEWING` and `SYNTHESIZING`:

```
INITIALIZING → SEARCHING → REVIEWING → RESEARCHING → SYNTHESIZING → COMPLETE
```

### New Agents

#### 1. **Entity Extraction Agent**
- **Tech**: GPT-4o-mini
- **Input**: Event title + description
- **Output**: Structured entities (artists, venues, organizers, topics)
- **Example**:
  ```python
  Event: "Mac Miller Tribute with Thundercat at White Oak Music Hall"
  
  Entities:
  - Artist: Mac Miller (deceased rapper)
  - Artist: Thundercat (bassist, collaborator)
  - Venue: White Oak Music Hall
  - Genre: Hip-hop, Jazz Fusion
  - Theme: Tribute concert
  ```

#### 2. **Query Generation Agent**
- **Tech**: GPT-4o with Chain-of-Thought
- **Input**: Extracted entities + event context
- **Output**: Research queries ranked by importance
- **Example**:
  ```python
  Queries:
  1. "Mac Miller biography career highlights" (priority: 10)
  2. "Mac Miller Thundercat collaborations" (priority: 9)
  3. "White Oak Music Hall Houston history" (priority: 7)
  4. "Thundercat recent performances reviews" (priority: 6)
  5. "Mac Miller cultural impact legacy" (priority: 8)
  ```

#### 3. **Deep Research Swarm**
Multiple specialized research agents working in parallel:

**a. Web Search Research Agent**
- Uses SerpAPI for general web research
- Extracts snippets and key facts
- High coverage, medium depth

**b. Wikipedia Research Agent**
- Queries Wikipedia API for entities
- Gets biographical info, history, context
- High reliability, structured data

**c. News Research Agent**
- Searches recent news articles
- Finds trending topics, recent events
- Temporal context, current relevance

**d. Social Media Research Agent** (Optional)
- Searches Twitter/Reddit mentions
- Gauges community excitement
- Social proof, sentiment

**e. Music/Artist Research Agent** (Domain-specific)
- Queries music databases (MusicBrainz, Last.fm)
- Gets discography, collaborations, genre info
- Domain expertise

#### 4. **Knowledge Synthesis Agent**
- **Tech**: GPT-4o
- **Input**: All research results for an event
- **Output**: Synthesized narrative with key insights
- **Example**:
  ```
  Mac Miller was a beloved Pittsburgh rapper who passed in 2018, 
  leaving a lasting impact on hip-hop. Thundercat, a virtuoso 
  bassist who collaborated with Mac on multiple tracks, brings 
  his unique jazz-fusion style to this tribute. White Oak Music 
  Hall, Houston's premier indie venue since 2016, provides an 
  intimate setting for fans to celebrate Mac's legacy.
  ```

---

## 🔄 Enhanced Workflow

### Phase Flow

```
1. SEARCHING Phase (existing)
   → Find events from multiple sources
   
2. REVIEWING Phase (existing)
   → Validate URLs, dates, relevance
   
3. RESEARCHING Phase (NEW)
   ├─ For each event (parallel):
   │  ├─ Extract entities
   │  ├─ Generate research queries
   │  ├─ Deep research swarm (parallel)
   │  │  ├─ Web search
   │  │  ├─ Wikipedia
   │  │  ├─ News
   │  │  └─ Domain-specific
   │  └─ Synthesize knowledge
   └─ Aggregate all research
   
4. SYNTHESIZING Phase (enhanced)
   → Generate promo WITH research insights
```

### REACT Loop Example

```
[8] PlanningAgent @ 09:15:45
    💭 Thought: Review complete. Now need deep research on 38 verified events.
    🎯 Action: transition_to_research
    👁️  Observation: Moving to RESEARCHING phase
    📊 Confidence: 0.95

[9] PlanningAgent @ 09:15:45
    💭 Thought: Will extract entities and generate queries for each event.
    🎯 Action: invoke_research_orchestrator
    📊 Confidence: 1.00

[10] EntityExtractionAgent @ 09:15:46
     💭 Thought: Analyzing "Mac Miller Tribute with Thundercat"
     🎯 Action: extract_entities
     👁️  Observation: Found 2 artists, 1 venue, 2 genres, 1 theme
     📊 Confidence: 0.95

[11] QueryGenerationAgent @ 09:15:47
     💭 Thought: Entities extracted. Generating research queries.
     🎯 Action: generate_queries
     👁️  Observation: Generated 5 priority queries
     📊 Confidence: 0.90

[12] WebSearchResearchAgent @ 09:15:48
     💭 Thought: Researching "Mac Miller biography career highlights"
     🎯 Action: deep_web_search
     👁️  Observation: Found 8 sources with biographical info
     📊 Confidence: 0.92

[13] WikipediaResearchAgent @ 09:15:48
     💭 Thought: Querying Wikipedia for "Mac Miller"
     🎯 Action: wikipedia_lookup
     👁️  Observation: Retrieved full biography (3,200 words)
     📊 Confidence: 1.00

[14] MusicResearchAgent @ 09:15:49
     💭 Thought: Looking up Mac Miller discography
     🎯 Action: musicbrainz_query
     👁️  Observation: Found 5 albums, 23 singles, 42 collaborations
     📊 Confidence: 0.95

[15] KnowledgeSynthesisAgent @ 09:15:52
     💭 Thought: Synthesizing research from 3 agents
     🎯 Action: synthesize_narrative
     👁️  Observation: Generated 250-word enriched context
     📊 Confidence: 0.93

[16] PlanningAgent @ 09:16:10
     💭 Thought: Research complete for 38 events. Rich context available.
     🎯 Action: analyze_research_results
     👁️  Observation: Avg 4.2 entities per event, 18.5 facts per event
     📊 Confidence: 0.91

[17] PlanningAgent @ 09:16:10
     💭 Thought: Research data is comprehensive. Ready for enhanced promo.
     🎯 Action: transition_to_synthesize
     👁️  Observation: Moving to SYNTHESIZING phase with research insights
     📊 Confidence: 0.95
```

---

## 📊 Domain Models

### New Models

```python
class Entity(BaseModel):
    """An entity extracted from an event."""
    name: str
    type: Literal["artist", "venue", "organizer", "topic", "genre"]
    confidence: float = Field(ge=0.0, le=1.0)
    aliases: List[str] = []
    metadata: Dict[str, Any] = {}


class ResearchQuery(BaseModel):
    """A research query to investigate."""
    query: str
    priority: int = Field(ge=1, le=10)
    entity: Optional[Entity] = None
    query_type: Literal["biographical", "contextual", "current", "relational"]
    executed: bool = False
    results: List[str] = []


class ResearchResult(BaseModel):
    """Result from a research agent."""
    agent_id: str
    query: ResearchQuery
    sources: List[str]  # URLs or source names
    facts: List[str]    # Key facts discovered
    snippets: List[str] # Text snippets
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time: float


class EventResearch(BaseModel):
    """Complete research for a single event."""
    event: Event
    entities: List[Entity]
    queries: List[ResearchQuery]
    results: List[ResearchResult]
    synthesized_narrative: str
    key_insights: List[str]
    overall_confidence: float


class ResearchState(BaseModel):
    """State for the research phase."""
    events_to_research: List[EnrichedEvent]
    research_complete: List[EventResearch]
    total_entities_found: int = 0
    total_queries_executed: int = 0
    total_facts_discovered: int = 0
```

### Enhanced PlanningState

```python
class PlanningState(BaseModel):
    phase: AgentPhase
    scratchpad: List[Observation]
    
    # Search phase
    events_found: List[Event]
    search_sources_completed: List[str]
    
    # Review phase
    events_reviewed: List[EnrichedEvent]
    
    # Research phase (NEW)
    research_state: Optional[ResearchState] = None
    events_researched: List[EventResearch] = []
    
    # Synthesis
    promo_generated: Optional[str]
```

---

## 🔧 Implementation Components

### 1. Entity Extraction Agent

```python
class EntityExtractionAgent(ABC):
    """
    Extracts entities from event descriptions.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = Agent(
            model=OpenAIModel("gpt-4o-mini"),
            system_prompt=(
                "You are an expert at extracting entities from event descriptions. "
                "Identify artists, venues, organizers, topics, and genres. "
                "Be thorough but precise. Return structured data."
            )
        )
    
    async def extract_entities(
        self, 
        event: Event
    ) -> List[Entity]:
        """Extract entities from an event."""
        
        prompt = f"""
Event Title: {event.title}
Description: {event.description or "N/A"}
Location: {event.location or "N/A"}
Categories: {", ".join(event.categories)}

Extract all entities:
1. Artists/Performers (musicians, speakers, etc.)
2. Venues (specific locations)
3. Organizers (companies, groups)
4. Topics (themes, subjects)
5. Genres (music, art styles)

For each entity, provide:
- Name
- Type
- Why it's important
- Any aliases or alternate names
"""
        
        result = await self.llm.run(prompt)
        # Parse structured output
        entities = self._parse_entities(result.data)
        
        return entities
```

### 2. Query Generation Agent

```python
class QueryGenerationAgent(ABC):
    """
    Generates intelligent research queries.
    """
    
    async def generate_queries(
        self,
        event: Event,
        entities: List[Entity]
    ) -> List[ResearchQuery]:
        """Generate prioritized research queries."""
        
        prompt = f"""
Event: {event.title}
Description: {event.description}

Entities Found:
{self._format_entities(entities)}

Generate 5-10 research queries to learn more about this event.
Prioritize queries that will:
1. Help understand why this event is special/interesting
2. Provide context about key people/places
3. Reveal recent developments or trending topics
4. Uncover connections or collaborations
5. Add storytelling elements

For each query:
- Write a clear search query
- Assign priority (1-10)
- Specify type (biographical, contextual, current, relational)
"""
        
        result = await self.llm.run(prompt)
        queries = self._parse_queries(result.data, entities)
        
        return queries
```

### 3. Deep Research Swarm

```python
async def run_deep_research_swarm(
    queries: List[ResearchQuery],
    research_agents: List[ResearchAgentPort],
    max_concurrent: int = 3
) -> List[ResearchResult]:
    """
    Execute research queries across multiple agents in parallel.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def research_query(query: ResearchQuery) -> List[ResearchResult]:
        async with semaphore:
            # All agents research this query in parallel
            results = await asyncio.gather(
                *[agent.research(query) for agent in research_agents],
                return_exceptions=True
            )
            return [r for r in results if isinstance(r, ResearchResult)]
    
    # Research all queries
    all_results = []
    for query in queries:
        results = await research_query(query)
        all_results.extend(results)
        query.executed = True
        query.results = [r.agent_id for r in results]
    
    return all_results
```

### 4. Knowledge Synthesis Agent

```python
class KnowledgeSynthesisAgent(ABC):
    """
    Synthesizes research results into coherent narratives.
    """
    
    async def synthesize(
        self,
        event: Event,
        entities: List[Entity],
        research_results: List[ResearchResult]
    ) -> EventResearch:
        """Synthesize all research into a rich narrative."""
        
        # Aggregate all facts
        all_facts = []
        for result in research_results:
            all_facts.extend(result.facts)
        
        # Deduplicate and rank facts
        unique_facts = self._deduplicate_facts(all_facts)
        
        prompt = f"""
Event: {event.title}
Description: {event.description}

Entities: {self._format_entities(entities)}

Research Facts Discovered:
{self._format_facts(unique_facts)}

Create a compelling 200-250 word narrative that:
1. Introduces the key entities with interesting context
2. Explains why this event is special or significant
3. Highlights connections, collaborations, or themes
4. Adds storytelling elements that make it engaging
5. Maintains accuracy while being vivid

Focus on what makes this event worth attending.
"""
        
        result = await self.llm.run(prompt)
        
        # Extract key insights
        key_insights = self._extract_key_insights(unique_facts)
        
        return EventResearch(
            event=event,
            entities=entities,
            queries=queries,
            results=research_results,
            synthesized_narrative=result.data,
            key_insights=key_insights,
            overall_confidence=self._calculate_confidence(research_results)
        )
```

---

## 🎬 Enhanced Promo Generation

The Promo Generator now receives **research-enriched events**:

```python
async def generate_promo(
    self,
    events: List[EnrichedEvent],
    research: List[EventResearch],  # NEW
    planning_context: PlanningState
) -> PromoGenerationResult:
    """
    Generate promo with deep research insights.
    """
    
    # Match research to events
    event_research_map = {
        r.event.title: r for r in research
    }
    
    # Build enriched context
    enriched_context = []
    for enriched in events:
        event = enriched.event
        res = event_research_map.get(event.title)
        
        if res:
            enriched_context.append({
                "event": event,
                "score": enriched.additional_metadata.get("relevance_score", 0),
                "narrative": res.synthesized_narrative,
                "insights": res.key_insights,
                "entities": res.entities
            })
    
    # Sort by score
    enriched_context.sort(key=lambda x: x["score"], reverse=True)
    
    # Enhanced template rendering
    template = self.env.get_template("summary_with_research.j2")
    
    rendered = template.render(
        enriched_events=enriched_context,
        date_str=datetime.now().strftime("%A, %B %d, %Y"),
        planning_insights=self._extract_planning_insights(planning_context)
    )
    
    result = await self.agent.run(rendered)
    
    return PromoGenerationResult(
        promo_text=result.data,
        events_included=[e["event"].title for e in enriched_context],
        confidence=0.95,
        generation_metadata={
            "total_entities": sum(len(e["entities"]) for e in enriched_context),
            "total_insights": sum(len(e["insights"]) for e in enriched_context),
            "research_enhanced": True
        }
    )
```

---

## 📝 Enhanced Template

New Jinja2 template: `summary_with_research.j2`

```jinja2
You are generating a LEGENDARY wrestling promo for Houston events on {{ date_str }}.

Channel MACHO MAN RANDY SAVAGE and ULTIMATE WARRIOR energy!

EVENTS WITH DEEP RESEARCH:

{% for item in enriched_events[:10] %}
---
EVENT #{{ loop.index }}: {{ item.event.title }}
URL: {{ item.event.url }}
Location: {{ item.event.location }}
Time: {{ item.event.start_time.strftime("%a %b %d at %I:%M %p") if item.event.start_time else "TBA" }}

RESEARCH INSIGHTS:
{{ item.narrative }}

KEY FACTS:
{% for insight in item.insights[:3] %}
- {{ insight }}
{% endfor %}

ENTITIES:
{% for entity in item.entities[:5] %}
- {{ entity.name }} ({{ entity.type }})
{% endfor %}

RELEVANCE SCORE: {{ item.score }}/10
---

{% endfor %}

INSTRUCTIONS:
1. Start with an EXPLOSIVE opening that grabs attention
2. For TOP 5-7 events, weave in the research insights naturally
3. Use the entity context to add depth and storytelling
4. Highlight what makes each event SPECIAL based on the research
5. Build intensity as you go
6. Include ACCURATE URLs for each event mentioned
7. Close with a POWERFUL call to action

Make it LEGENDARY! OOOOH YEAH!
```

---

## 🎯 Expected Output Example

### Before (without research):
```
OOOOH YEAH! Houston, the Ultimate Warrior is HERE with your events!

🎸 Mac Miller Tribute with Thundercat at White Oak Music Hall
Check it out: https://...

🚴 Critical Mass Bike Ride - meet at Market Square Park
Get there: https://...
```

### After (with research):
```
OOOOH YEAH! Houston, the Ultimate Warrior is HERE with LEGENDARY events!

🎸 DIG THIS, BROTHER! Mac Miller Tribute with THUNDERCAT at White Oak Music Hall!

Mac Miller - the Pittsburgh prodigy who changed hip-hop forever before 
his tragic passing in 2018 - gets the tribute he DESERVES! And who's 
bringing it? THUNDERCAT, the jazz-fusion VIRTUOSO who collaborated with 
Mac on classics like "What's The Use?" The man who's played with Kendrick, 
Flying Lotus, and won THREE Grammys is bringing his 6-string FURY to 
Houston's most INTIMATE venue! White Oak Music Hall - where indie legends 
are made - becomes a TEMPLE to Mac's legacy! This isn't just a concert, 
it's a CELEBRATION of a fallen hero!

Friday, Nov 22 at 8:00 PM - https://...

🚴 FEEL THE POWER! Critical Mass rides AGAIN! 

Since 1992, this global movement has UNITED cyclists in THOUSANDS of 
cities! Houston's chapter - 500+ riders strong - takes over the streets 
in a rolling demonstration of PEOPLE POWER! Starting at Market Square 
Park, where Houston's history BEGAN in 1836, you'll roll through downtown 
with a WARRIOR SPIRIT! No leaders, no rules, just PURE cycling energy! 
Last month broke records with 600 riders - can you handle the INTENSITY?

Friday, Nov 22 at 7:00 PM - Meet at Market Square Park - https://...
```

**Notice the difference**: Names, context, history, significance - all from deep research!

---

## 📊 Performance Considerations

### Timing
- **Entity Extraction**: ~1-2s per event (parallel)
- **Query Generation**: ~2-3s per event (parallel)
- **Deep Research**: ~3-5s per query (parallel, 3 concurrent)
- **Synthesis**: ~2-3s per event (parallel)

**Total Research Phase**: ~15-25 seconds for 40 events

### Optimization Strategies

1. **Batch Processing**: Extract entities for multiple events in one LLM call
2. **Query Deduplication**: Same artist in multiple events? Reuse research
3. **Caching**: Cache research results for common entities (venues, popular artists)
4. **Tiered Research**: Deep research for top 10 events, light research for others
5. **Concurrent Limits**: Tune `max_concurrent` based on API rate limits

### Cost Management

- Use **GPT-4o-mini** for extraction and query generation
- Use **GPT-4o** only for synthesis
- Cache Wikipedia/MusicBrainz results (free APIs)
- Rate limit expensive web searches

---

## 🔌 Integration Points

### In Planning Agent

```python
async def _research_phase(self, state: PlanningState) -> PlanningState:
    """Execute the deep research phase."""
    
    state.add_observation(
        agent="PlanningAgent",
        thought=f"Need deep research on {len(state.events_reviewed)} events.",
        action="invoke_research_orchestrator",
        confidence=1.0
    )
    
    # Initialize research state
    research_state = ResearchState(
        events_to_research=state.events_reviewed
    )
    
    # For each event
    for enriched in state.events_reviewed:
        event = enriched.event
        
        # Extract entities
        entities = await self.entity_extractor.extract_entities(event)
        research_state.total_entities_found += len(entities)
        
        state.add_observation(
            agent="EntityExtractionAgent",
            thought=f"Analyzing '{event.title}'",
            action="extract_entities",
            result=f"Found {len(entities)} entities",
            confidence=0.95
        )
        
        # Generate queries
        queries = await self.query_generator.generate_queries(event, entities)
        research_state.total_queries_executed += len(queries)
        
        state.add_observation(
            agent="QueryGenerationAgent",
            thought=f"Generated research plan for '{event.title}'",
            action="generate_queries",
            result=f"Generated {len(queries)} priority queries",
            confidence=0.90
        )
        
        # Execute research swarm
        results = await run_deep_research_swarm(
            queries=queries,
            research_agents=self.research_agents,
            max_concurrent=3
        )
        
        for result in results:
            research_state.total_facts_discovered += len(result.facts)
            state.add_observation(
                agent=f"ResearchAgent:{result.agent_id}",
                thought=f"Researching '{result.query.query}'",
                action="deep_research",
                result=f"Found {len(result.facts)} facts from {len(result.sources)} sources",
                confidence=result.confidence
            )
        
        # Synthesize knowledge
        event_research = await self.knowledge_synthesizer.synthesize(
            event=event,
            entities=entities,
            research_results=results
        )
        
        research_state.research_complete.append(event_research)
        
        state.add_observation(
            agent="KnowledgeSynthesisAgent",
            thought=f"Synthesizing research for '{event.title}'",
            action="synthesize_narrative",
            result=f"Generated narrative with {len(event_research.key_insights)} insights",
            confidence=event_research.overall_confidence
        )
    
    state.research_state = research_state
    state.events_researched = research_state.research_complete
    
    # Analyze overall research quality
    avg_entities = research_state.total_entities_found / len(state.events_reviewed)
    avg_facts = research_state.total_facts_discovered / len(state.events_reviewed)
    
    state.add_observation(
        agent="PlanningAgent",
        thought=f"Research complete. Deep context gathered.",
        action="analyze_research_results",
        result=f"Avg {avg_entities:.1f} entities per event, {avg_facts:.1f} facts per event",
        confidence=0.91
    )
    
    state.phase = AgentPhase.SYNTHESIZING
    return state
```

---

## 🚀 Rollout Strategy

### Phase 1: Foundation (Week 1-2)
- [ ] Create domain models (Entity, ResearchQuery, EventResearch)
- [ ] Implement EntityExtractionAgent
- [ ] Implement QueryGenerationAgent
- [ ] Add unit tests

### Phase 2: Research Agents (Week 2-3)
- [ ] Implement WebSearchResearchAgent
- [ ] Implement WikipediaResearchAgent
- [ ] Implement NewsResearchAgent (optional)
- [ ] Add contract tests

### Phase 3: Synthesis (Week 3-4)
- [ ] Implement KnowledgeSynthesisAgent
- [ ] Create enhanced promo template
- [ ] Integrate with Planning Agent
- [ ] Add integration tests

### Phase 4: Optimization (Week 4-5)
- [ ] Add caching layer
- [ ] Implement query deduplication
- [ ] Optimize concurrency
- [ ] Add performance monitoring

### Phase 5: Polish (Week 5-6)
- [ ] A/B test with/without research
- [ ] Tune confidence thresholds
- [ ] Add fallback mechanisms
- [ ] Documentation

---

## 🎓 Key Benefits

1. **Richer Promos**: Context and storytelling make events compelling
2. **Higher Engagement**: Users learn why events matter
3. **Better Decisions**: Deep context helps users choose
4. **Discovery**: Users learn about artists/venues they didn't know
5. **SEO Value**: Research content could power a blog/newsletter
6. **Differentiation**: No other event system does deep research

---

## 📚 Example Scratchpad Output

```
[16] PlanningAgent @ 09:16:10
     💭 Thought: Research complete for 38 events. Rich context available.
     🎯 Action: analyze_research_results
     👁️  Observation: 
         - Total entities: 156 (avg 4.1 per event)
         - Total queries: 178 (avg 4.7 per event)
         - Total facts: 892 (avg 23.5 per event)
         - Top entity types: Artists (45%), Venues (28%), Topics (18%)
         - Research confidence: 0.89
     📊 Confidence: 0.91
```

---

This design transforms your system into a **true AI research assistant** that discovers, investigates, and synthesizes knowledge! 🚀🔍🤖

