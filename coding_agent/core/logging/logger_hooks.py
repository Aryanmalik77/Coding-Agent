"""Logging hooks for tools and sub-agents to report context."""

from typing import Any, Optional, Dict
from loguru import logger

class LoggingHooks:
    """Provides wrappers for agent components to log their rationale and process."""

    def __init__(self, activity_tracker: Any):
        self.tracker = activity_tracker

    def log_tool_execution(self, tool_name: str, purpose: str, rationale: str, 
                           intent: str, process: str, metadata: Optional[Dict] = None):
        """Standard hook for tools to record why and how they are being used."""
        return self.tracker.log_activity(
            task_name=f"Tool: {tool_name}",
            intent=intent,
            purpose=purpose,
            process=process,
            rationale=rationale,
            metadata=metadata
        )

    def log_architectural_decision(self, decision_name: str, rationale: str, 
                                impact: str, purpose: str):
        """Specialized hook for engineering design decisions."""
        return self.tracker.log_activity(
            task_name=f"Design Decision: {decision_name}",
            intent="Architectural Refinement",
            purpose=purpose,
            process="System Design Analysis",
            rationale=rationale,
            metadata={"impact": impact, "category": "architecture"}
        )
