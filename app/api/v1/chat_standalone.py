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
        
        # Return a basic session response that matches frontend expectations
        response_data = {
            "session_id": session_id,
            "id": session_id,  # Frontend uses session.id for WebSocket URL
            "active": True,  # Frontend expects 'active' boolean instead of 'status'
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "content": "Welcome to Unitasa! I'm here to help you with CRM integrations and marketing automation questions.\n\nTry asking:\n• \"How does Unitasa integrate with Salesforce?\"\n• \"What CRM features do you support?\"\n• \"Help me choose the right integration\"\n• \"Tell me about the co-creator program\"",
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "text"
                }
            ],
            "context": request.context if request and request.context else {},
            "voiceEnabled": True
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
        # Return a proper chat message response
        response_message = {
            "id": str(uuid.uuid4()),
            "content": "Hello! I'm Unitasa's AI Marketing Assistant. I'm here to help you understand how AI can transform your marketing operations. What specific challenges are you facing with your current marketing setup?",
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text"
        }
        return response_message
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
        # Return a proper chat message response
        response_message = {
            "id": str(uuid.uuid4()),
            "content": "Thank you for your message! I'm here to help you with CRM integrations and marketing automation. What would you like to know?",
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text"
        }
        return response_message
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
            print(f"[WEBSOCKET] Received data: {data}")
            
            if data.get("type") == "message":
                user_content = data.get("content", "").lower()
                
                # Generate contextual responses
                if "hi" in user_content or "hello" in user_content:
                    response_content = "Hello! 👋 I'm Unitasa's AI Marketing Assistant. I'm here to help you transform your marketing operations with AI-powered CRM integrations. What can I help you with today?"
                elif "how are you" in user_content:
                    response_content = "I'm doing great, thank you for asking! I'm ready to help you with CRM integrations, marketing automation, and AI solutions. What specific challenges are you facing with your current marketing setup?"
                elif "crm" in user_content:
                    response_content = "Great question about CRM! Unitasa integrates with major CRM platforms like Salesforce, HubSpot, Pipedrive, and more. We can help automate your lead generation, scoring, and nurturing processes. Which CRM are you currently using?"
                elif "salesforce" in user_content:
                    response_content = "Excellent choice! Unitasa has deep Salesforce integration capabilities. We can help you automate lead capture, scoring, and nurturing directly in Salesforce. Would you like to know about our specific Salesforce features?"
                elif "price" in user_content or "cost" in user_content:
                    response_content = "Our pricing is designed to scale with your business needs. We offer flexible plans starting from basic integrations to enterprise solutions. Would you like me to connect you with our team for a personalized quote?"
                else:
                    response_content = f"Thanks for your message! I'm Unitasa's AI Marketing Assistant. I can help you with CRM integrations, marketing automation, lead generation, and AI readiness assessments. What specific area would you like to explore?"
                
                # Send back a proper chat message
                response_message = {
                    "id": str(uuid.uuid4()),
                    "content": response_content,
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "text"
                }
                print(f"[WEBSOCKET] Sending response: {response_message}")
                await websocket.send_json(response_message)
                
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