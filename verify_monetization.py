"""Verification script for Fortress Monetization Engine."""

import asyncio
from pathlib import Path
from coding_agent.fortress.engine import FortressEngine

async def verify_monetization():
    print("--- Verifying Fortress Monetization Engine ---")
    
    workspace = Path("c:/Users/HP/coding agent")
    from coding_agent.swarm.lmdb_store import LMDBStore
    store = LMDBStore(workspace)
    fortress = FortressEngine(store, workspace)
    
    # Retrieve the seeded objectives
    keys = store.list_keys()
    obj_keys = [k for k in keys if k.startswith("fortress:objective:")]
    
    if not obj_keys:
        print("[ERROR] No objectives found in registry. Run seed script first.")
        return

    for k in obj_keys:
        obj_id = k.split(":")[-1]
        print(f"\n[Auditing] {obj_id}")
        report = await fortress.calibrate_monetization(obj_id)
        
        if "error" in report:
            print(f"[FAILURE] {report['error']}")
            continue
            
        print(f"Daily Cost: ${report['daily_run_cost']}")
        print(f"Daily Revenue: ${report['estimated_daily_revenue']}")
        print(f"ROI: {report['projected_roi_percent']}%")
        print(f"Status: {report['sustainability_status']}")
        print(f"Recommendation: {report['recommendation']}")

    print("\n[SUCCESS] Monetization strategy audit complete.")

if __name__ == "__main__":
    asyncio.run(verify_monetization())
