"""Architecture Sentinel: Proactive governance and resource enforcement."""

import os
import psutil
from loguru import logger
from typing import Dict, Any, List, Optional

class ArchitectureSentinel:
    """
    Monitors system resources and agentic state to prevent architectural failures.
    """

    def __init__(self, memory_threshold_mb: int = 500):
        self.memory_threshold = memory_threshold_mb
        self.active_activities: Dict[str, int] = {} # activity_id -> recursion_depth
        self.max_recursion = 5

    def pre_flight_check(self, intent: str, activity_id: str) -> Dict[str, Any]:
        """
        Perform all guards before task execution.
        Returns a report with 'status' (allow/block/warn) and 'reason'.
        """
        report = {"status": "allow", "reason": []}

        # 1. Resource Guard
        res = self.check_resources()
        if res["status"] == "critical":
            report["status"] = "block"
            report["reason"].append(f"Resource Exhaustion: {res['message']}")
        elif res["status"] == "warning":
            report["status"] = "warn"
            report["reason"].append(f"Resource Strain: {res['message']}")

        # 2. Recursion Guard
        rec = self.check_recursion(activity_id)
        if not rec["allowed"]:
            report["status"] = "block"
            report["reason"].append(f"Infinite Loop Prevention: {rec['message']}")

        return report

    def check_resources(self) -> Dict[str, Any]:
        """Audit RAM and Disk availability."""
        mem = psutil.virtual_memory()
        available_mb = mem.available / (1024 * 1024)
        
        if available_mb < self.memory_threshold:
            return {
                "status": "critical",
                "message": f"Low RAM: {available_mb:.2f}MB available (Threshold: {self.memory_threshold}MB)"
            }
        
        if available_mb < self.memory_threshold * 1.5:
            return {
                "status": "warning",
                "message": f"Memory pressure detected: {available_mb:.2f}MB available"
            }

        return {"status": "nominal", "message": "Resources healthy"}

    def check_recursion(self, activity_id: str) -> Dict[str, Any]:
        """Detect and prevent deep agentic nesting."""
        depth = self.active_activities.get(activity_id, 0)
        if depth >= self.max_recursion:
            return {
                "allowed": False,
                "message": f"Max recursion depth ({self.max_recursion}) reached for activity {activity_id}"
            }
        
        self.active_activities[activity_id] = depth + 1
        return {"allowed": True, "message": f"Depth: {depth + 1}"}

    def finalize_activity(self, activity_id: str):
        """Cleanup activity state."""
        if activity_id in self.active_activities:
            del self.active_activities[activity_id]
            logger.debug(f"Sentinel finalized activity: {activity_id}")

    def validate_intent_safety(self, task: str) -> bool:
        """Heuristic check for destructive intents without confirmation."""
        destructive = ["rm -rf", "delete root", "format c:", "drop database"]
        task_lower = task.lower()
        if any(d in task_lower for d in destructive):
            logger.warning(f"Destructive intent detected: {task}")
            return False
        return True
