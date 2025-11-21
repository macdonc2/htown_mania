"""Web search research agent using SerpAPI."""
import time
import httpx
from typing import List

from app.core.domain.research_models import ResearchQuery, ResearchResult
from app.core.ports.research_port import ResearchAgentPort


class WebSearchResearchAgent(ResearchAgentPort):
    """
    Research agent that uses SerpAPI to search the web.
    Great for general information, recent news, and any topic.
    """
    
    def __init__(self, serpapi_key: str):
        self.serpapi_key = serpapi_key
        self.client = httpx.AsyncClient(timeout=15)
        self.base_url = "https://serpapi.com/search"
    
    def get_agent_id(self) -> str:
        return "web_search"
    
    async def research(self, query: ResearchQuery) -> ResearchResult:
        """Research a query using web search."""
        start_time = time.time()
        
        if not self.serpapi_key:
            return ResearchResult(
                agent_id=self.get_agent_id(),
                query=query,
                sources=[],
                facts=[],
                snippets=[],
                confidence=0.0,
                execution_time=time.time() - start_time
            )
        
        try:
            params = {
                "engine": "google",
                "q": query.query,
                "num": 5,  # Top 5 results
                "api_key": self.serpapi_key
            }
            
            response = await self.client.get(self.base_url, params=params)
            
            if response.status_code != 200:
                error_msg = response.text[:200] if response.text else "No error message"
                print(f"⚠️  SerpAPI Error (Status {response.status_code}): {error_msg}")
                if response.status_code == 429:
                    print("   → Rate limit exceeded. Check your SerpAPI usage at https://serpapi.com/account")
                return ResearchResult(
                    agent_id=self.get_agent_id(),
                    query=query,
                    sources=[],
                    facts=[],
                    snippets=[],
                    confidence=0.0,
                    execution_time=time.time() - start_time
                )
            
            data = response.json()
            
            # Check for SerpAPI errors
            if "error" in data:
                print(f"⚠️  SerpAPI Error: {data['error']}")
                return ResearchResult(
                    agent_id=self.get_agent_id(),
                    query=query,
                    sources=[],
                    facts=[],
                    snippets=[],
                    confidence=0.0,
                    execution_time=time.time() - start_time
                )
            
            # Extract organic search results
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                print(f"⚠️  No search results for query: '{query.query[:50]}...'")
                return ResearchResult(
                    agent_id=self.get_agent_id(),
                    query=query,
                    sources=[],
                    facts=[],
                    snippets=[],
                    confidence=0.0,
                    execution_time=time.time() - start_time
                )
            
            # Extract sources and facts
            sources = []
            facts = []
            snippets = []
            
            for result in organic_results[:5]:
                # Get URL
                link = result.get("link", "")
                if link:
                    sources.append(link)
                
                # Get snippet as a fact
                snippet = result.get("snippet", "")
                if snippet:
                    facts.append(snippet)
                    snippets.append(snippet)
            
            return ResearchResult(
                agent_id=self.get_agent_id(),
                query=query,
                sources=sources,
                facts=facts,
                snippets=snippets,
                confidence=0.85 if facts else 0.5,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            print(f"Web search research failed for '{query.query}': {e}")
            return ResearchResult(
                agent_id=self.get_agent_id(),
                query=query,
                sources=[],
                facts=[],
                snippets=[],
                confidence=0.0,
                execution_time=time.time() - start_time
            )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

