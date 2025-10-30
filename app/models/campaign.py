"""
Campaign model for marketing campaign management
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Campaign(Base, TimestampMixin):
    """Campaign model for marketing campaign orchestration"""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(255), unique=True, nullable=False, index=True)  # UUID or external ID

    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Campaign metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="draft")  # draft, active, paused, completed, failed

    # Campaign configuration
    campaign_type = Column(String(100), nullable=False)  # lead_generation, content_creation, full_funnel, landing_page
    target_audience = Column(JSON, nullable=False, default=dict)
    content_requirements = Column(JSON, default=dict)
    ad_platforms = Column(JSON, default=list)  # ["google_ads", "linkedin", "facebook"]
    
    # Landing page specific fields
    landing_page_url = Column(String(500))  # URL of the landing page
    landing_page_variant = Column(String(100))  # A/B test variant identifier
    crm_integration_focus = Column(String(100))  # Primary CRM integration being promoted
    assessment_completion_target = Column(Float, default=80.0)  # Target completion rate %
    co_creator_conversion_target = Column(Float, default=35.0)  # Target conversion rate %
    
    # Landing page performance metrics
    landing_page_metrics = Column(JSON, default=dict)  # Landing page specific KPIs
    assessment_metrics = Column(JSON, default=dict)  # Assessment completion and scoring metrics
    crm_engagement_metrics = Column(JSON, default=dict)  # CRM integration engagement tracking
    conversion_funnel_metrics = Column(JSON, default=dict)  # Funnel analysis data

    # Budget and spending
    budget = Column(Float, default=0.0)
    spent = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")

    # Performance metrics
    performance_metrics = Column(JSON, default=dict)  # CTR, CPC, CPA, ROAS, etc.
    overall_score = Column(Float, default=0.0)  # 0-100 performance score

    # Agent execution tracking
    agent_sequence = Column(JSON, default=list)  # ["lead_generation", "content_creator", "ad_manager"]
    current_agent = Column(String(100))
    next_agent = Column(String(100))

    # Results and outputs
    qualified_leads = Column(JSON, default=list)  # List of lead objects
    generated_content = Column(JSON, default=list)  # List of content objects
    ad_creatives = Column(JSON, default=list)  # List of ad creative objects

    # Error handling
    errors = Column(JSON, default=list)  # List of error objects
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Optimization
    optimization_attempts = Column(Integer, default=0)
    last_optimization = Column(DateTime)

    # Scheduling
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)

    # Timestamps (inherited from TimestampMixin)

    # Relationships
    user = relationship("User", back_populates="campaigns")
    leads = relationship("Lead", back_populates="campaign", cascade="all, delete-orphan")
    contents = relationship("Content", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}', user_id={self.user_id})>"

    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        return self.status == "active"

    @property
    def is_completed(self) -> bool:
        """Check if campaign is completed"""
        return self.status in ["completed", "failed"]

    @property
    def duration(self) -> Optional[float]:
        """Get campaign duration in hours"""
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 3600
        return None

    @property
    def budget_remaining(self) -> float:
        """Get remaining budget"""
        return max(0, self.budget - self.spent)

    @property
    def roi(self) -> Optional[float]:
        """Calculate return on investment"""
        if self.spent > 0 and self.performance_metrics:
            revenue = self.performance_metrics.get("total_revenue", 0)
            return (revenue - self.spent) / self.spent
        return None

    def start_campaign(self):
        """Mark campaign as started"""
        self.status = "active"
        self.actual_start = datetime.utcnow()
        self.current_agent = self.agent_sequence[0] if self.agent_sequence else None

    def complete_campaign(self):
        """Mark campaign as completed"""
        self.status = "completed"
        self.actual_end = datetime.utcnow()

    def fail_campaign(self, error: str):
        """Mark campaign as failed"""
        self.status = "failed"
        self.actual_end = datetime.utcnow()
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "agent": self.current_agent
        })

    def pause_campaign(self):
        """Pause the campaign"""
        if self.status == "active":
            self.status = "paused"

    def resume_campaign(self):
        """Resume the campaign"""
        if self.status == "paused":
            self.status = "active"

    def update_performance(self, metrics: Dict[str, Any]):
        """Update campaign performance metrics"""
        self.performance_metrics.update(metrics)
        self.overall_score = self._calculate_overall_score()
        self.updated_at = datetime.utcnow()

    def _calculate_overall_score(self) -> float:
        """Calculate overall campaign performance score"""
        metrics = self.performance_metrics
        score = 0.0

        # Lead quality score (30 points)
        lead_count = len(self.qualified_leads)
        if lead_count > 0:
            avg_score = sum(lead.get("score", 0) for lead in self.qualified_leads) / lead_count
            score += min(30, avg_score * 30)

        # Content performance (25 points)
        content_count = len(self.generated_content)
        if content_count > 0:
            avg_seo = sum(content.get("seo_score", 0) for content in self.generated_content) / content_count
            score += min(25, avg_seo * 0.25)

        # Ad performance (25 points)
        if metrics.get("roas", 0) > 0:
            roas = metrics["roas"]
            if roas >= 3.0:
                score += 25
            elif roas >= 2.0:
                score += 20
            elif roas >= 1.0:
                score += 10

        # Error-free execution (20 points)
        if not self.errors:
            score += 20
        elif len(self.errors) <= 2:
            score += 10

        return min(100.0, score)

    def can_retry(self) -> bool:
        """Check if campaign can be retried"""
        return self.retry_count < self.max_retries and self.status == "failed"

    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1

    def advance_to_next_agent(self):
        """Advance to the next agent in sequence"""
        if not self.agent_sequence:
            return

        try:
            current_index = self.agent_sequence.index(self.current_agent)
            if current_index < len(self.agent_sequence) - 1:
                self.current_agent = self.agent_sequence[current_index + 1]
                self.next_agent = self.agent_sequence[current_index + 2] if current_index + 2 < len(self.agent_sequence) else None
            else:
                # Campaign completed
                self.complete_campaign()
        except ValueError:
            # Current agent not in sequence
            pass

    def update_landing_page_metrics(self, metrics: Dict[str, Any]):
        """Update landing page specific metrics"""
        if not self.landing_page_metrics:
            self.landing_page_metrics = {}
        
        self.landing_page_metrics.update(metrics)
        self.updated_at = datetime.utcnow()

    def update_assessment_metrics(self, metrics: Dict[str, Any]):
        """Update assessment completion and scoring metrics"""
        if not self.assessment_metrics:
            self.assessment_metrics = {}
        
        self.assessment_metrics.update(metrics)
        self.updated_at = datetime.utcnow()

    def update_crm_engagement_metrics(self, metrics: Dict[str, Any]):
        """Update CRM integration engagement metrics"""
        if not self.crm_engagement_metrics:
            self.crm_engagement_metrics = {}
        
        self.crm_engagement_metrics.update(metrics)
        self.updated_at = datetime.utcnow()

    def update_conversion_funnel_metrics(self, metrics: Dict[str, Any]):
        """Update conversion funnel analysis metrics"""
        if not self.conversion_funnel_metrics:
            self.conversion_funnel_metrics = {}
        
        self.conversion_funnel_metrics.update(metrics)
        self.updated_at = datetime.utcnow()

    def get_landing_page_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of landing page performance"""
        return {
            "campaign_id": self.campaign_id,
            "campaign_name": self.name,
            "campaign_type": self.campaign_type,
            "landing_page_url": self.landing_page_url,
            "variant": self.landing_page_variant,
            "crm_focus": self.crm_integration_focus,
            "targets": {
                "assessment_completion": self.assessment_completion_target,
                "co_creator_conversion": self.co_creator_conversion_target
            },
            "metrics": {
                "landing_page": self.landing_page_metrics or {},
                "assessment": self.assessment_metrics or {},
                "crm_engagement": self.crm_engagement_metrics or {},
                "conversion_funnel": self.conversion_funnel_metrics or {}
            },
            "overall_performance": self.performance_metrics or {},
            "status": self.status,
            "duration_hours": self.duration,
            "roi": self.roi
        }

    @property
    def is_landing_page_campaign(self) -> bool:
        """Check if this is a landing page campaign"""
        return self.campaign_type == "landing_page"

    def calculate_assessment_completion_rate(self) -> float:
        """Calculate assessment completion rate"""
        if not self.assessment_metrics:
            return 0.0
        
        started = self.assessment_metrics.get("assessments_started", 0)
        completed = self.assessment_metrics.get("assessments_completed", 0)
        
        if started == 0:
            return 0.0
        
        return (completed / started) * 100

    def calculate_co_creator_conversion_rate(self) -> float:
        """Calculate co-creator program conversion rate"""
        if not self.conversion_funnel_metrics:
            return 0.0
        
        qualified_leads = self.conversion_funnel_metrics.get("qualified_leads", 0)
        co_creator_conversions = self.conversion_funnel_metrics.get("co_creator_conversions", 0)
        
        if qualified_leads == 0:
            return 0.0
        
        return (co_creator_conversions / qualified_leads) * 100

    def is_meeting_targets(self) -> Dict[str, bool]:
        """Check if campaign is meeting its targets"""
        assessment_rate = self.calculate_assessment_completion_rate()
        conversion_rate = self.calculate_co_creator_conversion_rate()
        
        return {
            "assessment_completion": assessment_rate >= self.assessment_completion_target,
            "co_creator_conversion": conversion_rate >= self.co_creator_conversion_target,
            "overall": (assessment_rate >= self.assessment_completion_target and 
                       conversion_rate >= self.co_creator_conversion_target)
        }