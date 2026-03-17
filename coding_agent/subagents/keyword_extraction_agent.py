"""Keyword Extraction Agent: Characterizes architectural essence for hybrid search."""

from typing import Dict, List, Any
import re

class KeywordExtractionAgent:
    """
    Subagent that analyzes case studies to extract high-essence 
    architectural keywords and structured attributes.
    """
    
    def __init__(self):
        # Essence keys to look for in content
        self.essence_schema = {
            "concurrency_model": ["async", "threaded", "parallel", "event-driven", "messaging", "blocking", "non-blocking"],
            "scalability_vector": ["horizontal", "vertical", "edge", "distributed", "sharding", "replication"],
            "bottleneck_profile": ["latency", "throughput", "io-bound", "cpu-bound", "memory-bound"],
            "deployment_topology": ["monolith", "microservices", "serverless", "p2p", "mesh"]
        }

    def extract_essence(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Processes a case study's title and details to extract architectural essence.
        """
        content = f"{data.get('title', '')} {data.get('implementation_details', '')} {data.get('benchmark_results', '')}".lower()
        extracted = {}
        
        for category, keywords in self.essence_schema.items():
            matches = []
            for kw in keywords:
                if re.search(rf"\b{kw}\b", content):
                    matches.append(kw)
            if matches:
                extracted[category] = matches
                
        return extracted

    def get_search_keywords(self, intent: str) -> List[str]:
        """
        Extracts key search terms from a user intent.
        """
        # Simple extraction for now: words with architectural weight
        weights = ["scale", "scaling", "real-time", "latency", "async", "distributed", "edge", "hft", "trading", "signal"]
        found = []
        for w in weights:
            if w in intent.lower():
                found.append(w)
        return found
