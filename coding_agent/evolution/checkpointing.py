"""Checkpoint Manager for state snapshots and self-correction."""

import shutil
import time
from pathlib import Path
from loguru import logger

class CheckpointManager:
    """Manages workspace snapshots for state checkpointing and fallback."""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.checkpoints_dir = workspace / ".checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)

    def create_snapshot(self, label: str) -> str:
        """Create a full snapshot of the coding_agent directory."""
        snapshot_id = f"snap_{int(time.time())}_{label}"
        target_dir = self.checkpoints_dir / snapshot_id
        
        # We only snapshot the source code and configuration
        source_dir = self.workspace / "coding_agent"
        
        try:
            shutil.copytree(source_dir, target_dir)
            logger.info(f"Created state checkpoint: {snapshot_id}")
            return snapshot_id
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return ""

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore a workspace snapshot."""
        source_dir = self.checkpoints_dir / snapshot_id
        target_dir = self.workspace / "coding_agent"
        
        if not source_dir.exists():
            logger.error(f"Checkpoint {snapshot_id} does not exist.")
            return False
            
        try:
            shutil.rmtree(target_dir)
            shutil.copytree(source_dir, target_dir)
            logger.info(f"Restored state checkpoint: {snapshot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return False
