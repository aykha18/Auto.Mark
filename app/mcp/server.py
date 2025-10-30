"""
MCP Server implementation for AI Marketing Agents
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import uuid

from .mcp_types import MCPMessage, MCPTool, ToolCall, ToolResult
from .tools import get_tool_registry
from .transport import get_mcp_transport

logger = logging.getLogger(__name__)


class MCPServer:
    """Base MCP Server class"""

    def __init__(self, server_id: str):
        self.server_id = server_id
        self.transport = get_mcp_transport()
        self.is_running = False
        self._setup_message_handlers()

    def _setup_message_handlers(self):
        """Setup message handlers for incoming requests"""
        self.transport.register_handler("tool_call", self._handle_tool_call)
        self.transport.register_handler("tool_list_request", self._handle_tool_list_request)

    async def start(self):
        """Start the MCP server"""
        self.is_running = True
        logger.info(f"MCP Server {self.server_id} started")

    async def stop(self):
        """Stop the MCP server"""
        self.is_running = False
        logger.info(f"MCP Server {self.server_id} stopped")

    async def _handle_tool_call(self, message: MCPMessage):
        """Handle incoming tool call requests"""
        try:
            tool_call_data = message.payload
            tool_call = ToolCall(**tool_call_data)

            # Execute the tool
            result = await self._execute_tool(tool_call)

            # Send result back
            tool_result = ToolResult(
                call_id=tool_call.call_id,
                success=result.get("success", True),
                result=result.get("result"),
                error=result.get("error"),
                execution_time=result.get("execution_time"),
                metadata=result.get("metadata")
            )

            await self.transport.send_tool_result(
                sender=self.server_id,
                receiver=message.sender,
                tool_result=tool_result
            )

        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            # Send error response
            error_result = ToolResult(
                call_id=message.payload.get("call_id", "unknown"),
                success=False,
                result=None,
                error=str(e)
            )
            await self.transport.send_tool_result(
                sender=self.server_id,
                receiver=message.sender,
                tool_result=error_result
            )

    async def _handle_tool_list_request(self, message: MCPMessage):
        """Handle tool list requests"""
        try:
            registry = await get_tool_registry()
            agent_filter = message.payload.get("agent_filter")

            tools = await registry.list_tools(agent_filter=agent_filter)

            # Send response (simplified - in practice would use a proper response message)
            response_payload = {
                "tools": [tool.to_dict() for tool in tools],
                "total_count": len(tools),
                "timestamp": datetime.utcnow().isoformat()
            }

            # For this implementation, we'll use the pending calls mechanism
            call_id = message.message_id
            if call_id in self.transport.pending_calls:
                future = self.transport.pending_calls[call_id]
                if not future.done():
                    future.set_result(response_payload)

        except Exception as e:
            logger.error(f"Error handling tool list request: {e}")

    async def _execute_tool(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_tool")


class AgentMCPServer(MCPServer):
    """MCP Server for individual agents"""

    def __init__(self, agent_name: str, agent_instance: Any):
        super().__init__(f"agent_{agent_name}")
        self.agent_name = agent_name
        self.agent_instance = agent_instance
        self.registered_tools: Dict[str, MCPTool] = {}

    async def register_tool(self, tool: MCPTool) -> bool:
        """Register a tool for this agent"""
        try:
            registry = await get_tool_registry()
            success = await registry.register_tool(tool)

            if success:
                self.registered_tools[tool.name] = tool
                logger.info(f"Agent {self.agent_name} registered tool: {tool.name}")

            return success
        except Exception as e:
            logger.error(f"Failed to register tool {tool.name}: {e}")
            return False

    async def register_tools(self, tools: List[MCPTool]) -> int:
        """Register multiple tools"""
        registered_count = 0
        for tool in tools:
            if await self.register_tool(tool):
                registered_count += 1
        return registered_count

    async def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        try:
            registry = await get_tool_registry()
            success = await registry.unregister_tool(tool_name)

            if success and tool_name in self.registered_tools:
                del self.registered_tools[tool_name]
                logger.info(f"Agent {self.agent_name} unregistered tool: {tool_name}")

            return success
        except Exception as e:
            logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False

    async def _execute_tool(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call on this agent"""
        start_time = datetime.utcnow()

        try:
            # Get the tool
            tool = self.registered_tools.get(tool_call.tool_name)
            if not tool:
                raise ValueError(f"Tool {tool_call.tool_name} not found")

            # Validate parameters
            if not tool.validate_parameters(tool_call.parameters):
                raise ValueError(f"Invalid parameters for tool {tool_call.tool_name}")

            # Execute the tool
            result = await tool.handler(**tool_call.parameters)

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "metadata": {
                    "agent": self.agent_name,
                    "tool": tool_call.tool_name
                }
            }

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Tool execution failed: {e}")

            return {
                "success": False,
                "result": None,
                "error": str(e),
                "execution_time": execution_time,
                "metadata": {
                    "agent": self.agent_name,
                    "tool": tool_call.tool_name
                }
            }

    async def get_registered_tools(self) -> List[MCPTool]:
        """Get all tools registered by this agent"""
        return list(self.registered_tools.values())

    async def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool by name"""
        return self.registered_tools.get(tool_name)

    async def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "server_id": self.server_id,
            "agent_name": self.agent_name,
            "registered_tools": len(self.registered_tools),
            "is_running": self.is_running,
            "tool_names": list(self.registered_tools.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }