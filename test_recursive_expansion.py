"""Verification script for Fortress Recursive Expansion."""

import asyncio
from pathlib import Path
from coding_agent.fortress.engine import FortressEngine
from coding_agent.swarm.lmdb_store import LMDBStore

async def test_expansion():
    print("--- Testing Fortress Recursive Expansion ---")
    
    workspace = Path("c:/Users/HP/coding agent")
    store = LMDBStore(workspace)
    fortress = FortressEngine(store, workspace)
    
    # Pillars to expand
    pillars = ["SaaS-Forge", "Oracle-Net", "Sentinel-Market", "Knowledge-Manifold"]
    
    for pillar_name in pillars:
        print(f"\n[Expanding] {pillar_name} pillar...")
        
        target_id = None
        for key, data in store.prefix_scan("fortress:objective:"):
            if pillar_name in data.get('title', ''):
                target_id = key.split(":")[-1]
                break
        
        if not target_id:
            print(f"[ERROR] {pillar_name} objective not found.")
            continue
            
        children = await fortress.recursive_expand(target_id)
        print(f"Generated {len(children)} child projects for {pillar_name}: {children}")
    
    # 2. Verify Scaffolding
    entities_dir = workspace / "autonomous_entities"
    if entities_dir.exists():
        projects = list(entities_dir.iterdir())
        print(f"\n[Verification] Found {len(projects)} scaffolded directories in autonomous_entities/")
        for p in projects:
            if p.is_dir():
                print(f" - {p.name}")
                if (p / "identity.md").exists():
                    print(f"   [OK] identity.md found")
                if (p / "main.py").exists():
                    print(f"   [OK] main.py found")
    else:
        print("\n[FAILURE] autonomous_entities/ directory not created.")

    print("\n--- Recursive Expansion Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_expansion())
