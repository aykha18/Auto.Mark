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
from app.models.campaign import Campaign
from app.models.co_creator_program import CoCreatorProgram, CoCreator
from app.models.user import User

router = APIRouter()
settings = get_settings()

print(f"[LANDING_WORKING] Router initialized successfully")
print(f"[LANDING_WORKING] Settings loaded: {settings.app_name}")


def generate_compact_assessment_id() -> str:
    """Generate a compact assessment ID"""
    # Use current date (YYMMDD) + 4 random characters
    date_part = datetime.utcnow().strftime("%y%m%d")
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"assess_{date_part}_{random_part}"


async def ensure_default_campaign_and_user(db: AsyncSession) -> int:
    """Ensure default user and campaign exist"""
    print(f"[CAMPAIGN] Starting ensure_default_campaign_and_user function")
    
    try:
        # First, try to find any existing campaign
        print(f"[CAMPAIGN] Checking for existing campaigns...")
        result = await db.execute(select(Campaign).limit(1))
        campaign = result.scalar_one_or_none()
        
        if campaign:
            print(f"[CAMPAIGN] Using existing campaign ID: {campaign.id}")
            return campaign.id
        
        print(f"[CAMPAIGN] No campaigns found, checking for users...")
        # Check if we have any users
        user_result = await db.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        if not user:
            print(f"[USER] No users found, creating system user...")
            # Create a system user
            user = User(
                id=1,
                email="system@unitasa.com",
                username="system",
                full_name="System User",
                is_active=True,
                is_superuser=True
            )
            db.add(user)
            await db.flush()
            print(f"[USER] Created system user with ID: {user.id}")
        else:
            print(f"[USER] Using existing user ID: {user.id}")
        
        print(f"[CAMPAIGN] Creating default campaign with user_id: {user.id}")
        # Now create the campaign
        campaign = Campaign(
            id=1,
            campaign_id="default_landing_page_campaign",
            user_id=user.id,
            name="Landing Page Assessments",
            description="Default campaign for landing page assessment leads",
            status="active",
            campaign_type="landing_page",
            target_audience={}
        )
        db.add(campaign)
        await db.flush()
        await db.commit()  # Commit the campaign and user creation
        print(f"[CAMPAIGN] Created and committed default campaign with ID: {campaign.id}")
        print(f"[CAMPAIGN] Returning campaign ID: {campaign.id}")
        
        return campaign.id
    except Exception as e:
        print(f"[CAMPAIGN] ERROR in ensure_default_campaign_and_user: {e}")
        import traceback
        print(f"[CAMPAIGN] Full traceback: {traceback.format_exc()}")
        # If all else fails, return 1 and let the error happen - it will be logged
        return 1


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
    print(f"[LANDING_WORKING] Health check endpoint called")
    return {
        "status": "healthy",
        "service": "landing_page_working",
        "version": settings.version,
        "environment": settings.environment,
        "router": "landing_working",
        "endpoints": [
            "/health",
            "/assessment/questions", 
            "/assessment/start",
            "/assessment/submit"
        ]
    }

@router.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint to verify router is working"""
    print(f"[LANDING_WORKING] Test endpoint called successfully")
    return {
        "status": "success",
        "message": "Landing working router is functioning",
        "timestamp": datetime.utcnow().isoformat()
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
    print(f"[ROUTER] ===== ASSESSMENT START ENDPOINT CALLED =====")
    print(f"[ROUTER] Request method: {http_request.method if http_request else 'Unknown'}")
    print(f"[ROUTER] Request URL: {http_request.url if http_request else 'Unknown'}")
    print(f"[ROUTER] Request data: email={request.email}, name={request.name}, company={request.company}, preferred_crm={request.preferred_crm}")

    try:
        print(f"[STEP 1] Starting assessment for email: {request.email}, lead_id: {request.lead_id}")

        # Create or find lead
        lead = None
        if request.lead_id:
            print(f"[STEP 2A] Looking for existing lead with ID: {request.lead_id}")
            result = await db.execute(select(Lead).where(Lead.id == request.lead_id))
            lead = result.scalar_one_or_none()
            if not lead:
                print(f"[STEP 2A] ERROR: Lead not found with ID: {request.lead_id}")
                raise HTTPException(status_code=404, detail="Lead not found")
            else:
                print(f"[STEP 2A] SUCCESS: Found existing lead: {lead.id} - {lead.email}")
        elif request.email:
            print(f"[STEP 2B] Looking for existing lead with email: {request.email}")
            # Try to find existing lead by email
            result = await db.execute(select(Lead).where(Lead.email == request.email))
            lead = result.scalar_one_or_none()

            if not lead:
                print(f"[STEP 2B] Creating new lead for email: {request.email}")
                # Ensure we have a campaign (and user if needed)
                print(f"[STEP 2B] Ensuring default campaign and user exist...")
                campaign_id = await ensure_default_campaign_and_user(db)
                print(f"[STEP 2B] Got campaign ID: {campaign_id}")

                # Create new lead
                lead_id = generate_compact_assessment_id()
                print(f"[STEP 2B] Generated lead_id: {lead_id}")

                lead = Lead(
                    lead_id=lead_id,
                    campaign_id=campaign_id,
                    email=request.email,
                    first_name=request.name.split()[0] if request.name else None,
                    last_name=" ".join(request.name.split()[1:]) if request.name and len(request.name.split()) > 1 else None,
                    company=request.company,
                    source="landing_page_assessment",
                    preferred_crm=request.preferred_crm
                )
                print(f"[STEP 2B] Created lead object: {lead}")

                db.add(lead)
                print(f"[STEP 2B] Added lead to session")

                await db.flush()  # Get the ID without committing
                print(f"[STEP 2B] SUCCESS: Created new lead with ID: {lead.id}")
            else:
                print(f"[STEP 2B] SUCCESS: Found existing lead: {lead.id} - {lead.email}")
                # Update preferred CRM if provided
                if request.preferred_crm:
                    lead.preferred_crm = request.preferred_crm
                    print(f"[STEP 2B] Updated preferred CRM to: {request.preferred_crm}")
        else:
            print(f"[STEP 2] ERROR: Neither lead_id nor email provided")
            raise HTTPException(status_code=400, detail="Either lead_id or email must be provided")

        print(f"[STEP 3] Checking for existing incomplete assessment for lead: {lead.id}")
        # Check for existing incomplete assessment
        result = await db.execute(
            select(Assessment).where(
                Assessment.lead_id == lead.id,
                Assessment.is_completed == False
            )
        )
        existing_assessment = result.scalar_one_or_none()

        if existing_assessment:
            print(f"[STEP 3] SUCCESS: Found existing incomplete assessment: {existing_assessment.id}")
            return {
                "assessment_id": existing_assessment.id,
                "status": "resumed",
                "message": "Resuming existing assessment",
                "questions": assessment_engine.get_questions()
            }

        print(f"[STEP 4] Creating new assessment for lead: {lead.id}")
        # Create new assessment
        assessment = Assessment(
            lead_id=lead.id,
            assessment_type="ai_business_readiness",
            version="1.0",
            user_agent=request.user_agent,
            referrer=request.referrer,
            ip_address=http_request.client.host if http_request else None
        )
        print(f"[STEP 4] Created assessment object: {assessment}")

        db.add(assessment)
        print(f"[STEP 4] Added assessment to session")

        print(f"[STEP 5] Committing transaction...")
        await db.commit()
        print(f"[STEP 5] SUCCESS: Assessment created and committed with ID: {assessment.id}")

        print(f"[STEP 6] Getting assessment questions...")
        questions = assessment_engine.get_questions()
        print(f"[STEP 6] Got {len(questions)} questions")

        return {
            "assessment_id": assessment.id,
            "status": "started",
            "message": "Assessment started successfully",
            "questions": questions
        }

    except Exception as e:
        print(f"[ASSESSMENT START] CRITICAL ERROR: {e}")
        import traceback
        print(f"[ASSESSMENT START] Full traceback: {traceback.format_exc()}")
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