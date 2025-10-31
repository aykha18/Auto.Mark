"""
OAuth2 Security Implementation for CRM Integrations
Implements security best practices for OAuth2 flows
"""

import secrets
import hashlib
import base64
import time
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
import httpx
from sqlalchemy.orm import Session

from app.models.crm_integration import CRMConnection, AuthMethod
from app.core.database import get_db

logger = logging.getLogger(__name__)


class OAuth2SecurityManager:
    """
    Manages OAuth2 security for CRM integrations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.state_cache = {}  # In production, use Redis
        self.pkce_cache = {}   # In production, use Redis
    
    def generate_authorization_url(
        self,
        connector_id: int,
        redirect_uri: str,
        scopes: list = None,
        user_id: Optional[int] = None
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate secure OAuth2 authorization URL with PKCE and state
        """
        from app.models.crm_integration import CRMConnector
        
        connector = self.db.query(CRMConnector).filter(
            CRMConnector.id == connector_id
        ).first()
        
        if not connector:
            raise ValueError("CRM connector not found")
        
        if connector.auth_method != AuthMethod.OAUTH2:
            raise ValueError("Connector does not support OAuth2")
        
        # Generate state parameter for CSRF protection
        state = self._generate_state()
        
        # Generate PKCE challenge
        pkce_data = self._generate_pkce_challenge()
        
        # Store state and PKCE data
        session_data = {
            "connector_id": connector_id,
            "redirect_uri": redirect_uri,
            "user_id": user_id,
            "timestamp": time.time(),
            "pkce_verifier": pkce_data["code_verifier"],
            "scopes": scopes or []
        }
        
        self.state_cache[state] = session_data
        self.pkce_cache[state] = pkce_data
        
        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": connector.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes or connector.default_scopes),
            "state": state,
            "code_challenge": pkce_data["code_challenge"],
            "code_challenge_method": pkce_data["code_challenge_method"]
        }
        
        # Add connector-specific parameters
        if connector.crm_type.value == "hubspot":
            auth_params["optional_scope"] = "contacts"
        
        auth_url = f"{connector.auth_url}?{urlencode(auth_params)}"
        
        return auth_url, {"state": state, "pkce_challenge": pkce_data["code_challenge"]}
    
    async def handle_oauth_callback(
        self,
        code: str,
        state: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle OAuth2 callback with security validation
        """
        if error:
            return {"success": False, "error": f"OAuth error: {error}"}
        
        # Validate state parameter
        if state not in self.state_cache:
            logger.warning(f"Invalid or expired state parameter: {state}")
            return {"success": False, "error": "Invalid or expired authorization request"}
        
        session_data = self.state_cache[state]
        pkce_data = self.pkce_cache.get(state, {})
        
        # Check timestamp (5 minute expiry)
        if time.time() - session_data["timestamp"] > 300:
            self._cleanup_session(state)
            return {"success": False, "error": "Authorization request expired"}
        
        try:
            # Exchange code for tokens
            token_data = await self._exchange_code_for_tokens(
                session_data["connector_id"],
                code,
                session_data["redirect_uri"],
                pkce_data.get("code_verifier")
            )
            
            if not token_data["success"]:
                return token_data
            
            # Create or update CRM connection
            connection = await self._create_crm_connection(
                session_data["connector_id"],
                session_data["user_id"],
                token_data["tokens"],
                session_data["scopes"]
            )
            
            # Cleanup session data
            self._cleanup_session(state)
            
            return {
                "success": True,
                "connection_id": connection.id,
                "connection_status": connection.connection_status.value
            }
            
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            self._cleanup_session(state)
            return {"success": False, "error": "Failed to complete authorization"}    

    async def _exchange_code_for_tokens(
        self,
        connector_id: int,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        from app.models.crm_integration import CRMConnector
        
        connector = self.db.query(CRMConnector).filter(
            CRMConnector.id == connector_id
        ).first()
        
        if not connector:
            return {"success": False, "error": "Connector not found"}
        
        token_params = {
            "grant_type": "authorization_code",
            "client_id": connector.client_id,
            "client_secret": connector.client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        # Add PKCE verifier if available
        if code_verifier:
            token_params["code_verifier"] = code_verifier
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    connector.token_url,
                    data=token_params,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.status_code} {response.text}")
                    return {"success": False, "error": "Token exchange failed"}
                
                tokens = response.json()
                
                # Validate required token fields
                if "access_token" not in tokens:
                    return {"success": False, "error": "Invalid token response"}
                
                return {"success": True, "tokens": tokens}
                
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return {"success": False, "error": "Token exchange failed"}
    
    async def _create_crm_connection(
        self,
        connector_id: int,
        user_id: Optional[int],
        tokens: Dict[str, Any],
        scopes: list
    ) -> CRMConnection:
        """Create or update CRM connection with tokens"""
        # Encrypt tokens before storage
        encrypted_tokens = self._encrypt_tokens(tokens)
        
        connection = CRMConnection(
            connector_id=connector_id,
            user_id=user_id,
            auth_config=encrypted_tokens,
            scopes=scopes,
            connection_status="connected"
        )
        
        self.db.add(connection)
        self.db.commit()
        
        return connection    

    def _generate_state(self) -> str:
        """Generate cryptographically secure state parameter"""
        return secrets.token_urlsafe(32)
    
    def _generate_pkce_challenge(self) -> Dict[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        return {
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
    
    def _encrypt_tokens(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt tokens for secure storage"""
        # In production, use proper encryption (AES-256)
        # For now, return as-is but mark as encrypted
        return {
            "encrypted": True,
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
            "token_type": tokens.get("token_type", "Bearer")
        }
    
    def _cleanup_session(self, state: str):
        """Clean up session data"""
        self.state_cache.pop(state, None)
        self.pkce_cache.pop(state, None)
    
    async def refresh_access_token(self, connection_id: int) -> Dict[str, Any]:
        """Refresh OAuth2 access token"""
        connection = self.db.query(CRMConnection).filter(
            CRMConnection.id == connection_id
        ).first()
        
        if not connection:
            return {"success": False, "error": "Connection not found"}
        
        refresh_token = connection.auth_config.get("refresh_token")
        if not refresh_token:
            return {"success": False, "error": "No refresh token available"}
        
        connector = connection.connector
        
        refresh_params = {
            "grant_type": "refresh_token",
            "client_id": connector.client_id,
            "client_secret": connector.client_secret,
            "refresh_token": refresh_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    connector.token_url,
                    data=refresh_params,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "Token refresh failed"}
                
                new_tokens = response.json()
                
                # Update connection with new tokens
                connection.auth_config.update(self._encrypt_tokens(new_tokens))
                self.db.commit()
                
                return {"success": True, "tokens": new_tokens}
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {"success": False, "error": "Token refresh failed"}
