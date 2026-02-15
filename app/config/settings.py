from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="EVENTS_",
    )

    openai_api_key: str
    openai_model: str = "gpt-5-mini"
    openai_temperature: float = 1.1
    
    # Event API Keys (optional - fallback to scraping if not provided)
    eventbrite_api_key: str = ""  # Deprecated - removed from system
    ticketmaster_api_key: str = ""
    meetup_api_key: str = ""
    serpapi_key: str = ""  # SerpAPI for Google Events aggregation
    
    # Deep Research APIs (optional)
    newsapi_key: str = ""  # NewsAPI for recent news articles

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    sms_recipient: str = ""
    
    # Email alternative (simpler than SMS!)
    gmail_address: str = ""
    gmail_app_password: str = ""

    database_url: str

    google_client_id: str = ""
    google_client_secret: str = ""
    allowed_emails: str = ""
    app_base_url: AnyHttpUrl = "http://localhost:8000"

    session_secret: str
    session_cookie_name: str = "event_mania_session"
    session_lifetime_days: int = 7

    dev_sms_mute: int = 0
    frontend_mode: str = "html"

    @property
    def allowed_emails_list(self) -> List[str]:
        """Parse allowed emails from comma-separated string."""
        if not self.allowed_emails:
            return []
        return [e.strip() for e in self.allowed_emails.split(",") if e.strip()]
