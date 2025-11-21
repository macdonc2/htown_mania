from app.core.ports.sms_port import SMSPort
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import logging
from typing import List, Optional

# Import premailer for inlining CSS styles for Gmail compatibility
try:
    from premailer import transform
    PREMAILER_AVAILABLE = True
except ImportError:
    PREMAILER_AVAILABLE = False
    logger.warning("⚠️  Premailer not available - Gmail may not display styles correctly")

logger = logging.getLogger(__name__)


class EmailSMSAdapter(SMSPort):
    """Send 'SMS' via email instead - with WRESTLEMANIA-STYLE HTML!"""
    
    def __init__(self, gmail_address: str, gmail_app_password: str):
        self.gmail_address = gmail_address
        self.gmail_app_password = gmail_app_password
        
        # Set up Jinja2 for HTML email templates
        template_dir = Path(__file__).parent.parent / "llm" / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    async def send_sms(
        self, 
        to_number: str, 
        message: str,
        events: Optional[List] = None,
        promo_text: Optional[str] = None,
        scratchpad_text: Optional[str] = None
    ) -> None:
        """
        Send email notification.
        
        Args:
            to_number: Recipient (not used for email, sends to gmail_address)
            message: Plain text message (fallback if HTML fails)
            events: List of Event objects for HTML rendering
            promo_text: Wrestling promo text for HTML rendering
            scratchpad_text: Agent scratchpad for HTML rendering
        """
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_address
            msg['To'] = self.gmail_address  # Send to yourself!
            msg['Subject'] = '🏆 Houston Event Mania - OHHH YEAHHH! 🎤'
            
            # Attach plain text version (fallback)
            plain_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(plain_part)
            
            # Render HTML version if we have the data
            if events is not None or promo_text is not None:
                try:
                    template = self.jinja_env.get_template('email_wrestlemania.html')
                    html_content = template.render(
                        promo_text=promo_text or message,
                        events=events or [],
                        scratchpad_text=scratchpad_text or ""
                    )
                    
                    # Inline CSS styles for Gmail compatibility
                    if PREMAILER_AVAILABLE:
                        try:
                            html_content = transform(html_content)
                            logger.info("✅ CSS styles inlined for Gmail compatibility")
                        except Exception as inline_error:
                            logger.warning(f"⚠️ CSS inlining failed: {inline_error}")
                    
                    html_part = MIMEText(html_content, 'html', 'utf-8')
                    msg.attach(html_part)
                    logger.info("✅ HTML email rendered with WrestleMania template")
                except Exception as template_error:
                    logger.warning(f"⚠️ HTML template failed, using plain text: {template_error}")
            
            # Send via Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {self.gmail_address}")
            print(f"✅ 🏆 WRESTLEMANIA EMAIL sent to {self.gmail_address}")
        except Exception as e:
            logger.error(f"❌ Email failed: {e}")
            print(f"❌ Email failed: {e}")
            raise
