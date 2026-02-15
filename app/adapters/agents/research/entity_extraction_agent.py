"""Entity extraction agent implementation."""
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.core.domain.models import Event
from app.core.domain.research_models import Entity
from app.core.ports.research_port import EntityExtractionPort


class EntityExtractionAgent(EntityExtractionPort):
    """
    Extracts entities (artists, venues, organizers, topics, genres) from events.
    Uses GPT-5-mini for cost-effective extraction.
    """
    
    def __init__(self, openai_api_key: str):
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.agent = Agent(
            model=OpenAIModel("gpt-5-mini"),
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        return """
You are an expert at extracting entities from event descriptions.

Your task: Identify and extract ALL relevant entities from the event.

Entity Types:
- artist: Musicians, performers, speakers, entertainers
- venue: Specific locations, halls, parks, buildings
- organizer: Companies, groups, organizations hosting the event
- topic: Main themes, subjects, causes
- genre: Music genres, art styles, activity types

For each entity, extract:
- Name (be specific and use proper names)
- Type (one of the types above)
- Brief context about why it's relevant

Extract 2-6 entities per event. Be thorough but precise.

Return your response as a simple list with this format:
ENTITY: [name] | TYPE: [type] | CONTEXT: [brief context]

Example:
ENTITY: Mac Miller | TYPE: artist | CONTEXT: Deceased rapper being honored in tribute
ENTITY: Thundercat | TYPE: artist | CONTEXT: Bassist and collaborator performing at tribute
ENTITY: White Oak Music Hall | TYPE: venue | CONTEXT: Houston indie venue hosting the event
"""
    
    async def extract_entities(self, event: Event) -> List[Entity]:
        """Extract entities from an event."""
        
        prompt = f"""
Event Title: {event.title}

Description: {event.description or "No description provided"}

Location: {event.location or "Location not specified"}

Categories: {", ".join(event.categories) if event.categories else "None"}

Extract ALL relevant entities from this event.
"""
        
        try:
            result = await self.agent.run(prompt)
            response_text = result.data if hasattr(result, 'data') else str(result.output)
            
            # Parse the response
            entities = self._parse_entities(response_text)
            
            return entities
            
        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return []
    
    def _parse_entities(self, text: str) -> List[Entity]:
        """Parse entities from the LLM response."""
        entities = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('ENTITY:'):
                continue
            
            try:
                # Parse: ENTITY: [name] | TYPE: [type] | CONTEXT: [context]
                parts = line.split('|')
                if len(parts) < 2:
                    continue
                
                name = parts[0].replace('ENTITY:', '').strip()
                type_str = parts[1].replace('TYPE:', '').strip().lower()
                
                # Validate type
                valid_types = ['artist', 'venue', 'organizer', 'topic', 'genre']
                if type_str not in valid_types:
                    type_str = 'topic'  # Default fallback
                
                context = parts[2].replace('CONTEXT:', '').strip() if len(parts) > 2 else ""
                
                entities.append(Entity(
                    name=name,
                    type=type_str,  # type: ignore
                    confidence=0.9,
                    metadata={'context': context}
                ))
            except Exception as e:
                print(f"Failed to parse entity line '{line}': {e}")
                continue
        
        return entities

