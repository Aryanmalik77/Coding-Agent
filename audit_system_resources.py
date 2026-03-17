"""Comprehensive System Audit Script: Phase 1 (Resources & Sentinel)"""

import psutil
import os
import platform
import datetime
from pathlib import Path
from coding_agent.fortress.sentinel import ArchitectureSentinel

def run_audit():
    print("=== Comprehensive System Audit: Resource & Sentinel Phase ===")
    print(f"Timestamp: {datetime.datetime.now()}")
    print("-" * 50)
    
    # 1. Environment Stats
    print("\n[Environment]")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    # 2. Resource Audit
    print("\n[Resource Audit]")
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    print(f"RAM Total: {mem.total / (1024**3):.2f} GB")
    print(f"RAM Available: {mem.available / (1024**3):.2f} GB ({mem.percent}%)")
    print(f"Disk Total: {disk.total / (1024**3):.2f} GB")
    print(f"Disk Free: {disk.free / (1024**3):.2f} GB ({disk.percent}%)")
    
    # 3. Sentinel Audit
    print("\n[Architecture Sentinel Audit]")
    sentinel = ArchitectureSentinel()
    res_status = sentinel.check_resources()
    print(f"Sentinel Health Status: {res_status['status']}")
    print(f"Sentinel Message: {res_status['message']}")
    print(f"Sentinel Threshold: {sentinel.memory_threshold} MB")
    
    # 4. Workspace Integrity
    print("\n[Workspace Integrity]")
    workspace_path = Path("c:/Users/HP/coding agent/coding agent workspace")
    if workspace_path.exists():
        print(f"Workspace Found: {workspace_path}")
        dirs = [d.name for d in workspace_path.iterdir() if d.is_dir()]
        print(f"Projects count: {len(dirs)}")
        print(f"Projects: {dirs}")
    else:
        print("ERROR: Workspace not found!")

if __name__ == "__main__":
    run_audit()
