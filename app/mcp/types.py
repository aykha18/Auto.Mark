"""
MCP Type Definitions for AI Marketing Agents
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MCPMessage:
    """MCP message format for inter-agent communication"""

    message_id: str
    sender: str
    receiver: str
    message_type: str  # "tool_call", "tool_result", "tool_list", "error"
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create from dictionary"""
        return cls(
            message_id=data["message_id"],
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class ToolCall:
    """Represents a tool call request"""

    tool_name: str
    parameters: Dict[str, Any]
    call_id: str
    timeout: Optional[int] = None  # seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "call_id": self.call_id,
            "timeout": self.timeout
        }


@dataclass
class ToolResult:
    """Represents a tool call result"""

    call_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {}
        }


@dataclass
class MCPTool:
    """MCP tool definition"""

    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema for parameters
    handler: callable
    agent_name: str
    version: str = "1.0.0"
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "agent_name": self.agent_name,
            "version": self.version,
            "metadata": self.metadata or {}
        }

    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Basic parameter validation"""
        # Simple validation - can be enhanced with JSON schema validation
        required_params = self.parameters.get("required", [])
        for param in required_params:
            if param not in params:
                return False
        return True


@dataclass
class ToolDiscoveryRequest:
    """Request for tool discovery"""

    requester: str
    agent_filter: Optional[str] = None  # Specific agent name
    tool_filter: Optional[str] = None   # Specific tool name
    category_filter: Optional[str] = None  # Tool category


@dataclass
class ToolDiscoveryResponse:
    """Response to tool discovery request"""

    requester: str
    tools: List[MCPTool]
    timestamp: datetime
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requester": self.requester,
            "tools": [tool.to_dict() for tool in self.tools],
            "timestamp": self.timestamp.isoformat(),
            "total_count": self.total_count
        }