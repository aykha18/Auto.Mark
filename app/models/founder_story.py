"""
FounderStory model for dynamic content management of founder journey and milestones
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class FounderStory(Base, TimestampMixin):
    """FounderStory model for managing founder journey content and milestones"""

    __tablename__ = "founder_stories"

    id = Column(Integer, primary_key=True, index=True)
    
    # Story metadata
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500))
    version = Column(String(20), default="1.0", nullable=False)
    
    # Story content
    hero_narrative = Column(Text, nullable=False)  # Main story narrative
    vision_statement = Column(Text)  # Future vision
    mission_statement = Column(Text)  # Mission statement
    
    # Current metrics and achievements
    total_leads_automated = Column(Integer, default=0, nullable=False)
    crms_integrated = Column(Integer, default=0, nullable=False)
    businesses_enabled = Column(Integer, default=0, nullable=False)
    integration_hours_saved = Column(Integer, default=0, nullable=False)
    
    # Story status and visibility
    is_published = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # SEO and metadata
    meta_description = Column(Text)
    keywords = Column(JSON, default=list)  # SEO keywords
    
    # Analytics
    views = Column(Integer, default=0, nullable=False)
    engagement_score = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    milestones = relationship("FounderMilestone", back_populates="story", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FounderStory(id={self.id}, title='{self.title}', milestones={len(self.milestones)})>"

    @property
    def milestone_count(self) -> int:
        """Get number of milestones"""
        return len(self.milestones) if self.milestones else 0

    @property
    def latest_milestone(self) -> Optional['FounderMilestone']:
        """Get the most recent milestone"""
        if not self.milestones:
            return None
        return max(self.milestones, key=lambda m: m.milestone_date)

    def record_view(self):
        """Record a story view"""
        self.views += 1
        self.updated_at = datetime.utcnow()

    def update_metrics(self, leads: int = None, crms: int = None, 
                      businesses: int = None, hours: int = None):
        """Update current metrics"""
        if leads is not None:
            self.total_leads_automated = leads
        if crms is not None:
            self.crms_integrated = crms
        if businesses is not None:
            self.businesses_enabled = businesses
        if hours is not None:
            self.integration_hours_saved = hours
        
        self.updated_at = datetime.utcnow()

    def publish(self):
        """Publish the story"""
        self.is_published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self):
        """Unpublish the story"""
        self.is_published = False
        self.updated_at = datetime.utcnow()

    def feature(self):
        """Feature the story"""
        self.is_featured = True
        self.updated_at = datetime.utcnow()

    def unfeature(self):
        """Unfeature the story"""
        self.is_featured = False
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_published_story(cls, db_session) -> Optional['FounderStory']:
        """Get the currently published founder story"""
        return db_session.query(cls).filter(
            cls.is_published == True
        ).order_by(cls.display_order.desc()).first()

    def to_dict(self) -> Dict[str, Any]:
        """Convert story to dictionary"""
        result = super().to_dict()
        result.update({
            'milestone_count': self.milestone_count,
            'latest_milestone': self.latest_milestone.to_dict() if self.latest_milestone else None,
            'milestones': [m.to_dict() for m in self.milestones] if self.milestones else []
        })
        return result


class FounderMilestone(Base, TimestampMixin):
    """Individual milestone in the founder's journey"""

    __tablename__ = "founder_milestones"

    id = Column(Integer, primary_key=True, index=True)
    
    # Story association
    story_id = Column(Integer, ForeignKey("founder_stories.id"), nullable=False, index=True)
    
    # Milestone details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    milestone_date = Column(Date, nullable=False, index=True)
    
    # Milestone metrics
    leads_generated = Column(Integer, default=0)
    crm_integrations = Column(Integer, default=0)
    automation_level = Column(Integer, default=0)  # Percentage 0-100
    time_saved_hours = Column(Integer, default=0)
    revenue_impact = Column(Float, default=0.0)
    
    # Technical details
    technologies_used = Column(JSON, default=list)  # List of technologies
    integration_challenges = Column(JSON, default=list)  # List of challenges
    solutions_implemented = Column(JSON, default=list)  # List of solutions
    
    # Learning and insights
    lesson_learned = Column(Text)
    key_insight = Column(Text)
    business_impact = Column(Text)
    
    # Milestone type and category
    milestone_type = Column(String(100), nullable=False)  # technical, business, personal, integration
    category = Column(String(100))  # crm_integration, automation, scaling, etc.
    
    # Display and ordering
    display_order = Column(Integer, default=0, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    
    # Media and assets
    image_url = Column(Text)
    video_url = Column(Text)
    demo_url = Column(Text)
    
    # Relationships
    story = relationship("FounderStory", back_populates="milestones")

    def __repr__(self):
        return f"<FounderMilestone(id={self.id}, title='{self.title}', date={self.milestone_date})>"

    @property
    def days_ago(self) -> int:
        """Calculate days since milestone"""
        return (date.today() - self.milestone_date).days

    @property
    def is_recent(self) -> bool:
        """Check if milestone is recent (within 30 days)"""
        return self.days_ago <= 30

    @property
    def has_metrics(self) -> bool:
        """Check if milestone has any metrics"""
        return any([
            self.leads_generated > 0,
            self.crm_integrations > 0,
            self.automation_level > 0,
            self.time_saved_hours > 0,
            self.revenue_impact > 0
        ])

    def add_technology(self, technology: str):
        """Add a technology to the milestone"""
        if not self.technologies_used:
            self.technologies_used = []
        
        if technology not in self.technologies_used:
            self.technologies_used.append(technology)
            self.updated_at = datetime.utcnow()

    def add_challenge(self, challenge: str):
        """Add a challenge to the milestone"""
        if not self.integration_challenges:
            self.integration_challenges = []
        
        if challenge not in self.integration_challenges:
            self.integration_challenges.append(challenge)
            self.updated_at = datetime.utcnow()

    def add_solution(self, solution: str):
        """Add a solution to the milestone"""
        if not self.solutions_implemented:
            self.solutions_implemented = []
        
        if solution not in self.solutions_implemented:
            self.solutions_implemented.append(solution)
            self.updated_at = datetime.utcnow()

    def update_metrics(self, leads: int = None, crms: int = None, 
                      automation: int = None, hours: int = None, revenue: float = None):
        """Update milestone metrics"""
        if leads is not None:
            self.leads_generated = leads
        if crms is not None:
            self.crm_integrations = crms
        if automation is not None:
            self.automation_level = max(0, min(100, automation))
        if hours is not None:
            self.time_saved_hours = hours
        if revenue is not None:
            self.revenue_impact = revenue
        
        self.updated_at = datetime.utcnow()

    def feature(self):
        """Feature this milestone"""
        self.is_featured = True
        self.updated_at = datetime.utcnow()

    def unfeature(self):
        """Unfeature this milestone"""
        self.is_featured = False
        self.updated_at = datetime.utcnow()

    def hide(self):
        """Hide this milestone"""
        self.is_visible = False
        self.updated_at = datetime.utcnow()

    def show(self):
        """Show this milestone"""
        self.is_visible = True
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_featured_milestones(cls, db_session, story_id: int = None) -> List['FounderMilestone']:
        """Get featured milestones"""
        query = db_session.query(cls).filter(
            cls.is_featured == True,
            cls.is_visible == True
        )
        
        if story_id:
            query = query.filter(cls.story_id == story_id)
        
        return query.order_by(cls.milestone_date.desc()).all()

    @classmethod
    def get_recent_milestones(cls, db_session, days: int = 90, story_id: int = None) -> List['FounderMilestone']:
        """Get recent milestones"""
        cutoff_date = date.today() - timedelta(days=days)
        
        query = db_session.query(cls).filter(
            cls.milestone_date >= cutoff_date,
            cls.is_visible == True
        )
        
        if story_id:
            query = query.filter(cls.story_id == story_id)
        
        return query.order_by(cls.milestone_date.desc()).all()

    def to_dict(self) -> Dict[str, Any]:
        """Convert milestone to dictionary"""
        result = super().to_dict()
        result.update({
            'days_ago': self.days_ago,
            'is_recent': self.is_recent,
            'has_metrics': self.has_metrics
        })
        return result
