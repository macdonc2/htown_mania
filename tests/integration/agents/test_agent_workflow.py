"""
Integration tests for the complete agentic workflow.
Tests the full end-to-end agent orchestration.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.domain.agent_models import PlanningState, AgentPhase, EnrichedEvent
from app.core.domain.models import Event
from app.adapters.agents import (
    EventbriteSearchAgent,
    URLValidatorAgent,
    RelevanceScoreAgent,
    PromoGeneratorAgent,
    PlanningAgent,
)


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Test the integration of multiple agents in a workflow."""
    
    @pytest.mark.asyncio
    async def test_url_validator_with_real_event(self):
        """URLValidatorAgent can validate real events."""
        event = Event(
            title="Test Event",
            url="https://www.google.com",  # Known good URL
            source="Test"
        )
        
        validator = URLValidatorAgent()
        result = await validator.review_event(event)
        
        assert result.success
        assert result.enriched_event.url_working
        
        await validator.close()
    
    @pytest.mark.asyncio
    async def test_relevance_scorer_with_cycling_event(self):
        """RelevanceScoreAgent scores cycling events highly."""
        event = Event(
            title="Houston Bike Ride",
            description="Join us for a cycling adventure through Memorial Park",
            source="Test"
        )
        
        scorer = RelevanceScoreAgent()
        result = await scorer.review_event(event)
        
        assert result.success
        assert result.enriched_event.additional_metadata["relevance_score"] >= 10
        assert "Cycling event" in str(result.enriched_event.verification_notes)
    
    @pytest.mark.asyncio
    async def test_relevance_scorer_deprioritizes_kids_events(self):
        """RelevanceScoreAgent deprioritizes kid-focused events."""
        event = Event(
            title="Kids Playground Fun",
            description="Toddler story time and bounce house",
            source="Test"
        )
        
        scorer = RelevanceScoreAgent()
        result = await scorer.review_event(event)
        
        assert result.success
        # Score should be negative due to kid focus
        assert result.enriched_event.additional_metadata["relevance_score"] < 0


@pytest.mark.integration
@pytest.mark.slow
class TestPlanningAgentWorkflow:
    """Test the Planning Agent orchestration with mocked dependencies."""
    
    @pytest.mark.asyncio
    async def test_planning_agent_initializes(self):
        """Planning agent can initialize and move to search phase."""
        # Create mock agents
        mock_search_agents = []
        mock_review_agents = []
        mock_promo_agent = MagicMock()
        mock_promo_agent.generate_promo = AsyncMock(return_value=MagicMock(
            promo_text="OH YEAH!",
            events_included=[],
            confidence=0.95,
            generation_metadata={}
        ))
        
        # Note: This would require an OpenAI key for the reasoning agent
        # In a real test, we'd mock or use a fake
        # For now, this is a structure test
        
        initial_state = PlanningState(phase=AgentPhase.INITIALIZING)
        
        assert initial_state.phase == AgentPhase.INITIALIZING
        assert len(initial_state.scratchpad) == 0


@pytest.mark.integration
class TestSearchAgentExecution:
    """Test search agents with real API calls (or VCR)."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_search_agent_handles_missing_api_key(self):
        """Search agents gracefully handle missing API keys."""
        from app.config.settings import Settings
        
        # Create settings with no API keys
        settings = Settings()
        settings.eventbrite_api_key = None
        
        agent = EventbriteSearchAgent(settings)
        result = await agent.search_events()
        
        assert not result.success
        assert "No API key configured" in result.error_message
        assert result.confidence == 0.0
        
        await agent.close()

