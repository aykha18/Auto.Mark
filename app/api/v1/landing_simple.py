"""
Simplified landing page API endpoints for testing
"""

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AssessmentStartRequest(BaseModel):
    """Request to start a new assessment"""
    email: str
    name: str
    company: str = None


@router.get("/health")
async def landing_health_check() -> Dict[str, Any]:
    """Health check endpoint for landing page services"""
    return {
        "status": "healthy",
        "service": "landing_page_simple",
        "version": "1.0.0"
    }


@router.post("/assessment/start")
async def start_assessment(request: AssessmentStartRequest) -> Dict[str, Any]:
    """Start a new AI Business Readiness Assessment (simplified)"""
    return {
        "assessment_id": 1,
        "status": "started",
        "message": "Assessment started successfully (simplified mode)",
        "email": request.email,
        "name": request.name
    }


@router.post("/assessment/submit")
async def submit_assessment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit assessment responses (simplified)"""
    return {
        "assessment_id": data.get("assessment_id", 1),
        "status": "completed",
        "message": "Assessment completed successfully (simplified mode)",
        "overall_score": 75.0,
        "readiness_level": "warm"
    }