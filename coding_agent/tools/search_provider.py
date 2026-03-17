"""Functional search tools for the coding agent."""

import httpx
import asyncio
from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict

class DuckDuckGoSearchTool:
    """A real search tool using DuckDuckGo scraping (no API key required)."""
    
    def __init__(self):
        self.name = "ddg_search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def execute(self, query: str, **kwargs) -> str:
        logger.info(f"Searching DuckDuckGo Lite for: {query}")
        # Use GET with query params for better reliability
        async with httpx.AsyncClient() as client:
            try:
                # Use params for automatic encoding
                response = await client.get("https://lite.duckduckgo.com/lite/", params={"q": query}, headers=self.headers, follow_redirects=True)
                
                if response.status_code != 200:
                    return f"Search failed with status {response.status_code}"
                
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                # DDG Lite results are structured in blocks of 4 rows: Title, Snippet, URL, Spacer
                rows = soup.find_all("tr")
                for i in range(len(rows)):
                    link = rows[i].find("a", class_="result-link")
                    if link:
                        # Find snippet in the following rows
                        snippet_text = ""
                        for j in range(i + 1, min(i + 4, len(rows))):
                            snippet_td = rows[j].find("td", class_="result-snippet")
                            if snippet_td:
                                snippet_text = snippet_td.text.strip()
                                break
                        
                        results.append(f"{link.text.strip()}\n{snippet_text}\nSource: {link['href']}")
                
                if not results:
                    return "No results found. The provider layout might have changed or the query yielded no data."
                
                return "\n\n".join(results[:5])
            except Exception as e:
                logger.error(f"DDG search error: {e}")
                return f"Search error: {str(e)}"
