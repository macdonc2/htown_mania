from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/api/templates")

def _svc(request: Request):
    return request.app.state.event_service

def _matches(e, q: str, tags: list[str]) -> bool:
    t = f"{e.title} {(e.description or '')}".lower()
    ok = True
    if q:
        ok = q.lower() in t
    if ok and tags:
        txt = t
        for tag in tags:
            tag = tag.lower()
            if tag == "cycling":
                ok = ok and any(k in txt for k in ["cycling","bike","biking","bicycle","mtb","ride","critical mass"])
            if tag == "outdoor":
                ok = ok and any(k in txt for k in ["outdoor","park","hike","trail","run","nature","bayou","memorial park"])
    return ok

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, service = Depends(_svc)):
    events = await service.repository.get_latest_events(limit=30)
    return templates.TemplateResponse("index.html", {"request": request, "events": events})

@router.get("/events/partial", response_class=HTMLResponse)
async def events_partial(
    request: Request,
    limit: int = 50,
    q: str | None = Query(None),
    tags: list[str] = Query(default=[]),
    service = Depends(_svc),
):
    all_events = await service.repository.get_latest_events(limit=200)
    filtered = [e for e in all_events if _matches(e, q or "", tags)]
    return templates.TemplateResponse("_events_list.html", {
        "request": request, "events": filtered[:limit], "q": q or "", "tags": tags
    })