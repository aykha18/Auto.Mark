"""
Mock Wise payment service for testing without valid API credentials
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


class MockWisePaymentService:
    """Mock Wise payment service for testing"""

    def __init__(self, db_session=None):
        self.db = db_session
        self.api_key = settings.wise.api_key or "mock_api_key"
        self.profile_id = settings.wise.profile_id or "mock_profile_123"
        self.environment = "sandbox_mock"
        self.base_url = "https://api.sandbox.transferwise.tech"

    async def create_payment_quote(self, amount: float, source_currency: str = "USD",
                                 target_currency: str = "USD") -> Dict[str, Any]:
        """Create a mock payment quote"""
        quote_id = str(uuid.uuid4())
        
        # Simulate quote creation
        quote = {
            "id": quote_id,
            "sourceCurrency": source_currency,
            "targetCurrency": target_currency,
            "sourceAmount": amount,
            "targetAmount": amount * 0.995,  # Mock 0.5% fee
            "rate": 1.0,
            "fee": amount * 0.005,
            "profile": self.profile_id,
            "createdTime": datetime.utcnow().isoformat(),
            "expirationTime": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        return quote

    async def create_recipient(self, recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock recipient"""
        recipient_id = str(uuid.uuid4())
        
        recipient = {
            "id": recipient_id,
            "currency": recipient_data.get("currency", "USD"),
            "type": recipient_data.get("type", "email"),
            "profile": self.profile_id,
            "accountHolderName": recipient_data.get("accountHolderName", "Mock Recipient"),
            "details": recipient_data.get("details", {}),
            "createdTime": datetime.utcnow().isoformat()
        }
        
        return recipient

    async def create_transfer(self, quote_id: str, recipient_id: str,
                            reference: str = "Co-Creator Program Payment") -> Dict[str, Any]:
        """Create a mock transfer"""
        transfer_id = str(uuid.uuid4())
        
        transfer = {
            "id": transfer_id,
            "user": 12345,
            "targetAccount": recipient_id,
            "sourceAccount": None,
            "quote": quote_id,
            "status": "incoming_payment_waiting",
            "reference": reference,
            "rate": 1.0,
            "created": datetime.utcnow().isoformat(),
            "business": self.profile_id,
            "transferRequest": None,
            "details": {
                "reference": reference
            },
            "hasActiveIssues": False,
            "sourceCurrency": "USD",
            "sourceValue": 250.0,
            "targetCurrency": "USD",
            "targetValue": 249.0,
            "customerTransactionId": reference
        }
        
        return transfer

    async def fund_transfer(self, transfer_id: str) -> Dict[str, Any]:
        """Mock transfer funding"""
        funding = {
            "id": str(uuid.uuid4()),
            "type": "BALANCE",
            "status": "COMPLETED",
            "balanceId": str(uuid.uuid4()),
            "createdTime": datetime.utcnow().isoformat()
        }
        
        return funding

    async def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Get mock transfer status"""
        # Simulate different statuses for testing
        import random
        
        statuses = [
            "incoming_payment_waiting",
            "processing",
            "funds_converted", 
            "outgoing_payment_sent"
        ]
        
        # 70% chance of completion for testing
        if random.random() < 0.7:
            status = "outgoing_payment_sent"
        else:
            status = random.choice(statuses[:-1])
        
        transfer = {
            "id": transfer_id,
            "status": status,
            "sourceCurrency": "USD",
            "sourceValue": 250.0,
            "targetCurrency": "USD", 
            "targetValue": 249.0,
            "rate": 1.0,
            "created": datetime.utcnow().isoformat(),
            "business": self.profile_id,
            "hasActiveIssues": False
        }
        
        return transfer

    async def create_co_creator_payment(self, co_creator_id: int, customer_email: str,
                                      customer_name: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Create a mock co-creator payment"""
        try:
            print(f"🧪 Mock: Creating payment for {customer_email}")
            
            # Create mock recipient
            recipient_data = {
                "currency": "USD",
                "type": "email",
                "profile": self.profile_id,
                "accountHolderName": customer_name or "Co-Creator",
                "details": {
                    "email": customer_email
                }
            }
            
            recipient = await self.create_recipient(recipient_data)
            print(f"🧪 Mock: Created recipient {recipient['id']}")
            
            # Create mock quote
            quote = await self.create_payment_quote(amount=497.0)
            print(f"🧪 Mock: Created quote {quote['id']}")
            
            # Create mock transfer
            transfer = await self.create_transfer(
                quote_id=quote["id"],
                recipient_id=recipient["id"],
                reference=f"Co-Creator Program - {customer_email}"
            )
            print(f"🧪 Mock: Created transfer {transfer['id']}")
            
            # Mock funding
            funding = await self.fund_transfer(transfer["id"])
            print(f"🧪 Mock: Funded transfer {funding['id']}")
            
            return True, "Mock payment initiated successfully", {
                "transfer_id": transfer["id"],
                "quote_id": quote["id"],
                "recipient_id": recipient["id"],
                "amount": 497.0,
                "currency": "USD",
                "status": "processing",
                "mock": True
            }

        except Exception as e:
            return False, f"Mock payment error: {str(e)}", None

    async def get_payment_status(self, transfer_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Get mock payment status"""
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

            return True, "Mock status retrieved successfully", {
                "transfer_id": transfer_id,
                "status": payment_status,
                "wise_status": status,
                "details": transfer,
                "mock": True
            }

        except Exception as e:
            return False, f"Mock status check error: {str(e)}", None

    async def process_webhook_event(self, payload: str, signature: str,
                                  endpoint_secret: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Process mock webhook events"""
        try:
            event_data = json.loads(payload)
            
            # Handle different event types
            event_type = event_data.get("event_type")
            transfer_id = event_data.get("data", {}).get("resource", {}).get("id")

            if event_type == "transfers#state-change" and transfer_id:
                return True, "Mock webhook processed successfully", {
                    **event_data,
                    "mock": True
                }
            else:
                return True, "Mock unknown event processed", {
                    "event_type": event_type,
                    "mock": True
                }

        except Exception as e:
            return False, f"Mock webhook processing error: {str(e)}", None


# Factory function to choose between real and mock service
def get_wise_service(db_session=None, use_mock=None):
    """Get Wise service (real or mock based on configuration)"""
    
    # Auto-detect if we should use mock based on API key validity
    if use_mock is None:
        api_key = settings.wise.api_key
        # Use mock if no API key or if it's obviously a placeholder
        use_mock = (
            not api_key or 
            api_key in ["", "your_wise_sandbox_api_token_here", "mock_api_key"] or
            len(api_key) < 10
        )
    
    if use_mock:
        print("🧪 Using Mock Wise Service for testing")
        return MockWisePaymentService(db_session)
    else:
        print("🔗 Using Real Wise Service")
        from app.core.wise_service import WisePaymentService
        return WisePaymentService(db_session)