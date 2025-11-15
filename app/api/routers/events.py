from fastapi import APIRouter, Request, BackgroundTasks
from app.core.domain.models import Event
from app.core.di import build_agentic_event_service

router = APIRouter()


@router.get('/latest', response_model=list[Event])
async def latest(request: Request, limit: int = 20):
    """Get the latest events from the repository."""
    svc = request.app.state.event_service
    return await svc.repository.get_latest_events(limit=limit)


@router.post('/trigger-agentic-flow')
async def trigger_agentic_flow(background_tasks: BackgroundTasks):
    """
    Trigger the agentic workflow in the background.
    
    This endpoint initiates the multi-agent system to:
    1. Search for events from multiple sources in parallel
    2. Review and enrich events with validation agents
    3. Generate a wrestling promo
    4. Send via SMS
    
    Returns immediately with a 202 Accepted status.
    """
    async def run_workflow():
        service = build_agentic_event_service()
        await service.run_daily_event_flow()
    
    background_tasks.add_task(run_workflow)
    
    return {
        "status": "accepted",
        "message": "Agentic workflow triggered in background",
        "details": {
            "phases": ["searching", "reviewing", "synthesizing"],
            "agents": {
                "search": ["Eventbrite", "Ticketmaster", "Meetup"],
                "review": ["URLValidator", "ContentEnricher", "RelevanceScorer", "DateVerifier"],
                "orchestrator": "PlanningAgent (REACT pattern)"
            }
        }
    }
