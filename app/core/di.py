from app.core.services.event_service import EventService
from app.core.services.agentic_event_service import AgenticEventService
from app.adapters.scraping.houston_scraper import HoustonEventsScraper
from app.adapters.llm.openai_llm import OpenAILLMAdapter
from app.adapters.sms.twilio_sms import TwilioSMSAdapter
from app.adapters.sms.email_sms import EmailSMSAdapter
from app.adapters.db.repository import PostgresEventRepository
from app.config.settings import Settings

# Agentic system imports
from app.adapters.agents import (
    TicketmasterSearchAgent,
    MeetupSearchAgent,
    SerpAPIEventsAgent,
    WebSearchEnricherAgent,
    ContentEnricherAgent,
    RelevanceScoreAgent,
    DateVerificationAgent,
    PromoGeneratorAgent,
    PlanningAgent,
)


def build_event_service() -> EventService:
    """Build the original (non-agentic) event service."""
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


def build_agentic_event_service() -> AgenticEventService:
    """
    Build the agentic event service with multi-agent system.
    
    This wires up:
    - Search agents (Eventbrite, Ticketmaster, Meetup)
    - Review agents (URL validator, content enricher, relevance scorer, date verifier)
    - Promo generator agent
    - Planning agent (orchestrator)
    """
    s = Settings()
    
    # Build search agents
    search_agents = [
        SerpAPIEventsAgent(s),  # Google Events aggregation - best coverage!
        TicketmasterSearchAgent(s),  # Backup/additional coverage
        MeetupSearchAgent(s),  # Community events
        # Eventbrite removed - they deprecated public event search in 2019
    ]
    
    # Build review agents
    review_agents = [
        RelevanceScoreAgent(),
        DateVerificationAgent(),
    ]
    
    # Add web search enricher if both SerpAPI and OpenAI keys are available
    if s.serpapi_key and s.openai_api_key:
        review_agents.append(WebSearchEnricherAgent(
            serpapi_key=s.serpapi_key,
            openai_api_key=s.openai_api_key
        ))
    
    # Add content enricher if OpenAI key is available
    if s.openai_api_key:
        review_agents.append(ContentEnricherAgent(
            openai_api_key=s.openai_api_key,
            model=s.openai_model
        ))
    
    # Build promo generator agent
    promo_agent = PromoGeneratorAgent(
        api_key=s.openai_api_key,
        model=s.openai_model,
        temperature=s.openai_temperature
    )
    
    # Build planning agent (orchestrator)
    planning_agent = PlanningAgent(
        openai_api_key=s.openai_api_key,
        search_agents=search_agents,
        review_agents=review_agents,
        promo_agent=promo_agent,
        model=s.openai_model
    )
    
    # Build SMS adapter
    if hasattr(s, 'gmail_address') and s.gmail_address:
        print("📧 Using Email for notifications")
        sms = EmailSMSAdapter(gmail_address=s.gmail_address, gmail_app_password=s.gmail_app_password)
    else:
        print("📱 Using Twilio SMS for notifications")
        sms = TwilioSMSAdapter(
            account_sid=s.twilio_account_sid,
            auth_token=s.twilio_auth_token,
            from_number=s.twilio_from_number
        )
    
    # Build repository
    repo = PostgresEventRepository()
    
    # Build and return the agentic service
    return AgenticEventService(
        planning_agent=planning_agent,
        sms=sms,
        repository=repo,
        sms_recipient=s.sms_recipient,
        dev_sms_mute=s.dev_sms_mute
    )
