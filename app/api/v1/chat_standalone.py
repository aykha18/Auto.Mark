"""
Standalone Chat API endpoints without database dependencies
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
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
            "id": session_id,  # Frontend uses session.id for WebSocket URL
            "status": "active",
            "started_at": datetime.utcnow().isoformat(),
            "lead_id": None,
            "user_id": None,
            "qualification_score": 0.0,
            "crm_interest_level": "unknown",
            "identified_crm": None,
            "total_messages": 0,
            "messages": []
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


@router.post("/{session_id}/message")
async def send_chat_message_fallback(
    session_id: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fallback message endpoint (standalone version)
    """
    try:
        # Mock response for now
        return {
            "success": True,
            "response": "Thank you for your message! I'm here to help you with CRM integrations and marketing automation. What would you like to know?",
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "processing_time_ms": 120,
            "requires_handoff": False,
            "analytics": {
                "intent_distribution": {"general_question": 1.0},
                "qualification_score": 0.0,
                "crm_interest_level": "unknown",
                "identified_crm": None,
                "pain_points": [],
                "sentiment": "neutral"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """
    Basic WebSocket endpoint for chat (standalone version)
    """
    await websocket.accept()
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connection established"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                # Echo back a simple response
                await websocket.send_json({
                    "type": "message_response",
                    "response": "I received your message. This is a basic WebSocket response.",
                    "message_id": str(uuid.uuid4()),
                    "processing_time_ms": 100,
                    "analytics": {},
                    "requires_handoff": False
                })
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        })


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