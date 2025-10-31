"""
CRM Integration models for managing CRM connections and configurations
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base, TimestampMixin


class CRMType(enum.Enum):
    """Supported CRM types"""
    NEURACRM = "neuracrm"
    PIPEDRIVE = "pipedrive"
    ZOHO = "zoho"
    HUBSPOT = "hubspot"
    MONDAY = "monday"
    SALESFORCE = "salesforce"
    OTHER = "other"


class AuthMethod(enum.Enum):
    """Authentication methods for CRM integrations"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"


class IntegrationStatus(enum.Enum):
    """Integration status values"""
    AVAILABLE = "available"
    BETA = "beta"
    COMING_SOON = "coming_soon"
    DEPRECATED = "deprecated"


class ConnectionStatus(enum.Enum):
    """Connection status values"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"
    EXPIRED = "expired"


class SyncStatus(enum.Enum):
    """Sync operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"


class CRMConnector(Base, TimestampMixin):
    """CRM connector registry - defines available CRM integrations"""

    __tablename__ = "crm_connectors"

    id = Column(Integer, primary_key=True, index=True)
    crm_type = Column(Enum(CRMType), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    logo_url = Column(String(500))
    
    # Integration capabilities
    auth_method = Column(Enum(AuthMethod), nullable=False)
    api_type = Column(String(50), default="REST")  # REST, GraphQL, SOAP
    api_version = Column(String(50))
    base_url = Column(String(500))
    
    # Setup information
    setup_complexity = Column(String(50), default="medium")  # easy, medium, advanced
    setup_time_minutes = Column(Integer, default=30)
    documentation_url = Column(String(500))
    sdk_available = Column(Boolean, default=False)
    
    # Feature support
    supported_objects = Column(JSON, default=list)  # [contacts, companies, deals, activities]
    webhook_support = Column(Boolean, default=False)
    real_time_sync = Column(Boolean, default=False)
    bulk_operations = Column(Boolean, default=False)
    custom_fields_support = Column(Boolean, default=False)
    
    # Status and availability
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    
    # Configuration schema
    auth_config_schema = Column(JSON, default=dict)  # JSON schema for auth config
    field_mapping_schema = Column(JSON, default=dict)  # Available fields for mapping
    
    # Relationships
    connections = relationship("CRMConnection", back_populates="connector", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CRMConnector(id={self.id}, crm_type='{self.crm_type.value}', name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = super().to_dict()
        result['crm_type'] = self.crm_type.value
        result['auth_method'] = self.auth_method.value
        result['status'] = self.status.value
        return result

    def get_capabilities(self) -> Dict[str, Any]:
        """Get connector capabilities"""
        return {
            "crm_type": self.crm_type.value,
            "name": self.name,
            "display_name": self.display_name,
            "auth_method": self.auth_method.value,
            "api_type": self.api_type,
            "setup_complexity": self.setup_complexity,
            "setup_time_minutes": self.setup_time_minutes,
            "supported_objects": self.supported_objects,
            "features": {
                "webhook_support": self.webhook_support,
                "real_time_sync": self.real_time_sync,
                "bulk_operations": self.bulk_operations,
                "custom_fields_support": self.custom_fields_support,
                "sdk_available": self.sdk_available
            },
            "status": self.status.value,
            "documentation_url": self.documentation_url
        }


class CRMConnection(Base, TimestampMixin):
    """CRM connection instance - represents a user's connection to a specific CRM"""

    __tablename__ = "crm_connections"

    id = Column(Integer, primary_key=True, index=True)
    connector_id = Column(Integer, ForeignKey("crm_connectors.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    
    # Connection details
    connection_name = Column(String(255), nullable=False)  # User-defined name
    connection_status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING)
    
    # Authentication data (encrypted)
    auth_config = Column(JSON, default=dict)  # Encrypted auth credentials
    refresh_token = Column(Text)  # For OAuth2
    token_expires_at = Column(DateTime)
    
    # Configuration
    field_mapping = Column(JSON, default=dict)  # Field mapping configuration
    sync_config = Column(JSON, default=dict)  # Sync settings
    webhook_url = Column(String(500))
    
    # Health and monitoring
    last_sync_at = Column(DateTime, index=True)
    last_health_check_at = Column(DateTime)
    health_status = Column(String(50), default="unknown")  # healthy, warning, error
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Usage statistics
    total_syncs = Column(Integer, default=0)
    successful_syncs = Column(Integer, default=0)
    failed_syncs = Column(Integer, default=0)
    records_synced = Column(Integer, default=0)
    
    # Relationships
    connector = relationship("CRMConnector", back_populates="connections")
    user = relationship("User", back_populates="crm_connections")
    lead = relationship("Lead", back_populates="crm_connections")
    sync_logs = relationship("CRMSyncLog", back_populates="connection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CRMConnection(id={self.id}, name='{self.connection_name}', status='{self.connection_status.value}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)"""
        result = super().to_dict()
        result['connection_status'] = self.connection_status.value
        result['connector_type'] = self.connector.crm_type.value if self.connector else None
        result['connector_name'] = self.connector.name if self.connector else None
        # Exclude sensitive auth_config and refresh_token
        result.pop('auth_config', None)
        result.pop('refresh_token', None)
        return result

    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        return (
            self.connection_status == ConnectionStatus.CONNECTED and
            self.health_status == "healthy" and
            self.error_count < 5
        )

    def needs_token_refresh(self) -> bool:
        """Check if OAuth2 token needs refresh"""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() >= self.token_expires_at

    def update_health_status(self, status: str, error: str = None):
        """Update connection health status"""
        self.health_status = status
        self.last_health_check_at = datetime.utcnow()
        if error:
            self.last_error = error
            self.error_count += 1
        elif status == "healthy":
            self.error_count = 0
        self.updated_at = datetime.utcnow()

    def record_sync_attempt(self, success: bool, records_count: int = 0, error: str = None):
        """Record a sync attempt"""
        self.total_syncs += 1
        self.last_sync_at = datetime.utcnow()
        
        if success:
            self.successful_syncs += 1
            self.records_synced += records_count
            self.update_health_status("healthy")
        else:
            self.failed_syncs += 1
            self.update_health_status("error", error)

    def get_sync_success_rate(self) -> float:
        """Calculate sync success rate"""
        if self.total_syncs == 0:
            return 0.0
        return (self.successful_syncs / self.total_syncs) * 100


class CRMSyncLog(Base, TimestampMixin):
    """Log of CRM sync operations"""

    __tablename__ = "crm_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("crm_connections.id"), nullable=False, index=True)
    
    # Sync operation details
    sync_type = Column(String(50), nullable=False)  # full, incremental, webhook
    sync_direction = Column(String(50), nullable=False)  # import, export, bidirectional
    object_type = Column(String(100))  # contacts, companies, deals, activities
    
    # Results
    status = Column(Enum(SyncStatus), nullable=False)
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON, default=dict)
    
    # Metadata
    sync_metadata = Column(JSON, default=dict)  # Additional sync information
    
    # Relationships
    connection = relationship("CRMConnection", back_populates="sync_logs")

    def __repr__(self):
        return f"<CRMSyncLog(id={self.id}, connection_id={self.connection_id}, status='{self.status.value}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = super().to_dict()
        result['status'] = self.status.value
        return result

    def mark_completed(self, status: SyncStatus, error_message: str = None):
        """Mark sync as completed"""
        self.status = status
        self.completed_at = datetime.utcnow()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        if error_message:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()


class CRMFieldMapping(Base, TimestampMixin):
    """Field mapping configuration for CRM integrations"""

    __tablename__ = "crm_field_mappings"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("crm_connections.id"), nullable=False, index=True)
    
    # Mapping details
    object_type = Column(String(100), nullable=False)  # contacts, companies, deals, activities
    unitasa_field = Column(String(255), nullable=False)  # Unitasa field name
    crm_field = Column(String(255), nullable=False)  # CRM field name
    
    # Field configuration
    data_type = Column(String(50), nullable=False)  # string, number, date, boolean
    is_required = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)
    
    # Transformation rules
    transformation_rule = Column(Text)  # Transformation logic/formula
    default_value = Column(String(500))  # Default value if source is empty
    
    # Sync configuration
    sync_direction = Column(String(50), default="bidirectional")  # import, export, bidirectional
    is_active = Column(Boolean, default=True)
    
    # Relationships
    connection = relationship("CRMConnection")

    def __repr__(self):
        return f"<CRMFieldMapping(id={self.id}, {self.automark_field} -> {self.crm_field})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return super().to_dict()


# Add relationship to existing models
from .user import User
from .lead import Lead

# Add to User model
User.crm_connections = relationship("CRMConnection", back_populates="user", cascade="all, delete-orphan")

# Add to Lead model  
Lead.crm_connections = relationship("CRMConnection", back_populates="lead", cascade="all, delete-orphan")

# Add CRM integration tracking methods to Lead model
def add_crm_integration_tracking(self, crm_type: str, status: str, metadata: Dict[str, Any] = None):
    """Add CRM integration tracking to lead"""
    if not self.custom_fields:
        self.custom_fields = {}
    
    tracking_data = {
        "crm_type": crm_type,
        "status": status,
        "tracked_at": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }
    
    if "crm_integration_tracking" not in self.custom_fields:
        self.custom_fields["crm_integration_tracking"] = []
    
    self.custom_fields["crm_integration_tracking"].append(tracking_data)
    self.add_tag(f"crm_interest_{crm_type}")
    self.add_tag(f"integration_status_{status}")

def get_crm_integration_history(self) -> List[Dict[str, Any]]:
    """Get CRM integration tracking history"""
    if not self.custom_fields:
        return []
    return self.custom_fields.get("crm_integration_tracking", [])

def get_latest_crm_interest(self) -> Optional[Dict[str, Any]]:
    """Get the latest CRM integration interest"""
    history = self.get_crm_integration_history()
    return history[-1] if history else None

# Add methods to Lead class
Lead.add_crm_integration_tracking = add_crm_integration_tracking
Lead.get_crm_integration_history = get_crm_integration_history  
Lead.get_latest_crm_interest = get_latest_crm_interest
