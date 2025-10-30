"""
PaymentTransaction model for Stripe integration and payment processing
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PaymentTransaction(Base, TimestampMixin):
    """PaymentTransaction model for tracking all payment transactions"""

    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # External payment provider IDs
    stripe_payment_intent_id = Column(String(255), unique=True, index=True)
    stripe_charge_id = Column(String(255), index=True)
    stripe_customer_id = Column(String(255), index=True)
    
    # User and lead associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    co_creator_id = Column(Integer, ForeignKey("co_creators.id"), nullable=True, index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)  # Amount in dollars (e.g., 250.00)
    currency = Column(String(3), default="USD", nullable=False)
    description = Column(Text)
    
    # Payment status
    status = Column(String(50), nullable=False, index=True)  # pending, succeeded, failed, cancelled, refunded
    payment_method = Column(String(50))  # card, bank_transfer, etc.
    payment_method_details = Column(JSON, default=dict)  # Card last 4, brand, etc.
    
    # Transaction timeline
    initiated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, index=True)
    failed_at = Column(DateTime)
    refunded_at = Column(DateTime)
    
    # Error handling
    failure_reason = Column(String(255))
    failure_code = Column(String(100))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Refund information
    refund_amount = Column(Float, default=0.0)
    refund_reason = Column(String(255))
    refunded_by = Column(String(255))  # admin user who processed refund
    
    # Receipt and billing
    receipt_email = Column(String(255))
    receipt_url = Column(Text)
    invoice_id = Column(String(255))
    
    # Metadata and tracking
    payment_metadata = Column(JSON, default=dict)  # Additional data from Stripe
    source = Column(String(100), default="landing_page")  # landing_page, admin, api
    user_agent = Column(Text)
    ip_address = Column(String(45))
    
    # Webhook processing
    webhook_received = Column(Boolean, default=False, nullable=False)
    webhook_processed_at = Column(DateTime)
    webhook_event_id = Column(String(255))
    
    # Relationships
    user = relationship("User")
    lead = relationship("Lead")
    co_creator = relationship("CoCreator")

    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, amount=${self.amount:.2f}, status='{self.status}', stripe_id='{self.stripe_payment_intent_id}')>"

    @property
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == "succeeded"

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == "pending"

    @property
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == "failed"

    @property
    def is_refunded(self) -> bool:
        """Check if payment was refunded"""
        return self.status == "refunded" or self.refund_amount > 0

    @property
    def net_amount(self) -> float:
        """Calculate net amount after refunds"""
        return self.amount - self.refund_amount

    @property
    def processing_time_seconds(self) -> Optional[int]:
        """Calculate processing time in seconds"""
        if self.processed_at and self.initiated_at:
            delta = self.processed_at - self.initiated_at
            return int(delta.total_seconds())
        return None

    def mark_succeeded(self, stripe_charge_id: str = None, processed_at: datetime = None):
        """Mark payment as succeeded"""
        self.status = "succeeded"
        self.processed_at = processed_at or datetime.utcnow()
        
        if stripe_charge_id:
            self.stripe_charge_id = stripe_charge_id
        
        self.updated_at = datetime.utcnow()

    def mark_failed(self, failure_reason: str = None, failure_code: str = None, 
                   error_message: str = None):
        """Mark payment as failed"""
        self.status = "failed"
        self.failed_at = datetime.utcnow()
        
        if failure_reason:
            self.failure_reason = failure_reason
        if failure_code:
            self.failure_code = failure_code
        if error_message:
            self.error_message = error_message
        
        self.retry_count += 1
        self.updated_at = datetime.utcnow()

    def mark_cancelled(self):
        """Mark payment as cancelled"""
        self.status = "cancelled"
        self.updated_at = datetime.utcnow()

    def process_refund(self, refund_amount: float, reason: str = None, 
                      refunded_by: str = None):
        """Process a refund"""
        self.refund_amount += refund_amount
        self.refund_reason = reason
        self.refunded_by = refunded_by
        self.refunded_at = datetime.utcnow()
        
        # If fully refunded, update status
        if self.refund_amount >= self.amount:
            self.status = "refunded"
        
        self.updated_at = datetime.utcnow()

    def update_payment_method_details(self, details: Dict[str, Any]):
        """Update payment method details"""
        self.payment_method_details = details
        
        # Extract common fields
        if "card" in details:
            card = details["card"]
            self.payment_method = "card"
        
        self.updated_at = datetime.utcnow()

    def set_receipt_info(self, receipt_email: str = None, receipt_url: str = None):
        """Set receipt information"""
        if receipt_email:
            self.receipt_email = receipt_email
        if receipt_url:
            self.receipt_url = receipt_url
        
        self.updated_at = datetime.utcnow()

    def process_webhook(self, event_id: str = None):
        """Mark webhook as processed"""
        self.webhook_received = True
        self.webhook_processed_at = datetime.utcnow()
        
        if event_id:
            self.webhook_event_id = event_id
        
        self.updated_at = datetime.utcnow()

    def add_metadata(self, key: str, value: Any):
        """Add metadata"""
        if not self.payment_metadata:
            self.payment_metadata = {}
        
        self.payment_metadata[key] = value
        self.updated_at = datetime.utcnow()

    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if payment can be retried"""
        return self.retry_count < max_retries and self.status == "failed"

    @classmethod
    def create_from_stripe_intent(cls, stripe_payment_intent: Dict[str, Any], 
                                 user_id: int = None, lead_id: int = None,
                                 **kwargs) -> 'PaymentTransaction':
        """Create transaction from Stripe PaymentIntent"""
        transaction = cls(
            stripe_payment_intent_id=stripe_payment_intent.get("id"),
            amount=stripe_payment_intent.get("amount", 0) / 100,  # Convert cents to dollars
            currency=stripe_payment_intent.get("currency", "usd").upper(),
            status=stripe_payment_intent.get("status", "pending"),
            description=stripe_payment_intent.get("description"),
            user_id=user_id,
            lead_id=lead_id,
            payment_metadata=stripe_payment_intent.get("metadata", {}),
            **kwargs
        )
        
        return transaction

    @classmethod
    def find_by_stripe_intent_id(cls, db_session, stripe_intent_id: str) -> Optional['PaymentTransaction']:
        """Find transaction by Stripe PaymentIntent ID"""
        return db_session.query(cls).filter(
            cls.stripe_payment_intent_id == stripe_intent_id
        ).first()

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        result = super().to_dict()
        result.update({
            'is_successful': self.is_successful,
            'is_pending': self.is_pending,
            'is_failed': self.is_failed,
            'is_refunded': self.is_refunded,
            'net_amount': self.net_amount,
            'processing_time_seconds': self.processing_time_seconds
        })
        return result