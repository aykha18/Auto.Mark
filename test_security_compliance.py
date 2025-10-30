"""
Security and Compliance Validation Tests
Tests OAuth2 security, webhook verification, fraud detection, and PCI compliance
"""

import pytest
import asyncio
import json
import time
import hmac
import hashlib
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.security_middleware import (
    OAuth2SecurityValidator, 
    WebhookSecurityValidator, 
    FraudDetectionService,
    PCIComplianceValidator
)
from app.core.oauth2_security import OAuth2SecurityManager
from app.core.webhook_security import WebhookSecurityManager, PaymentFraudDetector
from app.core.stripe_service import StripePaymentService
from app.models.crm_integration import CRMConnector, CRMType, AuthMethod


class TestOAuth2Security:
    """Test OAuth2 security best practices"""
    
    def test_oauth2_config_validation_secure(self):
        """Test OAuth2 configuration validation for secure setup"""
        secure_config = {
            "use_pkce": True,
            "redirect_uris": ["https://app.automark.ai/callback"],
            "scopes": ["read:contacts", "read:companies"],
            "scope_validation": True,
            "encrypt_tokens": True,
            "use_state_parameter": True,
            "environment": "production"
        }
        
        result = OAuth2SecurityValidator.validate_oauth2_config(secure_config)
        
        assert result["is_secure"] is True
        assert result["security_score"] == 100
        assert len(result["issues"]) == 0
    
    def test_oauth2_config_validation_insecure(self):
        """Test OAuth2 configuration validation for insecure setup"""
        insecure_config = {
            "use_pkce": False,
            "redirect_uris": ["http://localhost:3000/callback"],
            "scopes": ["write:all"],
            "scope_validation": False,
            "encrypt_tokens": False,
            "use_state_parameter": False,
            "environment": "production"
        }
        
        result = OAuth2SecurityValidator.validate_oauth2_config(insecure_config)
        
        assert result["is_secure"] is False
        assert result["security_score"] < 100
        assert len(result["issues"]) > 0
        assert "PKCE not enabled" in result["issues"][0]
    
    def test_pkce_generation(self):
        """Test PKCE code challenge generation"""
        pkce_data = OAuth2SecurityValidator.generate_pkce_challenge()
        
        assert "code_verifier" in pkce_data
        assert "code_challenge" in pkce_data
        assert "code_challenge_method" in pkce_data
        assert pkce_data["code_challenge_method"] == "S256"
        assert len(pkce_data["code_verifier"]) > 32
        assert len(pkce_data["code_challenge"]) > 32
    
    def test_state_generation(self):
        """Test secure state parameter generation"""
        state1 = OAuth2SecurityValidator.generate_secure_state()
        state2 = OAuth2SecurityValidator.generate_secure_state()
        
        assert len(state1) > 32
        assert len(state2) > 32
        assert state1 != state2  # Should be unique
    
    @pytest.mark.asyncio
    async def test_oauth2_authorization_url_generation(self):
        """Test OAuth2 authorization URL generation with security"""
        # Mock database session
        mock_db = Mock(spec=Session)
        
        # Mock CRM connector
        mock_connector = Mock()
        mock_connector.id = 1
        mock_connector.auth_method = AuthMethod.OAUTH2
        mock_connector.client_id = "test_client_id"
        mock_connector.auth_url = "https://api.example.com/oauth/authorize"
        mock_connector.default_scopes = ["read:contacts"]
        mock_connector.crm_type = Mock()
        mock_connector.crm_type.value = "pipedrive"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_connector
        
        oauth_manager = OAuth2SecurityManager(mock_db)
        
        auth_url, session_data = oauth_manager.generate_authorization_url(
            connector_id=1,
            redirect_uri="https://app.automark.ai/callback",
            scopes=["read:contacts", "read:companies"],
            user_id=123
        )
        
        assert "https://api.example.com/oauth/authorize" in auth_url
        assert "code_challenge=" in auth_url
        assert "code_challenge_method=S256" in auth_url
        assert "state=" in auth_url
        assert "state" in session_data
        assert "pkce_challenge" in session_data


class TestWebhookSecurity:
    """Test webhook security validation"""
    
    def test_stripe_webhook_signature_validation_valid(self):
        """Test valid Stripe webhook signature validation"""
        payload = '{"id": "evt_test", "type": "payment_intent.succeeded"}'
        secret = "whsec_test_secret"
        timestamp = str(int(time.time()))
        
        # Generate valid signature
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        stripe_signature = f"t={timestamp},v1={signature}"
        
        # Mock Stripe webhook validation
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = {"id": "evt_test", "type": "payment_intent.succeeded"}
            
            result = WebhookSecurityValidator.validate_stripe_webhook(
                payload, stripe_signature, secret
            )
            
            assert result is True
    
    def test_stripe_webhook_signature_validation_invalid(self):
        """Test invalid Stripe webhook signature validation"""
        payload = '{"id": "evt_test", "type": "payment_intent.succeeded"}'
        secret = "whsec_test_secret"
        invalid_signature = "t=123456789,v1=invalid_signature"
        
        result = WebhookSecurityValidator.validate_stripe_webhook(
            payload, invalid_signature, secret
        )
        
        assert result is False
    
    def test_webhook_timestamp_validation(self):
        """Test webhook timestamp validation for replay attack prevention"""
        current_time = int(time.time())
        
        # Valid timestamp (within tolerance)
        valid_timestamp = current_time - 100
        assert WebhookSecurityValidator.validate_webhook_timestamp(valid_timestamp) is True
        
        # Invalid timestamp (too old)
        old_timestamp = current_time - 400
        assert WebhookSecurityValidator.validate_webhook_timestamp(old_timestamp) is False
        
        # Invalid timestamp (future)
        future_timestamp = current_time + 400
        assert WebhookSecurityValidator.validate_webhook_timestamp(future_timestamp) is False
    
    def test_webhook_signature_generation(self):
        """Test webhook signature generation for outgoing webhooks"""
        payload = '{"event": "test", "data": {"id": "123"}}'
        secret = "webhook_secret_key"
        
        signature = WebhookSecurityValidator.generate_webhook_signature(payload, secret)
        
        assert signature.startswith("sha256=")
        assert len(signature) > 64  # SHA256 hash length
        
        # Verify signature can be validated
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert signature == f"sha256={expected_signature}"


class TestFraudDetection:
    """Test fraud detection system"""
    
    def test_payment_risk_analysis_low_risk(self):
        """Test payment risk analysis for low-risk transaction"""
        fraud_detector = FraudDetectionService()
        
        low_risk_payment = {
            "email": "john.doe@company.com",
            "ip_address": "192.168.1.1",
            "card_fingerprint": "fp_safe_card_123",
            "amount": 250.00
        }
        
        risk_result = fraud_detector.check_payment_risk(low_risk_payment)
        
        assert risk_result["risk_level"] == "low"
        assert risk_result["should_block"] is False
        assert risk_result["requires_review"] is False
    
    def test_payment_risk_analysis_high_risk(self):
        """Test payment risk analysis for high-risk transaction"""
        fraud_detector = FraudDetectionService()
        
        # Simulate rapid attempts by calling multiple times
        high_risk_payment = {
            "email": "suspicious@tempmail.com",
            "ip_address": "192.168.1.100",
            "card_fingerprint": "fp_suspicious_card",
            "amount": 250.00
        }
        
        # Make multiple rapid attempts to trigger fraud detection
        for _ in range(6):
            fraud_detector._check_rapid_attempts(high_risk_payment["email"])
        
        risk_result = fraud_detector.check_payment_risk(high_risk_payment)
        
        assert risk_result["risk_level"] in ["medium", "high"]
        assert len(risk_result["risk_factors"]) > 0
    
    def test_suspicious_email_detection(self):
        """Test suspicious email pattern detection"""
        fraud_detector = FraudDetectionService()
        
        suspicious_emails = [
            "test@tempmail.com",
            "user@10minutemail.com",
            "fake@guerrillamail.com",
            "temp@mailinator.com"
        ]
        
        for email in suspicious_emails:
            assert fraud_detector._check_suspicious_email(email) is True
        
        legitimate_emails = [
            "john@company.com",
            "user@gmail.com",
            "contact@business.org"
        ]
        
        for email in legitimate_emails:
            assert fraud_detector._check_suspicious_email(email) is False
    
    def test_enhanced_fraud_detection(self):
        """Test enhanced fraud detection with multiple risk factors"""
        fraud_detector = PaymentFraudDetector()
        
        high_risk_payment = {
            "amount": 1500,  # High amount
            "email": "test@tempmail.com",  # Suspicious email
            "country": "XX",  # Blacklisted country
            "card_fingerprint": "fp_reused_card"
        }
        
        risk_result = fraud_detector.analyze_payment_risk(high_risk_payment)
        
        assert risk_result["risk_score"] > 50
        assert risk_result["risk_level"] in ["medium", "high"]
        assert len(risk_result["risk_factors"]) >= 2
        assert len(risk_result["recommended_actions"]) > 0


class TestPCICompliance:
    """Test PCI DSS compliance validation"""
    
    def test_pci_compliance_validation(self):
        """Test PCI DSS compliance validation"""
        compliance_result = PCIComplianceValidator.validate_pci_compliance()
        
        assert compliance_result["overall_compliance"] is True
        assert compliance_result["compliance_score"] >= 95
        assert "detailed_checks" in compliance_result
        
        # Check specific compliance areas
        checks = compliance_result["detailed_checks"]
        assert "secure_network" in checks
        assert "cardholder_data_protection" in checks
        assert "vulnerability_management" in checks
        assert "access_control" in checks
        assert "network_monitoring" in checks
        assert "security_policies" in checks
        
        # Verify cardholder data protection (critical for Stripe integration)
        data_protection = checks["cardholder_data_protection"]
        assert data_protection["data_not_stored"] is True
        assert data_protection["encryption_in_transit"] is True
        assert data_protection["encryption_at_rest"] is True


class TestSecurityHeaders:
    """Test security headers implementation"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        client = TestClient(app)
        
        response = client.get("/health")
        
        # Check for security headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        
        # Verify header values
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "nosniff" in response.headers["X-Content-Type-Options"]
    
    def test_csp_header_configuration(self):
        """Test Content Security Policy header configuration"""
        client = TestClient(app)
        
        response = client.get("/health")
        csp_header = response.headers.get("Content-Security-Policy", "")
        
        # Check for essential CSP directives
        assert "default-src 'self'" in csp_header
        assert "script-src" in csp_header
        assert "style-src" in csp_header
        assert "object-src 'none'" in csp_header
        assert "frame-ancestors 'none'" in csp_header
        
        # Check for Stripe-specific allowances
        assert "https://js.stripe.com" in csp_header
        assert "https://api.stripe.com" in csp_header


class TestIntegrationSecurity:
    """Test end-to-end security integration"""
    
    @pytest.mark.asyncio
    async def test_secure_payment_flow(self):
        """Test secure payment flow with fraud detection"""
        # Mock database session
        mock_db = Mock(spec=Session)
        
        # Create Stripe service with security
        stripe_service = StripePaymentService(mock_db)
        
        # Mock payment data
        payment_data = {
            "email": "test@company.com",
            "amount": 250.00,
            "ip_address": "192.168.1.1",
            "card_fingerprint": "fp_safe_card"
        }
        
        # Test fraud detection integration
        risk_result = stripe_service.fraud_detector.analyze_payment_risk(payment_data)
        
        assert risk_result["risk_level"] == "low"
        assert risk_result["should_block"] is False
    
    @pytest.mark.asyncio
    async def test_webhook_security_integration(self):
        """Test webhook security integration"""
        webhook_manager = WebhookSecurityManager()
        
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1"}
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.1"
        
        # Mock Stripe event
        mock_event = {
            "id": "evt_test_123",
            "type": "payment_intent.succeeded",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "amount": 25000,
                    "currency": "usd"
                }
            }
        }
        
        # Test security checks
        security_result = await webhook_manager._perform_webhook_security_checks(
            mock_request, mock_event, "stripe"
        )
        
        assert security_result["is_secure"] is True


if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v", "--tb=short"])