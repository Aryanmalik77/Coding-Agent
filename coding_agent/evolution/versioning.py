"""Version Manager for Code Evolution Fallbacks."""

import subprocess
from pathlib import Path
from typing import Optional

from loguru import logger

from coding_agent.evolution.tracker import EvolutionTracker


class VersionManager:
    """
    Manages historical module versions and Git-based code fallbacks
    using records from the EvolutionTracker.
    """

    def __init__(self, workspace: Path, tracker: EvolutionTracker):
        self.workspace = workspace
        self.tracker = tracker

    def _run_git(self, args: list[str]) -> str:
        """Helper to run git commands in the workspace."""
        cmd = ["git"] + args
        result = subprocess.run(
            cmd, cwd=self.workspace, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            logger.error(f"Git command failed: {' '.join(cmd)}\n{result.stderr}")
            raise RuntimeError(f"Git execution failed: {result.stderr}")
        return result.stdout.strip()

    def query_historical_behavior(self, file_path: str) -> list[dict]:
        """
        Query the list of past changes for a file to understand
        how its capabilities altered over time.
        """
        return self.tracker.get_history(file_path)

    def revert_to_version(self, file_path: str, record_id: str) -> bool:
        """
        Revert a specific file to the exact commit associated with an EvolutionRecord.
        """
        history = self.query_historical_behavior(file_path)
        record = next((r for r in history if r.get("id") == record_id), None)
        
        if not record:
            logger.error(f"Cannot find evolution record {record_id} for file {file_path}")
            return False

        commit_hash = record.get("commit_hash")
        if not commit_hash:
            logger.error(f"Record {record_id} does not have an associated git commit_hash.")
            return False

        try:
            logger.info(f"Reverting {file_path} to state from commit {commit_hash}")
            # Checkout the specific file from the recorded commit
            self._run_git(["checkout", commit_hash, "--", file_path])
            
            # Record why we did this
            new_intent = self.tracker.record_intent(
                file_path=file_path,
                reasoning=f"Fallback to previous behavior {record_id} (commit {commit_hash})",
                expected_outcome=record.get("expected_outcome", "Restored previous stable behavior"),
            )
            
            # Mark the outcome as complete for tracing
            self.tracker.record_outcome(
                record_id=new_intent,
                actual_outcome="File restored successfully via git checkout.",
                capabilities_altered=f"Reverted to capabilities of {record_id}",
                side_effects="Restored system to a known previous state.",
                tangible_results="Functionality reverted to historical baseline."
            )
            
            return True
            
        except RuntimeError as e:
            logger.error(f"Failed to revert {file_path}: {e}")
            return False

    def load_fallback_module(self, file_path: str, commit_hash: str) -> str:
        """
        Reads the contents of a file at a specific historical commit
        without overriding the current working directory copy.
        """
        try:
            # Handle Windows paths for Git
            relative_path = Path(file_path).absolute().relative_to(self.workspace).as_posix()
            return self._run_git(["show", f"{commit_hash}:{relative_path}"])
        except ValueError:
            logger.error(f"File {file_path} is not under workspace {self.workspace}")
            return ""
        except RuntimeError as e:
            logger.error(f"Failed to load fallback module {file_path} at {commit_hash}: {e}")
            return ""
