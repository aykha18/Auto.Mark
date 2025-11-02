# Simplified agent stubs for deployment
# These provide basic functionality without complex dependencies

from typing import Dict, Any, Optional
import logging
import httpx

logger = logging.getLogger(__name__)


class AgentMessage:
    """Simple message class for agent communication"""
    def __init__(self, content: str, sender: str = "system", **kwargs):
        self.content = content
        self.sender = sender
        self.metadata = kwargs


class AgentCommunicator:
    """Simplified agent communicator"""
    def __init__(self):
        self.logger = logger
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message (stub implementation)"""
        self.logger.info(f"Agent message: {message.content}")
        return True


def get_communicator() -> AgentCommunicator:
    """Get agent communicator instance"""
    return AgentCommunicator()


def get_orchestrator():
    """Get orchestrator instance (stub)"""
    logger.info("Orchestrator requested - using stub implementation")
    return None


def get_conversational_agent():
    """Get conversational agent (stub)"""
    logger.info("Conversational agent requested - using stub implementation")
    return None


async def process_chat_message(session_id: str, user_message: str, conversation_history: list = None) -> Dict[str, Any]:
    """Process chat message using Grok API"""
    import httpx
    import json
    import os

    try:
        # Get Grok API key from environment
        grok_api_key = os.getenv("GROK_API_KEY")
        if not grok_api_key:
            logger.error("GROK_API_KEY environment variable not set")
            raise ValueError("GROK_API_KEY environment variable is required")

        # Prepare conversation context
        messages = []

        # Add system prompt
        system_prompt = """You are Unitasa's AI Marketing Assistant, a sophisticated conversational AI designed to help businesses transform their marketing operations.

Your capabilities:
- Expert knowledge of CRM integrations (HubSpot, Pipedrive, Zoho, Monday, Salesforce)
- Deep understanding of marketing automation and lead generation
- Ability to assess business readiness for AI implementation
- Knowledge of Unitasa's platform features and benefits

Your personality:
- Professional yet approachable
- Technically knowledgeable but not overwhelming
- Focused on solving business problems
- Always helpful and solution-oriented

Guidelines:
- Ask qualifying questions to understand their business needs
- Recommend specific CRM integrations based on their current setup
- Explain complex concepts in simple terms
- Guide them toward taking action (assessment, demo, etc.)
- Be conversational and engaging
- Never be pushy or salesy

Current context: User is on Unitasa's landing page, interested in AI marketing solutions."""

        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                role = "user" if msg.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("content", "")})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call Grok API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )

            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]

                # Generate analytics (mock for now)
                analytics = {
                    "intent_distribution": {"crm_inquiry": 0.3, "general_question": 0.4, "pricing_question": 0.3},
                    "qualification_score": 65.0,
                    "crm_interest_level": "medium",
                    "identified_crm": None,
                    "pain_points": ["marketing_automation", "lead_generation"],
                    "sentiment": "positive"
                }

                return {
                    "response": ai_response,
                    "session_id": session_id,
                    "analytics": analytics,
                    "requires_handoff": False,
                    "success": True
                }
            else:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                # Fallback response
                return {
                    "response": "I apologize, but I'm experiencing a temporary connection issue. Our AI marketing assistant is designed to help you with CRM integrations, lead generation strategies, and assessing your business readiness for AI-powered marketing automation. Would you like me to connect you with a human specialist who can assist you directly?",
                    "session_id": session_id,
                    "analytics": {
                        "intent_distribution": {"error": 1.0},
                        "qualification_score": 0.0,
                        "crm_interest_level": "unknown",
                        "identified_crm": None,
                        "pain_points": [],
                        "sentiment": "neutral"
                    },
                    "requires_handoff": True,
                    "handoff_reason": "api_error",
                    "success": True
                }

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        # Fallback response
        return {
            "response": "Thank you for your message. Our AI capabilities are currently being deployed. Would you like me to help you get started with our AI Readiness Assessment instead?",
            "session_id": session_id,
            "analytics": {
                "intent_distribution": {"error": 1.0},
                "qualification_score": 0.0,
                "crm_interest_level": "unknown",
                "identified_crm": None,
                "pain_points": [],
                "sentiment": "neutral"
            },
            "requires_handoff": False,
            "success": True
        }


# Export the functions that are commonly imported
__all__ = [
    "AgentMessage",
    "AgentCommunicator", 
    "get_communicator",
    "get_orchestrator",
    "get_conversational_agent",
    "process_chat_message"
]