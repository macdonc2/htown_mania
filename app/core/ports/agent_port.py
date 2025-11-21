"""
Port definitions for the agentic system.
"""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.models import Event
from app.core.domain.agent_models import (
    PlanningState,
    SearchAgentResult,
    ReviewAgentResult,
    EnrichedEvent,
    PromoGenerationResult,
)


class PlanningAgentPort(ABC):
    """
    Port for the planning agent that orchestrates the workflow using REACT.
    """
    
    @abstractmethod
    async def run_workflow(self, initial_state: PlanningState) -> PlanningState:
        """
        Run the complete agentic workflow from start to finish.
        Returns the final state with the generated promo.
        """
        pass


class SearchAgentPort(ABC):
    """
    Port for search agents that fetch events from various sources.
    """
    
    @abstractmethod
    async def search_events(self) -> SearchAgentResult:
        """
        Search for events from this agent's data source.
        """
        pass
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """
        Return the name of this search agent.
        """
        pass


class ReviewAgentPort(ABC):
    """
    Port for review agents that validate and enrich event data.
    """
    
    @abstractmethod
    async def review_event(self, event: Event) -> ReviewAgentResult:
        """
        Review and enrich a single event.
        """
        pass


class PromoAgentPort(ABC):
    """
    Port for the promo generator agent.
    """
    
    @abstractmethod
    async def generate_promo(
        self, 
        events: List[EnrichedEvent],
        planning_context: PlanningState,
        research_results: List = None
    ) -> PromoGenerationResult:
        """
        Generate the final wrestling promo based on enriched events.
        
        Args:
            events: Enriched and validated events
            planning_context: The planning state with observations and context
            research_results: Optional list of EventResearch with deep research insights
        """
        pass

