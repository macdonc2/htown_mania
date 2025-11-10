from app.core.services.event_service import EventService
from app.adapters.scraping.houston_scraper import HoustonEventsScraper
from app.adapters.llm.openai_llm import OpenAILLMAdapter
from app.adapters.sms.twilio_sms import TwilioSMSAdapter
from app.adapters.sms.email_sms import EmailSMSAdapter
from app.adapters.db.repository import PostgresEventRepository
from app.config.settings import Settings

def build_event_service() -> EventService:
    s = Settings()
    scraper = HoustonEventsScraper()
    llm = OpenAILLMAdapter(api_key=s.openai_api_key, model=s.openai_model)
    
    # Use email if Gmail credentials are provided, otherwise use Twilio
    if hasattr(s, 'gmail_address') and s.gmail_address:
        print("📧 Using Email for notifications")
        sms = EmailSMSAdapter(gmail_address=s.gmail_address, gmail_app_password=s.gmail_app_password)
    else:
        print("📱 Using Twilio SMS for notifications")
        sms = TwilioSMSAdapter(account_sid=s.twilio_account_sid, auth_token=s.twilio_auth_token, from_number=s.twilio_from_number)
    
    repo = PostgresEventRepository()
    return EventService(scraper=scraper, llm=llm, sms=sms, repository=repo, sms_recipient=s.sms_recipient, dev_sms_mute=s.dev_sms_mute)
