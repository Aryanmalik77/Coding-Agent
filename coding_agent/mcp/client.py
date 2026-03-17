"""MCP client: connects to MCP servers and wraps their tools."""

import asyncio
from contextlib import AsyncExitStack
from typing import Any

import httpx
from loguru import logger

# Note: This assumes the 'mcp' Python SDK is installed.
# We adapt the registration and execution logic to the coding agent's needs.

class MCPToolWrapper:
    """Wraps a single MCP server tool."""

    def __init__(self, session, server_name: str, tool_def, tool_timeout: int = 30):
        self._session = session
        self._server_name = server_name
        self._original_name = tool_def.name
        self._name = f"mcp_{server_name}_{tool_def.name}"
        self._description = tool_def.description or tool_def.name
        self._parameters = tool_def.inputSchema or {"type": "object", "properties": {}}
        self._tool_timeout = tool_timeout

    @property
    def server_name(self) -> str:
        return self._server_name

    @property
    def name(self) -> str:
        return self._name

    async def execute(self, **kwargs: Any) -> str:
        from mcp import types
        try:
            result = await asyncio.wait_for(
                self._session.call_tool(self._original_name, arguments=kwargs),
                timeout=self._tool_timeout,
            )
            parts = []
            for block in result.content:
                if isinstance(block, types.TextContent):
                    parts.append(block.text)
                else:
                    parts.append(str(block))
            return "\n".join(parts) or "(no output)"
        except Exception as exc:
            logger.error("MCP tool '{}' failed: {}", self._name, exc)
            return f"(MCP tool call failed: {type(exc).__name__})"


async def connect_mcp_servers(
    mcp_servers_cfg: dict, registry: Any, stack: AsyncExitStack
) -> None:
    """Connect to configured MCP servers."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    for name, cfg in mcp_servers_cfg.items():
        try:
            # We focus on 'stdio' for cocoindex usually, but keep it flexible
            if hasattr(cfg, 'command') and cfg.command:
                params = StdioServerParameters(
                    command=cfg.command, args=cfg.args, env=getattr(cfg, 'env', None)
                )
                read, write = await stack.enter_async_context(stdio_client(params))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                tools = await session.list_tools()
                for tool_def in tools.tools:
                    wrapper = MCPToolWrapper(session, name, tool_def)
                    registry.register(wrapper)
                    logger.debug("MCP: registered tool '{}' from server '{}'", wrapper._name, name)
        except Exception as e:
            logger.error("MCP server '{}' failed: {}", name, e)
