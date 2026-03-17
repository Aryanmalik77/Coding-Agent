"""Architectural Researcher: Discovers and appreciates design patterns."""

from typing import Optional, Any
from loguru import logger

class ArchitecturalResearcher:
    """
    Uses web search and semantic code search (cocoindex) to find,
    benchmark, and appreciate architectural designs.
    """

    def __init__(self, encyclopedia: Any, web_search_tool: Any = None, cocoindex_tool: Any = None):
        self.encyclopedia = encyclopedia
        self.web_search = web_search_tool
        self.cocoindex = cocoindex_tool

    async def benchmark_design(self, topic: str) -> str:
        """Search for industry standards or clever solutions for a given topic."""
        logger.info(f"Benmarking architectural design for: {topic}")
        
        results = []
        if self.web_search:
            web_results = await self.web_search.execute(query=f"advanced architectural patterns for {topic}")
            results.append(f"### Web Research Results\n{web_results}")
            
        if self.cocoindex:
             code_results = await self.cocoindex.execute(query=topic)
             results.append(f"### Internal Semantic Search\n{code_results}")
             
        return "\n\n".join(results) if results else "No research tools available."

    def appreciate_feature(self, name: str, snippet: str, rationale: str) -> str:
        """Explicitly record and classify a clever architectural feature."""
        logger.info(f"Appreciating innovative feature: {name}")
        pattern_id = self.encyclopedia.record_design_pattern(
            name=name,
            category="innovative_feature",
            rationale=rationale,
            snippet=snippet,
            cleverness=9
        )
        return pattern_id
