"""Domain-based MCP server selection and routing."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from coding_agent.swarm.lmdb_store import LMDBStore


@dataclass
class RoutingRule:
    """A single domain→server routing rule."""
    domain: str
    server_pattern: str
    keywords: list[str] = field(default_factory=list)
    priority: int = 0


_DEFAULT_RULES: list[RoutingRule] = [
    RoutingRule(
        domain="code",
        server_pattern="cocoindex",
        keywords=["code", "search code", "function", "class", "semantic", "architecture", "embedding"],
        priority=10,
    ),
    RoutingRule(
        domain="filesystem",
        server_pattern="filesystem",
        keywords=["file", "directory", "path", "read", "write", "delete file"],
        priority=3,
    ),
    RoutingRule(
        domain="git",
        server_pattern="git",
        keywords=["git", "commit", "branch", "merge", "pull request", "push"],
        priority=5,
    ),
]


class MCPRouter:
    """Routes task contexts to the best-fit MCP server."""

    def __init__(self, lmdb: LMDBStore | None = None):
        self._lmdb = lmdb
        self._rules: list[RoutingRule] = list(_DEFAULT_RULES)
        self._server_names: set[str] = set()
        self._load_learned_routes()

    def register_server(self, server_name: str) -> None:
        self._server_names.add(server_name)

    def _load_learned_routes(self) -> None:
        if not self._lmdb:
            return
        try:
            for key, val in self._lmdb.prefix_scan("trigger:mcp_route:"):
                if isinstance(val, dict):
                    self._rules.append(RoutingRule(
                        domain=val.get("domain", "unknown"),
                        server_pattern=val.get("server_pattern", ""),
                        keywords=val.get("keywords", []),
                        priority=val.get("priority", 1),
                    ))
        except Exception as exc:
            logger.debug("MCPRouter: could not load learned routes: {}", exc)

    def route(self, task_context: str) -> str | None:
        """Return the best MCP server name for the given task context."""
        task_lower = task_context.lower()
        scored: list[tuple[int, RoutingRule]] = []

        for rule in self._rules:
            score = 0
            for kw in rule.keywords:
                if kw in task_lower:
                    score += rule.priority
            if score > 0:
                scored.append((score, rule))

        if not scored:
            return None

        scored.sort(key=lambda t: t[0], reverse=True)
        best_rule = scored[0][1]

        for sn in self._server_names:
            if best_rule.server_pattern in sn:
                return sn

        return best_rule.server_pattern
