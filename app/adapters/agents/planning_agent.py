"""
Planning Agent - Orchestrates the workflow using REACT pattern.

The Planning Agent is the "brain" that:
1. Reasons about what to do next
2. Takes actions (invokes other agents)
3. Observes results
4. Updates its scratchpad
5. Decides when to move to the next phase
"""
from typing import List

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel

from app.core.domain.agent_models import (
    PlanningState,
    AgentPhase,
    Question
)
from app.core.ports.agent_port import (
    PlanningAgentPort,
    SearchAgentPort,
    ReviewAgentPort,
    PromoAgentPort
)
from app.adapters.agents.search_agents import run_search_agents_parallel
from app.adapters.agents.review_agents import run_review_swarm


class DecisionResult(BaseModel):
    """Result of a planning decision."""
    next_phase: str
    reasoning: str
    confidence: float
    questions_generated: List[str] = []


class PlanningAgent(PlanningAgentPort):
    """
    Planning Agent using REACT (Reasoning + Acting) pattern.
    
    REACT Loop:
    1. Thought: Reason about current state
    2. Action: Invoke agents or tools
    3. Observation: Record results in scratchpad
    4. Repeat until complete
    """
    
    def __init__(
        self,
        openai_api_key: str,
        search_agents: List[SearchAgentPort],
        review_agents: List[ReviewAgentPort],
        promo_agent: PromoAgentPort,
        model: str = "gpt-4o",
        # Deep research components (optional)
        entity_extractor = None,
        query_generator = None,
        web_search_agent = None,
        knowledge_synthesizer = None
    ):
        self.search_agents = search_agents
        self.review_agents = review_agents
        self.promo_agent = promo_agent
        
        # Deep research agents (optional)
        self.entity_extractor = entity_extractor
        self.query_generator = query_generator
        self.web_search_agent = web_search_agent
        self.knowledge_synthesizer = knowledge_synthesizer
        self.research_enabled = all([entity_extractor, query_generator, web_search_agent, knowledge_synthesizer])
        
        # Set API key in environment for PydanticAI
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Create PydanticAI agent for reasoning
        self.reasoning_agent = Agent(
            model=OpenAIModel(model),
            system_prompt=self._get_system_prompt(),
            retries=2
        )
        
        # Define tools for the agent
        self.reasoning_agent.tool(self._generate_questions_tool)
        self.reasoning_agent.tool(self._evaluate_data_quality_tool)
        self.reasoning_agent.tool(self._decide_next_phase_tool)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the reasoning agent."""
        return """
You are a Planning Agent orchestrating an event discovery workflow using REACT pattern.

Your responsibilities:
1. REASON about the current state and what needs to be done
2. ACT by deciding which phase to execute next
3. OBSERVE results and update your understanding
4. GENERATE questions about data gaps or uncertainties

Workflow phases:
- SEARCHING: Gather events from multiple sources in parallel
- REVIEWING: Validate and enrich events with review agents
- SYNTHESIZING: Generate the final promo
- COMPLETE: Workflow finished

At each step:
1. Analyze the current state (events found, confidence scores, questions)
2. Identify gaps or issues
3. Generate follow-up questions if needed
4. Decide the next phase with clear reasoning

Be thorough but efficient. Generate questions when you see:
- Events with missing venue information
- Events with broken URLs
- Events without dates
- Suspicious or low-confidence data

Always provide clear reasoning for your decisions.
"""
    
    async def run_workflow(self, initial_state: PlanningState) -> PlanningState:
        """
        Run the complete agentic workflow using REACT.
        
        This is the main orchestration loop.
        """
        state = initial_state
        max_iterations = 10  # Safety limit
        iteration = 0
        
        try:
            while state.phase != AgentPhase.COMPLETE and iteration < max_iterations:
                iteration += 1
                
                # REACT LOOP
                print(f"\n{'='*60}")
                print(f"ITERATION {iteration}: Phase = {state.phase.value}")
                print(f"{'='*60}")
                
                if state.phase == AgentPhase.INITIALIZING:
                    state = await self._initialize_phase(state)
                
                elif state.phase == AgentPhase.SEARCHING:
                    state = await self._search_phase(state)
                
                elif state.phase == AgentPhase.REVIEWING:
                    state = await self._review_phase(state)
                
                elif state.phase == AgentPhase.RESEARCHING:
                    state = await self._research_phase(state)
                
                elif state.phase == AgentPhase.SYNTHESIZING:
                    state = await self._synthesize_phase(state)
                
                else:
                    break
            
            if iteration >= max_iterations:
                state.add_observation(
                    agent="PlanningAgent",
                    thought="Max iterations reached, completing workflow",
                    confidence=0.7
                )
                state.mark_complete()
            
        except Exception as e:
            state.mark_failed(str(e))
            state.add_observation(
                agent="PlanningAgent",
                thought=f"Workflow failed: {str(e)}",
                confidence=0.0
            )
        
        return state
    
    async def _initialize_phase(self, state: PlanningState) -> PlanningState:
        """Initialize the workflow."""
        state.add_observation(
            agent="PlanningAgent",
            thought="Starting workflow. First step: search for events from multiple sources.",
            action="transition_to_search",
            result="Moving to SEARCHING phase",
            confidence=1.0
        )
        state.phase = AgentPhase.SEARCHING
        return state
    
    async def _search_phase(self, state: PlanningState) -> PlanningState:
        """Execute the search phase with parallel agents."""
        state.add_observation(
            agent="PlanningAgent",
            thought=f"Need to gather events. I have {len(self.search_agents)} search agents available.",
            action="invoke_parallel_search_agents",
            confidence=1.0
        )
        
        # Run search agents in parallel
        print("🔍 Running search agents in parallel...")
        results = await run_search_agents_parallel(self.search_agents)
        
        # Process results
        all_events = []
        for result in results:
            if result.success:
                all_events.extend(result.events)
                state.search_sources_completed.append(result.agent_name)
                state.add_observation(
                    agent=f"SearchAgent:{result.agent_name}",
                    thought=f"Searching {result.agent_name} API",
                    action="search_events",
                    result=f"Found {len(result.events)} events in {result.execution_time_seconds:.2f}s",
                    confidence=result.confidence
                )
            else:
                state.add_observation(
                    agent=f"SearchAgent:{result.agent_name}",
                    thought=f"Searching {result.agent_name} API",
                    action="search_events",
                    result=f"Failed: {result.error_message}",
                    confidence=0.0
                )
        
        # Deduplicate events
        seen_titles = set()
        unique_events = []
        for event in all_events:
            title_lower = event.title.lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_events.append(event)
        
        state.events_found = unique_events
        
        state.add_observation(
            agent="PlanningAgent",
            thought=f"Search phase complete. Found {len(unique_events)} unique events from {len(state.search_sources_completed)} sources.",
            action="analyze_search_results",
            result=f"Total: {len(unique_events)} unique events",
            confidence=0.9
        )
        
        # Generate questions about the data
        questions = await self._reason_and_generate_questions(state)
        state.questions_to_investigate.extend(questions)
        
        # Decide next phase
        if len(unique_events) > 0:
            state.add_observation(
                agent="PlanningAgent",
                thought="Events found. Need to validate and enrich them.",
                action="transition_to_review",
                result="Moving to REVIEWING phase",
                confidence=0.95
            )
            state.phase = AgentPhase.REVIEWING
        else:
            state.add_observation(
                agent="PlanningAgent",
                thought="No events found. Cannot proceed.",
                action="skip_to_complete",
                result="Moving to COMPLETE (no events)",
                confidence=1.0
            )
            state.mark_complete()
        
        return state
    
    async def _review_phase(self, state: PlanningState) -> PlanningState:
        """Execute the review phase with agent swarm."""
        state.add_observation(
            agent="PlanningAgent",
            thought=f"Need to validate {len(state.events_found)} events. Will use {len(self.review_agents)} review agents in parallel swarm.",
            action="invoke_review_swarm",
            confidence=1.0
        )
        
        # Run review swarm
        print(f"🔬 Running review swarm on {len(state.events_found)} events...")
        enriched_events = await run_review_swarm(
            events=state.events_found,
            agents=self.review_agents,
            max_concurrent=5
        )
        
        state.events_reviewed = enriched_events
        
        # Analyze quality
        verified_count = sum(1 for e in enriched_events if e.verified)
        avg_confidence = sum(e.confidence_score for e in enriched_events) / len(enriched_events) if enriched_events else 0
        
        state.add_observation(
            agent="PlanningAgent",
            thought=f"Review phase complete. {verified_count}/{len(enriched_events)} events verified.",
            action="analyze_review_results",
            result=f"Verified: {verified_count}, Avg confidence: {avg_confidence:.2f}",
            confidence=avg_confidence
        )
        
        # Answer questions based on review results
        for question in state.questions_to_investigate:
            if not question.answered:
                # Simple heuristic - mark as answered if we have good confidence
                if avg_confidence > 0.7:
                    question.answered = True
                    question.answer = f"Resolved via review swarm (confidence: {avg_confidence:.2f})"
        
        # Decide next phase
        if avg_confidence > 0.6:
            # Check if deep research is enabled
            if self.research_enabled and state.research_enabled:
                state.add_observation(
                    agent="PlanningAgent",
                    thought="Data quality good. Will run deep research for richer context.",
                    action="transition_to_research",
                    result="Moving to RESEARCHING phase",
                    confidence=0.95
                )
                state.phase = AgentPhase.RESEARCHING
            else:
                state.add_observation(
                    agent="PlanningAgent",
                    thought="Data quality is sufficient. Ready to generate promo.",
                    action="transition_to_synthesize",
                    result="Moving to SYNTHESIZING phase",
                    confidence=0.95
                )
                state.phase = AgentPhase.SYNTHESIZING
        else:
            state.add_observation(
                agent="PlanningAgent",
                thought="Data quality is low but proceeding anyway.",
                action="transition_to_synthesize",
                result="Moving to SYNTHESIZING phase (low confidence)",
                confidence=0.7
            )
            state.phase = AgentPhase.SYNTHESIZING
        
        return state
    
    async def _research_phase(self, state: PlanningState) -> PlanningState:
        """Execute the deep research phase (optional)."""
        
        if not self.research_enabled:
            # Skip research if not enabled
            state.add_observation(
                agent="PlanningAgent",
                thought="Research not enabled, skipping to synthesis.",
                action="skip_research",
                result="Moving to SYNTHESIZING phase",
                confidence=1.0
            )
            state.phase = AgentPhase.SYNTHESIZING
            return state
        
        state.add_observation(
            agent="PlanningAgent",
            thought=f"Starting deep research on {len(state.events_reviewed)} verified events.",
            action="invoke_research_pipeline",
            confidence=1.0
        )
        
        print(f"🔬 RESEARCHING PHASE: Deep research on {len(state.events_reviewed)} events...")
        
        # Import research models
        from app.core.domain.research_models import ResearchQuery, EventResearch
        
        import asyncio
        
        async def research_single_event(enriched):
            """Research a single event."""
            event = enriched.event
            
            # Step 1: Extract entities
            entities = await self.entity_extractor.extract_entities(event)
            
            state.add_observation(
                agent="EntityExtractionAgent",
                thought=f"Analyzing '{event.title}'",
                action="extract_entities",
                result=f"Found {len(entities)} entities",
                confidence=0.9
            )
            
            # Step 2: Generate targeted research queries using AI
            queries = await self.query_generator.generate_queries(event, entities)
            
            state.add_observation(
                agent="QueryGenerationAgent",
                thought=f"Formulating research strategy for {len(entities)} entities",
                action="generate_queries",
                result=f"Generated {len(queries)} targeted queries (priorities: {[q.priority for q in queries[:5]]})",
                confidence=0.95
            )
            
            # Step 3: Research with web search
            results = []
            for query in queries:
                result = await self.web_search_agent.research(query)
                results.append(result)
                
                if result.confidence > 0:
                    state.add_observation(
                        agent="WebSearchAgent",
                        thought=f"Researching '{query.query}'",
                        action="web_search",
                        result=f"Found {len(result.facts)} facts",
                        confidence=result.confidence
                    )
            
            # Step 4: Synthesize knowledge
            event_research = await self.knowledge_synthesizer.synthesize(
                event=event,
                entities=entities,
                research_results=results
            )
            
            state.add_observation(
                agent="KnowledgeSynthesisAgent",
                thought=f"Synthesizing research for '{event.title}'",
                action="synthesize_knowledge",
                result=f"Created narrative with {len(event_research.key_insights)} insights",
                confidence=event_research.overall_confidence
            )
            
            return event_research
        
        # Research events in batches (5 at a time)
        semaphore = asyncio.Semaphore(5)
        
        async def research_with_limit(enriched):
            async with semaphore:
                try:
                    return await research_single_event(enriched)
                except Exception as e:
                    print(f"Research failed for {enriched.event.title}: {e}")
                    # Return minimal research
                    from app.core.domain.research_models import EventResearch
                    return EventResearch(
                        event_title=enriched.event.title,
                        entities=[],
                        queries=[],
                        results=[],
                        synthesized_narrative=enriched.event.description or enriched.event.title,
                        key_insights=[],
                        overall_confidence=0.5
                    )
        
        # Research all events
        events_researched = await asyncio.gather(
            *[research_with_limit(e) for e in state.events_reviewed]
        )
        
        state.events_researched = events_researched
        
        # Summary statistics
        total_entities = sum(len(er.entities) for er in events_researched)
        total_facts = sum(len(r.facts) for r in sum([er.results for er in events_researched], []))
        avg_confidence = sum(er.overall_confidence for er in events_researched) / len(events_researched) if events_researched else 0
        
        state.add_observation(
            agent="PlanningAgent",
            thought="Deep research complete. Rich context gathered.",
            action="analyze_research_results",
            result=f"Researched {len(events_researched)} events: {total_entities} entities, {total_facts} facts, conf={avg_confidence:.2f}",
            confidence=avg_confidence
        )
        
        # Move to synthesis
        state.phase = AgentPhase.SYNTHESIZING
        return state
    
    async def _synthesize_phase(self, state: PlanningState) -> PlanningState:
        """Execute the synthesis phase to generate promo."""
        state.add_observation(
            agent="PlanningAgent",
            thought="Ready to generate the final promo with enriched events.",
            action="invoke_promo_agent",
            confidence=1.0
        )
        
        # Generate promo
        print("🎤 Generating wrestling promo...")
        promo_result = await self.promo_agent.generate_promo(
            events=state.events_reviewed,
            planning_context=state,
            research_results=state.events_researched  # Pass research results!
        )
        
        state.promo_generated = promo_result.promo_text
        
        state.add_observation(
            agent="PromoAgent",
            thought="Generating final promo",
            action="generate_promo",
            result=f"Generated promo with {len(promo_result.events_included)} events",
            confidence=promo_result.confidence
        )
        
        state.add_observation(
            agent="PlanningAgent",
            thought="Promo generated. Workflow complete.",
            action="finalize",
            result="SUCCESS",
            confidence=promo_result.confidence
        )
        
        state.mark_complete()
        
        return state
    
    async def _reason_and_generate_questions(self, state: PlanningState) -> List[Question]:
        """
        Use the reasoning agent to generate questions about the current data.
        """
        # Analyze events for issues
        events_without_dates = [e for e in state.events_found if not e.start_time]
        events_without_urls = [e for e in state.events_found if not e.url]
        events_without_location = [e for e in state.events_found if not e.location]
        
        questions = []
        
        if events_without_dates:
            questions.append(Question(
                text=f"How can we determine dates for {len(events_without_dates)} events without start times?",
                priority=8
            ))
        
        if events_without_urls:
            questions.append(Question(
                text=f"Should we exclude {len(events_without_urls)} events without URLs?",
                priority=5
            ))
        
        if events_without_location:
            questions.append(Question(
                text=f"Can we verify venue details for {len(events_without_location)} events?",
                priority=7
            ))
        
        return questions
    
    # Tools for the reasoning agent
    async def _generate_questions_tool(self, ctx: RunContext[PlanningState], topic: str) -> str:
        """Generate questions about a specific topic."""
        return f"Questions generated about: {topic}"
    
    async def _evaluate_data_quality_tool(
        self, 
        ctx: RunContext[PlanningState], 
        events_count: int,
        verified_count: int
    ) -> str:
        """Evaluate the quality of the data."""
        ratio = verified_count / events_count if events_count > 0 else 0
        if ratio > 0.8:
            return "Data quality is EXCELLENT"
        elif ratio > 0.6:
            return "Data quality is GOOD"
        elif ratio > 0.4:
            return "Data quality is FAIR"
        else:
            return "Data quality is POOR"
    
    async def _decide_next_phase_tool(
        self,
        ctx: RunContext[PlanningState],
        current_phase: str,
        data_quality: str
    ) -> str:
        """Decide the next phase based on current state."""
        phase_transitions = {
            "initializing": "searching",
            "searching": "reviewing",
            "reviewing": "synthesizing",
            "synthesizing": "complete"
        }
        return phase_transitions.get(current_phase, "complete")

