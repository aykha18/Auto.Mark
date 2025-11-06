"""
Security Audit Logging Configuration
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityAuditLogger:
    """Centralized security audit logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler for audit logs
        handler = logging.FileHandler("security_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_payment_attempt(self, customer_email: str, amount: float, 
                          currency: str, ip_address: str = None):
        """Log payment attempt"""
        self.logger.info(json.dumps({
            "event": "payment_attempt",
            "customer_email": customer_email,
            "amount": amount,
            "currency": currency,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def log_payment_success(self, payment_id: str, customer_email: str, 
                          amount: float):
        """Log successful payment"""
        self.logger.info(json.dumps({
            "event": "payment_success",
            "payment_id": payment_id,
            "customer_email": customer_email,
            "amount": amount,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def log_payment_failure(self, customer_email: str, reason: str, 
                          ip_address: str = None):
        """Log payment failure"""
        self.logger.warning(json.dumps({
            "event": "payment_failure",
            "customer_email": customer_email,
            "reason": reason,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log general security event"""
        self.logger.warning(json.dumps({
            "event": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }))

# Global audit logger instance
audit_logger = SecurityAuditLogger()
