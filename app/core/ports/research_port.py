"""Port definitions for research agents."""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.models import Event
from app.core.domain.research_models import (
    Entity,
    ResearchQuery,
    ResearchResult,
    EventResearch
)


class EntityExtractionPort(ABC):
    """Port for extracting entities from events."""
    
    @abstractmethod
    async def extract_entities(self, event: Event) -> List[Entity]:
        """Extract entities from an event."""
        pass


class QueryGenerationPort(ABC):
    """Port for generating research queries."""
    
    @abstractmethod
    async def generate_queries(
        self,
        event: Event,
        entities: List[Entity]
    ) -> List[ResearchQuery]:
        """Generate prioritized research queries."""
        pass


class ResearchAgentPort(ABC):
    """Port for research agents that investigate queries."""
    
    @abstractmethod
    async def research(self, query: ResearchQuery) -> ResearchResult:
        """Research a query and return findings."""
        pass
    
    @abstractmethod
    def get_agent_id(self) -> str:
        """Return the agent identifier."""
        pass


class KnowledgeSynthesisPort(ABC):
    """Port for synthesizing research results."""
    
    @abstractmethod
    async def synthesize(
        self,
        event: Event,
        entities: List[Entity],
        research_results: List[ResearchResult]
    ) -> EventResearch:
        """Synthesize all research into a narrative."""
        pass

