from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.di import build_event_service
from app.api.routers import events as events_router
from app.api import auth as auth_router
from app.api.routers import web as web_router
from app.middleware.session import SessionMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Houston Event Mania", version="1.0.0")
    app.state.event_service = build_event_service()

    app.add_middleware(SessionMiddleware)
    app.mount("/static", StaticFiles(directory="app/api/static"), name="static")

    # React Neon (stub) served at /neon (no build needed yet)
    app.mount("/neon", StaticFiles(directory="frontend/neon", html=True), name="neon")

    app.include_router(auth_router.router, tags=["Auth"])
    app.include_router(events_router.router, prefix="/events", tags=["Events"])
    app.include_router(web_router.router, tags=["Web"])
    return app

app = create_app()
