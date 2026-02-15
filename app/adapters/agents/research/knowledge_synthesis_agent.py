"""Knowledge synthesis agent - combines research into narratives."""
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.core.domain.models import Event
from app.core.domain.research_models import Entity, ResearchResult, EventResearch
from app.core.ports.research_port import KnowledgeSynthesisPort


class KnowledgeSynthesisAgent(KnowledgeSynthesisPort):
    """
    Synthesizes research results into compelling narratives.
    
    Takes all the facts discovered by research agents and creates:
    1. A coherent narrative about the event
    2. Key insights that make it compelling
    3. Context that helps with storytelling
    """
    
    def __init__(self, openai_api_key: str):
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.agent = Agent(
            model=OpenAIModel("gpt-5.2-2025-12-11"),
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        return """
You are a master storyteller who synthesizes facts into compelling narratives.

Your task: Take research facts about an event and create a rich, engaging narrative.

Guidelines:
1. Weave facts together into a coherent story
2. Focus on what makes this event special or significant
3. Highlight connections, collaborations, or interesting context
4. Use vivid, engaging language
5. Keep it concise (200-300 words)
6. Be accurate - only use the facts provided

Your narrative should answer:
- Why is this event worth attending?
- What makes the people/places involved interesting?
- What's the cultural or historical significance?
- What connections or stories make this compelling?

Write in an engaging, slightly dramatic style that works for a wrestling promo!
"""
    
    async def synthesize(
        self,
        event: Event,
        entities: List[Entity],
        research_results: List[ResearchResult]
    ) -> EventResearch:
        """Synthesize all research into a narrative."""
        
        # Aggregate all facts
        all_facts = []
        all_sources = []
        
        for result in research_results:
            all_facts.extend(result.facts)
            all_sources.extend(result.sources)
        
        # Deduplicate facts (simple approach)
        unique_facts = list(dict.fromkeys(all_facts))[:15]  # Top 15 unique facts
        
        if not unique_facts:
            # No research data, create basic narrative
            return EventResearch(
                event_title=event.title,
                entities=entities,
                queries=[],
                results=research_results,
                synthesized_narrative=f"{event.title} at {event.location or 'Houston'}. {event.description or 'A must-attend event!'}",
                key_insights=["Check event details for more information"],
                overall_confidence=0.5
            )
        
        # Create synthesis prompt
        entities_str = "\n".join([
            f"- {e.name} ({e.type}): {e.metadata.get('context', '')}"
            for e in entities[:5]
        ])
        
        facts_str = "\n".join([
            f"{i+1}. {fact[:200]}"
            for i, fact in enumerate(unique_facts)
        ])
        
        prompt = f"""
Event: {event.title}
Location: {event.location or 'Houston, TX'}
Description: {event.description or 'No description provided'}

Key Entities:
{entities_str}

Research Facts Discovered:
{facts_str}

Create a compelling 200-300 word narrative about this event that:
1. Explains what makes it special
2. Highlights interesting context about the people/places
3. Connects the dots between entities
4. Makes someone want to attend

Be dramatic and engaging - this will be part of a wrestling-style promo!
"""
        
        try:
            result = await self.agent.run(prompt)
            narrative = result.data if hasattr(result, 'data') else str(result.output)
            
            # Extract key insights from facts
            key_insights = self._extract_key_insights(unique_facts, entities)
            
            # Calculate overall confidence
            avg_confidence = (
                sum(r.confidence for r in research_results) / len(research_results)
                if research_results else 0.5
            )
            
            return EventResearch(
                event_title=event.title,
                entities=entities,
                queries=[r.query for r in research_results],
                results=research_results,
                synthesized_narrative=narrative,
                key_insights=key_insights,
                overall_confidence=min(0.95, avg_confidence + 0.1)  # Boost for synthesis
            )
            
        except Exception as e:
            print(f"Knowledge synthesis failed: {e}")
            
            # Fallback: create basic narrative from facts
            basic_narrative = f"{event.title}. "
            if unique_facts:
                basic_narrative += " ".join(unique_facts[:3])
            
            return EventResearch(
                event_title=event.title,
                entities=entities,
                queries=[],
                results=research_results,
                synthesized_narrative=basic_narrative[:500],
                key_insights=self._extract_key_insights(unique_facts, entities),
                overall_confidence=0.6
            )
    
    def _extract_key_insights(self, facts: List[str], entities: List[Entity]) -> List[str]:
        """Extract 3-5 key insights from facts."""
        insights = []
        
        # Look for particularly interesting facts
        priority_keywords = [
            'grammy', 'award', 'legendary', 'iconic', 'historic', 'first', 
            'founded', 'pioneered', 'revolution', 'collaborated', 'million',
            'famous', 'renowned', 'celebrated'
        ]
        
        for fact in facts:
            fact_lower = fact.lower()
            if any(keyword in fact_lower for keyword in priority_keywords):
                # This looks like an interesting insight
                insights.append(fact[:150])
                
                if len(insights) >= 5:
                    break
        
        # If we don't have enough, add entity contexts
        if len(insights) < 3:
            for entity in entities:
                if entity.metadata.get('context'):
                    insights.append(f"{entity.name}: {entity.metadata['context']}")
                    if len(insights) >= 3:
                        break
        
        return insights[:5]

