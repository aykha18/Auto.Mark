"""
Working landing page API endpoints (assessment only)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import string
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.config import get_settings
from app.core.assessment_engine import assessment_engine, CRMSystem
from app.core.lead_scoring import lead_scoring_engine, LeadSegment
from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.co_creator_program import CoCreatorProgram, CoCreator
from app.models.user import User

router = APIRouter()
settings = get_settings()


def generate_compact_assessment_id() -> str:
    """Generate a compact assessment ID"""
    # Use current date (YYMMDD) + 4 random characters
    date_part = datetime.utcnow().strftime("%y%m%d")
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"assess_{date_part}_{random_part}"


# Pydantic models for API requests/responses
class AssessmentStartRequest(BaseModel):
    """Request to start a new assessment"""
    lead_id: Optional[int] = None
    email: Optional[str] = None
    name: Optional[str] = None
    company: Optional[str] = None
    preferred_crm: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Single assessment response"""
    question_id: str
    answer: Any
    timestamp: Optional[datetime] = None


class AssessmentSubmissionRequest(BaseModel):
    """Request to submit assessment responses"""
    assessment_id: int
    responses: List[AssessmentResponse]
    completion_time_seconds: Optional[int] = None


@router.get("/health")
async def landing_health_check() -> Dict[str, Any]:
    """Health check endpoint for landing page services"""
    return {
        "status": "healthy",
        "service": "landing_page",
        "version": settings.version,
        "environment": settings.environment
    }


@router.get("/assessment/questions")
async def get_assessment_questions() -> Dict[str, Any]:
    """Get all assessment questions for the AI Business Readiness Assessment"""
    questions = assessment_engine.get_questions()
    
    return {
        "questions": questions,
        "total_questions": len(questions),
        "estimated_time_minutes": 5,
        "assessment_type": "ai_business_readiness",
        "version": "1.0"
    }


@router.post("/assessment/start")
async def start_assessment(
    request: AssessmentStartRequest,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
) -> Dict[str, Any]:
    """Start a new AI Business Readiness Assessment"""
    try:
        print(f"[ASSESSMENT START] Starting assessment for email: {request.email}, lead_id: {request.lead_id}")

        # Create or find lead
        lead = None
        if request.lead_id:
            print(f"[ASSESSMENT START] Looking for existing lead with ID: {request.lead_id}")
            result = await db.execute(select(Lead).where(Lead.id == request.lead_id))
            lead = result.scalar_one_or_none()
            if not lead:
                print(f"[ASSESSMENT START] Lead not found with ID: {request.lead_id}")
                raise HTTPException(status_code=404, detail="Lead not found")
            else:
                print(f"[ASSESSMENT START] Found existing lead: {lead.id} - {lead.email}")
        elif request.email:
            print(f"[ASSESSMENT START] Looking for existing lead with email: {request.email}")
            # Try to find existing lead by email
            result = await db.execute(select(Lead).where(Lead.email == request.email))
            lead = result.scalar_one_or_none()

            if not lead:
                print(f"[ASSESSMENT START] Creating new lead for email: {request.email}")
                # Create new lead
                lead = Lead(
                    lead_id=generate_compact_assessment_id(),
                    campaign_id=1,  # Default campaign for assessment leads
                    email=request.email,
                    first_name=request.name.split()[0] if request.name else None,
                    last_name=" ".join(request.name.split()[1:]) if request.name and len(request.name.split()) > 1 else None,
                    company=request.company,
                    source="landing_page_assessment",
                    preferred_crm=request.preferred_crm
                )
                db.add(lead)
                await db.flush()  # Get the ID without committing
                print(f"[ASSESSMENT START] Created new lead with ID: {lead.id}")
            else:
                print(f"[ASSESSMENT START] Found existing lead: {lead.id} - {lead.email}")
                # Update preferred CRM if provided
                if request.preferred_crm:
                    lead.preferred_crm = request.preferred_crm
        else:
            print(f"[ASSESSMENT START] ERROR: Neither lead_id nor email provided")
            raise HTTPException(status_code=400, detail="Either lead_id or email must be provided")

        print(f"[ASSESSMENT START] Checking for existing incomplete assessment for lead: {lead.id}")
        # Check for existing incomplete assessment
        result = await db.execute(
            select(Assessment).where(
                Assessment.lead_id == lead.id,
                Assessment.is_completed == False
            )
        )
        existing_assessment = result.scalar_one_or_none()

        if existing_assessment:
            print(f"[ASSESSMENT START] Found existing incomplete assessment: {existing_assessment.id}")
            return {
                "assessment_id": existing_assessment.id,
                "status": "resumed",
                "message": "Resuming existing assessment",
                "questions": assessment_engine.get_questions()
            }

        print(f"[ASSESSMENT START] Creating new assessment for lead: {lead.id}")
        # Create new assessment
        assessment = Assessment(
            lead_id=lead.id,
            assessment_type="ai_business_readiness",
            version="1.0",
            user_agent=request.user_agent,
            referrer=request.referrer,
            ip_address=http_request.client.host if http_request else None
        )

        db.add(assessment)
        await db.commit()
        print(f"[ASSESSMENT START] Assessment created and committed with ID: {assessment.id}")

        return {
            "assessment_id": assessment.id,
            "status": "started",
            "message": "Assessment started successfully",
            "questions": assessment_engine.get_questions()
        }

    except Exception as e:
        print(f"[ASSESSMENT START] ERROR: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")


@router.post("/assessment/submit")
async def submit_assessment_responses(
    request: AssessmentSubmissionRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Submit assessment responses and get results with recommendations"""
    try:
        print(f"[ASSESSMENT SUBMIT] Starting submission for assessment_id: {request.assessment_id}")

        # Get assessment using async query
        result = await db.execute(select(Assessment).where(Assessment.id == request.assessment_id))
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            print(f"[ASSESSMENT SUBMIT] ERROR: Assessment not found with ID: {request.assessment_id}")
            raise HTTPException(status_code=404, detail="Assessment not found")

        if assessment.is_completed:
            print(f"[ASSESSMENT SUBMIT] ERROR: Assessment already completed: {request.assessment_id}")
            raise HTTPException(status_code=400, detail="Assessment already completed")

        print(f"[ASSESSMENT SUBMIT] Processing {len(request.responses)} responses for assessment: {request.assessment_id}")

        # Process responses
        responses_dict = {}
        for response in request.responses:
            responses_dict[response.question_id] = response.answer

        # Update assessment responses
        assessment.responses = responses_dict
        
        print(f"[ASSESSMENT SUBMIT] Responses processed. CRM response: {responses_dict.get('crm_system', 'N/A')}")

        # Identify CRM system
        crm_response = responses_dict.get("crm_system", "")
        crm_system = assessment_engine.identify_crm_system(crm_response)
        assessment.current_crm = crm_system.value
        print(f"[ASSESSMENT SUBMIT] Identified CRM system: {crm_system.value}")

        # Calculate scores using assessment engine
        category_scores = assessment_engine.calculate_category_scores(responses_dict)
        overall_score = assessment_engine.calculate_overall_score(category_scores)
        
        # Round scores to 1 decimal place for better presentation
        overall_score = round(overall_score, 1)
        category_scores = {k: round(v, 1) for k, v in category_scores.items()}
        
        print(f"[ASSESSMENT SUBMIT] Calculated scores - Overall: {overall_score}, Categories: {category_scores}")

        # Calculate advanced lead score using lead scoring engine
        lead_score = lead_scoring_engine.calculate_lead_score(
            responses_dict, category_scores
        )
        
        # Round lead score to 1 decimal place
        lead_score.overall_score = round(lead_score.overall_score, 1)
        lead_score.confidence = round(lead_score.confidence, 2)
        
        print(f"[ASSESSMENT SUBMIT] Lead score calculated - Overall: {lead_score.overall_score}, Segment: {lead_score.segment.value}")

        # Update assessment with scores
        assessment.overall_score = overall_score
        assessment.category_scores = category_scores
        assessment.readiness_level = lead_score.segment.value
        assessment.segment = lead_score.segment.value
        assessment.is_completed = True
        assessment.completed_at = datetime.utcnow()
        if request.completion_time_seconds:
            assessment.completion_time_seconds = request.completion_time_seconds

        # Generate personalized recommendations
        personalized_recommendations = lead_scoring_engine.generate_personalized_recommendations(
            lead_score, responses_dict
        )
        print(f"[ASSESSMENT SUBMIT] Generated {len(personalized_recommendations)} personalized recommendations")

        # Convert personalized recommendations to assessment format
        assessment.integration_recommendations = [r.description for r in personalized_recommendations if r.category == "integration"]
        assessment.automation_opportunities = [r.description for r in personalized_recommendations if r.category == "automation"]
        assessment.technical_requirements = [r.description for r in personalized_recommendations if r.category == "technical"]
        assessment.next_steps = lead_scoring_engine.get_segment_next_steps(lead_score.segment, crm_system.value)

        # Update lead with assessment data
        print(f"[ASSESSMENT SUBMIT] Loading lead {assessment.lead_id} for update")
        lead_result = await db.execute(select(Lead).where(Lead.id == assessment.lead_id))
        lead = lead_result.scalar_one_or_none()
        
        if lead:
            print(f"[ASSESSMENT SUBMIT] Updating lead {lead.id} with assessment data")
            # Update lead score (0-1 scale for compatibility)
            lead.score = round(lead_score.overall_score / 100.0, 3)  # Round to 3 decimal places for 0-1 scale
            lead.readiness_segment = lead_score.segment.value
            lead.current_crm_system = crm_system.value
            lead.crm_integration_readiness = round(lead_score.overall_score, 1)
            lead.segment_confidence = round(lead_score.confidence, 2)
            lead.last_scored_at = datetime.utcnow()

        await db.commit()
        print(f"[ASSESSMENT SUBMIT] Assessment and lead data committed to database")

        # Return response
        response_data = {
            "assessment_id": assessment.id,
            "overall_score": assessment.overall_score,
            "category_scores": assessment.category_scores,
            "readiness_level": assessment.readiness_level,
            "segment": assessment.segment,
            "current_crm": assessment.current_crm,
            "integration_recommendations": assessment.integration_recommendations,
            "automation_opportunities": assessment.automation_opportunities,
            "technical_requirements": assessment.technical_requirements,
            "next_steps": assessment.next_steps,
            "is_completed": assessment.is_completed,
            "co_creator_qualified": lead_score.overall_score >= 70
        }

        # Add personalized co-creator invitation for qualified leads
        if lead_score.overall_score >= 70:
            print(f"[ASSESSMENT SUBMIT] Adding co-creator invitation for qualified lead")
            response_data["co_creator_invitation"] = {
                "message": "🎉 Congratulations! Based on your assessment results, you're qualified for our exclusive Co-Creator Program!",
                "benefits": [
                    "Lifetime access to all platform features",
                    "Direct influence on product development",
                    "Priority support and custom integrations",
                    "Exclusive community access"
                ],
                "next_action": "Reserve your founding member seat now",
                "urgency": "Only 25 seats available - program fills quickly"
            }

        return response_data

    except Exception as e:
        print(f"[ASSESSMENT SUBMIT] ERROR: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit assessment: {str(e)}")