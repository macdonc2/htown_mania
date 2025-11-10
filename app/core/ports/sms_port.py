from typing import Protocol

class SMSPort(Protocol):
    async def send_sms(self, to_number: str, message: str) -> None: ...
