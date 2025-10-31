"""
Landing Page Monitoring Integration
Extends existing monitoring infrastructure for landing page specific KPIs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.analytics_service import AnalyticsService
from app.core.dashboard_service import DashboardService
from app.core.crm_integration_monitoring import get_integration_health_summary
# from app.core.metrics import track_metric  # Function not available
from app.models.campaign import Campaign
from app.models.lead import Lead

logger = logging.getLogger(__name__)


class LandingPageMonitor:
    """Monitor for landing page performance and integration with existing monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)
        self.dashboard = DashboardService(db)
        
        # Performance thresholds
        self.thresholds = {
            "conversion_rate_warning": 5.0,
            "conversion_rate_critical": 2.0,
            "assessment_completion_warning": 50.0,
            "assessment_completion_critical": 30.0,
            "lead_capture_rate_warning": 10.0,
            "lead_capture_rate_critical": 5.0,
            "co_creator_seats_critical": 5,
            "co_creator_seats_warning": 10
        }
    
    async def get_comprehensive_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report combining landing page and CRM integration monitoring"""
        try:
            # Get landing page performance
            landing_performance = await self.dashboard.get_performance_summary(time_range_hours=24)
            
            # Get CRM integration health
            crm_health = await get_integration_health_summary(self.db)
            
            # Get campaign health
            campaign_health = await self._get_campaign_health()
            
            # Calculate overall system health
            overall_health = self._calculate_overall_health(
                landing_performance, crm_health, campaign_health
            )
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": overall_health,
                "components": {
                    "landing_page": {
                        "health_status": landing_performance["health_status"],
                        "health_score": landing_performance["health_score"],
                        "key_metrics": landing_performance["key_metrics"],
                        "alerts_count": landing_performance["alerts_count"]
                    },
                    "crm_integration": {
                        "health_status": crm_health["overall_health"],
                        "total_connections": crm_health["total_connections"],
                        "healthy_connections": crm_health["healthy_connections"],
                        "sync_success_rate": crm_health["sync_success_rate"]
                    },
                    "campaigns": campaign_health
                },
                "recommendations": await self._generate_health_recommendations(
                    landing_performance, crm_health, campaign_health
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive health report: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": "error",
                "error": str(e)
            }
    
    async def _get_campaign_health(self) -> Dict[str, Any]:
        """Get health status of active campaigns"""
        try:
            active_campaigns = self.db.query(Campaign).filter(
                Campaign.status == "active",
                Campaign.campaign_type == "landing_page"
            ).all()
            
            healthy_campaigns = 0
            total_campaigns = len(active_campaigns)
            campaign_details = []
            
            for campaign in active_campaigns:
                targets_met = campaign.is_meeting_targets()
                is_healthy = targets_met["overall"]
                
                if is_healthy:
                    healthy_campaigns += 1
                
                campaign_details.append({
                    "id": campaign.id,
                    "name": campaign.name,
                    "is_healthy": is_healthy,
                    "targets_met": targets_met,
                    "performance_score": campaign.overall_score
                })
            
            health_percentage = (healthy_campaigns / total_campaigns * 100) if total_campaigns > 0 else 100
            
            return {
                "total_campaigns": total_campaigns,
                "healthy_campaigns": healthy_campaigns,
                "health_percentage": health_percentage,
                "status": "healthy" if health_percentage >= 80 else "warning" if health_percentage >= 50 else "critical",
                "campaign_details": campaign_details
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign health: {e}")
            return {
                "total_campaigns": 0,
                "healthy_campaigns": 0,
                "health_percentage": 0,
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_overall_health(self, landing_performance: Dict[str, Any], 
                                 crm_health: Dict[str, Any], 
                                 campaign_health: Dict[str, Any]) -> str:
        """Calculate overall system health status"""
        try:
            # Weight different components
            landing_weight = 0.5
            crm_weight = 0.3
            campaign_weight = 0.2
            
            # Convert health statuses to scores
            health_scores = {
                "excellent": 100,
                "good": 80,
                "healthy": 80,
                "fair": 60,
                "warning": 40,
                "needs_attention": 30,
                "critical": 20,
                "unhealthy": 10,
                "error": 0
            }
            
            landing_score = health_scores.get(landing_performance["health_status"], 0)
            crm_score = health_scores.get(crm_health["overall_health"], 0)
            campaign_score = health_scores.get(campaign_health["status"], 0)
            
            # Calculate weighted average
            overall_score = (
                landing_score * landing_weight +
                crm_score * crm_weight +
                campaign_score * campaign_weight
            )
            
            # Convert back to health status
            if overall_score >= 80:
                return "healthy"
            elif overall_score >= 60:
                return "warning"
            elif overall_score >= 30:
                return "critical"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"Failed to calculate overall health: {e}")
            return "error"
    
    async def _generate_health_recommendations(self, landing_performance: Dict[str, Any],
                                             crm_health: Dict[str, Any],
                                             campaign_health: Dict[str, Any]) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        try:
            # Landing page recommendations
            key_metrics = landing_performance["key_metrics"]
            
            if key_metrics["conversion_rate"] < self.thresholds["conversion_rate_warning"]:
                recommendations.append(
                    f"Conversion rate is {key_metrics['conversion_rate']:.1f}% - "
                    "Consider optimizing landing page CTAs and value proposition"
                )
            
            if key_metrics["assessment_completion_rate"] < self.thresholds["assessment_completion_warning"]:
                recommendations.append(
                    f"Assessment completion rate is {key_metrics['assessment_completion_rate']:.1f}% - "
                    "Review assessment length and question clarity"
                )
            
            # CRM integration recommendations
            if crm_health["sync_success_rate"] < 90:
                recommendations.append(
                    f"CRM sync success rate is {crm_health['sync_success_rate']:.1f}% - "
                    "Review CRM connection health and error logs"
                )
            
            # Campaign recommendations
            if campaign_health["health_percentage"] < 80:
                recommendations.append(
                    f"Only {campaign_health['health_percentage']:.1f}% of campaigns are meeting targets - "
                    "Review campaign performance and adjust targeting"
                )
            
            # Co-creator program recommendations
            co_creator_fill_rate = key_metrics.get("co_creator_fill_rate", 0)
            if co_creator_fill_rate < 50:
                recommendations.append(
                    f"Co-creator program is {co_creator_fill_rate:.1f}% filled - "
                    "Consider increasing promotion or adjusting program benefits"
                )
            
            if not recommendations:
                recommendations.append("System is performing well - continue monitoring key metrics")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Unable to generate recommendations due to system error")
        
        return recommendations
    
    async def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts and return them"""
        alerts = []
        
        try:
            # Get recent metrics
            dashboard_data = await self.dashboard.get_real_time_dashboard(time_range_hours=1)
            core_metrics = dashboard_data["core_metrics"]
            co_creator_status = dashboard_data["co_creator_program"]
            
            # Check conversion rate
            conversion_rate = core_metrics["rates"]["conversion_rate"]
            if conversion_rate <= self.thresholds["conversion_rate_critical"]:
                alerts.append({
                    "type": "performance",
                    "severity": "critical",
                    "metric": "conversion_rate",
                    "value": conversion_rate,
                    "threshold": self.thresholds["conversion_rate_critical"],
                    "message": f"Critical: Conversion rate dropped to {conversion_rate:.1f}%",
                    "recommendation": "Immediate review of landing page and funnel optimization needed"
                })
            elif conversion_rate <= self.thresholds["conversion_rate_warning"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "metric": "conversion_rate",
                    "value": conversion_rate,
                    "threshold": self.thresholds["conversion_rate_warning"],
                    "message": f"Warning: Low conversion rate at {conversion_rate:.1f}%",
                    "recommendation": "Review landing page performance and consider A/B testing"
                })
            
            # Check assessment completion rate
            completion_rate = core_metrics["rates"]["assessment_completion_rate"]
            if completion_rate <= self.thresholds["assessment_completion_critical"]:
                alerts.append({
                    "type": "performance",
                    "severity": "critical",
                    "metric": "assessment_completion_rate",
                    "value": completion_rate,
                    "threshold": self.thresholds["assessment_completion_critical"],
                    "message": f"Critical: Assessment completion rate at {completion_rate:.1f}%",
                    "recommendation": "Review assessment design and user experience"
                })
            elif completion_rate <= self.thresholds["assessment_completion_warning"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "metric": "assessment_completion_rate",
                    "value": completion_rate,
                    "threshold": self.thresholds["assessment_completion_warning"],
                    "message": f"Warning: Low assessment completion at {completion_rate:.1f}%",
                    "recommendation": "Consider simplifying assessment or improving UX"
                })
            
            # Check co-creator program capacity
            seats_remaining = co_creator_status["seats_remaining"]
            if seats_remaining <= self.thresholds["co_creator_seats_critical"]:
                alerts.append({
                    "type": "capacity",
                    "severity": "critical",
                    "metric": "co_creator_seats_remaining",
                    "value": seats_remaining,
                    "threshold": self.thresholds["co_creator_seats_critical"],
                    "message": f"Critical: Only {seats_remaining} co-creator seats remaining",
                    "recommendation": "Prepare for program closure or expansion decision"
                })
            elif seats_remaining <= self.thresholds["co_creator_seats_warning"]:
                alerts.append({
                    "type": "capacity",
                    "severity": "warning",
                    "metric": "co_creator_seats_remaining",
                    "value": seats_remaining,
                    "threshold": self.thresholds["co_creator_seats_warning"],
                    "message": f"Warning: {seats_remaining} co-creator seats remaining",
                    "recommendation": "Monitor capacity and plan for potential program expansion"
                })
            
            # Track alerts
            for alert in alerts:
                await track_metric("landing_page_alert", alert)
            
        except Exception as e:
            logger.error(f"Failed to check performance alerts: {e}")
            alerts.append({
                "type": "system",
                "severity": "error",
                "message": f"Failed to check performance alerts: {str(e)}",
                "recommendation": "Check system logs and monitoring infrastructure"
            })
        
        return alerts
    
    async def run_health_check_cycle(self) -> Dict[str, Any]:
        """Run a complete health check cycle"""
        logger.info("Starting landing page health check cycle")
        
        try:
            # Get comprehensive health report
            health_report = await self.get_comprehensive_health_report()
            
            # Check for alerts
            alerts = await self.check_performance_alerts()
            health_report["alerts"] = alerts
            
            # Track health metrics
            await track_metric("landing_page_health_check", {
                "overall_health": health_report["overall_health"],
                "alerts_count": len(alerts),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Health check completed: {health_report['overall_health']} status with {len(alerts)} alerts")
            
            return health_report
            
        except Exception as e:
            logger.error(f"Health check cycle failed: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": "error",
                "error": str(e)
            }


# Background monitoring service
async def start_landing_page_monitoring_service(db: Session):
    """Start the background landing page monitoring service"""
    logger.info("Starting landing page monitoring service")
    
    monitor = LandingPageMonitor(db)
    
    while True:
        try:
            await monitor.run_health_check_cycle()
            
            # Wait 10 minutes before next check
            await asyncio.sleep(600)
            
        except Exception as e:
            logger.error(f"Landing page monitoring service error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error


# Utility functions
async def get_landing_page_health_summary(db: Session) -> Dict[str, Any]:
    """Get a summary of landing page health for integration with existing monitoring"""
    monitor = LandingPageMonitor(db)
    
    try:
        health_report = await monitor.get_comprehensive_health_report()
        
        return {
            "overall_health": health_report["overall_health"],
            "landing_page_health": health_report["components"]["landing_page"]["health_status"],
            "conversion_rate": health_report["components"]["landing_page"]["key_metrics"]["conversion_rate"],
            "assessment_completion_rate": health_report["components"]["landing_page"]["key_metrics"]["assessment_completion_rate"],
            "active_campaigns": health_report["components"]["campaigns"]["total_campaigns"],
            "alerts_count": health_report["components"]["landing_page"]["alerts_count"],
            "timestamp": health_report["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get landing page health summary: {e}")
        return {
            "overall_health": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
