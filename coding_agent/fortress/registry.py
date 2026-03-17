"""Fortress Registry: Structured indexing of problems, bottlenecks, and shortcomings."""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
from loguru import logger

class IssueCategory(Enum):
    PROBLEM = "problem"
    DIFFICULTY = "difficulty"
    SHORTCOMING = "shortcoming"
    ERROR = "error"
    BOTTLENECK = "bottleneck"
    ROOT_CAUSE = "root_cause"
    OBSERVABILITY_CONSTRAINT = "observability_constraint"

class SoftwareType(Enum):
    DETERMINISTIC = "deterministic"
    NEURAL = "neural"
    SEMI_DETERMINISTIC = "semi_deterministic"

@dataclass
class FortressIssue:
    id: str = field(default_factory=lambda: f"issue_{uuid.uuid4().hex[:8]}")
    timestamp: float = field(default_factory=time.time)
    category: IssueCategory = IssueCategory.PROBLEM
    description: str = ""
    root_cause_id: Optional[str] = None
    software_type: SoftwareType = SoftwareType.DETERMINISTIC
    impact_level: int = 1  # 1-10
    prioritization_score: float = 0.0
    is_resolved: bool = False
    resolution_objective_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class FortressRegistry:
    """
    Central repository for tracking system weaknesses and constraints.
    """

    def __init__(self, lmdb_store: Any):
        self.lmdb = lmdb_store
        logger.info("Fortress Registry initialized.")

    def record_issue(self, category: IssueCategory, description: str, 
                    software_type: SoftwareType = SoftwareType.DETERMINISTIC,
                    metadata: Optional[Dict] = None) -> str:
        """Log a new issue in the fortress index."""
        issue = FortressIssue(
            category=category,
            description=description,
            software_type=software_type,
            metadata=metadata or {}
        )
        
        # Calculate initial priority (simplified for now)
        issue.prioritization_score = issue.impact_level * (1.0 if category == IssueCategory.ERROR else 0.5)
        
        try:
            # We convert enum to string for storage
            data = asdict(issue)
            data['category'] = issue.category.value
            data['software_type'] = issue.software_type.value
            
            self.lmdb.put(f"fortress:issue:{issue.id}", data)
            logger.info(f"Fortress indexed {category.value}: {issue.id} | {description[:50]}...")
            return issue.id
        except Exception as e:
            logger.error(f"Failed to index fortress issue: {e}")
            return ""

    def get_unresolved_issues(self) -> List[Dict]:
        """Retrieve all pending problems and shortcomings."""
        issues = []
        try:
            keys = self.lmdb.list_keys()
            issue_keys = [k for k in keys if k.startswith("fortress:issue:")]
            for k in issue_keys:
                data = self.lmdb.get(k)
                if data and not data.get('is_resolved'):
                    issues.append(data)
            
            # Sort by priority
            issues.sort(key=lambda x: x.get('prioritization_score', 0), reverse=True)
            return issues
        except Exception as e:
            logger.error(f"Failed to retrieve fortress issues: {e}")
            return []

    def link_root_cause(self, issue_id: str, root_cause_id: str):
        """Associate an issue with its identified root cause."""
        try:
            data = self.lmdb.get(f"fortress:issue:{issue_id}")
            if data:
                data['root_cause_id'] = root_cause_id
                self.lmdb.put(f"fortress:issue:{issue_id}", data)
                logger.info(f"Linked issue {issue_id} to root cause {root_cause_id}")
        except Exception as e:
            logger.error(f"Failed to link root cause: {e}")
