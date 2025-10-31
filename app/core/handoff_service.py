"""
Human Handoff Service for Chat System
Manages escalation from AI to human support agents
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.chat_session import ChatSession, ChatMessage
from app.models.lead import Lead
from app.models.user import User
from app.agents.stubs import get_communicator, AgentMessage


class HandoffService:
    """Service for managing chat handoffs to human agents"""

    def __init__(self, db: Session):
        self.db = db
        self.communicator = get_communicator()
        
        # Handoff priority levels
        self.priority_levels = {
            "high_value_lead": 1,      # Highest priority
            "enterprise_inquiry": 2,
            "technical_complexity": 3,
            "payment_issue": 2,
            "general_escalation": 4    # Lowest priority
        }

    async def request_handoff(self, 
                            session_id: str, 
                            reason: str,
                            priority: str = "medium",
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Request human handoff for a chat session
        
        Args:
            session_id: Chat session ID
            reason: Reason for handoff
            priority: Priority level (high, medium, low)
            context: Additional context for human agent
            
        Returns:
            Handoff request result
        """
        try:
            # Get chat session
            session = self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                return {
                    "success": False,
                    "error": "Chat session not found"
                }
            
            # Check if already requested
            if session.requires_human_handoff:
                return {
                    "success": False,
                    "error": "Handoff already requested for this session",
                    "existing_reason": session.handoff_reason
                }
            
            # Update session with handoff request
            session.request_handoff(reason)
            
            # Create handoff context
            handoff_context = {
                "session_id": session_id,
                "reason": reason,
                "priority": priority,
                "qualification_score": session.qualification_score,
                "crm_interest_level": session.crm_interest_level,
                "identified_crm": session.identified_crm,
                "pain_points": session.pain_points,
                "session_duration": session.duration_minutes,
                "total_messages": session.total_messages,
                "lead_id": session.lead_id,
                "user_id": session.user_id,
                "additional_context": context or {}
            }
            
            # Get conversation summary
            conversation_summary = await self._generate_conversation_summary(session.id)
            handoff_context["conversation_summary"] = conversation_summary
            
            # Notify human agents via communication system
            await self._notify_human_agents(handoff_context)
            
            # Log handoff request
            await self._log_handoff_request(session_id, reason, handoff_context)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Handoff requested successfully",
                "session_id": session_id,
                "reason": reason,
                "priority": priority,
                "estimated_response_time": self._get_estimated_response_time(reason)
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to request handoff: {str(e)}"
            }

    async def _generate_conversation_summary(self, session_db_id: int) -> str:
        """Generate a summary of the conversation for human agents"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_db_id
        ).order_by(ChatMessage.timestamp.asc()).limit(20).all()
        
        if not messages:
            return "No conversation history available."
        
        # Create a concise summary
        summary_parts = []
        user_messages = [m for m in messages if m.sender == "user"]
        agent_messages = [m for m in messages if m.sender == "agent"]
        
        summary_parts.append(f"Conversation with {len(user_messages)} user messages and {len(agent_messages)} AI responses.")
        
        # Key topics mentioned
        all_content = " ".join([m.content for m in messages])
        key_topics = []
        
        topic_keywords = {
            "CRM Integration": ["crm", "integration", "connect", "sync"],
            "Pricing": ["price", "cost", "$497", "co-creator", "payment", "founder", "discount"],
            "Technical": ["api", "technical", "developer", "webhook"],
            "Assessment": ["assessment", "questions", "score", "readiness"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_content.lower() for keyword in keywords):
                key_topics.append(topic)
        
        if key_topics:
            summary_parts.append(f"Key topics discussed: {', '.join(key_topics)}")
        
        # Recent messages (last 3 exchanges)
        recent_messages = messages[-6:] if len(messages) >= 6 else messages
        if recent_messages:
            summary_parts.append("Recent conversation:")
            for msg in recent_messages:
                role = "User" if msg.sender == "user" else "AI"
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                summary_parts.append(f"  {role}: {content}")
        
        return "\n".join(summary_parts)

    async def _notify_human_agents(self, handoff_context: Dict[str, Any]):
        """Notify available human agents about handoff request"""
        # Create notification message
        notification = AgentMessage(
            sender="handoff_service",
            receiver="human_agents",
            message_type="handoff_request",
            payload=handoff_context
        )
        
        # Send via communication system
        await self.communicator.send_message(notification)
        
        # TODO: In production, also send via:
        # - Slack/Teams notification
        # - Email alert for high priority
        # - SMS for urgent cases
        # - Dashboard notification

    async def _log_handoff_request(self, session_id: str, reason: str, context: Dict[str, Any]):
        """Log handoff request for analytics"""
        # Create system message in chat
        session = self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if session:
            system_message = ChatMessage(
                session_id=session.id,
                message_id=str(uuid.uuid4()),
                content=f"Handoff requested: {reason}",
                message_type="system",
                sender="system",
                intent="handoff_request"
            )
            
            self.db.add(system_message)

    def _get_estimated_response_time(self, reason: str) -> str:
        """Get estimated response time based on handoff reason"""
        response_times = {
            "high_value_lead": "5-10 minutes",
            "enterprise_inquiry": "10-15 minutes", 
            "technical_complexity": "15-30 minutes",
            "payment_issue": "10-15 minutes",
            "general_escalation": "30-60 minutes"
        }
        
        return response_times.get(reason, "30-60 minutes")

    def get_handoff_queue(self, 
                         priority_filter: Optional[str] = None,
                         limit: int = 50) -> List[Dict[str, Any]]:
        """Get current handoff queue for human agents"""
        query = self.db.query(ChatSession).filter(
            and_(
                ChatSession.requires_human_handoff == True,
                ChatSession.status == "active"
            )
        )
        
        # Sort by priority and request time
        sessions = query.order_by(
            ChatSession.handoff_requested_at.desc()
        ).limit(limit).all()
        
        queue = []
        for session in sessions:
            # Calculate priority score
            priority_score = self.priority_levels.get(session.handoff_reason, 5)
            
            # Calculate wait time
            wait_time_minutes = 0
            if session.handoff_requested_at:
                wait_time_minutes = (datetime.utcnow() - session.handoff_requested_at).total_seconds() / 60
            
            queue_item = {
                "session_id": session.session_id,
                "handoff_reason": session.handoff_reason,
                "priority_score": priority_score,
                "wait_time_minutes": round(wait_time_minutes, 1),
                "qualification_score": session.qualification_score,
                "crm_interest_level": session.crm_interest_level,
                "identified_crm": session.identified_crm,
                "total_messages": session.total_messages,
                "session_duration": session.duration_minutes,
                "lead_id": session.lead_id,
                "handoff_requested_at": session.handoff_requested_at
            }
            
            # Add lead information if available
            if session.lead_id:
                lead = self.db.query(Lead).filter(Lead.id == session.lead_id).first()
                if lead:
                    queue_item["lead_info"] = {
                        "email": lead.email,
                        "company": lead.company,
                        "full_name": lead.full_name,
                        "crm_readiness": lead.crm_integration_readiness
                    }
            
            queue.append(queue_item)
        
        # Sort by priority score (lower = higher priority) and wait time
        queue.sort(key=lambda x: (x["priority_score"], -x["wait_time_minutes"]))
        
        return queue

    async def assign_to_human_agent(self, 
                                  session_id: str, 
                                  agent_id: str,
                                  agent_name: str) -> Dict[str, Any]:
        """Assign a handoff session to a human agent"""
        try:
            session = self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                return {
                    "success": False,
                    "error": "Chat session not found"
                }
            
            if not session.requires_human_handoff:
                return {
                    "success": False,
                    "error": "Session does not require handoff"
                }
            
            # Update session status
            session.status = "transferred"
            session.add_context("assigned_agent_id", agent_id)
            session.add_context("assigned_agent_name", agent_name)
            session.add_context("assignment_time", datetime.utcnow().isoformat())
            
            # Create system message
            system_message = ChatMessage(
                session_id=session.id,
                message_id=str(uuid.uuid4()),
                content=f"Chat transferred to {agent_name}",
                message_type="system",
                sender="system",
                intent="agent_assignment"
            )
            
            self.db.add(system_message)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Session assigned to {agent_name}",
                "session_id": session_id,
                "agent_id": agent_id,
                "agent_name": agent_name
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to assign session: {str(e)}"
            }

    def get_handoff_analytics(self, 
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get analytics on handoff requests and resolution"""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get handoff sessions in date range
        handoff_sessions = self.db.query(ChatSession).filter(
            and_(
                ChatSession.requires_human_handoff == True,
                ChatSession.handoff_requested_at >= start_date,
                ChatSession.handoff_requested_at <= end_date
            )
        ).all()
        
        total_handoffs = len(handoff_sessions)
        
        # Analyze by reason
        reason_counts = {}
        for session in handoff_sessions:
            reason = session.handoff_reason or "unknown"
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        # Calculate average wait times
        wait_times = []
        resolved_count = 0
        
        for session in handoff_sessions:
            if session.status == "transferred" and session.handoff_requested_at:
                assignment_time_str = session.get_context("assignment_time")
                if assignment_time_str:
                    try:
                        assignment_time = datetime.fromisoformat(assignment_time_str)
                        wait_time = (assignment_time - session.handoff_requested_at).total_seconds() / 60
                        wait_times.append(wait_time)
                        resolved_count += 1
                    except:
                        pass
        
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_handoff_requests": total_handoffs,
            "resolved_handoffs": resolved_count,
            "pending_handoffs": total_handoffs - resolved_count,
            "resolution_rate": (resolved_count / total_handoffs * 100) if total_handoffs > 0 else 0,
            "average_wait_time_minutes": round(avg_wait_time, 2),
            "handoff_reasons": reason_counts,
            "top_handoff_reason": max(reason_counts.items(), key=lambda x: x[1])[0] if reason_counts else None
        }


# Global handoff service instance per database session
def get_handoff_service(db: Session) -> HandoffService:
    """Get handoff service instance"""
    return HandoffService(db)
