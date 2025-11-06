"""
Lead model for managing marketing leads and prospects
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Lead(Base, TimestampMixin):
    """Lead model for tracking marketing prospects and their qualification status"""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(String(255), unique=True, nullable=False, index=True)  # UUID or external ID

    # Campaign association
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)

    # Basic contact information
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    company = Column(String(255), index=True)
    job_title = Column(String(255))
    website = Column(String(500))

    # Company information
    company_size = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 501-1000, 1000+
    industry = Column(String(100), index=True)
    company_revenue = Column(String(50))  # ranges like $0-1M, $1-10M, etc.
    location = Column(String(255))  # city, state/country

    # Lead qualification
    score = Column(Float, default=0.0, index=True)  # 0-1 qualification score
    status = Column(String(50), default="new")  # new, contacted, qualified, unqualified, converted
    source = Column(String(100))  # web_scraping, linkedin, company_search, manual
    source_url = Column(Text)  # URL where lead was found

    # Qualification criteria
    budget = Column(String(50))  # low, medium, high, enterprise
    timeline = Column(String(50))  # immediate, 1-3 months, 3-6 months, 6+ months
    decision_maker = Column(Boolean, default=False)  # is this person a decision maker?
    pain_points = Column(JSON, default=list)  # list of identified pain points
    interests = Column(JSON, default=list)  # marketing interests/topics

    # Engagement tracking
    first_contacted = Column(DateTime)
    last_contacted = Column(DateTime)
    contact_attempts = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)

    # Conversion tracking
    converted = Column(Boolean, default=False)
    converted_at = Column(DateTime)
    conversion_value = Column(Float, default=0.0)
    conversion_type = Column(String(100))  # sale, demo, trial, etc.

    # Assessment and CRM integration data
    preferred_crm = Column(String(100), index=True)  # Preferred CRM system
    crm_integration_readiness = Column(Float, default=0.0, index=True)  # 0-100 scale
    technical_capability_score = Column(Float, default=0.0)  # Technical readiness score
    business_maturity_score = Column(Float, default=0.0)  # Business maturity score
    investment_capacity_score = Column(Float, default=0.0)  # Investment capacity score
    automation_gaps_score = Column(Float, default=0.0)  # Automation opportunity score
    data_quality_score = Column(Float, default=0.0)  # Data quality score
    
    # Lead segmentation
    readiness_segment = Column(String(50), index=True)  # cold, warm, hot
    segment_confidence = Column(Float, default=0.0)  # Confidence in segmentation
    last_scored_at = Column(DateTime, index=True)  # When lead was last scored
    
    # CRM preferences and capabilities
    current_crm_system = Column(String(100), index=True)  # Current CRM in use
    crm_usage_level = Column(String(50))  # basic, intermediate, advanced
    has_api_access = Column(Boolean, default=False)  # API access availability
    integration_complexity = Column(String(50))  # easy, medium, advanced
    
    # Business context
    monthly_lead_volume = Column(String(50))  # Lead volume range
    automation_goals = Column(JSON, default=list)  # Primary automation goals
    marketing_automation_level = Column(String(50))  # Current automation level
    
    # Consultation booking fields
    consultation_requested = Column(Boolean, default=False)  # Has requested consultation
    consultation_booked = Column(Boolean, default=False)  # Has booked consultation
    consultation_completed = Column(Boolean, default=False)  # Has completed consultation
    consultation_type = Column(String(100))  # Type of consultation requested
    consultation_challenges = Column(Text)  # Challenges/goals mentioned in booking
    consultation_scheduled_at = Column(DateTime)  # When consultation is scheduled
    consultation_completed_at = Column(DateTime)  # When consultation was completed
    
    # Additional metadata
    tags = Column(JSON, default=list)  # custom tags for segmentation
    custom_fields = Column(JSON, default=dict)  # extensible custom data
    notes = Column(Text)  # internal notes

    # Relationships
    campaign = relationship("Campaign", back_populates="leads")
    assessments = relationship("Assessment", back_populates="lead", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        score = self.score if self.score is not None else 0.0
        return f"<Lead(id={self.id}, email='{self.email}', company='{self.company}', score={score:.2f})>"

    @property
    def full_name(self) -> str:
        """Get full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(filter(None, parts)) or "Unknown"

    @property
    def is_qualified(self) -> bool:
        """Check if lead meets qualification criteria"""
        return self.score >= 0.7 and self.status in ["qualified", "converted"]

    @property
    def is_converted(self) -> bool:
        """Check if lead has converted"""
        return self.converted and self.converted_at is not None

    @property
    def response_rate(self) -> float:
        """Calculate response rate"""
        if self.emails_sent == 0:
            return 0.0
        return (self.responses_received / self.emails_sent) * 100

    @property
    def days_since_last_contact(self) -> Optional[int]:
        """Calculate days since last contact"""
        if not self.last_contacted:
            return None
        return (datetime.utcnow() - self.last_contacted).days

    def update_score(self, new_score: float):
        """Update lead qualification score"""
        self.score = max(0.0, min(1.0, new_score))
        self.updated_at = datetime.utcnow()

    def mark_qualified(self):
        """Mark lead as qualified"""
        self.status = "qualified"
        self.updated_at = datetime.utcnow()

    def mark_unqualified(self):
        """Mark lead as unqualified"""
        self.status = "unqualified"
        self.updated_at = datetime.utcnow()

    def record_contact(self):
        """Record a contact attempt"""
        self.contact_attempts += 1
        self.last_contacted = datetime.utcnow()
        if not self.first_contacted:
            self.first_contacted = self.last_contacted
        self.updated_at = datetime.utcnow()

    def record_email_sent(self):
        """Record an email sent"""
        self.emails_sent += 1
        self.record_contact()

    def record_response(self):
        """Record a response received"""
        self.responses_received += 1
        self.updated_at = datetime.utcnow()

    def convert(self, value: float = 0.0, conversion_type: str = "sale"):
        """Mark lead as converted"""
        self.converted = True
        self.converted_at = datetime.utcnow()
        self.conversion_value = value
        self.conversion_type = conversion_type
        self.status = "converted"
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str):
        """Add a tag to the lead"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str):
        """Remove a tag from the lead"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def update_assessment_data(self, assessment_data: Dict[str, Any], 
                             factor_scores: Dict[str, float],
                             segment: str, confidence: float):
        """Update lead with assessment data and scoring results"""
        # Update CRM information
        self.current_crm_system = assessment_data.get("crm_system")
        self.preferred_crm = assessment_data.get("crm_system")
        self.crm_usage_level = assessment_data.get("crm_usage_level")
        self.has_api_access = "Full API access" in assessment_data.get("api_access", "")
        
        # Update business context
        self.monthly_lead_volume = assessment_data.get("monthly_leads")
        self.marketing_automation_level = assessment_data.get("marketing_automation")
        
        # Store automation goals
        goals = []
        if assessment_data.get("automation_goals"):
            goals.append(assessment_data["automation_goals"])
        if assessment_data.get("lead_nurturing"):
            goals.append(f"Current nurturing: {assessment_data['lead_nurturing']}")
        self.automation_goals = goals
        
        # Update factor scores
        self.crm_integration_readiness = factor_scores.get("crm_integration_readiness", 0.0)
        self.technical_capability_score = factor_scores.get("technical_capability", 0.0)
        self.business_maturity_score = factor_scores.get("business_maturity", 0.0)
        self.investment_capacity_score = factor_scores.get("investment_capacity", 0.0)
        self.automation_gaps_score = factor_scores.get("automation_gaps", 0.0)
        self.data_quality_score = factor_scores.get("data_quality", 0.0)
        
        # Update segmentation
        self.readiness_segment = segment
        self.segment_confidence = confidence
        self.last_scored_at = datetime.utcnow()
        
        # Determine integration complexity
        complexity_map = {
            "neuracrm": "easy",
            "hubspot": "easy", 
            "pipedrive": "easy",
            "zoho": "medium",
            "monday": "medium",
            "salesforce": "advanced",
            "other": "advanced",
            "none": "easy"
        }
        self.integration_complexity = complexity_map.get(self.current_crm_system, "medium")
        
        # Add relevant tags
        self.add_tag(f"segment_{segment}")
        self.add_tag(f"crm_{self.current_crm_system}")
        if self.crm_integration_readiness >= 80:
            self.add_tag("high_crm_readiness")
        if self.technical_capability_score >= 70:
            self.add_tag("tech_capable")
        if self.investment_capacity_score >= 60:
            self.add_tag("budget_ready")
        
        self.updated_at = datetime.utcnow()
    
    def get_crm_readiness_summary(self) -> Dict[str, Any]:
        """Get a summary of CRM integration readiness"""
        return {
            "overall_readiness": self.crm_integration_readiness,
            "segment": self.readiness_segment,
            "confidence": self.segment_confidence,
            "current_crm": self.current_crm_system,
            "preferred_crm": self.preferred_crm,
            "integration_complexity": self.integration_complexity,
            "has_api_access": self.has_api_access,
            "factor_scores": {
                "crm_integration": self.crm_integration_readiness,
                "technical_capability": self.technical_capability_score,
                "business_maturity": self.business_maturity_score,
                "investment_capacity": self.investment_capacity_score,
                "automation_gaps": self.automation_gaps_score,
                "data_quality": self.data_quality_score
            },
            "last_scored": self.last_scored_at
        }
    
    def is_co_creator_qualified(self) -> bool:
        """Check if lead qualifies for co-creator program (warm or hot)"""
        return self.readiness_segment in ["warm", "hot"] and self.crm_integration_readiness >= 41
    
    def is_priority_lead(self) -> bool:
        """Check if this is a priority lead (hot segment)"""
        return self.readiness_segment == "hot" and self.crm_integration_readiness >= 71
    
    def needs_nurturing(self) -> bool:
        """Check if lead needs nurturing (cold segment)"""
        return self.readiness_segment == "cold" or self.crm_integration_readiness <= 40
    
    def get_recommended_next_steps(self) -> List[str]:
        """Get recommended next steps based on lead segment"""
        if self.is_priority_lead():
            return [
                "Book priority demo with founder",
                "Discuss partnership opportunities",
                "Fast-track CRM integration setup"
            ]
        elif self.is_co_creator_qualified():
            return [
                "Invite to Co-Creator Program",
                "Provide guided integration setup",
                "Offer personalized implementation support"
            ]
        else:
            return [
                "Send CRM integration strategy guide",
                "Schedule consultation call",
                "Provide foundation building resources"
            ]

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'Lead':
        """Create a lead from dictionary data"""
        # Extract known fields
        lead_data = {
            key: value for key, value in data.items()
            if key in cls.__table__.columns.keys()
        }

        # Handle custom fields
        custom_fields = {
            key: value for key, value in data.items()
            if key not in cls.__table__.columns.keys()
        }
        if custom_fields:
            lead_data['custom_fields'] = custom_fields

        return cls(**lead_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert lead to dictionary"""
        result = super().to_dict()
        result['full_name'] = self.full_name
        result['is_qualified'] = self.is_qualified
        result['is_converted'] = self.is_converted
        result['response_rate'] = self.response_rate
        result['days_since_last_contact'] = self.days_since_last_contact
        return result
