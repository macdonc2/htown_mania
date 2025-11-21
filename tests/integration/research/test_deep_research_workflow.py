"""
Integration tests for deep research workflow.

Tests the full deep research pipeline with mocked external API calls.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.domain.models import Event
from app.core.domain.research_models import (
    Entity,
    ResearchQuery,
    ResearchResult,
    EventResearch
)
from app.adapters.agents.research.entity_extraction_agent import EntityExtractionAgent
from app.adapters.agents.research.query_generation_agent import QueryGenerationAgent
from app.adapters.agents.research.web_search_research_agent import WebSearchResearchAgent
from app.adapters.agents.research.knowledge_synthesis_agent import KnowledgeSynthesisAgent


@pytest.fixture
def sample_music_event():
    """Sample music event for testing."""
    return Event(
        title="Hot Mulligan - THE SOUND A BODY MAKES WHEN IT'S STILL TOUR",
        description="Emo/pop-punk band from Michigan performing their latest album",
        start_time=datetime(2025, 11, 16, 18, 0),
        location="House of Blues Houston",
        categories=["music"],
        url="https://www.ticketmaster.com/hot-mulligan",
        confidence=0.95
    )


@pytest.fixture
def sample_comedy_event():
    """Sample comedy event for testing."""
    return Event(
        title="Sarah Millican: Late Bloomer",
        description="British comedian performing stand-up",
        start_time=datetime(2025, 11, 16, 19, 30),
        location="Bayou Music Center",
        categories=["arts"],
        url="https://www.ticketmaster.com/sarah-millican",
        confidence=0.90
    )


@pytest.fixture
def mock_openai_api_key():
    """Mock OpenAI API key for testing."""
    return "sk-test-mock-key-123"


@pytest.mark.integration
class TestEntityExtractionIntegration:
    """Test entity extraction with mocked LLM."""
    
    @pytest.mark.asyncio
    @patch('app.adapters.agents.research.entity_extraction_agent.Agent')
    async def test_extract_entities_from_music_event(
        self,
        mock_agent_class,
        sample_music_event,
        mock_openai_api_key
    ):
        """Entity extractor should identify key entities in a music event."""
        # Mock the agent response
        mock_agent_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = {
            "entities": [
                {
                    "name": "Hot Mulligan",
                    "type": "artist",
                    "confidence": 0.95
                },
                {
                    "name": "House of Blues Houston",
                    "type": "venue",
                    "confidence": 0.90
                },
                {
                    "name": "Emo",
                    "type": "topic",
                    "confidence": 0.85
                }
            ]
        }
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance
        
        # Run extraction
        extractor = EntityExtractionAgent(mock_openai_api_key)
        entities = await extractor.extract_entities(sample_music_event)
        
        # Verify results
        assert len(entities) >= 2
        assert any(e.name == "Hot Mulligan" for e in entities)
        assert any(e.type == "venue" for e in entities)
        assert all(0.0 <= e.confidence <= 1.0 for e in entities)


@pytest.mark.integration
class TestQueryGenerationIntegration:
    """Test query generation with mocked LLM."""
    
    @pytest.mark.asyncio
    @patch('app.adapters.agents.research.query_generation_agent.Agent')
    async def test_generate_queries_for_music_event(
        self,
        mock_agent_class,
        sample_music_event,
        mock_openai_api_key
    ):
        """Query generator should create music-focused queries for music events."""
        # Mock entities
        entities = [
            Entity(name="Hot Mulligan", type="artist", confidence=0.95),
            Entity(name="House of Blues Houston", type="venue", confidence=0.90)
        ]
        
        # Mock the agent response
        mock_agent_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = '''{
            "queries": [
                {
                    "query": "What are Hot Mulligan's biggest hit songs and albums?",
                    "priority": 10,
                    "entity_name": "Hot Mulligan",
                    "query_type": "biographical"
                },
                {
                    "query": "What is the history of House of Blues Houston?",
                    "priority": 8,
                    "entity_name": "House of Blues Houston",
                    "query_type": "venue_history"
                }
            ]
        }'''
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance
        
        # Run query generation
        generator = QueryGenerationAgent(mock_openai_api_key)
        queries = await generator.generate_queries(sample_music_event, entities)
        
        # Verify results
        assert len(queries) >= 1
        assert len(queries) <= 3  # Should respect rate limit (2-3 queries)
        
        # Check that at least one query is music-related
        music_related = any(
            any(keyword in q.query.lower() for keyword in ['hit', 'album', 'song', 'tour'])
            for q in queries
        )
        assert music_related, "Should have at least one music-related query"
        
        # Verify query structure
        for query in queries:
            assert 1 <= query.priority <= 10
            assert query.query_type in [
                "biographical", "contextual", "current", "relational",
                "cultural_impact", "venue_history", "genre_overview",
                "collaboration", "historical", "awards"
            ]


@pytest.mark.integration
class TestWebSearchResearchIntegration:
    """Test web search research with mocked SerpAPI."""
    
    @pytest.mark.asyncio
    async def test_research_with_mocked_serpapi(self, mock_openai_api_key):
        """Web search agent should handle mocked SerpAPI responses."""
        query = ResearchQuery(
            query="What are Hot Mulligan's biggest hits?",
            priority=10,
            entity_name="Hot Mulligan",
            query_type="biographical"
        )
        
        # Mock SerpAPI response
        mock_serpapi_response = {
            "organic_results": [
                {
                    "title": "Hot Mulligan - Top Songs",
                    "snippet": "Hot Mulligan's biggest hits include 'Equip Sunglasses' and 'BCKYRD'",
                    "link": "https://example.com/hot-mulligan"
                },
                {
                    "title": "Hot Mulligan Albums",
                    "snippet": "you'll be fine is their most successful album",
                    "link": "https://example.com/albums"
                }
            ]
        }
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_serpapi_response
            mock_get.return_value = mock_response
            
            # Run research
            agent = WebSearchResearchAgent(serpapi_key="mock-key")
            result = await agent.research(query)
            
            # Verify results
            assert isinstance(result, ResearchResult)
            assert result.query == query.query
            assert result.agent_id == "web_search"
            assert len(result.facts) > 0
            assert result.confidence > 0.0


@pytest.mark.integration
class TestKnowledgeSynthesisIntegration:
    """Test knowledge synthesis with mocked LLM."""
    
    @pytest.mark.asyncio
    @patch('app.adapters.agents.research.knowledge_synthesis_agent.Agent')
    async def test_synthesize_research_into_narrative(
        self,
        mock_agent_class,
        sample_music_event,
        mock_openai_api_key
    ):
        """Synthesizer should combine research into coherent narrative."""
        # Mock entities
        entities = [
            Entity(name="Hot Mulligan", type="artist", confidence=0.95),
            Entity(name="House of Blues", type="venue", confidence=0.90)
        ]
        
        # Mock research results
        results = [
            ResearchResult(
                query="What are Hot Mulligan's hits?",
                agent_id="web_search",
                facts=[
                    "Hot Mulligan's biggest hit is 'Equip Sunglasses'",
                    "Their album 'you'll be fine' was critically acclaimed",
                    "They've toured with bands like Mom Jeans and Prince Daddy"
                ],
                confidence=0.90,
                sources=["https://example.com/1"]
            ),
            ResearchResult(
                query="What is House of Blues history?",
                agent_id="web_search",
                facts=[
                    "House of Blues opened in 1992",
                    "Known for hosting major rock and alternative acts",
                    "Capacity of 1,000+ in Houston location"
                ],
                confidence=0.85,
                sources=["https://example.com/2"]
            )
        ]
        
        # Mock the agent response
        mock_agent_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = {
            "narrative": (
                "Hot Mulligan, the acclaimed emo/pop-punk band known for hits like "
                "'Equip Sunglasses' and their critically acclaimed album 'you'll be fine', "
                "brings their energetic live show to Houston's iconic House of Blues, "
                "a venue that has hosted major rock acts since 1992."
            ),
            "key_insights": [
                "'Equip Sunglasses' is their biggest hit song",
                "They've toured with Mom Jeans and Prince Daddy",
                "House of Blues opened in 1992",
                "The venue is known for major rock acts",
                "'you'll be fine' was critically acclaimed"
            ]
        }
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance
        
        # Run synthesis
        synthesizer = KnowledgeSynthesisAgent(mock_openai_api_key)
        research = await synthesizer.synthesize(sample_music_event, entities, results)
        
        # Verify results
        assert isinstance(research, EventResearch)
        assert research.event_title == sample_music_event.title
        assert len(research.entities) == 2
        assert len(research.results) == 2
        assert len(research.synthesized_narrative) > 100
        assert len(research.key_insights) >= 3
        assert 0.0 <= research.confidence <= 1.0
        
        # Verify narrative mentions key facts
        narrative_lower = research.synthesized_narrative.lower()
        assert "hot mulligan" in narrative_lower
        assert "house of blues" in narrative_lower


@pytest.mark.integration
class TestFullDeepResearchWorkflow:
    """Test the complete deep research workflow."""
    
    @pytest.mark.asyncio
    @patch('app.adapters.agents.research.entity_extraction_agent.Agent')
    @patch('app.adapters.agents.research.query_generation_agent.Agent')
    @patch('app.adapters.agents.research.knowledge_synthesis_agent.Agent')
    async def test_end_to_end_research_workflow(
        self,
        mock_synthesis_agent,
        mock_query_agent,
        mock_entity_agent,
        sample_music_event,
        mock_openai_api_key
    ):
        """Test full workflow from entity extraction to synthesis."""
        
        # ============================================================
        # Step 1: Mock Entity Extraction
        # ============================================================
        mock_entity_instance = MagicMock()
        mock_entity_result = MagicMock()
        mock_entity_result.data = {
            "entities": [
                {"name": "Hot Mulligan", "type": "artist", "confidence": 0.95},
                {"name": "House of Blues", "type": "venue", "confidence": 0.90}
            ]
        }
        mock_entity_instance.run = AsyncMock(return_value=mock_entity_result)
        mock_entity_agent.return_value = mock_entity_instance
        
        # ============================================================
        # Step 2: Mock Query Generation
        # ============================================================
        mock_query_instance = MagicMock()
        mock_query_result = MagicMock()
        mock_query_result.data = '''{
            "queries": [
                {
                    "query": "What are Hot Mulligan's biggest hits and albums?",
                    "priority": 10,
                    "entity_name": "Hot Mulligan",
                    "query_type": "biographical"
                },
                {
                    "query": "What is the capacity and history of House of Blues Houston?",
                    "priority": 8,
                    "entity_name": "House of Blues",
                    "query_type": "venue_history"
                }
            ]
        }'''
        mock_query_instance.run = AsyncMock(return_value=mock_query_result)
        mock_query_agent.return_value = mock_query_instance
        
        # ============================================================
        # Step 3: Mock Research (SerpAPI)
        # ============================================================
        mock_serpapi_response = {
            "organic_results": [
                {
                    "title": "Hot Mulligan Greatest Hits",
                    "snippet": "Top songs: Equip Sunglasses, BCKYRD, Featuring Mark Hoppus",
                    "link": "https://example.com/hits"
                }
            ]
        }
        
        # ============================================================
        # Step 4: Mock Knowledge Synthesis
        # ============================================================
        mock_synthesis_instance = MagicMock()
        mock_synthesis_result = MagicMock()
        mock_synthesis_result.data = {
            "narrative": "Hot Mulligan brings their emo energy to House of Blues!",
            "key_insights": [
                "Known for 'Equip Sunglasses'",
                "House of Blues is an iconic venue"
            ]
        }
        mock_synthesis_instance.run = AsyncMock(return_value=mock_synthesis_result)
        mock_synthesis_agent.return_value = mock_synthesis_instance
        
        # ============================================================
        # Execute Full Workflow
        # ============================================================
        
        # 1. Extract entities
        entity_extractor = EntityExtractionAgent(mock_openai_api_key)
        entities = await entity_extractor.extract_entities(sample_music_event)
        assert len(entities) == 2
        
        # 2. Generate queries
        query_generator = QueryGenerationAgent(mock_openai_api_key)
        queries = await query_generator.generate_queries(sample_music_event, entities)
        assert len(queries) == 2
        
        # 3. Research queries
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_serpapi_response
            mock_get.return_value = mock_response
            
            research_agent = WebSearchResearchAgent(serpapi_key="mock-key")
            results = []
            for query in queries:
                result = await research_agent.research(query)
                results.append(result)
            
            assert len(results) == 2
        
        # 4. Synthesize knowledge
        synthesizer = KnowledgeSynthesisAgent(mock_openai_api_key)
        final_research = await synthesizer.synthesize(
            sample_music_event,
            entities,
            results
        )
        
        # ============================================================
        # Verify Complete Research
        # ============================================================
        assert isinstance(final_research, EventResearch)
        assert final_research.event_title == sample_music_event.title
        assert len(final_research.entities) == 2
        assert len(final_research.results) == 2
        assert len(final_research.synthesized_narrative) > 0
        assert len(final_research.key_insights) >= 2
        assert final_research.confidence > 0.0
        
        print("\n" + "="*60)
        print("🎤 FULL DEEP RESEARCH WORKFLOW TEST COMPLETE! 🎤")
        print("="*60)
        print(f"Event: {final_research.event_title}")
        print(f"Entities: {len(final_research.entities)}")
        print(f"Queries Researched: {len(final_research.results)}")
        print(f"Facts Gathered: {sum(len(r.facts) for r in final_research.results)}")
        print(f"Key Insights: {len(final_research.key_insights)}")
        print(f"Confidence: {final_research.confidence:.2f}")
        print("="*60)

