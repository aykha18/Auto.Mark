"""
CRM Integration Health Monitoring System
Monitors CRM connections, sync performance, and system health
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.crm_integration import (
    CRMConnection, CRMSyncLog, CRMConnector,
    ConnectionStatus, SyncStatus
)
from app.core.metrics import track_metric
from app.core.database import get_db

logger = logging.getLogger(__name__)


class CRMIntegrationMonitor:
    """Monitor for CRM integration health and performance"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_thresholds = {
            "error_rate_threshold": 0.1,  # 10% error rate
            "sync_delay_threshold": 3600,  # 1 hour delay
            "connection_timeout_threshold": 300,  # 5 minutes
            "failed_syncs_threshold": 5  # 5 consecutive failures
        }
    
    async def check_all_connections_health(self) -> Dict[str, Any]:
        """Check health of all CRM connections"""
        connections = self.db.query(CRMConnection).filter(
            CRMConnection.connection_status != ConnectionStatus.DISCONNECTED
        ).all()
        
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_connections": len(connections),
            "healthy_connections": 0,
            "unhealthy_connections": 0,
            "connection_details": [],
            "alerts": [],
            "recommendations": []
        }
        
        for connection in connections:
            connection_health = await self._check_connection_health(connection)
            health_report["connection_details"].append(connection_health)
            
            if connection_health["is_healthy"]:
                health_report["healthy_connections"] += 1
            else:
                health_report["unhealthy_connections"] += 1
                health_report["alerts"].extend(connection_health.get("alerts", []))
        
        # Generate system-wide recommendations
        health_report["recommendations"] = self._generate_system_recommendations(
            health_report["connection_details"]
        )
        
        # Track overall health metrics
        await track_metric("crm_integration_health_check", {
            "total_connections": health_report["total_connections"],
            "healthy_percentage": (health_report["healthy_connections"] / len(connections) * 100) if connections else 0,
            "alerts_count": len(health_report["alerts"])
        })
        
        return health_report
    
    async def _check_connection_health(self, connection: CRMConnection) -> Dict[str, Any]:
        """Check health of a single CRM connection"""
        health_data = {
            "connection_id": connection.id,
            "connection_name": connection.connection_name,
            "crm_type": connection.connector.crm_type.value,
            "status": connection.connection_status.value,
            "is_healthy": True,
            "health_score": 100,
            "issues": [],
            "alerts": [],
            "last_check": datetime.utcnow().isoformat()
        }
        
        # Check connection status
        if connection.connection_status != ConnectionStatus.CONNECTED:
            health_data["is_healthy"] = False
            health_data["health_score"] -= 50
            health_data["issues"].append("Connection not active")
            health_data["alerts"].append({
                "type": "error",
                "message": f"Connection {connection.connection_name} is not active",
                "severity": "high"
            })
        
        # Check error count
        if connection.error_count >= self.alert_thresholds["failed_syncs_threshold"]:
            health_data["is_healthy"] = False
            health_data["health_score"] -= 30
            health_data["issues"].append(f"High error count: {connection.error_count}")
            health_data["alerts"].append({
                "type": "warning",
                "message": f"High error count ({connection.error_count}) for {connection.connection_name}",
                "severity": "medium"
            })
        
        # Check token expiration
        if connection.needs_token_refresh():
            health_data["health_score"] -= 20
            health_data["issues"].append("Token needs refresh")
            health_data["alerts"].append({
                "type": "warning",
                "message": f"Token refresh needed for {connection.connection_name}",
                "severity": "medium"
            })
        
        # Check sync performance
        sync_health = await self._check_sync_performance(connection)
        health_data["sync_performance"] = sync_health
        
        if not sync_health["is_healthy"]:
            health_data["is_healthy"] = False
            health_data["health_score"] -= 20
            health_data["issues"].extend(sync_health["issues"])
            health_data["alerts"].extend(sync_health["alerts"])
        
        # Check last sync time
        if connection.last_sync_at:
            time_since_sync = datetime.utcnow() - connection.last_sync_at
            if time_since_sync.total_seconds() > self.alert_thresholds["sync_delay_threshold"]:
                health_data["health_score"] -= 10
                health_data["issues"].append("Sync overdue")
                health_data["alerts"].append({
                    "type": "info",
                    "message": f"No recent sync for {connection.connection_name}",
                    "severity": "low"
                })
        
        return health_data
    
    async def _check_sync_performance(self, connection: CRMConnection) -> Dict[str, Any]:
        """Check sync performance for a connection"""
        # Get recent sync logs (last 24 hours)
        recent_syncs = self.db.query(CRMSyncLog).filter(
            CRMSyncLog.connection_id == connection.id,
            CRMSyncLog.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        sync_health = {
            "is_healthy": True,
            "issues": [],
            "alerts": [],
            "metrics": {
                "total_syncs": len(recent_syncs),
                "successful_syncs": 0,
                "failed_syncs": 0,
                "avg_duration": 0,
                "error_rate": 0
            }
        }
        
        if not recent_syncs:
            return sync_health
        
        successful_syncs = [s for s in recent_syncs if s.status == SyncStatus.SUCCESS]
        failed_syncs = [s for s in recent_syncs if s.status == SyncStatus.FAILED]
        
        sync_health["metrics"]["successful_syncs"] = len(successful_syncs)
        sync_health["metrics"]["failed_syncs"] = len(failed_syncs)
        sync_health["metrics"]["error_rate"] = len(failed_syncs) / len(recent_syncs)
        
        # Calculate average duration
        durations = [s.duration_seconds for s in recent_syncs if s.duration_seconds]
        if durations:
            sync_health["metrics"]["avg_duration"] = sum(durations) / len(durations)
        
        # Check error rate
        if sync_health["metrics"]["error_rate"] > self.alert_thresholds["error_rate_threshold"]:
            sync_health["is_healthy"] = False
            sync_health["issues"].append(f"High sync error rate: {sync_health['metrics']['error_rate']:.1%}")
            sync_health["alerts"].append({
                "type": "warning",
                "message": f"High sync error rate for {connection.connection_name}",
                "severity": "medium"
            })
        
        return sync_health
    
    def _generate_system_recommendations(self, connection_details: List[Dict[str, Any]]) -> List[str]:
        """Generate system-wide recommendations"""
        recommendations = []
        
        unhealthy_connections = [c for c in connection_details if not c["is_healthy"]]
        if len(unhealthy_connections) > 0:
            recommendations.append(f"Review {len(unhealthy_connections)} unhealthy connections")
        
        high_error_connections = [c for c in connection_details if len(c["issues"]) >= 3]
        if high_error_connections:
            recommendations.append(f"Investigate {len(high_error_connections)} connections with multiple issues")
        
        token_refresh_needed = [c for c in connection_details if "Token needs refresh" in c["issues"]]
        if token_refresh_needed:
            recommendations.append(f"Refresh tokens for {len(token_refresh_needed)} connections")
        
        return recommendations
    
    async def get_performance_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for specified time range"""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Get sync statistics
        sync_stats = self.db.query(
            func.count(CRMSyncLog.id).label('total_syncs'),
            func.sum(func.case([(CRMSyncLog.status == SyncStatus.SUCCESS, 1)], else_=0)).label('successful_syncs'),
            func.sum(func.case([(CRMSyncLog.status == SyncStatus.FAILED, 1)], else_=0)).label('failed_syncs'),
            func.avg(CRMSyncLog.duration_seconds).label('avg_duration'),
            func.sum(CRMSyncLog.records_processed).label('total_records')
        ).filter(CRMSyncLog.created_at >= start_time).first()
        
        # Get connection statistics
        connection_stats = self.db.query(
            func.count(CRMConnection.id).label('total_connections'),
            func.sum(func.case([(CRMConnection.connection_status == ConnectionStatus.CONNECTED, 1)], else_=0)).label('connected'),
            func.sum(func.case([(CRMConnection.connection_status == ConnectionStatus.ERROR, 1)], else_=0)).label('error_status')
        ).first()
        
        # Calculate metrics
        total_syncs = sync_stats.total_syncs or 0
        successful_syncs = sync_stats.successful_syncs or 0
        failed_syncs = sync_stats.failed_syncs or 0
        
        success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        error_rate = (failed_syncs / total_syncs * 100) if total_syncs > 0 else 0
        
        return {
            "time_range_hours": time_range_hours,
            "sync_metrics": {
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "failed_syncs": failed_syncs,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "avg_duration_seconds": float(sync_stats.avg_duration or 0),
                "total_records_processed": sync_stats.total_records or 0
            },
            "connection_metrics": {
                "total_connections": connection_stats.total_connections or 0,
                "connected_connections": connection_stats.connected or 0,
                "error_connections": connection_stats.error_status or 0,
                "health_percentage": ((connection_stats.connected or 0) / (connection_stats.total_connections or 1) * 100)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_connector_performance(self, connector_id: int, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for a specific connector"""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Get connector info
        connector = self.db.query(CRMConnector).filter(CRMConnector.id == connector_id).first()
        if not connector:
            return {"error": "Connector not found"}
        
        # Get connections for this connector
        connections = self.db.query(CRMConnection).filter(
            CRMConnection.connector_id == connector_id
        ).all()
        
        # Get sync logs for these connections
        connection_ids = [c.id for c in connections]
        sync_logs = self.db.query(CRMSyncLog).filter(
            CRMSyncLog.connection_id.in_(connection_ids),
            CRMSyncLog.created_at >= start_time
        ).all()
        
        # Calculate metrics
        total_syncs = len(sync_logs)
        successful_syncs = len([s for s in sync_logs if s.status == SyncStatus.SUCCESS])
        failed_syncs = len([s for s in sync_logs if s.status == SyncStatus.FAILED])
        
        success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        
        # Connection health
        healthy_connections = len([c for c in connections if c.is_healthy()])
        
        return {
            "connector_id": connector_id,
            "connector_name": connector.display_name,
            "crm_type": connector.crm_type.value,
            "time_range_hours": time_range_hours,
            "connection_metrics": {
                "total_connections": len(connections),
                "healthy_connections": healthy_connections,
                "health_percentage": (healthy_connections / len(connections) * 100) if connections else 0
            },
            "sync_metrics": {
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "failed_syncs": failed_syncs,
                "success_rate": success_rate,
                "total_records_processed": sum(s.records_processed for s in sync_logs)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_health_alert(self, connection_id: int, alert_type: str, 
                                 message: str, severity: str = "medium") -> bool:
        """Create a health alert for a connection"""
        try:
            await track_metric("crm_health_alert", {
                "connection_id": connection_id,
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.warning(f"CRM Health Alert - {alert_type}: {message} (Connection: {connection_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create health alert: {e}")
            return False
    
    async def run_health_check_cycle(self) -> Dict[str, Any]:
        """Run a complete health check cycle"""
        logger.info("Starting CRM integration health check cycle")
        
        try:
            health_report = await self.check_all_connections_health()
            
            # Create alerts for critical issues
            for alert in health_report["alerts"]:
                if alert["severity"] == "high":
                    await self.create_health_alert(
                        0,  # System-wide alert
                        alert["type"],
                        alert["message"],
                        alert["severity"]
                    )
            
            logger.info(f"Health check completed: {health_report['healthy_connections']}/{health_report['total_connections']} connections healthy")
            
            return health_report
            
        except Exception as e:
            logger.error(f"Health check cycle failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


# Background monitoring task
async def start_monitoring_service():
    """Start the background monitoring service"""
    logger.info("Starting CRM integration monitoring service")
    
    while True:
        try:
            async with get_db() as db:
                monitor = CRMIntegrationMonitor(db)
                await monitor.run_health_check_cycle()
            
            # Wait 5 minutes before next check
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Monitoring service error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error


# Utility functions for integration with existing monitoring system
async def get_integration_health_summary(db: Session) -> Dict[str, Any]:
    """Get a summary of integration health for dashboard"""
    monitor = CRMIntegrationMonitor(db)
    
    # Get basic metrics
    performance = await monitor.get_performance_metrics(24)
    
    # Get connection count by status
    connection_counts = db.query(
        CRMConnection.connection_status,
        func.count(CRMConnection.id)
    ).group_by(CRMConnection.connection_status).all()
    
    status_counts = {status.value: 0 for status in ConnectionStatus}
    for status, count in connection_counts:
        status_counts[status.value] = count
    
    return {
        "overall_health": "healthy" if performance["sync_metrics"]["success_rate"] > 90 else "warning",
        "total_connections": performance["connection_metrics"]["total_connections"],
        "healthy_connections": performance["connection_metrics"]["connected_connections"],
        "sync_success_rate": performance["sync_metrics"]["success_rate"],
        "last_24h_syncs": performance["sync_metrics"]["total_syncs"],
        "connection_status_breakdown": status_counts,
        "timestamp": datetime.utcnow().isoformat()
    }