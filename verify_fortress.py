"""Verification script for the Incremental Fortress architecture."""

import asyncio
import os
from pathlib import Path
from coding_agent.core.agent import CodingAgent
from coding_agent.fortress.registry import IssueCategory, SoftwareType
from coding_agent.fortress.objectives import ResponsibilityScope

async def verify_fortress():
    print("--- Initializing CodingAgent with Fortress ---")
    workspace = Path(os.getcwd())
    agent = CodingAgent(workspace)
    
    diagnostic = agent.tools.get_tool("fortress_diagnostic")
    
    print("\n--- Testing Objective Management ---")
    obj_id = agent.fortress.objectives.create_objective(
        title="Implement Non-Deterministic Log Analyzer",
        description="Analyze logs from neural sub-agents with high variance.",
        scope=ResponsibilityScope.GREATER,
        metadata={"category": "observability"}
    )
    print(f"Created Strategic Objective: {obj_id}")
    
    print("\n--- Testing Prioritization ---")
    priorities = await diagnostic.execute(action="prioritize")
    print(priorities)
    
    print("\n--- Testing Human Intervention Trigger ---")
    human_check = await diagnostic.execute(action="check_human", task="Delete core architectural components", failures=3)
    print(f"Human Required for critical task: {human_check}")
    
    print("\n--- Testing Issue Recording & Dependency Matrix ---")
    issue_id = await diagnostic.execute(
        action="record_issue", 
        category="bottleneck", 
        description="High latency in neural inference loop",
        software_type="neural"
    )
    print(issue_id)
    
    agent.fortress.dependencies.register_dependency(
        source_path="coding_agent/core/agent.py",
        target_path="coding_agent/fortress/engine.py",
        target_sw_type=SoftwareType.DETERMINISTIC
    )
    print("Registered deterministic dependency.")

    print("\n--- Testing Resolution Synthesis ---")
    synthesis_report = await diagnostic.execute(
        action="synthesize",
        issue_id=issue_id.split()[-1] # Extract ID from "Fortress: Recorded bottleneck issue_..."
    )
    print(synthesis_report)
    
    print("\n--- Testing Observability Audit ---")
    # Simulate some activity hits
    agent.activity.log_activity(
        task_name="Tool: search",
        intent="Finding data",
        purpose="Fulfill request",
        process="Search failed with Timeout",
        rationale="Retry required"
    )
    
    audit_results = await diagnostic.execute(action="audit")
    print(audit_results)
    
    print("\n--- Fortress Component Verification Complete ---")

if __name__ == "__main__":
    import contextlib
    with open("verify_results.txt", "w") as f:
        with contextlib.redirect_stdout(f):
            asyncio.run(verify_fortress())
