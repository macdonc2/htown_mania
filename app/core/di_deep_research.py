"""Deep Research Service Builder - Temporary until we merge into di.py"""

from app.core.services.agentic_event_service import AgenticEventService
from app.adapters.sms.twilio_sms import TwilioSMSAdapter
from app.adapters.sms.email_sms import EmailSMSAdapter
from app.adapters.db.repository import PostgresEventRepository
from app.config.settings import Settings

# Agentic system imports
from app.adapters.agents import (
    TicketmasterSearchAgent,
    SerpAPIEventsAgent,
    WebSearchEnricherAgent,
    ContentEnricherAgent,
    RelevanceScoreAgent,
    DateVerificationAgent,
    PromoGeneratorAgent,
    PlanningAgent,
)

# Deep research imports
from app.adapters.agents.reddit_events_agent import RedditEventsAgent
from app.adapters.agents.research.entity_extraction_agent import EntityExtractionAgent
from app.adapters.agents.research.query_generation_agent import QueryGenerationAgent
from app.adapters.agents.research.web_search_research_agent import WebSearchResearchAgent
from app.adapters.agents.research.knowledge_synthesis_agent import KnowledgeSynthesisAgent


def build_deep_research_service(include_reddit: bool = False) -> AgenticEventService:
    """
    Build the deep research service with full multi-agent system including research.
    
    This adds to agentic service:
    - Reddit Events Agent (optional, can be noisy)
    - Entity Extraction Agent
    - Query Generation Agent
    - Web Search Research Agent
    - Knowledge Synthesis Agent
    
    Args:
        include_reddit: If True, includes Reddit /r/houston events (default: False)
    """
    s = Settings()
    
    # Build search agents
    search_agents = [
        SerpAPIEventsAgent(s),  # Google Events aggregation
        TicketmasterSearchAgent(s),  # Major events
    ]
    
    # Optionally add Reddit (can be noisy, so opt-in)
    if include_reddit:
        search_agents.append(RedditEventsAgent())  # /r/houston weekly threads
    
    # Build review agents
    review_agents = [
        RelevanceScoreAgent(),
        DateVerificationAgent(),
    ]
    
    # Add enrichers if keys available
    if s.serpapi_key and s.openai_api_key:
        review_agents.append(WebSearchEnricherAgent(
            serpapi_key=s.serpapi_key,
            openai_api_key=s.openai_api_key
        ))
    
    if s.openai_api_key:
        review_agents.append(ContentEnricherAgent(
            openai_api_key=s.openai_api_key,
            model=s.openai_model
        ))
    
    # Build promo generator
    promo_agent = PromoGeneratorAgent(
        api_key=s.openai_api_key,
        model=s.openai_model,
        temperature=s.openai_temperature
    )
    
    # Build research agents - NEW!
    entity_extractor = EntityExtractionAgent(s.openai_api_key)
    query_generator = QueryGenerationAgent(s.openai_api_key)  # AI-powered query generation!
    web_search_agent = WebSearchResearchAgent(s.serpapi_key)
    knowledge_synthesizer = KnowledgeSynthesisAgent(s.openai_api_key)
    
    # Build planning agent with research capabilities
    planning_agent = PlanningAgent(
        openai_api_key=s.openai_api_key,
        search_agents=search_agents,
        review_agents=review_agents,
        promo_agent=promo_agent,
        model=s.openai_model,
        # Deep research components
        entity_extractor=entity_extractor,
        query_generator=query_generator,
        web_search_agent=web_search_agent,
        knowledge_synthesizer=knowledge_synthesizer
    )
    
    # Build SMS adapter
    if hasattr(s, 'gmail_address') and s.gmail_address:
        print("📧 Using Email for notifications")
        sms = EmailSMSAdapter(gmail_address=s.gmail_address, gmail_app_password=s.gmail_app_password)
    else:
        print("📱 Using Twilio SMS for notifications")
        sms = TwilioSMSAdapter(account_sid=s.twilio_account_sid, auth_token=s.twilio_auth_token, from_number=s.twilio_from_number)
    
    repo = PostgresEventRepository()
    
    # Create service with research enabled
    service = AgenticEventService(
        planning_agent=planning_agent,
        sms=sms,
        repository=repo,
        sms_recipient=s.sms_recipient,
        dev_sms_mute=s.dev_sms_mute
    )
    
    # Wrap run method to enable research
    original_run = service.run_daily_event_flow
    
    async def run_with_research():
        return await original_run(enable_research=True)
    
    service.run_daily_event_flow = run_with_research
    
    return service

