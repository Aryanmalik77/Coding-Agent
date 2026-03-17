"""Fortress Device: Unified control interface for the Incremental Fortress."""

from typing import Dict, List, Any, Optional
from loguru import logger
from coding_agent.fortress.engine import FortressEngine
from coding_agent.fortress.responsibility import ResponsibilityTier

class FortressDevice:
    """
    The 'Device' as requested by the user, unifying the Fortress modules.
    Acts as a high-level controller for defense, observability, and responsibility.
    """

    def __init__(self, engine: FortressEngine):
        self.engine = engine
        logger.info("Fortress Device initialized and online.")

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Perform a complete health check of the agent's defense systems."""
        env_audit = self.engine.observability.audit_system_environment()
        unresolved = self.engine.registry.get_unresolved_issues()
        priorities = self.engine.prioritize_objectives()
        
        return {
            "status": "Operational",
            "environment": env_audit,
            "unresolved_issue_count": len(unresolved),
            "top_priority_objective": priorities[0]['title'] if priorities else "None"
        }

    def assess_task_responsibility(self, task: str) -> Dict[str, Any]:
        """Assess the responsibility tier and requirements for a given task."""
        tier = self.engine.responsibility.map_objective_to_tier(task, "Autonomous Assessment")
        reqs = self.engine.responsibility.get_tier_requirements(tier)
        
        return {
            "task": task,
            "tier": tier.value,
            "requirements": reqs
        }

    def deploy_mitigation(self, issue_id: str) -> str:
        """Deploy a synthesized resolution path for an issue."""
        path = self.engine.synthesize_resolution_path(issue_id)
        # Log active mitigation
        logger.warning(f"Deploying mitigation strategy: {path['strategy_name']}")
        return f"Deployment initiated for {issue_id}. Strategy: {path['strategy_name']}"
