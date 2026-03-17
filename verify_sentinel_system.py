"""Verification script for Architecture Sentinel."""

import asyncio
from pathlib import Path
from coding_agent.core.agent import CodingAgent
from coding_agent.fortress.sentinel import ArchitectureSentinel
import psutil

async def verify_sentinel():
    print("--- Verifying Architecture Sentinel ---")
    
    workspace = Path("c:/Users/HP/coding agent/coding agent workspace")
    agent = CodingAgent(workspace)
    
    # 1. Test Resource Guard (Simulate low memory)
    print("\n[Test 1] Resource Guard (Simulated Low Memory)")
    # Set threshold higher than current available memory to trigger block
    mem = psutil.virtual_memory()
    available_mb = mem.available / (1024 * 1024)
    print(f"Current available RAM: {available_mb:.2f}MB")
    
    agent.fortress.sentinel.memory_threshold = int(available_mb + 500)
    print(f"Setting threshold to: {agent.fortress.sentinel.memory_threshold}MB")
    
    result = await agent.run_task("Analyze market trends")
    if "Sentinel Block" in result and "Low RAM" in result:
        print("[SUCCESS] Sentinel blocked task due to low memory simulation.")
    else:
        print("[FAILURE] Sentinel failed to block task despite low memory.")

    # 2. Test Recursion Guard
    print("\n[Test 2] Recursion Guard")
    # Reset memory threshold to allow execution
    agent.fortress.sentinel.memory_threshold = 100 
    
    activity_id = "test_recursion_123"
    print(f"Simulating recursive calls for activity: {activity_id}")
    
    # Fill up recursion depth
    for i in range(5):
        report = agent.fortress.sentinel.pre_flight_check("step", activity_id)
        print(f"Call {i+1}: {report['status']}")
        
    # 6th call should block
    final_report = agent.fortress.sentinel.pre_flight_check("step", activity_id)
    print(f"Call 6: {final_report['status']}")
    
    if final_report["status"] == "block" and "Max recursion" in final_report["reason"][0]:
        print("[SUCCESS] Sentinel blocked infinite recursion.")
    else:
        print("[FAILURE] Sentinel allowed excessive recursion.")

    # 3. Test Intent Safety
    print("\n[Test 3] Intent Safety")
    dangerous_task = "rm -rf / --no-preserve-root"
    is_safe = agent.fortress.sentinel.validate_intent_safety(dangerous_task)
    if not is_safe:
        print(f"[SUCCESS] Sentinel flagged dangerous intent: {dangerous_task}")
    else:
        print("[FAILURE] Sentinel failed to flag dangerous intent.")

if __name__ == "__main__":
    asyncio.run(verify_sentinel())
