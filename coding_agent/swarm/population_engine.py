"""Population Engine: Ingests architectural knowledge into the GraphStore."""

import json
from pathlib import Path
from typing import Dict, Any, List
from coding_agent.swarm.graph_store import GraphStore
from coding_agent.subagents.keyword_extraction_agent import KeywordExtractionAgent

class PopulationEngine:
    def __init__(self, workspace: Path):
        self.graph = GraphStore(workspace)
        self.extractor = KeywordExtractionAgent()

    def ingest_case_study(self, study_id: str, data: Dict[str, Any]):
        """Ingest a case study and augment with architectural essence."""
        print(f"Ingesting Case Study: {data.get('title', study_id)}")
        
        # Extract Essence (OpenCodeWiki style)
        essence = self.extractor.extract_essence(data)
        data["essence"] = json.dumps(essence) # Store as string for Kuzu/SQLite simplicity
        
        self.graph.create_node("CaseStudy", study_id, data)

    def close(self):
        """Close database connections."""
        self.graph.close()

    def ingest_justification(self, justification_id: str, data: Dict[str, Any]):
        """Ingest a design justification (human input or calculation)."""
        print(f"Ingesting Justification: {justification_id}")
        self.graph.create_node("ImplementationJustification", justification_id, data)

    def link_evidence(self, case_study_id: str, justification_id: str, relationship: str = "RESEARCHED_FROM"):
        """Link evidence to justifications or components."""
        self.graph.create_edge(relationship, case_study_id, justification_id)

    def close(self):
        self.graph.close()
