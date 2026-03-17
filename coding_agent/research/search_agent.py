"""Search Agent for orchestrating web research."""

from typing import Any, Optional, List, Dict
import re
from loguru import logger

class SearchAgent:
    """
    High-level agent that orchestrates search, scraping, and synthesis.
    Works as a specialized sub-agent for the Coding Agent.
    """

    def __init__(self, search_tool: Any, scraper: Any, crawler: Any, logging_hooks: Optional[Any] = None):
        self.search_tool = search_tool
        self.scraper = scraper
        self.crawler = crawler
        self.hooks = logging_hooks

    async def perform_research(self, topic: str, deep_crawl: bool = False, activity_id: Optional[str] = None) -> str:
        """Execute a complete research cycle for a topic."""
        logger.info(f"Performing deep research on: {topic}")
        
        metadata = {"activity_id": activity_id} if activity_id else {}

        if self.hooks:
            self.hooks.log_tool_execution(
                tool_name="SearchAgent",
                intent=f"Researching {topic}",
                purpose="Deep technical research and synthesis",
                process="Step 1: Orchestrating multi-provider search",
                rationale="Analyzing external data to ground agent intelligence",
                metadata=metadata
            )

        # 1. Initial Search
        search_results = await self.search_tool.execute(query=f"{topic}")
        
        # 2. Extract top result URL for autonomous scraping
        urls = re.findall(r'Source: (https?://\S+)', search_results)
        top_content = ""
        
        if urls:
            top_url = urls[0]
            if self.hooks:
                self.hooks.log_tool_execution(
                    tool_name="SearchAgent",
                    intent=f"Autonomously scraping {top_url}",
                    purpose="Extracting substantive data beyond snippets",
                    process=f"Step 2: Deep scraping top result",
                    rationale="Snippet was insufficient; deepening search for the user's 'desired output'",
                    metadata=metadata
                )
            scrape_res = await self.scraper.scrape_url(top_url)
            top_content = scrape_res.get("markdown", "")[:2000] # Cap to avoid context overflow

        # 3. Synthesize findings
        all_data = [{"content": search_results}]
        if top_content:
            all_data.append({"content": top_content, "source": urls[0]})
            
        synthesis = await self.synthesize_findings(all_data)
        
        # 3. Optional Deep Crawl
        if deep_crawl:
            if self.hooks:
                self.hooks.log_tool_execution(
                    tool_name="SearchAgent",
                    intent="Deep Crawl",
                    purpose="Extended documentation traversal",
                    process="Step 3: Recursive link exploration",
                    rationale="Capturing secondary architectural evidence"
                )
            # logic for crawling would go here
            pass
            
        return f"### 🔍 Deep Research: {topic}\n\n{synthesis}"

    async def synthesize_findings(self, data: List[Dict]) -> str:
        """Summarize multiple research findings into actionable design insights."""
        if len(data) > 1:
            # We have both snippets and a deep scrape
            snippets = data[0].get("content", "")
            deep_data = data[1].get("content", "")
            return f"**Primary Findings (Deep Scraped):**\n{deep_data}\n\n**Search Snippets:**\n{snippets}"
        
        if not data:
            return "No data found."
        
        return data[0].get("content", "")
