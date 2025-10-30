"""
Stripe Payment Service
Handles Stripe payment processing, webhooks, and co-creator program payments
"""

import os
import stripe
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.payment_transaction import PaymentTransaction
from app.models.co_creator_program import CoCreator
from app.models.user import User
from app.models.lead import Lead
from app.core.co_creator_service import CoCreatorProgramService
from app.core.email_service import EmailService
from app.core.webhook_security import WebhookSecurityManager, PaymentFraudDetector
from app.config import get_settings

settings = get_settings()

# Configure Stripe
stripe.api_key = settings.stripe.secret_key


class StripePaymentService:
    """Service for handling Stripe payment processing"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.co_creator_service = CoCreatorProgramService(db_session)
        self.email_service = EmailService()
        self.webhook_security = WebhookSecurityManager()
        self.fraud_detector = PaymentFraudDetector()
    
    def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        description: str = None,
        customer_email: str = None,
        metadata: Dict[str, Any] = None,
        user_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        co_creator_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Create a Stripe PaymentIntent for co-creator program payment
        Returns: (success, message, payment_data)
        """
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            # Prepare metadata
            payment_metadata = {
                "source": "co_creator_program",
                "amount_dollars": str(amount),
                **(metadata or {})
            }
            
            if user_id:
                payment_metadata["user_id"] = str(user_id)
            if lead_id:
                payment_metadata["lead_id"] = str(lead_id)
            if co_creator_id:
                payment_metadata["co_creator_id"] = str(co_creator_id)
            
            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                description=description or "Co-Creator Program - Founding User Access",
                receipt_email=customer_email,
                metadata=payment_metadata,
                automatic_payment_methods={
                    "enabled": True
                }
            )
            
            # Create local transaction record
            transaction = PaymentTransaction.create_from_stripe_intent(
                stripe_payment_intent=intent,
                user_id=user_id,
                lead_id=lead_id,
                co_creator_id=co_creator_id,
                description=description,
                receipt_email=customer_email,
                source="landing_page"
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            payment_data = {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency.upper(),
                "status": intent.status,
                "transaction_id": transaction.id
            }
            
            return True, "Payment intent created successfully", payment_data
            
        except stripe.error.StripeError as e:
            return False, f"Stripe error: {str(e)}", None
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to create payment intent: {str(e)}", None
    
    def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: str = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Confirm a payment intent
        Returns: (success, message, payment_data)
        """
        try:
            # Retrieve and confirm the PaymentIntent
            if payment_method_id:
                intent = stripe.PaymentIntent.confirm(
                    payment_intent_id,
                    payment_method=payment_method_id
                )
            else:
                intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            # Update local transaction
            transaction = PaymentTransaction.find_by_stripe_intent_id(
                self.db, payment_intent_id
            )
            
            if transaction:
                if intent.status == "succeeded":
                    transaction.mark_succeeded(
                        stripe_charge_id=intent.charges.data[0].id if intent.charges.data else None
                    )
                    
                    # Activate co-creator if associated
                    if transaction.co_creator_id:
                        self.co_creator_service.activate_co_creator(
                            transaction.co_creator_id, payment_confirmed=True
                        )
                
                elif intent.status == "requires_action":
                    # Payment requires additional action (3D Secure, etc.)
                    pass
                
                elif intent.status in ["canceled", "payment_failed"]:
                    transaction.mark_failed(
                        failure_reason=intent.last_payment_error.message if intent.last_payment_error else "Payment failed",
                        failure_code=intent.last_payment_error.code if intent.last_payment_error else None
                    )
                
                self.db.commit()
            
            payment_data = {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency.upper()
            }
            
            if intent.status == "succeeded":
                return True, "Payment confirmed successfully", payment_data
            elif intent.status == "requires_action":
                payment_data["next_action"] = intent.next_action
                return False, "Payment requires additional action", payment_data
            else:
                return False, f"Payment confirmation failed: {intent.status}", payment_data
            
        except stripe.error.StripeError as e:
            return False, f"Stripe error: {str(e)}", None
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to confirm payment: {str(e)}", None
    
    def process_webhook_event(
        self,
        payload: str,
        signature: str,
        endpoint_secret: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process Stripe webhook event
        Returns: (success, message, event_data)
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, endpoint_secret
            )
            
            event_type = event["type"]
            event_data = event["data"]["object"]
            
            # Handle different event types
            if event_type == "payment_intent.succeeded":
                return self._handle_payment_succeeded(event_data, event["id"])
            
            elif event_type == "payment_intent.payment_failed":
                return self._handle_payment_failed(event_data, event["id"])
            
            elif event_type == "payment_intent.canceled":
                return self._handle_payment_canceled(event_data, event["id"])
            
            elif event_type == "charge.dispute.created":
                return self._handle_dispute_created(event_data, event["id"])
            
            else:
                # Unhandled event type
                return True, f"Unhandled event type: {event_type}", {"event_type": event_type}
            
        except stripe.error.SignatureVerificationError:
            return False, "Invalid webhook signature", None
        except Exception as e:
            return False, f"Webhook processing error: {str(e)}", None
    
    def _handle_payment_succeeded(
        self,
        payment_intent: Dict[str, Any],
        event_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Handle successful payment webhook"""
        try:
            transaction = PaymentTransaction.find_by_stripe_intent_id(
                self.db, payment_intent["id"]
            )
            
            if not transaction:
                return False, "Transaction not found", None
            
            # Mark payment as succeeded
            transaction.mark_succeeded()
            transaction.process_webhook(event_id)
            
            # Set receipt information
            if payment_intent.get("receipt_email"):
                transaction.set_receipt_info(
                    receipt_email=payment_intent["receipt_email"]
                )
            
            # Activate co-creator and send emails
            co_creator_activated = False
            if transaction.co_creator_id:
                success, message = self.co_creator_service.activate_co_creator(
                    transaction.co_creator_id, payment_confirmed=True
                )
                
                if success:
                    co_creator_activated = True
                    # Send receipt and welcome emails
                    co_creator = self.db.query(CoCreator).filter(CoCreator.id == transaction.co_creator_id).first()
                    if co_creator and transaction.receipt_email:
                        # Send payment receipt
                        self.email_service.send_payment_receipt(transaction, co_creator)
                        # Send welcome email
                        self.email_service.send_welcome_email(co_creator, transaction.receipt_email)
                        
                        # Trigger onboarding workflow (async, don't wait for completion)
                        try:
                            from app.core.co_creator_onboarding import CoCreatorOnboardingService
                            onboarding_service = CoCreatorOnboardingService(self.db)
                            # Note: In production, this should be queued as a background task
                            # For now, we'll just mark it for onboarding
                            co_creator.add_metadata("onboarding_required", True)
                            co_creator.add_metadata("payment_completed_at", datetime.utcnow().isoformat())
                            self.db.commit()
                        except Exception as onboarding_error:
                            print(f"Failed to trigger onboarding for co-creator {transaction.co_creator_id}: {onboarding_error}")
                else:
                    # Log error but don't fail webhook
                    print(f"Failed to activate co-creator {transaction.co_creator_id}: {message}")
            
            self.db.commit()
            
            return True, "Payment succeeded webhook processed", {
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "co_creator_activated": co_creator_activated
            }
            
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to process payment succeeded: {str(e)}", None
    
    def _handle_payment_failed(
        self,
        payment_intent: Dict[str, Any],
        event_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Handle failed payment webhook"""
        try:
            transaction = PaymentTransaction.find_by_stripe_intent_id(
                self.db, payment_intent["id"]
            )
            
            if not transaction:
                return False, "Transaction not found", None
            
            # Mark payment as failed
            last_error = payment_intent.get("last_payment_error", {})
            transaction.mark_failed(
                failure_reason=last_error.get("message"),
                failure_code=last_error.get("code"),
                error_message=str(last_error)
            )
            transaction.process_webhook(event_id)
            
            # Release co-creator seat and send notification
            if transaction.co_creator_id:
                co_creator = self.db.query(CoCreator).filter(CoCreator.id == transaction.co_creator_id).first()
                self.co_creator_service.cancel_reservation(
                    transaction.co_creator_id, reason="payment_failed"
                )
                
                # Send payment failure notification
                if co_creator and transaction.receipt_email:
                    self.email_service.send_payment_failed_notification(
                        transaction.receipt_email, co_creator, transaction.failure_reason
                    )
            
            self.db.commit()
            
            return True, "Payment failed webhook processed", {
                "transaction_id": transaction.id,
                "failure_reason": transaction.failure_reason
            }
            
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to process payment failed: {str(e)}", None
    
    def _handle_payment_canceled(
        self,
        payment_intent: Dict[str, Any],
        event_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Handle canceled payment webhook"""
        try:
            transaction = PaymentTransaction.find_by_stripe_intent_id(
                self.db, payment_intent["id"]
            )
            
            if not transaction:
                return False, "Transaction not found", None
            
            # Mark payment as cancelled
            transaction.mark_cancelled()
            transaction.process_webhook(event_id)
            
            # Release co-creator seat if reserved
            if transaction.co_creator_id:
                self.co_creator_service.cancel_reservation(
                    transaction.co_creator_id, reason="payment_cancelled"
                )
            
            self.db.commit()
            
            return True, "Payment canceled webhook processed", {
                "transaction_id": transaction.id
            }
            
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to process payment canceled: {str(e)}", None
    
    def _handle_dispute_created(
        self,
        charge: Dict[str, Any],
        event_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Handle dispute created webhook"""
        try:
            # Find transaction by charge ID
            transaction = self.db.query(PaymentTransaction).filter(
                PaymentTransaction.stripe_charge_id == charge["id"]
            ).first()
            
            if not transaction:
                return False, "Transaction not found for dispute", None
            
            # Add dispute metadata
            transaction.add_metadata("dispute_created", True)
            transaction.add_metadata("dispute_reason", charge.get("dispute", {}).get("reason"))
            transaction.process_webhook(event_id)
            
            self.db.commit()
            
            return True, "Dispute created webhook processed", {
                "transaction_id": transaction.id,
                "dispute_reason": charge.get("dispute", {}).get("reason")
            }
            
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to process dispute: {str(e)}", None
    
    def create_co_creator_payment_intent(
        self,
        co_creator_id: int,
        customer_email: str,
        customer_name: str = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Create payment intent specifically for co-creator program
        """
        try:
            # Get co-creator details
            co_creator = self.db.query(CoCreator).filter(CoCreator.id == co_creator_id).first()
            if not co_creator:
                return False, "Co-creator not found", None
            
            program = co_creator.program
            if not program:
                return False, "Co-creator program not found", None
            
            # Create payment intent
            return self.create_payment_intent(
                amount=program.program_price,
                currency=program.currency.lower(),
                description=f"{program.program_name} - Seat #{co_creator.seat_number}",
                customer_email=customer_email,
                metadata={
                    "co_creator_id": str(co_creator_id),
                    "seat_number": str(co_creator.seat_number),
                    "program_id": str(program.id),
                    "customer_name": customer_name or ""
                },
                user_id=co_creator.user_id,
                lead_id=co_creator.lead_id,
                co_creator_id=co_creator_id
            )
            
        except Exception as e:
            return False, f"Failed to create co-creator payment intent: {str(e)}", None
    
    def get_payment_status(
        self,
        payment_intent_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Get current payment status from Stripe
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Update local transaction
            transaction = PaymentTransaction.find_by_stripe_intent_id(
                self.db, payment_intent_id
            )
            
            if transaction and transaction.status != intent.status:
                if intent.status == "succeeded":
                    transaction.mark_succeeded()
                elif intent.status in ["canceled", "payment_failed"]:
                    last_error = intent.last_payment_error
                    transaction.mark_failed(
                        failure_reason=last_error.message if last_error else "Payment failed",
                        failure_code=last_error.code if last_error else None
                    )
                
                self.db.commit()
            
            return True, "Payment status retrieved", {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency.upper(),
                "client_secret": intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            return False, f"Stripe error: {str(e)}", None
        except Exception as e:
            return False, f"Failed to get payment status: {str(e)}", None
    
    def process_refund(
        self,
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: str = "requested_by_customer"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process a refund for a payment
        """
        try:
            # Get the payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status != "succeeded":
                return False, "Payment not succeeded, cannot refund", None
            
            # Get the charge
            charge_id = intent.charges.data[0].id if intent.charges.data else None
            if not charge_id:
                return False, "No charge found for payment", None
            
            # Create refund
            refund_amount_cents = int(amount * 100) if amount else None
            refund = stripe.Refund.create(
                charge=charge_id,
                amount=refund_amount_cents,
                reason=reason
            )
            
            # Update local transaction
            transaction = PaymentTransaction.find_by_stripe_intent_id(
                self.db, payment_intent_id
            )
            
            if transaction:
                refund_amount_dollars = refund.amount / 100
                transaction.process_refund(
                    refund_amount=refund_amount_dollars,
                    reason=reason
                )
                
                # Deactivate co-creator if fully refunded
                if transaction.co_creator_id and refund_amount_dollars >= transaction.amount:
                    self.co_creator_service.cancel_reservation(
                        transaction.co_creator_id, reason="refunded"
                    )
                
                self.db.commit()
            
            return True, "Refund processed successfully", {
                "refund_id": refund.id,
                "amount": refund.amount / 100,
                "status": refund.status
            }
            
        except stripe.error.StripeError as e:
            return False, f"Stripe error: {str(e)}", None
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to process refund: {str(e)}", None