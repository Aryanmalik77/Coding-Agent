"""Advanced Scraper for the Coding Agent research subsystem."""

import httpx
from bs4 import BeautifulSoup
from typing import Any, Optional, List
import re
from loguru import logger

class Scraper:
    """
    Handles extraction of structured and unstructured data from URLs.
    Supports both HTTP-based and browser-based scraping.
    """

    def __init__(self, use_browser: bool = False):
        self.use_browser = use_browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def scrape_url(self, url: str) -> dict[str, Any]:
        """Scrape a URL and return content and metadata."""
        logger.info(f"Scraping URL: {url}")
        
        result = {
            "url": url,
            "title": "",
            "markdown": "",
            "metadata": {},
            "status": "pending"
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code != 200:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                soup = BeautifulSoup(response.text, "html.parser")
                result["title"] = soup.title.string if soup.title else ""
                
                # Basic HTML to Markdown conversion
                # In a full system, we'd use a more robust library like 'markdownify'
                # For this implementation, we extract text and code blocks.
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                result["markdown"] = "\n".join(lines)
                result["status"] = "success"
                
                # Extract meta tags
                for meta in soup.find_all("meta"):
                    if meta.get("name"):
                        result["metadata"][meta["name"]] = meta.get("content", "")
                    elif meta.get("property"):
                        result["metadata"][meta["property"]] = meta.get("content", "")

        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def extract_patterns(self, content: str) -> List[str]:
        """Extract potential architectural patterns or code snippets from markdown."""
        # Extract code blocks using regex
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", content, re.DOTALL)
        return code_blocks
