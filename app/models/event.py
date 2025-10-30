"""
Event model for behavioral tracking and analytics
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    """Event model for tracking user behavior and marketing interactions"""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # page_view, click, purchase, etc.
    event_name = Column(String(255), nullable=False)  # specific event identifier

    # User association
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    anonymous_id = Column(String(255), index=True)  # for anonymous users
    session_id = Column(String(255), index=True)

    # Event properties
    properties = Column(JSON, nullable=False, default=dict)  # event-specific data
    context = Column(JSON, default=dict)  # additional context (user_agent, url, etc.)

    # Marketing attribution
    campaign_id = Column(String(255), index=True)
    source = Column(String(100))  # organic, paid, social, email, etc.
    medium = Column(String(100))  # search, display, email, social, etc.
    term = Column(String(255))  # search terms
    content = Column(String(255))  # content identifier

    # Geographic and device info
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    country = Column(String(2))  # ISO country code
    city = Column(String(100))
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    os = Column(String(100))

    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime)  # when event was processed for analytics

    # Processing status
    is_processed = Column(Boolean, default=False, index=True)
    processing_attempts = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', name='{self.event_name}', user_id={self.user_id})>"

    @property
    def is_anonymous(self) -> bool:
        """Check if this is an anonymous event"""
        return self.user_id is None and self.anonymous_id is not None

    @property
    def has_user(self) -> bool:
        """Check if event is associated with a registered user"""
        return self.user_id is not None

    def mark_processed(self):
        """Mark event as processed"""
        self.is_processed = True
        self.processed_at = datetime.utcnow()

    def increment_processing_attempts(self):
        """Increment processing attempts counter"""
        self.processing_attempts += 1

    def should_retry_processing(self, max_attempts: int = 3) -> bool:
        """Check if processing should be retried"""
        return not self.is_processed and self.processing_attempts < max_attempts

    @classmethod
    def create_page_view(
        cls,
        url: str,
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create a page view event"""
        return cls(
            event_type="page_view",
            event_name="page_viewed",
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "url": url,
                "path": url.split('?')[0] if '?' in url else url,
                **kwargs
            }
        )

    @classmethod
    def create_click(
        cls,
        element: str,
        page_url: str,
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create a click event"""
        return cls(
            event_type="click",
            event_name="element_clicked",
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "element": element,
                "page_url": page_url,
                **kwargs
            }
        )

    @classmethod
    def create_conversion(
        cls,
        conversion_type: str,
        value: Optional[float] = None,
        currency: str = "USD",
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create a conversion event"""
        return cls(
            event_type="conversion",
            event_name=conversion_type,
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "conversion_type": conversion_type,
                "value": value,
                "currency": currency,
                **kwargs
            }
        )

    @classmethod
    def create_assessment_event(
        cls,
        event_name: str,
        lead_id: Optional[int] = None,
        assessment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create an assessment-related event"""
        return cls(
            event_type="assessment",
            event_name=event_name,
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "lead_id": lead_id,
                "assessment_id": assessment_id,
                **kwargs
            }
        )

    @classmethod
    def create_crm_integration_event(
        cls,
        event_name: str,
        crm_type: Optional[str] = None,
        integration_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create a CRM integration-related event"""
        return cls(
            event_type="crm_integration",
            event_name=event_name,
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "crm_type": crm_type,
                "integration_id": integration_id,
                "lead_id": lead_id,
                **kwargs
            }
        )

    @classmethod
    def create_co_creator_event(
        cls,
        event_name: str,
        program_id: Optional[int] = None,
        payment_amount: Optional[float] = None,
        lead_id: Optional[int] = None,
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create a co-creator program-related event"""
        return cls(
            event_type="co_creator",
            event_name=event_name,
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "program_id": program_id,
                "payment_amount": payment_amount,
                "lead_id": lead_id,
                **kwargs
            }
        )

    @classmethod
    def create_landing_page_event(
        cls,
        event_name: str,
        page_section: Optional[str] = None,
        cta_clicked: Optional[str] = None,
        lead_id: Optional[int] = None,
        user_id: Optional[int] = None,
        anonymous_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Create a landing page-related event"""
        return cls(
            event_type="landing_page",
            event_name=event_name,
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties={
                "page_section": page_section,
                "cta_clicked": cta_clicked,
                "lead_id": lead_id,
                **kwargs
            }
        )