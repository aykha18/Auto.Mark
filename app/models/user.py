"""
User model for authentication and user management
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for the marketing platform"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company = Column(String(255))
    role = Column(String(50), default="user")  # admin, user, agent
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # API key for authentication
    api_key = Column(String(255), unique=True, index=True)

    # Profile information
    avatar_url = Column(Text)
    bio = Column(Text)
    website = Column(String(255))

    # Subscription and limits
    subscription_tier = Column(String(50), default="free")  # free, pro, enterprise
    monthly_request_limit = Column(Integer, default=1000)
    requests_this_month = Column(Integer, default=0)

    # Timestamps (inherited from TimestampMixin)
    last_login = Column(DateTime)

    # Relationships
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    def can_make_request(self) -> bool:
        """Check if user can make another API request this month"""
        return self.requests_this_month < self.monthly_request_limit

    def increment_request_count(self):
        """Increment the monthly request count"""
        self.requests_this_month += 1

    def reset_request_count(self):
        """Reset monthly request count (for billing cycle)"""
        self.requests_this_month = 0

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == "admin"

    @property
    def is_pro(self) -> bool:
        """Check if user has pro subscription"""
        return self.subscription_tier in ["pro", "enterprise"]

    @property
    def is_enterprise(self) -> bool:
        """Check if user has enterprise subscription"""
        return self.subscription_tier == "enterprise"