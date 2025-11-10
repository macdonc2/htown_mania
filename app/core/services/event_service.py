from app.core.domain.models import Event
from app.core.domain.services import prioritize_events
from app.core.ports.scraper_port import ScraperPort
from app.core.ports.llm_port import LLMPort
from app.core.ports.sms_port import SMSPort
from app.core.ports.event_repository_port import EventRepositoryPort

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
        await self.repository.save_events(prioritized)
        if not self.dev_sms_mute:
            await self.sms.send_sms(self.sms_recipient, summary)
        else:
            print("[DEV_SMS_MUTE=1] SMS would be sent to", self.sms_recipient)
            print(summary)
        return summary
