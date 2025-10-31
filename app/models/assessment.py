"""
Assessment model for storing AI Business Readiness Assessment responses and scores
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Assessment(Base, TimestampMixin):
    """Assessment model for tracking AI Business Readiness Assessment responses and scores"""

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Lead association
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    
    # Assessment metadata
    assessment_type = Column(String(100), default="ai_business_readiness", nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    
    # Assessment responses
    responses = Column(JSON, nullable=False, default=dict)  # Question ID -> Answer mapping
    
    # Current CRM information
    current_crm = Column(String(100), index=True)  # Pipedrive, Zoho, HubSpot, Monday, Salesforce, etc.
    crm_usage_level = Column(String(50))  # basic, intermediate, advanced
    crm_data_quality = Column(String(50))  # poor, fair, good, excellent
    
    # Scoring results
    overall_score = Column(Float, nullable=False, default=0.0, index=True)  # 0-100 scale
    category_scores = Column(JSON, default=dict)  # Category -> Score mapping
    
    # Lead qualification
    readiness_level = Column(String(50), index=True)  # cold, warm, hot
    segment = Column(String(50), index=True)  # nurture_with_guides, co_creator_qualified, priority_integration
    
    # Recommendations and insights
    integration_recommendations = Column(JSON, default=list)  # List of specific recommendations
    automation_opportunities = Column(JSON, default=list)  # List of automation opportunities
    technical_requirements = Column(JSON, default=list)  # List of technical requirements
    next_steps = Column(JSON, default=list)  # List of recommended next steps
    
    # Assessment completion tracking
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, index=True)
    is_completed = Column(Boolean, default=False, index=True)
    completion_time_seconds = Column(Integer)  # Time taken to complete
    
    # Additional metadata
    user_agent = Column(Text)  # Browser/device information
    ip_address = Column(String(45))  # IPv4 or IPv6 address
    referrer = Column(Text)  # Where they came from
    
    # Relationships
    lead = relationship("Lead", back_populates="assessments")

    def __repr__(self):
        return f"<Assessment(id={self.id}, lead_id={self.lead_id}, score={self.overall_score:.1f}, level='{self.readiness_level}')>"

    @property
    def is_cold_lead(self) -> bool:
        """Check if this is a cold lead (0-40%)"""
        return self.overall_score <= 40.0

    @property
    def is_warm_lead(self) -> bool:
        """Check if this is a warm lead (41-70%)"""
        return 40.0 < self.overall_score <= 70.0

    @property
    def is_hot_lead(self) -> bool:
        """Check if this is a hot lead (71-100%)"""
        return self.overall_score > 70.0

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage based on responses"""
        if not self.responses:
            return 0.0
        
        # Assuming 10 questions total (as per requirements)
        total_questions = 10
        answered_questions = len([r for r in self.responses.values() if r is not None and r != ""])
        return (answered_questions / total_questions) * 100

    def calculate_readiness_level(self) -> str:
        """Calculate readiness level based on overall score"""
        if self.overall_score <= 40.0:
            return "cold"
        elif self.overall_score <= 70.0:
            return "warm"
        else:
            return "hot"

    def calculate_segment(self) -> str:
        """Calculate lead segment based on readiness level"""
        readiness = self.calculate_readiness_level()
        
        if readiness == "cold":
            return "nurture_with_guides"
        elif readiness == "warm":
            return "co_creator_qualified"
        else:
            return "priority_integration"

    def update_score(self, overall_score: float, category_scores: Dict[str, float] = None):
        """Update assessment scores and derived fields"""
        self.overall_score = max(0.0, min(100.0, overall_score))
        
        if category_scores:
            self.category_scores = category_scores
        
        self.readiness_level = self.calculate_readiness_level()
        self.segment = self.calculate_segment()
        self.updated_at = datetime.utcnow()

    def complete_assessment(self, completion_time_seconds: int = None):
        """Mark assessment as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        
        if completion_time_seconds:
            self.completion_time_seconds = completion_time_seconds
        elif self.started_at:
            delta = self.completed_at - self.started_at
            self.completion_time_seconds = int(delta.total_seconds())
        
        self.updated_at = datetime.utcnow()

    def add_response(self, question_id: str, answer: Any):
        """Add or update a response to a specific question"""
        if not self.responses:
            self.responses = {}
        
        self.responses[question_id] = answer
        self.updated_at = datetime.utcnow()

    def get_response(self, question_id: str) -> Any:
        """Get response for a specific question"""
        return self.responses.get(question_id) if self.responses else None

    def add_recommendation(self, recommendation: str):
        """Add an integration recommendation"""
        if not self.integration_recommendations:
            self.integration_recommendations = []
        
        if recommendation not in self.integration_recommendations:
            self.integration_recommendations.append(recommendation)
            self.updated_at = datetime.utcnow()

    def add_automation_opportunity(self, opportunity: str):
        """Add an automation opportunity"""
        if not self.automation_opportunities:
            self.automation_opportunities = []
        
        if opportunity not in self.automation_opportunities:
            self.automation_opportunities.append(opportunity)
            self.updated_at = datetime.utcnow()

    def add_next_step(self, step: str):
        """Add a recommended next step"""
        if not self.next_steps:
            self.next_steps = []
        
        if step not in self.next_steps:
            self.next_steps.append(step)
            self.updated_at = datetime.utcnow()

    @classmethod
    def create_from_responses(cls, lead_id: int, responses: Dict[str, Any], 
                            current_crm: str = None, **kwargs) -> 'Assessment':
        """Create assessment from response data"""
        assessment = cls(
            lead_id=lead_id,
            responses=responses,
            current_crm=current_crm,
            **kwargs
        )
        
        return assessment

    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary"""
        result = super().to_dict()
        result.update({
            'is_cold_lead': self.is_cold_lead,
            'is_warm_lead': self.is_warm_lead,
            'is_hot_lead': self.is_hot_lead,
            'completion_percentage': self.completion_percentage
        })
        return result
