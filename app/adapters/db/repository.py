from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.domain.models import Event
from app.core.ports.event_repository_port import EventRepositoryPort
from .models import EventORM
from .session import SessionLocal

def _to_domain(e: EventORM) -> Event:
    cats = (e.categories or "").split(",") if e.categories else []
    return Event(id=e.id, title=e.title, description=e.description, url=e.url, location=e.location, start_time=e.start_time, end_time=e.end_time, categories=cats, source=e.source)

class PostgresEventRepository(EventRepositoryPort):
    def __init__(self, session_factory: SessionLocal.__class__ = SessionLocal):
        self._session_factory = session_factory

    async def save_events(self, events: List[Event]) -> None:
        async with self._session_factory() as session:  # type: AsyncSession
            for ev in events:
                orm = EventORM(title=ev.title, description=ev.description, url=str(ev.url) if ev.url else None, location=ev.location, start_time=ev.start_time, end_time=ev.end_time, categories=",".join(ev.categories) if ev.categories else None, source=ev.source)
                session.add(orm)
            await session.commit()

    async def get_latest_events(self, limit: int = 20) -> List[Event]:
        async with self._session_factory() as session:  # type: AsyncSession
            stmt = select(EventORM).order_by(desc(EventORM.created_at)).limit(limit)
            res = await session.execute(stmt)
            rows = res.scalars().all()
            return [_to_domain(r) for r in rows]
