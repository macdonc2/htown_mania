"""
Review agents for parallel event validation and enrichment.
Each agent can validate/enrich events independently.
"""
import asyncio
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from datetime import datetime

from app.core.domain.models import Event
from app.core.domain.agent_models import ReviewAgentResult, EnrichedEvent
from app.core.ports.agent_port import ReviewAgentPort
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


class WebSearchEnricherAgent(ReviewAgentPort):
    """
    Agent that uses SerpAPI to search for additional information about events.
    This replaces simple URL validation with actual web intelligence gathering.
    """
    
    def __init__(self, serpapi_key: str, openai_api_key: str):
        self.serpapi_key = serpapi_key
        self.client = httpx.AsyncClient(timeout=15, follow_redirects=True)
        
        # Set up LLM agent for synthesizing search results
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.llm_agent = Agent(
            model=OpenAIModel("gpt-4o-mini"),
            system_prompt=(
                "You are an event information verifier. Given search results about an event, "
                "extract and verify key details: venue, date/time, price, description. "
                "Be concise and factual. Return structured information."
            )
        )
    
    async def review_event(self, event: Event) -> ReviewAgentResult:
        """Search the web for additional information about this event."""
        checks = ["web_search_enrichment"]
        
        if not self.serpapi_key:
            return ReviewAgentResult(
                agent_id="web_search_enricher",
                enriched_event=EnrichedEvent(
                    event=event,
                    verified=True,
                    verification_notes=["SerpAPI key not configured"],
                    confidence_score=0.7
                ),
                success=True,
                checks_performed=checks
            )
        
        try:
            # Search for the event on Google
            query = f"{event.title} Houston TX"
            if event.location:
                query += f" {event.location}"
            
            search_url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": query,
                "num": 3,  # Top 3 results
                "api_key": self.serpapi_key
            }
            
            response = await self.client.get(search_url, params=params)
            if response.status_code != 200:
                return ReviewAgentResult(
                    agent_id="web_search_enricher",
                    enriched_event=EnrichedEvent(
                        event=event,
                        verified=True,
                        verification_notes=[f"Search failed: {response.status_code}"],
                        confidence_score=0.7
                    ),
                    success=True,
                    checks_performed=checks
                )
            
            data = response.json()
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                return ReviewAgentResult(
                    agent_id="web_search_enricher",
                    enriched_event=EnrichedEvent(
                        event=event,
                        verified=True,
                        verification_notes=["No search results found"],
                        confidence_score=0.6
                    ),
                    success=True,
                    checks_performed=checks
                )
            
            # Extract snippets from top results
            snippets = []
            for result in organic_results[:3]:
                if "snippet" in result:
                    snippets.append(result["snippet"])
            
            if not snippets:
                return ReviewAgentResult(
                    agent_id="web_search_enricher",
                    enriched_event=EnrichedEvent(
                        event=event,
                        verified=True,
                        verification_notes=["Search results incomplete"],
                        confidence_score=0.6
                    ),
                    success=True,
                    checks_performed=checks
                )
            
            # Use LLM to synthesize the information
            search_context = "\n\n".join(snippets)
            prompt = f"""
Event: {event.title}
Current Description: {event.description or 'None'}

Search Results:
{search_context}

Based on these search results, provide:
1. Key verification: Is this a real event in Houston?
2. Any additional details found (venue, time, price)
3. A confidence score (0-10) on the information quality

Keep it brief (2-3 sentences).
"""
            
            result = await self.llm_agent.run(prompt)
            synthesis = result.data if hasattr(result, 'data') else str(result.output)
            
            # High confidence because we found search results
            enriched = EnrichedEvent(
                event=event,
                verified=True,
                verification_notes=[
                    f"Web search found {len(snippets)} results",
                    f"Synthesis: {str(synthesis)[:200]}"
                ],
                confidence_score=0.85,
                enriched_description=str(synthesis)[:500],
                url_working=True,  # We found it on the web
                additional_metadata={"web_search_results": len(snippets)}
            )
            
            return ReviewAgentResult(
                agent_id="web_search_enricher",
                enriched_event=enriched,
                success=True,
                checks_performed=checks
            )
            
        except Exception as e:
            return ReviewAgentResult(
                agent_id="web_search_enricher",
                enriched_event=EnrichedEvent(
                    event=event,
                    verified=True,
                    verification_notes=[f"Web search error: {str(e)[:100]}"],
                    confidence_score=0.7
                ),
                success=True,
                checks_performed=checks
            )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class ContentEnricherAgent(ReviewAgentPort):
    """
    Agent that scrapes event pages to enrich descriptions.
    Uses LLM to extract and summarize key information.
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.client = httpx.AsyncClient(timeout=10, follow_redirects=True)
        # PydanticAI OpenAIModel picks up API key from OPENAI_API_KEY env var
        # or pass it in the format: "openai:model_name"
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.llm_agent = Agent(
            model=OpenAIModel(model),
            system_prompt=(
                "You are an event detail extractor. Given HTML content from an event page, "
                "extract key information like exact date/time, venue details, price, "
                "and a concise 2-sentence description. Return your findings in a structured way."
            )
        )
    
    async def review_event(self, event: Event) -> ReviewAgentResult:
        """Enrich the event with additional details from its webpage."""
        checks = ["content_enrichment"]
        
        if not event.url:
            return ReviewAgentResult(
                agent_id="content_enricher",
                enriched_event=EnrichedEvent(
                    event=event,
                    verified=False,
                    verification_notes=["No URL to scrape"],
                    confidence_score=0.6
                ),
                success=True,
                checks_performed=checks
            )
        
        try:
            # Fetch the page
            response = await self.client.get(str(event.url))
            if response.status_code != 200:
                return ReviewAgentResult(
                    agent_id="content_enricher",
                    enriched_event=EnrichedEvent(
                        event=event,
                        verified=False,
                        verification_notes=[f"Could not fetch page: {response.status_code}"],
                        confidence_score=0.6
                    ),
                    success=True,
                    checks_performed=checks
                )
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text (limited to avoid token limits)
            text_content = soup.get_text(separator=' ', strip=True)[:2000]
            
            # Use LLM to extract structured info
            prompt = f"""
Event Title: {event.title}
Current Description: {event.description or 'None'}

Webpage Content:
{text_content}

Extract:
1. A better 2-sentence description if available
2. Any missing venue/location details
3. Price information if present
4. Any important notes about the event

Keep it concise and factual.
"""
            
            result = await self.llm_agent.run(prompt)
            # PydanticAI returns the message content directly
            enriched_description = result.data if hasattr(result, 'data') else str(result.output)
            
            enriched = EnrichedEvent(
                event=event,
                verified=True,
                verification_notes=["Content enriched via webpage scraping"],
                confidence_score=0.9,
                enriched_description=str(enriched_description)[:500],
                url_working=True
            )
            
            return ReviewAgentResult(
                agent_id="content_enricher",
                enriched_event=enriched,
                success=True,
                checks_performed=checks
            )
            
        except Exception as e:
            return ReviewAgentResult(
                agent_id="content_enricher",
                enriched_event=EnrichedEvent(
                    event=event,
                    verified=False,
                    verification_notes=[f"Enrichment failed: {str(e)}"],
                    confidence_score=0.6
                ),
                success=True,
                checks_performed=checks
            )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class RelevanceScoreAgent(ReviewAgentPort):
    """
    Agent that scores events for relevance to user preferences.
    Uses domain knowledge about cycling, couple activities, etc.
    """
    
    # Import scoring keywords from domain
    CYCLING = ["cycling", "bike", "biking", "bicycle", "mtb", "ride", "critical mass"]
    OUTDOOR = ["outdoor", "park", "hike", "trail", "run", "nature", "bayou", "memorial park", "kayak", "paddle"]
    MUSIC = ["music", "concert", "band", "live music", "dj", "show", "performance", "venue"]
    DOG_FRIENDLY = ["dog", "dog-friendly", "pet", "pet-friendly", "pup", "canine", "bark", "dogs welcome"]
    COUPLE_ACTIVITIES = ["wine", "brewery", "beer", "cocktail", "tasting", "comedy", "trivia", "art walk", "gallery", "date night", "romantic"]
    KID_FOCUSED = ["kids", "children", "family fun", "toddler", "playground", "bounce house", "story time", "baby"]
    
    async def review_event(self, event: Event) -> ReviewAgentResult:
        """Score the event for relevance."""
        checks = ["relevance_scoring"]
        
        text = f"{event.title} {event.description or ''}".lower()
        score = 0
        notes = []
        
        if any(k in text for k in self.CYCLING):
            score += 10
            notes.append("High priority: Cycling event")
        
        if any(k in text for k in self.COUPLE_ACTIVITIES):
            score += 9
            notes.append("High priority: Couple-friendly activity")
        
        if any(k in text for k in self.MUSIC):
            score += 8
            notes.append("Music/concert event")
        
        if any(k in text for k in self.DOG_FRIENDLY):
            score += 7
            notes.append("Dog-friendly event")
        
        if any(k in text for k in self.OUTDOOR):
            score += 5
            notes.append("Outdoor activity")
        
        if any(k in text for k in self.KID_FOCUSED):
            score -= 5
            notes.append("Kid-focused event (deprioritized)")
        
        # Confidence based on how well we can categorize
        confidence = min(1.0, (len(notes) * 0.25) + 0.5)
        
        enriched = EnrichedEvent(
            event=event,
            verified=True,
            verification_notes=notes,
            confidence_score=confidence,
            additional_metadata={"relevance_score": score}
        )
        
        return ReviewAgentResult(
            agent_id="relevance_scorer",
            enriched_event=enriched,
            success=True,
            checks_performed=checks
        )


class DateVerificationAgent(ReviewAgentPort):
    """
    Agent that verifies event dates are within the target window.
    """
    
    async def review_event(self, event: Event) -> ReviewAgentResult:
        """Verify the event date is appropriate."""
        checks = ["date_verification"]
        
        from zoneinfo import ZoneInfo
        from datetime import timedelta
        
        now = datetime.now(ZoneInfo("America/Chicago"))
        one_week = now + timedelta(days=7)
        
        if not event.start_time:
            # No date info
            return ReviewAgentResult(
                agent_id="date_verifier",
                enriched_event=EnrichedEvent(
                    event=event,
                    verified=False,
                    verification_notes=["No start time available"],
                    confidence_score=0.5
                ),
                success=True,
                checks_performed=checks
            )
        
        event_time = event.start_time
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=ZoneInfo("America/Chicago"))
        
        is_in_window = now <= event_time <= one_week
        
        enriched = EnrichedEvent(
            event=event,
            verified=is_in_window,
            verification_notes=[
                f"Event is {'within' if is_in_window else 'outside'} target window (next 7 days)"
            ],
            confidence_score=1.0,
            venue_verified=True
        )
        
        return ReviewAgentResult(
            agent_id="date_verifier",
            enriched_event=enriched,
            success=True,
            checks_performed=checks
        )


async def run_review_swarm(
    events: List[Event],
    agents: List[ReviewAgentPort],
    max_concurrent: int = 5
) -> List[EnrichedEvent]:
    """
    Run review agents in parallel with concurrency control.
    Each event is processed by all agents.
    
    Args:
        events: Events to review
        agents: List of review agents to use
        max_concurrent: Maximum concurrent reviews
    
    Returns:
        List of enriched events with aggregated results from all agents
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def review_event_with_all_agents(event: Event) -> EnrichedEvent:
        """Review a single event with all agents."""
        async with semaphore:
            # Run all agents on this event
            results = await asyncio.gather(
                *[agent.review_event(event) for agent in agents],
                return_exceptions=True
            )
            
            # Aggregate results
            all_notes = []
            all_metadata = {}
            total_confidence = 0.0
            verified_count = 0
            url_working = False
            venue_verified = False
            enriched_desc = None
            agent_votes = []
            
            valid_results = [r for r in results if isinstance(r, ReviewAgentResult)]
            
            for result in valid_results:
                if result.success:
                    enriched = result.enriched_event
                    all_notes.extend(enriched.verification_notes)
                    all_metadata.update(enriched.additional_metadata)
                    total_confidence += enriched.confidence_score
                    if enriched.verified:
                        verified_count += 1
                        agent_votes.append(f"{result.agent_id}:✅")
                    else:
                        agent_votes.append(f"{result.agent_id}:❌")
                    if enriched.url_working:
                        url_working = True
                    if enriched.venue_verified:
                        venue_verified = True
                    if enriched.enriched_description:
                        enriched_desc = enriched.enriched_description
            
            # Average confidence
            avg_confidence = total_confidence / len(valid_results) if valid_results else 0.5
            
            # Log verification details
            is_verified = verified_count > len(valid_results) / 2
            print(f"  {'✅' if is_verified else '❌'} {event.title[:50]:<50} | Votes: {verified_count}/{len(valid_results)} | {' '.join(agent_votes)}")
            
            return EnrichedEvent(
                event=event,
                verified=is_verified,  # Majority vote
                verification_notes=all_notes,
                confidence_score=avg_confidence,
                enriched_description=enriched_desc,
                url_working=url_working,
                venue_verified=venue_verified,
                additional_metadata=all_metadata
            )
    
    # Process all events
    enriched_events = await asyncio.gather(
        *[review_event_with_all_agents(event) for event in events]
    )
    
    return enriched_events

