"""Evolution and versioning tools for architectural awareness."""

from pathlib import Path
from typing import Any, Optional
from loguru import logger

from coding_agent.evolution.tracker import EvolutionTracker
from coding_agent.evolution.versioning import VersionManager

class RecordEvolutionOutcomeTool:
    """Record tangible results and side-effects of a code change."""

    def __init__(self, tracker: EvolutionTracker):
        self._tracker = tracker

    @property
    def name(self) -> str: return "record_evolution_outcome"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "record_id": {"type": "string"},
                "actual_outcome": {"type": "string"},
                "capabilities_altered": {"type": "string"},
                "side_effects": {"type": "string"},
                "tangible_results": {"type": "string"},
                "commit_hash": {"type": "string"},
            },
            "required": ["record_id", "actual_outcome", "capabilities_altered"],
        }

    async def execute(self, record_id: str, actual_outcome: str, capabilities_altered: str, 
                     side_effects: str = "", tangible_results: str = "", commit_hash: str = "", **kwargs: Any) -> str:
        try:
            success = self._tracker.record_outcome(
                record_id=record_id,
                actual_outcome=actual_outcome,
                capabilities_altered=capabilities_altered,
                side_effects=side_effects,
                tangible_results=tangible_results,
                commit_hash=commit_hash
            )
            if success:
                return f"Successfully recorded evolution outcome for {record_id}."
            return f"Failed to find record {record_id}."
        except Exception as e:
            return f"Error: {e}"


class RevertToHistoricalVersionTool:
    def __init__(self, version_manager: VersionManager):
        self._vm = version_manager

    @property
    def name(self) -> str: return "revert_to_version"

    async def execute(self, file_path: str, record_id: str, **kwargs: Any) -> str:
        success = self._vm.revert_to_version(file_path, record_id)
        return "Success" if success else "Failed"


class AddEvolutionInsightTool:
    def __init__(self, tracker: EvolutionTracker):
        self._tracker = tracker

    @property
    def name(self) -> str: return "add_evolution_insight"

    async def execute(self, record_id: str, insight: str, **kwargs: Any) -> str:
        success = self._tracker.add_insight(record_id, insight)
        return "Insight added" if success else "Record not found"
