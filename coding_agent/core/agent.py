"""Simplified Agent Loop for the standalone Coding Agent."""

import asyncio
from pathlib import Path
from typing import Optional, Any
import re
import os
import datetime

from loguru import logger

from coding_agent.swarm.lmdb_store import LMDBStore
from coding_agent.swarm.graph_store import GraphStore
from coding_agent.evolution.tracker import EvolutionTracker
from coding_agent.evolution.versioning import VersionManager
from coding_agent.identity.encyclopedia import IdentityEncyclopedia
from coding_agent.core.rationalizer import Rationalizer
from coding_agent.core.introspection import IntrospectionEngine
from coding_agent.fortress.engine import FortressEngine
from coding_agent.fortress.device import FortressDevice
from coding_agent.core.logging.activity_tracker import ActivityTracker
from coding_agent.core.logging.logger_hooks import LoggingHooks
from coding_agent.swarm.workspace_architect import WorkspaceArchitect

class CodingAgent:
    """
    Main agent class that encapsulates the coding capabilities.
    """

    def __init__(self, workspace: Any):
        self.workspace = Path(workspace) if isinstance(workspace, str) else workspace
        self.lmdb = LMDBStore(self.workspace)
        self.graph = GraphStore(self.workspace)
        self.evolution = EvolutionTracker(self.workspace, self.lmdb, self.graph)
        self.versioning = VersionManager(self.workspace, self.evolution)
        self.identity = IdentityEncyclopedia(self.workspace, self.lmdb, self.graph)
        self.rationalizer = Rationalizer(self.identity, self.evolution)
        self.introspection = IntrospectionEngine(self.identity, self.evolution)
        self.fortress = FortressEngine(self.lmdb, workspace=self.workspace)
        self.device = FortressDevice(self.fortress)
        self.activity = ActivityTracker(self.lmdb)
        self.hooks = LoggingHooks(self.activity)
        self.architect = WorkspaceArchitect(self.workspace, self.fortress, self.identity)
        
        # State Checkpointing
        from coding_agent.evolution.checkpointing import CheckpointManager
        self.checkpoints = CheckpointManager(self.workspace)
        
        # Swarm Coordination
        from coding_agent.swarm.bridge import SwarmBridge
        self.swarm = SwarmBridge()
        
        # Initialize Tool Registry
        from coding_agent.core.tools import initialize_tools
        self.tools = initialize_tools(self)
        
        logger.info("Coding Agent initialized for workspace: {}", workspace)

    async def run_task(self, task_description: str) -> str:
        """Execute a coding task with full agentic autonomy (Checkpoint -> Rationalize -> Route -> Correct)."""
        logger.info("Starting advanced coding task: {}", task_description)
        desc = task_description.lower()
        snapshot_id = None
        activity_id = "unknown"
        
        # 0. Context Detection: Check for follow-up requests
        vague_refinement = any(p in desc for p in ["only the link", "just the url", "give link", "show url"])
        if vague_refinement:
            history = self.activity.get_activity_history(limit=5)
            last_result = next((log.get('result') for log in history if log.get('result')), None)
            if last_result:
                logger.info("Contextual follow-up detected. Extracting from last result.")
                url_match = re.search(r'https?://[^\s\]]+', last_result)
                if url_match:
                    return f"Activity ID: context_{snapshot_id or 'fup'}\n\nHere is the requested link from our previous research:\n\n{url_match.group(0)}"
                else:
                    logger.warning("No link found in previous context.")
        
        try:
            # 1. State Checkpointing: Snapshot before potentially destructive work
            snapshot_id = self.checkpoints.create_snapshot(label="pre_task")
            
            # 1.1 Architecture Sentinel: Pre-flight Audit
            sentinel_report = self.fortress.sentinel.pre_flight_check(task_description, activity_id)
            if sentinel_report["status"] == "block":
                logger.error(f"Sentinel Blocked Task: {sentinel_report['reason']}")
                return f"Activity ID: {activity_id}\n\n### 🛡️ Sentinel Block\nYour task was blocked by the Architecture Sentinel for the following reason(s):\n- " + "\n- ".join(sentinel_report["reason"])
            elif sentinel_report["status"] == "warn":
                logger.warning(f"Sentinel Warning: {sentinel_report['reason']}")
                # We proceed but we will append the warning to the result later
            
            # 2. Rationalize the Intent and Purpose
            intent = f"Execute Task: {task_description}"
            purpose = "Fulfill remote request while maintaining architectural integrity."
            rationale = self.rationalizer.rationalize_intent(intent, purpose)
            
            # 3. Environmental & Resource Audit
            resource_audit = ""
            auditor = self.tools.get_tool("audit_system_resources")
            if auditor:
                resource_audit = await auditor.execute()
                logger.info("Resource Audit completed: {}", resource_audit.split('\n')[0])

            # 4. Dimensional Task Classification
            keywords = ["insights", "research", "stock", "price", "pricing", "lpg", "gas", "trending", "weather", "news"]
            matches = [kw for kw in keywords if kw in desc]
            dimension = "Real-World Operations" if matches else "Coding & System Design"
            logger.info("Task classified as Dimension: {} (Matches: {})", dimension, matches)

            # 5. Log the activity start
            activity_id = self.hooks.log_tool_execution(
                tool_name="AgentLoop",
                intent=intent,
                purpose=purpose,
                process=f"Autonomous Execution in [{dimension}] context",
                rationale=rationale,
                metadata={
                    "snapshot_id": snapshot_id,
                    "dimension": dimension,
                    "has_resource_audit": bool(resource_audit)
                }
            )
            
            # 6. Task Routing and Delegation
            result = await self._dynamic_route_and_execute(task_description, activity_id, dimension)
            
            # 6.1 Retrieve and format Process Log for traceability
            history = self.activity.get_activity_history(limit=10)
            process_log = "\n### 🛠️ Process Traceability Log\n"
            relevant_logs = []
            for log in history:
                meta = log.get('metadata') or {}
                # Match by activity_id in metadata or the record's own ID
                if meta.get('activity_id') == activity_id or log.get('id') == activity_id:
                    relevant_logs.append(log)
            
            # Sort relevant logs by timestamp (ascending for chronological order)
            relevant_logs.sort(key=lambda x: x.get('timestamp', 0))
            for log in relevant_logs:
                process_log += f"- **{log['task_name']}**: {log['process']}\n"
                process_log += f"  - *Rationale*: {log['rationale']}\n"

            # Prepend resource audit and dimension metadata
            header = f"### [{dimension}] Intelligence Context\n"
            header += f"{resource_audit}\n---\n"
            
            # Only append the fallback if the result is still empty after processing
            if not result or len(result.strip()) < 10:
                result = result or ""
                result += f"\n[!] Notice: Tool returned limited data. Synthesizing from internal knowledge...\n"
                result += f"The system analyzed the request '{task_description}' and determined the optimal path was [{dimension}]. "
                result += "However, external providers returned minimal delta. Checking introspection engine for alternatives..."
                
                # Force introspection if output is poor
                diag = self.introspection.introspect_failure(Exception("Poor Output Quality"), {"task": task_description})
                result += f"\n\n### 🧬 Autonomous Adjustments\n- **Diagnosis**: {diag['root_cause']}\n- **Suggestion**: {diag['alternatives'][0] if diag['alternatives'] else 'Broaden search parameters'}"
            
            # 7.1 Advanced Workspace Documentation & Dependency Mapping
            summary_path = self.architect.generate_project_summary(activity_id, task_description, result)
            self.architect.update_dependency_map()
            
            # 7.2 Fortress Asset Repositioning & Memory Update
            # Detect created files in activity folder and workspace root
            activity_dir = self.workspace / f"activity_{activity_id}"
            created_files = []
            
            # Heuristic: files in activity folder
            if activity_dir.exists():
                created_files.extend([str(activity_dir / f) for f in os.listdir(activity_dir)])
            
            # Heuristic: new files in workspace root (excluding activity folders and state logs)
            for f in os.listdir(self.workspace):
                f_path = self.workspace / f
                if f_path.is_file() and not f.startswith("activity_") and not f.endswith(".db") and not f == "SUMMARY.md":
                    # Check if it was created very recently (within last 2 minutes)
                    if (datetime.datetime.now().timestamp() - f_path.stat().st_ctime) < 120:
                        created_files.append(str(f_path))
            
            if created_files:
                self.fortress.categorize_and_reposition(activity_id, created_files)
                
            # 7.3 Fortress Ambition Calibration
            self.fortress.calibrate_ambition(activity_id, task_description, result)

            result = header + result + process_log

            # 7. Outcome Verification & Identity Ingestion
            self.identity.update_component_status("agent_core", "Operational", {"last_task_id": activity_id})
            
            if "fail" in result.lower() or "error" in result.lower():
                # Trigger Self-Correction Logic
                logger.warning(f"Task result indicates potential failure. Initiating self-correction.")
                correction = self.rationalizer.propose_self_correction(activity_id, result)
                result += f"\n\n### Self-Correction Analysis\n{correction}"

            # 7.1 Persist the result for future context
            self.activity.update_activity_result(activity_id, result)
            
            # 7.2 Sentinel Finalization
            self.fortress.sentinel.finalize_activity(activity_id)

        except Exception as e:
            logger.error(f"Critical task failure: {e}")
            
            # 8. Introspection & Autonomous Healing
            diag = self.introspection.introspect_failure(e, {"task": task_description, "activity_id": activity_id})
            
            introspection_report = f"\n\n### 🧬 Introspection Report\n"
            introspection_report += f"- **Diagnosis**: {diag['root_cause']}\n"
            introspection_report += f"- **Error Type**: {diag['error_type']}\n"
            introspection_report += f"- **Recommended Alternatives**:\n"
            for alt in diag['alternatives']:
                introspection_report += f"  - {alt}\n"
            
            # 9. Autonomous Resolution (Retry if Recommended)
            if diag['retry_recommended'] and diag['alternatives']:
                alternative = diag['alternatives'][0]
                logger.info(f"Autonomously attempting alternative: {alternative}")
                try:
                    # Attempt the first alternative strategy
                    result = await self._dynamic_route_and_execute(alternative, activity_id, dimension)
                    return f"Activity ID: {activity_id}\n\nTask initially failed ({e}), but successfully resolved via alternative path.\n\n### 🏁 Resolution:\n{result}"
                except Exception as retry_err:
                    logger.error(f"Autonomous resolution failed: {retry_err}")
                    introspection_report += f"\n- **Auto-Resolution Status**: Failed ({retry_err})\n"

            # Attempt rollback if checkpoint exists
            if snapshot_id:
                try:
                    self.checkpoints.restore_snapshot(snapshot_id)
                    result = f"CRITICAL FAILURE: {str(e)}. System rolled back to checkpoint {snapshot_id}.{introspection_report}"
                except Exception as rollback_error:
                    result = f"CRITICAL FAILURE: {str(e)}. Rollback also failed: {rollback_error}.{introspection_report}"
            else:
                result = f"CRITICAL FAILURE: {str(e)}. No checkpoint available for rollback.{introspection_report}"
            
        return f"Activity ID: {activity_id}\n\n{result}"

    async def _dynamic_route_and_execute(self, task: str, activity_id: str, dimension: str) -> str:
        """Dynamically route a task to the most appropriate registered tool(s)."""
        desc = task.lower()
        results = []
        
        # 0. Check for Multi-Step Intent (e.g., "then", "and then", "after that")
        # For simplicity, we split by common conjunctions and execute in sequence if present.
        sub_tasks = [t.strip() for t in re.split(r'\s+then\s+|\s+and then\s+|\s+after that\s+', task, flags=re.IGNORECASE)]
        
        if len(sub_tasks) > 1:
            logger.info("Detected multi-step task with {} steps", len(sub_tasks))
            for i, step in enumerate(sub_tasks):
                logger.debug("Executing Step {}: {}", i+1, step)
                step_result = await self._route_single_task(step, activity_id, dimension)
                results.append(f"### Step {i+1}: {step}\n{step_result}")
            return "\n\n".join(results)
        
        return await self._route_single_task(task, activity_id, dimension)

    async def _route_single_task(self, task: str, activity_id: str, dimension: str) -> str:
        """Internal helper to route a single task description to a tool."""
        desc = task.lower()
        
        # Dimensions-based pre-routing logic
        if dimension == "Coding & System Design":
            # For system tasks, ground in identity first
            identity_context = f"Identity grounding for system task: {task}"
            logger.info(identity_context)

        # 1. UI Coordination / Browser Tasks
        if any(kw in desc for kw in ["ui", "button", "click", "browser", "form"]):
            tool = self.tools.get_tool("delegate_ui_task")
            if tool:
                return await tool.execute(task=task, session_key=activity_id)

        # 2. Research & Scraping (Priority for Real-World Operations)
        research_keywords = ["insights", "research", "search", "trending", "stock", "price", "pricing", "lpg", "gas", "market", "bench mark", "scrape", "crawl", "get", "show", "display", "print", "link", "url", "source"]
        if any(kw in desc for kw in research_keywords):
            # Specific URL scraping
            if "http" in task:
                tool = self.tools.get_tool("scrape_url")
                if tool:
                    url_match = re.search(r'https?://\S+', task)
                    if url_match:
                        return await tool.execute(url=url_match.group(0))
            
            # General Deep Research (Search Agent)
            tool = self.tools.get_tool("deep_research")
            if tool:
                logger.info("Spinning Deep Research Tool for: {}", task)
                return await tool.execute(topic=task, activity_id=activity_id)

        # 3. Auditing & History
        audit_keywords = ["audit", "logs", "history", "rational", "introspect", "failure"]
        # Use regex for word boundaries to avoid 'show' matching 'how' or 'error' substrings
        if any(re.search(rf'\b{kw}\b', desc) for kw in audit_keywords) or "error" in desc or "why" in desc:
            if "introspect" in desc or "error" in desc or "failure" in desc:
                tool = self.tools.get_tool("introspect_failure")
                if tool:
                    # Attempt to extract error message if provided
                    err = task.split("error")[-1].strip() if "error" in desc else task
                    return await tool.execute(error_msg=err)
            
            tool = self.tools.get_tool("audit_activity_history")
            if tool:
                return await tool.execute()

        # 4. Identity & Documentation
        if any(kw in desc for kw in ["identity", "encyclopedia", "component", "pattern", "responsibility"]):
            if "query" in desc or "what" in desc:
                tool = self.tools.get_tool("query_encyclopedia")
                if tool: return await tool.execute()
            
            # Autonomous Documentation
            tool = self.tools.get_tool("document_system_component")
            if tool and "document" in desc:
                # Basic extraction of component name
                parts = task.split("document")
                if len(parts) > 1:
                    name = parts[1].strip().split()[0]
                    return await tool.execute(name=name, responsibility="Autonomous discovery")
                
        # 5. Evolution & Versioning
        if any(kw in desc for kw in ["revert", "rollback", "undo", "historical", "version"]):
            tool = self.tools.get_tool("revert_to_version")
            if tool:
                return "Revert tool found. Manual parameter extraction required for safe rollback."

        return ""

    def shutdown(self):
        self.lmdb.close()
        self.graph.close()
        logger.info("Coding Agent shutdown.")
