import asyncio
from pathlib import Path
from coding_agent.core.agent import CodingAgent
import os

async def test_re_shadowing():
    print("--- Starting RE Shadowing Verification Test ---")
    workspace = Path(r"c:\Users\HP\coding agent")
    agent = CodingAgent(workspace)
    
    tasks = [
        "search for current oil prices",
        "scrape https://example.com and then show audit logs",
        "why did the last task fail?",
        "research latest trending tech topics"
    ]
    
    for i, task in enumerate(tasks):
        print(f"\n[Test {i+1}] Executing: {task}")
        try:
            # We use a short timeout or just run it. 
            # We expect it might fail tool calls due to networking, but NOT raise NameError: re
            result = await agent.run_task(task)
            if "CRITICAL FAILURE" in result and "re" in result:
                print(f"FAILED: NameError: re or similar found in result for task: {task}")
                print(result)
                return False
            print(f"SUCCESS: Task {i+1} completed without NameError: re")
        except NameError as e:
            if 're' in str(e):
                print(f"FAILED: NameError: re caught! {e}")
                return False
            else:
                print(f"Caught NameError (not re): {e}")
        except Exception as e:
            if "free variable 're'" in str(e) or "UnboundLocalError" in str(e):
                print(f"FAILED: Scoping error for 're' caught! {e}")
                return False
            print(f"Caught expected/other exception: {e}")
            
    print("\n--- ALL TESTS PASSED: No 're' NameError detected ---")
    return True

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(test_re_shadowing())
    if not success:
        exit(1)
    exit(0)
