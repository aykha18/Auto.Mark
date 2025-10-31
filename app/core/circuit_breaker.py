"""
Circuit Breaker Pattern Implementation
Provides resilience for external API calls with automatic failure detection and recovery
"""

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Optional, Dict, Tuple
from contextlib import asynccontextmanager
import structlog

from app.core.config import get_settings
settings = get_settings()
from app.core.metrics import circuit_breaker_state, circuit_breaker_failures


logger = structlog.get_logger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation with configurable failure thresholds and recovery logic
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Tuple[Exception, ...] = (Exception,),
        success_threshold: int = 3,
    ):
        """
        Initialize circuit breaker

        Args:
            service_name: Name of the service being protected
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            expected_exception: Exception types that count as failures
            success_threshold: Number of successes needed in half-open state
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None

        # Update metrics
        circuit_breaker_state.labels(service_name=service_name).set(0)

        logger.info(
            "Circuit breaker initialized",
            service_name=service_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: When circuit is open
        """
        if self.state == CircuitBreakerState.OPEN:
            if not self._should_attempt_reset():
                logger.warning(
                    "Circuit breaker is OPEN, rejecting request",
                    service_name=self.service_name,
                    time_since_failure=time.time() - (self.last_failure_time or 0)
                )
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN for service {self.service_name}"
                )
            else:
                self.state = CircuitBreakerState.HALF_OPEN
                circuit_breaker_state.labels(service_name=self.service_name).set(2)
                logger.info(
                    "Circuit breaker transitioning to HALF_OPEN",
                    service_name=self.service_name
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self):
        """Handle successful operation"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._reset()
        # In CLOSED state, success is normal - no action needed

    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Failed during recovery test - go back to OPEN
            self._trip()
        elif self.failure_count >= self.failure_threshold:
            # Too many failures - trip the circuit
            self._trip()

        # Update metrics
        circuit_breaker_failures.labels(service_name=self.service_name).inc()

    def _trip(self):
        """Trip the circuit breaker to OPEN state"""
        self.state = CircuitBreakerState.OPEN
        circuit_breaker_state.labels(service_name=self.service_name).set(1)
        logger.warning(
            "Circuit breaker tripped to OPEN",
            service_name=self.service_name,
            failure_count=self.failure_count
        )

    def _reset(self):
        """Reset circuit breaker to CLOSED state"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        circuit_breaker_state.labels(service_name=self.service_name).set(0)
        logger.info(
            "Circuit breaker reset to CLOSED",
            service_name=self.service_name
        )

    @property
    def is_closed(self) -> bool:
        """Check if circuit breaker is closed"""
        return self.state == CircuitBreakerState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        return self.state == CircuitBreakerState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit breaker is half-open"""
        return self.state == CircuitBreakerState.HALF_OPEN


# Global circuit breaker registry
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """
    Get or create a circuit breaker for a service

    Args:
        service_name: Name of the service

    Returns:
        CircuitBreaker instance
    """
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(
            service_name=service_name,
            failure_threshold=settings.circuit_breaker.failure_threshold,
            recovery_timeout=settings.circuit_breaker.recovery_timeout,
        )
    return _circuit_breakers[service_name]


def setup_circuit_breakers():
    """
    Initialize circuit breakers for external services
    """
    # Pre-initialize circuit breakers for known services
    services = [
        "grok_api",
        "openai_api",
        "pinecone_api",
        "google_ads_api",
        "linkedin_api",
        "serpapi",
    ]

    for service in services:
        get_circuit_breaker(service)

    logger.info("Circuit breakers initialized", services=services)


@asynccontextmanager
async def circuit_breaker_context(service_name: str):
    """
    Context manager for circuit breaker protection

    Args:
        service_name: Name of the service

    Usage:
        async with circuit_breaker_context("grok_api"):
            result = await grok_api.call(...)
    """
    breaker = get_circuit_breaker(service_name)

    try:
        yield breaker
    except CircuitBreakerOpenException:
        # Circuit is open, provide fallback or graceful degradation
        logger.warning(
            "Circuit breaker open, using fallback",
            service_name=service_name
        )
        raise


async def call_with_circuit_breaker(service_name: str, func: Callable, *args, **kwargs) -> Any:
    """
    Call a function with circuit breaker protection

    Args:
        service_name: Name of the service
        func: Function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    breaker = get_circuit_breaker(service_name)
    return await breaker.call(func, *args, **kwargs)


# Decorator for circuit breaker protection
def with_circuit_breaker(service_name: str):
    """
    Decorator to add circuit breaker protection to async functions

    Args:
        service_name: Name of the service

    Usage:
        @with_circuit_breaker("grok_api")
        async def call_grok_api(prompt):
            return await grok_api.generate(prompt)
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            return await call_with_circuit_breaker(service_name, func, *args, **kwargs)
        return wrapper
    return decorator
