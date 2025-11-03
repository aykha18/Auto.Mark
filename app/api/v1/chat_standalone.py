"""
Standalone Chat API endpoints without database dependencies
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class ChatSessionCreateRequest(BaseModel):
    """Request to create a new chat session"""
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for chat service
    """
    return {
        "status": "healthy",
        "service": "chat_service_standalone",
        "message": "Chat service is operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/initialize")
async def initialize_chat_session(
    request: Optional[ChatSessionCreateRequest] = None,
    http_request: Request = None
) -> Dict[str, Any]:
    """
    Create a new chat session (standalone version)
    """
    try:
        # Generate a simple session ID
        session_id = str(uuid.uuid4())
        
        # Return a basic session response
        response_data = {
            "session_id": session_id,
            "status": "active",
            "started_at": datetime.utcnow().isoformat(),
            "lead_id": None,
            "user_id": None,
            "qualification_score": 0.0,
            "crm_interest_level": "unknown",
            "identified_crm": None,
            "total_messages": 0,
            "messages": [],
            "id": session_id  # Add id field that frontend expects
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.post("/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send a message to the chat (standalone version)
    """
    try:
        # Mock response for now
        return {
            "success": True,
            "response": "Hello! I'm Unitasa's AI Marketing Assistant. I'm here to help you understand how AI can transform your marketing operations. What specific challenges are you facing with your current marketing setup?",
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "processing_time_ms": 150,
            "requires_handoff": False,
            "analytics": {
                "intent_distribution": {"general_greeting": 1.0},
                "qualification_score": 0.0,
                "crm_interest_level": "unknown",
                "identified_crm": None,
                "pain_points": [],
                "sentiment": "neutral"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """
    Test endpoint to verify chat router is working
    """
    return {
        "success": True,
        "message": "Standalone chat router is working correctly",
        "timestamp": datetime.utcnow().isoformat()
    }