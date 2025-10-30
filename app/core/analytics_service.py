"""
Analytics Service for Landing Page and CRM Integration Tracking
Provides comprehensive analytics and reporting for the landing page system
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc

from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.event import Event
from app.models.campaign import Campaign
from app.models.payment_transaction import PaymentTransaction
from app.models.co_creator_program import CoCreatorProgram
from app.models.crm_integration import CRMConnection
from app.core.metrics import (
    leads_generated_total, campaigns_created_total,
    track_metric
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and reporting on landing page performance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def track_lead_capture(self, lead: Lead, source: str = "landing_page", 
                                campaign_id: Optional[int] = None) -> bool:
        """Track lead capture event with integration insights"""
        try:
            # Create lead capture event
            event = Event.create_landing_page_event(
                event_name="lead_captured",
                lead_id=lead.id,
                anonymous_id=f"lead_{lead.id}",
                source=source,
                campaign_id=str(campaign_id) if campaign_id else None,
                crm_preference=lead.preferred_crm,
                readiness_segment=lead.readiness_segment,
                integration_complexity=lead.integration_complexity
            )
            
            self.db.add(event)
            
            # Update Prometheus metrics
            leads_generated_total.labels(
                source=source,
                quality=lead.readiness_segment or "unknown"
            ).inc()
            
            # Track custom metric
            await track_metric("lead_captured", {
                "lead_id": lead.id,
                "source": source,
                "crm_preference": lead.preferred_crm,
                "readiness_score": lead.crm_integration_readiness,
                "segment": lead.readiness_segment,
                "campaign_id": campaign_id
            })
            
            logger.info(f"Tracked lead capture: {lead.id} from {source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track lead capture: {e}")
            return False
    
    async def track_assessment_response(self, assessment: Assessment, 
                                      question_id: str, answer: Any) -> bool:
        """Track assessment response with integration insights"""
        try:
            # Create assessment response event
            event = Event.create_assessment_event(
                event_name="assessment_response",
                lead_id=assessment.lead_id,
                assessment_id=assessment.id,
                anonymous_id=f"assessment_{assessment.id}",
                question_id=question_id,
                answer=str(answer),
                current_crm=assessment.current_crm,
                assessment_type=assessment.assessment_type
            )
            
            self.db.add(event)
            
            # Track custom metric
            await track_metric("assessment_response", {
                "assessment_id": assessment.id,
                "lead_id": assessment.lead_id,
                "question_id": question_id,
                "current_crm": assessment.current_crm,
                "completion_percentage": assessment.completion_percentage
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track assessment response: {e}")
            return False
    
    async def track_assessment_completion(self, assessment: Assessment) -> bool:
        """Track assessment completion with scoring results"""
        try:
            # Create assessment completion event
            event = Event.create_assessment_event(
                event_name="assessment_completed",
                lead_id=assessment.lead_id,
                assessment_id=assessment.id,
                anonymous_id=f"assessment_{assessment.id}",
                overall_score=assessment.overall_score,
                readiness_level=assessment.readiness_level,
                segment=assessment.segment,
                current_crm=assessment.current_crm,
                completion_time=assessment.completion_time_seconds
            )
            
            self.db.add(event)
            
            # Track custom metric
            await track_metric("assessment_completed", {
                "assessment_id": assessment.id,
                "lead_id": assessment.lead_id,
                "overall_score": assessment.overall_score,
                "readiness_level": assessment.readiness_level,
                "segment": assessment.segment,
                "current_crm": assessment.current_crm,
                "completion_time_seconds": assessment.completion_time_seconds
            })
            
            logger.info(f"Tracked assessment completion: {assessment.id} - Score: {assessment.overall_score}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track assessment completion: {e}")
            return False
    
    async def track_crm_integration_engagement(self, lead_id: int, crm_type: str, 
                                             engagement_type: str, **kwargs) -> bool:
        """Track CRM integration engagement events"""
        try:
            # Create CRM integration event
            event = Event.create_crm_integration_event(
                event_name=engagement_type,
                crm_type=crm_type,
                lead_id=lead_id,
                anonymous_id=f"lead_{lead_id}",
                **kwargs
            )
            
            self.db.add(event)
            
            # Track custom metric
            await track_metric("crm_integration_engagement", {
                "lead_id": lead_id,
                "crm_type": crm_type,
                "engagement_type": engagement_type,
                **kwargs
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track CRM integration engagement: {e}")
            return False
    
    async def track_conversion_event(self, lead_id: int, conversion_type: str, 
                                   value: Optional[float] = None, **kwargs) -> bool:
        """Track conversion events with integration focus"""
        try:
            # Get lead for context
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            
            # Create conversion event
            event = Event.create_conversion(
                conversion_type=conversion_type,
                value=value,
                anonymous_id=f"lead_{lead_id}",
                lead_id=lead_id,
                crm_preference=lead.preferred_crm if lead else None,
                readiness_segment=lead.readiness_segment if lead else None,
                **kwargs
            )
            
            self.db.add(event)
            
            # Track custom metric
            await track_metric("conversion_event", {
                "lead_id": lead_id,
                "conversion_type": conversion_type,
                "value": value,
                "crm_preference": lead.preferred_crm if lead else None,
                "readiness_segment": lead.readiness_segment if lead else None,
                **kwargs
            })
            
            logger.info(f"Tracked conversion: {conversion_type} for lead {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track conversion event: {e}")
            return False
    
    async def get_landing_page_metrics(self, time_range_hours: int = 24, 
                                     campaign_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive landing page metrics"""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Base query filters
        base_filters = [Event.timestamp >= start_time]
        if campaign_id:
            base_filters.append(Event.campaign_id == str(campaign_id))
        
        # Page view metrics
        page_views = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.event_type == "page_view",
                *base_filters
            )
        ).scalar() or 0
        
        # Lead capture metrics
        leads_captured = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.event_type == "landing_page",
                Event.event_name == "lead_captured",
                *base_filters
            )
        ).scalar() or 0
        
        # Assessment metrics
        assessments_started = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.event_type == "assessment",
                Event.event_name == "assessment_started",
                *base_filters
            )
        ).scalar() or 0
        
        assessments_completed = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.event_type == "assessment",
                Event.event_name == "assessment_completed",
                *base_filters
            )
        ).scalar() or 0
        
        # Conversion metrics
        conversions = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.event_type == "conversion",
                *base_filters
            )
        ).scalar() or 0
        
        # CRM engagement metrics
        crm_engagements = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.event_type == "crm_integration",
                *base_filters
            )
        ).scalar() or 0
        
        # Calculate rates
        lead_capture_rate = (leads_captured / page_views * 100) if page_views > 0 else 0
        assessment_completion_rate = (assessments_completed / assessments_started * 100) if assessments_started > 0 else 0
        conversion_rate = (conversions / leads_captured * 100) if leads_captured > 0 else 0
        
        return {
            "time_range_hours": time_range_hours,
            "campaign_id": campaign_id,
            "traffic_metrics": {
                "page_views": page_views,
                "unique_visitors": page_views,  # Simplified for now
                "bounce_rate": 0.0  # Would need session tracking
            },
            "lead_metrics": {
                "leads_captured": leads_captured,
                "lead_capture_rate": lead_capture_rate
            },
            "assessment_metrics": {
                "assessments_started": assessments_started,
                "assessments_completed": assessments_completed,
                "completion_rate": assessment_completion_rate
            },
            "conversion_metrics": {
                "total_conversions": conversions,
                "conversion_rate": conversion_rate
            },
            "crm_engagement_metrics": {
                "total_engagements": crm_engagements,
                "engagement_rate": (crm_engagements / leads_captured * 100) if leads_captured > 0 else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_crm_integration_analytics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get CRM integration engagement analytics"""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # CRM preference distribution
        crm_preferences = self.db.query(
            Lead.preferred_crm,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.created_at >= start_time
        ).group_by(Lead.preferred_crm).all()
        
        # Integration readiness distribution
        readiness_segments = self.db.query(
            Lead.readiness_segment,
            func.count(Lead.id).label('count'),
            func.avg(Lead.crm_integration_readiness).label('avg_score')
        ).filter(
            Lead.created_at >= start_time
        ).group_by(Lead.readiness_segment).all()
        
        # CRM engagement events
        crm_events = self.db.query(
            Event.properties['crm_type'].astext.label('crm_type'),
            Event.event_name,
            func.count(Event.id).label('count')
        ).filter(
            and_(
                Event.event_type == "crm_integration",
                Event.timestamp >= start_time
            )
        ).group_by(
            Event.properties['crm_type'].astext,
            Event.event_name
        ).all()
        
        return {
            "time_range_hours": time_range_hours,
            "crm_preferences": {
                pref or "unknown": count for pref, count in crm_preferences
            },
            "readiness_segments": {
                segment or "unknown": {
                    "count": count,
                    "avg_score": float(avg_score or 0)
                } for segment, count, avg_score in readiness_segments
            },
            "crm_engagement_events": [
                {
                    "crm_type": crm_type or "unknown",
                    "event_name": event_name,
                    "count": count
                } for crm_type, event_name, count in crm_events
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_conversion_funnel_analysis(self, time_range_hours: int = 24, 
                                           campaign_id: Optional[int] = None) -> Dict[str, Any]:
        """Get conversion funnel analysis with integration focus"""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Base query for leads in time range
        lead_query = self.db.query(Lead).filter(Lead.created_at >= start_time)
        if campaign_id:
            lead_query = lead_query.filter(Lead.campaign_id == campaign_id)
        
        total_leads = lead_query.count()
        
        # Funnel stages
        leads_with_assessment = lead_query.join(Assessment).count()
        completed_assessments = lead_query.join(Assessment).filter(
            Assessment.is_completed == True
        ).count()
        
        qualified_leads = lead_query.filter(
            Lead.readiness_segment.in_(["warm", "hot"])
        ).count()
        
        co_creator_conversions = self.db.query(PaymentTransaction).join(Lead).filter(
            and_(
                Lead.created_at >= start_time,
                PaymentTransaction.status == "completed",
                PaymentTransaction.amount == 250.0  # Co-creator program amount
            )
        ).count()
        
        # Calculate conversion rates
        assessment_start_rate = (leads_with_assessment / total_leads * 100) if total_leads > 0 else 0
        assessment_completion_rate = (completed_assessments / leads_with_assessment * 100) if leads_with_assessment > 0 else 0
        qualification_rate = (qualified_leads / completed_assessments * 100) if completed_assessments > 0 else 0
        co_creator_conversion_rate = (co_creator_conversions / qualified_leads * 100) if qualified_leads > 0 else 0
        
        # Segment breakdown
        segment_breakdown = self.db.query(
            Lead.readiness_segment,
            func.count(Lead.id).label('count'),
            func.avg(Lead.crm_integration_readiness).label('avg_readiness')
        ).filter(
            Lead.created_at >= start_time
        ).group_by(Lead.readiness_segment).all()
        
        return {
            "time_range_hours": time_range_hours,
            "campaign_id": campaign_id,
            "funnel_stages": {
                "total_leads": total_leads,
                "assessment_started": leads_with_assessment,
                "assessment_completed": completed_assessments,
                "qualified_leads": qualified_leads,
                "co_creator_conversions": co_creator_conversions
            },
            "conversion_rates": {
                "assessment_start_rate": assessment_start_rate,
                "assessment_completion_rate": assessment_completion_rate,
                "qualification_rate": qualification_rate,
                "co_creator_conversion_rate": co_creator_conversion_rate,
                "overall_conversion_rate": (co_creator_conversions / total_leads * 100) if total_leads > 0 else 0
            },
            "segment_breakdown": {
                segment or "unknown": {
                    "count": count,
                    "avg_readiness": float(avg_readiness or 0)
                } for segment, count, avg_readiness in segment_breakdown
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_weekly_metrics_report(self) -> Dict[str, Any]:
        """Generate comprehensive weekly metrics report"""
        # Get metrics for the last 7 days
        weekly_metrics = await self.get_landing_page_metrics(time_range_hours=168)  # 7 days
        crm_analytics = await self.get_crm_integration_analytics(time_range_hours=168)
        funnel_analysis = await self.get_conversion_funnel_analysis(time_range_hours=168)
        
        # Get campaign performance
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_campaigns = self.db.query(Campaign).filter(
            and_(
                Campaign.campaign_type == "landing_page",
                Campaign.created_at >= week_ago
            )
        ).all()
        
        campaign_performance = []
        for campaign in active_campaigns:
            campaign_metrics = await self.get_landing_page_metrics(
                time_range_hours=168,
                campaign_id=campaign.id
            )
            campaign_performance.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "status": campaign.status,
                "metrics": campaign_metrics,
                "performance_summary": campaign.get_landing_page_performance_summary()
            })
        
        # Co-creator program metrics
        co_creator_metrics = await self._get_co_creator_program_metrics(time_range_hours=168)
        
        return {
            "report_period": "weekly",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_leads": weekly_metrics["lead_metrics"]["leads_captured"],
                "assessment_completion_rate": weekly_metrics["assessment_metrics"]["completion_rate"],
                "conversion_rate": weekly_metrics["conversion_metrics"]["conversion_rate"],
                "crm_engagement_rate": weekly_metrics["crm_engagement_metrics"]["engagement_rate"]
            },
            "landing_page_metrics": weekly_metrics,
            "crm_integration_analytics": crm_analytics,
            "conversion_funnel_analysis": funnel_analysis,
            "campaign_performance": campaign_performance,
            "co_creator_program_metrics": co_creator_metrics
        }
    
    async def _get_co_creator_program_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get co-creator program specific metrics"""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Get program status
        program = self.db.query(CoCreatorProgram).first()
        
        # Payment metrics
        payments = self.db.query(PaymentTransaction).filter(
            and_(
                PaymentTransaction.created_at >= start_time,
                PaymentTransaction.amount == 250.0
            )
        ).all()
        
        successful_payments = [p for p in payments if p.status == "completed"]
        failed_payments = [p for p in payments if p.status == "failed"]
        
        return {
            "program_status": {
                "seats_filled": program.seats_filled if program else 0,
                "total_seats": program.total_seats if program else 25,
                "seats_remaining": program.seats_remaining if program else 25,
                "is_active": program.is_active if program else False
            },
            "payment_metrics": {
                "total_attempts": len(payments),
                "successful_payments": len(successful_payments),
                "failed_payments": len(failed_payments),
                "success_rate": (len(successful_payments) / len(payments) * 100) if payments else 0,
                "total_revenue": sum(p.amount for p in successful_payments)
            },
            "time_range_hours": time_range_hours,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def update_campaign_metrics(self, campaign_id: int) -> bool:
        """Update campaign metrics with latest data"""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign or not campaign.is_landing_page_campaign:
                return False
            
            # Get latest metrics
            landing_metrics = await self.get_landing_page_metrics(
                time_range_hours=24,
                campaign_id=campaign_id
            )
            
            crm_analytics = await self.get_crm_integration_analytics(time_range_hours=24)
            funnel_analysis = await self.get_conversion_funnel_analysis(
                time_range_hours=24,
                campaign_id=campaign_id
            )
            
            # Update campaign metrics
            campaign.update_landing_page_metrics(landing_metrics["traffic_metrics"])
            campaign.update_assessment_metrics(landing_metrics["assessment_metrics"])
            campaign.update_crm_engagement_metrics(landing_metrics["crm_engagement_metrics"])
            campaign.update_conversion_funnel_metrics(funnel_analysis["funnel_stages"])
            
            self.db.commit()
            
            logger.info(f"Updated metrics for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update campaign metrics: {e}")
            self.db.rollback()
            return False