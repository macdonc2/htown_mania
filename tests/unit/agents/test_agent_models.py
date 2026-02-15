"""
Unit tests for agent domain models.
Tests invariants, validation, and behavior.
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.core.domain.agent_models import (
    AgentPhase,
    Observation,
    Question,
    EnrichedEvent,
    PlanningState,
    SearchAgentResult,
    ReviewAgentResult,
    PromoGenerationResult,
)
from app.core.domain.models import Event


@pytest.mark.unit
class TestAgentPhase:
    """Test AgentPhase enum."""
    
    def test_all_phases_defined(self):
        """Ensure all expected phases are defined."""
        phases = [phase.value for phase in AgentPhase]
        expected = ["initializing", "searching", "reviewing", "synthesizing", "complete", "failed"]
        assert set(phases) == set(expected)


@pytest.mark.unit
class TestObservation:
    """Test Observation model."""
    
    def test_create_observation_with_defaults(self):
        """Observation can be created with minimal data."""
        obs = Observation(agent="TestAgent", thought="Testing")
        
        assert obs.agent == "TestAgent"
        assert obs.thought == "Testing"
        assert obs.action is None
        assert obs.result is None
        assert obs.confidence == 1.0
        assert isinstance(obs.timestamp, datetime)
    
    def test_create_observation_with_all_fields(self):
        """Observation can be created with all fields."""
        obs = Observation(
            agent="TestAgent",
            thought="Need to search",
            action="invoke_search",
            result="Found 10 events",
            confidence=0.9
        )
        
        assert obs.action == "invoke_search"
        assert obs.result == "Found 10 events"
        assert obs.confidence == 0.9
    
    def test_confidence_validation(self):
        """Confidence must be between 0 and 1."""
        with pytest.raises(ValidationError):
            Observation(agent="Test", thought="Test", confidence=1.5)
        
        with pytest.raises(ValidationError):
            Observation(agent="Test", thought="Test", confidence=-0.1)


@pytest.mark.unit
class TestQuestion:
    """Test Question model."""
    
    def test_create_question(self):
        """Question can be created with text and priority."""
        q = Question(text="What is the venue?", priority=8)
        
        assert q.text == "What is the venue?"
        assert q.priority == 8
        assert q.answered is False
        assert q.answer is None
    
    def test_answer_question(self):
        """Question can be answered."""
        q = Question(text="Where is it?", priority=5)
        q.answered = True
        q.answer = "Houston"
        
        assert q.answered
        assert q.answer == "Houston"


@pytest.mark.unit
class TestPlanningState:
    """Test PlanningState model."""
    
    def test_initial_state(self):
        """Planning state starts in initializing phase."""
        state = PlanningState()
        
        assert state.phase == AgentPhase.INITIALIZING
        assert len(state.scratchpad) == 0
        assert len(state.events_found) == 0
        assert len(state.questions_to_investigate) == 0
        assert state.promo_generated is None
        assert state.completed_at is None
    
    def test_add_observation(self):
        """Can add observations to scratchpad."""
        state = PlanningState()
        
        state.add_observation(
            agent="PlanningAgent",
            thought="Starting search",
            action="invoke_agents",
            result="Success",
            confidence=1.0
        )
        
        assert len(state.scratchpad) == 1
        assert state.scratchpad[0].agent == "PlanningAgent"
        assert state.scratchpad[0].thought == "Starting search"
    
    def test_get_latest_observations(self):
        """Can retrieve latest N observations."""
        state = PlanningState()
        
        for i in range(10):
            state.add_observation(
                agent="Agent",
                thought=f"Thought {i}",
                confidence=1.0
            )
        
        latest = state.get_latest_observations(n=3)
        assert len(latest) == 3
        assert latest[-1].thought == "Thought 9"
    
    def test_mark_complete(self):
        """Can mark state as complete."""
        state = PlanningState()
        state.mark_complete()
        
        assert state.phase == AgentPhase.COMPLETE
        assert state.completed_at is not None
        assert isinstance(state.completed_at, datetime)
    
    def test_mark_failed(self):
        """Can mark state as failed with error message."""
        state = PlanningState()
        state.mark_failed("API error")
        
        assert state.phase == AgentPhase.FAILED
        assert state.error_message == "API error"
        assert state.completed_at is not None


@pytest.mark.unit
class TestEnrichedEvent:
    """Test EnrichedEvent model."""
    
    def test_create_enriched_event(self):
        """Enriched event wraps a base event."""
        event = Event(title="Test Event", source="Test")
        
        enriched = EnrichedEvent(
            event=event,
            verified=True,
            verification_notes=["URL validated"],
            confidence_score=0.95
        )
        
        assert enriched.event.title == "Test Event"
        assert enriched.verified is True
        assert len(enriched.verification_notes) == 1
        assert enriched.confidence_score == 0.95
    
    def test_enriched_metadata(self):
        """Enriched event can have additional metadata."""
        event = Event(title="Bike Ride", source="Test")
        
        enriched = EnrichedEvent(
            event=event,
            verified=True,
            confidence_score=0.9,
            additional_metadata={"relevance_score": 10}
        )
        
        assert enriched.additional_metadata["relevance_score"] == 10


@pytest.mark.unit
class TestSearchAgentResult:
    """Test SearchAgentResult model."""
    
    def test_successful_search(self):
        """Search result can represent success."""
        events = [Event(title="Event 1", source="Test")]
        
        result = SearchAgentResult(
            agent_name="TestAgent",
            events=events,
            success=True,
            confidence=0.9,
            execution_time_seconds=1.5
        )
        
        assert result.success
        assert len(result.events) == 1
        assert result.error_message is None
    
    def test_failed_search(self):
        """Search result can represent failure."""
        result = SearchAgentResult(
            agent_name="TestAgent",
            events=[],
            success=False,
            error_message="API timeout",
            confidence=0.0,
            execution_time_seconds=10.0
        )
        
        assert not result.success
        assert result.error_message == "API timeout"


@pytest.mark.unit
class TestReviewAgentResult:
    """Test ReviewAgentResult model."""
    
    def test_successful_review(self):
        """Review result includes enriched event."""
        event = Event(title="Test", source="Test")
        enriched = EnrichedEvent(
            event=event,
            verified=True,
            confidence_score=0.95
        )
        
        result = ReviewAgentResult(
            agent_id="url_validator",
            enriched_event=enriched,
            success=True,
            checks_performed=["url_validation"]
        )
        
        assert result.success
        assert len(result.checks_performed) == 1


@pytest.mark.unit
class TestPromoGenerationResult:
    """Test PromoGenerationResult model."""
    
    def test_promo_result(self):
        """Promo result includes text and metadata."""
        result = PromoGenerationResult(
            promo_text="OH YEAH! The cream rises to the top!",
            events_included=["Event 1", "Event 2"],
            confidence=0.95,
            generation_metadata={"model": "gpt-5.2", "temperature": 0.9}
        )
        
        assert "OH YEAH" in result.promo_text
        assert len(result.events_included) == 2
        assert result.generation_metadata["model"] == "gpt-5.2"

