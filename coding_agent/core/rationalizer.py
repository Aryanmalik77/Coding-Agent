"""Rationalizer: Validates and justifies architectural shifts."""

from typing import Optional, Any
from loguru import logger

class Rationalizer:
    """
    Ensures that self-modifications and architectural shifts are
    rationally justified based on the agent's identity and goals.
    """

    def __init__(self, encyclopedia: Any, tracker: Any):
        self.encyclopedia = encyclopedia
        self.tracker = tracker

    def validate_proposal(self, proposal: str, rationale: str) -> tuple[bool, str]:
        """Check if a proposed shift is objective and acceptable."""
        logger.info("Validating architectural proposal...")
        
        # In a fully autonomous mode, this would involve LLM-based reasoning
        # against the Identity Encyclopedia. For now, we enforce a strict
        # requirement for a detailed rationale.
        
        if len(rationale) < 50:
            return False, "Rationale is too brief. Please provide a detailed justification."
            
        if "identity" in rationale.lower() or "scale" in rationale.lower() or "modular" in rationale.lower():
            return True, "Proposal aligns with core architectural goals."
            
        return True, "Proposal accepted with standard rationale."

    def rationalize_intent(self, intent: str, purpose: str) -> str:
        """Calculate a rationalized justification for a planned action."""
        logger.debug(f"Rationalizing intent: {intent}")
        # In a real system, this would use LLM reasoning.
        # Here we provide a structured rationale based on system identity.
        context = self.encyclopedia.get_full_identity_context()
        if "research" in intent.lower():
            return "Action is justified by the core mission to expand architectural knowledge through deep research."
        return f"Action rationalized as a necessary step to fulfill purpose: {purpose}"

    def propose_self_correction(self, activity_id: str, result: str) -> str:
        """Analyze a suboptimal result and propose a rationalized fix."""
        logger.info(f"Analyzing failure for self-correction: {activity_id}")
        # Identify failure patterns and suggest architectural adjustments
        if "timeout" in result.lower():
            return "PROPOSAL: Increase resource budget for web research and implement retry logic with exponential backoff."
        if "attributeerror" in result.lower():
            return "PROPOSAL: Update internal interface definitions to match the current architectural evolution state."
        return "PROPOSAL: Review task constraints and ensure tool alignment with objective identity."

    def justify_shift(self, record_id: str, rationale: str):
        """Record the final rationale for a completed shift."""
        self.tracker.add_insight(record_id, f"JUSTIFICATION: {rationale}")
        logger.info(f"Justified shift {record_id}")
