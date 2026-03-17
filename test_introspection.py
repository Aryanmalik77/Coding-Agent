import asyncio
from pathlib import Path
from coding_agent.core.agent import CodingAgent

async def test_introspection():
    workspace = Path("c:/Users/HP/coding agent")
    agent = CodingAgent(workspace)
    
    print("--- Simulating a failing task with Introspection ---")
    # This task will fail because there is no tool for 'invalid_tool_keyword'
    # But it will match the 'research' keywords if we include one, and then we'll force a failure.
    # Actually, let's just trigger a scenario that should trigger introspection.
    
    # We'll use a task that contains 'research' to route it, but we'll mock a crash in the tool.
    # For a simpler test, we'll just check if the introspection report is generated on a generic failure.
    
    task = "research an invalid topic that causes a crash"
    result = await agent.run_task(task)
    
    print("\n--- Agent Result ---")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_introspection())
