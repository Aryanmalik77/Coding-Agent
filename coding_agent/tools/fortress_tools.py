"""Fortress Tools: Agent tools for interacting with the Incremental Fortress architecture."""

from typing import Dict, List, Any, Optional
from loguru import logger
from coding_agent.fortress.registry import IssueCategory, SoftwareType

class FortressDiagnosticTool:
    """
    Diagnostic tool for auditing the agent's own shortcomings and bottlenecks.
    """
    name = "fortress_diagnostic"
    description = "Run a diagnostic audit of agent shortcomings, bottlenecks, and observability constraints."

    def __init__(self, fortress_engine: Any, activity_tracker: Any):
        self.fortress = fortress_engine
        self.tracker = activity_tracker

    async def execute(self, action: str = "audit", **kwargs) -> str:
        """
        Execute a fortress diagnostic action.
        Actions: 'audit', 'prioritize', 'record_issue', 'check_human', 'synthesize', 'device_audit', 'assess_responsibility'
        """
        logger.info(f"Executing Fortress Diagnostic: {action}")
        
        if action == "audit":
            # Get recent logs and run an observability audit
            logs = self.tracker.get_activity_history(limit=20)
            findings = self.fortress.run_observability_audit(logs)
            return f"Fortress Observability Audit: Found {len(findings)} items.\n" + "\n".join(findings)
            
        elif action == "prioritize":
            # Prioritize implementation objectives
            priorities = self.fortress.prioritize_objectives()
            result = "### Fortress Objective Priorities\n"
            for obj in priorities:
                result += f"- **{obj['title']}** (Weight: {obj['priority_weight']}): {obj['description']}\n"
            return result
            
        elif action == "record_issue":
            # Manually record an identified shortcoming
            cat = kwargs.get("category", "shortcoming")
            desc = kwargs.get("description", "No description provided")
            sw_type_str = kwargs.get("software_type", "deterministic")
            
            issue_id = self.fortress.registry.record_issue(
                category=IssueCategory(cat),
                description=desc,
                software_type=SoftwareType(sw_type_str)
            )
            return f"Fortress: Recorded {cat} {issue_id}"
            
        elif action == "check_human":
            # Determine if current task complexity requires human feedback
            task = kwargs.get("task", "unknown")
            failures = kwargs.get("failures", 0)
            required = self.fortress.check_human_requirement(task, failures)
            return "HUMAN_REQUIRED: True" if required else "HUMAN_REQUIRED: False"
            
        elif action == "synthesize":
            # Correlate an issue with a resolution path
            issue_id = kwargs.get("issue_id")
            if not issue_id: return "Error: issue_id required for synthesis"
            path = self.fortress.synthesize_resolution_path(issue_id)
            
            result = f"### Resolution Synthesis for {issue_id}\n"
            result += f"- **Strategy**: {path.get('strategy_name')}\n"
            result += "- **Recommended Actions**:\n"
            for act in path.get('recommended_actions', []):
                result += f"  - {act}\n"
            result += f"- **Risk Mitigation**: {path.get('risk_mitigation')}\n"
            result += f"- **Human in the Loop**: {path.get('human_in_the_loop')}\n"
            if path.get('rationale'):
                result += f"- **Rationale**: {path.get('rationale')}\n"
            return result
            
        elif action == "device_audit":
            # Access the underlying device for a full audit
            # Assuming the fortress engine has a 'device' attribute or we can access it
            # For simplicity, we implement it here using the engine's sub-modules
            env_audit = self.fortress.observability.audit_system_environment()
            return f"### Fortress Device Audit\nStatus: Operational\nEnvironment: {env_audit}"
            
        elif action == "assess_responsibility":
            task = kwargs.get("task", "unknown")
            tier = self.fortress.responsibility.map_objective_to_tier(task, "Autonomous Assessment")
            reqs = self.fortress.responsibility.get_tier_requirements(tier)
            return f"### Responsibility Assessment for '{task}'\nTier: {tier.value}\nRequirements: {reqs}"
            
        return f"Unknown fortress action: {action}"
