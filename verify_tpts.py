
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from coding_agent.fortress.engine import FortressEngine
from coding_agent.fortress.memory_manager import FortressMemoryManager

def verify_observer_pattern():
    print("--- Starting Fortress Observer Pattern Verification ---")
    
    workspace = Path(r"c:\Users\HP\coding agent\coding agent workspace")
    memory = FortressMemoryManager(workspace / "fortress")
    engine = FortressEngine(None, workspace)
    
    # 1. Audit Task Lifecycle (External TPTS provided tasks)
    goal = "Implement a quantum-resistant encryption utility"
    tasks = [
        "Initialize project environment",
        "Select Lattice-based algorithm",
        "Implement key generation",
        "Implement encryption/decryption modules",
        "Run security audit"
    ]
    print(f"Auditing task lifecycle for external goal: {goal}")
    engine.audit_task_lifecycle(goal, tasks)
    
    # 2. Record Design Delta (External shift observed)
    delta = "Migration from FrodoKEM to Kyber due to better performance metrics"
    print(f"Recording external design delta: {delta}")
    engine.record_design_delta(delta)
    
    # 3. Register Scope Boundary (External boundary defined)
    test_dir = workspace / "activity_act_crypto_vault"
    test_dir.mkdir(exist_ok=True)
    scope_specs = {
        "boundaries": "Cryptography and Secure Storage layers",
        "restricted": "No access to outer workspace networking",
        "policy": "Zero-trust verification for all file I/O"
    }
    print(f"Registering external scope definition for: {test_dir.name}")
    engine.register_scope_boundary(test_dir, scope_specs)
    
    # 4. Independent Objective Audit
    print("Fortress performing independent objective alignment audit...")
    engine.audit_objective_alignment()
    
    print("--- Verification Complete ---")
    print("Check the following logs (Fortress as Observatory):")
    print(f"- {workspace}/fortress/memory/TASK_GRAPH.md")
    print(f"- {workspace}/fortress/memory/OBJECTIVE_ALIGNMENT.md")
    print(f"- {workspace}/fortress/memory/SCOPE_REGISTRY.md")

if __name__ == "__main__":
    verify_observer_pattern()
