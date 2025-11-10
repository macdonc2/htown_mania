from app.core.ports.sms_port import SMSPort
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)


class EmailSMSAdapter(SMSPort):
    """Send 'SMS' via email instead - much simpler for personal use!"""
    
    def __init__(self, gmail_address: str, gmail_app_password: str):
        self.gmail_address = gmail_address
        self.gmail_app_password = gmail_app_password

    async def send_sms(self, to_number: str, message: str) -> None:
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = self.gmail_address  # Send to yourself!
            msg['Subject'] = '🚴 Houston Events Update'
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send via Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {self.gmail_address}")
            print(f"✅ Email sent to {self.gmail_address}")
        except Exception as e:
            logger.error(f"❌ Email failed: {e}")
            print(f"❌ Email failed: {e}")
            raise




