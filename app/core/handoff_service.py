"""
Handoff Service for managing human agent handoffs
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class HandoffService:
    """Service for managing chat handoffs to human agents"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    async def request_handoff(self, 
                            session_id: str, 
                            reason: str = "user_requested",
                            priority: str = "normal") -> Dict[str, Any]:
        """
        Request a handoff to a human agent
        """
        try:
            self.logger.info(f"Handoff requested for session {session_id}: {reason}")
            
            # In production, this would:
            # 1. Update the chat session status
            # 2. Notify available human agents
            # 3. Queue the session for assignment
            # 4. Send notifications via email/Slack/etc.
            
            # Mock response
            return {
                "success": True,
                "handoff_id": f"handoff_{session_id}_{int(datetime.utcnow().timestamp())}",
                "session_id": session_id,
                "reason": reason,
                "priority": priority,
                "status": "queued",
                "estimated_response_time": "5-10 minutes",
                "queue_position": 2,
                "message": "Your request has been queued for a human agent. Expected response time: 5-10 minutes."
            }
            
        except Exception as e:
            self.logger.error(f"Handoff request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to request human agent. Please try again."
            }
    
    async def assign_agent(self, 
                         session_id: str, 
                         agent_id: str, 
                         agent_name: str) -> Dict[str, Any]:
        """
        Assign a human agent to a session
        """
        try:
            self.logger.info(f"Assigning agent {agent_name} to session {session_id}")
            
            # In production, this would:
            # 1. Update the session with agent info
            # 2. Notify the customer
            # 3. Set up agent dashboard access
            # 4. Start tracking agent response times
            
            return {
                "success": True,
                "session_id": session_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "assigned_at": datetime.utcnow().isoformat(),
                "message": f"You've been connected to {agent_name}"
            }
            
        except Exception as e:
            self.logger.error(f"Agent assignment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to assign agent. Please try again."
            }
    
    def get_handoff_queue(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get sessions waiting for human handoff
        """
        try:
            # Mock queue data
            # In production, this would query the database for sessions
            # with status = "handoff_requested" or similar
            
            mock_queue = [
                {
                    "session_id": "session_123",
                    "requested_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "reason": "complex_technical_question",
                    "priority": "high",
                    "customer_info": {
                        "name": "John Doe",
                        "email": "john@example.com",
                        "company": "Tech Corp"
                    },
                    "wait_time_minutes": 5
                },
                {
                    "session_id": "session_456",
                    "requested_at": (datetime.utcnow() - timedelta(minutes=12)).isoformat(),
                    "reason": "pricing_inquiry",
                    "priority": "normal",
                    "customer_info": {
                        "name": "Jane Smith",
                        "email": "jane@example.com",
                        "company": "Business Inc"
                    },
                    "wait_time_minutes": 12
                }
            ]
            
            return mock_queue[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get handoff queue: {e}")
            return []
    
    def get_handoff_analytics(self, 
                            start_date: datetime, 
                            end_date: datetime) -> Dict[str, Any]:
        """
        Get handoff analytics and metrics
        """
        try:
            # Mock analytics data
            # In production, this would calculate real metrics from the database
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "handoff_metrics": {
                    "total_handoffs": 45,
                    "successful_handoffs": 42,
                    "failed_handoffs": 3,
                    "success_rate": 93.3,
                    "average_wait_time_minutes": 8.5,
                    "average_resolution_time_minutes": 25.2
                },
                "handoff_reasons": {
                    "complex_technical_question": 18,
                    "pricing_inquiry": 12,
                    "user_requested": 8,
                    "escalation_required": 5,
                    "billing_issue": 2
                },
                "agent_performance": {
                    "total_agents": 5,
                    "active_agents": 3,
                    "average_sessions_per_agent": 9,
                    "customer_satisfaction": 4.2
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get handoff analytics: {e}")
            return {}


# Global handoff service instances
_handoff_services = {}


def get_handoff_service(db: Session) -> HandoffService:
    """Get a handoff service instance for the given database session"""
    # Create a new instance for each database session to avoid sharing state
    return HandoffService(db)