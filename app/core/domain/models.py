from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field

class Event(BaseModel):
    id: Optional[int] = Field(default=None)
    title: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    categories: List[str] = []
    source: Optional[str] = None
