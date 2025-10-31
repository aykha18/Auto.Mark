"""
Chat Monitoring Service
Tracks chat performance, agent effectiveness, and system health
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.chat_session import ChatSession, ChatMessage
from app.models.lead import Lead
from app.agents.monitoring import record_agent_execution


class ChatMonitoringService:
    """Service for monitoring chat system performance and health"""

    def __init__(self, db: Session):
        self.db = db

    async def record_chat_interaction(self,
                                    session_id: str,
                                    interaction_type: str,
                                    processing_time_ms: int,
                                    success: bool,
                                    metadata: Dict[str, Any] = None):
        """Record a chat interaction for monitoring"""
        try:
            await record_agent_execution(
                agent_name="conversational_agent",
                execution_time=processing_time_ms / 1000,
                success=success,
                metadata={
                    "session_id": session_id,
                    "interaction_type": interaction_type,
                    **(metadata or {})
                }
            )
        except Exception as e:
            # Don't fail the main operation if monitoring fails
            print(f"Failed to record chat interaction: {e}")

    def get_chat_performance_metrics(self,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive chat performance metrics"""
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)  # Last 7 days

        # Base queries for the time period
        sessions_query = self.db.query(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date
            )
        )
        
        messages_query = self.db.query(ChatMessage).join(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date
            )
        )

        # Session metrics
        total_sessions = sessions_query.count()
        active_sessions = sessions_query.filter(ChatSession.status == "active").count()
        ended_sessions = sessions_query.filter(ChatSession.status == "ended").count()
        transferred_sessions = sessions_query.filter(ChatSession.status == "transferred").count()

        # Message metrics
        total_messages = messages_query.count()
        user_messages = messages_query.filter(ChatMessage.sender == "user").count()
        agent_messages = messages_query.filter(ChatMessage.sender == "agent").count()

        # Response time metrics
        agent_messages_with_time = messages_query.filter(
            and_(
                ChatMessage.sender == "agent",
                ChatMessage.response_time_ms.isnot(None)
            )
        ).all()

        response_times = [msg.response_time_ms for msg in agent_messages_with_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0

        # Session duration metrics
        completed_sessions = sessions_query.filter(
            ChatSession.session_duration_seconds.isnot(None)
        ).all()

        durations = [s.session_duration_seconds for s in completed_sessions]
        avg_session_duration = sum(durations) / len(durations) if durations else 0

        # Qualification metrics
        qualified_sessions = sessions_query.filter(
            ChatSession.qualification_score >= 50
        ).count()

        high_value_sessions = sessions_query.filter(
            ChatSession.qualification_score >= 80
        ).count()

        # Handoff metrics
        handoff_sessions = sessions_query.filter(
            ChatSession.requires_human_handoff == True
        ).count()

        # CRM interest distribution
        crm_interest_dist = self.db.query(
            ChatSession.crm_interest_level,
            func.count(ChatSession.id)
        ).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date,
                ChatSession.crm_interest_level.isnot(None)
            )
        ).group_by(ChatSession.crm_interest_level).all()

        # Voice message metrics
        voice_messages = messages_query.filter(
            ChatMessage.message_type == "voice"
        ).count()

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": (end_date - start_date).days
            },
            "session_metrics": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "ended_sessions": ended_sessions,
                "transferred_sessions": transferred_sessions,
                "avg_session_duration_seconds": round(avg_session_duration, 2),
                "completion_rate": (ended_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            "message_metrics": {
                "total_messages": total_messages,
                "user_messages": user_messages,
                "agent_messages": agent_messages,
                "voice_messages": voice_messages,
                "avg_messages_per_session": round(total_messages / total_sessions, 2) if total_sessions > 0 else 0,
                "voice_message_rate": (voice_messages / total_messages * 100) if total_messages > 0 else 0
            },
            "performance_metrics": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": min_response_time,
                "max_response_time_ms": max_response_time,
                "response_time_sla_met": (avg_response_time <= 3000) if avg_response_time > 0 else True  # 3 second SLA
            },
            "qualification_metrics": {
                "qualified_sessions": qualified_sessions,
                "qualification_rate": (qualified_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "high_value_sessions": high_value_sessions,
                "high_value_rate": (high_value_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            "handoff_metrics": {
                "handoff_requests": handoff_sessions,
                "handoff_rate": (handoff_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "transfer_rate": (transferred_sessions / handoff_sessions * 100) if handoff_sessions > 0 else 0
            },
            "crm_interest_distribution": {
                level: count for level, count in crm_interest_dist
            }
        }

    def get_agent_effectiveness_metrics(self,
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get metrics on conversational agent effectiveness"""
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)

        # Get sessions with lead associations
        sessions_with_leads = self.db.query(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date,
                ChatSession.lead_id.isnot(None)
            )
        ).all()

        # Analyze lead progression
        lead_improvements = 0
        total_lead_sessions = len(sessions_with_leads)

        for session in sessions_with_leads:
            if session.lead_id:
                lead = self.db.query(Lead).filter(Lead.id == session.lead_id).first()
                if lead and session.qualification_score > 0:
                    # Check if chat improved lead qualification
                    if lead.crm_integration_readiness >= session.qualification_score:
                        lead_improvements += 1

        # Intent recognition accuracy (mock calculation)
        messages_with_intent = self.db.query(ChatMessage).join(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date,
                ChatMessage.intent.isnot(None),
                ChatMessage.sender == "user"
            )
        ).all()

        # Intent distribution
        intent_counts = {}
        for msg in messages_with_intent:
            intent = msg.intent
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        # Conversation completion rate
        sessions_query = self.db.query(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date
            )
        )

        total_sessions = sessions_query.count()
        completed_conversations = sessions_query.filter(
            ChatSession.total_messages >= 3  # At least 3 messages indicates engagement
        ).count()

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "lead_qualification": {
                "sessions_with_leads": total_lead_sessions,
                "lead_improvements": lead_improvements,
                "improvement_rate": (lead_improvements / total_lead_sessions * 100) if total_lead_sessions > 0 else 0
            },
            "conversation_quality": {
                "total_sessions": total_sessions,
                "completed_conversations": completed_conversations,
                "completion_rate": (completed_conversations / total_sessions * 100) if total_sessions > 0 else 0,
                "avg_messages_per_completed": round(
                    sum(s.total_messages for s in sessions_query.filter(ChatSession.total_messages >= 3).all()) / 
                    completed_conversations, 2
                ) if completed_conversations > 0 else 0
            },
            "intent_recognition": {
                "messages_with_intent": len(messages_with_intent),
                "intent_distribution": intent_counts,
                "top_intent": max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
            }
        }

    def get_system_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        
        # Check recent performance (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        recent_sessions = self.db.query(ChatSession).filter(
            ChatSession.started_at >= one_hour_ago
        ).count()

        recent_messages = self.db.query(ChatMessage).join(ChatSession).filter(
            ChatSession.started_at >= one_hour_ago
        ).count()

        # Check for any error patterns
        recent_errors = self.db.query(ChatMessage).join(ChatSession).filter(
            and_(
                ChatSession.started_at >= one_hour_ago,
                ChatMessage.content.like("%error%")
            )
        ).count()

        # Calculate health score
        health_score = 100
        
        # Deduct points for high error rate
        if recent_messages > 0:
            error_rate = (recent_errors / recent_messages) * 100
            if error_rate > 5:  # More than 5% errors
                health_score -= min(30, error_rate * 2)

        # Check response times
        recent_agent_messages = self.db.query(ChatMessage).join(ChatSession).filter(
            and_(
                ChatSession.started_at >= one_hour_ago,
                ChatMessage.sender == "agent",
                ChatMessage.response_time_ms.isnot(None)
            )
        ).all()

        if recent_agent_messages:
            avg_response_time = sum(msg.response_time_ms for msg in recent_agent_messages) / len(recent_agent_messages)
            if avg_response_time > 5000:  # More than 5 seconds
                health_score -= 20
            elif avg_response_time > 3000:  # More than 3 seconds
                health_score -= 10

        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "health_score": health_score,
            "timestamp": datetime.utcnow().isoformat(),
            "recent_activity": {
                "sessions_last_hour": recent_sessions,
                "messages_last_hour": recent_messages,
                "error_count": recent_errors,
                "error_rate": (recent_errors / recent_messages * 100) if recent_messages > 0 else 0
            },
            "performance": {
                "avg_response_time_ms": round(
                    sum(msg.response_time_ms for msg in recent_agent_messages) / len(recent_agent_messages), 2
                ) if recent_agent_messages else 0,
                "response_time_sla_met": avg_response_time <= 3000 if recent_agent_messages else True
            }
        }

    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily summary of chat activity"""
        
        if not date:
            date = datetime.utcnow().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)

        metrics = self.get_chat_performance_metrics(start_date, end_date)
        effectiveness = self.get_agent_effectiveness_metrics(start_date, end_date)

        return {
            "date": date.isoformat(),
            "summary": {
                "total_sessions": metrics["session_metrics"]["total_sessions"],
                "total_messages": metrics["message_metrics"]["total_messages"],
                "qualification_rate": metrics["qualification_metrics"]["qualification_rate"],
                "handoff_rate": metrics["handoff_metrics"]["handoff_rate"],
                "avg_response_time_ms": metrics["performance_metrics"]["avg_response_time_ms"],
                "completion_rate": effectiveness["conversation_quality"]["completion_rate"]
            },
            "highlights": {
                "high_value_sessions": metrics["qualification_metrics"]["high_value_sessions"],
                "voice_messages": metrics["message_metrics"]["voice_messages"],
                "top_crm_interest": max(
                    metrics["crm_interest_distribution"].items(), 
                    key=lambda x: x[1]
                )[0] if metrics["crm_interest_distribution"] else None
            }
        }


def get_chat_monitoring_service(db: Session) -> ChatMonitoringService:
    """Get chat monitoring service instance"""
    return ChatMonitoringService(db)
