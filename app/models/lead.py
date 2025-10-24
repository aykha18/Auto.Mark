"""
Lead model for managing marketing leads and prospects
"""

from datetime import datetime
from typing import Optional, Dict, Any
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

    # Additional metadata
    tags = Column(JSON, default=list)  # custom tags for segmentation
    custom_fields = Column(JSON, default=dict)  # extensible custom data
    notes = Column(Text)  # internal notes

    # Relationships
    campaign = relationship("Campaign", back_populates="leads")

    def __repr__(self):
        return f"<Lead(id={self.id}, email='{self.email}', company='{self.company}', score={self.score:.2f})>"

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
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str):
        """Remove a tag from the lead"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

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