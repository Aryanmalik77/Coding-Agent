"""Fortress Observability: Monitoring system constraints and bottlenecks."""

from typing import Dict, List, Any, Optional
from loguru import logger
import psutil
import platform

class ObservabilityConstraints:
    """
    Defines and monitors the observability surface of the agent.
    Identifies if the system has enough 'eyes' (logs, metrics) to self-diagnose.
    """

    def __init__(self, lmdb_store: Any):
        self.lmdb = lmdb_store
        logger.info("Fortress Observability Constraints initialized.")

    def audit_system_environment(self) -> Dict[str, Any]:
        """Check if the environment provides enough diagnostics."""
        audit = {
            "os": platform.system(),
            "cpu_count": psutil.cpu_count(),
            "has_lmdb": self.lmdb is not None,
            "has_psutil": True,
            "observability_status": "Healthy"
        }
        
        # Check for common constraints
        if psutil.virtual_memory().available < 500 * 1024 * 1024:
            audit["observability_status"] = "Memory Constrained"
            
        return audit

    def define_artifact_requirement(self, software_type: str) -> List[str]:
        """Define what logs/metrics are required for a specific software type."""
        if software_type == "neural":
            return ["token_usage", "temperature_log", "latency_metrics", "grounding_context"]
        return ["stack_trace", "activity_history", "diff_logs"]
