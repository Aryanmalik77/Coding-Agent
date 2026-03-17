"""Tools for auditing and querying the history of 'Why' and 'How' decisions."""

from typing import Any, List, Optional

class AuditHistoryTool:
    def __init__(self, tracker: Any):
        self._tracker = tracker

    @property
    def name(self) -> str: return "audit_activity_history"

    @property
    def description(self) -> str:
        return "Retrieve the history of agent activities, including intents, purposes, and rationales."

    async def execute(self, limit: int = 10, component: Optional[str] = None, **kwargs: Any) -> str:
        # In a real tool, this would query the LMDB store via the tracker
        history = [
            {
                "task_name": "Web Research: Oil Pricing",
                "intent": "Gather market insights",
                "purpose": "Inform architectural benchmarking",
                "process": "Autonomous Search -> Synthesis",
                "rationale": "Direct user request to test research subsystem."
            }
        ]
        
        output = "### Activity Audit Log\n\n"
        for entry in history:
            output += f"**Task**: {entry['task_name']}\n"
            output += f"- **Intent**: {entry['intent']}\n"
            output += f"- **Purpose**: {entry['purpose']}\n"
            output += f"- **Process**: {entry['process']}\n"
            output += f"- **Rationale**: {entry['rationale']}\n\n"
        
        return output
