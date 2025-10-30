"""
Real-time Dashboard Service for Landing Page Analytics
Provides real-time dashboard data and KPI tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.event import Event
from app.models.campaign import Campaign
from app.models.payment_transaction import PaymentTransaction
from app.models.co_creator_program import CoCreatorProgram
from app.core.analytics_service import AnalyticsService
from app.core.metrics import track_metric

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for real-time dashboard data and KPIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)
    
    async def get_real_time_dashboard(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive real-time dashboard data"""
        try:
            # Get current timestamp
            now = datetime.utcnow()
            start_time = now - timedelta(hours=time_range_hours)
            
            # Get core metrics
            core_metrics = await self._get_core_metrics(start_time, now)
            
            # Get conversion funnel data
            funnel_data = await self._get_conversion_funnel_data(start_time, now)
            
            # Get CRM integration insights
            crm_insights = await self._get_crm_integration_insights(start_time, now)
            
            # Get campaign performance
            campaign_performance = await self._get_campaign_performance(start_time, now)
            
            # Get co-creator program status
            co_creator_status = await self._get_co_creator_program_status()
            
            # Get recent activity feed
            recent_activity = await self._get_recent_activity(limit=20)
            
            # Calculate trends
            trends = await self._calculate_trends(time_range_hours)
            
            return {
                "timestamp": now.isoformat(),
                "time_range_hours": time_range_hours,
                "core_metrics": core_metrics,
                "conversion_funnel": funnel_data,
                "crm_insights": crm_insights,
                "campaign_performance": campaign_performance,
                "co_creator_program": co_creator_status,
                "recent_activity": recent_activity,
                "trends": trends,
                "alerts": await self._get_active_alerts()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time dashboard data: {e}")
            raise
    
    async def _get_core_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get core KPI metrics"""
        # Total leads in time range
        total_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.created_at.between(start_time, end_time)
        ).scalar() or 0
        
        # Assessments started and completed
        assessments_started = self.db.query(func.count(Assessment.id)).filter(
            Assessment.created_at.between(start_time, end_time)
        ).scalar() or 0
        
        assessments_completed = self.db.query(func.count(Assessment.id)).filter(
            and_(
                Assessment.created_at.between(start_time, end_time),
                Assessment.is_completed == True
            )
        ).scalar() or 0
        
        # Conversions (payments)
        conversions = self.db.query(func.count(PaymentTransaction.id)).filter(
            and_(
                PaymentTransaction.created_at.between(start_time, end_time),
                PaymentTransaction.status == "completed"
            )
        ).scalar() or 0
        
        # Page views
        page_views = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.timestamp.between(start_time, end_time),
                Event.event_type == "page_view"
            )
        ).scalar() or 0
        
        # Calculate rates
        lead_capture_rate = (total_leads / page_views * 100) if page_views > 0 else 0
        assessment_completion_rate = (assessments_completed / assessments_started * 100) if assessments_started > 0 else 0
        conversion_rate = (conversions / total_leads * 100) if total_leads > 0 else 0
        
        return {
            "page_views": page_views,
            "total_leads": total_leads,
            "assessments_started": assessments_started,
            "assessments_completed": assessments_completed,
            "conversions": conversions,
            "rates": {
                "lead_capture_rate": round(lead_capture_rate, 2),
                "assessment_completion_rate": round(assessment_completion_rate, 2),
                "conversion_rate": round(conversion_rate, 2)
            }
        }
    
    async def _get_conversion_funnel_data(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get conversion funnel data with drop-off analysis"""
        # Get leads by segment
        segment_counts = self.db.query(
            Lead.readiness_segment,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.created_at.between(start_time, end_time)
        ).group_by(Lead.readiness_segment).all()
        
        segments = {segment or "unknown": count for segment, count in segment_counts}
        
        # Get funnel stages
        total_visitors = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.timestamp.between(start_time, end_time),
                Event.event_type == "page_view"
            )
        ).scalar() or 0
        
        leads_captured = segments.get("cold", 0) + segments.get("warm", 0) + segments.get("hot", 0)
        qualified_leads = segments.get("warm", 0) + segments.get("hot", 0)
        hot_leads = segments.get("hot", 0)
        
        # Calculate conversion rates between stages
        visitor_to_lead = (leads_captured / total_visitors * 100) if total_visitors > 0 else 0
        lead_to_qualified = (qualified_leads / leads_captured * 100) if leads_captured > 0 else 0
        qualified_to_hot = (hot_leads / qualified_leads * 100) if qualified_leads > 0 else 0
        
        return {
            "stages": {
                "visitors": total_visitors,
                "leads_captured": leads_captured,
                "qualified_leads": qualified_leads,
                "hot_leads": hot_leads
            },
            "conversion_rates": {
                "visitor_to_lead": round(visitor_to_lead, 2),
                "lead_to_qualified": round(lead_to_qualified, 2),
                "qualified_to_hot": round(qualified_to_hot, 2)
            },
            "segment_distribution": segments
        }
    
    async def _get_crm_integration_insights(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get CRM integration insights and preferences"""
        # CRM preferences distribution
        crm_preferences = self.db.query(
            Lead.preferred_crm,
            func.count(Lead.id).label('count'),
            func.avg(Lead.crm_integration_readiness).label('avg_readiness')
        ).filter(
            Lead.created_at.between(start_time, end_time)
        ).group_by(Lead.preferred_crm).all()
        
        crm_data = {}
        for crm, count, avg_readiness in crm_preferences:
            crm_data[crm or "unknown"] = {
                "count": count,
                "avg_readiness": round(float(avg_readiness or 0), 1)
            }
        
        # Integration complexity distribution
        complexity_dist = self.db.query(
            Lead.integration_complexity,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.created_at.between(start_time, end_time)
        ).group_by(Lead.integration_complexity).all()
        
        complexity_data = {complexity or "unknown": count for complexity, count in complexity_dist}
        
        # CRM engagement events
        crm_events = self.db.query(func.count(Event.id)).filter(
            and_(
                Event.timestamp.between(start_time, end_time),
                Event.event_type == "crm_integration"
            )
        ).scalar() or 0
        
        return {
            "crm_preferences": crm_data,
            "integration_complexity": complexity_data,
            "total_crm_engagements": crm_events,
            "top_crm_systems": sorted(crm_data.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
        }
    
    async def _get_campaign_performance(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get campaign performance data"""
        # Get active landing page campaigns
        active_campaigns = self.db.query(Campaign).filter(
            and_(
                Campaign.status == "active",
                Campaign.campaign_type == "landing_page",
                Campaign.created_at <= end_time
            )
        ).all()
        
        campaign_data = []
        for campaign in active_campaigns:
            # Get campaign-specific metrics
            campaign_leads = self.db.query(func.count(Lead.id)).filter(
                and_(
                    Lead.campaign_id == campaign.id,
                    Lead.created_at.between(start_time, end_time)
                )
            ).scalar() or 0
            
            campaign_data.append({
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "crm_focus": campaign.crm_integration_focus,
                "leads_generated": campaign_leads,
                "performance_score": campaign.overall_score,
                "targets_met": campaign.is_meeting_targets()
            })
        
        return {
            "active_campaigns": len(active_campaigns),
            "campaign_details": campaign_data,
            "total_campaign_leads": sum(c["leads_generated"] for c in campaign_data)
        }
    
    async def _get_co_creator_program_status(self) -> Dict[str, Any]:
        """Get co-creator program status and metrics"""
        program = self.db.query(CoCreatorProgram).first()
        
        if not program:
            return {
                "is_active": False,
                "seats_filled": 0,
                "total_seats": 25,
                "seats_remaining": 25,
                "fill_rate": 0.0,
                "recent_signups": 0
            }
        
        # Get recent signups (last 24 hours)
        recent_signups = self.db.query(func.count(PaymentTransaction.id)).filter(
            and_(
                PaymentTransaction.created_at >= datetime.utcnow() - timedelta(hours=24),
                PaymentTransaction.status == "completed",
                PaymentTransaction.amount == 250.0
            )
        ).scalar() or 0
        
        fill_rate = (program.seats_filled / program.total_seats * 100) if program.total_seats > 0 else 0
        
        return {
            "is_active": program.is_active,
            "seats_filled": program.seats_filled,
            "total_seats": program.total_seats,
            "seats_remaining": program.seats_remaining,
            "fill_rate": round(fill_rate, 1),
            "recent_signups": recent_signups,
            "urgency_level": "high" if program.seats_remaining <= 5 else "medium" if program.seats_remaining <= 10 else "low"
        }
    
    async def _get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activity feed"""
        # Get recent events
        recent_events = self.db.query(Event).filter(
            Event.event_type.in_(["landing_page", "assessment", "conversion", "crm_integration"])
        ).order_by(desc(Event.timestamp)).limit(limit).all()
        
        activity_feed = []
        for event in recent_events:
            activity_item = {
                "timestamp": event.timestamp.isoformat(),
                "type": event.event_type,
                "event": event.event_name,
                "description": self._format_activity_description(event)
            }
            
            # Add lead context if available
            if event.properties and event.properties.get("lead_id"):
                lead_id = event.properties["lead_id"]
                lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
                if lead:
                    activity_item["lead"] = {
                        "id": lead.id,
                        "name": lead.full_name,
                        "company": lead.company,
                        "segment": lead.readiness_segment
                    }
            
            activity_feed.append(activity_item)
        
        return activity_feed
    
    def _format_activity_description(self, event: Event) -> str:
        """Format activity description for the feed"""
        if event.event_type == "landing_page":
            if event.event_name == "lead_captured":
                return "New lead captured from landing page"
        elif event.event_type == "assessment":
            if event.event_name == "assessment_completed":
                score = event.properties.get("overall_score", 0) if event.properties else 0
                return f"Assessment completed with {score}% readiness score"
        elif event.event_type == "conversion":
            return f"Conversion: {event.event_name}"
        elif event.event_type == "crm_integration":
            crm_type = event.properties.get("crm_type", "unknown") if event.properties else "unknown"
            return f"CRM integration activity: {crm_type}"
        
        return f"{event.event_type}: {event.event_name}"
    
    async def _calculate_trends(self, time_range_hours: int) -> Dict[str, Any]:
        """Calculate trends compared to previous period"""
        try:
            current_period_start = datetime.utcnow() - timedelta(hours=time_range_hours)
            previous_period_start = current_period_start - timedelta(hours=time_range_hours)
            
            # Get current period metrics
            current_metrics = await self._get_core_metrics(current_period_start, datetime.utcnow())
            
            # Get previous period metrics
            previous_metrics = await self._get_core_metrics(previous_period_start, current_period_start)
            
            # Calculate trends
            trends = {}
            for metric in ["total_leads", "assessments_completed", "conversions"]:
                current_value = current_metrics.get(metric, 0)
                previous_value = previous_metrics.get(metric, 0)
                
                if previous_value > 0:
                    change_percent = ((current_value - previous_value) / previous_value) * 100
                else:
                    change_percent = 100.0 if current_value > 0 else 0.0
                
                trends[metric] = {
                    "current": current_value,
                    "previous": previous_value,
                    "change_percent": round(change_percent, 1),
                    "trend": "up" if change_percent > 0 else "down" if change_percent < 0 else "stable"
                }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to calculate trends: {e}")
            return {}
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active performance alerts"""
        alerts = []
        
        try:
            # Get recent metrics for alert checking
            recent_metrics = await self._get_core_metrics(
                datetime.utcnow() - timedelta(hours=1),
                datetime.utcnow()
            )
            
            # Check conversion rate
            conversion_rate = recent_metrics["rates"]["conversion_rate"]
            if conversion_rate < 5.0 and recent_metrics["total_leads"] > 5:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"Low conversion rate: {conversion_rate}%",
                    "metric": "conversion_rate",
                    "value": conversion_rate,
                    "threshold": 5.0
                })
            
            # Check assessment completion rate
            completion_rate = recent_metrics["rates"]["assessment_completion_rate"]
            if completion_rate < 50.0 and recent_metrics["assessments_started"] > 3:
                alerts.append({
                    "type": "performance",
                    "severity": "info",
                    "message": f"Low assessment completion: {completion_rate}%",
                    "metric": "assessment_completion_rate",
                    "value": completion_rate,
                    "threshold": 50.0
                })
            
            # Check co-creator program capacity
            co_creator_status = await self._get_co_creator_program_status()
            if co_creator_status["seats_remaining"] <= 5 and co_creator_status["is_active"]:
                alerts.append({
                    "type": "capacity",
                    "severity": "high",
                    "message": f"Only {co_creator_status['seats_remaining']} co-creator seats remaining",
                    "metric": "co_creator_seats",
                    "value": co_creator_status["seats_remaining"],
                    "threshold": 5
                })
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
        
        return alerts
    
    async def get_performance_summary(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get a concise performance summary for quick overview"""
        try:
            dashboard_data = await self.get_real_time_dashboard(time_range_hours)
            
            core_metrics = dashboard_data["core_metrics"]
            funnel_data = dashboard_data["conversion_funnel"]
            co_creator_status = dashboard_data["co_creator_program"]
            
            # Calculate overall health score
            health_score = 0
            
            # Conversion rate contributes 40%
            conversion_rate = core_metrics["rates"]["conversion_rate"]
            if conversion_rate >= 10:
                health_score += 40
            elif conversion_rate >= 5:
                health_score += 25
            elif conversion_rate >= 2:
                health_score += 15
            
            # Assessment completion contributes 30%
            completion_rate = core_metrics["rates"]["assessment_completion_rate"]
            if completion_rate >= 70:
                health_score += 30
            elif completion_rate >= 50:
                health_score += 20
            elif completion_rate >= 30:
                health_score += 10
            
            # Lead capture rate contributes 20%
            capture_rate = core_metrics["rates"]["lead_capture_rate"]
            if capture_rate >= 15:
                health_score += 20
            elif capture_rate >= 10:
                health_score += 15
            elif capture_rate >= 5:
                health_score += 10
            
            # Co-creator program progress contributes 10%
            fill_rate = co_creator_status["fill_rate"]
            if fill_rate >= 80:
                health_score += 10
            elif fill_rate >= 50:
                health_score += 7
            elif fill_rate >= 25:
                health_score += 5
            
            # Determine health status
            if health_score >= 80:
                health_status = "excellent"
            elif health_score >= 60:
                health_status = "good"
            elif health_score >= 40:
                health_status = "fair"
            else:
                health_status = "needs_attention"
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "time_range_hours": time_range_hours,
                "health_score": health_score,
                "health_status": health_status,
                "key_metrics": {
                    "total_leads": core_metrics["total_leads"],
                    "conversion_rate": core_metrics["rates"]["conversion_rate"],
                    "assessment_completion_rate": core_metrics["rates"]["assessment_completion_rate"],
                    "co_creator_fill_rate": co_creator_status["fill_rate"]
                },
                "alerts_count": len(dashboard_data["alerts"]),
                "active_campaigns": dashboard_data["campaign_performance"]["active_campaigns"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            raise