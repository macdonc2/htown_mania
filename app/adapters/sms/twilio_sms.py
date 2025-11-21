from app.core.ports.sms_port import SMSPort
from twilio.rest import Client
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TwilioSMSAdapter(SMSPort):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    async def send_sms(
        self, 
        to_number: str, 
        message: str,
        events: Optional[List] = None,
        promo_text: Optional[str] = None,
        scratchpad_text: Optional[str] = None
    ) -> None:
        """
        Send SMS via Twilio (ignores HTML formatting - plain text only).
        
        Args:
            to_number: Phone number to send to
            message: Plain text message
            events: Ignored for SMS (HTML only)
            promo_text: Ignored for SMS (HTML only)
            scratchpad_text: Ignored for SMS (HTML only)
        """
        try:
            msg = self.client.messages.create(body=message, from_=self.from_number, to=to_number)
            logger.info(f"✅ SMS sent! SID: {msg.sid}, Status: {msg.status}, To: {to_number}")
            print(f"✅ SMS sent! SID: {msg.sid}, Status: {msg.status}, To: {to_number}")
        except Exception as e:
            logger.error(f"❌ SMS failed: {e}")
            print(f"❌ SMS failed: {e}")
            raise
