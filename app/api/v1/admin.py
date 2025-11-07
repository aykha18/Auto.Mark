from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
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
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get dashboard statistics"""
    
    # Total leads
    total_leads = db.query(Lead).count()
    
    # Assessments completed
    assessments_completed = db.query(Assessment).filter(
        Assessment.completed == True
    ).count()
    
    # Consultations booked
    consultations_booked = db.query(Lead).filter(
        Lead.consultation_booked == True
    ).count()
    
    # Payments completed
    payments_completed = db.query(PaymentTransaction).filter(
        PaymentTransaction.status == 'completed'
    ).count()
    
    # Total revenue
    total_revenue_result = db.query(
        func.sum(PaymentTransaction.amount)
    ).filter(
        PaymentTransaction.status == 'completed'
    ).scalar()
    
    total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
    
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
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get all leads with details"""
    
    leads = db.query(Lead).order_by(desc(Lead.created_at)).limit(limit).offset(offset).all()
    
    leads_data = []
    for lead in leads:
        # Get assessment score if exists
        assessment = db.query(Assessment).filter(
            Assessment.lead_id == lead.id,
            Assessment.completed == True
        ).first()
        
        # Check payment status
        payment = db.query(PaymentTransaction).filter(
            PaymentTransaction.customer_email == lead.email,
            PaymentTransaction.status == 'completed'
        ).first()
        
        leads_data.append({
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "phone": lead.phone,
            "crm_system": lead.crm_system,
            "assessment_score": assessment.overall_score if assessment else None,
            "consultation_booked": lead.consultation_booked or False,
            "payment_completed": payment is not None,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        })
    
    return {
        "leads": leads_data,
        "total": db.query(Lead).count()
    }

@router.get("/recent-activity")
async def get_recent_activity(
    days: int = 7,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get recent activity for the last N days"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # New leads
    new_leads = db.query(Lead).filter(
        Lead.created_at >= since_date
    ).count()
    
    # New assessments
    new_assessments = db.query(Assessment).filter(
        Assessment.created_at >= since_date,
        Assessment.completed == True
    ).count()
    
    # New payments
    new_payments = db.query(PaymentTransaction).filter(
        PaymentTransaction.created_at >= since_date,
        PaymentTransaction.status == 'completed'
    ).count()
    
    # Revenue in period
    revenue_result = db.query(
        func.sum(PaymentTransaction.amount)
    ).filter(
        PaymentTransaction.created_at >= since_date,
        PaymentTransaction.status == 'completed'
    ).scalar()
    
    revenue = float(revenue_result) if revenue_result else 0.0
    
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
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get detailed information about a specific lead"""
    
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.lead_id == lead_id,
        Assessment.completed == True
    ).first()
    
    # Get payment
    payment = db.query(PaymentTransaction).filter(
        PaymentTransaction.customer_email == lead.email
    ).first()
    
    return {
        "lead": {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "phone": lead.phone,
            "crm_system": lead.crm_system,
            "consultation_booked": lead.consultation_booked,
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
