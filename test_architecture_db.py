
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from coding_agent.swarm.graph_store import GraphStore

def test_architecture_db():
    print("--- Starting Architecture DB Verification ---")
    
    workspace = Path(r"c:\Users\HP\coding agent\coding_agent workspace")
    graph = GraphStore(workspace)
    
    # 1. Simulate "Human Input / Research" - Part 1: Case Study
    case_study_id = "cs_distributed_logging"
    case_study_props = {
        "title": "Low-Latency Distributed Logging (ZeroMQ Case Study)",
        "implementation_details": "Implemented as a fan-in pattern with non-blocking sockets. Used ZeroMQ's PUSH/PULL for asynchronous log aggregation.",
        "benchmark_results": "500k messages/sec per node with <1ms latency.",
        "source_url": "https://example.com/case-studies/distributed-logging"
    }
    print(f"Creating Case Study: {case_study_props['title']}")
    graph.create_node("CaseStudy", case_study_id, case_study_props)
    
    # 2. Simulate "Mathematical Calculation / Justification" - Part 2: Justification
    justification_id = "just_zeromq_async"
    justification_props = {
        "rationale": "ZeroMQ PUSH/PULL removes the overhead of TCP handshakes for every log entry compared to standard sockets.",
        "mathematical_model": "Throughput = N / (L + S/B) where N is node count, L is latency, S is size, B is bandwidth.",
        "resource_tradeoffs": "Memory usage increases slightly due to background buffering (approx 100MB per sender).",
        "physical_limits": "Limited by kernel network buffer size (max 4MB per socket)."
    }
    print(f"Creating Justification: {justification_id}")
    graph.create_node("ImplementationJustification", justification_id, justification_props)
    
    # 3. Create a Design Pattern to link them
    pattern_id = "pat_async_drain"
    pattern_props = {
        "name": "Asynchronous Drain Pattern",
        "category": "Messaging",
        "rationale": "Prevents blocking main threads during I/O heavy operations.",
        "snippet": "socket = ctx.socket(zmq.PUSH); socket.connect(url);",
        "cleverness": 8
    }
    graph.create_node("DesignPattern", pattern_id, pattern_props)
    
    # 4. Link everything via RELATIONSHIPS
    print("Linking Case Study -> Design Pattern -> Justification")
    graph.create_edge("RESEARCHED_FROM", case_study_id, justification_id)
    graph.create_edge("RESEARCHED_FROM", case_study_id, pattern_id)
    graph.create_edge("JUSTIFIES", justification_id, pattern_id)
    
    # 5. Verification
    print("\n--- DB Verification Results ---")
    if graph.kuzu_conn:
        print("[SUCCESS] Connected to KuzuDB.")
        # Test a complex query
        query = "MATCH (c:CaseStudy)-[:RESEARCHED_FROM]->(j:ImplementationJustification) RETURN j.mathematical_model"
        res = graph.kuzu_conn.execute(query)
        if res.has_next():
            print(f"Verified Relationship Query Result: {res.get_next()}")
    elif graph.sqlite_conn:
        print("[SUCCESS] Using SQLite Fallback.")
        cursor = graph.sqlite_conn.cursor()
        cursor.execute("SELECT props_json FROM graph_nodes WHERE label = 'CaseStudy'")
        row = cursor.fetchone()
        if row:
            print(f"Verified SQLite Record: {row[0][:50]}...")
            
    graph.close()
    print("\n--- Architecture DB Test Complete ---")

if __name__ == "__main__":
    test_architecture_db()
