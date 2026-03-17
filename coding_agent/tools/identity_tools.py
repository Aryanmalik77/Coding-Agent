"""Tools for managing architectural identity and encyclopedia."""

from typing import Any, Optional
from coding_agent.identity.encyclopedia import IdentityEncyclopedia

class DocumentSystemComponentTool:
    def __init__(self, encyclopedia: IdentityEncyclopedia):
        self._encyclopedia = encyclopedia

    @property
    def name(self) -> str: return "document_system_component"

    async def execute(self, name: str, responsibility: str, status: str = "active", **kwargs: Any) -> str:
        cid = self._encyclopedia.document_component(name, responsibility, status)
        return f"Component documented with ID: {cid}"


class RecordDesignPatternTool:
    def __init__(self, encyclopedia: IdentityEncyclopedia):
        self._encyclopedia = encyclopedia

    @property
    def name(self) -> str: return "record_design_pattern"

    async def execute(self, name: str, category: str, rationale: str, snippet: str = "", cleverness: int = 5, **kwargs: Any) -> str:
        pid = self._encyclopedia.record_design_pattern(name, category, rationale, snippet, cleverness)
        return f"Design pattern recorded with ID: {pid}"


class QueryEncyclopediaTool:
    def __init__(self, encyclopedia: IdentityEncyclopedia):
        self._encyclopedia = encyclopedia

    @property
    def name(self) -> str: return "query_encyclopedia"

    async def execute(self, **kwargs: Any) -> str:
        return self._encyclopedia.get_full_identity_context()
