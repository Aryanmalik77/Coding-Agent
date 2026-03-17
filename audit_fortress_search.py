import asyncio
from coding_agent.core.agent import CodingAgent

async def audit_failure():
    agent = CodingAgent("c:/Users/HP/coding agent")
    print("--- Auditing Search Shortcoming in Fortress ---")
    
    # 1. Record the issue
    issue_id = await agent.tools.get_tool("fortress_diagnostic").execute(
        action="record_issue",
        category="shortcoming",
        description="Search tool returns HTTP 202 (Accepted) for common queries, failing to scrape results.",
        software_type="deterministic"
    )
    print(f"Recorded ID: {issue_id}")
    
    # 2. Synthesize resolution
    # extract id from "Fortress: Recorded shortcoming issue_..."
    actual_id = issue_id.split()[-1]
    report = await agent.tools.get_tool("fortress_diagnostic").execute(
        action="synthesize",
        issue_id=actual_id
    )
    print("\n--- Resolution Synthesis report ---")
    print(report)

if __name__ == "__main__":
    asyncio.run(audit_failure())
