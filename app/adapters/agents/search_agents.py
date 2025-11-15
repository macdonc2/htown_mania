"""
Search agents for parallel event discovery.
Each agent specializes in a specific data source.

NOTE: Eventbrite removed - they deprecated public event search in 2019-2020.
"""
import time
from typing import List
import httpx
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil import parser as date_parser

from app.core.domain.models import Event
from app.core.domain.agent_models import SearchAgentResult
from app.core.ports.agent_port import SearchAgentPort
from app.config.settings import Settings


class TicketmasterSearchAgent(SearchAgentPort):
    """
    Search agent specialized in Ticketmaster Discovery API.
    """
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.client = httpx.AsyncClient(timeout=15)
    
    def get_agent_name(self) -> str:
        return "Ticketmaster"
    
    async def search_events(self) -> SearchAgentResult:
        """Search for events from Ticketmaster API."""
        start_time = time.time()
        events = []
        
        try:
            if not self.settings.ticketmaster_api_key:
                return SearchAgentResult(
                    agent_name=self.get_agent_name(),
                    events=[],
                    success=False,
                    error_message="No API key configured",
                    confidence=0.0,
                    execution_time_seconds=time.time() - start_time
                )
            
            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            
            start_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            params = {
                "apikey": self.settings.ticketmaster_api_key,
                "city": "Houston",
                "stateCode": "TX",
                "startDateTime": start_date,
                "endDateTime": end_date,
                "size": 50,
                "sort": "date,asc"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                return SearchAgentResult(
                    agent_name=self.get_agent_name(),
                    events=[],
                    success=False,
                    error_message=f"API returned status {response.status_code}",
                    confidence=0.0,
                    execution_time_seconds=time.time() - start_time
                )
            
            data = response.json()
            
            for item in data.get("_embedded", {}).get("events", [])[:20]:
                categories = self._categorize_event(
                    item.get("name", ""),
                    item.get("info", "")
                )
                
                # Add specific category from Ticketmaster
                classifications = item.get("classifications", [])
                if classifications:
                    genre = classifications[0].get("genre", {}).get("name", "").lower()
                    if "music" in genre or "concert" in genre:
                        if "music" not in categories:
                            categories.append("music")
                    elif "sports" in genre:
                        if "outdoor" not in categories:
                            categories.append("outdoor")
                
                start_time_dt = None
                if item.get("dates", {}).get("start"):
                    date_str = item["dates"]["start"].get("dateTime")
                    if date_str:
                        try:
                            utc_time = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            start_time_dt = utc_time.astimezone(ZoneInfo("America/Chicago"))
                        except Exception:
                            pass
                
                location = None
                if item.get("_embedded", {}).get("venues"):
                    venue = item["_embedded"]["venues"][0]
                    venue_name = venue.get("name", "")
                    city = venue.get("city", {}).get("name", "")
                    if venue_name:
                        location = f"{venue_name}, {city}" if city else venue_name
                
                events.append(Event(
                    title=item.get("name", "")[:200],
                    description=item.get("info", "")[:500] if item.get("info") else None,
                    url=item.get("url"),
                    start_time=start_time_dt,
                    location=location,
                    source="Ticketmaster",
                    categories=categories
                ))
            
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=events,
                success=True,
                confidence=0.9,
                execution_time_seconds=time.time() - start_time
            )
            
        except Exception as e:
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=[],
                success=False,
                error_message=str(e),
                confidence=0.0,
                execution_time_seconds=time.time() - start_time
            )
    
    def _categorize_event(self, title: str, description: str = "") -> List[str]:
        """Intelligently categorize events."""
        categories = []
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["bike", "cycling", "cycle", "ride", "pedal", "cyclist", "bicycle"]):
            categories.append("cycling")
        
        if any(word in text for word in ["hike", "trail", "park", "outdoor", "nature", "kayak", "run", "walk", "camping", "fishing"]):
            categories.append("outdoor")
        
        if any(word in text for word in ["concert", "music", "band", "show", "live music", "performance", "symphony", "jazz", "rock", "hip hop", "dj", "singer", "festival"]):
            categories.append("music")
        
        if any(word in text for word in ["food", "dining", "restaurant", "brunch", "dinner", "cooking", "culinary", "wine", "beer", "tasting"]):
            categories.append("food")
        
        if any(word in text for word in ["art", "museum", "gallery", "exhibition", "theater", "theatre", "play", "comedy", "film", "movie"]):
            categories.append("arts")
        
        if any(word in text for word in ["family", "kids", "children", "playground"]):
            categories.append("family")
        
        if any(word in text for word in ["sports", "game", "match", "basketball", "football", "baseball", "soccer", "hockey"]):
            categories.append("sports")
        
        return categories
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class MeetupSearchAgent(SearchAgentPort):
    """
    Search agent specialized in Meetup GraphQL API.
    """
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.client = httpx.AsyncClient(timeout=15)
    
    def get_agent_name(self) -> str:
        return "Meetup"
    
    async def search_events(self) -> SearchAgentResult:
        """Search for events from Meetup API."""
        start_time = time.time()
        events = []
        
        try:
            if not self.settings.meetup_api_key:
                return SearchAgentResult(
                    agent_name=self.get_agent_name(),
                    events=[],
                    success=False,
                    error_message="No API key configured",
                    confidence=0.0,
                    execution_time_seconds=time.time() - start_time
                )
            
            url = "https://api.meetup.com/gql"
            headers = {"Authorization": f"Bearer {self.settings.meetup_api_key}"}
            
            query = """
            query {
              keywordSearch(input: {query: "Houston", first: 20}) {
                edges {
                  node {
                    ... on Event {
                      title
                      description
                      eventUrl
                    }
                  }
                }
              }
            }
            """
            
            response = await self.client.post(url, headers=headers, json={"query": query})
            
            if response.status_code != 200:
                return SearchAgentResult(
                    agent_name=self.get_agent_name(),
                    events=[],
                    success=False,
                    error_message=f"API returned status {response.status_code}",
                    confidence=0.0,
                    execution_time_seconds=time.time() - start_time
                )
            
            data = response.json()
            
            for edge in data.get("data", {}).get("keywordSearch", {}).get("edges", []):
                node = edge.get("node", {})
                title = node.get("title", "")
                desc = node.get("description", "")
                
                categories = self._categorize_event(title, desc)
                
                events.append(Event(
                    title=title[:200],
                    description=desc[:500] if desc else None,
                    url=node.get("eventUrl"),
                    source="Meetup",
                    categories=categories
                ))
            
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=events,
                success=True,
                confidence=0.8,
                execution_time_seconds=time.time() - start_time
            )
            
        except Exception as e:
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=[],
                success=False,
                error_message=str(e),
                confidence=0.0,
                execution_time_seconds=time.time() - start_time
            )
    
    def _categorize_event(self, title: str, description: str = "") -> List[str]:
        """Intelligently categorize events."""
        categories = []
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["bike", "cycling", "cycle", "ride", "pedal", "cyclist", "bicycle"]):
            categories.append("cycling")
        
        if any(word in text for word in ["hike", "trail", "park", "outdoor", "nature", "kayak", "run", "walk", "camping", "fishing"]):
            categories.append("outdoor")
        
        if any(word in text for word in ["concert", "music", "band", "show", "live music", "performance", "symphony", "jazz", "rock", "hip hop", "dj", "singer", "festival"]):
            categories.append("music")
        
        if any(word in text for word in ["food", "dining", "restaurant", "brunch", "dinner", "cooking", "culinary", "wine", "beer", "tasting"]):
            categories.append("food")
        
        if any(word in text for word in ["art", "museum", "gallery", "exhibition", "theater", "theatre", "play", "comedy", "film", "movie"]):
            categories.append("arts")
        
        if any(word in text for word in ["family", "kids", "children", "playground"]):
            categories.append("family")
        
        if any(word in text for word in ["sports", "game", "match", "basketball", "football", "baseball", "soccer", "hockey"]):
            categories.append("sports")
        
        return categories
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class SerpAPIEventsAgent(SearchAgentPort):
    """
    Search agent using SerpAPI to scrape Google Events.
    This aggregates events from ALL sources (Eventbrite, Ticketmaster, Meetup, etc.)
    """
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.client = httpx.AsyncClient(timeout=15)
    
    def get_agent_name(self) -> str:
        return "SerpAPI (Google Events)"
    
    async def search_events(self) -> SearchAgentResult:
        """Search for events using SerpAPI's Google Events engine."""
        start_time = time.time()
        events = []
        
        try:
            if not self.settings.serpapi_key:
                return SearchAgentResult(
                    agent_name=self.get_agent_name(),
                    events=[],
                    success=False,
                    error_message="No API key configured",
                    confidence=0.0,
                    execution_time_seconds=time.time() - start_time
                )
            
            url = "https://serpapi.com/search"
            
            # Query Google Events - use "this week" for better results
            params = {
                "engine": "google_events",
                "q": "Houston TX events this week",
                "hl": "en",
                "gl": "us",
                "api_key": self.settings.serpapi_key
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f": {error_data['error']}"
                except Exception:
                    pass
                
                return SearchAgentResult(
                    agent_name=self.get_agent_name(),
                    events=[],
                    success=False,
                    error_message=error_msg,
                    confidence=0.0,
                    execution_time_seconds=time.time() - start_time
                )
            
            data = response.json()
            
            # Parse Google Events results
            for item in data.get("events_results", [])[:30]:  # Limit to 30
                title = item.get("title", "")
                
                # Parse date
                start_time_dt = None
                date_info = item.get("date", {})
                if date_info:
                    # Try to parse start_date and when
                    start_date_str = date_info.get("start_date", "")
                    when_str = date_info.get("when", "")
                    
                    if start_date_str:
                        try:
                            # Combine date and time if available
                            combined = f"{start_date_str} {when_str}" if when_str else start_date_str
                            parsed = date_parser.parse(combined, fuzzy=True)
                            # Assume Houston timezone
                            start_time_dt = parsed.replace(tzinfo=ZoneInfo("America/Chicago"))
                        except Exception:
                            pass
                
                # Get location
                location = None
                address = item.get("address", [])
                if address:
                    location = ", ".join(address) if isinstance(address, list) else str(address)
                elif item.get("venue", {}).get("name"):
                    location = item["venue"]["name"]
                
                # Get URL
                event_url = item.get("link")
                
                # Get description from venue or other fields
                description = None
                if item.get("description"):
                    description = item["description"][:500]
                
                # Categorize
                categories = self._categorize_event(title, description or "")
                
                events.append(Event(
                    title=title[:200],
                    description=description,
                    url=event_url,
                    start_time=start_time_dt,
                    location=location,
                    source="Google Events (SerpAPI)",
                    categories=categories
                ))
            
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=events,
                success=True,
                confidence=0.95,  # High confidence - Google aggregates from many sources
                execution_time_seconds=time.time() - start_time
            )
            
        except Exception as e:
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=[],
                success=False,
                error_message=str(e),
                confidence=0.0,
                execution_time_seconds=time.time() - start_time
            )
    
    def _categorize_event(self, title: str, description: str = "") -> List[str]:
        """Intelligently categorize events."""
        categories = []
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["bike", "cycling", "cycle", "ride", "pedal", "cyclist", "bicycle"]):
            categories.append("cycling")
        
        if any(word in text for word in ["hike", "trail", "park", "outdoor", "nature", "kayak", "run", "walk", "camping", "fishing"]):
            categories.append("outdoor")
        
        if any(word in text for word in ["concert", "music", "band", "show", "live music", "performance", "symphony", "jazz", "rock", "hip hop", "dj", "singer", "festival"]):
            categories.append("music")
        
        if any(word in text for word in ["food", "dining", "restaurant", "brunch", "dinner", "cooking", "culinary", "wine", "beer", "tasting"]):
            categories.append("food")
        
        if any(word in text for word in ["art", "museum", "gallery", "exhibition", "theater", "theatre", "play", "comedy", "film", "movie"]):
            categories.append("arts")
        
        if any(word in text for word in ["family", "kids", "children", "playground"]):
            categories.append("family")
        
        if any(word in text for word in ["sports", "game", "match", "basketball", "football", "baseball", "soccer", "hockey"]):
            categories.append("sports")
        
        return categories
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def run_search_agents_parallel(
    agents: List[SearchAgentPort]
) -> List[SearchAgentResult]:
    """
    Run multiple search agents in parallel.
    """
    import asyncio
    
    results = await asyncio.gather(
        *[agent.search_events() for agent in agents],
        return_exceptions=True
    )
    
    # Convert exceptions to failed results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(SearchAgentResult(
                agent_name=f"Agent_{i}",
                events=[],
                success=False,
                error_message=str(result),
                confidence=0.0,
                execution_time_seconds=0.0
            ))
        else:
            processed_results.append(result)
    
    return processed_results

