"""
MCP Transport Layer for inter-agent communication
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

from .mcp_types import MCPMessage, ToolCall, ToolResult
from .monitoring import monitor_tool_call_start, monitor_tool_call_end, monitor_message_routed

logger = logging.getLogger(__name__)


class MCPTransport:
    """Transport layer for MCP message passing between agents"""

    def __init__(self):
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_calls: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def send_message(self, message: MCPMessage) -> bool:
        """Send an MCP message"""
        try:
            # Monitor message routing
            await monitor_message_routed(message.message_type, message.sender, message.receiver)

            # Route message to appropriate handler
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(message)
                logger.debug(f"Message {message.message_id} routed to handler")
                return True
            else:
                logger.warning(f"No handler for message type: {message.message_type}")
                return False
        except Exception as e:
            logger.error(f"Error sending message {message.message_id}: {e}")
            return False

    async def send_tool_call(
        self,
        sender: str,
        receiver: str,
        tool_call: ToolCall,
        timeout: Optional[int] = 30
    ) -> ToolResult:
        """Send a tool call and wait for result"""
        call_id = tool_call.call_id

        # Monitor the start of the tool call
        await monitor_tool_call_start(call_id, tool_call.tool_name, sender, receiver)

        # Create future for the result
        future = asyncio.Future()
        async with self._lock:
            self.pending_calls[call_id] = future

        # Create MCP message
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            message_type="tool_call",
            payload=tool_call.to_dict(),
            timestamp=datetime.utcnow(),
            correlation_id=call_id
        )

        # Send the message
        success = await self.send_message(message)
        if not success:
            async with self._lock:
                del self.pending_calls[call_id]
            # Monitor failed tool call
            await monitor_tool_call_end(call_id, False, "Failed to send message")
            raise Exception(f"Failed to send tool call {call_id}")

        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            # Monitor successful tool call
            await monitor_tool_call_end(call_id, result.success, result.error)
            return result
        except asyncio.TimeoutError:
            async with self._lock:
                if call_id in self.pending_calls:
                    del self.pending_calls[call_id]
            # Monitor timeout
            await monitor_tool_call_end(call_id, False, "Timeout")
            raise TimeoutError(f"Tool call {call_id} timed out")
        finally:
            async with self._lock:
                if call_id in self.pending_calls:
                    del self.pending_calls[call_id]

    async def send_tool_result(
        self,
        sender: str,
        receiver: str,
        tool_result: ToolResult
    ) -> bool:
        """Send a tool result"""
        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            message_type="tool_result",
            payload=tool_result.to_dict(),
            timestamp=datetime.utcnow(),
            correlation_id=tool_result.call_id
        )

        return await self.send_message(message)

    async def request_tool_list(
        self,
        requester: str,
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Request list of available tools"""
        payload = {"agent_filter": agent_name} if agent_name else {}

        message = MCPMessage(
            message_id=str(uuid.uuid4()),
            sender=requester,
            receiver="tool_registry",  # Special receiver for registry
            message_type="tool_list_request",
            payload=payload,
            timestamp=datetime.utcnow()
        )

        # For tool list requests, we expect an immediate response
        # This is a simplified implementation
        future = asyncio.Future()
        call_id = message.message_id

        async with self._lock:
            self.pending_calls[call_id] = future

        success = await self.send_message(message)
        if not success:
            async with self._lock:
                del self.pending_calls[call_id]
            raise Exception("Failed to send tool list request")

        try:
            result = await asyncio.wait_for(future, timeout=10)
            return result
        except asyncio.TimeoutError:
            async with self._lock:
                if call_id in self.pending_calls:
                    del self.pending_calls[call_id]
            raise TimeoutError("Tool list request timed out")
        finally:
            async with self._lock:
                if call_id in self.pending_calls:
                    del self.pending_calls[call_id]

    async def handle_incoming_message(self, message: MCPMessage):
        """Handle incoming MCP messages"""
        try:
            if message.message_type == "tool_call":
                await self._handle_tool_call(message)
            elif message.message_type == "tool_result":
                await self._handle_tool_result(message)
            elif message.message_type == "tool_list_request":
                await self._handle_tool_list_request(message)
            elif message.message_type == "error":
                await self._handle_error(message)
            else:
                logger.warning(f"Unknown message type: {message.message_type}")
        except Exception as e:
            logger.error(f"Error handling message {message.message_id}: {e}")

    async def _handle_tool_call(self, message: MCPMessage):
        """Handle incoming tool call"""
        # This would be implemented by the agent receiving the call
        logger.info(f"Received tool call from {message.sender}: {message.payload}")

    async def _handle_tool_result(self, message: MCPMessage):
        """Handle incoming tool result"""
        call_id = message.correlation_id
        if call_id and call_id in self.pending_calls:
            future = self.pending_calls[call_id]
            if not future.done():
                result = ToolResult(**message.payload)
                future.set_result(result)
            async with self._lock:
                del self.pending_calls[call_id]
        else:
            logger.warning(f"Received result for unknown call: {call_id}")

    async def _handle_tool_list_request(self, message: MCPMessage):
        """Handle tool list request"""
        # This would be handled by the tool registry
        logger.info(f"Received tool list request from {message.sender}")

    async def _handle_error(self, message: MCPMessage):
        """Handle error messages"""
        call_id = message.correlation_id
        if call_id and call_id in self.pending_calls:
            future = self.pending_calls[call_id]
            if not future.done():
                future.set_exception(Exception(message.payload.get("error", "Unknown error")))
            async with self._lock:
                del self.pending_calls[call_id]
        logger.error(f"Received error from {message.sender}: {message.payload}")

    async def cleanup_pending_calls(self, max_age_seconds: int = 300):
        """Clean up old pending calls"""
        cutoff_time = datetime.utcnow().timestamp() - max_age_seconds
        to_remove = []

        async with self._lock:
            for call_id, future in self.pending_calls.items():
                # This is a simplified cleanup - in practice you'd track creation time
                if future.done():
                    to_remove.append(call_id)

            for call_id in to_remove:
                del self.pending_calls[call_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} completed pending calls")


# Global transport instance
_transport = None


def get_mcp_transport() -> MCPTransport:
    """Get the global MCP transport instance"""
    global _transport
    if _transport is None:
        _transport = MCPTransport()
    return _transport