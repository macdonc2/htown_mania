"""Wikipedia research agent implementation."""
import time
import httpx
from typing import List

from app.core.domain.research_models import ResearchQuery, ResearchResult
from app.core.ports.research_port import ResearchAgentPort


class WikipediaResearchAgent(ResearchAgentPort):
    """
    Research agent that queries Wikipedia API.
    Free, reliable, great for biographical and contextual info.
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15)
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
    
    def get_agent_id(self) -> str:
        return "wikipedia_research"
    
    async def research(self, query: ResearchQuery) -> ResearchResult:
        """Research a query using Wikipedia."""
        start_time = time.time()
        
        # Extract main subject from query
        # Use entity name if available, otherwise first few words
        if query.entity_name:
            search_term = query.entity_name
        else:
            # Extract key terms from query (simple heuristic)
            words = query.query.split()
            # Skip common words
            skip_words = {'about', 'the', 'a', 'an', 'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'biography', 'information'}
            key_words = [w for w in words if w.lower() not in skip_words]
            search_term = " ".join(key_words[:3]) if key_words else " ".join(words[:3])
        
        # Try multiple search strategies
        search_attempts = [
            search_term,
            search_term.replace(" ", "_"),
            search_term.split()[0] if search_term else search_term,  # Try first word only
        ]
        
        for attempt in search_attempts:
            try:
                # Clean search term for URL
                search_term_clean = attempt.replace(" ", "_")
                url = f"{self.base_url}/{search_term_clean}"
                
                response = await self.client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract info
                    title = data.get("title", "")
                    extract = data.get("extract", "")
                    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    
                    # Parse facts from extract
                    facts = self._extract_facts(extract)
                    
                    if facts:  # Success!
                        return ResearchResult(
                            agent_id=self.get_agent_id(),
                            query=query,
                            sources=[page_url] if page_url else [],
                            facts=facts,
                            snippets=[extract[:500]] if extract else [],
                            confidence=0.95,
                            execution_time=time.time() - start_time
                        )
            except Exception as e:
                # Try next search attempt
                continue
        
        # All attempts failed
        print(f"Wikipedia research failed for '{search_term}' after {len(search_attempts)} attempts")
        return ResearchResult(
            agent_id=self.get_agent_id(),
            query=query,
            sources=[],
            facts=[],
            snippets=[],
            confidence=0.0,
            execution_time=time.time() - start_time
        )
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract key facts from Wikipedia extract."""
        if not text:
            return []
        
        # Simple fact extraction: split by periods, take first 3-5 sentences
        sentences = [s.strip() + '.' for s in text.split('.') if len(s.strip()) > 20]
        return sentences[:5]
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

