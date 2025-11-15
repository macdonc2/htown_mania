from app.core.domain.models import Event
from app.core.domain.services import prioritize_events
from app.core.ports.scraper_port import ScraperPort
from app.core.ports.llm_port import LLMPort
from app.core.ports.sms_port import SMSPort
from app.core.ports.event_repository_port import EventRepositoryPort
from typing import List
from datetime import datetime, timedelta

def format_event_listing(events: List[Event]) -> str:
    """Format events into a plain text listing with titles and links."""
    if not events:
        return ""
    
    listing_lines = [
        "\n\n" + "=" * 60,
        "COMPLETE EVENT LISTING",
        "=" * 60,
        ""
    ]
    
    for idx, event in enumerate(events, 1):
        # Title
        listing_lines.append(f"{idx}. {event.title.upper()}")
        
        # URL
        if event.url:
            listing_lines.append(f"   {event.url}")
        
        # Location and Time on same line
        details = []
        if event.location:
            details.append(f"Location: {event.location}")
        if event.start_time:
            time_str = event.start_time.strftime("%a, %b %d at %I:%M %p")
            details.append(f"Time: {time_str}")
        if details:
            listing_lines.append(f"   {' | '.join(details)}")
        
        # Categories
        if event.categories:
            cats = ", ".join(event.categories)
            listing_lines.append(f"   Categories: {cats}")
        
        # Separator
        listing_lines.append("")
    
    listing_lines.append("=" * 60)
    
    return "\n".join(listing_lines)


class EventService:
    def __init__(self, scraper: ScraperPort, llm: LLMPort, sms: SMSPort, repository: EventRepositoryPort, sms_recipient: str, dev_sms_mute: int = 0):
        self.scraper = scraper
        self.llm = llm
        self.sms = sms
        self.repository = repository
        self.sms_recipient = sms_recipient
        self.dev_sms_mute = dev_sms_mute

    async def run_daily_event_flow(self) -> str:
        events = await self.scraper.scrape_events()
        if not events:
            return "No events found today."
        
        # Filter events to only include those happening in the next 3 days
        # AND remove events with suspicious/generic titles (likely old/stale data)
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/Chicago"))  # Houston time
        three_days = now + timedelta(days=3)
        
        filtered_events = []
        stale_keywords = ["bike fest", "music fest", "food fest", "festival", "annual"]
        
        for event in events:
            # If event has a start_time, check if it's within next 3 days
            if event.start_time:
                # Make timezone-aware if needed (assume Central if naive)
                event_time = event.start_time
                if event_time.tzinfo is None:
                    event_time = event_time.replace(tzinfo=ZoneInfo("America/Chicago"))
                
                if now <= event_time <= three_days:
                    filtered_events.append(event)
                else:
                    print(f"⏭️  Filtered out (wrong date): {event.title} - {event.start_time}")
            else:
                # If no start_time, be cautious with "fest" events (often stale)
                title_lower = event.title.lower()
                if any(keyword in title_lower for keyword in stale_keywords):
                    print(f"⚠️  Filtered out (suspicious/stale): {event.title}")
                else:
                    # Include events without dates if they're not suspicious
                    filtered_events.append(event)
        
        if not filtered_events:
            return "No events found for the next 3 days."
        
        print(f"✅ After date filtering: {len(filtered_events)} events remain (from {len(events)} total)")
        prioritized = prioritize_events(filtered_events)
        summary = await self.llm.summarize_events(prioritized)
        
        # Add complete event listing at the end
        event_listing = format_event_listing(prioritized)
        full_message = summary + event_listing
        
        await self.repository.save_events(prioritized)
        if not self.dev_sms_mute:
            await self.sms.send_sms(self.sms_recipient, full_message)
        else:
            print("[DEV_SMS_MUTE=1] SMS would be sent to", self.sms_recipient)
            print(full_message)
        return full_message
