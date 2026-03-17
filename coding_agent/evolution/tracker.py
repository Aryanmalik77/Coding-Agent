"""Advanced architectural evolution and code impact tracker."""

import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, Any

from loguru import logger

from coding_agent.swarm.lmdb_store import LMDBStore
from coding_agent.swarm.graph_store import GraphStore


@dataclass
class EvolutionRecord:
    id: str
    timestamp: float
    file_path: str
    reasoning: str
    expected_outcome: str
    actual_outcome: Optional[str] = None
    capabilities_altered: Optional[str] = None
    side_effects: Optional[str] = None
    tangible_results: Optional[str] = None
    commit_hash: Optional[str] = None
    human_insights: list[str] = field(default_factory=list)
    rationales: list[str] = field(default_factory=list)


class EvolutionTracker:
    """
    Persists and tracks the intent, expected outcomes, and actual
    tangible results of code changes across the architecture.
    """

    def __init__(self, workspace: Path, lmdb: LMDBStore, graph: Optional[GraphStore] = None):
        self.workspace = workspace
        self.lmdb = lmdb
        self.graph = graph

    def record_intent(
        self, file_path: str, reasoning: str, expected_outcome: str
    ) -> str:
        """Record the intent to change a file."""
        record_id = f"evo_{uuid.uuid4().hex[:8]}"
        record = EvolutionRecord(
            id=record_id,
            timestamp=time.time(),
            file_path=file_path,
            reasoning=reasoning,
            expected_outcome=expected_outcome,
        )
        self.lmdb.put(f"evolution:intent:{record_id}", asdict(record))
        logger.debug(f"Recorded evolution intent {record_id} for {file_path}")
        return record_id

    def record_outcome(
        self,
        record_id: str,
        actual_outcome: str,
        capabilities_altered: str,
        side_effects: str = "",
        tangible_results: str = "",
        commit_hash: Optional[str] = None,
    ) -> bool:
        """Update an intent record with the actual outcome, side-effects and capability shifts."""
        data = self.lmdb.get(f"evolution:intent:{record_id}")
        if not data:
            logger.error(f"Cannot find evolution intent record {record_id}")
            return False

        # Migrate data to current record structure
        record_dict = dict(data)
        record_dict["actual_outcome"] = actual_outcome
        record_dict["capabilities_altered"] = capabilities_altered
        record_dict["side_effects"] = side_effects
        record_dict["tangible_results"] = tangible_results
        record_dict["commit_hash"] = commit_hash

        record = EvolutionRecord(**record_dict)

        # Move from intent space to outcome space
        self.lmdb.delete(f"evolution:intent:{record_id}")
        
        # We index by file path prefix so we can quickly scan a file's history
        key = f"evolution:record:{record.file_path}:{record_id}"
        self.lmdb.put(key, asdict(record))

        # Record in graph store for deep architectural tracing
        if self.graph is not None:
            try:
                self.graph.create_node(
                    "EvolutionNode",
                    record_id,
                    {
                        "file_path": record.file_path,
                        "reason": record.reasoning,
                        "expected": record.expected_outcome,
                        "actual": record.actual_outcome or "",
                        "capabilities": record.capabilities_altered or "",
                        "side_effects": record.side_effects or "",
                        "tangible_results": record.tangible_results or "",
                        "insights": " | ".join(getattr(record, "human_insights", [])),
                    }
                )
                
                # If there are previous records for this file, link them in the graph
                # (Simple linear evolution link for now)
                history = self.get_history(record.file_path)
                if len(history) > 1:
                    prev_id = history[1].get("id")
                    if prev_id:
                         self.graph.create_edge("EVOLVED_INTO", prev_id, record_id)

            except Exception as e:
                logger.warning(f"Failed to index evolution in graph: {e}")

        logger.info(f"Evolution {record_id} completed for {record.file_path}")
        return True

    def get_history(self, file_path: str) -> list[dict]:
        """Fetch all evolution records for a given file."""
        history = []
        for key, val in self.lmdb.prefix_scan(f"evolution:record:{file_path}:"):
            history.append(val)
        return sorted(history, key=lambda x: x.get("timestamp", 0.0), reverse=True)

    def add_insight(self, record_id: str, insight: str) -> bool:
        """Add a human insight or rationalized justification to an evolution record."""
        # 1. Check intent space
        data = self.lmdb.get(f"evolution:intent:{record_id}")
        if data:
            data.setdefault("human_insights", []).append(insight)
            self.lmdb.put(f"evolution:intent:{record_id}", data)
            return True

        # 2. Check outcome space
        for key, val in self.lmdb.prefix_scan("evolution:record:"):
            if val.get("id") == record_id:
                val.setdefault("human_insights", []).append(insight)
                self.lmdb.put(key, val)
                return True
                
        return False
