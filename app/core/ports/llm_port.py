from typing import List, Protocol
from app.core.domain.models import Event

class LLMPort(Protocol):
    async def summarize_events(self, events: List[Event]) -> str: ...
