from app.core.ports.sms_port import SMSPort
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


class TwilioSMSAdapter(SMSPort):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    async def send_sms(self, to_number: str, message: str) -> None:
        try:
            msg = self.client.messages.create(body=message, from_=self.from_number, to=to_number)
            logger.info(f"✅ SMS sent! SID: {msg.sid}, Status: {msg.status}, To: {to_number}")
            print(f"✅ SMS sent! SID: {msg.sid}, Status: {msg.status}, To: {to_number}")
        except Exception as e:
            logger.error(f"❌ SMS failed: {e}")
            print(f"❌ SMS failed: {e}")
            raise
