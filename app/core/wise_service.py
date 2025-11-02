"""
Wise payment service for Unitasa
Handles payment processing using Wise API
"""

import os
import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException

from app.core.config import get_settings
from app.models.payment_transaction import PaymentTransaction

settings = get_settings()


class WisePaymentService:
    """Wise payment processing service"""

    def __init__(self, db_session=None):
        self.db = db_session
        self.api_key = settings.wise.api_key
        self.profile_id = settings.wise.profile_id
        self.environment = settings.wise.environment

        # Wise API endpoints
        if self.environment == "live":
            self.base_url = "https://api.wise.com"
        else:
            self.base_url = "https://api.sandbox.transferwise.tech"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_payment_quote(self, amount: float, source_currency: str = "USD",
                                 target_currency: str = "USD") -> Dict[str, Any]:
        """Create a Wise payment quote"""
        try:
            async with httpx.AsyncClient() as client:
                quote_data = {
                    "sourceCurrency": source_currency,
                    "targetCurrency": target_currency,
                    "sourceAmount": amount,
                    "profile": self.profile_id
                }

                response = await client.post(
                    f"{self.base_url}/v3/quotes",
                    headers=self.headers,
                    json=quote_data
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Wise quote creation failed: {response.text}"
                    )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Wise API error: {str(e)}")

    async def create_recipient(self, recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Wise recipient"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/accounts",
                    headers=self.headers,
                    json=recipient_data
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Wise recipient creation failed: {response.text}"
                    )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Wise API error: {str(e)}")

    async def create_transfer(self, quote_id: str, recipient_id: str,
                            reference: str = "Co-Creator Program Payment") -> Dict[str, Any]:
        """Create a Wise transfer"""
        try:
            async with httpx.AsyncClient() as client:
                transfer_data = {
                    "targetAccount": recipient_id,
                    "quoteUuid": quote_id,
                    "customerTransactionId": reference,
                    "details": {
                        "referenceText": reference
                    }
                }

                response = await client.post(
                    f"{self.base_url}/v1/transfers",
                    headers=self.headers,
                    json=transfer_data
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Wise transfer creation failed: {response.text}"
                    )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Wise API error: {str(e)}")

    async def fund_transfer(self, transfer_id: str) -> Dict[str, Any]:
        """Fund a Wise transfer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v3/profiles/{self.profile_id}/transfers/{transfer_id}/payments",
                    headers=self.headers,
                    json={"type": "BALANCE"}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Wise transfer funding failed: {response.text}"
                    )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Wise API error: {str(e)}")

    async def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Get Wise transfer status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/transfers/{transfer_id}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Wise transfer status check failed: {response.text}"
                    )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Wise API error: {str(e)}")

    async def create_co_creator_payment(self, co_creator_id: int, customer_email: str,
                                      customer_name: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Create a Wise payment for co-creator program"""
        try:
            # Get co-creator details (simplified - you'd get this from database)
            # For now, create a basic recipient
            recipient_data = {
                "currency": "USD",
                "type": "email",
                "profile": self.profile_id,
                "accountHolderName": customer_name or "Co-Creator",
                "details": {
                    "email": customer_email
                }
            }

            # Create recipient
            recipient = await self.create_recipient(recipient_data)

            # Create quote for $250 payment
            quote = await self.create_payment_quote(amount=250.0)

            # Create transfer
            transfer = await self.create_transfer(
                quote_id=quote["id"],
                recipient_id=recipient["id"],
                reference=f"Co-Creator Program - {customer_email}"
            )

            # Fund transfer
            funding = await self.fund_transfer(transfer["id"])

            # Create local transaction record
            transaction = PaymentTransaction(
                wise_transfer_id=transfer["id"],
                amount=250.0,
                currency="USD",
                status="processing",
                description="Co-Creator Program Payment",
                co_creator_id=co_creator_id,
                payment_metadata={
                    "wise_quote_id": quote["id"],
                    "wise_recipient_id": recipient["id"],
                    "funding_id": funding.get("id")
                }
            )

            if self.db:
                self.db.add(transaction)
                await self.db.commit()

            return True, "Payment initiated successfully", {
                "transfer_id": transfer["id"],
                "quote_id": quote["id"],
                "recipient_id": recipient["id"],
                "amount": 250.0,
                "currency": "USD"
            }

        except Exception as e:
            return False, f"Wise payment error: {str(e)}", None

    async def get_payment_status(self, transfer_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Get payment status from Wise"""
        try:
            transfer = await self.get_transfer_status(transfer_id)

            status = transfer.get("status", "unknown")

            # Map Wise status to our status
            if status == "outgoing_payment_sent":
                payment_status = "completed"
            elif status in ["processing", "funds_converted"]:
                payment_status = "processing"
            elif status == "cancelled":
                payment_status = "cancelled"
            else:
                payment_status = "pending"

            return True, "Status retrieved successfully", {
                "transfer_id": transfer_id,
                "status": payment_status,
                "wise_status": status,
                "details": transfer
            }

        except Exception as e:
            return False, f"Status check error: {str(e)}", None

    async def process_webhook_event(self, payload: str, signature: str,
                                  endpoint_secret: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Process Wise webhook events"""
        try:
            # Verify webhook signature (simplified - you'd implement proper verification)
            if signature != endpoint_secret:
                return False, "Invalid webhook signature", None

            event_data = json.loads(payload)

            # Handle different event types
            event_type = event_data.get("event_type")
            transfer_id = event_data.get("data", {}).get("resource", {}).get("id")

            if event_type == "transfers#state-change" and transfer_id:
                # Update local transaction status
                if self.db:
                    transaction = self.db.query(PaymentTransaction).filter(
                        PaymentTransaction.wise_transfer_id == transfer_id
                    ).first()

                    if transaction:
                        wise_status = event_data.get("data", {}).get("current_state")
                        if wise_status == "outgoing_payment_sent":
                            transaction.status = "completed"
                            transaction.processed_at = datetime.utcnow()
                        elif wise_status == "cancelled":
                            transaction.status = "cancelled"

                        await self.db.commit()

            return True, "Webhook processed successfully", event_data

        except Exception as e:
            return False, f"Webhook processing error: {str(e)}", None