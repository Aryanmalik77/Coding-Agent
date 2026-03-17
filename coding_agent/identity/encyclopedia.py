"""Identity Encyclopedia: Architectural awareness and knowledge management."""

from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

from loguru import logger

from coding_agent.swarm.lmdb_store import LMDBStore
from coding_agent.swarm.graph_store import GraphStore


class IdentityEncyclopedia:
    """
    Manages the 'Identity Awareness' of the coding agent.
    Stores and retrieves architectural artifacts, design patterns, and system components.
    """

    def __init__(self, workspace: Path, lmdb: LMDBStore, graph: Optional[GraphStore] = None):
        self.workspace = workspace
        self.lmdb = lmdb
        self.graph = graph

    def document_component(self, name: str, responsibility: str, status: str = "active") -> str:
        """Record a system component and its responsibility."""
        comp_id = f"comp_{name.lower().replace(' ', '_')}"
        data = {
            "id": comp_id,
            "name": name,
            "responsibility": responsibility,
            "status": status
        }
        self.lmdb.put(f"identity:component:{comp_id}", data)
        
        if self.graph is not None:
            self.graph.create_node("SystemComponent", comp_id, data)
            
        logger.info(f"Documented system component: {name}")
        return comp_id

    def record_design_pattern(self, name: str, category: str, rationale: str, snippet: str = "", cleverness: int = 5) -> str:
        """Learn and categorize a design pattern or clever architectural feature."""
        pattern_id = f"pattern_{uuid.uuid4().hex[:8]}"
        data = {
            "id": pattern_id,
            "name": name,
            "category": category,
            "rationale": rationale,
            "snippet": snippet,
            "cleverness": cleverness
        }
        self.lmdb.put(f"identity:pattern:{pattern_id}", data)
        
        if self.graph is not None:
            self.graph.create_node("DesignPattern", pattern_id, data)
            
        logger.info(f"Recorded design pattern: {name} (Category: {category})")
        return pattern_id

    def add_identity_facet(self, name: str, content: str) -> str:
        """Add a high-level identity facet (e.g., 'Core Purpose', 'Scaling Strategy')."""
        facet_id = f"facet_{name.lower().replace(' ', '_')}"
        data = {
            "id": facet_id,
            "name": name,
            "content": content
        }
        self.lmdb.put(f"identity:facet:{facet_id}", data)
        
        if self.graph is not None:
            self.graph.create_node("IdentityFacet", facet_id, data)
            
        logger.info(f"Added identity facet: {name}")
        return facet_id

    def update_component_status(self, name: str, status: str, metadata: Optional[dict] = None) -> bool:
        """Update the status and metadata of an existing system component."""
        comp_id = f"comp_{name.lower().replace(' ', '_')}"
        existing = self.lmdb.get(f"identity:component:{comp_id}")
        
        if not existing:
            # If it doesn't exist, we document it as new
            self.document_component(name, "Auto-discovered via task execution", status)
            return True
            
        existing["status"] = status
        if metadata:
            existing.setdefault("metadata", {}).update(metadata)
            
        self.lmdb.put(f"identity:component:{comp_id}", existing)
        
        if self.graph is not None:
            self.graph.update_node_properties("SystemComponent", comp_id, {"status": status})
            
        logger.info(f"Updated component status: {name} -> {status}")
        return True

    def query_component(self, name: str) -> Optional[dict]:
        comp_id = f"comp_{name.lower().replace(' ', '_')}"
        return self.lmdb.get(f"identity:component:{comp_id}")

    def list_patterns(self, category: Optional[str] = None) -> list[dict]:
        patterns = []
        for key, val in self.lmdb.prefix_scan("identity:pattern:"):
            if not category or val.get("category") == category:
                patterns.append(val)
        return patterns

    def get_full_identity_context(self) -> str:
        """Generate a summarized context of the agent's identity for specialized sub-agents."""
        facets = []
        for key, val in self.lmdb.prefix_scan("identity:facet:"):
            facets.append(f"## {val['name']}\n{val['content']}")
            
        components = []
        for key, val in self.lmdb.prefix_scan("identity:component:"):
            components.append(f"- **{val['name']}**: {val['responsibility']}")
            
        context = "# Identity Awareness\n\n"
        context += "\n\n".join(facets)
        context += "\n\n## Known System Components\n"
        context += "\n".join(components)
        
        return context
    def get_component_correlations(self) -> List[Dict[str, Any]]:
        """Retrieve all components and their responsibilities for correlation analysis."""
        components = []
        try:
            for _, val in self.lmdb.prefix_scan("identity:component:"):
                components.append(val)
            return components
        except Exception as e:
            logger.error(f"Failed to retrieve components: {e}")
            return []
