"""Tools for inter-agent coordination."""

from typing import Any
from coding_agent.swarm.bridge import SwarmBridge

class DelegateUITaskTool:
    def __init__(self, bridge: SwarmBridge):
        self._bridge = bridge

    @property
    def name(self) -> str: return "delegate_ui_task"

    async def execute(self, task: str, **kwargs: Any) -> str:
        return await self._bridge.delegate_to_ui_agent(task, kwargs.get("session_key", "default"))


class RequestSwarmPlanningTool:
    def __init__(self, bridge: SwarmBridge):
        self._bridge = bridge

    @property
    def name(self) -> str: return "request_swarm_planning"

    async def execute(self, objective: str, **kwargs: Any) -> str:
        return await self._bridge.request_swarm_planning(objective)
