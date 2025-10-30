"""
CRM Integration Marketplace API endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.config import get_settings
from app.core.crm_marketplace_service import CRMMarketplaceService
from app.core.crm_integration_framework import CRMIntegrationFramework
from app.models.crm_integration import CRMConnector, CRMConnection

router = APIRouter()
settings = get_settings()


# Pydantic models for API requests/responses
class CRMConnectorResponse(BaseModel):
    """CRM connector response model"""
    id: int
    crm_type: str
    name: str
    display_name: str
    description: Optional[str]
    logo_url: Optional[str]
    auth_method: str
    setup_complexity: str
    setup_time_minutes: int
    supported_objects: List[str]
    features: Dict[str, bool]
    status: str
    connection_count: int
    success_rate: float
    avg_setup_time: int
    user_rating: float
    demo_available: bool


class CRMComparisonRequest(BaseModel):
    """Request to compare CRM connectors"""
    connector_ids: List[int] = Field(..., min_items=2, max_items=5)


class DemoConnectionRequest(BaseModel):
    """Request to create demo connection"""
    crm_type: str
    user_email: str
    lead_id: Optional[int] = None


class DemoConnectionResponse(BaseModel):
    """Response for demo connection creation"""
    success: bool
    message: str
    connection_id: Optional[int] = None
    demo_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[str] = None


class CRMIntegrationTrackingRequest(BaseModel):
    """Request to track CRM integration for lead"""
    lead_id: int
    crm_type: str
    integration_status: str  # interested, demo_requested, demo_completed, integration_started


@router.get("/health")
async def crm_marketplace_health_check() -> Dict[str, Any]:
    """Health check endpoint for CRM marketplace"""
    return {
        "status": "healthy",
        "service": "crm_marketplace",
        "version": settings.version,
        "environment": settings.environment
    }


@router.get("/connectors")
async def get_available_connectors(
    include_beta: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all available CRM connectors with capabilities and marketplace data
    """
    try:
        service = CRMMarketplaceService(db)
        connectors = service.get_available_connectors(include_beta=include_beta)
        
        return {
            "connectors": connectors,
            "total_count": len(connectors),
            "beta_included": include_beta
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connectors: {str(e)}")


@router.get("/connectors/{connector_id}")
async def get_connector_details(
    connector_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific CRM connector
    """
    try:
        service = CRMMarketplaceService(db)
        details = service.get_connector_details(connector_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Connector not found")
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connector details: {str(e)}")


@router.post("/connectors/compare")
async def compare_connectors(
    request: CRMComparisonRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare multiple CRM connectors side by side
    """
    try:
        service = CRMMarketplaceService(db)
        comparison = service.compare_connectors(request.connector_ids)
        
        if "error" in comparison:
            raise HTTPException(status_code=400, detail=comparison["error"])
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare connectors: {str(e)}")


@router.post("/demo/create")
async def create_demo_connection(
    request: DemoConnectionRequest,
    db: Session = Depends(get_db)
) -> DemoConnectionResponse:
    """
    Create a one-click demo connection with sandbox environment
    """
    try:
        service = CRMMarketplaceService(db)
        result = await service.create_demo_connection(request.crm_type, request.user_email)
        
        return DemoConnectionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create demo connection: {str(e)}")


@router.get("/demo/{connection_id}/status")
async def get_demo_connection_status(
    connection_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get status of a demo connection
    """
    try:
        connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            raise HTTPException(status_code=404, detail="Demo connection not found")
        
        # Check if it's a demo connection
        if not connection.sync_config.get("demo_mode"):
            raise HTTPException(status_code=400, detail="Not a demo connection")
        
        framework = CRMIntegrationFramework(db)
        health = framework.get_connection_health(connection_id)
        
        return {
            "connection_id": connection_id,
            "status": health["status"],
            "is_healthy": health["is_healthy"],
            "demo_expires_at": connection.created_at + timedelta(hours=24) if connection.created_at else None,
            "sample_data_available": True,
            "features_tested": ["sync", "field_mapping", "webhooks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get demo status: {str(e)}")


@router.post("/demo/{connection_id}/test-sync")
async def test_demo_sync(
    connection_id: int,
    object_type: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test sync functionality with demo connection
    """
    try:
        connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            raise HTTPException(status_code=404, detail="Demo connection not found")
        
        if not connection.sync_config.get("demo_mode"):
            raise HTTPException(status_code=400, detail="Not a demo connection")
        
        framework = CRMIntegrationFramework(db)
        result = await framework.sync_objects(connection_id, object_type, "import")
        
        return {
            "success": result["success"],
            "object_type": object_type,
            "records_synced": result["count"],
            "demo_note": "This is sample data from the demo environment"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test demo sync: {str(e)}")


@router.get("/health/overview")
async def get_integration_health_overview(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get overall health overview of all CRM integrations
    """
    try:
        service = CRMMarketplaceService(db)
        overview = service.get_integration_health_overview()
        
        return overview
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health overview: {str(e)}")


@router.post("/tracking/lead-integration")
async def track_lead_crm_integration(
    request: CRMIntegrationTrackingRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Track CRM integration interest/status for a lead
    """
    try:
        service = CRMMarketplaceService(db)
        success = service.track_lead_crm_integration(
            request.lead_id,
            request.crm_type,
            request.integration_status
        )
        
        if success:
            return {
                "success": True,
                "message": "Lead CRM integration tracked successfully",
                "lead_id": request.lead_id,
                "crm_type": request.crm_type,
                "status": request.integration_status
            }
        else:
            raise HTTPException(status_code=404, detail="Lead not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track lead integration: {str(e)}")


@router.get("/analytics")
async def get_marketplace_analytics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive marketplace analytics and metrics
    """
    try:
        service = CRMMarketplaceService(db)
        analytics = service.get_marketplace_analytics()
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get marketplace analytics: {str(e)}")


@router.get("/connectors/{connector_id}/health")
async def get_connector_health(
    connector_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get health metrics for a specific connector
    """
    try:
        # Get all connections for this connector
        connections = db.query(CRMConnection).filter(
            CRMConnection.connector_id == connector_id
        ).all()
        
        if not connections:
            return {
                "connector_id": connector_id,
                "total_connections": 0,
                "health_metrics": {}
            }
        
        framework = CRMIntegrationFramework(db)
        health_data = []
        
        for connection in connections:
            health = framework.get_connection_health(connection.id)
            health_data.append(health)
        
        # Aggregate health metrics
        total_connections = len(connections)
        healthy_connections = len([h for h in health_data if h["is_healthy"]])
        avg_success_rate = sum(h["sync_success_rate"] for h in health_data) / total_connections
        total_syncs = sum(h["total_syncs"] for h in health_data)
        total_records = sum(h["records_synced"] for h in health_data)
        
        return {
            "connector_id": connector_id,
            "total_connections": total_connections,
            "healthy_connections": healthy_connections,
            "health_percentage": (healthy_connections / total_connections * 100),
            "avg_sync_success_rate": avg_success_rate,
            "total_syncs_performed": total_syncs,
            "total_records_synced": total_records,
            "connection_details": health_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connector health: {str(e)}")


@router.get("/supported-objects")
async def get_supported_objects() -> Dict[str, Any]:
    """
    Get list of supported CRM objects and their standard fields
    """
    return {
        "supported_objects": {
            "contacts": {
                "description": "Individual people/contacts",
                "standard_fields": [
                    "first_name", "last_name", "email", "phone", 
                    "company", "job_title", "created_at", "updated_at"
                ]
            },
            "companies": {
                "description": "Organizations/companies",
                "standard_fields": [
                    "name", "website", "industry", "size", "revenue", 
                    "location", "created_at", "updated_at"
                ]
            },
            "deals": {
                "description": "Sales opportunities/deals",
                "standard_fields": [
                    "title", "value", "stage", "status", "contact_id", 
                    "company_id", "owner_id", "created_at", "updated_at"
                ]
            },
            "activities": {
                "description": "Tasks, calls, meetings, emails",
                "standard_fields": [
                    "type", "subject", "description", "contact_id", 
                    "deal_id", "due_date", "completed", "created_at", "updated_at"
                ]
            }
        },
        "field_mapping_info": {
            "description": "Fields can be mapped between Auto.Mark and CRM systems",
            "custom_fields_supported": True,
            "transformation_rules_available": True
        }
    }


@router.get("/setup-guides/{crm_type}")
async def get_setup_guide(
    crm_type: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed setup guide for a specific CRM type
    """
    try:
        service = CRMMarketplaceService(db)
        
        # Get connector for this CRM type
        from app.models.crm_integration import CRMType
        connector = db.query(CRMConnector).filter(
            CRMConnector.crm_type == CRMType(crm_type)
        ).first()
        
        if not connector:
            raise HTTPException(status_code=404, detail="CRM type not supported")
        
        guide = service._get_setup_guide(CRMType(crm_type))
        examples = service._get_integration_examples(CRMType(crm_type))
        troubleshooting = service._get_troubleshooting_guide(CRMType(crm_type))
        
        return {
            "crm_type": crm_type,
            "connector_name": connector.display_name,
            "setup_guide": guide,
            "integration_examples": examples,
            "troubleshooting": troubleshooting,
            "demo_available": service._has_demo_environment(CRMType(crm_type))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get setup guide: {str(e)}")


# Import monitoring system
from app.core.crm_integration_monitoring import CRMIntegrationMonitor, get_integration_health_summary


@router.get("/monitoring/health-check")
async def run_health_check(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run a comprehensive health check on all CRM integrations
    """
    try:
        monitor = CRMIntegrationMonitor(db)
        health_report = await monitor.check_all_connections_health()
        
        return health_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run health check: {str(e)}")


@router.get("/monitoring/performance")
async def get_performance_metrics(
    time_range_hours: int = 24,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get performance metrics for CRM integrations
    """
    try:
        if time_range_hours > 168:  # Limit to 1 week
            raise HTTPException(status_code=400, detail="Time range cannot exceed 168 hours (1 week)")
        
        monitor = CRMIntegrationMonitor(db)
        metrics = await monitor.get_performance_metrics(time_range_hours)
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/monitoring/connectors/{connector_id}/performance")
async def get_connector_performance(
    connector_id: int,
    time_range_hours: int = 24,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get performance metrics for a specific CRM connector
    """
    try:
        if time_range_hours > 168:  # Limit to 1 week
            raise HTTPException(status_code=400, detail="Time range cannot exceed 168 hours (1 week)")
        
        monitor = CRMIntegrationMonitor(db)
        metrics = await monitor.get_connector_performance(connector_id, time_range_hours)
        
        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connector performance: {str(e)}")


@router.get("/monitoring/dashboard")
async def get_monitoring_dashboard(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get monitoring dashboard data with key metrics and alerts
    """
    try:
        # Get health summary
        health_summary = await get_integration_health_summary(db)
        
        # Get recent performance
        monitor = CRMIntegrationMonitor(db)
        performance_24h = await monitor.get_performance_metrics(24)
        performance_7d = await monitor.get_performance_metrics(168)
        
        # Get top performing and problematic connectors
        connectors = db.query(CRMConnector).filter(CRMConnector.is_active == True).all()
        connector_performance = []
        
        for connector in connectors:
            perf = await monitor.get_connector_performance(connector.id, 24)
            if "error" not in perf:
                connector_performance.append({
                    "connector_id": connector.id,
                    "name": connector.display_name,
                    "crm_type": connector.crm_type.value,
                    "health_percentage": perf["connection_metrics"]["health_percentage"],
                    "sync_success_rate": perf["sync_metrics"]["success_rate"],
                    "total_connections": perf["connection_metrics"]["total_connections"]
                })
        
        # Sort by health and success rate
        top_performers = sorted(connector_performance, 
                               key=lambda x: (x["health_percentage"], x["sync_success_rate"]), 
                               reverse=True)[:3]
        
        problematic = sorted(connector_performance,
                           key=lambda x: (x["health_percentage"], x["sync_success_rate"]))[:3]
        
        return {
            "health_summary": health_summary,
            "performance_trends": {
                "last_24h": performance_24h,
                "last_7d": performance_7d
            },
            "top_performers": top_performers,
            "needs_attention": problematic,
            "dashboard_updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring dashboard: {str(e)}")


@router.post("/monitoring/connections/{connection_id}/test")
async def test_connection_health(
    connection_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test health of a specific CRM connection
    """
    try:
        connection = db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        monitor = CRMIntegrationMonitor(db)
        health_data = await monitor._check_connection_health(connection)
        
        return {
            "connection_id": connection_id,
            "test_completed_at": datetime.utcnow().isoformat(),
            "health_data": health_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test connection health: {str(e)}")


@router.get("/monitoring/alerts")
async def get_active_alerts(
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get active monitoring alerts
    """
    try:
        monitor = CRMIntegrationMonitor(db)
        health_report = await monitor.check_all_connections_health()
        
        alerts = health_report.get("alerts", [])
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert.get("severity") == severity]
        
        # Limit results
        alerts = alerts[:limit]
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "severity_filter": severity,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


# Add missing import for timedelta
from datetime import timedelta