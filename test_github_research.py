"""Verification script for High-Volume GitHub Research (GRAE)."""

import asyncio
from pathlib import Path
from coding_agent.fortress.engine import FortressEngine
from coding_agent.swarm.lmdb_store import LMDBStore

async def test_research():
    print("--- Testing High-Volume GitHub Research ---")
    
    workspace = Path("c:/Users/HP/coding agent")
    store = LMDBStore(workspace)
    fortress = FortressEngine(store, workspace)
    
    # Trigger a small sprint for verification
    print("\n[Executing] Research Sprint (10 repos)...")
    await fortress.trigger_research_sprint(query="python autonomous agents", count=10)
    
    # Verify workspace population
    repo_ws = workspace / "repo_workspace"
    if repo_ws.exists():
        dirs = [d for d in repo_ws.iterdir() if d.is_dir()]
        print(f"\n[Verification] Found {len(dirs)} repository entries in repo_workspace/")
        for d in dirs[:5]: # Show first 5
            print(f" - {d.name}")
            if (d / "insights.json").exists():
                print("   [OK] insights.json found")
    else:
        print("\n[FAILURE] repo_workspace/ was not created.")

    print("\n--- GitHub Research Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_research())
