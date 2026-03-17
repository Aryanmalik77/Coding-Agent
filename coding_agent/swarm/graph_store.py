"""KuzuDB-backed graph store for the Advanced Coding Agent."""

import os
import sqlite3
import json
from pathlib import Path
from typing import Any, Optional

from loguru import logger

try:
    import kuzu
    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False
    logger.warning("KuzuDB not available. Falling back to SQLite graph emulation.")


class GraphStore:
    """
    Graph topology store for architectural awareness and knowledge.
    """
    kuzu_db: Any = None
    kuzu_conn: Any = None
    sqlite_conn: Optional[sqlite3.Connection] = None

    def __init__(self, workspace: Path, db_name: str = "coding_agent_graph.kuzu"):
        self.db_path = workspace / db_name
        os.makedirs(self.db_path, exist_ok=True)
        
        self.kuzu_db = None
        self.kuzu_conn = None
        self.sqlite_conn = None

        if KUZU_AVAILABLE:
            try:
                self.kuzu_db = kuzu.Database(str(self.db_path))
                self.kuzu_conn = kuzu.Connection(self.kuzu_db)
                self._init_kuzu_schema()
                logger.debug("Initialized KuzuDB at {}", self.db_path)
            except Exception as e:
                logger.error("Failed to initialize KuzuDB: {}. Falling back to SQLite.", e)
                self._init_sqlite_fallback(workspace / "coding_agent_graph.sqlite")
        else:
            self._init_sqlite_fallback(workspace / "coding_agent_graph.sqlite")

    def _init_kuzu_schema(self):
        k_conn = self.kuzu_conn
        if k_conn is None:
            return

        try:
            k_conn.execute("MATCH (n:EvolutionNode) RETURN count(n)")
            schema_exists = True
        except RuntimeError:
            schema_exists = False

        if schema_exists:
            return

        logger.info("Creating KuzuDB schema for Coding Agent Identity...")

        nodes = [
            "CREATE NODE TABLE EvolutionNode (id STRING, file_path STRING, reason STRING, expected STRING, actual STRING, capabilities STRING, side_effects STRING, tangible_results STRING, PRIMARY KEY (id))",
            "CREATE NODE TABLE DesignPattern (id STRING, name STRING, category STRING, rationale STRING, snippet STRING, cleverness INT64, PRIMARY KEY (id))",
            "CREATE NODE TABLE SystemComponent (id STRING, name STRING, responsibility STRING, status STRING, PRIMARY KEY (id))",
            "CREATE NODE TABLE IdentityFacet (id STRING, name STRING, content STRING, PRIMARY KEY (id))",
            "CREATE NODE TABLE CaseStudy (id STRING, title STRING, implementation_details STRING, benchmark_results STRING, source_url STRING, essence STRING, monetization_model STRING, PRIMARY KEY (id))",
            "CREATE NODE TABLE ImplementationJustification (id STRING, rationale STRING, mathematical_model STRING, resource_tradeoffs STRING, physical_limits STRING, resource_budget STRING, PRIMARY KEY (id))",
        ]

        edges = [
            "CREATE REL TABLE EVOLVED_INTO (FROM EvolutionNode TO EvolutionNode)",
            "CREATE REL TABLE INSPIRES_DESIGN (FROM DesignPattern TO EvolutionNode, FROM DesignPattern TO SystemComponent)",
            "CREATE REL TABLE MANAGES (FROM SystemComponent TO EvolutionNode)",
            "CREATE REL TABLE DEFINES_IDENTITY (FROM IdentityFacet TO SystemComponent)",
            "CREATE REL TABLE JUSTIFIES (FROM ImplementationJustification TO SystemComponent, FROM ImplementationJustification TO DesignPattern)",
            "CREATE REL TABLE RESEARCHED_FROM (FROM CaseStudy TO DesignPattern, FROM CaseStudy TO ImplementationJustification)",
        ]

        for query in nodes + edges:
            try:
                if k_conn is not None:
                    k_conn.execute(query)
            except RuntimeError as e:
                logger.warning("Schema creation notice: {}", e)

    def _init_sqlite_fallback(self, db_path: Path):
        conn = sqlite3.connect(str(db_path))
        self.sqlite_conn = conn
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                props_json TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                rel_type TEXT NOT NULL,
                props_json TEXT,
                FOREIGN KEY (source_id) REFERENCES graph_nodes(id),
                FOREIGN KEY (target_id) REFERENCES graph_nodes(id)
            )
        ''')
        
        self.sqlite_conn.commit()
        logger.debug("Initialized SQLite graph fallback at {}", db_path)

    def create_node(self, label: str, node_id: str, props: dict[str, Any]) -> None:
        k_conn = self.kuzu_conn
        if k_conn is not None:
            props["id"] = node_id
            # Ensure properties are primitives or serialized for Kuzu
            processed_props = {}
            for k, v in props.items():
                if isinstance(v, (dict, list)) and k != "id":
                    processed_props[k] = json.dumps(v)
                else:
                    processed_props[k] = v
            
            prop_str = ", ".join([f"{k}: ${k}" for k in processed_props.keys()])
            query = f"CREATE (n:{label} {{{prop_str}}})"
            try:
                k_conn.execute(query, processed_props)
            except RuntimeError as e:
                logger.warning("Node creation warning: {}", e)
        elif self.sqlite_conn is not None:
            cursor = self.sqlite_conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO graph_nodes (id, label, props_json) VALUES (?, ?, ?)",
                    (node_id, label, json.dumps(props))
                )
                if self.sqlite_conn is not None:
                    self.sqlite_conn.commit()
            except sqlite3.IntegrityError:
                cursor.execute(
                    "UPDATE graph_nodes SET props_json = ? WHERE id = ? AND label = ?",
                    (json.dumps(props), node_id, label)
                )
                if self.sqlite_conn is not None:
                    self.sqlite_conn.commit()

    def update_node_properties(self, label: str, node_id: str, props: dict[str, Any]) -> None:
        """Update properties of an existing node in the graph."""
        if self.kuzu_conn:
            prop_updates = ", ".join([f"n.{k} = ${k}" for k in props.keys()])
            query = f"MATCH (n:{label}) WHERE n.id = $id SET {prop_updates}"
            params = {"id": node_id, **props}
            try:
                self.kuzu_conn.execute(query, params)
            except RuntimeError as e:
                logger.warning("Node property update warning: {}", e)
        elif self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT props_json FROM graph_nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            if row:
                current_props = json.loads(row[0])
                current_props.update(props)
                cursor.execute(
                    "UPDATE graph_nodes SET props_json = ? WHERE id = ?",
                    (json.dumps(current_props), node_id)
                )
                self.sqlite_conn.commit()

    def create_edge(self, rel_type: str, source_id: str, target_id: str, props: dict[str, Any] | None = None) -> None:
        props = props or {}
        if self.kuzu_conn:
            prop_str = ""
            if props:
                prop_str = " {" + ", ".join([f"{k}: ${k}" for k in props.keys()]) + "}"
            query = f"MATCH (a), (b) WHERE a.id = $source_id AND b.id = $target_id CREATE (a)-[r:{rel_type}{prop_str}]->(b)"
            params = {"source_id": source_id, "target_id": target_id, **props}
            try:
                self.kuzu_conn.execute(query, params)
            except RuntimeError as e:
                 logger.warning("Edge creation warning: {}", e)
        elif self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT INTO graph_edges (source_id, target_id, rel_type, props_json) VALUES (?, ?, ?, ?)",
                (source_id, target_id, rel_type, json.dumps(props))
            )
            self.sqlite_conn.commit()

    def search_knowledge(self, label: str, keyword: str) -> list[dict[str, Any]]:
        """Search for knowledge nodes matching a keyword in their properties."""
        results = []
        k_conn = self.kuzu_conn
        if k_conn is not None:
            # Simple keyword match in title, rationale, implementation_details, or essence
            query = f"MATCH (n:{label}) WHERE n.title CONTAINS $kw OR n.rationale CONTAINS $kw OR n.implementation_details CONTAINS $kw OR n.essence CONTAINS $kw RETURN n.*"
            try:
                res = k_conn.execute(query, {"kw": keyword})
                while res.has_next():
                    results.append(res.get_next())
            except Exception:
                pass 
        elif self.sqlite_conn is not None:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                f"SELECT props_json FROM graph_nodes WHERE label = ? AND props_json LIKE ?",
                (label, f"%{keyword}%")
            )
            rows = cursor.fetchall()
            for row in rows:
                results.append(json.loads(row[0]))
        return results

    async def hybrid_search(self, label: str, query: str, semantic_tool: Any = None, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Performs hybrid search: Lexical (SQLite/Kuzu) + Semantic (CocoIndex).
        """
        # 1. Lexical Search (Keyword matching)
        lexical_results = self.search_knowledge(label, query)
        
        # 2. Semantic Search (via cocoindex if provided)
        semantic_results = []
        if semantic_tool:
            try:
                # We expect the tool to return a list of dicts or a string to parse
                raw_res = await semantic_tool.execute(query=query)
                if isinstance(raw_res, str):
                    # Mocking parsing if the tool returns a summary string
                    # In a real scenario, cocoindex might return structured node IDs
                    pass
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")

        # Merge and deduplicate (simple merge for now)
        seen_ids = set()
        final_results = []
        for res in lexical_results:
            node_id = res.get('id')
            if node_id not in seen_ids:
                final_results.append(res)
                seen_ids.add(node_id)
        
        # (Ranking logic could be added here)
        return final_results[:top_k]

    def close(self):
        s_conn = self.sqlite_conn
        if s_conn is not None:
            s_conn.close()
