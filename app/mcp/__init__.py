"""
Model Context Protocol (MCP) implementation for AI Marketing Agents
"""

from .server import MCPServer, AgentMCPServer
from .client import MCPClient, AgentMCPClient
from .transport import MCPTransport
from .tools import MCPTool, ToolRegistry
from .mcp_types import MCPMessage, ToolCall, ToolResult

__all__ = [
    "MCPServer",
    "AgentMCPServer",
    "MCPClient",
    "AgentMCPClient",
    "MCPTransport",
    "MCPTool",
    "ToolRegistry",
    "MCPMessage",
    "ToolCall",
    "ToolResult"
]