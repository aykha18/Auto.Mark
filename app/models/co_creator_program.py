"""
CoCreatorProgram model for managing seat allocation and program status
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class CoCreatorProgram(Base, TimestampMixin):
    """CoCreatorProgram model for managing the exclusive 25-seat co-creator program"""

    __tablename__ = "co_creator_programs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Program configuration
    program_name = Column(String(255), default="Founding Users Co-Creator Program", nullable=False)
    total_seats = Column(Integer, default=25, nullable=False)
    seats_filled = Column(Integer, default=0, nullable=False, index=True)
    program_price = Column(Float, default=250.0, nullable=False)  # USD
    currency = Column(String(3), default="USD", nullable=False)
    
    # Program status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_full = Column(Boolean, default=False, nullable=False, index=True)
    program_status = Column(String(50), default="active", nullable=False)  # active, paused, full, closed
    
    # Program timeline
    launch_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    target_fill_date = Column(DateTime)  # Target date to fill all seats
    filled_date = Column(DateTime)  # Date when program became full
    
    # Urgency and messaging
    urgency_level = Column(String(20), default="medium", nullable=False)  # low, medium, high
    urgency_message = Column(Text)
    scarcity_message = Column(Text)
    
    # Program benefits and features
    benefits = Column(JSON, default=list)  # List of program benefits
    features = Column(JSON, default=list)  # List of exclusive features
    support_level = Column(String(50), default="priority")  # standard, priority, white_glove
    
    # Waitlist management
    waitlist_enabled = Column(Boolean, default=True, nullable=False)
    waitlist_count = Column(Integer, default=0, nullable=False)
    
    # Analytics and tracking
    page_views = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)  # Percentage
    average_time_to_convert = Column(Integer)  # Seconds
    
    # Relationships
    co_creators = relationship("CoCreator", back_populates="program", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CoCreatorProgram(id={self.id}, seats={self.seats_filled}/{self.total_seats}, status='{self.program_status}')>"

    @property
    def seats_remaining(self) -> int:
        """Calculate remaining seats"""
        return max(0, self.total_seats - self.seats_filled)

    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage"""
        if self.total_seats == 0:
            return 0.0
        return (self.seats_filled / self.total_seats) * 100

    @property
    def is_nearly_full(self) -> bool:
        """Check if program is nearly full (>80%)"""
        return self.fill_percentage > 80.0

    @property
    def is_almost_full(self) -> bool:
        """Check if program is almost full (>90%)"""
        return self.fill_percentage > 90.0

    def calculate_urgency_level(self) -> str:
        """Calculate urgency level based on fill percentage"""
        if self.fill_percentage >= 90.0:
            return "high"
        elif self.fill_percentage >= 70.0:
            return "medium"
        else:
            return "low"

    def update_urgency_messaging(self):
        """Update urgency and scarcity messaging based on current status"""
        remaining = self.seats_remaining
        urgency = self.calculate_urgency_level()
        
        if urgency == "high":
            self.urgency_message = f"Only {remaining} seats left! Program closes soon."
            self.scarcity_message = "This exclusive opportunity won't last long."
        elif urgency == "medium":
            self.urgency_message = f"{remaining} seats remaining in this exclusive program."
            self.scarcity_message = "Join now to secure your spot as a founding user."
        else:
            self.urgency_message = f"Limited to {self.total_seats} founding users only."
            self.scarcity_message = "Be part of shaping the future of AI marketing automation."
        
        self.urgency_level = urgency
        self.updated_at = datetime.utcnow()

    def reserve_seat(self) -> bool:
        """Reserve a seat (atomic operation)"""
        if self.seats_remaining <= 0 or not self.is_active:
            return False
        
        self.seats_filled += 1
        
        # Check if program is now full
        if self.seats_filled >= self.total_seats:
            self.is_full = True
            self.program_status = "full"
            self.filled_date = datetime.utcnow()
        
        self.update_urgency_messaging()
        self.updated_at = datetime.utcnow()
        return True

    def release_seat(self) -> bool:
        """Release a seat (for cancellations/refunds)"""
        if self.seats_filled <= 0:
            return False
        
        self.seats_filled -= 1
        self.is_full = False
        
        if self.program_status == "full":
            self.program_status = "active"
            self.filled_date = None
        
        self.update_urgency_messaging()
        self.updated_at = datetime.utcnow()
        return True

    def add_to_waitlist(self) -> bool:
        """Add someone to waitlist"""
        if not self.waitlist_enabled:
            return False
        
        self.waitlist_count += 1
        self.updated_at = datetime.utcnow()
        return True

    def remove_from_waitlist(self) -> bool:
        """Remove someone from waitlist"""
        if self.waitlist_count <= 0:
            return False
        
        self.waitlist_count -= 1
        self.updated_at = datetime.utcnow()
        return True

    def record_page_view(self):
        """Record a page view"""
        self.page_views += 1
        self.updated_at = datetime.utcnow()

    def update_conversion_rate(self, conversions: int):
        """Update conversion rate based on page views and conversions"""
        if self.page_views > 0:
            self.conversion_rate = (conversions / self.page_views) * 100
        else:
            self.conversion_rate = 0.0
        self.updated_at = datetime.utcnow()

    def pause_program(self):
        """Pause the program"""
        self.is_active = False
        self.program_status = "paused"
        self.updated_at = datetime.utcnow()

    def resume_program(self):
        """Resume the program"""
        if not self.is_full:
            self.is_active = True
            self.program_status = "active"
            self.updated_at = datetime.utcnow()

    def close_program(self):
        """Close the program permanently"""
        self.is_active = False
        self.program_status = "closed"
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_active_program(cls, db_session):
        """Get the currently active co-creator program"""
        return db_session.query(cls).filter(
            cls.is_active == True,
            cls.program_status.in_(["active", "full"])
        ).first()

    def to_dict(self) -> Dict[str, Any]:
        """Convert program to dictionary"""
        result = super().to_dict()
        result.update({
            'seats_remaining': self.seats_remaining,
            'fill_percentage': self.fill_percentage,
            'is_nearly_full': self.is_nearly_full,
            'is_almost_full': self.is_almost_full
        })
        return result


class CoCreator(Base, TimestampMixin):
    """Individual co-creator within the program"""

    __tablename__ = "co_creators"

    id = Column(Integer, primary_key=True, index=True)
    
    # Program association
    program_id = Column(Integer, ForeignKey("co_creator_programs.id"), nullable=False, index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    
    # Co-creator details
    seat_number = Column(Integer, nullable=False, index=True)  # 1-25
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Status and access
    status = Column(String(50), default="active", nullable=False)  # active, inactive, cancelled
    lifetime_access = Column(Boolean, default=True, nullable=False)
    access_level = Column(String(50), default="co_creator", nullable=False)  # co_creator, founder, vip
    
    # Benefits and recognition
    supporter_badge = Column(Boolean, default=True, nullable=False)
    testimonial_opt_in = Column(Boolean, default=False, nullable=False)
    feature_influence_count = Column(Integer, default=0, nullable=False)
    
    # Engagement tracking
    last_login = Column(DateTime)
    total_logins = Column(Integer, default=0, nullable=False)
    features_suggested = Column(Integer, default=0, nullable=False)
    votes_cast = Column(Integer, default=0, nullable=False)
    
    # Custom benefits
    custom_benefits = Column(JSON, default=list)
    special_privileges = Column(JSON, default=list)
    
    # Metadata for tracking onboarding and other data
    co_creator_metadata = Column(JSON, default=dict)
    
    # Relationships
    program = relationship("CoCreatorProgram", back_populates="co_creators")
    user = relationship("User")
    lead = relationship("Lead")

    def __repr__(self):
        return f"<CoCreator(id={self.id}, seat={self.seat_number}, user_id={self.user_id}, status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if co-creator is active"""
        return self.status == "active"

    @property
    def days_as_co_creator(self) -> int:
        """Calculate days as co-creator"""
        return (datetime.utcnow() - self.joined_at).days

    def record_login(self):
        """Record a login"""
        self.last_login = datetime.utcnow()
        self.total_logins += 1
        self.updated_at = datetime.utcnow()

    def suggest_feature(self):
        """Record a feature suggestion"""
        self.features_suggested += 1
        self.updated_at = datetime.utcnow()

    def cast_vote(self):
        """Record a vote cast"""
        self.votes_cast += 1
        self.updated_at = datetime.utcnow()

    def influence_feature(self):
        """Record feature influence"""
        self.feature_influence_count += 1
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate co-creator"""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()

    def reactivate(self):
        """Reactivate co-creator"""
        self.status = "active"
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancel co-creator membership"""
        self.status = "cancelled"
        self.lifetime_access = False
        self.updated_at = datetime.utcnow()

    def add_metadata(self, key: str, value: Any):
        """Add metadata to co-creator"""
        if self.co_creator_metadata is None:
            self.co_creator_metadata = {}
        
        self.co_creator_metadata[key] = value
        self.updated_at = datetime.utcnow()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        if self.co_creator_metadata is None:
            return default
        
        return self.co_creator_metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert co-creator to dictionary"""
        result = super().to_dict()
        result.update({
            'is_active': self.is_active,
            'days_as_co_creator': self.days_as_co_creator
        })
        return result