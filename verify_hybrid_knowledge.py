
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from coding_agent.swarm.population_engine import PopulationEngine
from coding_agent.subagents.diligence_agent import DueDiligenceAgent
from coding_agent.fortress.engine import FortressEngine
import asyncio

async def test_hybrid_flow():
    workspace = Path(r"c:\Users\HP\coding agent\coding_agent workspace")
    project_path = workspace / "activity_hybrid_test"
    project_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Ingest Case Study via Population Engine (Triggers Extraction)
    populator = PopulationEngine(workspace)
    
    print("\n--- Phase 1: Ingestion & Extraction ---")
    study_data = {
        "title": "Asynchronous Parallel Processing on Distributed Edge Nodes",
        "implementation_details": "Uses event-driven messaging with non-blocking I/O for high throughput.",
        "benchmark_results": "Achieved 500k ops/sec with <5ms latency.",
        "source_url": "https://arch-patterns.test/edge-async"
    }
    populator.ingest_case_study("cs_edge_async", study_data)
    populator.close()

    # 2. Verify stored essence via direct Graph lookup
    print("\n--- Phase 2: Knowledge Lookup (Hybrid) ---")
    engine = FortressEngine(None, workspace)
    diligence = DueDiligenceAgent(project_path, workspace=workspace)
    
    # Intent that should match multiple extracted essence keywords
    intent = "I need a distributed edge system that uses async messaging to handle high throughput signals."
    print(f"Auditing Intent: {intent}")
    
    report = await diligence.audit_intent(intent, {}, engine)
    
    print("\n--- Diligence Report Precedents ---")
    if report["precedents"]:
        for p in report["precedents"]:
            print(f"[FOUND] {p}")
    else:
        print("[FAILURE] No precedents found via hybrid search.")

    # 3. Verify Local Log
    log_path = project_path / ".fortress_context" / "DILIGENCE_AUDIT.md"
    if log_path.exists():
        print(f"\n[SUCCESS] Hybrid Search Audit log created.")
    else:
        print("\n[FAILURE] Log missing.")

if __name__ == "__main__":
    asyncio.run(test_hybrid_flow())
