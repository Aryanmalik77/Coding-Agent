"""Fortress Responsibility Scoper: Mapping goals to responsibility tiers."""

from enum import Enum
from typing import Dict, List, Any
from loguru import logger

class ResponsibilityTier(Enum):
    SELF = "self"                # Internal agent health and state
    OTHER = "other"              # External interactions and tools
    GREATER = "greater"          # Holistic system integrity and long-term evolution

class ResponsibilityScoper:
    """
    Categorizes objectives and actions into responsibility tiers.
    Helps the agent decide when it can act autonomously vs when it needs human approval.
    """

    def __init__(self, lmdb_store: Any):
        self.lmdb = lmdb_store
        logger.info("Fortress Responsibility Scoper initialized.")

    def map_objective_to_tier(self, title: str, description: str) -> ResponsibilityTier:
        """Heuristically map an objective to a responsibility tier."""
        text = (title + " " + description).lower()
        
        if any(kw in text for kw in ["delete", "wipe", "format", "critical", "architectural shift"]):
            return ResponsibilityTier.GREATER
        
        if any(kw in text for kw in ["search", "scrape", "display", "print", "news"]):
            return ResponsibilityTier.OTHER
            
        return ResponsibilityTier.SELF

    def get_tier_requirements(self, tier: ResponsibilityTier) -> Dict[str, Any]:
        """Get the operational requirements for a specific tier."""
        if tier == ResponsibilityTier.GREATER:
            return {
                "human_approval_required": True,
                "pre_snapshot_required": True,
                "verification_depth": "deep"
            }
        elif tier == ResponsibilityTier.OTHER:
            return {
                "human_approval_required": False,
                "pre_snapshot_required": False,
                "verification_depth": "standard"
            }
        else: # SELF
            return {
                "human_approval_required": False,
                "pre_snapshot_required": True,
                "verification_depth": "standard"
            }
