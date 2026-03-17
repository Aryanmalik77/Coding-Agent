"""Fortress GUI Context: Action indexing and multi-instance management."""

import time
from typing import Dict, List, Any, Optional
from loguru import logger

class GUIActionIndexer:
    """
    Tracks and indexes recursive/repetitive GUI actions across multiple instances.
    """

    def __init__(self, lmdb_store: Any):
        self.lmdb = lmdb_store
        logger.info("Fortress GUI Action Indexer initialized.")

    def index_action(self, instance_id: str, action_type: str, 
                     target_element: str, value: Optional[str] = None):
        """Record a GUI interaction, specifically for multi-window management."""
        action_id = f"gui_act_{int(time.time() * 1000)}"
        data = {
            "instance_id": instance_id, # e.g. "chrome_window_1"
            "type": action_type,
            "target": target_element,
            "value": value,
            "timestamp": time.time()
        }
        
        try:
            self.lmdb.put(f"fortress:gui_action:{action_id}", data)
            
            # Detect repetitive actions (simplified)
            self._analyze_repetition(instance_id, action_type, target_element)
        except Exception as e:
            logger.error(f"Failed to index GUI action: {e}")

    def _analyze_repetition(self, instance_id: str, action_type: str, target: str):
        """Track counter for repetitive actions to identify bottlenecks."""
        counter_key = f"fortress:gui_stats:{instance_id}:{action_type}:{target}"
        count = self.lmdb.get(counter_key) or 0
        count += 1
        self.lmdb.put(counter_key, count)
        
        if count > 5:
            logger.warning(f"Repetitive GUI action detected in {instance_id}: {action_type} on {target} (count: {count})")
