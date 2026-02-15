"""Query Generation Agent - Generates targeted research queries using PydanticAI."""
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import json

from app.core.domain.models import Event
from app.core.domain.research_models import Entity, ResearchQuery
from app.core.ports.research_port import QueryGenerationPort


class QueryGenerationAgent(QueryGenerationPort):
    """Agent that generates sophisticated, targeted research queries using GPT-5-mini-2025-08-07."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-5-mini-2025-08-07"):
        """Initialize the query generation agent."""
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.agent = Agent(
            model=OpenAIModel(model),
            system_prompt="""You are an expert research query generator for event information.

Your task is to analyze an event and its extracted entities, then generate SPECIFIC, TARGETED research queries that will gather the most valuable information for enriching a wrestling-style event promo.

**SPECIAL FOCUS FOR MUSIC EVENTS:**
When the event involves MUSIC (concerts, shows, performances), prioritize queries about:
- Hit songs and chart performance ("What are [Artist]'s biggest hit songs and their chart positions?")
- Albums and discography ("What are [Artist]'s most critically acclaimed albums?")
- Current tours and recent performances ("What is [Artist]'s current tour schedule and recent performances?")
- Awards and accolades ("What major music awards has [Artist] won?")
- Collaborations with other artists ("What notable collaborations has [Artist] done?")
- Music style evolution ("How has [Artist]'s sound evolved over their career?")
- Genre influence ("What impact has [Artist] had on the [genre] scene?")

GOOD QUERIES (specific, actionable):
MUSIC EVENTS:
- "What are ASTN's biggest hit songs and their chart performance?"
- "What albums has Hot Mulligan released and which tracks are fan favorites?"
- "What is Sarah Millican's current tour schedule and recent special releases?"
- "What collaborations has Wynton Marsalis done with other jazz legends?"
- "How many Grammy Awards has the Jazz At Lincoln Center Orchestra won?"
- "What is Texas Hippie Coalition's most popular album and breakthrough moment?"

NON-MUSIC EVENTS:
- "What is the Bayou Music Center known for in Houston's music scene?"
- "What is the significance of Durango Fest in Houston's music culture?"
- "What are the key themes in A Christmas Carol at the Alley Theatre?"

BAD QUERIES (too vague):
- "Mac Miller information"
- "Bayou Music Center"
- "Tell me about Thundercat"

QUERY TYPES (choose the most appropriate):
- biographical: Artist/performer background, career, achievements, style
- contextual: General background/context information
- current: Recent/latest developments, announcements, news, tour updates
- relational: Relationships, collaborations between entities
- cultural_impact: Why this matters, significance, cultural influence
- venue_history: Venue significance, notable past events, reputation
- genre_overview: Music/performance genre, scene, style information
- collaboration: Collaborative work, partnerships, joint projects
- historical: Historical background, origins, legacy, past significance
- awards: Awards, accolades, honors, achievements, Grammy/Tony/Emmy wins

PRIORITIES (1-10):
- 10: Critical to understanding the event (main artist/act - ESPECIALLY hits, albums, current tour for musicians)
- 7-9: Important context (venue, supporting acts, genre, awards, collaborations)
- 4-6: Nice-to-have enrichment (related artists, history, style evolution)
- 1-3: Optional background (tangential info)

**RATE LIMIT AWARENESS**: Generate ONLY 2-3 high-quality queries (not 3-6) to conserve API quota!
For MUSIC events, ensure at least 1-2 queries focus on hits, albums, tours, or awards!

OUTPUT FORMAT (JSON):
{
  "queries": [
    {"query": "...", "priority": 10, "entity_name": "...", "query_type": "biographical"},
    {"query": "...", "priority": 9, "entity_name": "...", "query_type": "current"}
  ],
  "reasoning": "Brief explanation of strategy"
}
"""
        )
    
    async def generate_queries(
        self,
        event: Event,
        entities: List[Entity]
    ) -> List[ResearchQuery]:
        """Generate prioritized research queries based on event and entities."""
        
        if not entities:
            return []
        
        # Prepare context for the agent
        entity_context = "\n".join([
            f"- {e.name} ({e.type}, confidence: {e.confidence:.2f})"
            for e in entities
        ])
        
        # Detect if this is a music event
        categories = getattr(event, 'categories', []) or []
        is_music_event = 'music' in categories or any(
            keyword in event.title.lower() 
            for keyword in ['concert', 'tour', 'show', 'live music', 'orchestra', 'band', 'singer', 'rapper', 'dj']
        )
        
        music_hint = ""
        if is_music_event:
            music_hint = """
🎸 THIS IS A MUSIC EVENT! 🎸
CRITICAL: Generate queries that focus on:
- Hit songs and chart performance
- Albums and discography highlights
- Current tour information and recent performances
- Awards and music accolades
- Notable collaborations with other artists
- Genre influence and style evolution

Make at least 1-2 queries specifically about the artist's MUSIC (hits, albums, tours, awards)!
"""
        
        prompt = f"""Generate research queries for this event:

EVENT: {event.title}
DESCRIPTION: {event.description or 'N/A'}
LOCATION: {event.location or 'N/A'}
DATE: {event.start_time or 'Date not specified'}
CATEGORIES: {', '.join(categories) if categories else 'N/A'}
{music_hint}
EXTRACTED ENTITIES:
{entity_context}

⚠️ RATE LIMIT CONSTRAINT: Generate ONLY 2-3 targeted queries (NOT 3-6) to stay under API quota limits!
Focus on the MOST IMPORTANT entities (highest confidence) and queries that will reveal the most compelling stories, achievements, or cultural significance.
Prioritize quality over quantity - each query should be high-impact!
{"For music events, prioritize 1-2 queries about hit songs, albums, tours, or awards!" if is_music_event else ""}"""
        
        try:
            result = await self.agent.run(prompt)
            response_text = result.data if hasattr(result, 'data') else str(result.output)
            
            # Try to parse as JSON
            try:
                # Extract JSON from response (might have markdown code blocks)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Convert to ResearchQuery objects
                queries = []
                for q in data.get("queries", []):
                    try:
                        queries.append(ResearchQuery(
                            query=q["query"],
                            priority=q.get("priority", 5),
                            entity_name=q.get("entity_name", ""),
                            query_type=q.get("query_type", "contextual")
                        ))
                    except Exception as e:
                        # Skip queries with invalid data
                        print(f"⚠️  Skipping invalid query: {e}")
                        continue
                
                # Sort by priority (highest first)
                queries.sort(key=lambda x: x.priority, reverse=True)
                
                return queries
                
            except (json.JSONDecodeError, ValueError, KeyError) as parse_error:
                print(f"⚠️  Failed to parse query generation response: {parse_error}")
                return self._generate_fallback_queries(event, entities)
            
        except Exception as e:
            # Fallback to simple queries if agent fails
            print(f"⚠️  Query generation agent failed: {e}")
            return self._generate_fallback_queries(event, entities)
    
    def _generate_fallback_queries(
        self,
        event: Event,
        entities: List[Entity]
    ) -> List[ResearchQuery]:
        """Generate simple fallback queries if agent fails."""
        queries = []
        for i, entity in enumerate(entities[:3]):
            queries.append(ResearchQuery(
                query=f"{entity.name} information",
                priority=10 - i,
                entity_name=entity.name,
                query_type="biographical"
            ))
        return queries

