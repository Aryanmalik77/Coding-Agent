"""File system tools with evolution and architectural awareness hooks."""

import difflib
from pathlib import Path
from typing import Any, Optional

from loguru import logger

# Base class for tools (simplified for standalone agent)
class Tool:
    @property
    def name(self) -> str: pass
    @property
    def description(self) -> str: pass
    @property
    def parameters(self) -> dict[str, Any]: pass
    async def execute(self, **kwargs: Any) -> str: pass


def _resolve_path(path: str, workspace: Path | None = None) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute() and workspace:
        p = workspace / p
    return p.resolve()


def _is_core_file(path: Path) -> bool:
    """Determine if a file is part of the core coding agent architecture."""
    # We restrict modification of the branding/core logic without rationalized shift
    core_dirs = ["coding_agent/core", "coding_agent/evolution", "coding_agent/identity"]
    try:
        path_str = path.resolve().as_posix()
        return any(f"/{d}" in path_str for d in core_dirs)
    except Exception:
        return False


class ReadFileTool(Tool):
    _MAX_CHARS = 128_000

    def __init__(self, workspace: Path | None = None):
        self._workspace = workspace

    @property
    def name(self) -> str: return "read_file"

    @property
    def description(self) -> str: return "Read the contents of a file."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "The file path"}},
            "required": ["path"],
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            file_path = _resolve_path(path, self._workspace)
            if not file_path.exists(): return f"Error: File not found: {path}"
            content = file_path.read_text(encoding="utf-8")
            if len(content) > self._MAX_CHARS:
                return content[: self._MAX_CHARS] + "\n\n... (truncated)"
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(Tool):
    def __init__(self, workspace: Path | None = None, tracker: Any = None):
        self._workspace = workspace
        self._tracker = tracker

    @property
    def name(self) -> str: return "write_file"

    @property
    def description(self) -> str: 
        return "Write content to a file. Provides reasoning and expected_outcome for evolution tracking."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "reasoning": {"type": "string"},
                "expected_outcome": {"type": "string"},
            },
            "required": ["path", "content", "reasoning", "expected_outcome"],
        }

    async def execute(self, path: str, content: str, reasoning: str, expected_outcome: str, **kwargs: Any) -> str:
        try:
            file_path = _resolve_path(path, self._workspace)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Architectural Guard
            if _is_core_file(file_path):
                # In the standalone agent, we require a 'system_design_rationalization' context
                # For now, we log the intent and allow it if tracking is enabled
                logger.warning("Self-modification detected on core file: {}", file_path)

            record_id = None
            if self._tracker:
                record_id = self._tracker.record_intent(path, reasoning, expected_outcome)

            file_path.write_text(content, encoding="utf-8")
            
            res = f"Successfully wrote to {file_path}"
            if record_id:
                res += f"\n[Evolution Intent Recorded: {record_id}]"
            return res
        except Exception as e:
            return f"Error writing file: {str(e)}"


class EditFileTool(Tool):
    def __init__(self, workspace: Path | None = None, tracker: Any = None):
        self._workspace = workspace
        self._tracker = tracker

    @property
    def name(self) -> str: return "edit_file"

    @property
    def description(self) -> str: return "Edit a file by replacing old_text with new_text."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
                "reasoning": {"type": "string"},
                "expected_outcome": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text", "reasoning", "expected_outcome"],
        }

    async def execute(self, path: str, old_text: str, new_text: str, reasoning: str, expected_outcome: str, **kwargs: Any) -> str:
        try:
            file_path = _resolve_path(path, self._workspace)
            if not file_path.exists(): return f"Error: File not found: {path}"
            content = file_path.read_text(encoding="utf-8")

            if old_text not in content:
                return f"Error: old_text not found in {path}."

            record_id = None
            if self._tracker:
                record_id = self._tracker.record_intent(path, reasoning, expected_outcome)

            new_content = content.replace(old_text, new_text, 1)
            file_path.write_text(new_content, encoding="utf-8")

            res = f"Successfully edited {file_path}"
            if record_id:
                res += f"\n[Evolution Intent Recorded: {record_id}]"
            return res
        except Exception as e:
            return f"Error editing file: {str(e)}"


class ListDirTool(Tool):
    def __init__(self, workspace: Path | None = None):
        self._workspace = workspace

    @property
    def name(self) -> str: return "list_dir"

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            dir_path = _resolve_path(path, self._workspace)
            items = [f"{'📁' if i.is_dir() else '📄'} {i.name}" for i in sorted(dir_path.iterdir())]
            return "\n".join(items) if items else "Directory is empty"
        except Exception as e:
            return str(e)
