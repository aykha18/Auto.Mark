"""
MCP Type Definitions for AI Marketing Agents
"""

# Rename this file to avoid conflict with built-in types module
from datetime import datetime


class MCPMessage:
    """MCP message format for inter-agent communication"""

    def __init__(self, message_id, sender, receiver, message_type, payload, timestamp, correlation_id=None, metadata=None):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type  # "tool_call", "tool_result", "tool_list", "error"
        self.payload = payload
        self.timestamp = timestamp
        self.correlation_id = correlation_id
        self.metadata = metadata

    def to_dict(self):
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
    def from_dict(cls, data):
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


class ToolCall:
    """Represents a tool call request"""

    def __init__(self, tool_name, parameters, call_id, timeout=None):
        self.tool_name = tool_name
        self.parameters = parameters
        self.call_id = call_id
        self.timeout = timeout  # seconds

    def to_dict(self):
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "call_id": self.call_id,
            "timeout": self.timeout
        }


class ToolResult:
    """Represents a tool call result"""

    def __init__(self, call_id, success, result, error=None, execution_time=None, metadata=None):
        self.call_id = call_id
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.metadata = metadata

    def to_dict(self):
        return {
            "call_id": self.call_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {}
        }


class MCPTool:
    """MCP tool definition"""

    def __init__(self, name, description, parameters, handler=None, agent_name="", version="1.0.0", metadata=None):
        self.name = name
        self.description = description
        self.parameters = parameters  # JSON schema for parameters
        self.handler = handler
        self.agent_name = agent_name
        self.version = version
        self.metadata = metadata

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "agent_name": self.agent_name,
            "version": self.version,
            "metadata": self.metadata or {}
        }

    def validate_parameters(self, params):
        """Basic parameter validation"""
        # Simple validation - can be enhanced with JSON schema validation
        required_params = self.parameters.get("required", [])
        for param in required_params:
            if param not in params:
                return False
        return True


class ToolDiscoveryRequest:
    """Request for tool discovery"""

    def __init__(self, requester, agent_filter=None, tool_filter=None, category_filter=None):
        self.requester = requester
        self.agent_filter = agent_filter  # Specific agent name
        self.tool_filter = tool_filter   # Specific tool name
        self.category_filter = category_filter  # Tool category


class ToolDiscoveryResponse:
    """Response to tool discovery request"""

    def __init__(self, requester, tools, timestamp, total_count):
        self.requester = requester
        self.tools = tools
        self.timestamp = timestamp
        self.total_count = total_count

    def to_dict(self):
        return {
            "requester": self.requester,
            "tools": [tool.to_dict() for tool in self.tools],
            "timestamp": self.timestamp.isoformat(),
            "total_count": self.total_count
        }
