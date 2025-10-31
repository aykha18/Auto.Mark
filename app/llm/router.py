"""
LLM Router with Grok-2 Integration
Implements intelligent routing between multiple LLM providers with fallback strategies
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import structlog
from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

# Try to import Anthropic (optional)
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

from app.core.config import get_settings
settings = get_settings()

logger = structlog.get_logger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    GROK_2 = "grok_2"
    CLAUDE_SONNET = "claude_sonnet"
    GPT_4 = "gpt_4"
    GPT_3_5_TURBO = "gpt_3_5_turbo"


@dataclass
class LLMConfig:
    """Configuration for an LLM provider"""
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    cost_per_1k_tokens: float = 0.0
    rate_limit_rpm: int = 60
    timeout: int = 30


@dataclass
class RoutingDecision:
    """Decision made by the router"""
    provider: LLMProvider
    reason: str
    confidence: float
    estimated_cost: float
    estimated_latency: float


class Grok2LLM:
    """Custom wrapper for Grok-2 (simplified for now)"""

    def __init__(self, api_key: str, model_name: str = "grok-2", **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 4096)

        # Initialize xAI client (placeholder - would use actual xAI SDK)
        try:
            import xai_grok
            self.client = xai_grok.Client(api_key=api_key)
        except ImportError:
            logger.warning("xAI Grok SDK not available, using mock implementation")
            self.client = None

    def invoke(self, messages, **kwargs):
        """Generate response from Grok-2"""
        try:
            if self.client:
                # Real implementation would use xAI SDK
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content
            else:
                # Mock implementation for development
                return self._mock_response(messages)
        except Exception as e:
            logger.error(f"Grok-2 API error: {e}")
            raise

    async def ainvoke(self, messages, **kwargs):
        """Async generate response from Grok-2"""
        # For now, just call sync version
        return self.invoke(messages, **kwargs)

    def _mock_response(self, messages) -> str:
        """Mock response for development/testing"""
        last_message = messages[-1]['content'] if messages else "Hello"
        return f"Grok-2 Response to: {last_message[:50]}... This is a mock response for development."


class LLMRouter:
    """Intelligent LLM router with cost optimization and fallback strategies"""

    def __init__(self):
        self.providers = self._initialize_providers()
        self.usage_stats = {}
        self.rate_limiters = {}
        self._initialize_rate_limiters()

    def _initialize_providers(self) -> Dict[LLMProvider, LLMConfig]:
        """Initialize LLM provider configurations"""
        return {
            LLMProvider.GROK_2: LLMConfig(
                provider=LLMProvider.GROK_2,
                model_name="grok-2",
                api_key=settings.external_apis.grok_api_key,
                cost_per_1k_tokens=0.002,  # Example pricing
                rate_limit_rpm=30,
                temperature=0.7
            ),
            LLMProvider.CLAUDE_SONNET: LLMConfig(
                provider=LLMProvider.CLAUDE_SONNET,
                model_name="claude-3-sonnet-20240229",
                api_key=settings.external_apis.anthropic_api_key,
                cost_per_1k_tokens=0.015,
                rate_limit_rpm=50,
                temperature=0.7
            ),
            LLMProvider.GPT_4: LLMConfig(
                provider=LLMProvider.GPT_4,
                model_name="gpt-4-turbo-preview",
                api_key=settings.llm.openai_api_key,
                cost_per_1k_tokens=0.01,
                rate_limit_rpm=100,
                temperature=0.7
            ),
            LLMProvider.GPT_3_5_TURBO: LLMConfig(
                provider=LLMProvider.GPT_3_5_TURBO,
                model_name="gpt-3.5-turbo",
                api_key=settings.llm.openai_api_key,
                cost_per_1k_tokens=0.002,
                rate_limit_rpm=3500,
                temperature=0.7
            )
        }

    def _initialize_rate_limiters(self):
        """Initialize rate limiters for each provider"""
        for provider, config in self.providers.items():
            self.rate_limiters[provider] = {
                'requests': [],
                'rpm_limit': config.rate_limit_rpm
            }

    def _check_rate_limit(self, provider: LLMProvider) -> bool:
        """Check if provider is within rate limits"""
        limiter = self.rate_limiters[provider]
        current_time = time.time()

        # Remove requests older than 1 minute
        limiter['requests'] = [
            req_time for req_time in limiter['requests']
            if current_time - req_time < 60
        ]

        return len(limiter['requests']) < limiter['rpm_limit']

    def _record_request(self, provider: LLMProvider):
        """Record a request for rate limiting"""
        self.rate_limiters[provider]['requests'].append(time.time())

    def _analyze_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task to determine optimal LLM routing"""
        task_lower = task_description.lower()

        # Task complexity analysis
        complexity_score = 0
        if len(task_description.split()) > 100:
            complexity_score += 2
        if any(keyword in task_lower for keyword in ['analyze', 'compare', 'evaluate', 'optimize']):
            complexity_score += 1
        if any(keyword in task_lower for keyword in ['creative', 'generate', 'design']):
            complexity_score += 1

        # Context analysis
        has_code = 'code' in task_lower or '```' in task_description
        has_math = any(char in task_description for char in ['=', '+', '-', '*', '/'])
        needs_research = any(keyword in task_lower for keyword in ['research', 'find', 'discover'])

        # Cost sensitivity
        budget_conscious = context.get('budget_conscious', False)
        speed_priority = context.get('speed_priority', False)

        return {
            'complexity': complexity_score,
            'has_code': has_code,
            'has_math': has_math,
            'needs_research': needs_research,
            'budget_conscious': budget_conscious,
            'speed_priority': speed_priority
        }

    def _make_routing_decision(self, task_analysis: Dict[str, Any]) -> RoutingDecision:
        """Make intelligent routing decision based on task analysis"""

        # Priority order: Grok-2 > Claude > GPT-4 > GPT-3.5
        fallback_order = [
            LLMProvider.GROK_2,
            LLMProvider.CLAUDE_SONNET,
            LLMProvider.GPT_4,
            LLMProvider.GPT_3_5_TURBO
        ]

        for provider in fallback_order:
            config = self.providers[provider]

            # Skip if no API key
            if not config.api_key or config.api_key == f"your_{provider.value}_api_key":
                continue

            # Check rate limits
            if not self._check_rate_limit(provider):
                continue

            # Calculate estimated cost and latency
            estimated_tokens = 1000  # Rough estimate
            estimated_cost = (estimated_tokens / 1000) * config.cost_per_1k_tokens

            # Base latency estimates
            latency_estimates = {
                LLMProvider.GROK_2: 2.0,
                LLMProvider.CLAUDE_SONNET: 1.5,
                LLMProvider.GPT_4: 3.0,
                LLMProvider.GPT_3_5_TURBO: 1.0
            }
            estimated_latency = latency_estimates[provider]

            # Determine if this provider is suitable
            reason = self._get_selection_reason(provider, task_analysis)

            return RoutingDecision(
                provider=provider,
                reason=reason,
                confidence=0.9,  # High confidence in routing logic
                estimated_cost=estimated_cost,
                estimated_latency=estimated_latency
            )

        # Fallback to GPT-3.5 if nothing else available
        return RoutingDecision(
            provider=LLMProvider.GPT_3_5_TURBO,
            reason="Fallback: No preferred providers available",
            confidence=0.5,
            estimated_cost=0.002,
            estimated_latency=1.0
        )

    def _get_selection_reason(self, provider: LLMProvider, task_analysis: Dict[str, Any]) -> str:
        """Get reason for selecting this provider"""
        reasons = {
            LLMProvider.GROK_2: "Grok-2 selected for innovative reasoning and real-time knowledge",
            LLMProvider.CLAUDE_SONNET: "Claude Sonnet selected for balanced performance and safety",
            LLMProvider.GPT_4: "GPT-4 selected for complex reasoning and analysis",
            LLMProvider.GPT_3_5_TURBO: "GPT-3.5 Turbo selected for speed and cost efficiency"
        }
        return reasons.get(provider, "Default selection")

    def get_llm(self, task_description: str = "", context: Dict[str, Any] = None) -> BaseLanguageModel:
        """Get the optimal LLM for the given task"""
        context = context or {}

        # Analyze task
        task_analysis = self._analyze_task(task_description, context)

        # Make routing decision
        decision = self._make_routing_decision(task_analysis)

        # Record the decision
        self._record_request(decision.provider)

        logger.info(
            "LLM routing decision",
            provider=decision.provider.value,
            reason=decision.reason,
            estimated_cost=decision.estimated_cost,
            task_complexity=task_analysis['complexity']
        )

        # Create and return the LLM instance
        return self._create_llm_instance(decision.provider)

    def _create_llm_instance(self, provider: LLMProvider) -> BaseLanguageModel:
        """Create LLM instance for the selected provider"""
        config = self.providers[provider]

        if provider == LLMProvider.GROK_2:
            return Grok2LLM(
                api_key=config.api_key,
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

        elif provider == LLMProvider.CLAUDE_SONNET:
            if not ANTHROPIC_AVAILABLE or not ChatAnthropic:
                raise ValueError("Anthropic Claude not available - install langchain-anthropic")
            return ChatAnthropic(
                model=config.model_name,
                anthropic_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

        elif provider in [LLMProvider.GPT_4, LLMProvider.GPT_3_5_TURBO]:
            return ChatOpenAI(
                model=config.model_name,
                openai_api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all providers"""
        return {
            provider.value: {
                'requests_last_minute': len(limiter['requests']),
                'rate_limit': limiter['rpm_limit']
            }
            for provider, limiter in self.rate_limiters.items()
        }

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        for provider, config in self.providers.items():
            if config.api_key and config.api_key != f"your_{provider.value}_api_key":
                available.append(provider.value)
        return available


# Global router instance
_router = None


def get_llm_router() -> LLMRouter:
    """Get global LLM router instance"""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


def get_optimal_llm(task_description: str = "", context: Dict[str, Any] = None) -> BaseLanguageModel:
    """Convenience function to get optimal LLM for a task"""
    router = get_llm_router()
    return router.get_llm(task_description, context)
