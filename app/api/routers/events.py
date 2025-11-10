from fastapi import APIRouter, Request
from app.core.domain.models import Event

router = APIRouter()

@router.get('/latest', response_model=list[Event])
async def latest(request: Request, limit: int = 20):
    svc = request.app.state.event_service
    return await svc.repository.get_latest_events(limit=limit)
