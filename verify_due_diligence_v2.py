
import sys
from pathlib import Path

# Add project root to path (Enforce local version)
sys.path.insert(0, str(Path(__file__).parent))

from coding_agent.fortress.engine import FortressEngine
from coding_agent.subagents.diligence_agent import DueDiligenceAgent
from coding_agent.swarm.population_engine import PopulationEngine

import asyncio

async def verify_due_diligence_with_knowledge():
    print("--- Starting Due Diligence + Knowledge Verification (v3) ---")
    
    workspace = Path(r"c:\Users\HP\coding agent\coding_agent workspace")
    engine = FortressEngine(None, workspace)
    
    # 1. Populate the Knowledge Bank with diverse architectural essences
    populator = PopulationEngine(workspace)
    
    # HFT Case Study
    populator.ingest_case_study("cs_scaling_hft", {
        "title": "Real-time Scaling HFT via Edge Computing",
        "implementation_details": "Distributed exchange gateways with <10ms latency. Uses non-blocking I/O.",
        "benchmark_results": "Successfully processed 1M signals/sec at the edge.",
        "source_url": "https://hft-labs.io/scaling"
    })
    
    # Async Logging Case Study
    populator.ingest_case_study("cs_zeromq_logging", {
        "title": "Low-Latency Distributed Logging (ZeroMQ Case Study)",
        "implementation_details": "Uses ZeroMQ async messaging patterns for parallel log aggregation.",
        "benchmark_results": "500k messages/sec per node with <1ms latency.",
        "source_url": "https://zeromq.org/case-studies/logging"
    })
    
    populator.close()
    
    # 2. Create a project activity
    activity_id = "trading_bot_v3_hybrid"
    project_path = workspace / f"activity_{activity_id}"
    project_path.mkdir(parents=True, exist_ok=True)
    
    # 3. Spawn subagents context
    engine.spawn_project_subagents(project_path)
    
    # 4. Use Due Diligence Agent (Pass workspace for knowledge lookup)
    diligence = DueDiligenceAgent(project_path, workspace=workspace)
    
    # INTENT: Wants "real-time" and "trading" (Matches HFT) 
    # and "async messaging" (Matches ZeroMQ)
    intent = "I need a real-time trading system that uses async messaging and scales horizontally."
    
    constraints = {
        "network": {
            "max_latency_ms": 50 # Tight limit
        }
    }
    
    print(f"Auditing Intent: {intent}")
    report = await diligence.audit_intent(intent, constraints, engine)
    
    print("\n--- Diligence Report Summary ---")
    print(f"Status: {report['status']}")
    print(f"Feasibility Score: {report['feasibility_score']}")
    
    if report['precedents']:
        print(f"Found {len(report['precedents'])} Precedents:")
        for p in report['precedents']:
            print(f"- {p}")
    else:
        print("[WARNING] No precedents found.")
        
    # Verify local log creation
    log_path = project_path / ".fortress_context" / "DILIGENCE_AUDIT.md"
    if log_path.exists():
        print(f"\n[SUCCESS] Local Hybrid Audit log created.")
    else:
        print("\n[FAILURE] Diligence log not found.")

if __name__ == "__main__":
    asyncio.run(verify_due_diligence_with_knowledge())
