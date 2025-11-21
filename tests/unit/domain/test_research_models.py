"""
Unit tests for deep research domain models.

Tests the core research data structures without any I/O or external dependencies.
"""
import pytest
from datetime import datetime
from app.core.domain.research_models import (
    Entity,
    ResearchQuery,
    ResearchResult,
    EventResearch
)
from app.core.domain.models import Event


@pytest.mark.unit
class TestEntity:
    """Test Entity value object."""
    
    def test_entity_creation(self):
        """Entity should be created with all required fields."""
        entity = Entity(
            name="Macho Man Randy Savage",
            type="artist",
            confidence=0.95
        )
        
        assert entity.name == "Macho Man Randy Savage"
        assert entity.type == "artist"
        assert entity.confidence == 0.95
    
    def test_entity_types(self):
        """Entity should support all defined types."""
        valid_types = ["artist", "venue", "organizer", "topic", "genre"]
        
        for entity_type in valid_types:
            entity = Entity(
                name="Test Entity",
                type=entity_type,
                confidence=0.8
            )
            assert entity.type == entity_type
    
    def test_entity_confidence_bounds(self):
        """Entity confidence should be between 0 and 1."""
        # Valid confidences
        Entity(name="Test", type="artist", confidence=0.0)
        Entity(name="Test", type="artist", confidence=0.5)
        Entity(name="Test", type="artist", confidence=1.0)
        
        # Invalid confidence should fail validation
        with pytest.raises(Exception):  # Pydantic ValidationError
            Entity(name="Test", type="artist", confidence=1.5)


@pytest.mark.unit
class TestResearchQuery:
    """Test ResearchQuery value object."""
    
    def test_query_creation(self):
        """ResearchQuery should be created with required fields."""
        query = ResearchQuery(
            query="What are the Macho Man's greatest promos?",
            priority=10,
            entity_name="Macho Man Randy Savage",
            query_type="biographical"
        )
        
        assert query.query == "What are the Macho Man's greatest promos?"
        assert query.priority == 10
        assert query.entity_name == "Macho Man Randy Savage"
        assert query.query_type == "biographical"
        assert query.executed is False
        assert query.agent_results == []
    
    def test_all_query_types(self):
        """ResearchQuery should support all defined query types."""
        valid_types = [
            "biographical", "contextual", "current", "relational",
            "cultural_impact", "venue_history", "genre_overview",
            "collaboration", "historical", "awards"
        ]
        
        for query_type in valid_types:
            query = ResearchQuery(
                query=f"Test query for {query_type}",
                priority=5,
                query_type=query_type
            )
            assert query.query_type == query_type
    
    def test_query_priority_bounds(self):
        """Priority should be between 1 and 10."""
        # Valid priorities
        ResearchQuery(query="Test", priority=1)
        ResearchQuery(query="Test", priority=5)
        ResearchQuery(query="Test", priority=10)
        
        # Invalid priorities should fail
        with pytest.raises(Exception):  # Pydantic ValidationError
            ResearchQuery(query="Test", priority=0)
        
        with pytest.raises(Exception):
            ResearchQuery(query="Test", priority=11)
    
    def test_query_execution_tracking(self):
        """Query should track execution and agent results."""
        query = ResearchQuery(
            query="Test query",
            priority=7,
            executed=True,
            agent_results=["web_search", "wikipedia"]
        )
        
        assert query.executed is True
        assert "web_search" in query.agent_results
        assert "wikipedia" in query.agent_results


@pytest.mark.unit
class TestResearchResult:
    """Test ResearchResult aggregate."""
    
    def test_result_creation(self):
        """ResearchResult should store query results."""
        query = ResearchQuery(
            query="What are Macho Man's biggest achievements?",
            priority=10,
            entity_name="Macho Man",
            query_type="biographical"
        )
        
        result = ResearchResult(
            query=query,
            agent_id="web_search",
            facts=[
                "Won WWF Championship twice",
                "Famous for 'Macho Madness' catchphrase",
                "Inducted into WWE Hall of Fame in 2015"
            ],
            confidence=0.90,
            sources=["https://wwe.com/macho-man"]
        )
        
        assert result.query.query == "What are Macho Man's biggest achievements?"
        assert result.agent_id == "web_search"
        assert len(result.facts) == 3
        assert "Won WWF Championship twice" in result.facts
        assert result.confidence == 0.90
        assert len(result.sources) == 1
    
    def test_empty_result(self):
        """ResearchResult can have empty facts list."""
        query = ResearchQuery(
            query="Test query with no results",
            priority=5,
            query_type="contextual"
        )
        
        result = ResearchResult(
            query=query,
            agent_id="web_search",
            facts=[],
            confidence=0.0,
            sources=[]
        )
        
        assert len(result.facts) == 0
        assert result.confidence == 0.0
        assert result.sources == []


@pytest.mark.unit
class TestEventResearch:
    """Test EventResearch aggregate."""
    
    def test_event_research_creation(self):
        """EventResearch should aggregate all research for an event."""
        entities = [
            Entity(name="Macho Man", type="artist", confidence=0.95),
            Entity(name="WrestleMania", type="venue", confidence=0.90)
        ]
        
        query = ResearchQuery(
            query="What are Macho Man's famous promos?",
            priority=10,
            query_type="biographical",
            executed=True
        )
        
        queries = [query]
        
        results = [
            ResearchResult(
                query=query,
                agent_id="web_search",
                facts=["Cream of the Crop promo", "Hulkamania is dead promo"],
                confidence=0.90,
                sources=["https://wwe.com"]
            )
        ]
        
        research = EventResearch(
            event_title="Macho Man Wrestling Special",
            entities=entities,
            queries=queries,
            results=results,
            synthesized_narrative="Macho Man was known for legendary promos...",
            key_insights=[
                "Famous for 'Cream of the Crop' promo",
                "Intense rivalry with Hulk Hogan"
            ],
            overall_confidence=0.92
        )
        
        assert research.event_title == "Macho Man Wrestling Special"
        assert len(research.entities) == 2
        assert len(research.queries) == 1
        assert len(research.results) == 1
        assert len(research.key_insights) == 2
        assert research.overall_confidence == 0.92
        assert "legendary promos" in research.synthesized_narrative
    
    def test_event_research_counts(self):
        """EventResearch should track entity and fact counts."""
        entities = [
            Entity(name="Entity 1", type="artist", confidence=0.9),
            Entity(name="Entity 2", type="venue", confidence=0.8),
            Entity(name="Entity 3", type="organizer", confidence=0.7),
        ]
        
        query1 = ResearchQuery(query="Query 1", priority=8, query_type="contextual")
        query2 = ResearchQuery(query="Query 2", priority=7, query_type="contextual")
        
        results = [
            ResearchResult(
                query=query1,
                agent_id="web",
                facts=["Fact 1", "Fact 2", "Fact 3"],
                confidence=0.9,
                sources=[]
            ),
            ResearchResult(
                query=query2,
                agent_id="wiki",
                facts=["Fact 4", "Fact 5"],
                confidence=0.85,
                sources=[]
            )
        ]
        
        research = EventResearch(
            event_title="Test Event",
            entities=entities,
            queries=[],
            results=results,
            synthesized_narrative="Test",
            key_insights=["Insight 1", "Insight 2", "Insight 3", "Insight 4"],
            overall_confidence=0.88
        )
        
        assert len(research.entities) == 3
        assert len(research.results) == 2
        assert len(research.key_insights) == 4
        # Total facts = 3 + 2 = 5
        total_facts = sum(len(r.facts) for r in research.results)
        assert total_facts == 5
    
    def test_empty_event_research(self):
        """EventResearch can have minimal/empty data."""
        research = EventResearch(
            event_title="Event with No Research",
            entities=[],
            queries=[],
            results=[],
            synthesized_narrative="",
            key_insights=[],
            overall_confidence=0.0
        )
        
        assert len(research.entities) == 0
        assert len(research.results) == 0
        assert len(research.key_insights) == 0
        assert research.overall_confidence == 0.0


@pytest.mark.unit
class TestResearchModelIntegration:
    """Test how research models work together."""
    
    def test_full_research_workflow(self):
        """Test a complete research workflow from entities to synthesis."""
        # Step 1: Extract entities
        entities = [
            Entity(name="Wynton Marsalis", type="artist", confidence=0.95),
            Entity(name="Hobby Center", type="venue", confidence=0.90),
            Entity(name="Jazz", type="genre", confidence=0.85)
        ]
        
        # Step 2: Generate queries
        queries = [
            ResearchQuery(
                query="What are Wynton Marsalis's major jazz achievements?",
                priority=10,
                entity_name="Wynton Marsalis",
                query_type="awards",
                executed=False
            ),
            ResearchQuery(
                query="What is the history of Hobby Center in Houston?",
                priority=8,
                entity_name="Hobby Center",
                query_type="venue_history",
                executed=False
            ),
            ResearchQuery(
                query="What is the cultural impact of jazz in Houston?",
                priority=7,
                query_type="cultural_impact",
                executed=False
            )
        ]
        
        # Step 3: Execute queries and get results
        results = []
        for query in queries:
            result = ResearchResult(
                query=query,
                agent_id="mock_agent",
                facts=[
                    f"Mock fact 1 for {query.entity_name or 'unknown'}",
                    f"Mock fact 2 for {query.entity_name or 'unknown'}"
                ],
                confidence=0.85,
                sources=[f"https://mock-source.com/{query.query_type}"]
            )
            results.append(result)
            query.executed = True
            query.agent_results.append("mock_agent")
        
        # Step 4: Synthesize knowledge
        research = EventResearch(
            event_title="Jazz At Lincoln Center Orchestra with Wynton Marsalis",
            entities=entities,
            queries=queries,
            results=results,
            synthesized_narrative=(
                "Wynton Marsalis, a legendary jazz trumpeter, brings his "
                "acclaimed Lincoln Center Orchestra to Houston's prestigious "
                "Hobby Center, celebrating the cultural impact of jazz."
            ),
            key_insights=[
                "Wynton Marsalis has won 9 Grammy Awards",
                "Hobby Center opened in 2002 as Houston's premier performing arts venue",
                "Jazz has deep roots in Houston's music culture"
            ],
            overall_confidence=0.88
        )
        
        # Verify the complete research
        assert len(research.entities) == 3
        assert len(research.queries) == 3
        assert len(research.results) == 3
        assert len(research.key_insights) == 3
        assert all(q.executed for q in research.queries)
        assert research.overall_confidence > 0.8
        assert "Wynton Marsalis" in research.synthesized_narrative
        assert "Hobby Center" in research.synthesized_narrative

