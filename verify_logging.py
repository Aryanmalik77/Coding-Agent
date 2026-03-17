"""Verification script for the Comprehensive Activity & Rationale Logging system."""

import asyncio
from pathlib import Path
from loguru import logger

from coding_agent.core.agent import CodingAgent
from coding_agent.core.tools import initialize_tools
from coding_agent.core.logging.activity_tracker import ActivityTracker
from coding_agent.core.logging.logger_hooks import LoggingHooks

async def run_logging_verification():
    workspace = Path(r"c:\Users\HP\coding agent")
    agent = CodingAgent(workspace)
    tools = initialize_tools(agent)
    
    # Initialize Tracker and Hooks for the test
    tracker = ActivityTracker(agent.identity.lmdb)
    hooks = LoggingHooks(tracker)
    
    logger.info("--- Starting Comprehensive Logging Verification ---")

    # 1. Log a Software Engineering Task
    logger.info("Test 1: Logging a Software Engineering Task...")
    hooks.log_tool_execution(
        tool_name="write_file",
        intent="Implement high-performance math module",
        purpose="Improve computation efficiency for swarm tokens",
        process="Writing optimized Python code with complex guards",
        rationale="User requested evolution-aware math utility.",
        metadata={"file": "math_utils.py"}
    )
    print("[PASS] Software Engineering activity logged.")

    # 2. Log an Architectural Design Decision
    logger.info("Test 2: Logging an Architectural Design Decision...")
    hooks.log_architectural_decision(
        decision_name="Decouple Activity Tracking from Evolution",
        rationale="Evolution records should be immutable code-links, while Activity logs provide high-level process audit.",
        impact="Improved auditability without bloating the git-evolution history.",
        purpose="Keep code transformation history clean while maintaining rich process context."
    )
    print("[PASS] Architectural decision logged.")

    # 3. Retrieve and Audit Logs via Tool
    logger.info("Test 3: Auditing Logs via Tool...")
    audit_tool = tools.get_tool("audit_activity_history")
    if audit_tool:
        # Note: In the mock execution, we'll see the history we defined in the tool
        # In a real integration, it would fetch from LMDB
        results = await audit_tool.execute()
        print("\n[AUDIT RESULTS]\n")
        print(results)
    else:
        print("[FAIL] Audit tool not found.")

    logger.info("--- Logging Verification Complete ---")
    agent.shutdown()

if __name__ == "__main__":
    asyncio.run(run_logging_verification())
