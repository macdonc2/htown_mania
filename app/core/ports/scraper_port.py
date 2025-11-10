from typing import List, Protocol
from app.core.domain.models import Event

class ScraperPort(Protocol):
    async def scrape_events(self) -> List[Event]: ...
