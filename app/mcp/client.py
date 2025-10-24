"""
MCP Client implementation for AI Marketing Agents
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from .types import MCPMessage, MCPTool, ToolCall, ToolResult, ToolDiscoveryRequest, ToolDiscoveryResponse
from .tools import get_tool_registry
from .transport import get_mcp_transport

logger = logging.getLogger(__name__)


class MCPClient:
    """Base MCP Client class"""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.transport = get_mcp_transport()
        self.discovered_tools: Dict[str, MCPTool] = {}
        self._lock = asyncio.Lock()

    async def discover_tools(
        self,
        agent_filter: Optional[str] = None,
        tool_filter: Optional[str] = None
    ) -> List[MCPTool]:
        """Discover available tools"""
        try:
            registry = await get_tool_registry()
            request = ToolDiscoveryRequest(
                requester=self.client_id,
                agent_filter=agent_filter,
                tool_filter=tool_filter
            )

            response = await registry.discover_tools(request)

            # Cache discovered tools
            async with self._lock:
                for tool in response.tools:
                    self.discovered_tools[tool.name] = tool

            logger.info(f"Discovered {len(response.tools)} tools")
            return response.tools

        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            return []

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: Optional[int] = 30
    ) -> ToolResult:
        """Call a tool by name"""
        try:
            # Get tool info
            tool = self.discovered_tools.get(tool_name)
            if not tool:
                # Try to discover the tool first
                await self.discover_tools(tool_filter=tool_name)
                tool = self.discovered_tools.get(tool_name)
                if not tool:
                    raise ValueError(f"Tool {tool_name} not found")

            # Create tool call
            tool_call = ToolCall(
                tool_name=tool_name,
                parameters=parameters,
                call_id=str(uuid.uuid4()),
                timeout=timeout
            )

            # Send via transport
            result = await self.transport.send_tool_call(
                sender=self.client_id,
                receiver=tool.agent_name,
                tool_call=tool_call,
                timeout=timeout
            )

            logger.info(f"Successfully called tool {tool_name}")
            return result

        except Exception as e:
            logger.error(f"Tool call failed for {tool_name}: {e}")
            # Return error result
            return ToolResult(
                call_id=str(uuid.uuid4()),
                success=False,
                result=None,
                error=str(e)
            )

    async def get_available_tools(self) -> List[MCPTool]:
        """Get all available tools"""
        async with self._lock:
            return list(self.discovered_tools.values())

    async def refresh_tools(self) -> int:
        """Refresh discovered tools"""
        old_count = len(self.discovered_tools)
        await self.discover_tools()
        new_count = len(self.discovered_tools)
        refreshed = new_count - old_count

        if refreshed > 0:
            logger.info(f"Refreshed {refreshed} new tools")

        return refreshed


class AgentMCPClient(MCPClient):
    """MCP Client for individual agents"""

    def __init__(self, agent_name: str):
        super().__init__(f"agent_{agent_name}")
        self.agent_name = agent_name
        self.preferred_agents: List[str] = []  # Agents this agent commonly interacts with

    async def call_agent_tool(
        self,
        target_agent: str,
        tool_name: str,
        **kwargs
    ) -> Any:
        """Call a tool from a specific agent"""
        try:
            # Ensure we have discovered tools from this agent
            if not any(tool.agent_name == target_agent for tool in self.discovered_tools.values()):
                await self.discover_tools(agent_filter=target_agent)

            # Call the tool
            result = await self.call_tool(tool_name, kwargs)

            if result.success:
                return result.result
            else:
                raise Exception(f"Tool call failed: {result.error}")

        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} from agent {target_agent}: {e}")
            raise

    async def get_agent_tools(self, agent_name: str) -> List[MCPTool]:
        """Get all tools available from a specific agent"""
        await self.discover_tools(agent_filter=agent_name)
        return [tool for tool in self.discovered_tools.values() if tool.agent_name == agent_name]

    async def find_tool_by_capability(self, capability: str) -> Optional[MCPTool]:
        """Find a tool by its capability/description"""
        await self.discover_tools()  # Ensure we have all tools

        capability_lower = capability.lower()
        for tool in self.discovered_tools.values():
            if (capability_lower in tool.description.lower() or
                capability_lower in tool.name.lower()):
                return tool

        return None

    async def call_tool_by_capability(
        self,
        capability: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> Any:
        """Call a tool by describing its capability"""
        tool = await self.find_tool_by_capability(capability)
        if not tool:
            raise ValueError(f"No tool found for capability: {capability}")

        return await self.call_agent_tool(tool.agent_name, tool.name, **parameters)

    async def set_preferred_agents(self, agent_names: List[str]):
        """Set preferred agents for faster tool discovery"""
        self.preferred_agents = agent_names
        logger.info(f"Set preferred agents for {self.agent_name}: {agent_names}")

    async def discover_preferred_tools(self) -> int:
        """Discover tools from preferred agents"""
        discovered_count = 0
        for agent_name in self.preferred_agents:
            tools = await self.get_agent_tools(agent_name)
            discovered_count += len(tools)

        logger.info(f"Discovered {discovered_count} tools from preferred agents")
        return discovered_count

    async def get_client_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        async with self._lock:
            agent_tool_counts = {}
            for tool in self.discovered_tools.values():
                agent = tool.agent_name
                agent_tool_counts[agent] = agent_tool_counts.get(agent, 0) + 1

            return {
                "client_id": self.client_id,
                "agent_name": self.agent_name,
                "discovered_tools": len(self.discovered_tools),
                "preferred_agents": self.preferred_agents,
                "tools_by_agent": agent_tool_counts,
                "timestamp": datetime.utcnow().isoformat()
            }


# Convenience functions
async def create_agent_mcp_client(agent_name: str) -> AgentMCPClient:
    """Create an MCP client for an agent"""
    client = AgentMCPClient(agent_name)

    # Auto-discover tools from common agents
    common_agents = ["lead_generation", "content_creator", "ad_manager"]
    if agent_name in common_agents:
        other_agents = [a for a in common_agents if a != agent_name]
        await client.set_preferred_agents(other_agents)
        await client.discover_preferred_tools()

    return client


async def quick_tool_call(
    caller_agent: str,
    target_agent: str,
    tool_name: str,
    **kwargs
) -> Any:
    """Quick tool call between agents"""
    client = await create_agent_mcp_client(caller_agent)
    return await client.call_agent_tool(target_agent, tool_name, **kwargs)