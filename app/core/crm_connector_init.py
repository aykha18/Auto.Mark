"""
CRM Connector Initialization
Initialize default CRM connectors in the database
"""

import logging
from sqlalchemy.orm import Session
from app.models.crm_integration import (
    CRMConnector, CRMType, AuthMethod, IntegrationStatus
)

logger = logging.getLogger(__name__)


def initialize_crm_connectors(db: Session) -> None:
    """Initialize default CRM connectors"""
    
    connectors_data = [
        {
            "crm_type": CRMType.NEURACRM,
            "name": "neuracrm",
            "display_name": "NeuraLead CRM",
            "description": "Native CRM integration with full Auto.Mark compatibility",
            "logo_url": "/static/logos/neuracrm.png",
            "auth_method": AuthMethod.API_KEY,
            "api_type": "REST",
            "api_version": "v1",
            "base_url": "https://api.neuracrm.com",
            "setup_complexity": "easy",
            "setup_time_minutes": 10,
            "documentation_url": "https://docs.neuracrm.com/automark-integration",
            "sdk_available": True,
            "supported_objects": ["contacts", "companies", "deals", "activities"],
            "webhook_support": True,
            "real_time_sync": True,
            "bulk_operations": True,
            "custom_fields_support": True,
            "status": IntegrationStatus.AVAILABLE,
            "auth_config_schema": {
                "type": "object",
                "properties": {
                    "api_key": {"type": "string", "description": "NeuraLead API Key"},
                    "environment": {"type": "string", "enum": ["production", "sandbox"], "default": "production"}
                },
                "required": ["api_key"]
            },
            "field_mapping_schema": {
                "contacts": {
                    "id": "string",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string",
                    "phone": "string",
                    "company": "string",
                    "job_title": "string"
                }
            }
        },
        {
            "crm_type": CRMType.PIPEDRIVE,
            "name": "pipedrive",
            "display_name": "Pipedrive",
            "description": "Popular sales CRM with strong pipeline management",
            "logo_url": "/static/logos/pipedrive.png",
            "auth_method": AuthMethod.API_KEY,
            "api_type": "REST",
            "api_version": "v1",
            "base_url": "https://api.pipedrive.com",
            "setup_complexity": "easy",
            "setup_time_minutes": 15,
            "documentation_url": "https://developers.pipedrive.com/docs/api/v1",
            "sdk_available": True,
            "supported_objects": ["contacts", "companies", "deals", "activities"],
            "webhook_support": True,
            "real_time_sync": True,
            "bulk_operations": True,
            "custom_fields_support": True,
            "status": IntegrationStatus.AVAILABLE,
            "auth_config_schema": {
                "type": "object",
                "properties": {
                    "api_key": {"type": "string", "description": "Pipedrive API Token"},
                    "domain": {"type": "string", "description": "Your Pipedrive domain"}
                },
                "required": ["api_key", "domain"]
            }
        },
        {
            "crm_type": CRMType.HUBSPOT,
            "name": "hubspot",
            "display_name": "HubSpot",
            "description": "All-in-one marketing, sales, and service platform",
            "logo_url": "/static/logos/hubspot.png",
            "auth_method": AuthMethod.OAUTH2,
            "api_type": "REST",
            "api_version": "v3",
            "base_url": "https://api.hubapi.com",
            "setup_complexity": "easy",
            "setup_time_minutes": 20,
            "documentation_url": "https://developers.hubspot.com/docs/api/overview",
            "sdk_available": True,
            "supported_objects": ["contacts", "companies", "deals", "activities"],
            "webhook_support": True,
            "real_time_sync": True,
            "bulk_operations": True,
            "custom_fields_support": True,
            "status": IntegrationStatus.AVAILABLE,
            "auth_config_schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "description": "HubSpot Access Token"},
                    "refresh_token": {"type": "string", "description": "HubSpot Refresh Token"},
                    "portal_id": {"type": "string", "description": "HubSpot Portal ID"}
                },
                "required": ["access_token"]
            }
        },
        {
            "crm_type": CRMType.ZOHO,
            "name": "zoho",
            "display_name": "Zoho CRM",
            "description": "Comprehensive CRM solution for businesses of all sizes",
            "logo_url": "/static/logos/zoho.png",
            "auth_method": AuthMethod.OAUTH2,
            "api_type": "REST",
            "api_version": "v2",
            "base_url": "https://www.zohoapis.com/crm",
            "setup_complexity": "medium",
            "setup_time_minutes": 25,
            "documentation_url": "https://www.zoho.com/crm/developer/docs/api/v2/",
            "sdk_available": False,
            "supported_objects": ["contacts", "companies", "deals", "activities"],
            "webhook_support": True,
            "real_time_sync": False,
            "bulk_operations": True,
            "custom_fields_support": True,
            "status": IntegrationStatus.BETA,
            "auth_config_schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "description": "Zoho Access Token"},
                    "refresh_token": {"type": "string", "description": "Zoho Refresh Token"},
                    "api_domain": {"type": "string", "description": "Zoho API Domain"}
                },
                "required": ["access_token", "api_domain"]
            }
        },
        {
            "crm_type": CRMType.MONDAY,
            "name": "monday",
            "display_name": "Monday.com",
            "description": "Work management platform with CRM capabilities",
            "logo_url": "/static/logos/monday.png",
            "auth_method": AuthMethod.API_KEY,
            "api_type": "GraphQL",
            "api_version": "2023-10",
            "base_url": "https://api.monday.com/v2",
            "setup_complexity": "medium",
            "setup_time_minutes": 30,
            "documentation_url": "https://developer.monday.com/api-reference/docs",
            "sdk_available": False,
            "supported_objects": ["contacts", "companies", "deals"],
            "webhook_support": True,
            "real_time_sync": False,
            "bulk_operations": False,
            "custom_fields_support": True,
            "status": IntegrationStatus.COMING_SOON,
            "auth_config_schema": {
                "type": "object",
                "properties": {
                    "api_key": {"type": "string", "description": "Monday.com API Token"},
                    "account_id": {"type": "string", "description": "Monday.com Account ID"}
                },
                "required": ["api_key"]
            }
        },
        {
            "crm_type": CRMType.SALESFORCE,
            "name": "salesforce",
            "display_name": "Salesforce",
            "description": "World's leading CRM platform for enterprise",
            "logo_url": "/static/logos/salesforce.png",
            "auth_method": AuthMethod.OAUTH2,
            "api_type": "REST",
            "api_version": "v58.0",
            "base_url": "https://login.salesforce.com",
            "setup_complexity": "advanced",
            "setup_time_minutes": 45,
            "documentation_url": "https://developer.salesforce.com/docs/api-explorer",
            "sdk_available": True,
            "supported_objects": ["contacts", "companies", "deals", "activities"],
            "webhook_support": True,
            "real_time_sync": True,
            "bulk_operations": True,
            "custom_fields_support": True,
            "status": IntegrationStatus.COMING_SOON,
            "auth_config_schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "description": "Salesforce Access Token"},
                    "refresh_token": {"type": "string", "description": "Salesforce Refresh Token"},
                    "instance_url": {"type": "string", "description": "Salesforce Instance URL"},
                    "client_id": {"type": "string", "description": "Connected App Client ID"},
                    "client_secret": {"type": "string", "description": "Connected App Client Secret"}
                },
                "required": ["access_token", "instance_url"]
            }
        }
    ]
    
    for connector_data in connectors_data:
        # Check if connector already exists
        existing = db.query(CRMConnector).filter(
            CRMConnector.crm_type == connector_data["crm_type"]
        ).first()
        
        if not existing:
            connector = CRMConnector(**connector_data)
            db.add(connector)
            logger.info(f"Added CRM connector: {connector_data['display_name']}")
        else:
            # Update existing connector with new data
            for key, value in connector_data.items():
                if key != "crm_type":  # Don't update the primary identifier
                    setattr(existing, key, value)
            logger.info(f"Updated CRM connector: {connector_data['display_name']}")
    
    try:
        db.commit()
        logger.info("Successfully initialized CRM connectors")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to initialize CRM connectors: {e}")
        raise


def get_connector_by_type(db: Session, crm_type: CRMType) -> CRMConnector:
    """Get connector by CRM type"""
    return db.query(CRMConnector).filter(CRMConnector.crm_type == crm_type).first()


def update_connector_status(db: Session, crm_type: CRMType, status: IntegrationStatus) -> bool:
    """Update connector status"""
    try:
        connector = get_connector_by_type(db, crm_type)
        if connector:
            connector.status = status
            db.commit()
            logger.info(f"Updated {crm_type.value} connector status to {status.value}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update connector status: {e}")
        return False


def enable_connector(db: Session, crm_type: CRMType) -> bool:
    """Enable a CRM connector"""
    return update_connector_status(db, crm_type, IntegrationStatus.AVAILABLE)


def disable_connector(db: Session, crm_type: CRMType) -> bool:
    """Disable a CRM connector"""
    try:
        connector = get_connector_by_type(db, crm_type)
        if connector:
            connector.is_active = False
            db.commit()
            logger.info(f"Disabled {crm_type.value} connector")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to disable connector: {e}")
        return False