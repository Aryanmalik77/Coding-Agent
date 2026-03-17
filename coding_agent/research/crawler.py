from typing import List, Set, Any, Optional
from loguru import logger
from urllib.parse import urljoin, urlparse
from coding_agent.research.scraper import Scraper

class Crawler:
    """
    Traverses websites to find relevant technical information.
    Filters by relevance to architectural design and system patterns.
    """

    def __init__(self, scraper: Scraper, max_depth: int = 2, max_pages: int = 10):
        self.scraper = scraper
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited: Set[str] = set()

    async def crawl(self, start_url: str, keyword_filters: List[str] | None = None) -> List[dict]:
        """Perform a breadth-first crawl starting from a URL."""
        logger.info(f"Starting crawl at {start_url} (depth={self.max_depth})")
        
        results = []
        queue = [(start_url, 0)]
        self.visited = set()
        
        base_domain = urlparse(start_url).netloc
        
        while queue and len(self.visited) < self.max_pages:
            url, depth = queue.pop(0)
            if url in self.visited or depth > self.max_depth:
                continue
                
            self.visited.add(url)
            logger.debug(f"Crawling: {url} (Depth: {depth})")
            
            scrape_data = await self.scraper.scrape_url(url)
            if scrape_data["status"] == "success":
                # Check relevance
                content = scrape_data["markdown"].lower()
                is_relevant = True
                if keyword_filters:
                    is_relevant = any(kw.lower() in content for kw in keyword_filters)
                
                if is_relevant:
                    results.append({
                        "url": url,
                        "title": scrape_data["title"],
                        "content": scrape_data["markdown"][:1000], # Snippet
                        "relevance_score": 1.0 if is_relevant else 0.5
                    })
                
                # Extract links if we haven't reached max depth
                if depth < self.max_depth:
                    # Very basic link extraction from markdown/text if we don't have soup
                    # But we can better do it $using $the soup inside $scraper if $integrated.
                    # For now, we'll assume the scraper could provide links or we just find them.
                    # Let's refine Scraper to return links.
                    pass
            
        return results
