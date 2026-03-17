"""Dependency Matrix: Tracking artifact dependencies across deterministic and neural systems."""

from typing import Dict, List, Any, Optional
from loguru import logger
from coding_agent.fortress.registry import SoftwareType

class DependencyMatrix:
    """
    Manages the web of dependencies between code artifacts, models, and data.
    """

    def __init__(self, lmdb_store: Any):
        self.lmdb = lmdb_store
        logger.info("Fortress Dependency Matrix initialized.")

    def register_dependency(self, source_path: str, target_path: str, 
                           dependency_type: str = "import",
                           source_sw_type: SoftwareType = SoftwareType.DETERMINISTIC,
                           target_sw_type: SoftwareType = SoftwareType.DETERMINISTIC):
        """Record a dependency between two artifacts."""
        dep_id = f"dep:{source_path}:{target_path}"
        data = {
            "source": source_path,
            "target": target_path,
            "type": dependency_type,
            "source_type": source_sw_type.value,
            "target_type": target_sw_type.value,
            "indeterministic_risk": 1.0 if target_sw_type == SoftwareType.NEURAL else 0.0
        }
        
        try:
            self.lmdb.put(f"fortress:dependency:{dep_id}", data)
            # Store reverse lookup for impact analysis
            self.lmdb.put(f"fortress:reverse_dep:{target_path}:{source_path}", source_path)
            logger.debug(f"Registered dependency: {source_path} -> {target_path} ({target_sw_type.value})")
        except Exception as e:
            logger.error(f"Failed to register dependency: {e}")

    def get_impact_surface(self, artifact_path: str) -> List[str]:
        """Find all artifacts that depend on the given path (upstream impact)."""
        impacted = []
        try:
            keys = self.lmdb.list_keys()
            prefix = f"fortress:reverse_dep:{artifact_path}:"
            for k in keys:
                if k.startswith(prefix):
                    impacted.append(self.lmdb.get(k))
            return impacted
        except Exception as e:
            logger.error(f"Failed to calculate impact surface: {e}")
            return []
    def get_all_dependencies(self) -> List[Dict[str, Any]]:
        """Retrieve all registered dependencies."""
        deps = []
        try:
            for _, val in self.lmdb.prefix_scan("fortress:dependency:"):
                deps.append(val)
            return deps
        except Exception as e:
            logger.error(f"Failed to retrieve all dependencies: {e}")
            return []
