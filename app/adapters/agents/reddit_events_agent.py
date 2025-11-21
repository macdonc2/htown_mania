"""
Reddit Events Agent - Scrapes /r/houston weekly events threads.

The /r/houston community maintains a weekly "Things to do" thread that's 
a goldmine of local events. This agent scrapes those threads.
"""
import time
import httpx
from typing import List
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

from app.core.domain.models import Event
from app.core.domain.agent_models import SearchAgentResult
from app.core.ports.agent_port import SearchAgentPort


class RedditEventsAgent(SearchAgentPort):
    """
    Search agent that scrapes /r/houston weekly events threads.
    
    Strategy:
    1. Fetch the Reddit thread (no API key needed for public posts!)
    2. Parse the post content and comments
    3. Extract event information using patterns
    4. Return structured events
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
    
    def get_agent_name(self) -> str:
        return "Reddit r/houston"
    
    async def search_events(self) -> SearchAgentResult:
        """Search for events from /r/houston weekly thread."""
        start_time = time.time()
        events = []
        
        # Known thread patterns - we'll search for the most recent weekly thread
        reddit_urls = [
            # Direct link provided by user
            "https://www.reddit.com/r/houston/comments/1owi703/things_to_do_in_houston_during_the_weekend_of/",
            # Can also search for latest
            "https://www.reddit.com/r/houston/search/?q=things+to+do+weekend&restrict_sr=1&sort=new",
        ]
        
        try:
            # Try the direct thread first
            for url in reddit_urls[:1]:  # Just try the first one for now
                events_from_url = await self._scrape_reddit_thread(url)
                events.extend(events_from_url)
                
                if events:
                    break  # Found events, no need to try other URLs
            
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=events,
                success=True,
                confidence=0.8,  # Reddit is community-curated, pretty reliable
                execution_time_seconds=time.time() - start_time
            )
            
        except Exception as e:
            print(f"Reddit events search failed: {e}")
            return SearchAgentResult(
                agent_name=self.get_agent_name(),
                events=[],
                success=False,
                error_message=str(e),
                confidence=0.0,
                execution_time_seconds=time.time() - start_time
            )
    
    async def _scrape_reddit_thread(self, url: str) -> List[Event]:
        """Scrape a Reddit thread for events."""
        events = []
        
        try:
            # Fetch the page
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main post content
            # Reddit has various layouts, look for common patterns
            post_content = soup.find('div', {'data-test-id': 'post-content'})
            if not post_content:
                # Try alternative selectors
                post_content = soup.find('div', class_='md')
            
            if post_content:
                text = post_content.get_text(separator='\n', strip=True)
                events.extend(self._parse_events_from_text(text))
            
            # Also check comments for additional events
            comments = soup.find_all('div', {'data-testid': 'comment'})
            for comment in comments[:20]:  # First 20 comments
                text = comment.get_text(separator='\n', strip=True)
                events.extend(self._parse_events_from_text(text))
            
        except Exception as e:
            print(f"Failed to scrape Reddit thread {url}: {e}")
        
        return events
    
    def _parse_events_from_text(self, text: str) -> List[Event]:
        """Parse events from Reddit post/comment text."""
        events = []
        
        # Split into lines
        lines = text.split('\n')
        
        current_event = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_event:
                    events.append(current_event)
                    current_event = None
                continue
            
            # Look for event patterns
            # Common Reddit formats:
            # - "Event Name - Location - Date"
            # - "**Event Name** at Venue"
            # - "[Event Name](url) - description"
            
            # Simple heuristic: lines with certain keywords
            event_keywords = ['concert', 'show', 'festival', 'market', 'ride', 'party', 
                            'night', 'performance', 'exhibit', 'fair', 'game', 'meet']
            
            line_lower = line.lower()
            
            # Check if this looks like an event
            if any(keyword in line_lower for keyword in event_keywords) or \
               ('at' in line_lower and len(line) > 20) or \
               ('pm' in line_lower or 'am' in line_lower):
                
                # Extract URL if present
                url = None
                if 'http' in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('http'):
                            url = part.strip('()')
                            break
                
                # Create event (title is the line, we'll clean it)
                title = self._clean_title(line)
                
                if len(title) > 10:  # Reasonable title length
                    events.append(Event(
                        title=title[:200],
                        description=line[:500] if line != title else None,
                        url=url,
                        source="Reddit r/houston",
                        categories=self._categorize_line(line_lower),
                        start_time=self._extract_date(line)
                    ))
        
        return events
    
    def _clean_title(self, text: str) -> str:
        """Clean up a title from Reddit formatting."""
        # Remove markdown formatting
        text = text.replace('**', '').replace('*', '')
        text = text.replace('[', '').replace(']', '')
        
        # Remove URLs
        words = text.split()
        words = [w for w in words if not w.startswith('http')]
        text = ' '.join(words)
        
        # Remove common prefixes
        prefixes = ['Event:', 'TONIGHT:', 'THIS WEEK:', 'WEEKEND:']
        for prefix in prefixes:
            if text.upper().startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text.strip()
    
    def _categorize_line(self, text: str) -> List[str]:
        """Categorize based on keywords."""
        categories = []
        
        if any(k in text for k in ['bike', 'cycling', 'ride', 'pedal']):
            categories.append('cycling')
        
        if any(k in text for k in ['concert', 'music', 'band', 'show', 'dj']):
            categories.append('music')
        
        if any(k in text for k in ['food', 'restaurant', 'dining', 'brunch']):
            categories.append('food')
        
        if any(k in text for k in ['art', 'gallery', 'museum', 'exhibit']):
            categories.append('arts')
        
        if any(k in text for k in ['market', 'fair', 'festival']):
            categories.append('outdoor')
        
        return categories
    
    def _extract_date(self, text: str) -> datetime:
        """Try to extract a date from text."""
        # Simple heuristic: look for day names
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        text_lower = text.lower()
        
        now = datetime.now(ZoneInfo("America/Chicago"))
        
        for i, day in enumerate(days):
            if day in text_lower:
                # Calculate days until that day
                current_weekday = now.weekday()
                target_weekday = i
                days_ahead = (target_weekday - current_weekday) % 7
                
                if days_ahead == 0:
                    days_ahead = 0  # Today
                
                target_date = now + timedelta(days=days_ahead)
                return target_date.replace(hour=19, minute=0, second=0, microsecond=0)
        
        # Default: this weekend (Saturday)
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.hour > 12:
            days_until_saturday = 7
        
        return now + timedelta(days=days_until_saturday)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

