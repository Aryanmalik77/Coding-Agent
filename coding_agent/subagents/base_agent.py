"""Base Subagent: Core logic for project-local context management."""

from pathlib import Path
from typing import Optional
import os

class BaseSubagent:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.context_dir = project_path / ".fortress_context"
        self._ensure_context()

    def _ensure_context(self):
        """Ensure the local context directory exists."""
        self.context_dir.mkdir(parents=True, exist_ok=True)

    def read_context_file(self, filename: str) -> str:
        """Read a file from the local context."""
        file_path = self.context_dir / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""

    def write_context_file(self, filename: str, content: str):
        """Write a file to the local context."""
        file_path = self.context_dir / filename
        file_path.write_text(content, encoding="utf-8")
