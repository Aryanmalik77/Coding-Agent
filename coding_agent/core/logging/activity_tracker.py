"""Activity Tracker for recording agent tasks and design rationales."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict
from loguru import logger

@dataclass
class ActivityRecord:
    id: str = field(default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}")
    timestamp: float = field(default_factory=time.time)
    task_name: str = ""
    intent: str = ""
    purpose: str = ""
    process: str = ""
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    design_context: Optional[str] = None
    result: Optional[str] = None

class ActivityTracker:
    """
    Main engine for recording non-evolutionary high-level tasks.
    Captures the 'Why', 'How', and 'Intent' of all major agent actions.
    """

    def __init__(self, lmdb: Any):
        self.lmdb = lmdb # Reference to IdentityEncyclopedia's LMDBStore

    def log_activity(self, task_name: str, intent: str, purpose: str, 
                     process: str, rationale: str, metadata: Optional[Dict] = None) -> str:
        record = ActivityRecord(
            task_name=task_name,
            intent=intent,
            purpose=purpose,
            process=process,
            rationale=rationale,
            metadata=metadata or {}
        )
        
        logger.info(f"Logging Activity: {task_name} | Intent: {intent}")
        
        # Store in Encyclopedia (LMDB)
        try:
            self.lmdb.put(f"activity:{record.id}", record.__dict__)
            
            # Link to architectural context if present
            if metadata and "component" in metadata:
                self.lmdb.put(f"component:activity:{metadata['component']}:{record.id}", record.id)
        except Exception as e:
            logger.error(f"Failed to store activity log: {e}")
            
        return record.id

    def update_activity_result(self, activity_id: str, result: str) -> None:
        """Update an existing activity record with its final result."""
        try:
            key = f"activity:{activity_id}"
            data = self.lmdb.get(key)
            if data:
                data['result'] = result
                self.lmdb.put(key, data)
                logger.debug(f"Updated activity {activity_id} with result context.")
        except Exception as e:
            logger.error(f"Failed to update activity result: {e}")

    def get_activity_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent activity logs from LMDB."""
        logs = []
        try:
            # We iterate through keys starting with 'activity:'
            # Note: This is a simplified iteration for the standalone implementation
            keys = self.lmdb.list_keys()
            act_keys = [k for k in keys if k.startswith("activity:")]
            # Sort by timestamp (descending)
            records = []
            for k in act_keys:
                data = self.lmdb.get(k)
                if data:
                    records.append(data)
            
            records.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return records[:limit]
        except Exception as e:
            logger.error(f"Failed to retrieve activity history: {e}")
            return []
