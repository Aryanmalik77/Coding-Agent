"""To-Do Subagent: Manages high-level project objectives."""

from pathlib import Path
from datetime import datetime
from coding_agent.subagents.base_agent import BaseSubagent

class ToDoSubagent(BaseSubagent):
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.todo_file = "TODO.md"

    def add_objective(self, objective: str, priority: str = "Medium"):
        """Add a high-level objective to the project To-Do list."""
        content = self.read_context_file(self.todo_file)
        if not content:
            content = "# Project To-Do List (Localized)\n\n"
        
        timestamp = datetime.now().isoformat()
        entry = f"- [ ] **{objective}** (Priority: {priority}) | Added: {timestamp}\n"
        
        if entry not in content:
            content += entry
            self.write_context_file(self.todo_file, content)
            return True
        return False

    def list_objectives(self):
        """Return all objectives from the local TODO.md."""
        content = self.read_context_file(self.todo_file)
        return [line.strip() for line in content.split("\n") if line.startswith("- [ ]")]

    def sync_with_global_strategy(self, fortress_engine):
        """
        Audit the local objectives against the global fortress strategy.
        (Passive registration of alignment).
        """
        objectives = self.list_objectives()
        for obj in objectives:
            fortress_engine.audit_objective_alignment() # Placeholder for complex logic
