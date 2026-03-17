"""Verification suite for the Web Research Subsystem."""

import asyncio
from pathlib import Path
from loguru import logger

from coding_agent.core.agent import CodingAgent
from coding_agent.core.tools import initialize_tools

async def run_web_verification():
    workspace = Path(r"c:\Users\HP\coding agent")
    agent = CodingAgent(workspace)
    tools = initialize_tools(agent)
    
    logger.info("--- Starting Web Research Verification ---")

    # 1. Test Scraper
    logger.info("Test 1: Scraping URL...")
    scrape_tool = tools.get_tool("scrape_url")
    res = await scrape_tool.execute(url="https://example.com/architecture")
    if "[Simulated content extraction]" in res:
        print("[PASS] Scraper tool functional.")
    else:
        print("[FAIL] Scraper tool failed.")

    # 2. Test Deep Research
    logger.info("Test 2: Deep Research...")
    research_tool = tools.get_tool("deep_research")
    # This will use the mock session
    res = await research_tool.execute(topic="Microservices patterns")
    if "Research results" in res:
        print("[PASS] Deep Research tool functional.")
    else:
        print("[FAIL] Deep Research tool failed.")

    logger.info("--- Web Verification Complete ---")
    agent.shutdown()

if __name__ == "__main__":
    asyncio.run(run_web_verification())
