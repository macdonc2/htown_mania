"""
Contract tests for agent ports.
Ensures all implementations conform to port behavior.
"""
import pytest
from abc import ABC

from app.core.ports.agent_port import (
    SearchAgentPort,
    ReviewAgentPort,
    PromoAgentPort,
    PlanningAgentPort,
)
from app.adapters.agents import (
    EventbriteSearchAgent,
    TicketmasterSearchAgent,
    MeetupSearchAgent,
    URLValidatorAgent,
    RelevanceScoreAgent,
    DateVerificationAgent,
)


@pytest.mark.contract
class TestSearchAgentPort:
    """Contract tests for SearchAgentPort implementations."""
    
    @pytest.mark.parametrize("agent_class", [
        EventbriteSearchAgent,
        TicketmasterSearchAgent,
        MeetupSearchAgent,
    ])
    def test_search_agent_implements_port(self, agent_class):
        """All search agents implement SearchAgentPort."""
        assert issubclass(agent_class, SearchAgentPort)
    
    @pytest.mark.parametrize("agent_class", [
        EventbriteSearchAgent,
        TicketmasterSearchAgent,
        MeetupSearchAgent,
    ])
    def test_search_agent_has_required_methods(self, agent_class):
        """All search agents have required methods."""
        assert hasattr(agent_class, 'search_events')
        assert hasattr(agent_class, 'get_agent_name')
    
    @pytest.mark.parametrize("agent_class", [
        EventbriteSearchAgent,
        TicketmasterSearchAgent,
        MeetupSearchAgent,
    ])
    def test_search_agent_get_name_returns_string(self, agent_class):
        """get_agent_name returns a string."""
        from app.config.settings import Settings
        agent = agent_class(Settings())
        name = agent.get_agent_name()
        assert isinstance(name, str)
        assert len(name) > 0


@pytest.mark.contract
class TestReviewAgentPort:
    """Contract tests for ReviewAgentPort implementations."""
    
    @pytest.mark.parametrize("agent_class", [
        URLValidatorAgent,
        RelevanceScoreAgent,
        DateVerificationAgent,
    ])
    def test_review_agent_implements_port(self, agent_class):
        """All review agents implement ReviewAgentPort."""
        assert issubclass(agent_class, ReviewAgentPort)
    
    @pytest.mark.parametrize("agent_class", [
        URLValidatorAgent,
        RelevanceScoreAgent,
        DateVerificationAgent,
    ])
    def test_review_agent_has_required_methods(self, agent_class):
        """All review agents have required methods."""
        assert hasattr(agent_class, 'review_event')
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("agent_class", [
        URLValidatorAgent,
        RelevanceScoreAgent,
        DateVerificationAgent,
    ])
    async def test_review_agent_returns_correct_type(self, agent_class):
        """review_event returns ReviewAgentResult."""
        from app.core.domain.models import Event
        from app.core.domain.agent_models import ReviewAgentResult
        
        agent = agent_class()
        event = Event(title="Test", source="Test")
        result = await agent.review_event(event)
        
        assert isinstance(result, ReviewAgentResult)
        assert hasattr(result, 'agent_id')
        assert hasattr(result, 'enriched_event')
        assert hasattr(result, 'success')


@pytest.mark.contract
class TestPortsAreAbstract:
    """Verify ports are properly abstract."""
    
    def test_search_agent_port_is_abstract(self):
        """SearchAgentPort cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SearchAgentPort()
    
    def test_review_agent_port_is_abstract(self):
        """ReviewAgentPort cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ReviewAgentPort()
    
    def test_promo_agent_port_is_abstract(self):
        """PromoAgentPort cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PromoAgentPort()
    
    def test_planning_agent_port_is_abstract(self):
        """PlanningAgentPort cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PlanningAgentPort()

