"""Design Pattern Categorizer: Organizes learned knowledge."""

from typing import Any, Optional
from loguru import logger

class Categorizer:
    """
    Categorizes architectural features and patterns for easier
    retrieval and appreciation.
    """

    def __init__(self, encyclopedia: Any):
        self.encyclopedia = encyclopedia

    def classify_feature(self, name: str, snippet: str) -> str:
        """Suggest a category for a new architectural feature."""
        snippet_lower = snippet.lower()
        
        if "class " in snippet_lower and "abstract" in snippet_lower:
            return "abstraction_pattern"
        if "async " in snippet_lower or "await " in snippet_lower:
            return "async_concurrency"
        if "store" in snippet_lower or "db" in snippet_lower:
            return "persistence_layer"
        if "mcp" in snippet_lower or "server" in snippet_lower:
            return "integration_hook"
            
        return "general_design"
