"""
Chat session model for conversational AI agent system
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    """Chat session model for tracking conversational AI interactions"""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)  # UUID for session
    
    # User/Lead association
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Session metadata
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    referrer = Column(String(500))
    
    # Session state
    status = Column(String(50), default="active")  # active, ended, transferred
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Conversation context
    conversation_context = Column(JSON, default=dict)  # Persistent context
    current_topic = Column(String(255))  # Current conversation topic
    intent = Column(String(100))  # Detected user intent
    
    # Lead qualification data
    qualification_score = Column(Float, default=0.0)  # Real-time qualification score
    crm_interest_level = Column(String(50))  # low, medium, high
    identified_crm = Column(String(100))  # Identified CRM system
    pain_points = Column(JSON, default=list)  # Identified pain points
    
    # Handoff and escalation
    requires_human_handoff = Column(Boolean, default=False)
    handoff_reason = Column(String(255))
    handoff_requested_at = Column(DateTime, nullable=True)
    
    # Analytics
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    agent_messages = Column(Integer, default=0)
    session_duration_seconds = Column(Integer, default=0)
    
    # Relationships
    lead = relationship("Lead", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def end_session(self, reason: str = "user_ended"):
        """End the chat session"""
        self.status = "ended"
        self.ended_at = datetime.utcnow()
        if self.started_at:
            self.session_duration_seconds = int((self.ended_at - self.started_at).total_seconds())
        self.updated_at = datetime.utcnow()

    def request_handoff(self, reason: str):
        """Request human handoff"""
        self.requires_human_handoff = True
        self.handoff_reason = reason
        self.handoff_requested_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_qualification_data(self, score: float, crm_interest: str, identified_crm: str = None, pain_points: List[str] = None):
        """Update lead qualification data from conversation"""
        self.qualification_score = max(0.0, min(100.0, score))
        self.crm_interest_level = crm_interest
        if identified_crm:
            self.identified_crm = identified_crm
        if pain_points:
            self.pain_points = pain_points
        self.updated_at = datetime.utcnow()

    def add_context(self, key: str, value: Any):
        """Add context to conversation"""
        if not self.conversation_context:
            self.conversation_context = {}
        self.conversation_context[key] = value
        self.updated_at = datetime.utcnow()

    def get_context(self, key: str, default=None):
        """Get context value"""
        if not self.conversation_context:
            return default
        return self.conversation_context.get(key, default)

    def increment_message_count(self, is_user_message: bool = True):
        """Increment message counters"""
        self.total_messages += 1
        if is_user_message:
            self.user_messages += 1
        else:
            self.agent_messages += 1
        self.update_activity()

    @property
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == "active"

    @property
    def duration_minutes(self) -> float:
        """Get session duration in minutes"""
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds() / 60
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        result = super().to_dict()
        result.update({
            'is_active': self.is_active,
            'duration_minutes': self.duration_minutes,
            'message_counts': {
                'total': self.total_messages,
                'user': self.user_messages,
                'agent': self.agent_messages
            }
        })
        return result


class ChatMessage(Base, TimestampMixin):
    """Individual chat message model"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    
    # Message content
    message_id = Column(String(255), unique=True, nullable=False, index=True)  # UUID for message
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, voice, system, handoff
    
    # Message metadata
    sender = Column(String(50), nullable=False)  # user, agent, system
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # AI processing data
    intent = Column(String(100))  # Detected intent
    confidence = Column(Float, default=0.0)  # AI confidence score
    entities = Column(JSON, default=list)  # Extracted entities
    sentiment = Column(String(50))  # positive, negative, neutral
    
    # Response generation
    response_time_ms = Column(Integer, default=0)  # Response generation time
    model_used = Column(String(100))  # LLM model used
    tokens_used = Column(Integer, default=0)  # Token count
    
    # Voice-to-text data (if applicable)
    audio_duration_seconds = Column(Float, nullable=True)
    transcription_confidence = Column(Float, nullable=True)
    original_audio_url = Column(String(500), nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender='{self.sender}', type='{self.message_type}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        result = super().to_dict()
        result.update({
            'content_preview': self.content[:100] + '...' if len(self.content) > 100 else self.content
        })
        return result