"""Recursive Decomposer: Breaks high-level objectives into granular sub-projects."""

from typing import List, Dict, Any, Optional
from loguru import logger
from coding_agent.fortress.objectives import ResponsibilityScope

class RecursiveDecomposer:
    """
    Analyzes high-level objectives and proposes a set of tactical sub-objectives (Child projects).
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace = workspace_path
        
        # Taxonomy of child project templates by category
        self.templates = {
            "Infrastructure": [
                {"title": "{parent} - Orchestration Layer", "desc": "Central API and process manager for {parent}."},
                {"title": "{parent} - Deployment Hook", "desc": "Autonomous CI/CD and hosting logic for {parent}."}
            ],
            "Research": [
                {"title": "{parent} - Data Ingestion", "desc": "Raw data scraping and ingestion pipeline for {parent}."},
                {"title": "{parent} - Synthesis Engine", "desc": "Recursive summarization and RAG indexing for {parent}."}
            ],
            "Finance": [
                {"title": "{parent} - Risk Engine", "desc": "Real-time risk monitoring and cap-management for {parent}."},
                {"title": "{parent} - Execution Bot", "desc": "High-frequency trade execution and order-routing for {parent}."}
            ],
            "Database": [
                {"title": "{parent} - Partition Manager", "desc": "Autonomous data sharding and partition logic for {parent}."},
                {"title": "{parent} - Sync Layer", "desc": "Distributed consistency and sync manager for {parent}."}
            ]
        }

    def propose_children(self, parent_title: str, category: str) -> List[Dict[str, Any]]:
        """Propose a set of child objectives based on parent category."""
        parent_name = parent_title.split(":")[0].strip()
        proposals = self.templates.get(category, [
            {"title": f"{parent_name} - Module Alpha", "desc": f"Primary functional module for {parent_name}."},
            {"title": f"{parent_name} - Documentation", "desc": f"Automated technical docs for {parent_name}."}
        ])
        
        # Hydrate templates
        hydrated = []
        for p in proposals:
            hydrated.append({
                "title": p["title"].format(parent=parent_name),
                "description": p["desc"].format(parent=parent_name),
                "category": category
            })
            
        logger.info(f"Decomposer proposed {len(hydrated)} children for {parent_name} ({category})")
        return hydrated
