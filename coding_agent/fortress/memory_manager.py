"""Fortress Memory Manager: Persistent tracking of architectural health and capabilities."""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger
import datetime

class FortressMemoryManager:
    """
    Manages the 'Subagent Memory' by maintaining structured markdown files
    representing the agent's identity, design knowledge, and execution history.
    """

    def __init__(self, fortress_workspace: Path):
        self.workspace = fortress_workspace
        self.memory_dir = self.workspace / "memory"
        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"Fortress Memory Manager initialized at {self.memory_dir}")
        self._initialize_memory_files()

    def _initialize_memory_files(self):
        """Ensure core memory files exist."""
        files = {
            "CAPABILITIES.md": "# Agent Capabilities & Features\n\nLive tracking of functional modules and utilities.",
            "ACCESS_PRIVILEGES.md": "# Access Privileges & Governance\n\nDefined scopes and permissions for neural and deterministic operations.",
            "DESIGN_KNOWLEDGE.md": "# Software & System Design Knowledge Base\n\nShared architectural patterns and design best-practices.",
            "RCA_HISTORY.md": "# Root Cause Analysis (RCA) History\n\nTracking system errors and their fundamental causes.",
            "PRIORITY_LIST.md": "# Priority List of New Features\n\nRanked objectives for system evolution.",
            "AMBITION_TRACKER.md": "# Fortress Ambition & Capability Tracker\n\nHolistic tracking of digital ambition, resource control, financials, benchmarks, and competitive analysis.",
            "STRATEGIC_BENCHMARKS.md": "# Strategic Benchmarks & Usability Matrix\n\nComparative performance ratings and wider usability metrics across entities and competitors.",
            "RESOURCE_MANEUVERS.md": "# Resource Maneuvers & Scaling Logs\n\nAutonomous resource allocation and scaling decisions based on ambition requirements.",
            "SEMANTIC_MAP.md": "# Semantic Correlation Map\n\nFunctional overlaps and functional similarities detected across disconnected activities.",
            "QUIRK_REGISTRY.md": "# Architectural Quirk Registry\n\nTracking of architectural nuances, emergent behaviors, and behavior propagation transforms.",
            "MATHEMATICAL_LIBRARY.md": "# Mathematical Mastery Library\n\nCentralized repository of the agent's mathematical understanding and its software applicability.",
            "COMPUTATIONAL_NATURE.md": "# Computational Nature Analysis\n\nDeep audits of algorithmic complexity, resource intensity, and fundamental computational traits.",
            "TASK_GRAPH.md": "# Task Dependency Graph & Lifecycle Modeling\n\nExhaustive modeling of task branches, architectural dependencies, and evolutionary shifts.",
            "OBJECTIVE_ALIGNMENT.md": "# Strategic Objective Alignment\n\nSync logs between granular tasks and high-level deliverables/agendas.",
            "SCOPE_REGISTRY.md": "# Custom Scope & Boundary Registry\n\nDefined boundaries and focus areas for non-fortress entities in the workspace."
        }
        for filename, content in files.items():
            path = self.memory_dir / filename
            if not path.exists():
                header = f"{content}\n\n---\n*Created by Fortress Sentinel on {datetime.datetime.now().isoformat()}*\n\n"
                with open(path, "w", encoding="utf-8") as f:
                    f.write(header)

    def update_block(self, filename: str, section: str, content: str, append: bool = True):
        """Update or append to a specific section in a memory file."""
        path = self.memory_dir / filename
        if not path.exists():
            self._initialize_memory_files()
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            new_lines = []
            section_found = False
            skip = False
            
            header = f"## {section}"
            
            # If section exists, we might need to append within it or replace it
            for line in lines:
                if line.strip().startswith(header):
                    section_found = True
                    if append:
                        new_lines.append(line)
                    else:
                        new_lines.append(f"{header}\n{content}\n")
                        skip = True
                elif section_found and skip and line.strip().startswith("##"):
                    skip = False
                    new_lines.append(line)
                elif not skip:
                    new_lines.append(line)
            
            if not section_found:
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines.append("\n")
                new_lines.append(f"\n{header}\n{content}\n")
            elif append:
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines.append("\n")
                new_lines.append(f"{content}\n")
            
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
                
            logger.debug(f"Updated Fortress memory: {filename} -> {section}")
        except Exception as e:
            logger.error(f"Failed to update Fortress memory block: {e}")

    def log_rca(self, activity_id: str, error: str, root_cause: str, possibility_score: float):
        """Append a granular RCA entry to history."""
        entry = f"""
### Activity {activity_id} | {datetime.datetime.now().isoformat()}
- **Error**: {error}
- **Root Cause**: {root_cause}
- **Possibility Analysis Score**: {possibility_score}
- **Shortcomings Detected**: Potential lack of input validation or resource constraint.
"""
        self.update_block("RCA_HISTORY.md", "Recent Root Cause Analyses", entry)

    def log_ambition(self, activity_id: str, software_name: str, metrics: Dict[str, Any]):
        """Update the Ambition Tracker with new software metrics."""
        category = metrics.get("category", "General Utility")
        complexity = metrics.get("complexity", "Unknown")
        genius_score = metrics.get("genius_score", 0)
        costs = metrics.get("estimated_costs", "$0.00")
        resources = metrics.get("resources", "Local CPU/RAM")
        
        # New deep strategic metrics
        sophistication = metrics.get("sophistication", "Standard")
        hypothesis = metrics.get("hypothesis", "N/A")
        evidence = metrics.get("evidence", "N/A")
        
        entry = f"""
### {software_name} (Activity: {activity_id}) | {datetime.datetime.now().isoformat()}
- **Category**: {category}
- **Computational Complexity**: {complexity}
- **Architectural Genius Score**: {genius_score}/100
- **Sophistication Level**: {sophistication}
- **Controlled Resources**: {resources}
- **Financial Implication (Est. Cost)**: {costs}
- **Hypothesis**: {hypothesis}
- **Evidence/Metrics**: {evidence}
- **Ambition Alignment**: Contributing to digital dominance in '{category}' domain.
"""
        self.update_block("AMBITION_TRACKER.md", f"Recent Calibrations: {category}", entry)

    def log_benchmark(self, software_name: str, benchmark_data: Dict[str, Any]):
        """Record comparative performance and usability benchmarks."""
        rating = benchmark_data.get("rating", "N/A")
        usability = benchmark_data.get("usability", "N/A")
        popularity = benchmark_data.get("popularity", "N/A")
        ease_of_adoption = benchmark_data.get("ease_of_adoption", "N/A")
        competitor_analysis = benchmark_data.get("competitor_analysis", {})
        
        positives = ", ".join(competitor_analysis.get("positives", ["N/A"]))
        negatives = ", ".join(competitor_analysis.get("negatives", ["N/A"]))
        
        entry = f"""
### {software_name} | {datetime.datetime.now().isoformat()}
- **Performance Rating**: {rating}/10
- **Wider Usability**: {usability}
- **Market Popularity**: {popularity}
- **Ease of Adoption**: {ease_of_adoption}
- **Competitor Analysis**:
    - *Positives*: {positives}
    - *Negatives*: {negatives}
    - *Sophistication vs Market*: {competitor_analysis.get('sophistication_delta', 'Parity')}
"""
        self.update_block("STRATEGIC_BENCHMARKS.md", "Comparative Benchmarks", entry)

    def log_resource_maneuver(self, activity_id: str, maneuver_details: Dict[str, Any]):
        """Log an autonomous resource scaling or allocation decision."""
        resource_type = maneuver_details.get("resource_type", "Generic")
        action = maneuver_details.get("action", "Observation")
        reason = maneuver_details.get("reason", "Ambition alignment")
        delta = maneuver_details.get("delta", "N/A")
        
        entry = f"""
### {resource_type} Adjustment ({activity_id}) | {datetime.datetime.now().isoformat()}
- **Action Taken**: {action}
- **Scale Delta**: {delta}
- **Strategic Justification**: {reason}
- **Execution Mode**: Autonomous / Heuristic
"""
        self.update_block("RESOURCE_MANEUVERS.md", "Autonomous Scaling Logs", entry)

    def log_semantic_correlation(self, project_a: str, project_b: str, similarity_score: float, reasoning: str):
        """Log a detected semantic correlation between two projects."""
        entry = f"""
### Correlation: {project_a} <--> {project_b} | {datetime.datetime.now().isoformat()}
- **Similarity Score**: {similarity_score * 100:.1f}%
- **Functional Overlap**: {reasoning}
- **Action Recommended**: Shared module extraction / Dependency mapping.
"""
        self.update_block("SEMANTIC_MAP.md", "Functional Correlations", entry)

    def log_architectural_quirk(self, software_name: str, quirk_details: Dict[str, Any]):
        """Log a detected architectural quirk or emergent behavior."""
        quirk_type = quirk_details.get("type", "Nuance")
        behavior = quirk_details.get("behavior", "Emergent")
        impact = quirk_details.get("impact", "Moderate")
        context = quirk_details.get("context", "General System Design")
        
        entry = f"""
### Quirk: {quirk_type} in {software_name} | {datetime.datetime.now().isoformat()}
- **Emergent Behavior**: {behavior}
- **System Impact**: {impact}
- **Applicability Context**: {context}
- **Nature**: Deterministic / Partial Propagation
"""
        self.update_block("QUIRK_REGISTRY.md", "Detected Nuances & Transforms", entry)

    def log_mathematical_mastery(self, software_name: str, math_details: Dict[str, Any]):
        """Log a mathematical capability or structure applied in software."""
        concept = math_details.get("concept", "Generic Logic")
        application = math_details.get("application", "Algorithm refinement")
        maturity = math_details.get("maturity", "Developing")
        
        entry = f"""
### Mathematical Concept: {concept} ({software_name}) | {datetime.datetime.now().isoformat()}
- **Application Logic**: {application}
- **Fortress Mastery Level**: {maturity}
- **Artifact Type**: Mathematical structure transform
"""
        self.update_block("MATHEMATICAL_LIBRARY.md", "Mathematical Capability Registry", entry)

    def log_computational_nature(self, software_name: str, audit_details: Dict[str, Any]):
        """Log a detected computational nature audit."""
        complexity = audit_details.get("complexity", "O(unknown)")
        nature = audit_details.get("nature", "Iterative")
        intensity = audit_details.get("intensity", "Balanced")
        reasoning = audit_details.get("reasoning", "Heuristic analysis")
        
        entry = f"""
### Audit: {software_name} | {datetime.datetime.now().isoformat()}
- **Theoretical Complexity**: {complexity}
- **Algorithmic Nature**: {nature}
- **Resource Intensity**: {intensity}
- **Fortress Reasoning**: {reasoning}
"""
        self.update_block("COMPUTATIONAL_NATURE.md", "Algorithmic Intensity Audits", entry)

    def log_task_lifecycle(self, goal: str, tasks: List[str]):
        """Log exhaustive task modeling and lifecycle decomposition."""
        entry = f"### Lifecycle: {goal} | {datetime.datetime.now().isoformat()}\n"
        for i, task in enumerate(tasks):
            entry += f"{i+1}. [ ] {task}\n"
        self.update_block("TASK_GRAPH.md", "Task Dependencies & Lifecycles", entry)

    def log_objective_alignment(self, agenda: str, alignment_data: Dict[str, Any]):
        """Log alignment between tasks and high-level agendas."""
        deliverable = alignment_data.get("deliverable", "None")
        status = alignment_data.get("status", "Pending")
        mapping = alignment_data.get("mapping", "Direct")
        
        entry = f"""
### Agenda Alignment: {agenda} | {datetime.datetime.now().isoformat()}
- **Deliverable Target**: {deliverable}
- **Alignment Strength**: {status}
- **Strategic Mapping**: {mapping}
"""
        self.update_block("OBJECTIVE_ALIGNMENT.md", "Strategic Agenda Sync", entry)

    def log_diligence_report(self, intent: str, status: str, score: float, violations: List[str]):
        """Log a due diligence architectural feasibility audit."""
        violations_str = "\n".join([f"- ⚠️ {v}" for v in violations])
        entry = f"""
### Due Diligence Audit: {intent[:50]}... | {datetime.datetime.now().isoformat()}
- **Intent**: {intent}
- **Status**: {status}
- **Feasibility Score**: {score}/100
- **Violations Detected**:
{violations_str}
"""
        self.update_block("OBJECTIVE_ALIGNMENT.md", "Strategic Agenda Sync", entry)

    def log_scope_definition(self, entity_name: str, scope_specs: Dict[str, Any]):
        """Log custom scope boundaries for an entity."""
        boundaries = scope_specs.get("boundaries", "No restrictive boundaries")
        restricted = scope_specs.get("restricted", "All areas open")
        policy = scope_specs.get("policy", "Standard isolation")
        
        entry = f"""
### Scope: {entity_name} | {datetime.datetime.now().isoformat()}
- **Boundaries**: {boundaries}
- **Restricted Domains**: {restricted}
- **Inter-Dependency Policy**: {policy}
"""
        self.update_block("SCOPE_REGISTRY.md", "Custom Scope boundaries", entry)
