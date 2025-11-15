"""
API-based event aggregator for Houston events.
Pulls from multiple APIs: Eventbrite, Ticketmaster, Meetup.
"""
from typing import List
import httpx
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.core.domain.models import Event
from app.config.settings import Settings


class EventAPIAggregator:
    """Aggregates events from multiple API sources."""
    
    HOUSTON_LAT = 29.7604
    HOUSTON_LON = -95.3698
    SEARCH_RADIUS = "50mi"  # 50 mile radius from Houston
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.client = httpx.AsyncClient(timeout=15)
    
    async def get_all_events(self) -> List[Event]:
        """Fetch events from all sources."""
        all_events = []
        
        # Get events from each source
        if self.settings.eventbrite_api_key:
            all_events.extend(await self._get_eventbrite_events())
        
        if self.settings.ticketmaster_api_key:
            all_events.extend(await self._get_ticketmaster_events())
        
        if self.settings.meetup_api_key:
            all_events.extend(await self._get_meetup_events())
        
        # Deduplicate by title
        seen_titles = set()
        unique_events = []
        for event in all_events:
            title_lower = event.title.lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_events.append(event)
        
        return unique_events
    
    async def _get_eventbrite_events(self) -> List[Event]:
        """Fetch events from Eventbrite API."""
        events = []
        try:
            # Eventbrite Event Search API
            url = "https://www.eventbriteapi.com/v3/events/search/"
            headers = {"Authorization": f"Bearer {self.settings.eventbrite_api_key}"}
            
            # Get events for TODAY through next 3 days only
            start_date = datetime.now().isoformat()
            end_date = (datetime.now() + timedelta(days=3)).isoformat()
            
            params = {
                "location.latitude": self.HOUSTON_LAT,
                "location.longitude": self.HOUSTON_LON,
                "location.within": self.SEARCH_RADIUS,
                "start_date.range_start": start_date,
                "start_date.range_end": end_date,
                "expand": "venue,category",
                "page_size": 50
            }
            
            response = await self.client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("events", [])[:20]:  # Limit to 20
                    categories = self._categorize_event(
                        item.get("name", {}).get("text", ""),
                        item.get("description", {}).get("text", "")
                    )
                    
                    # Parse start time and convert to Houston (Central) time
                    start_time = None
                    if item.get("start"):
                        try:
                            utc_time = datetime.fromisoformat(item["start"].get("utc", "").replace("Z", "+00:00"))
                            # Convert to Houston time (US/Central)
                            start_time = utc_time.astimezone(ZoneInfo("America/Chicago"))
                        except:
                            pass
                    
                    # Parse location
                    location = None
                    if item.get("venue"):
                        venue_name = item["venue"].get("name", "")
                        city = item["venue"].get("address", {}).get("city", "")
                        if venue_name:
                            location = f"{venue_name}, {city}" if city else venue_name
                    
                    events.append(Event(
                        title=item.get("name", {}).get("text", "")[:200],
                        description=item.get("description", {}).get("text", "")[:500] if item.get("description") else None,
                        url=item.get("url"),
                        start_time=start_time,
                        location=location,
                        source="Eventbrite",
                        categories=categories
                    ))
        except Exception as e:
            print(f"Eventbrite API error: {e}")
        
        return events
    
    async def _get_ticketmaster_events(self) -> List[Event]:
        """Fetch events from Ticketmaster Discovery API."""
        events = []
        try:
            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            
            # Filter to TODAY through next 3 days only
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
            if response.status_code == 200:
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
                    
                    # Parse start time and convert to Houston (Central) time
                    start_time = None
                    if item.get("dates", {}).get("start"):
                        date_str = item["dates"]["start"].get("dateTime")
                        if date_str:
                            try:
                                utc_time = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                # Convert to Houston time (US/Central)
                                start_time = utc_time.astimezone(ZoneInfo("America/Chicago"))
                            except:
                                pass
                    
                    # Parse location
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
                        start_time=start_time,
                        location=location,
                        source="Ticketmaster",
                        categories=categories
                    ))
        except Exception as e:
            print(f"Ticketmaster API error: {e}")
        
        return events
    
    async def _get_meetup_events(self) -> List[Event]:
        """Fetch events from Meetup API."""
        events = []
        try:
            # Meetup GraphQL API
            url = "https://api.meetup.com/gql"
            headers = {"Authorization": f"Bearer {self.settings.meetup_api_key}"}
            
            # GraphQL query for Houston events
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
            if response.status_code == 200:
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
        except Exception as e:
            print(f"Meetup API error: {e}")
        
        return events
    
    def _categorize_event(self, title: str, description: str = "") -> List[str]:
        """Intelligently categorize events based on title and description."""
        categories = []
        text = f"{title} {description}".lower()
        
        # Cycling
        if any(word in text for word in ["bike", "cycling", "cycle", "ride", "pedal", "cyclist", "bicycle"]):
            categories.append("cycling")
        
        # Outdoor
        if any(word in text for word in ["hike", "trail", "park", "outdoor", "nature", "kayak", "run", "walk", "camping", "fishing"]):
            categories.append("outdoor")
        
        # Music
        if any(word in text for word in ["concert", "music", "band", "show", "live music", "performance", "symphony", "jazz", "rock", "hip hop", "dj", "singer", "festival"]):
            categories.append("music")
        
        # Food & Dining
        if any(word in text for word in ["food", "dining", "restaurant", "brunch", "dinner", "cooking", "culinary", "wine", "beer", "tasting"]):
            categories.append("food")
        
        # Arts & Culture
        if any(word in text for word in ["art", "museum", "gallery", "exhibition", "theater", "theatre", "play", "comedy", "film", "movie"]):
            categories.append("arts")
        
        # Family & Kids
        if any(word in text for word in ["family", "kids", "children", "playground"]):
            categories.append("family")
        
        # Sports
        if any(word in text for word in ["sports", "game", "match", "basketball", "football", "baseball", "soccer", "hockey"]):
            categories.append("sports")
        
        return categories
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

