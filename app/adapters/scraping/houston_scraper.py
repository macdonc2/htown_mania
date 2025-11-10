from typing import List
import httpx
from bs4 import BeautifulSoup
from app.core.domain.models import Event
from app.core.ports.scraper_port import ScraperPort
from app.adapters.scraping.event_api_aggregator import EventAPIAggregator

HINT_SITES = [
    # Outdoor & Parks
    ("https://www.discoverygreen.com/events", "Discovery Green"),
    ("https://buffalobayou.org/event/", "Buffalo Bayou"),
    ("https://www.houstonparks.org/", "Houston Parks Board"),
    ("https://www.houstontx.gov/parks/events.html", "Houston Parks & Recreation"),
    ("https://www.visithoustontexas.com/events/", "Visit Houston"),
    
    # Cycling
    ("https://www.bikehouston.org/events/", "BikeHouston"),
    
    # Music Venues
    ("https://www.whiteoakmusichall.com", "White Oak Music Hall"),
    ("https://www.houseofblues.com/houston/shows", "House of Blues Houston"),
    ("https://www.milleroutdoortheatre.com/schedule/", "Miller Outdoor Theatre"),
    ("https://713musichall.com/shows/", "713 Music Hall"),
    
    # Comedy & Entertainment
    ("https://improvhouston.com/events/", "Houston Improv"),
    
    # Dog-Friendly
    ("https://www.bringfido.com/attraction/city/houston_tx_us/", "BringFido Houston"),
]

def _parse_events_from_html(html: str, source_name: str) -> List[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: List[Event] = []
    for a in soup.select("a"):
        title = (a.get_text() or "").strip()
        href = a.get("href")
        if title and href and len(title) > 6:
            # Auto-categorize based on keywords
            categories = []
            title_lower = title.lower()
            
            # Cycling (HIGHEST priority!)
            if any(word in title_lower for word in ["bike", "cycling", "cycle", "ride", "pedal", "cyclist"]):
                categories.append("cycling")
            
            # Music
            if any(word in title_lower for word in ["concert", "music", "band", "show", "live music", "performance", "symphony", "jazz", "rock", "hip hop", "dj"]):
                categories.append("music")
            
            # Dog-friendly
            if any(word in title_lower for word in ["dog", "dog-friendly", "pet", "pet-friendly", "pup", "canine", "bark", "dogs welcome"]):
                categories.append("dog-friendly")
            
            # Couple activities
            if any(word in title_lower for word in ["wine", "brewery", "beer", "cocktail", "tasting", "comedy", "trivia", "art walk", "gallery", "date night"]):
                categories.append("couple-friendly")
            
            # Outdoor
            if any(word in title_lower for word in ["hike", "trail", "park", "outdoor", "nature", "kayak", "run", "walk", "paddle"]):
                categories.append("outdoor")
            
            events.append(Event(
                title=title[:200], 
                url=href if href.startswith("http") else None, 
                source=source_name, 
                categories=categories
            ))
    return events[:20]

class HoustonEventsScraper(ScraperPort):
    async def scrape_events(self) -> List[Event]:
        out: List[Event] = []
        
        # First, try to get events from APIs (Eventbrite, Ticketmaster, Meetup)
        api_aggregator = EventAPIAggregator()
        try:
            api_events = await api_aggregator.get_all_events()
            out.extend(api_events)
            print(f"✅ Fetched {len(api_events)} events from APIs")
        except Exception as e:
            print(f"⚠️ API aggregation error: {e}")
        finally:
            await api_aggregator.close()
        
        # Then, supplement with web scraping as fallback/additional source
        async with httpx.AsyncClient(timeout=15) as client:
            for url, name in HINT_SITES:
                try:
                    r = await client.get(url, follow_redirects=True)
                    if r.status_code == 200 and r.text:
                        scraped = _parse_events_from_html(r.text, name)
                        out.extend(scraped)
                        print(f"✅ Scraped {len(scraped)} events from {name}")
                except Exception as e:
                    print(f"⚠️ Scraping error for {name}: {e}")
                    continue
        
        # Deduplicate by title (case insensitive)
        seen_titles = set()
        unique_events = []
        for event in out:
            title_lower = event.title.lower()
            if title_lower not in seen_titles and len(title_lower) > 5:
                seen_titles.add(title_lower)
                unique_events.append(event)
        
        print(f"🎉 Total unique events: {len(unique_events)}")
        return unique_events
