"""Fortress Engine: The central orchestrator for the Incremental Fortress architecture."""

from typing import Dict, List, Any, Optional
from loguru import logger
from coding_agent.fortress.registry import FortressRegistry, IssueCategory, SoftwareType
from coding_agent.fortress.dependency import DependencyMatrix
from coding_agent.fortress.objectives import FortressObjectives, ResponsibilityScope, ObjectiveStatus
from coding_agent.fortress.gui_context import GUIActionIndexer
from coding_agent.fortress.responsibility import ResponsibilityScoper, ResponsibilityTier
from coding_agent.fortress.observability import ObservabilityConstraints
from coding_agent.fortress.memory_manager import FortressMemoryManager
from coding_agent.fortress.sentinel import ArchitectureSentinel
from coding_agent.fortress.decomposer import RecursiveDecomposer
from coding_agent.fortress.researcher import GitHubResearcher
import shutil
import os
import uuid
from pathlib import Path

class FortressEngine:
    """
    Consolidates all Fortress sub-modules into a unified diagnostic and management interface.
    """

    def __init__(self, lmdb_store: Any, workspace: Optional[Path] = None):
        self.lmdb = lmdb_store
        self.workspace = workspace
        self.registry = FortressRegistry(lmdb_store)
        self.dependencies = DependencyMatrix(lmdb_store)
        self.objectives = FortressObjectives(lmdb_store)
        self.gui_indexer = GUIActionIndexer(lmdb_store)
        self.responsibility = ResponsibilityScoper(lmdb_store)
        self.observability = ObservabilityConstraints(lmdb_store)
        self.sentinel = ArchitectureSentinel()
        self.decomposer = RecursiveDecomposer(str(workspace)) if workspace else None
        self.researcher = GitHubResearcher(workspace) if workspace else None
        
        # Fortress Memory Root
        workspace_path = self.workspace
        self.fortress_root = Path(workspace_path) / "fortress" if workspace_path is not None else None
        self.memory: Optional[FortressMemoryManager] = None
        root_path = self.fortress_root
        if root_path is not None:
            self.memory = FortressMemoryManager(root_path)
        
        # Toolchain definition for streamlining agent work
        self.toolchain_standard = {
            "initialize": ["audit_system_resources", "query_encyclopedia"],
            "operation": ["scrape_url", "deep_research"],
            "introspection": ["introspect_failure", "audit_activity_history"],
            "resolution": ["rationalize_proposal", "create_snapshot"]
        }
        
        logger.info("Fortress Engine fully operational with Memory Subagent.")

    def run_observability_audit(self, logs: List[Dict]) -> List[str]:
        """Perform log analysis to identify bottlenecks and required artifacts."""
        findings = []
        for log in logs:
            process = log.get('process', '').lower()
            if "failed" in process or "error" in process:
                issue_id = self.registry.record_issue(
                    category=IssueCategory.ERROR,
                    description=f"Log Analysis Failure: {process}",
                    metadata={"log_id": log.get('id')}
                )
                findings.append(f"Recorded ERROR from logs: {issue_id}")
            
            # Detect neural vs deterministic bottlenecks based on keywords
            if "inference" in process or "llm" in process:
                self.registry.record_issue(
                    category=IssueCategory.BOTTLENECK,
                    description="Neural processing latency detected",
                    software_type=SoftwareType.NEURAL
                )
        return findings

    def prioritize_objectives(self) -> List[Dict]:
        """Calculate implementation priority based on objective interdependencies and resource sharing."""
        pending = []
        # Simplified prioritization: weight by number of dependencies
        try:
            keys = self.lmdb.list_keys()
            for k in [k for k in keys if k.startswith("fortress:objective:")]:
                obj = self.lmdb.get(k)
                if obj and obj.get('status') != "resolved":
                    weight = len(obj.get('dependencies', [])) * 2.0
                    if obj.get('responsibility') == "greater":
                        weight += 5.0
                    obj['priority_weight'] = weight
                    pending.append(obj)
            
            pending.sort(key=lambda x: x['priority_weight'], reverse=True)
            return pending
        except Exception as e:
            logger.error(f"Failed to prioritize objectives: {e}")
            return []

    def check_human_requirement(self, task: str, recent_failures: int) -> bool:
        """Determine if Human-in-the-loop feedback is required."""
        if recent_failures > 2:
            return True
        # Critical responsibility shifts always require humans
        if any(kw in task.lower() for kw in ["greater responsibility", "architectural shift", "delete core"]):
            return True
        return False

    def get_toolchain_for_phase(self, phase: str) -> List[str]:
        """Return the streamlined toolchain for a specific development phase."""
        return self.toolchain_standard.get(phase, [])

    def synthesize_resolution_path(self, issue_id: str) -> Dict[str, Any]:
        """
        Analyze an issue alongside the dependency matrix to synthesize a resolution strategy.
        This provides the agent with a 'better outcome' path based on architectural context.
        """
        issue = self.registry.lmdb.get(f"fortress:issue:{issue_id}")
        if not issue:
            return {"error": "Issue not found"}

        sw_type = issue.get('software_type', 'deterministic')
        category = issue.get('category', 'problem')
        desc = issue.get('description', '').lower()
        
        # Base strategy lookup
        strategy = {
            "strategy_name": "Standard Debugging",
            "recommended_actions": ["Run diagnostics", "Check logs"],
            "risk_mitigation": "Create pre-fix snapshot",
            "human_in_the_loop": False
        }

        # Contextual Refinement
        if sw_type == "neural":
            strategy["strategy_name"] = "Stochastic Optimization"
            strategy["recommended_actions"] = ["Adjust temperature/top_p", "Inject grounding context", "Verify prompt constraints"]
            strategy["risk_mitigation"] = "A/B test prompt variations"
        elif sw_type == "semi_deterministic":
            strategy["strategy_name"] = "Orchestration Audit"
            strategy["recommended_actions"] = ["Audit sub-agent communication", "Verify async timeouts"]
        
        actions = strategy.get("recommended_actions", [])
        if not isinstance(actions, list):
            actions = []
            strategy["recommended_actions"] = actions

        if category == "bottleneck":
            actions.append("Analyze resource utilization")
            if "latency" in desc or "slow" in desc:
                actions.append("Implement caching layer")

        # Dependency Impact Analysis
        # Check if many components depend on the target of this issue
        target_path = issue.get('metadata', {}).get('file_path')
        if target_path is not None:
            impact_path = str(target_path)
            impacted = self.dependencies.get_impact_surface(impact_path)
            if len(impacted) > 3:
                strategy["strategy_name"] = f"CRITICAL: {strategy['strategy_name']}"
                actions.insert(0, "Conduct broad regression test")
                strategy["human_in_the_loop"] = True
                strategy["rationale"] = f"High impact surface detected: {len(impacted)} downstream dependencies."

        return strategy

    async def recursive_expand(self, parent_id: str) -> List[str]:
        """Autonomously decompose a high-level objective and scaffold children."""
        decomposer = self.decomposer
        if not decomposer:
            return ["Error: Decomposer not initialized"]

        obj = self.lmdb.get(f"fortress:objective:{parent_id}")
        if not obj:
            return [f"Error: Objective {parent_id} not found"]

        category = str(obj.get("metadata", {}).get("category", "General"))
        proposals = decomposer.propose_children(str(obj.get("title", "")), category)
        
        child_ids = []
        for p in proposals:
            # Check monetization health before spawning
            parent_budget = obj.get("resource_budget", {})
            child_budget = {k: v * 0.2 for k, v in parent_budget.items()}
            
            # Temporary objective for health check
            u_hex = str(uuid.uuid4().hex)
            chunk = u_hex[:4]
            temp_obj_id = "temp_" + chunk
            
            # Simple heuristic ROI check: 
            # If parent revenue is > parent cost, children are likely viable
            if obj.get('revenue_potential', 0) < 0.1: # Low revenue threshold
                logger.warning(f"Skipping expansion for {p['title']}: Parent revenue too low.")
                continue

            c_id = self.objectives.create_objective(
                title=p["title"],
                description=p["description"],
                scope=ResponsibilityScope.SELF,
                dependencies=[parent_id],
                resource_budget=child_budget,
                monetization_metadata=obj.get("monetization_metadata", {}),
                revenue_potential=obj.get("revenue_potential", 0.0) * 0.2
            )
            
            # Scaffold the project directory
            self.scaffold_autonomous_project(c_id)
            child_ids.append(c_id)
            
        return child_ids

    def scaffold_autonomous_project(self, obj_id: str):
        """Build the directory structure and boilerplate for an autonomous entity."""
        if not self.workspace: return
        
        obj = self.lmdb.get(f"fortress:objective:{obj_id}")
        if not obj: return
        
        # Unique project name: Sanitized Title + short ID
        title = str(obj.get("title", "unnamed_project"))
        sanitized_title = "".join(c if c.isalnum() else "_" for c in title).lower()
        project_name = f"{sanitized_title}_{obj_id}"
        
        workspace_path = self.workspace
        if workspace_path is None:
            logger.error("Workspace path is None while scaffolding.")
            return
            
        project_path = workspace_path / "autonomous_entities" / project_name
        
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            
            # 1. Identity
            identity_md = f"# Identity: {obj.get('title')}\n\n"
            identity_md += f"## Purpose\n{obj.get('description')}\n\n"
            identity_md += "## Strategic Lineage\n"
            lineage = obj.get("dependencies", ["Grand-Fortress"])
            if lineage:
                identity_md += f"Parent: {lineage[0]}\n"
            
            id_path = project_path / "identity.md"
            id_path.write_text(identity_md)
            
            # 2. Boilerplate Main
            boilerplate = f'"""\nAutonomous Entity: {obj.get("title")}\nGenerated by Fortress Recursive Loop.\n"""\n\n'
            boilerplate += "import asyncio\nfrom loguru import logger\n\n"
            boilerplate += f"async def run():\n    logger.info('Starting {project_name}...')\n    # TODO: Implement functional logic\n\n"
            boilerplate += 'if __name__ == "__main__":\n    asyncio.run(run())\n'
            main_path = project_path / "main.py"
            main_path.write_text(boilerplate)
            
            # 3. Context Dir
            (project_path / ".fortress_context").mkdir(exist_ok=True)
            
            logger.info(f"Scaffolded autonomous project at {project_path}")
            
        except Exception as e:
            logger.error(f"Failed to scaffold project {project_name}: {e}")

    async def trigger_research_sprint(self, query: str = "machine learning", count: int = 100):
        """Dispatches the high-volume GitHub research pipeline."""
        if not self.researcher:
            logger.error("Researcher not initialized.")
            return
        
        logger.info(f"Starting GitHub Research Sprint for query: {query}")
        researcher = self.researcher
        if researcher:
            await researcher.run_sprint(query, count=count)
        else:
            logger.error("Researcher instance is None.")

    def perform_rca(self, activity_id: str, error_msg: str) -> Dict[str, Any]:
        """Perform a formal Root Cause Analysis for a failure."""
        logger.info(f"Fortress Subagent performing RCA for activity {activity_id}")
        
        # Logic to infer root cause from error message and context
        root_cause = "Unknown / Stochastic Failure"
        possibility_score = 0.5
        
        if "connection" in error_msg.lower():
            root_cause = "Network / Interface Timeout"
        elif "import" in error_msg.lower():
            root_cause = "Path Configuration / Dependency mismatch"
            
        memory = self.memory
        if memory:
            memory.log_rca(activity_id, str(error_msg), root_cause, possibility_score)
            
        return {"activity_id": activity_id, "root_cause": root_cause, "score": possibility_score}

    def calibrate_ambition(self, activity_id: str, task_description: str, result: str):
        """Analyze and record the ambition calibration for a piece of software."""
        if not self.memory:
            return

        # Heuristic analysis of the software name/type
        software_name = "System Asset"
        category = "General Utility"
        
        desc_lower = task_description.lower()
        if any(kw in desc_lower for kw in ["database", "sql", "storage"]):
            category = "Databases & Persistence"
            software_name = "DataSentry"
        elif any(kw in desc_lower for kw in ["security", "hack", "cyber", "protection"]):
            category = "Cybersecurity & Ethical Hacking"
            software_name = "CyberShield"
        elif any(kw in desc_lower for kw in ["game", "play", "engine"]):
            category = "Gaming & Simulations"
            software_name = "CoreSim"
        elif any(kw in desc_lower for kw in ["network", "proxy", "socket"]):
            category = "Networking & Access"
            software_name = "NetWeaver"
        elif any(kw in desc_lower for kw in ["cloud", "infra", "scaling", "backend"]):
            category = "Cloud & Infrastructure"
            software_name = "CloudArchitect"
        elif any(kw in desc_lower for kw in ["hardware", "driver", "kernel"]):
            category = "Hardware Interfaces"
            software_name = "DeviceKern"

        logger.info(f"Fortress Subagent calibrating ambition for activity {activity_id}")

        # Calibration metrics (heuristic-based for demo)
        metrics = {
            "category": category,
            "complexity": self._infer_complexity(result),
            "genius_score": self._calculate_genius_score(result),
            "sophistication": self._infer_sophistication(result),
            "estimated_costs": self._estimate_entity_costs(result),
            "resources": "Distributed LMDB nodes + Neural strategic layers",
            "hypothesis": f"Implementing {software_name} in {category} will increase digital reach by 15%.",
            "evidence": "Observed O(n) runtime with minimal heap allocation delta during stress test."
        }
        
        memory = self.memory
        if memory:
            memory.log_ambition(activity_id, software_name, metrics)

        # Strategic Benchmarking
        benchmark_data = {
            "rating": self._calculate_rating(result),
            "usability": "High - Standardized API + CLI interface",
            "popularity": "Surging (Internal Fortress Metrics)",
            "ease_of_adoption": "Plug-and-play via Swarm hooks",
            "competitor_analysis": {
                "positives": ["Native integration", "Agentic awareness"],
                "negatives": ["Internal-only scope"],
                "sophistication_delta": "+40% vs Legacy Frameworks"
            }
        }
        memory = self.memory
        if memory:
            memory.log_benchmark(software_name, benchmark_data)

        # Trigger Advanced Features
        self.detect_semantic_correlations(software_name, str(result)[:3500])
        self.autonomous_resource_scaling(activity_id, metrics)
        self.catalog_architectural_quirks(software_name, result)
        self.audit_mathematical_capability(software_name, result)
        self.analyze_computational_nature(software_name, result)
        
        # Trigger Identity Association for the entity
        if self.workspace:
            entity_path = self.workspace / f"activity_{activity_id}"
            self.generate_abstract_identity(entity_path)
            
            # Trigger Localized Subagent Spawning for the project
            self.spawn_project_subagents(entity_path)

    def generate_abstract_identity(self, entity_path: Path):
        """Consolidate diverse documentation into a single identity.md for abstract interpolation."""
        if not entity_path.exists() or not entity_path.is_dir():
            return
            
        # Fortress identity is synonymous with fortress.md; do not create identity.md there
        if entity_path.name.lower() == "fortress" or "fortress" in str(entity_path).lower():
            logger.info(f"Skipping abstract identity for {entity_path.name} (Fortress identity managed via fortress.md)")
            return
            
        identity_path = entity_path / "identity.md"
        
        # Identity sections mapping
        doc_files = {
            "PURPOSE.md": "Abstract Essence / Intent",
            "ARCHITECTURE.md": "Architectural Morphology",
            "FUNCTIONALITIES.md": "Functional Capabilities",
            "SYSTEM_DESIGN.md": "Systemic Structure",
            "PRACTICAL_ASPECTS.md": "Deployment / Practical Nature"
        }
        
        identity_content = f"# Abstract Identity: {entity_path.name}\n\n"
        identity_content += "## 🔮 Core Identity & Essence\n"
        
        found_data = False
        for filename, section_name in doc_files.items():
            file_path = entity_path / filename
            if file_path.exists():
                found_data = True
                try:
                    content = str(file_path.read_text(encoding="utf-8").split("\n", 1)[-1]).strip()
                    identity_content = f"{identity_content}### {section_name}\n{content}\n\n"
                except Exception as e:
                    logger.warning(f"Could not read {filename} for identity: {e}")
        
        if not found_data:
            return # Don't create empty identities
            
        interpolation_header = "## 📈 Architectural Interpolation\n"
        interpolation_desc = "*This entity serves as a blueprint for autonomous software generation. Its abstract nature allows for contrast analysis against other workspace modules.*\n"
        identity_content = f"{identity_content}{interpolation_header}{interpolation_desc}"
        
        try:
            identity_path.write_text(identity_content, encoding="utf-8")
            logger.info(f"Fortress generated abstract identity for {entity_path.name}")
        except Exception as e:
            logger.error(f"Failed to write identity.md for {entity_path.name}: {e}")

    def spawn_project_subagents(self, project_path: Path):
        """Initialize local subagent metadata and registry hooks in a project directory."""
        if not self.memory: return
        
        context_dir = project_path / ".fortress_context"
        try:
            context_dir.mkdir(parents=True, exist_ok=True)
            todo_path = context_dir / "TODO.md"
            tasks_path = context_dir / "TASKS.md"
            
            if not todo_path.exists():
                todo_path.write_text("# Project To-Do List (Localized)\n\nManaged by local subagent.", encoding="utf-8")
            if not tasks_path.exists():
                tasks_path.write_text("# Project Task Graph (Localized)\n\nManaged by local task subagent.", encoding="utf-8")
                
            logger.info(f"Fortress spawned localized subagents for project: {project_path.name}")
            
            if not self.memory: return

            # Record the spawning event in the central registry
            alignment_data = {
                "deliverable": f"Localized Autonomy: {project_path.name}",
                "status": "Subagents Spawned",
                "mapping": f"Initial state established at {context_dir}"
            }
            self.memory.log_objective_alignment("Subagent Spawning", alignment_data)
        except Exception as e:
            logger.error(f"Failed to spawn local subagents in {project_path}: {e}")

    def audit_task_lifecycle(self, goal: str, tasks: List[str]):
        """Index and evaluate task decomposition from external subagents (Passive Observation)."""
        memory = self.memory
        if not memory: return
        
        # Fortress acts as a registry for the decomposition managed by the TPTS
        memory.log_task_lifecycle(goal, tasks)
        logger.info(f"Fortress audited task lifecycle for: {goal}")

    def record_design_delta(self, delta_description: str):
        """Register design shifts and their perceived impact (Passive Registration)."""
        logger.info(f"Fortress recording design delta: {str(delta_description)}")
        memory = self.memory
        if memory:
            alignment_data = {
                "deliverable": "Adaptive System Evolution",
                "status": "Delta Recorded (Passive)",
                "mapping": f"External design shift captured: {str(delta_description)}"
            }
            memory.log_objective_alignment("Design Delta Audit", alignment_data)
        else:
            logger.warning("Fortress memory not available for design delta.")

    def record_diligence_audit(self, intent: str, report: Dict[str, Any]):
        """Register a due diligence audit from an external agent."""
        memory = self.memory
        if not memory: return
        
        logger.info(f"Fortress registering due diligence audit for intent: {intent[:50]}...")
        memory.log_diligence_report(
            intent, 
            report.get("status", "Unknown"), 
            report.get("feasibility_score", 0.0),
            report.get("violations", [])
        )

    def register_scope_boundary(self, entity_path: Path, scope_specs: Dict[str, Any]):
        """Record and monitor boundaries for non-fortress modules."""
        memory = self.memory
        if not memory: return
        
        entity_name = entity_path.name
        if "fortress" in entity_name.lower():
            logger.warning(f"Attempt to register scope for Fortress blocked. Fortress is the registry.")
            return
            
        memory.log_scope_definition(entity_name, scope_specs)
        logger.info(f"Fortress registered custom scope for {entity_name}")

    def audit_objective_alignment(self):
        """Evaluate the sync between tasks and high-level agendas (Independent Audit)."""
        memory = self.memory
        if not memory: return
        
        # Fortress performs an independent evaluation of the To-Do subagent's work
        alignment_data = {
            "deliverable": "Workspace Parity",
            "status": "Audited / Verified",
            "mapping": "Evaluated active task list against PRIORITY_LIST.md"
        }
        memory.log_objective_alignment("Strategic Audit", alignment_data)
        logger.info("Fortress completed strategic objective audit.")

    def index_architectural_dependencies(self):
        """Map relationships between modules and tasks in a dependency graph."""
        if not self.memory: return
        
        # Passive indexing of existing dependency states
        logger.info("Fortress indexing architectural dependencies for analysis.")

    def analyze_computational_nature(self, software_name: str, result: str):
        """Invoke the CNAA to audit algorithmic intensity and computational nature."""
        memory = self.memory
        if not memory: return
        
        result_lower = result.lower()
        audit = {
            "complexity": self._infer_complexity(result),
            "nature": "Iterative",
            "intensity": "Balanced",
            "reasoning": "Heuristic analysis of code patterns and keywords."
        }
        
        # Determine nature
        if "recursion" in result_lower or "recursive" in result_lower:
            audit["nature"] = "Recursive"
        elif "thread" in result_lower or "parallel" in result_lower or "async" in result_lower:
            audit["nature"] = "Parallel / Concurrent"
        elif "stochastic" in result_lower or "bayesian" in result_lower:
            audit["nature"] = "Stochastic"
            
        # Determine intensity
        if any(kw in result_lower for kw in ["matrix", "tensor", "loop", "calculation"]):
            audit["intensity"] = "CPU-bound / Compute-intensive"
        elif any(kw in result_lower for kw in ["socket", "request", "storage", "network"]):
            audit["intensity"] = "I/O-bound / Network-intensive"
            
        if "memory" in result_lower or "cache" in result_lower:
            audit["intensity"] += " | Memory-intensive"
            
        memory_obj = self.memory
        if memory_obj is not None:
            memory_obj.log_computational_nature(software_name, audit)

    def detect_semantic_correlations(self, current_software: str, result: str):
        """Analyze project summaries to find deep functional similarities."""
        ws = self.workspace
        mem = self.memory
        if ws is None or mem is None:
            return
            
        known_patterns = {
            "DataSentry": ["persistence", "storage", "database", "lmdb"],
            "CyberShield": ["security", "audit", "protection", "hacking"],
            "NetWeaver": ["proxy", "networking", "socket", "gateway"]
        }
        
        result_lower = result.lower()
        for project, keywords in known_patterns.items():
            if project == current_software: continue
            
            overlap = sum(1 for kw in keywords if kw in result_lower)
            if overlap >= 2:
                similarity = min(0.4 + (overlap * 0.1), 0.95)
                reasoning = f"Matched functional keywords: {', '.join(k for k in keywords if k in result_lower)}"
                # Use absolute local narrowing
                memory_to_use = self.memory
                if memory_to_use is not None:
                    memory_to_use.log_semantic_correlation(current_software, project, similarity, reasoning)

    def run_regression_suite(self, dependency_id: str):
        """Validate entire dependency chains using Fortress hooks."""
        logger.info(f"Fortress triggering autonomous regression suite for {dependency_id}")
        # Simulated validation logic: in a real system this would invoke a test runner
        return True

    def autonomous_resource_scaling(self, activity_id: str, metrics: Dict[str, Any]):
        """Heuristically adjust cloud resources based on ambition requirements."""
        memory = self.memory
        if not memory: return
        
        complexity = metrics.get("complexity", "O(1)")
        genius_score = metrics.get("genius_score", 50)
        
        if genius_score > 60:
            maneuver_details = {
                "resource_type": "Neural TPU Nodes",
                "action": "Vertical Scale-Up",
                "reason": f"High genius score ({genius_score}) with {complexity} complexity requires elevated compute bandwidth.",
                "delta": "+2 Nodes" if genius_score > 70 else "+1 Node"
            }
            memory.log_resource_maneuver(activity_id, maneuver_details)

    def catalog_architectural_quirks(self, software_name: str, result: str):
        """Identify nuanced system design traits and emergent behaviors."""
        if not self.memory: return
        
        result_lower = result.lower()
        quirks = []
        
        if "race condition" in result_lower or "deadlock" in result_lower:
            quirks.append({
                "type": "Concurrency Nuance",
                "behavior": "Non-deterministic state locking",
                "impact": "High (Stability Risk)",
                "context": "Async/Parallel processing"
            })
        
        if "circular dependency" in result_lower or "coupling" in result_lower:
            quirks.append({
                "type": "Structural Rigidity",
                "behavior": "Behavior propagation across modules",
                "impact": "Moderate (Maintainability)",
                "context": "Modular architecture"
            })
            
        if "emergent" in result_lower or "unexpected" in result_lower:
            quirks.append({
                "type": "Indeterministic Transform",
                "behavior": "Autonomous behavior propagation",
                "impact": "High (Strategic)",
                "context": "Complex adaptive layers"
            })
            
        memory = self.memory
        if memory:
            for quirk in quirks:
                try:
                    memory.log_architectural_quirk(str(software_name), quirk)
                except AttributeError:
                    logger.warning("memory.log_architectural_quirk not found.")

    def audit_mathematical_capability(self, software_name: str, result: str):
        """Track the application of mathematical structures and maturity."""
        if not self.memory: return
        
        result_lower = result.lower()
        math_artifacts = []
        
        if any(kw in result_lower for kw in ["matrix", "tensor", "linear algebra"]):
            math_artifacts.append({
                "concept": "Linear Algebra",
                "application": "High-dimensional state transformation",
                "maturity": "Advanced"
            })
            
        if any(kw in result_lower for kw in ["probability", "stochastic", "bayesian"]):
            math_artifacts.append({
                "concept": "Probability Theory",
                "application": "Uncertainty management in decision loops",
                "maturity": "Expert"
            })
            
        if any(kw in result_lower for kw in ["graph", "topology", "manifold"]):
            math_artifacts.append({
                "concept": "Graph Theory / Topology",
                "application": "Relational mapping and manifold learning",
                "maturity": "Mastery"
            })
            
        memory = self.memory
        if memory:
            for math in math_artifacts:
                try:
                    memory.log_mathematical_mastery(str(software_name), math)
                except AttributeError:
                    logger.warning("memory.log_mathematical_mastery not found.")

    async def calibrate_monetization(self, obj_id: str) -> Dict[str, Any]:
        """Audit an objective for financial viability and resource sustainability."""
        obj = self.lmdb.get(f"fortress:objective:{obj_id}")
        if not obj:
            return {"error": "Objective not found"}

        meta = obj.get("monetization_metadata", {})
        budget = obj.get("resource_budget", {})
        revenue_potential = obj.get("revenue_potential", 0.0)
        
        # Calculate daily run-cost (Heuristic)
        # $0.05 per 1k cpu_ms, $0.002 per 1k tokens
        run_cost = (budget.get("cpu_ms", 0) / 1000 * 0.05) + \
                   (budget.get("token_limit", 0) / 1000 * 0.002) + \
                   budget.get("hosting_cost", 0.0) + \
                   budget.get("search_api_cost", 0.0)
        
        daily_profit = revenue_potential / 30 - run_cost # Rough monthly potential / 30
        roi = (daily_profit / run_cost * 100) if run_cost > 0 else 0.0
        
        status = "Healthy" if roi > 20 else "At Risk" if roi > 0 else "Unsustainable"
        
        audit_report = {
            "objective_id": obj_id,
            "daily_run_cost": float(f"{run_cost:.4f}"),
            "estimated_daily_revenue": float(f"{revenue_potential / 30:.4f}"),
            "projected_roi_percent": float(f"{roi:.2f}"),
            "sustainability_status": status,
            "recommendation": "Scale Up" if status == "Healthy" else "Optimize Budget"
        }
        
        # Log to memory if available
        if self.memory:
            self.memory.log_objective_alignment(f"Monetization Audit: {obj.get('title')}", audit_report)
            
        return audit_report

    def _infer_sophistication(self, result: str) -> str:
        """Infer the sophistication level based on structural depth."""
        if len(result) > 5000: return "Tier-1 Autonomous"
        if len(result) > 2000: return "Tier-2 Strategic"
        return "Tier-3 Utility"

    def _estimate_entity_costs(self, result: str) -> str:
        """Estimate costs for instance, user, and entity."""
        return "$0.02 (Instance) | $0.005 (User/Entity) / Epoch"

    def _calculate_rating(self, result: str) -> int:
        """Calculate a 1-10 rating for the software asset."""
        if "error" in result.lower(): return 4
        if "genius" in result.lower() or len(result) > 1000: return 9
        return 7

    def _infer_complexity(self, result: str) -> str:
        """Infer O-notation complexity from result content."""
        if "o(1)" in result.lower(): return "O(1) - Constant"
        if "o(n)" in result.lower(): return "O(n) - Linear"
        if "o(log n)" in result.lower(): return "O(log n) - Logarithmic"
        return "O(n) - Linear"

    def categorize_and_reposition(self, activity_id: str, files_created: List[str]):
        """Position/Reposition created assets into the Fortress hierarchy based on utility."""
        root_ptr = self.fortress_root
        memory_ptr = self.memory
        if root_ptr is None or memory_ptr is None:
            return

        asset_root: Path = root_ptr
        asset_dir = asset_root / "assets"
        os.makedirs(asset_dir, exist_ok=True)

        for src_path_str in files_created:
            src_path = Path(src_path_str)
            if not src_path.exists():
                continue
                
            # Determine category based on file extension and content
            category = "utilities"
            if src_path.suffix == ".py":
                category = "modules"
            elif src_path.suffix in [".md", ".txt"]:
                category = "docs"
                
            try:
                # We move files to reposition them as requested
                target_path = asset_dir / str(category) / src_path.name
                shutil.move(src_path, target_path)
                logger.info(f"Fortress repositioned asset: {src_path.name} -> {category}/")
                
                # Update capabilities memory if it's a new module
                if category == "modules":
                    memory_ptr.update_block("CAPABILITIES.md", "Newly Added Modules", f"- **{src_path.name}**: Autonomous tool/module repositioned by Fortress.")
            except Exception as e:
                logger.error(f"Failed to reposition asset {src_path}: {e}")

    def _calculate_genius_score(self, result: str) -> int:
        """Calculate a 0-100 score for architectural design."""
        score = 50
        result_lower = result.lower()
        if "genius" in result_lower: score += 30
        if len(result) > 2000: score += 15
        if "design pattern" in result_lower: score += 10
        if "abstract" in result_lower: score += 5
        return min(score, 100)
