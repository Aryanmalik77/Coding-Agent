"""Task Subagent: Manages granular task lifecycles and dependencies."""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from coding_agent.subagents.base_agent import BaseSubagent

class TaskSubagent(BaseSubagent):
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.tasks_file = "TASKS.md"

    def decompose_objective(self, objective: str, tasks: List[Dict[str, str]]):
        """Decompose a high-level objective into granular tasks in TASKS.md."""
        content = self.read_context_file(self.tasks_file)
        if not content:
            content = "# Project Task Graph (Localized)\n\n"
        
        timestamp = datetime.now().isoformat()
        content += f"## Objective: {objective} | {timestamp}\n"
        
        for task in tasks:
            task_id = task.get("id", "unknown")
            desc = task.get("description", "No description")
            dep = task.get("dependency", "None")
            
            content += f"- [ ] {desc} (ID: {task_id})\n"
            content += f"  - Dependency: {dep}\n"
            
        self.write_context_file(self.tasks_file, content)
        return True

    def record_architectural_delta(self, task_id: str, delta: str, fortress_engine):
        """Record an architectural shift resulting from a task completion."""
        # Passive observation: Fortress records the delta
        fortress_engine.record_design_delta(f"Task {task_id}: {delta}")
