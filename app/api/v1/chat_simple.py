"""
Simple Chat API endpoints for testing
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint for chat service
    """
    return {
        "status": "healthy",
        "service": "chat_service_simple",
        "message": "Chat service is running"
    }


@router.post("/initialize")
async def initialize_chat_session_simple() -> Dict[str, Any]:
    """
    Simple chat session initialization
    """
    return {
        "session_id": "test_session_123",
        "status": "active",
        "message": "Chat session initialized successfully",
        "test": True
    }


@router.post("/test")
async def test_chat_endpoint() -> Dict[str, Any]:
    """
    Test endpoint to verify chat router is working
    """
    return {
        "success": True,
        "message": "Chat router is working correctly",
        "timestamp": "2025-11-03T07:30:00Z"
    }