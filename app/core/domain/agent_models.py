"""
Domain models for the agentic system.
These models define the state, observations, and results used by agents.
"""
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, HttpUrl

from app.core.domain.models import Event


class AgentPhase(str, Enum):
    """Phases of the agentic workflow."""
    INITIALIZING = "initializing"
    SEARCHING = "searching"
    REVIEWING = "reviewing"
    SYNTHESIZING = "synthesizing"
    COMPLETE = "complete"
    FAILED = "failed"


class Observation(BaseModel):
    """A single observation in the REACT loop."""
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: str
    thought: str
    action: Optional[str] = None
    result: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class Question(BaseModel):
    """A question to investigate during the planning phase."""
    text: str
    priority: int = Field(ge=1, le=10)
    answered: bool = False
    answer: Optional[str] = None


class EnrichedEvent(BaseModel):
    """An event enriched with additional data from review agents."""
    event: Event
    verified: bool = False
    verification_notes: List[str] = []
    confidence_score: float = Field(ge=0.0, le=1.0)
    enriched_description: Optional[str] = None
    venue_verified: bool = False
    url_working: bool = False
    additional_metadata: Dict[str, Any] = {}


class PlanningState(BaseModel):
    """
    The state of the planning agent.
    Tracks progress through the workflow and maintains the scratchpad.
    """
    phase: AgentPhase = AgentPhase.INITIALIZING
    scratchpad: List[Observation] = []
    
    # Search phase
    events_found: List[Event] = []
    search_sources_completed: List[str] = []
    
    # Review phase
    events_reviewed: List[EnrichedEvent] = []
    urls_to_check: List[HttpUrl] = []
    
    # Planning
    questions_to_investigate: List[Question] = []
    
    # Synthesis
    promo_generated: Optional[str] = None
    
    # Metadata
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def add_observation(self, agent: str, thought: str, action: Optional[str] = None, 
                       result: Optional[str] = None, confidence: float = 1.0):
        """Add an observation to the scratchpad."""
        obs = Observation(
            agent=agent,
            thought=thought,
            action=action,
            result=result,
            confidence=confidence
        )
        self.scratchpad.append(obs)
    
    def get_latest_observations(self, n: int = 5) -> List[Observation]:
        """Get the n most recent observations."""
        return self.scratchpad[-n:]
    
    def get_observations_by_phase(self, phase: AgentPhase) -> List[Observation]:
        """Get all observations for a specific phase."""
        # Filter observations based on timestamp during that phase
        # For now, return all - can be enhanced with phase tracking
        return self.scratchpad
    
    def mark_complete(self):
        """Mark the planning process as complete."""
        self.phase = AgentPhase.COMPLETE
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        """Mark the planning process as failed."""
        self.phase = AgentPhase.FAILED
        self.completed_at = datetime.now()
        self.error_message = error


class SearchAgentResult(BaseModel):
    """Result from a search agent."""
    agent_name: str
    events: List[Event]
    success: bool
    error_message: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    execution_time_seconds: float


class ReviewAgentResult(BaseModel):
    """Result from a review agent."""
    agent_id: str
    enriched_event: EnrichedEvent
    success: bool
    error_message: Optional[str] = None
    checks_performed: List[str] = []


class PromoGenerationResult(BaseModel):
    """Result from the promo generator agent."""
    promo_text: str
    events_included: List[str]  # Event titles
    confidence: float = Field(ge=0.0, le=1.0)
    generation_metadata: Dict[str, Any] = {}

