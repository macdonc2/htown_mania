"""Domain models for the deep research system."""
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """An entity extracted from an event."""
    name: str
    type: Literal["artist", "venue", "organizer", "topic", "genre"]
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    aliases: List[str] = []
    metadata: Dict[str, Any] = {}


class ResearchQuery(BaseModel):
    """A research query to investigate."""
    query: str
    priority: int = Field(ge=1, le=10)
    entity_name: Optional[str] = None
    query_type: Literal[
        "biographical",      # About a person's life/career
        "contextual",        # General background/context
        "current",           # Recent/current information
        "relational",        # Relationships between entities
        "cultural_impact",   # Cultural significance/impact
        "venue_history",     # Venue background/history
        "genre_overview",    # Genre/style information
        "collaboration",     # Collaborative work
        "historical",        # Historical background/context
        "awards"             # Awards, accolades, achievements
    ] = "contextual"
    executed: bool = False
    agent_results: List[str] = []  # Agent IDs that researched this


class ResearchResult(BaseModel):
    """Result from a research agent."""
    agent_id: str
    query: ResearchQuery
    sources: List[str]  # URLs or source names
    facts: List[str]    # Key facts discovered
    snippets: List[str] = []  # Text snippets
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time: float = 0.0


class EventResearch(BaseModel):
    """Complete research for a single event."""
    event_title: str  # Reference to the event
    entities: List[Entity]
    queries: List[ResearchQuery]
    results: List[ResearchResult]
    synthesized_narrative: str = ""
    key_insights: List[str] = []
    overall_confidence: float = 0.8
    research_timestamp: datetime = Field(default_factory=datetime.now)


class ResearchState(BaseModel):
    """State for the research phase."""
    total_entities_found: int = 0
    total_queries_executed: int = 0
    total_facts_discovered: int = 0
    events_researched: List[EventResearch] = []

