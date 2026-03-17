"""Fortress Objectives: Goal management and responsibility scoping."""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from enum import Enum
from loguru import logger

class ResponsibilityScope(Enum):
    SELF = "self"
    OTHER = "other"
    GREATER = "greater"

class ObjectiveStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    BLOCKED = "blocked"

@dataclass
class FortressObjective:
    id: str = field(default_factory=lambda: f"obj_{uuid.uuid4().hex[:8]}")
    title: str = ""
    description: str = ""
    status: ObjectiveStatus = ObjectiveStatus.PENDING
    responsibility: ResponsibilityScope = ResponsibilityScope.SELF
    dependencies: List[str] = field(default_factory=list) # List of objective IDs
    co_dependencies: List[str] = field(default_factory=list) # Bi-directional
    resources_shared: List[str] = field(default_factory=list) # e.g. ["api_key_1", "workspace_lock"]
    resource_budget: Dict[str, float] = field(default_factory=dict) # Daily limits: {"cpu_ms": 1000, "token_limit": 50000}
    monetization_metadata: Dict[str, Any] = field(default_factory=dict) # {"model": "subscription", "price": 9.99}
    revenue_potential: float = 0.0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class FortressObjectives:
    """
    Manages high-level goals and the distribution of responsibility.
    """

    def __init__(self, lmdb_store: Any):
        self.lmdb = lmdb_store
        logger.info("Fortress Objective Engine initialized.")

    def create_objective(self, title: str, description: str, 
                        scope: ResponsibilityScope = ResponsibilityScope.SELF,
                        dependencies: Optional[List[str]] = None,
                        resource_budget: Optional[Dict[str, float]] = None,
                        monetization_metadata: Optional[Dict[str, Any]] = None,
                        revenue_potential: float = 0.0,
                        metadata: Optional[Dict] = None) -> str:
        """Initialize a new strategic goal."""
        obj = FortressObjective(
            title=title,
            description=description,
            responsibility=scope,
            dependencies=dependencies or [],
            resource_budget=resource_budget or {},
            monetization_metadata=monetization_metadata or {},
            revenue_potential=revenue_potential,
            metadata=metadata or {}
        )
        
        try:
            data = asdict(obj)
            data['status'] = obj.status.value
            data['responsibility'] = obj.responsibility.value
            data['resource_budget'] = obj.resource_budget
            data['monetization_metadata'] = obj.monetization_metadata
            data['revenue_potential'] = obj.revenue_potential
            
            self.lmdb.put(f"fortress:objective:{obj.id}", data)
            logger.info(f"Fortress Objective created: {obj.id} | {title}")
            return obj.id
        except Exception as e:
            logger.error(f"Failed to create fortress objective: {e}")
            return ""

    def analyze_resource_sharing(self) -> Dict[str, List[str]]:
        """Identify which resources are being shared across different objectives."""
        sharing_map = {}
        try:
            keys = self.lmdb.list_keys()
            obj_keys = [k for k in keys if k.startswith("fortress:objective:")]
            for k in obj_keys:
                data = self.lmdb.get(k)
                if data and data.get('resources_shared'):
                    for res in data['resources_shared']:
                        if res not in sharing_map:
                            sharing_map[res] = []
                        sharing_map[res].append(data['id'])
            return sharing_map
        except Exception as e:
            logger.error(f"Failed to analyze resource sharing: {e}")
            return {}

    def update_status(self, obj_id: str, status: ObjectiveStatus):
        """Transition an objective to a new state."""
        try:
            data = self.lmdb.get(f"fortress:objective:{obj_id}")
            if data:
                data['status'] = status.value
                self.lmdb.put(f"fortress:objective:{obj_id}", data)
                logger.info(f"Objective {obj_id} status updated to {status.value}")
        except Exception as e:
            logger.error(f"Failed to update objective status: {e}")
