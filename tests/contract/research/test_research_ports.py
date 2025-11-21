"""
Contract tests for research ports.

These tests define the expected behavior of research port implementations.
Any adapter implementing these ports should pass these contract tests.
"""
import pytest
from datetime import datetime
from app.core.ports.research_port import (
    EntityExtractionPort,
    QueryGenerationPort,
    ResearchAgentPort,
    KnowledgeSynthesisPort
)
from app.core.domain.models import Event
from app.core.domain.research_models import (
    Entity,
    ResearchQuery,
    ResearchResult,
    EventResearch
)


# ============================================================
# FAKE IMPLEMENTATIONS FOR TESTING
# ============================================================

class FakeEntityExtractor(EntityExtractionPort):
    """In-memory fake entity extractor for testing."""
    
    async def extract_entities(self, event: Event) -> list[Entity]:
        """Extract mock entities based on event title keywords."""
        entities = []
        
        # Simple keyword-based entity extraction
        if "concert" in event.title.lower() or "music" in event.title.lower():
            entities.append(Entity(
                name="Mock Artist",
                type="artist",
                confidence=0.9
            ))
        
        if event.location:
            entities.append(Entity(
                name=event.location,
                type="venue",
                confidence=0.85
            ))
        
        return entities


class FakeQueryGenerator(QueryGenerationPort):
    """In-memory fake query generator for testing."""
    
    async def generate_queries(
        self,
        event: Event,
        entities: list[Entity]
    ) -> list[ResearchQuery]:
        """Generate mock queries based on entities."""
        queries = []
        
        for entity in entities[:2]:  # Limit to 2 queries
            queries.append(ResearchQuery(
                query=f"What is the history of {entity.name}?",
                priority=8,
                entity_name=entity.name,
                query_type="biographical" if entity.type == "artist" else "contextual"
            ))
        
        return queries


class FakeResearchAgent(ResearchAgentPort):
    """In-memory fake research agent for testing."""
    
    def __init__(self, agent_id: str = "fake_agent"):
        self.agent_id = agent_id
    
    async def research(self, query: ResearchQuery) -> ResearchResult:
        """Return mock research results."""
        return ResearchResult(
            query=query,
            agent_id=self.agent_id,
            facts=[
                f"Mock fact 1 about: {query.entity_name or 'topic'}",
                f"Mock fact 2 about: {query.entity_name or 'topic'}"
            ],
            confidence=0.85,
            sources=[f"https://mock-source.com/{self.agent_id}"]
        )
    
    def get_agent_id(self) -> str:
        return self.agent_id


class FakeKnowledgeSynthesizer(KnowledgeSynthesisPort):
    """In-memory fake knowledge synthesizer for testing."""
    
    async def synthesize(
        self,
        event: Event,
        entities: list[Entity],
        research_results: list[ResearchResult]
    ) -> EventResearch:
        """Synthesize mock research."""
        all_facts = [fact for result in research_results for fact in result.facts]
        
        return EventResearch(
            event_title=event.title,
            entities=entities,
            queries=[],  # Simplified
            results=research_results,
            synthesized_narrative=f"This is a synthesized narrative about {event.title}. " + 
                                 " ".join(all_facts[:3]),
            key_insights=all_facts[:5],
            overall_confidence=0.88
        )


# ============================================================
# CONTRACT TESTS
# ============================================================

@pytest.mark.contract
class TestEntityExtractionPortContract:
    """Contract tests for EntityExtractionPort implementations."""
    
    @pytest.fixture
    def entity_extractor(self):
        """Provide a fake entity extractor."""
        return FakeEntityExtractor()
    
    @pytest.fixture
    def sample_event(self):
        """Provide a sample event."""
        return Event(
            title="Hot Mulligan Concert",
            description="Emo/pop-punk band from Michigan",
            start_time=datetime(2025, 11, 16, 19, 0),
            location="House of Blues Houston",
            categories=["music"]
        )
    
    @pytest.mark.asyncio
    async def test_extract_entities_returns_list(self, entity_extractor, sample_event):
        """extract_entities should return a list of Entity objects."""
        entities = await entity_extractor.extract_entities(sample_event)
        
        assert isinstance(entities, list)
        assert all(isinstance(e, Entity) for e in entities)
    
    @pytest.mark.asyncio
    async def test_extract_entities_includes_confidence(self, entity_extractor, sample_event):
        """All extracted entities should have confidence scores."""
        entities = await entity_extractor.extract_entities(sample_event)
        
        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_extract_entities_valid_types(self, entity_extractor, sample_event):
        """All extracted entities should have valid types."""
        valid_types = ["artist", "venue", "organizer", "topic", "genre"]
        entities = await entity_extractor.extract_entities(sample_event)
        
        for entity in entities:
            assert entity.type in valid_types


@pytest.mark.contract
class TestQueryGenerationPortContract:
    """Contract tests for QueryGenerationPort implementations."""
    
    @pytest.fixture
    def query_generator(self):
        """Provide a fake query generator."""
        return FakeQueryGenerator()
    
    @pytest.fixture
    def sample_event(self):
        """Provide a sample event."""
        return Event(
            title="Jazz Concert",
            description="Wynton Marsalis performs",
            start_time=datetime(2025, 11, 16, 19, 0),
            location="Hobby Center"
        )
    
    @pytest.fixture
    def sample_entities(self):
        """Provide sample entities."""
        return [
            Entity(name="Wynton Marsalis", type="artist", confidence=0.95),
            Entity(name="Hobby Center", type="venue", confidence=0.90)
        ]
    
    @pytest.mark.asyncio
    async def test_generate_queries_returns_list(
        self,
        query_generator,
        sample_event,
        sample_entities
    ):
        """generate_queries should return a list of ResearchQuery objects."""
        queries = await query_generator.generate_queries(sample_event, sample_entities)
        
        assert isinstance(queries, list)
        assert all(isinstance(q, ResearchQuery) for q in queries)
    
    @pytest.mark.asyncio
    async def test_generate_queries_valid_priorities(
        self,
        query_generator,
        sample_event,
        sample_entities
    ):
        """All queries should have valid priority (1-10)."""
        queries = await query_generator.generate_queries(sample_event, sample_entities)
        
        for query in queries:
            assert 1 <= query.priority <= 10
    
    @pytest.mark.asyncio
    async def test_generate_queries_valid_types(
        self,
        query_generator,
        sample_event,
        sample_entities
    ):
        """All queries should have valid query types."""
        valid_types = [
            "biographical", "contextual", "current", "relational",
            "cultural_impact", "venue_history", "genre_overview",
            "collaboration", "historical", "awards"
        ]
        queries = await query_generator.generate_queries(sample_event, sample_entities)
        
        for query in queries:
            assert query.query_type in valid_types


@pytest.mark.contract
class TestResearchAgentPortContract:
    """Contract tests for ResearchAgentPort implementations."""
    
    @pytest.fixture
    def research_agent(self):
        """Provide a fake research agent."""
        return FakeResearchAgent()
    
    @pytest.fixture
    def sample_query(self):
        """Provide a sample research query."""
        return ResearchQuery(
            query="What are the biggest hits of Hot Mulligan?",
            priority=10,
            entity_name="Hot Mulligan",
            query_type="biographical"
        )
    
    @pytest.mark.asyncio
    async def test_research_returns_result(self, research_agent, sample_query):
        """research should return a ResearchResult."""
        result = await research_agent.research(sample_query)
        
        assert isinstance(result, ResearchResult)
        assert result.query.query == sample_query.query
    
    @pytest.mark.asyncio
    async def test_research_includes_facts(self, research_agent, sample_query):
        """research result should include facts list."""
        result = await research_agent.research(sample_query)
        
        assert isinstance(result.facts, list)
        assert all(isinstance(fact, str) for fact in result.facts)
    
    @pytest.mark.asyncio
    async def test_research_includes_confidence(self, research_agent, sample_query):
        """research result should include confidence score."""
        result = await research_agent.research(sample_query)
        
        assert 0.0 <= result.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_research_includes_agent_id(self, research_agent, sample_query):
        """research result should include agent_id."""
        result = await research_agent.research(sample_query)
        
        assert result.agent_id == research_agent.get_agent_id()
    
    def test_get_agent_id_returns_string(self, research_agent):
        """get_agent_id should return a string identifier."""
        agent_id = research_agent.get_agent_id()
        
        assert isinstance(agent_id, str)
        assert len(agent_id) > 0


@pytest.mark.contract
class TestKnowledgeSynthesisPortContract:
    """Contract tests for KnowledgeSynthesisPort implementations."""
    
    @pytest.fixture
    def synthesizer(self):
        """Provide a fake knowledge synthesizer."""
        return FakeKnowledgeSynthesizer()
    
    @pytest.fixture
    def sample_event(self):
        """Provide a sample event."""
        return Event(
            title="Wynton Marsalis Jazz Concert",
            description="Jazz at Lincoln Center Orchestra",
            start_time=datetime(2025, 11, 16, 19, 0),
            location="Hobby Center"
        )
    
    @pytest.fixture
    def sample_entities(self):
        """Provide sample entities."""
        return [
            Entity(name="Wynton Marsalis", type="artist", confidence=0.95),
            Entity(name="Hobby Center", type="venue", confidence=0.90)
        ]
    
    @pytest.fixture
    def sample_results(self):
        """Provide sample research results."""
        query1 = ResearchQuery(
            query="What are Wynton Marsalis's achievements?",
            priority=10,
            entity_name="Wynton Marsalis",
            query_type="awards"
        )
        query2 = ResearchQuery(
            query="What is Hobby Center's history?",
            priority=8,
            entity_name="Hobby Center",
            query_type="venue_history"
        )
        return [
            ResearchResult(
                query=query1,
                agent_id="web_search",
                facts=["Won 9 Grammy Awards", "Pulitzer Prize winner"],
                confidence=0.90,
                sources=["https://example.com/wynton"]
            ),
            ResearchResult(
                query=query2,
                agent_id="web_search",
                facts=["Opened in 2002", "Premier Houston venue"],
                confidence=0.85,
                sources=["https://example.com/hobby-center"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_synthesize_returns_event_research(
        self,
        synthesizer,
        sample_event,
        sample_entities,
        sample_results
    ):
        """synthesize should return EventResearch object."""
        research = await synthesizer.synthesize(
            sample_event,
            sample_entities,
            sample_results
        )
        
        assert isinstance(research, EventResearch)
        assert research.event_title == sample_event.title
    
    @pytest.mark.asyncio
    async def test_synthesize_includes_narrative(
        self,
        synthesizer,
        sample_event,
        sample_entities,
        sample_results
    ):
        """synthesize should produce a narrative string."""
        research = await synthesizer.synthesize(
            sample_event,
            sample_entities,
            sample_results
        )
        
        assert isinstance(research.synthesized_narrative, str)
        assert len(research.synthesized_narrative) > 0
    
    @pytest.mark.asyncio
    async def test_synthesize_includes_insights(
        self,
        synthesizer,
        sample_event,
        sample_entities,
        sample_results
    ):
        """synthesize should extract key insights."""
        research = await synthesizer.synthesize(
            sample_event,
            sample_entities,
            sample_results
        )
        
        assert isinstance(research.key_insights, list)
        assert all(isinstance(insight, str) for insight in research.key_insights)
    
    @pytest.mark.asyncio
    async def test_synthesize_includes_confidence(
        self,
        synthesizer,
        sample_event,
        sample_entities,
        sample_results
    ):
        """synthesize should include overall confidence score."""
        research = await synthesizer.synthesize(
            sample_event,
            sample_entities,
            sample_results
        )
        
        assert 0.0 <= research.overall_confidence <= 1.0

