"""
MCP Tool Registry and Management for AI Marketing Agents
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from .mcp_types import MCPTool, ToolDiscoveryRequest, ToolDiscoveryResponse
from .monitoring import monitor_discovery_request

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing MCP tools across agents"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}  # tool_name -> MCPTool
        self.agent_tools: Dict[str, List[str]] = {}  # agent_name -> [tool_names]
        self._lock = asyncio.Lock()

    async def register_tool(self, tool: MCPTool) -> bool:
        """Register a new tool"""
        async with self._lock:
            if tool.name in self.tools:
                logger.warning(f"Tool {tool.name} already registered, updating")
                return False

            self.tools[tool.name] = tool

            # Add to agent tools mapping
            if tool.agent_name not in self.agent_tools:
                self.agent_tools[tool.agent_name] = []
            self.agent_tools[tool.agent_name].append(tool.name)

            logger.info(f"Registered tool: {tool.name} from agent: {tool.agent_name}")
            return True

    async def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        async with self._lock:
            if tool_name not in self.tools:
                return False

            tool = self.tools[tool_name]
            agent_name = tool.agent_name

            # Remove from tools dict
            del self.tools[tool_name]

            # Remove from agent tools mapping
            if agent_name in self.agent_tools:
                if tool_name in self.agent_tools[agent_name]:
                    self.agent_tools[agent_name].remove(tool_name)
                    if not self.agent_tools[agent_name]:
                        del self.agent_tools[agent_name]

            logger.info(f"Unregistered tool: {tool_name}")
            return True

    async def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        async with self._lock:
            return self.tools.get(tool_name)

    async def list_tools(
        self,
        agent_filter: Optional[str] = None,
        tool_filter: Optional[str] = None
    ) -> List[MCPTool]:
        """List tools with optional filtering"""
        async with self._lock:
            tools = list(self.tools.values())

            if agent_filter:
                tools = [t for t in tools if t.agent_name == agent_filter]

            if tool_filter:
                tools = [t for t in tools if tool_filter.lower() in t.name.lower()]

            return tools

    async def get_agent_tools(self, agent_name: str) -> List[MCPTool]:
        """Get all tools for a specific agent"""
        async with self._lock:
            tool_names = self.agent_tools.get(agent_name, [])
            return [self.tools[name] for name in tool_names if name in self.tools]

    async def discover_tools(self, request: ToolDiscoveryRequest) -> ToolDiscoveryResponse:
        """Handle tool discovery requests"""
        # Monitor discovery request
        await monitor_discovery_request(request.requester, request.agent_filter)

        tools = await self.list_tools(
            agent_filter=request.agent_filter,
            tool_filter=request.tool_filter
        )

        return ToolDiscoveryResponse(
            requester=request.requester,
            tools=tools,
            timestamp=datetime.utcnow(),
            total_count=len(tools)
        )

    async def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        async with self._lock:
            return {
                "total_tools": len(self.tools),
                "total_agents": len(self.agent_tools),
                "tools_per_agent": {
                    agent: len(tools) for agent, tools in self.agent_tools.items()
                },
                "timestamp": datetime.utcnow().isoformat()
            }


# Global tool registry instance
_tool_registry = None


async def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


# Convenience functions for tool management
async def register_agent_tools(agent_name: str, tools: List[MCPTool]) -> int:
    """Register multiple tools for an agent"""
    registry = await get_tool_registry()
    registered_count = 0

    for tool in tools:
        if await registry.register_tool(tool):
            registered_count += 1

    logger.info(f"Registered {registered_count} tools for agent: {agent_name}")
    return registered_count


async def discover_agent_tools(agent_name: str, requester: str) -> List[MCPTool]:
    """Discover tools available from a specific agent"""
    registry = await get_tool_registry()
    request = ToolDiscoveryRequest(
        requester=requester,
        agent_filter=agent_name
    )
    response = await registry.discover_tools(request)
    return response.tools


async def call_agent_tool(agent_name: str, tool_name: str, **kwargs) -> Any:
    """Call a tool from a specific agent"""
    registry = await get_tool_registry()

    # Find the tool
    tool = await registry.get_tool(tool_name)
    if not tool:
        raise ValueError(f"Tool {tool_name} not found")

    if tool.agent_name != agent_name:
        raise ValueError(f"Tool {tool_name} does not belong to agent {agent_name}")

    # Validate parameters
    if not tool.validate_parameters(kwargs):
        raise ValueError(f"Invalid parameters for tool {tool_name}")

    # Call the tool handler
    try:
        result = await tool.handler(**kwargs)
        logger.info(f"Successfully called tool {tool_name} from agent {agent_name}")
        return result
    except Exception as e:
        logger.error(f"Error calling tool {tool_name} from agent {agent_name}: {e}")
        raise