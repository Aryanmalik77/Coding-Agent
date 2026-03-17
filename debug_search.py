import asyncio
from coding_agent.tools.search_provider import DuckDuckGoSearchTool

async def test_search():
    tool = DuckDuckGoSearchTool()
    print("Testing LPG search...")
    result = await tool.execute("lpg gas price today in India")
    print(f"Result:\n{result}")

if __name__ == "__main__":
    asyncio.run(test_search())
