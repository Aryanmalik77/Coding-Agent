import asyncio
import os
import shutil
from pathlib import Path
from coding_agent.fortress.engine import FortressEngine
from coding_agent.swarm.lmdb_store import LMDBStore
from coding_agent.subagents.todo_agent import ToDoSubagent
from coding_agent.subagents.task_agent import TaskSubagent
from coding_agent.subagents.diligence_agent import DueDiligenceAgent
from loguru import logger

async def verify_orchestration():
    workspace = Path("c:/Users/HP/coding agent/subagent_test_ws")
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    
    db_path = workspace / "test_db"
    lmdb = LMDBStore(db_path)
    engine = FortressEngine(lmdb, workspace=workspace)
    
    logger.info("--- Testing ToDoSubagent synchronization ---")
    todo = ToDoSubagent(workspace)
    todo.add_objective("Implement Neural Core", priority="High")
    todo.sync_with_global_strategy(engine)
    
    logger.info("--- Testing TaskSubagent decomposition ---")
    task_sub = TaskSubagent(workspace)
    task_sub.decompose_objective("Neural Core", [
        {"id": "nc_1", "description": "Initialize Weights", "dependency": "None"},
        {"id": "nc_2", "description": "Propagate Tensor", "dependency": "nc_1"}
    ])
    task_sub.record_architectural_delta("nc_1", "Weights initialized with Gaussian noise", engine)
    
    logger.info("--- Testing DiligenceAgent audit ---")
    diligence = DueDiligenceAgent(workspace, workspace=workspace)
    intent = "Train a 175B parameter model on a single 8GB GPU"
    constraints = {"hardware": {"max_ram_gb": 8}, "mathematical_limit": "O(2^n)"}
    report = await diligence.audit_intent(intent, constraints, engine)
    
    logger.info(f"Diligence Status: {report['status']}")
    logger.info(f"Feasibility Score: {report['feasibility_score']}")
    
    # Check Fortress Memory
    memory_dir = workspace / "fortress" / "memory"
    if memory_dir.exists():
        align_file = memory_dir / "OBJECTIVE_ALIGNMENT.md"
        if align_file.exists():
            logger.info("SUCCESS: OBJECTIVE_ALIGNMENT.md created.")
            # logger.info(f"Alignment Content:\n{align_file.read_text()}")
        else:
            logger.error("FAILURE: OBJECTIVE_ALIGNMENT.md missing.")
            
    logger.info("Subagent Orchestration Verification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_orchestration())
