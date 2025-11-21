"""Research agents for deep event investigation."""

from app.adapters.agents.research.entity_extraction_agent import EntityExtractionAgent
from app.adapters.agents.research.query_generation_agent import QueryGenerationAgent
from app.adapters.agents.research.wikipedia_research_agent import WikipediaResearchAgent
from app.adapters.agents.research.web_search_research_agent import WebSearchResearchAgent
from app.adapters.agents.research.knowledge_synthesis_agent import KnowledgeSynthesisAgent

__all__ = [
    "EntityExtractionAgent",
    "QueryGenerationAgent",
    "WikipediaResearchAgent",
    "WebSearchResearchAgent",
    "KnowledgeSynthesisAgent",
]

