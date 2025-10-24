"""
Agent Communication Protocol - Standardized messaging between agents
"""

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Standardized message format for inter-agent communication"""

    sender: str
    receiver: str
    message_type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'message_type': self.message_type,
            'payload': self.payload,
            'correlation_id': self.correlation_id,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        return cls(
            sender=data['sender'],
            receiver=data['receiver'],
            message_type=data['message_type'],
            payload=data['payload'],
            correlation_id=data.get('correlation_id'),
            timestamp=data.get('timestamp')
        )


# Message Types
MESSAGE_TYPES = {
    'task_request': 'Request to perform a task',
    'task_result': 'Result of completed task',
    'data_request': 'Request for data or information',
    'data_response': 'Response with requested data',
    'status_update': 'Status update from agent',
    'error_notification': 'Error notification',
    'optimization_suggestion': 'Suggested optimization',
    'approval_request': 'Request for human approval',
    'campaign_update': 'Campaign status update',
    'lead_notification': 'New lead notification',
    'content_ready': 'Content generation completed',
    'performance_alert': 'Performance threshold alert'
}


class AgentCommunicator:
    """Handles inter-agent communication"""

    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.active_conversations: Dict[str, List[AgentMessage]] = {}
        self.message_handlers: Dict[str, callable] = {}

        logger.info("Agent Communicator initialized")

    async def send_message(self, message: AgentMessage) -> None:
        """Send message to another agent"""
        # Store in conversation history
        conversation_id = message.correlation_id
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []

        self.active_conversations[conversation_id].append(message)

        # Add to message queue for processing
        await self.message_queue.put(message)

        logger.info(
            "Message sent",
            sender=message.sender,
            receiver=message.receiver,
            message_type=message.message_type,
            correlation_id=message.correlation_id
        )

    async def receive_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get messages for specific agent"""
        messages = []

        # Check message queue for relevant messages
        temp_queue = asyncio.Queue()
        while not self.message_queue.empty():
            message = await self.message_queue.get()

            if message.receiver == agent_name or message.receiver == 'all':
                messages.append(message)
            else:
                await temp_queue.put(message)

        # Restore non-relevant messages
        while not temp_queue.empty():
            await self.message_queue.put(await temp_queue.get())

        return messages

    async def broadcast_status(self, agent_name: str, status: Dict[str, Any]) -> None:
        """Broadcast agent status to all other agents"""
        message = AgentMessage(
            sender=agent_name,
            receiver='all',
            message_type='status_update',
            payload=status
        )

        await self.send_message(message)

    async def request_data(self, from_agent: str, to_agent: str, data_type: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Request data from another agent"""
        correlation_id = str(uuid.uuid4())

        message = AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type='data_request',
            payload={
                'data_type': data_type,
                'filters': filters or {}
            },
            correlation_id=correlation_id
        )

        await self.send_message(message)
        return correlation_id

    async def send_task_result(self, from_agent: str, to_agent: str, task_id: str, result: Dict[str, Any]) -> None:
        """Send task completion result"""
        message = AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type='task_result',
            payload={
                'task_id': task_id,
                'result': result,
                'status': 'completed'
            }
        )

        await self.send_message(message)

    async def notify_error(self, from_agent: str, error_details: Dict[str, Any]) -> None:
        """Send error notification"""
        message = AgentMessage(
            sender=from_agent,
            receiver='orchestrator',  # Send to orchestrator by default
            message_type='error_notification',
            payload=error_details
        )

        await self.send_message(message)

    async def suggest_optimization(self, from_agent: str, suggestions: List[Dict[str, Any]]) -> None:
        """Send optimization suggestions"""
        message = AgentMessage(
            sender=from_agent,
            receiver='orchestrator',
            message_type='optimization_suggestion',
            payload={'suggestions': suggestions}
        )

        await self.send_message(message)

    def register_handler(self, message_type: str, handler: callable) -> None:
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
        logger.info(f"Handler registered for message type: {message_type}")

    async def process_messages(self) -> None:
        """Process messages in the queue (for background processing)"""
        while True:
            try:
                message = await self.message_queue.get()

                # Process message with registered handler
                handler = self.message_handlers.get(message.message_type)
                if handler:
                    await handler(message)
                else:
                    logger.warning(f"No handler for message type: {message.message_type}")

                self.message_queue.task_done()

            except Exception as e:
                logger.error(f"Error processing message: {e}")

    def get_conversation_history(self, correlation_id: str) -> List[AgentMessage]:
        """Get conversation history for a correlation ID"""
        return self.active_conversations.get(correlation_id, [])

    def clear_old_conversations(self, max_age_hours: int = 24) -> int:
        """Clear conversations older than specified hours"""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        conversations_to_remove = []

        for correlation_id, messages in self.active_conversations.items():
            if messages and datetime.fromisoformat(messages[0].timestamp).timestamp() < cutoff_time:
                conversations_to_remove.append(correlation_id)

        for correlation_id in conversations_to_remove:
            del self.active_conversations[correlation_id]

        logger.info(f"Cleared {len(conversations_to_remove)} old conversations")
        return len(conversations_to_remove)


# Global communicator instance
_communicator = None


def get_communicator() -> AgentCommunicator:
    """Get the global communicator instance"""
    global _communicator
    if _communicator is None:
        _communicator = AgentCommunicator()
    return _communicator


# Convenience functions for common messaging patterns
async def send_lead_notification(agent_name: str, leads: List[Dict[str, Any]]) -> None:
    """Send notification about new leads"""
    communicator = get_communicator()
    message = AgentMessage(
        sender=agent_name,
        receiver='content_creator',
        message_type='lead_notification',
        payload={'leads': leads, 'count': len(leads)}
    )
    await communicator.send_message(message)


async def send_content_ready_notification(agent_name: str, content: List[Dict[str, Any]]) -> None:
    """Send notification about ready content"""
    communicator = get_communicator()
    message = AgentMessage(
        sender=agent_name,
        receiver='ad_manager',
        message_type='content_ready',
        payload={'content': content, 'count': len(content)}
    )
    await communicator.send_message(message)


async def send_performance_alert(agent_name: str, metric: str, value: float, threshold: float) -> None:
    """Send performance alert"""
    communicator = get_communicator()
    message = AgentMessage(
        sender=agent_name,
        receiver='orchestrator',
        message_type='performance_alert',
        payload={
            'metric': metric,
            'value': value,
            'threshold': threshold,
            'alert_type': 'below_threshold' if value < threshold else 'above_threshold'
        }
    )
    await communicator.send_message(message)


async def request_campaign_data(from_agent: str, campaign_id: str) -> str:
    """Request campaign data from orchestrator"""
    communicator = get_communicator()
    return await communicator.request_data(
        from_agent=from_agent,
        to_agent='orchestrator',
        data_type='campaign_data',
        filters={'campaign_id': campaign_id}
    )