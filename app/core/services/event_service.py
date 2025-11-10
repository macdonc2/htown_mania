from app.core.domain.models import Event
from app.core.domain.services import prioritize_events
from app.core.ports.scraper_port import ScraperPort
from app.core.ports.llm_port import LLMPort
from app.core.ports.sms_port import SMSPort
from app.core.ports.event_repository_port import EventRepositoryPort
from typing import List

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
        prioritized = prioritize_events(events)
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
