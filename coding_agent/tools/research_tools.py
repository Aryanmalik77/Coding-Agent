"""Tools for architectural research and benchmark."""

from typing import Any, Optional
from coding_agent.identity.researcher import ArchitecturalResearcher

class BenchmarkDesignTool:
    def __init__(self, researcher: ArchitecturalResearcher):
        self._researcher = researcher

    @property
    def name(self) -> str: return "benchmark_design"

    @property
    def description(self) -> str:
        return "Search for industry standards and clever architectural solutions for a topic."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"topic": {"type": "string"}},
            "required": ["topic"],
        }

    async def execute(self, topic: str, **kwargs: Any) -> str:
        return await self._researcher.benchmark_design(topic)


class AppreciateFeatureTool:
    def __init__(self, researcher: ArchitecturalResearcher):
        self._researcher = researcher

    @property
    def name(self) -> str: return "appreciate_feature"

    @property
    def description(self) -> str:
        return "Explicitly record and classify a clever architectural feature encountered."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "snippet": {"type": "string"},
                "rationale": {"type": "string"},
            },
            "required": ["name", "snippet", "rationale"],
        }

    async def execute(self, name: str, snippet: str, rationale: str, **kwargs: Any) -> str:
        pid = self._researcher.appreciate_feature(name, snippet, rationale)
        return f"Innovative feature recorded with ID: {pid}"
