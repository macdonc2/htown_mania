from typing import Protocol, List, Optional

class SMSPort(Protocol):
    async def send_sms(
        self, 
        to_number: str, 
        message: str,
        events: Optional[List] = None,
        promo_text: Optional[str] = None,
        scratchpad_text: Optional[str] = None
    ) -> None: ...
