"""
Agent Monitoring and Observability with LangSmith Integration
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class AgentMonitor:
    """Monitor agent performance and integrate with LangSmith"""

    def __init__(self):
        self.metrics = {
            "agent_calls": {},
            "response_times": {},
            "error_rates": {},
            "success_rates": {}
        }
        self.langsmith_enabled = self._check_langsmith_config()

        if self.langsmith_enabled:
            self._init_langsmith()
        else:
            logger.warning("LangSmith not configured - observability features limited")

    def _check_langsmith_config(self) -> bool:
        """Check if LangSmith is properly configured"""
        return (
            settings.langsmith.api_key and
            settings.langsmith.api_key != "your_langsmith_api_key" and
            settings.langsmith.tracing_v2
        )

    def _init_langsmith(self):
        """Initialize LangSmith client"""
        try:
            from langsmith import Client
            self.langsmith_client = Client(
                api_key=settings.langsmith.api_key,
                api_url=settings.langsmith.endpoint
            )
            logger.info("LangSmith client initialized")
        except ImportError:
            logger.warning("LangSmith package not available")
            self.langsmith_enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith: {e}")
            self.langsmith_enabled = False

    async def record_agent_execution(
        self,
        agent_name: str,
        execution_time: float,
        success: bool,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record agent execution metrics"""

        # Update local metrics
        if agent_name not in self.metrics["agent_calls"]:
            self.metrics["agent_calls"][agent_name] = 0
            self.metrics["response_times"][agent_name] = []
            self.metrics["error_rates"][agent_name] = 0
            self.metrics["success_rates"][agent_name] = 0

        self.metrics["agent_calls"][agent_name] += 1

        if success:
            self.metrics["response_times"][agent_name].append(execution_time)
            # Keep only last 100 measurements
            if len(self.metrics["response_times"][agent_name]) > 100:
                self.metrics["response_times"][agent_name].pop(0)
        else:
            self.metrics["error_rates"][agent_name] += 1

        # Calculate success rate
        total_calls = self.metrics["agent_calls"][agent_name]
        error_count = self.metrics["error_rates"][agent_name]
        self.metrics["success_rates"][agent_name] = (total_calls - error_count) / total_calls

        # Send to LangSmith if enabled
        if self.langsmith_enabled:
            await self._send_to_langsmith(
                agent_name, execution_time, success, error, metadata
            )

        # Log the execution
        log_data = {
            "agent": agent_name,
            "execution_time": execution_time,
            "success": success,
            "error": error,
            "metadata": metadata
        }
        logger.info("Agent execution recorded", **log_data)

    async def _send_to_langsmith(
        self,
        agent_name: str,
        execution_time: float,
        success: bool,
        error: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ):
        """Send metrics to LangSmith"""
        try:
            run_data = {
                "name": f"agent_execution_{agent_name}",
                "run_type": "chain",
                "inputs": metadata or {},
                "outputs": {
                    "success": success,
                    "execution_time": execution_time,
                    "error": error
                },
                "tags": [agent_name, "agent_execution"],
                "metadata": {
                    "agent_name": agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            # Create run in LangSmith
            self.langsmith_client.create_run(**run_data)

        except Exception as e:
            logger.error(f"Failed to send data to LangSmith: {e}")

    def get_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Get metrics for a specific agent"""
        if agent_name not in self.metrics["agent_calls"]:
            return {"error": f"No metrics found for agent: {agent_name}"}

        response_times = self.metrics["response_times"][agent_name]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "agent_name": agent_name,
            "total_calls": self.metrics["agent_calls"][agent_name],
            "success_rate": self.metrics["success_rates"][agent_name],
            "error_count": self.metrics["error_rates"][agent_name],
            "avg_response_time": avg_response_time,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all agents"""
        all_metrics = {}
        for agent_name in self.metrics["agent_calls"].keys():
            all_metrics[agent_name] = self.get_agent_metrics(agent_name)

        return {
            "agents": all_metrics,
            "langsmith_enabled": self.langsmith_enabled,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_langsmith_runs(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent runs from LangSmith"""
        if not self.langsmith_enabled:
            return []

        try:
            filters = {}
            if agent_name:
                filters["tags"] = [agent_name]

            runs = self.langsmith_client.list_runs(
                project_name=settings.langsmith.project,
                limit=limit,
                **filters
            )

            return [
                {
                    "run_id": run.id,
                    "name": run.name,
                    "status": run.status,
                    "start_time": run.start_time.isoformat() if run.start_time else None,
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "execution_time": (run.end_time - run.start_time).total_seconds() if run.end_time and run.start_time else None,
                    "tags": run.tags,
                    "metadata": run.extra.get("metadata", {}) if run.extra else {}
                }
                for run in runs
            ]

        except Exception as e:
            logger.error(f"Failed to get LangSmith runs: {e}")
            return []

    async def create_campaign_trace(
        self,
        campaign_id: str,
        campaign_config: Dict[str, Any],
        final_state: Dict[str, Any]
    ):
        """Create a comprehensive trace for a campaign execution"""
        if not self.langsmith_enabled:
            return

        try:
            trace_data = {
                "name": f"campaign_execution_{campaign_id}",
                "run_type": "chain",
                "inputs": campaign_config,
                "outputs": {
                    "campaign_id": campaign_id,
                    "success": len(final_state.get("errors", [])) == 0,
                    "qualified_leads": len(final_state.get("qualified_leads", [])),
                    "content_created": len(final_state.get("generated_content", [])),
                    "performance_score": final_state.get("campaign_performance", {}).get("overall_score", 0)
                },
                "tags": ["campaign", "orchestration"],
                "metadata": {
                    "campaign_id": campaign_id,
                    "agent_sequence": ["lead_generation", "content_creation", "ad_management"],
                    "errors": final_state.get("errors", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            self.langsmith_client.create_run(**trace_data)
            logger.info(f"Campaign trace created for {campaign_id}")

        except Exception as e:
            logger.error(f"Failed to create campaign trace: {e}")


# Global monitor instance
_monitor = None


def get_agent_monitor() -> AgentMonitor:
    """Get the global agent monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = AgentMonitor()
    return _monitor


# Convenience functions
async def record_agent_execution(
    agent_name: str,
    execution_time: float,
    success: bool,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Record agent execution metrics"""
    monitor = get_agent_monitor()
    await monitor.record_agent_execution(agent_name, execution_time, success, error, metadata)


def get_agent_metrics(agent_name: str) -> Dict[str, Any]:
    """Get metrics for a specific agent"""
    monitor = get_agent_monitor()
    return monitor.get_agent_metrics(agent_name)


def get_all_agent_metrics() -> Dict[str, Any]:
    """Get metrics for all agents"""
    monitor = get_agent_monitor()
    return monitor.get_all_metrics()