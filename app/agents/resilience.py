"""
Resilience patterns for agent operations - Circuit breaker and retry strategies
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import Any, Callable, Optional, Dict, Tuple
from enum import Enum

from app.core.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenException
from app.core.config import get_settings
settings = get_settings()

logger = logging.getLogger(__name__)


class AgentCircuitBreaker:
    """Circuit breaker for agent operations"""

    def __init__(self, agent_name: str, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.agent_name = agent_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

        logger.info(f"Circuit breaker initialized for agent: {agent_name}")

    async def call(self, agent_method, *args, **kwargs):
        """Execute agent method with circuit breaker protection"""

        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
                logger.info(f"Circuit breaker transitioning to HALF_OPEN for {self.agent_name}")
            else:
                raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for agent {self.agent_name}")

        try:
            result = await agent_method(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = 'CLOSED'

    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker tripped to OPEN for {self.agent_name}")


class AgentRetryHandler:
    """Handles retries and fallbacks for agent operations"""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute_with_retry(
        self,
        operation,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        *args,
        **kwargs
    ):
        """Execute operation with exponential backoff retry"""

        max_retries = max_retries or self.max_retries
        backoff_factor = backoff_factor or self.backoff_factor

        last_exception = None

        for attempt in range(max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed for operation: {e}")

                if attempt < max_retries - 1:
                    delay = backoff_factor ** attempt
                    await asyncio.sleep(delay)

        # All retries failed
        raise last_exception

    async def execute_with_fallback(
        self,
        primary_operation,
        fallback_operation,
        *args,
        **kwargs
    ):
        """Execute primary operation with fallback"""

        try:
            return await primary_operation(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary operation failed, using fallback: {e}")
            return await fallback_operation(*args, **kwargs)


class AgentResilienceManager:
    """Manages resilience patterns for all agents"""

    def __init__(self):
        self.circuit_breakers: Dict[str, AgentCircuitBreaker] = {}
        self.retry_handlers: Dict[str, AgentRetryHandler] = {}
        self.fallback_strategies: Dict[str, Dict[str, Callable]] = {}

        # Initialize circuit breakers for each agent
        self._init_circuit_breakers()

    def _init_circuit_breakers(self):
        """Initialize circuit breakers for all agents"""
        agents = ['lead_generation', 'content_creator', 'ad_manager']

        for agent in agents:
            self.circuit_breakers[agent] = AgentCircuitBreaker(
                agent_name=agent,
                failure_threshold=settings.circuit_breaker.failure_threshold,
                recovery_timeout=settings.circuit_breaker.recovery_timeout
            )

            self.retry_handlers[agent] = AgentRetryHandler()

    def register_fallback(self, agent_name: str, operation_name: str, fallback_func: Callable):
        """Register a fallback function for an agent operation"""
        if agent_name not in self.fallback_strategies:
            self.fallback_strategies[agent_name] = {}

        self.fallback_strategies[agent_name][operation_name] = fallback_func
        logger.info(f"Registered fallback for {agent_name}.{operation_name}")

    async def execute_with_resilience(
        self,
        agent_name: str,
        operation: Callable,
        operation_name: str = "default",
        use_retry: bool = True,
        use_fallback: bool = True,
        *args,
        **kwargs
    ) -> Any:
        """Execute agent operation with full resilience patterns"""

        circuit_breaker = self.circuit_breakers.get(agent_name)
        retry_handler = self.retry_handlers.get(agent_name)

        if not circuit_breaker or not retry_handler:
            raise ValueError(f"No resilience configuration found for agent: {agent_name}")

        try:
            # Execute with circuit breaker protection
            if use_retry:
                # Execute with retry logic
                result = await retry_handler.execute_with_retry(
                    lambda: circuit_breaker.call(operation, *args, **kwargs)
                )
            else:
                # Execute directly with circuit breaker
                result = await circuit_breaker.call(operation, *args, **kwargs)

            return result

        except Exception as e:
            # Try fallback if available
            if use_fallback:
                fallback = self.fallback_strategies.get(agent_name, {}).get(operation_name)
                if fallback:
                    logger.info(f"Using fallback for {agent_name}.{operation_name}")
                    try:
                        return await fallback(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed for {agent_name}.{operation_name}: {fallback_error}")
                        raise fallback_error

            # No fallback or fallback failed
            raise e

    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get resilience status for an agent"""
        circuit_breaker = self.circuit_breakers.get(agent_name)
        if not circuit_breaker:
            return {"error": f"No circuit breaker found for agent: {agent_name}"}

        return {
            "agent_name": agent_name,
            "circuit_breaker_state": circuit_breaker.state,
            "failure_count": circuit_breaker.failure_count,
            "last_failure_time": circuit_breaker.last_failure_time,
            "has_fallbacks": agent_name in self.fallback_strategies
        }

    def reset_agent(self, agent_name: str):
        """Reset circuit breaker for an agent"""
        circuit_breaker = self.circuit_breakers.get(agent_name)
        if circuit_breaker:
            circuit_breaker.failure_count = 0
            circuit_breaker.last_failure_time = None
            circuit_breaker.state = 'CLOSED'
            logger.info(f"Reset circuit breaker for agent: {agent_name}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        results = {}

        for agent_name, circuit_breaker in self.circuit_breakers.items():
            results[agent_name] = {
                "circuit_breaker": circuit_breaker.state,
                "failures": circuit_breaker.failure_count,
                "healthy": circuit_breaker.state == 'CLOSED'
            }

        # Overall health
        all_healthy = all(status["healthy"] for status in results.values())
        results["overall_health"] = "healthy" if all_healthy else "degraded"

        return results


# Global resilience manager instance
_resilience_manager = None


def get_resilience_manager() -> AgentResilienceManager:
    """Get the global resilience manager instance"""
    global _resilience_manager
    if _resilience_manager is None:
        _resilience_manager = AgentResilienceManager()
    return _resilience_manager


# Convenience functions
async def execute_agent_operation(
    agent_name: str,
    operation: Callable,
    operation_name: str = "default",
    *args,
    **kwargs
) -> Any:
    """Execute agent operation with resilience patterns"""
    manager = get_resilience_manager()
    return await manager.execute_with_resilience(
        agent_name, operation, operation_name, *args, **kwargs
    )


def register_agent_fallback(agent_name: str, operation_name: str, fallback_func: Callable):
    """Register a fallback function for an agent operation"""
    manager = get_resilience_manager()
    manager.register_fallback(agent_name, operation_name, fallback_func)


def get_agent_health() -> Dict[str, Any]:
    """Get health status of all agents"""
    manager = get_resilience_manager()
    # Run health check synchronously for API compatibility
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(manager.health_check())
    finally:
        loop.close()
