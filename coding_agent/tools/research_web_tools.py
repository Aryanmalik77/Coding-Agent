"""Tools for advanced web research and scraping."""

from typing import Any
from coding_agent.research.search_agent import SearchAgent
from coding_agent.research.scraper import Scraper

class DeepResearchTool:
    def __init__(self, search_agent: SearchAgent):
        self._agent = search_agent

    @property
    def name(self) -> str: return "deep_research"

    @property
    def description(self) -> str:
        return "Perform multi-step web research on a technical topic, including scraping and synthesis."

    async def execute(self, topic: str, deep_crawl: bool = False, **kwargs: Any) -> str:
        return await self._agent.perform_research(topic, deep_crawl, **kwargs)


class ScrapeUrlTool:
    def __init__(self, scraper: Scraper):
        self._scraper = scraper

    @property
    def name(self) -> str: return "scrape_url"

    async def execute(self, url: str, **kwargs: Any) -> str:
        res = await self._scraper.scrape_url(url)
        return res.get("markdown", "Failed to extract content.")
