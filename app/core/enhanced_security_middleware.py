"""
Enhanced Security Middleware
Implements rate limiting, request logging, and security headers
"""

import time
import logging
from typing import Dict, Any
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque

logger = logging.getLogger("security")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with rate limiting and logging"""
    
    def __init__(self, app, rate_limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.request_counts: Dict[str, deque] = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Rate limiting check
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # Log security-relevant requests
        if self._is_security_relevant(request):
            logger.info(f"Security request: {request.method} {request.url.path} from {client_ip}")
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add security headers
        self._add_security_headers(response)
        
        # Log slow requests (potential DoS)
        if process_time > 5.0:
            logger.warning(f"Slow request: {process_time:.2f}s for {request.url.path}")
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request headers"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        while self.request_counts[client_ip] and self.request_counts[client_ip][0] < window_start:
            self.request_counts[client_ip].popleft()
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.rate_limit:
            return True
        
        # Add current request
        self.request_counts[client_ip].append(now)
        return False
    
    def _is_security_relevant(self, request: Request) -> bool:
        """Check if request is security-relevant"""
        security_paths = ["/api/v1/payments/", "/api/v1/auth/", "/webhook"]
        return any(path in str(request.url.path) for path in security_paths)
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' https://checkout.razorpay.com; style-src 'self' 'unsafe-inline'",
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
