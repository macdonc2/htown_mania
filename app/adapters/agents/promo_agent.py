"""
Promo Generator Agent - Creates the final wrestling promo.
Uses PydanticAI with the wrestling promo template.
"""
from typing import List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.core.domain.agent_models import (
    EnrichedEvent,
    PlanningState,
    PromoGenerationResult
)
from app.core.ports.agent_port import PromoAgentPort


class PromoGeneratorAgent(PromoAgentPort):
    """
    Agent that generates the final wrestling promo.
    Uses the existing template and integrates planning context.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-5.2-2025-12-11", temperature: float = 0.9):
        # Set API key in environment for PydanticAI
        import os
        os.environ["OPENAI_API_KEY"] = api_key
        self.agent = Agent(
            model=OpenAIModel(model),
            system_prompt=(
                "You are a LEGENDARY wrestling promo generator. "
                "You channel the energy of Macho Man Randy Savage and Ultimate Warrior. "
                "You create EXPLOSIVE, HIGH-ENERGY content that builds intensity. "
                "You follow the promo template EXACTLY and use ONLY the URLs provided."
            )
        )
        self.temperature = temperature
        
        # Load the promo template
        tmpl_dir = os.path.join(
            os.path.dirname(__file__), 
            "../../adapters/llm/templates"
        )
        self.env = Environment(loader=FileSystemLoader(tmpl_dir))
    
    async def generate_promo(
        self,
        events: List[EnrichedEvent],
        planning_context: PlanningState,
        research_results: List = None
    ) -> PromoGenerationResult:
        """
        Generate the wrestling promo.
        
        Args:
            events: Enriched and validated events
            planning_context: The planning state with observations and context
            research_results: Optional list of EventResearch with deep research insights
        
        Returns:
            PromoGenerationResult with the generated promo
        """
        research_results = research_results or []
        try:
            # Prepare events with scores
            events_with_scores = []
            for enriched in events:
                event = enriched.event
                # Get relevance score from metadata, or calculate it
                score = enriched.additional_metadata.get("relevance_score", 0)
                if score == 0:
                    score = self._calculate_score(event)
                
                events_with_scores.append({
                    "event": event,
                    "score": score,
                    "enriched": enriched
                })
            
            # Sort by score (descending)
            events_with_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Prepare context from planning observations
            planning_insights = self._extract_planning_insights(planning_context)
            
            # ⭐ INJECT RESEARCH INTO EACH EVENT (not after template!)
            research_by_title = {}
            if research_results:
                for research in research_results:
                    research_by_title[research.event_title] = research
            
            # Enhance events_with_scores with research data
            for item in events_with_scores:
                event = item["event"]
                research = research_by_title.get(event.title)
                
                if research:
                    # Add research narrative and insights to the event item
                    item["research_narrative"] = research.synthesized_narrative
                    item["research_insights"] = research.key_insights[:5]
                    item["research_facts_count"] = sum(len(r.facts) for r in research.results)
                else:
                    item["research_narrative"] = ""
                    item["research_insights"] = []
                    item["research_facts_count"] = 0
            
            # Render the template with research-enhanced events
            template = self.env.get_template("summary.j2")
            today = datetime.now()
            date_str = today.strftime("%A, %B %d, %Y")
            
            rendered_prompt = template.render(
                events=[item["event"] for item in events_with_scores],
                events_with_scores=events_with_scores,
                date_str=date_str,
                has_research=bool(research_results)
            )
            
            # Add planning context to the prompt
            if planning_insights:
                rendered_prompt += f"\n\n**PLANNING INSIGHTS:**\n{planning_insights}\n"
            
            # Generate with PydanticAI
            result = await self.agent.run(rendered_prompt)
            # PydanticAI returns the message content directly
            promo_text = result.data if hasattr(result, 'data') else str(result.output)
            
            # Extract which events were included (all of them, brother!)
            events_included = [
                item["event"].title
                for item in events_with_scores  # ALL events included!
            ]
            
            return PromoGenerationResult(
                promo_text=promo_text,
                events_included=events_included,
                confidence=0.95,
                generation_metadata={
                    "model": self.agent.model.model_name if hasattr(self.agent.model, "model_name") else "unknown",
                    "temperature": self.temperature,
                    "events_processed": len(events),
                    "planning_observations": len(planning_context.scratchpad)
                }
            )
            
        except Exception as e:
            # Return a fallback result
            return PromoGenerationResult(
                promo_text=f"ERROR: Could not generate promo - {str(e)}",
                events_included=[],
                confidence=0.0,
                generation_metadata={"error": str(e)}
            )
    
    def _calculate_score(self, event) -> int:
        """Calculate relevance score for an event."""
        from app.core.domain.services import (
            CYCLING, COUPLE_ACTIVITIES, MUSIC, 
            DOG_FRIENDLY, OUTDOOR, KID_FOCUSED
        )
        
        text = f"{event.title} {event.description or ''}".lower()
        score = 0
        
        if any(k in text for k in CYCLING):
            score += 10
        if any(k in text for k in COUPLE_ACTIVITIES):
            score += 9
        if any(k in text for k in MUSIC):
            score += 8
        if any(k in text for k in DOG_FRIENDLY):
            score += 7
        if any(k in text for k in OUTDOOR):
            score += 5
        if any(k in text for k in KID_FOCUSED):
            score -= 5
        
        return score
    
    def _extract_planning_insights(self, state: PlanningState) -> str:
        """
        Extract key insights from the planning state to inform promo generation.
        """
        insights = []
        
        # Check if any questions were raised
        unanswered = [q for q in state.questions_to_investigate if not q.answered]
        if unanswered:
            insights.append(
                f"Note: {len(unanswered)} questions remain unanswered, "
                "so focus on well-verified events."
            )
        
        # Check confidence from observations
        recent_obs = state.get_latest_observations(n=5)
        low_confidence_obs = [o for o in recent_obs if o.confidence < 0.7]
        if low_confidence_obs:
            insights.append(
                "Some events had lower confidence scores - emphasize the verified ones."
            )
        
        # Check sources
        if len(state.search_sources_completed) < 3:
            insights.append(
                f"Only {len(state.search_sources_completed)} source(s) completed, "
                "so data may be limited."
            )
        
        return "\n".join(insights) if insights else ""

