"""
Landing page API endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.config import get_settings
from app.core.assessment_engine import assessment_engine, CRMSystem
from app.core.lead_scoring import lead_scoring_engine, LeadSegment
from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.co_creator_program import CoCreatorProgram, CoCreator
from app.models.user import User
from app.core.co_creator_service import CoCreatorProgramService
from app.core.stripe_service import StripePaymentService
from app.core.co_creator_onboarding import CoCreatorOnboardingService

router = APIRouter()
settings = get_settings()


# Pydantic models for API requests/responses
class AssessmentStartRequest(BaseModel):
    """Request to start a new assessment"""
    lead_id: Optional[int] = None
    email: Optional[str] = None
    name: Optional[str] = None
    company: Optional[str] = None
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


class AssessmentResultResponse(BaseModel):
    """Assessment result response"""
    assessment_id: int
    overall_score: float
    category_scores: Dict[str, float]
    readiness_level: str
    segment: str
    current_crm: Optional[str]
    integration_recommendations: List[str]
    automation_opportunities: List[str]
    technical_requirements: List[str]
    next_steps: List[str]
    is_completed: bool


# Co-Creator Program Models
class CoCreatorProgramStatusResponse(BaseModel):
    """Co-creator program status response"""
    program_id: int
    seats_remaining: int
    total_seats: int
    seats_filled: int
    fill_percentage: float
    urgency_level: str
    urgency_message: str
    scarcity_message: str
    program_price: float
    currency: str
    is_active: bool
    is_full: bool
    program_status: str
    waitlist_enabled: bool
    waitlist_count: int


class CoCreatorReservationRequest(BaseModel):
    """Request to reserve a co-creator seat"""
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    email: str
    name: str
    company: Optional[str] = None


class CoCreatorReservationResponse(BaseModel):
    """Response for seat reservation"""
    success: bool
    message: str
    seat_number: Optional[int] = None
    program_id: Optional[int] = None
    reservation_expires_at: Optional[datetime] = None


# Payment Models
class PaymentIntentRequest(BaseModel):
    """Request to create payment intent"""
    co_creator_id: int
    customer_email: str
    customer_name: Optional[str] = None


class PaymentIntentResponse(BaseModel):
    """Response for payment intent creation"""
    success: bool
    message: str
    payment_intent_id: Optional[str] = None
    client_secret: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None


class PaymentConfirmationRequest(BaseModel):
    """Request to confirm payment"""
    payment_intent_id: str
    payment_method_id: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    """Response for payment status"""
    payment_intent_id: str
    status: str
    amount: float
    currency: str
    transaction_id: Optional[int] = None


@router.get("/health")
async def landing_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for landing page services
    """
    return {
        "status": "healthy",
        "service": "landing_page",
        "version": settings.version,
        "environment": settings.environment
    }


@router.get("/config")
async def get_landing_config() -> Dict[str, Any]:
    """
    Get configuration data for landing page frontend
    """
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "features": {
            "assessment_enabled": True,
            "co_creator_program_enabled": True,
            "payment_processing_enabled": True,
            "chat_enabled": True
        },
        "limits": {
            "co_creator_seats": 25,
            "assessment_questions": 10
        }
    }


@router.get("/status")
async def get_system_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get system status including database connectivity
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "operational",
        "services": {
            "database": db_status,
            "api": "operational",
            "landing_page": "operational"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Assessment API Endpoints

@router.get("/assessment/questions")
async def get_assessment_questions() -> Dict[str, Any]:
    """
    Get all assessment questions for the AI Business Readiness Assessment
    """
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
    db: Session = Depends(get_db),
    http_request: Request = None
) -> Dict[str, Any]:
    """
    Start a new AI Business Readiness Assessment
    """
    try:
        # Create or find lead
        lead = None
        if request.lead_id:
            lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
        elif request.email:
            # Try to find existing lead by email
            lead = db.query(Lead).filter(Lead.email == request.email).first()
            
            if not lead:
                # Create new lead - we need a campaign_id, let's use a default one or create
                # For now, we'll assume campaign_id = 1 exists or handle this gracefully
                try:
                    lead = Lead(
                        lead_id=f"assessment_{datetime.utcnow().timestamp()}",
                        campaign_id=1,  # Default campaign for assessment leads
                        email=request.email,
                        first_name=request.name.split()[0] if request.name else None,
                        last_name=" ".join(request.name.split()[1:]) if request.name and len(request.name.split()) > 1 else None,
                        company=request.company,
                        source="landing_page_assessment"
                    )
                    db.add(lead)
                    db.flush()  # Get the ID without committing
                except Exception as e:
                    # If campaign doesn't exist, create a minimal lead record
                    raise HTTPException(status_code=400, detail="Unable to create lead record")
        else:
            raise HTTPException(status_code=400, detail="Either lead_id or email must be provided")
        
        # Check for existing incomplete assessment
        existing_assessment = db.query(Assessment).filter(
            Assessment.lead_id == lead.id,
            Assessment.is_completed == False
        ).first()
        
        if existing_assessment:
            return {
                "assessment_id": existing_assessment.id,
                "status": "resumed",
                "message": "Resuming existing assessment",
                "questions": assessment_engine.get_questions()
            }
        
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
        db.commit()
        
        return {
            "assessment_id": assessment.id,
            "status": "started",
            "message": "Assessment started successfully",
            "questions": assessment_engine.get_questions()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")


@router.post("/assessment/submit")
async def submit_assessment_responses(
    request: AssessmentSubmissionRequest,
    db: Session = Depends(get_db)
) -> AssessmentResultResponse:
    """
    Submit assessment responses and get results with recommendations
    """
    try:
        # Get assessment
        assessment = db.query(Assessment).filter(Assessment.id == request.assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if assessment.is_completed:
            raise HTTPException(status_code=400, detail="Assessment already completed")
        
        # Process responses
        responses_dict = {}
        for response in request.responses:
            assessment.add_response(response.question_id, response.answer)
            responses_dict[response.question_id] = response.answer
        
        # Identify CRM system
        crm_response = responses_dict.get("crm_system", "")
        crm_system = assessment_engine.identify_crm_system(crm_response)
        assessment.current_crm = crm_system.value
        
        # Calculate scores using assessment engine
        category_scores = assessment_engine.calculate_category_scores(responses_dict)
        overall_score = assessment_engine.calculate_overall_score(category_scores)
        
        # Calculate advanced lead score using lead scoring engine
        lead_score = lead_scoring_engine.calculate_lead_score(
            responses_dict, category_scores
        )
        
        # Update assessment with scores
        assessment.update_score(lead_score.overall_score, category_scores)
        
        # Generate personalized recommendations
        personalized_recommendations = lead_scoring_engine.generate_personalized_recommendations(
            lead_score, responses_dict
        )
        
        # Convert personalized recommendations to assessment format
        assessment.integration_recommendations = [r.description for r in personalized_recommendations if r.category == "integration"]
        assessment.automation_opportunities = [r.description for r in personalized_recommendations if r.category == "automation"]
        assessment.technical_requirements = [r.description for r in personalized_recommendations if r.category == "technical"]
        assessment.next_steps = lead_scoring_engine.get_segment_next_steps(lead_score.segment, crm_system.value)
        
        # Complete assessment
        assessment.complete_assessment(request.completion_time_seconds)
        
        # Update lead with comprehensive assessment data and scoring
        if assessment.lead:
            # Update lead score (0-1 scale for compatibility)
            assessment.lead.update_score(lead_score.overall_score / 100.0)

            # Update lead with detailed assessment data
            assessment.lead.update_assessment_data(
                responses_dict,
                lead_score.factor_scores,
                lead_score.segment.value,
                lead_score.confidence
            )

            # Add assessment-related tags
            assessment.lead.add_tag("assessment_completed")
            assessment.lead.add_tag(f"crm_{crm_system.value}")
            assessment.lead.add_tag(f"readiness_{assessment.readiness_level}")
            assessment.lead.add_tag(f"confidence_{int(lead_score.confidence * 100)}")

            # Auto-qualify high-scoring leads for co-creator program
            if lead_score.overall_score >= 70:  # Hot leads
                assessment.lead.add_tag("co_creator_qualified")
                assessment.lead.add_tag("high_priority")
                # Could trigger email notification here
        
        db.commit()

        # Return enhanced response with co-creator qualification
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
            "co_creator_qualified": lead_score.overall_score >= 70,
            "co_creator_invitation": None
        }

        # Add personalized co-creator invitation for qualified leads
        if lead_score.overall_score >= 70:
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

        return AssessmentResultResponse(**{k: v for k, v in response_data.items() if k != "co_creator_invitation"})
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit assessment: {str(e)}")


@router.get("/assessment/{assessment_id}")
async def get_assessment_results(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> AssessmentResultResponse:
    """
    Get assessment results by ID
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if not assessment.is_completed:
        raise HTTPException(status_code=400, detail="Assessment not completed yet")
    
    return AssessmentResultResponse(
        assessment_id=assessment.id,
        overall_score=assessment.overall_score,
        category_scores=assessment.category_scores,
        readiness_level=assessment.readiness_level,
        segment=assessment.segment,
        current_crm=assessment.current_crm,
        integration_recommendations=assessment.integration_recommendations,
        automation_opportunities=assessment.automation_opportunities,
        technical_requirements=assessment.technical_requirements,
        next_steps=assessment.next_steps,
        is_completed=assessment.is_completed
    )


@router.get("/assessment/{assessment_id}/recommendations")
async def get_assessment_recommendations(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed recommendations for a completed assessment
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if not assessment.is_completed:
        raise HTTPException(status_code=400, detail="Assessment not completed yet")
    
    # Get CRM-specific information
    crm_info = assessment_engine.crm_capabilities.get(assessment.current_crm, {})
    
    return {
        "assessment_id": assessment.id,
        "overall_score": assessment.overall_score,
        "readiness_level": assessment.readiness_level,
        "segment": assessment.segment,
        "current_crm": {
            "system": assessment.current_crm,
            "name": crm_info.get("name", "Unknown"),
            "integration_complexity": crm_info.get("integration_complexity", "unknown"),
            "setup_time_minutes": crm_info.get("setup_time_minutes", 30),
            "automation_potential": crm_info.get("automation_potential", "medium")
        },
        "recommendations": {
            "integration": assessment.integration_recommendations,
            "automation_opportunities": assessment.automation_opportunities,
            "technical_requirements": assessment.technical_requirements,
            "next_steps": assessment.next_steps
        },
        "category_breakdown": assessment.category_scores
    }


@router.get("/crm-systems")
async def get_supported_crm_systems() -> Dict[str, Any]:
    """
    Get list of supported CRM systems with capabilities
    """
    return {
        "supported_crms": [
            {
                "id": crm.value,
                "name": info.get("name", crm.value.title()),
                "integration_complexity": info.get("integration_complexity", "medium"),
                "setup_time_minutes": info.get("setup_time_minutes", 30),
                "oauth2_supported": info.get("oauth2_supported", False),
                "webhook_support": info.get("webhook_support", False),
                "automation_potential": info.get("automation_potential", "medium"),
                "common_objects": info.get("common_objects", [])
            }
            for crm, info in assessment_engine.crm_capabilities.items()
        ]
    }


# Lead Scoring and Segmentation Endpoints

@router.get("/leads/{lead_id}/score")
async def get_lead_score(
    lead_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive lead score and segmentation data
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "lead_id": lead.id,
        "crm_readiness_summary": lead.get_crm_readiness_summary(),
        "is_co_creator_qualified": lead.is_co_creator_qualified(),
        "is_priority_lead": lead.is_priority_lead(),
        "needs_nurturing": lead.needs_nurturing(),
        "recommended_next_steps": lead.get_recommended_next_steps()
    }


@router.get("/leads/segments/{segment}")
async def get_leads_by_segment(
    segment: str,
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get leads filtered by readiness segment (cold, warm, hot)
    """
    if segment not in ["cold", "warm", "hot"]:
        raise HTTPException(status_code=400, detail="Invalid segment. Must be 'cold', 'warm', or 'hot'")
    
    leads_query = db.query(Lead).filter(Lead.readiness_segment == segment)
    total_count = leads_query.count()
    
    leads = leads_query.offset(offset).limit(limit).all()
    
    return {
        "segment": segment,
        "total_count": total_count,
        "returned_count": len(leads),
        "offset": offset,
        "limit": limit,
        "leads": [
            {
                "id": lead.id,
                "email": lead.email,
                "company": lead.company,
                "full_name": lead.full_name,
                "crm_integration_readiness": lead.crm_integration_readiness,
                "current_crm_system": lead.current_crm_system,
                "segment_confidence": lead.segment_confidence,
                "last_scored_at": lead.last_scored_at,
                "is_co_creator_qualified": lead.is_co_creator_qualified(),
                "recommended_next_steps": lead.get_recommended_next_steps()
            }
            for lead in leads
        ]
    }


@router.get("/leads/co-creator-qualified")
async def get_co_creator_qualified_leads(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get leads qualified for co-creator program (warm and hot segments)
    """
    leads_query = db.query(Lead).filter(
        Lead.readiness_segment.in_(["warm", "hot"]),
        Lead.crm_integration_readiness >= 41
    ).order_by(Lead.crm_integration_readiness.desc())
    
    total_count = leads_query.count()
    leads = leads_query.offset(offset).limit(limit).all()
    
    return {
        "total_qualified": total_count,
        "returned_count": len(leads),
        "offset": offset,
        "limit": limit,
        "qualification_criteria": {
            "min_readiness_score": 41,
            "required_segments": ["warm", "hot"]
        },
        "leads": [
            {
                "id": lead.id,
                "email": lead.email,
                "company": lead.company,
                "full_name": lead.full_name,
                "crm_integration_readiness": lead.crm_integration_readiness,
                "readiness_segment": lead.readiness_segment,
                "current_crm_system": lead.current_crm_system,
                "segment_confidence": lead.segment_confidence,
                "factor_scores": {
                    "technical_capability": lead.technical_capability_score,
                    "business_maturity": lead.business_maturity_score,
                    "investment_capacity": lead.investment_capacity_score
                },
                "last_scored_at": lead.last_scored_at
            }
            for lead in leads
        ]
    }


@router.get("/analytics/segmentation")
async def get_segmentation_analytics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analytics on lead segmentation and scoring
    """
    # Get segment counts
    cold_count = db.query(Lead).filter(Lead.readiness_segment == "cold").count()
    warm_count = db.query(Lead).filter(Lead.readiness_segment == "warm").count()
    hot_count = db.query(Lead).filter(Lead.readiness_segment == "hot").count()
    total_scored = cold_count + warm_count + hot_count
    
    # Get CRM distribution
    crm_distribution = db.query(Lead.current_crm_system, db.func.count(Lead.id)).filter(
        Lead.current_crm_system.isnot(None)
    ).group_by(Lead.current_crm_system).all()
    
    # Get average scores by segment
    avg_scores = db.query(
        Lead.readiness_segment,
        db.func.avg(Lead.crm_integration_readiness).label('avg_readiness'),
        db.func.avg(Lead.technical_capability_score).label('avg_technical'),
        db.func.avg(Lead.business_maturity_score).label('avg_business'),
        db.func.avg(Lead.investment_capacity_score).label('avg_investment')
    ).filter(
        Lead.readiness_segment.isnot(None)
    ).group_by(Lead.readiness_segment).all()
    
    # Co-creator program metrics
    co_creator_qualified = db.query(Lead).filter(
        Lead.readiness_segment.in_(["warm", "hot"]),
        Lead.crm_integration_readiness >= 41
    ).count()
    
    priority_leads = db.query(Lead).filter(
        Lead.readiness_segment == "hot",
        Lead.crm_integration_readiness >= 71
    ).count()
    
    return {
        "total_leads_scored": total_scored,
        "segment_distribution": {
            "cold": {"count": cold_count, "percentage": (cold_count / total_scored * 100) if total_scored > 0 else 0},
            "warm": {"count": warm_count, "percentage": (warm_count / total_scored * 100) if total_scored > 0 else 0},
            "hot": {"count": hot_count, "percentage": (hot_count / total_scored * 100) if total_scored > 0 else 0}
        },
        "crm_distribution": [
            {"crm_system": crm, "count": count}
            for crm, count in crm_distribution
        ],
        "average_scores_by_segment": [
            {
                "segment": segment,
                "avg_readiness": float(avg_readiness) if avg_readiness else 0,
                "avg_technical": float(avg_technical) if avg_technical else 0,
                "avg_business": float(avg_business) if avg_business else 0,
                "avg_investment": float(avg_investment) if avg_investment else 0
            }
            for segment, avg_readiness, avg_technical, avg_business, avg_investment in avg_scores
        ],
        "co_creator_program": {
            "qualified_leads": co_creator_qualified,
            "priority_leads": priority_leads,
            "qualification_rate": (co_creator_qualified / total_scored * 100) if total_scored > 0 else 0
        }
    }


# Co-Creator Program Management Endpoints

@router.get("/co-creator-program/status")
async def get_co_creator_program_status(
    db: Session = Depends(get_db)
) -> CoCreatorProgramStatusResponse:
    """
    Get current co-creator program status including seat availability and urgency messaging
    """
    try:
        service = CoCreatorProgramService(db)
        status = service.get_program_status_with_urgency()
        
        return CoCreatorProgramStatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get program status: {str(e)}")


@router.get("/co-creator-program/{program_id}")
async def get_co_creator_program_details(
    program_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific co-creator program
    """
    program = db.query(CoCreatorProgram).filter(CoCreatorProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Co-creator program not found")
    
    # Get co-creators for this program
    co_creators = db.query(CoCreator).filter(CoCreator.program_id == program_id).all()
    
    return {
        "program": program.to_dict(),
        "co_creators": [
            {
                "id": cc.id,
                "seat_number": cc.seat_number,
                "joined_at": cc.joined_at,
                "status": cc.status,
                "lifetime_access": cc.lifetime_access,
                "supporter_badge": cc.supporter_badge,
                "days_as_co_creator": cc.days_as_co_creator,
                "feature_influence_count": cc.feature_influence_count,
                "user_id": cc.user_id,
                "lead_id": cc.lead_id
            }
            for cc in co_creators
        ],
        "analytics": {
            "total_co_creators": len(co_creators),
            "active_co_creators": len([cc for cc in co_creators if cc.is_active]),
            "average_engagement": sum(cc.total_logins for cc in co_creators) / len(co_creators) if co_creators else 0,
            "total_feature_influences": sum(cc.feature_influence_count for cc in co_creators)
        }
    }


@router.post("/co-creator-program/reserve-seat")
async def reserve_co_creator_seat(
    request: CoCreatorReservationRequest,
    db: Session = Depends(get_db)
) -> CoCreatorReservationResponse:
    """
    Reserve a seat in the co-creator program (atomic operation with concurrency control)
    """
    try:
        service = CoCreatorProgramService(db)
        success, message, reservation_data = service.reserve_seat_atomic(
            email=request.email,
            name=request.name,
            company=request.company,
            lead_id=request.lead_id,
            user_id=request.user_id
        )
        
        if success and reservation_data:
            return CoCreatorReservationResponse(
                success=True,
                message=message,
                seat_number=reservation_data["seat_number"],
                program_id=reservation_data["program_id"],
                reservation_expires_at=reservation_data["reservation_expires_at"]
            )
        else:
            return CoCreatorReservationResponse(
                success=False,
                message=message
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reserve seat: {str(e)}")


@router.get("/co-creator-program/analytics")
async def get_co_creator_program_analytics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analytics and metrics for the co-creator program
    """
    try:
        service = CoCreatorProgramService(db)
        return service.get_program_analytics()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get program analytics: {str(e)}")


@router.post("/co-creator-program/{program_id}/record-page-view")
async def record_program_page_view(
    program_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Record a page view for the co-creator program (for analytics)
    """
    try:
        service = CoCreatorProgramService(db)
        success = service.record_page_view(program_id)
        
        if success:
            return {
                "success": True,
                "message": "Page view recorded"
            }
        else:
            raise HTTPException(status_code=404, detail="Co-creator program not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record page view: {str(e)}")


@router.get("/co-creator-program/qualified-leads")
async def get_co_creator_qualified_leads_detailed(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get leads qualified for co-creator program with detailed scoring and recommendations
    """
    try:
        service = CoCreatorProgramService(db)
        return service.get_qualified_leads_for_program(limit=limit, offset=offset)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get qualified leads: {str(e)}")


@router.get("/co-creator-program/benefits")
async def get_co_creator_program_benefits(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed co-creator program benefits and features
    """
    try:
        service = CoCreatorProgramService(db)
        benefits = service.get_co_creator_benefits()
        
        return {
            "program_name": "Founding Users Co-Creator Program",
            "price": 250.0,
            "currency": "USD",
            "seat_limit": 25,
            "benefits": benefits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get program benefits: {str(e)}")


@router.post("/co-creator-program/{co_creator_id}/activate")
async def activate_co_creator(
    co_creator_id: int,
    payment_confirmed: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Activate a co-creator after payment confirmation
    """
    try:
        service = CoCreatorProgramService(db)
        success, message = service.activate_co_creator(co_creator_id, payment_confirmed)
        
        return {
            "success": success,
            "message": message,
            "co_creator_id": co_creator_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate co-creator: {str(e)}")


@router.post("/co-creator-program/{co_creator_id}/cancel")
async def cancel_co_creator_reservation(
    co_creator_id: int,
    reason: str = "user_cancelled",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cancel a co-creator seat reservation
    """
    try:
        service = CoCreatorProgramService(db)
        success, message = service.cancel_reservation(co_creator_id, reason)
        
        return {
            "success": success,
            "message": message,
            "co_creator_id": co_creator_id,
            "reason": reason
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel reservation: {str(e)}")


# Payment Processing Endpoints

@router.post("/payments/create-intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    db: Session = Depends(get_db)
) -> PaymentIntentResponse:
    """
    Create a Stripe PaymentIntent for co-creator program payment
    """
    try:
        stripe_service = StripePaymentService(db)
        success, message, payment_data = stripe_service.create_co_creator_payment_intent(
            co_creator_id=request.co_creator_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name
        )
        
        if success and payment_data:
            return PaymentIntentResponse(
                success=True,
                message=message,
                payment_intent_id=payment_data["payment_intent_id"],
                client_secret=payment_data["client_secret"],
                amount=payment_data["amount"],
                currency=payment_data["currency"]
            )
        else:
            return PaymentIntentResponse(
                success=False,
                message=message
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment intent: {str(e)}")


@router.post("/payments/confirm")
async def confirm_payment(
    request: PaymentConfirmationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Confirm a payment intent
    """
    try:
        stripe_service = StripePaymentService(db)
        success, message, payment_data = stripe_service.confirm_payment(
            payment_intent_id=request.payment_intent_id,
            payment_method_id=request.payment_method_id
        )
        
        response = {
            "success": success,
            "message": message
        }
        
        if payment_data:
            response.update(payment_data)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm payment: {str(e)}")


@router.get("/payments/{payment_intent_id}/status")
async def get_payment_status(
    payment_intent_id: str,
    db: Session = Depends(get_db)
) -> PaymentStatusResponse:
    """
    Get current payment status
    """
    try:
        stripe_service = StripePaymentService(db)
        success, message, payment_data = stripe_service.get_payment_status(payment_intent_id)
        
        if success and payment_data:
            return PaymentStatusResponse(
                payment_intent_id=payment_data["payment_intent_id"],
                status=payment_data["status"],
                amount=payment_data["amount"],
                currency=payment_data["currency"],
                transaction_id=payment_data.get("transaction_id")
            )
        else:
            raise HTTPException(status_code=404, detail=message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")


@router.post("/payments/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Handle Stripe webhook events
    """
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Get webhook endpoint secret from environment
        endpoint_secret = settings.stripe.webhook_secret
        if not endpoint_secret:
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
        stripe_service = StripePaymentService(db)
        success, message, event_data = stripe_service.process_webhook_event(
            payload=payload.decode("utf-8"),
            signature=signature,
            endpoint_secret=endpoint_secret
        )
        
        if success:
            return {
                "success": True,
                "message": message,
                "event_data": event_data
            }
        else:
            raise HTTPException(status_code=400, detail=message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.post("/payments/{payment_intent_id}/refund")
async def process_refund(
    payment_intent_id: str,
    amount: Optional[float] = None,
    reason: str = "requested_by_customer",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process a refund for a payment (admin endpoint)
    """
    try:
        stripe_service = StripePaymentService(db)
        success, message, refund_data = stripe_service.process_refund(
            payment_intent_id=payment_intent_id,
            amount=amount,
            reason=reason
        )
        
        response = {
            "success": success,
            "message": message
        }
        
        if refund_data:
            response.update(refund_data)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process refund: {str(e)}")


@router.get("/payments/transactions")
async def get_payment_transactions(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get payment transactions with optional filtering
    """
    try:
        from app.models.payment_transaction import PaymentTransaction
        
        query = db.query(PaymentTransaction)
        
        if status:
            query = query.filter(PaymentTransaction.status == status)
        
        total_count = query.count()
        transactions = query.order_by(PaymentTransaction.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "total_count": total_count,
            "returned_count": len(transactions),
            "offset": offset,
            "limit": limit,
            "transactions": [
                {
                    "id": t.id,
                    "stripe_payment_intent_id": t.stripe_payment_intent_id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "status": t.status,
                    "description": t.description,
                    "user_id": t.user_id,
                    "lead_id": t.lead_id,
                    "co_creator_id": t.co_creator_id,
                    "initiated_at": t.initiated_at,
                    "processed_at": t.processed_at,
                    "receipt_email": t.receipt_email,
                    "is_successful": t.is_successful,
                    "net_amount": t.net_amount
                }
                for t in transactions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transactions: {str(e)}")


# Co-Creator Onboarding Endpoints

@router.post("/co-creator-program/{co_creator_id}/start-onboarding")
async def start_co_creator_onboarding(
    co_creator_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start the onboarding workflow for a co-creator
    """
    try:
        onboarding_service = CoCreatorOnboardingService(db)
        success, message, workflow_data = await onboarding_service.start_onboarding_workflow(co_creator_id)
        
        response = {
            "success": success,
            "message": message,
            "co_creator_id": co_creator_id
        }
        
        if workflow_data:
            response["workflow"] = workflow_data
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start onboarding: {str(e)}")


@router.get("/co-creator-program/{co_creator_id}/onboarding-status")
async def get_co_creator_onboarding_status(
    co_creator_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get onboarding status for a co-creator
    """
    try:
        onboarding_service = CoCreatorOnboardingService(db)
        status = onboarding_service.get_onboarding_status(co_creator_id)
        
        if status:
            return {
                "success": True,
                "co_creator_id": co_creator_id,
                "onboarding_status": status
            }
        else:
            raise HTTPException(status_code=404, detail="Co-creator not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding status: {str(e)}")


@router.post("/co-creator-program/{co_creator_id}/trigger-nurturing")
async def trigger_co_creator_nurturing(
    co_creator_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger ongoing nurturing workflow for a co-creator
    """
    try:
        onboarding_service = CoCreatorOnboardingService(db)
        success, message = await onboarding_service.trigger_co_creator_nurturing(co_creator_id)
        
        return {
            "success": success,
            "message": message,
            "co_creator_id": co_creator_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger nurturing: {str(e)}")


@router.get("/co-creator-program/onboarding-analytics")
async def get_onboarding_analytics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analytics on co-creator onboarding completion rates
    """
    try:
        # Get all co-creators
        co_creators = db.query(CoCreator).all()
        
        total_co_creators = len(co_creators)
        onboarded_count = 0
        pending_onboarding = 0
        failed_onboarding = 0
        
        onboarding_times = []
        
        for cc in co_creators:
            if cc.co_creator_metadata and cc.co_creator_metadata.get("onboarding_completed"):
                onboarded_count += 1
                
                # Calculate onboarding time if available
                joined_at = cc.joined_at
                completed_at_str = cc.co_creator_metadata.get("onboarding_completed_at")
                if joined_at and completed_at_str:
                    try:
                        completed_at = datetime.fromisoformat(completed_at_str)
                        onboarding_time = (completed_at - joined_at).total_seconds() / 3600  # hours
                        onboarding_times.append(onboarding_time)
                    except:
                        pass
            elif cc.status == "active":
                pending_onboarding += 1
            else:
                failed_onboarding += 1
        
        # Calculate average onboarding time
        avg_onboarding_time = sum(onboarding_times) / len(onboarding_times) if onboarding_times else 0
        
        return {
            "total_co_creators": total_co_creators,
            "onboarding_metrics": {
                "completed": onboarded_count,
                "pending": pending_onboarding,
                "failed": failed_onboarding,
                "completion_rate": (onboarded_count / total_co_creators * 100) if total_co_creators > 0 else 0
            },
            "timing_metrics": {
                "average_onboarding_time_hours": avg_onboarding_time,
                "fastest_onboarding_hours": min(onboarding_times) if onboarding_times else 0,
                "slowest_onboarding_hours": max(onboarding_times) if onboarding_times else 0
            },
            "status_distribution": {
                "active_onboarded": onboarded_count,
                "active_pending": pending_onboarding,
                "inactive_or_failed": failed_onboarding
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding analytics: {str(e)}")
