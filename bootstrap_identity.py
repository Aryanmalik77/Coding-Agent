"""Script to bootstrap the identity encyclopedia with nanobot's architecture."""

import asyncio
from pathlib import Path
from coding_agent.core.agent import CodingAgent

async def bootstrap():
    workspace = Path(r"c:\Users\HP\coding agent")
    agent = CodingAgent(workspace)
    
    # 1. Document Core Identity
    agent.identity.add_identity_facet(
        "Core Purpose", 
        "A highly evolved, self-modifying coding agent capable of architectural research and deep evolution tracking."
    )
    
    # 2. Document Core Components
    agent.identity.document_component("Evolution Tracker", "Tracks intents, outcomes, and side-effects of code changes.")
    agent.identity.document_component("Identity Encyclopedia", "Manages architectural knowledge and identity awareness.")
    agent.identity.document_component("Version Manager", "Handles granular fallbacks and historical state management.")
    agent.identity.document_component("MCP Gateway", "Routes coding tasks to cocoindex and other MCP servers.")
    
    # 3. Record Initial Design Patterns
    agent.identity.record_design_pattern(
        "Evolution-Linked Filesystem",
        "Infrastructure",
        "Every write/edit is linked to an evolution record to ensure intentionality and traceability.",
        cleverness=8
    )
    
    agent.identity.record_design_pattern(
        "Decoupled Identity Awareness",
        "Architecture",
        "Architectural knowledge is kept in the Encyclopedia to prevent prompt bloat and allow granular retrieval.",
        cleverness=9
    )
    
    print("Identity Encyclopedia bootstrapped successfully.")
    agent.shutdown()

if __name__ == "__main__":
    asyncio.run(bootstrap())
