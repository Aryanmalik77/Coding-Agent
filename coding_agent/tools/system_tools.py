"""Tools for auditing system resources and environment specifications."""

import os
import platform
import psutil
from typing import Any, Dict

class ResourceAuditorTool:
    """Audit system resources to ensure task feasibility and multi-environment readiness."""

    def __init__(self):
        self.name = "audit_system_resources"
        self.description = "Check CPU, RAM, OS, and environment specs for task feasibility."

    async def execute(self, **kwargs: Any) -> str:
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        specs = {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu_logical_cores": cpu_count,
            "cpu_freq_mhz": cpu_freq,
            "total_ram_gb": round(memory.total / (1024**3), 2),
            "available_ram_gb": round(memory.available / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "python_version": platform.python_version()
        }
        
        output = "### System Resource Audit\n\n"
        output += f"- **Operating System**: {specs['os']} {specs['os_release']}\n"
        output += f"- **CPU**: {specs['cpu_logical_cores']} cores @ {specs['cpu_freq_mhz']} MHz\n"
        output += f"- **RAM**: {specs['available_ram_gb']}GB available / {specs['total_ram_gb']}GB total\n"
        output += f"- **Disk**: {specs['disk_free_gb']}GB free\n"
        output += f"- **Environment**: Python {specs['python_version']}\n\n"
        
        available_ram = float(specs['available_ram_gb'])
        if available_ram < 1.0:
            output += "⚠️ **Warning**: Low available memory. High-resource tasks (like deep crawling) may fail.\n"
        else:
            output += "✅ **Status**: System meets requirements for autonomous operations.\n"
            
        return output
