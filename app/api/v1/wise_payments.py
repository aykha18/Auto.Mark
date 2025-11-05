"""
Wise payment API endpoints for Co-Creator Program
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.wise_service_mock import get_wise_service
from app.models.payment_transaction import PaymentTransaction
from app.models.co_creator_program import CoCreator
from app.models.lead import Lead

router = APIRouter()

class PaymentRequest(BaseModel):
    amount: float
    customer_email: EmailStr
    customer_name: str
    lead_id: Optional[int] = None
    program_type: str = "co_creator"

class PaymentStatusRequest(BaseModel):
    transfer_id: str

@router.post("/create-payment")
async def create_wise_payment(
    request: PaymentRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a Wise payment for Co-Creator Program"""
    try:
        wise_service = get_wise_service(db_session=db)
        
        # For testing, we'll create a mock co-creator ID
        co_creator_id = 1  # This would normally come from your co-creator creation logic
        
        success, message, payment_data = await wise_service.create_co_creator_payment(
            co_creator_id=co_creator_id,
            customer_email=request.customer_email,
            customer_name=request.customer_name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {
            "success": True,
            "message": message,
            "payment_data": payment_data,
            "transfer_id": payment_data.get("transfer_id") if payment_data else None,
            "amount": request.amount,
            "currency": "USD"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

@router.get("/payment-status/{transfer_id}")
async def get_payment_status(
    transfer_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get Wise payment status"""
    try:
        wise_service = get_wise_service(db_session=db)
        
        success, message, status_data = await wise_service.get_payment_status(transfer_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {
            "success": True,
            "message": message,
            "status_data": status_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.post("/webhook")
async def wise_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Handle Wise webhook notifications"""
    try:
        # Get raw body and headers
        body = await request.body()
        signature = request.headers.get("X-Wise-Signature", "")
        
        wise_service = get_wise_service(db_session=db)
        
        # For testing, we'll use a simple secret
        endpoint_secret = "test_webhook_secret"
        
        success, message, event_data = await wise_service.process_webhook_event(
            payload=body.decode(),
            signature=signature,
            endpoint_secret=endpoint_secret
        )
        
        return {
            "success": success,
            "message": message,
            "processed": success
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Webhook processing failed: {str(e)}",
            "processed": False
        }

@router.post("/test-sandbox")
async def test_wise_sandbox(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Test Wise sandbox integration"""
    try:
        wise_service = get_wise_service(db_session=db)
        
        # Test with dummy data
        test_email = "test@unitasa.in"
        test_name = "Test Co-Creator"
        
        success, message, payment_data = await wise_service.create_co_creator_payment(
            co_creator_id=999,  # Test ID
            customer_email=test_email,
            customer_name=test_name
        )
        
        return {
            "success": success,
            "message": message,
            "payment_data": payment_data,
            "test_mode": True,
            "environment": wise_service.environment
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Sandbox test failed: {str(e)}",
            "test_mode": True
        }

@router.get("/config-test")
async def test_wise_config() -> Dict[str, Any]:
    """Test Wise configuration"""
    try:
        wise_service = get_wise_service()
        
        return {
            "success": True,
            "environment": wise_service.environment,
            "base_url": wise_service.base_url,
            "has_api_key": bool(wise_service.api_key),
            "has_profile_id": bool(wise_service.profile_id),
            "api_key_preview": f"{wise_service.api_key[:8]}..." if wise_service.api_key else "Not set"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }