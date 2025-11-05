"""
Simple working assessment endpoints - no dependencies
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AssessmentStartRequest(BaseModel):
    email: str
    name: str = None
    company: str = None
    preferred_crm: str = None

@router.get("/questions")
async def get_questions() -> Dict[str, Any]:
    """Get assessment questions"""
    return {
        "questions": [
            {
                "id": "crm_system",
                "question": "Which CRM system are you currently using?",
                "type": "multiple_choice",
                "options": ["Salesforce", "HubSpot", "Pipedrive", "Zoho", "Monday.com", "Other", "None"]
            },
            {
                "id": "monthly_leads", 
                "question": "How many leads do you generate per month?",
                "type": "multiple_choice",
                "options": ["0-50", "51-200", "201-500", "501-1000", "1000+"]
            },
            {
                "id": "automation_level",
                "question": "What's your current marketing automation level?",
                "type": "scale",
                "min": 1,
                "max": 10
            }
        ],
        "total_questions": 3,
        "estimated_time_minutes": 3,
        "assessment_type": "ai_business_readiness"
    }

@router.post("/start")
async def start_assessment(request: AssessmentStartRequest) -> Dict[str, Any]:
    """Start assessment"""
    assessment_id = f"assess_{datetime.utcnow().strftime('%y%m%d')}_{hash(request.email) % 10000:04d}"
    
    return {
        "assessment_id": assessment_id,
        "status": "started",
        "message": "Assessment started successfully",
        "questions": (await get_questions())["questions"]
    }

@router.post("/submit")
async def submit_assessment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit assessment"""
    return {
        "assessment_id": data.get("assessment_id"),
        "overall_score": 75.0,
        "category_scores": {
            "crm_integration": 75.0,
            "technical_capability": 70.0,
            "business_maturity": 80.0,
            "automation_readiness": 65.0
        },
        "readiness_level": "warm",
        "segment": "warm",
        "current_crm": data.get("responses", [{}])[0].get("answer", "other"),
        "integration_recommendations": [
            "Integrate with your CRM for automated lead capture",
            "Set up real-time data synchronization",
            "Configure custom field mapping"
        ],
        "automation_opportunities": [
            "Automate lead scoring and qualification",
            "Set up email nurturing sequences", 
            "Implement behavior-based triggers"
        ],
        "technical_requirements": [
            "API access to your CRM system",
            "Webhook configuration for real-time updates",
            "Data validation and cleanup"
        ],
        "next_steps": [
            "Schedule integration consultation",
            "Review CRM data quality",
            "Plan automation workflow"
        ],
        "is_completed": True,
        "co_creator_qualified": True
    }