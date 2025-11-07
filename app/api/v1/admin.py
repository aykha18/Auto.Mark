from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.payment_transaction import PaymentTransaction

router = APIRouter(prefix="/admin", tags=["admin"])

# Simple password-based auth (in production, use proper JWT auth)
ADMIN_PASSWORD = "unitasa2025"  # Change this to a secure password

def verify_admin(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    if token != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return True

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get dashboard statistics"""
    
    # Total leads
    total_leads_result = await db.execute(select(func.count()).select_from(Lead))
    total_leads = total_leads_result.scalar() or 0
    
    # Assessments completed
    assessments_result = await db.execute(
        select(func.count()).select_from(Assessment).where(Assessment.is_completed == True)
    )
    assessments_completed = assessments_result.scalar() or 0
    
    # Consultations booked
    consultations_result = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.consultation_booked == True)
    )
    consultations_booked = consultations_result.scalar() or 0
    
    # Payments completed
    payments_result = await db.execute(
        select(func.count()).select_from(PaymentTransaction).where(
            PaymentTransaction.status == 'completed'
        )
    )
    payments_completed = payments_result.scalar() or 0
    
    # Total revenue
    revenue_result = await db.execute(
        select(func.sum(PaymentTransaction.amount)).where(
            PaymentTransaction.status == 'completed'
        )
    )
    total_revenue_value = revenue_result.scalar()
    total_revenue = float(total_revenue_value) if total_revenue_value else 0.0
    
    # Conversion rate (payments / total leads)
    conversion_rate = (payments_completed / total_leads * 100) if total_leads > 0 else 0.0
    
    return {
        "totalLeads": total_leads,
        "assessmentsCompleted": assessments_completed,
        "consultationsBooked": consultations_booked,
        "paymentsCompleted": payments_completed,
        "totalRevenue": total_revenue,
        "conversionRate": conversion_rate
    }

@router.get("/leads")
async def get_leads(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get all leads with details"""
    
    # Get leads using raw SQL to avoid ORM schema mismatch
    from sqlalchemy import text
    query = text("""
        SELECT id, name, email, company, preferred_crm, consultation_booked, created_at
        FROM leads
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    leads_result = await db.execute(query, {"limit": limit, "offset": offset})
    leads = leads_result.all()
    
    leads_data = []
    for row in leads:
        lead_id = row[0]
        lead_name = row[1]
        lead_email = row[2]
        lead_company = row[3]
        lead_crm = row[4]
        lead_consultation_booked = row[5]
        lead_created_at = row[6]
        
        # Get assessment score if exists
        assessment_result = await db.execute(
            select(Assessment).where(
                Assessment.lead_id == lead_id,
                Assessment.is_completed == True
            )
        )
        assessment = assessment_result.scalar_one_or_none()
        
        # Check payment status
        payment_result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.customer_email == lead_email,
                PaymentTransaction.status == 'completed'
            )
        )
        payment = payment_result.scalar_one_or_none()
        
        leads_data.append({
            "id": lead_id,
            "name": lead_name,
            "email": lead_email,
            "company": lead_company,
            "phone": None,  # Not in current schema
            "crm_system": lead_crm,
            "assessment_score": assessment.overall_score if assessment else None,
            "consultation_booked": lead_consultation_booked or False,
            "payment_completed": payment is not None,
            "created_at": lead_created_at.isoformat() if lead_created_at else None
        })
    
    # Get total count
    total_result = await db.execute(select(func.count()).select_from(Lead))
    total = total_result.scalar() or 0
    
    return {
        "leads": leads_data,
        "total": total
    }

@router.get("/recent-activity")
async def get_recent_activity(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get recent activity for the last N days"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # New leads
    new_leads_result = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.created_at >= since_date)
    )
    new_leads = new_leads_result.scalar() or 0
    
    # New assessments
    new_assessments_result = await db.execute(
        select(func.count()).select_from(Assessment).where(
            Assessment.created_at >= since_date,
            Assessment.is_completed == True
        )
    )
    new_assessments = new_assessments_result.scalar() or 0
    
    # New payments
    new_payments_result = await db.execute(
        select(func.count()).select_from(PaymentTransaction).where(
            PaymentTransaction.created_at >= since_date,
            PaymentTransaction.status == 'completed'
        )
    )
    new_payments = new_payments_result.scalar() or 0
    
    # Revenue in period
    revenue_result = await db.execute(
        select(func.sum(PaymentTransaction.amount)).where(
            PaymentTransaction.created_at >= since_date,
            PaymentTransaction.status == 'completed'
        )
    )
    revenue_value = revenue_result.scalar()
    revenue = float(revenue_value) if revenue_value else 0.0
    
    return {
        "period_days": days,
        "new_leads": new_leads,
        "new_assessments": new_assessments,
        "new_payments": new_payments,
        "revenue": revenue
    }

@router.get("/lead/{lead_id}")
async def get_lead_details(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get detailed information about a specific lead"""
    
    # Get lead
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get assessment
    assessment_result = await db.execute(
        select(Assessment).where(
            Assessment.lead_id == lead_id,
            Assessment.is_completed == True
        )
    )
    assessment = assessment_result.scalar_one_or_none()
    
    # Get payment
    payment_result = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.customer_email == lead.email
        )
    )
    payment = payment_result.scalar_one_or_none()
    
    return {
        "lead": {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "phone": lead.phone,
            "crm_system": lead.crm_system,
            "consultation_booked": getattr(lead, 'consultation_booked', False),
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        },
        "assessment": {
            "score": assessment.overall_score,
            "completed_at": assessment.completed_at.isoformat() if assessment and assessment.completed_at else None
        } if assessment else None,
        "payment": {
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "created_at": payment.created_at.isoformat() if payment and payment.created_at else None
        } if payment else None
    }
