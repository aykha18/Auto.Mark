"""
RAG Performance Monitoring and Analytics
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

import structlog

from app.core.config import get_settings
settings = get_settings()

logger = structlog.get_logger(__name__)


@dataclass
class RAGQueryMetrics:
    """Metrics for a single RAG query"""
    query: str
    response: str
    confidence: float
    execution_time: float
    success: bool
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    retriever_type: str = "unknown"
    num_docs_retrieved: int = 0
    llm_provider: str = "unknown"


class RAGMonitor:
    """Monitor RAG system performance and usage"""

    def __init__(self):
        self.metrics_history: List[RAGQueryMetrics] = []
        self.performance_stats = defaultdict(list)
        self.error_counts = defaultdict(int)

        # Rolling window for recent metrics (last 1000 queries)
        self.max_history_size = 1000

        logger.info("RAG Monitor initialized")

    async def record_query(self, metrics: RAGQueryMetrics) -> None:
        """Record a RAG query with its metrics"""

        # Set timestamp if not provided
        if metrics.timestamp is None:
            metrics.timestamp = datetime.utcnow()

        # Add to history
        self.metrics_history.append(metrics)

        # Maintain rolling window
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)

        # Update performance stats
        self.performance_stats['execution_times'].append(metrics.execution_time)
        self.performance_stats['confidence_scores'].append(metrics.confidence)

        # Track errors
        if not metrics.success:
            self.error_counts[metrics.error or 'unknown'] += 1

        # Log the query
        log_data = {
            "query_length": len(metrics.query),
            "response_length": len(metrics.response),
            "confidence": metrics.confidence,
            "execution_time": metrics.execution_time,
            "success": metrics.success,
            "retriever_type": metrics.retriever_type,
            "llm_provider": metrics.llm_provider
        }

        if metrics.error:
            log_data["error"] = metrics.error

        logger.info("RAG query recorded", **log_data)

    def get_performance_stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance statistics for the specified time window"""

        # Filter metrics by time window
        cutoff_time = datetime.utcnow().timestamp() - (window_minutes * 60)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp and m.timestamp.timestamp() > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No metrics available for the specified time window"}

        # Calculate statistics
        execution_times = [m.execution_time for m in recent_metrics]
        confidence_scores = [m.confidence for m in recent_metrics]
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)

        return {
            "total_queries": len(recent_metrics),
            "success_rate": success_rate,
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "avg_confidence": sum(confidence_scores) / len(confidence_scores),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "min_confidence": min(confidence_scores),
            "max_confidence": max(confidence_scores),
            "time_window_minutes": window_minutes,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors"""
        total_errors = sum(self.error_counts.values())
        total_queries = len(self.metrics_history)

        return {
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_queries, 1),
            "error_types": dict(self.error_counts),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent queries with metrics"""
        recent = self.metrics_history[-limit:] if limit > 0 else self.metrics_history

        return [
            {
                "query": m.query[:100] + "..." if len(m.query) > 100 else m.query,
                "confidence": m.confidence,
                "execution_time": m.execution_time,
                "success": m.success,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                "retriever_type": m.retriever_type,
                "llm_provider": m.llm_provider
            }
            for m in recent
        ]

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of RAG system"""

        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics available"}

        recent_stats = self.get_performance_stats(window_minutes=5)

        # Determine health based on metrics
        success_rate = recent_stats.get("success_rate", 0)
        avg_execution_time = recent_stats.get("avg_execution_time", float('inf'))
        avg_confidence = recent_stats.get("avg_confidence", 0)

        if success_rate >= 0.95 and avg_execution_time <= 3.0 and avg_confidence >= 0.7:
            status = "healthy"
        elif success_rate >= 0.85 and avg_execution_time <= 5.0:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "avg_confidence": avg_confidence,
            "total_queries": len(self.metrics_history),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global monitor instance
_rag_monitor = None


def get_rag_monitor() -> RAGMonitor:
    """Get the global RAG monitor instance"""
    global _rag_monitor
    if _rag_monitor is None:
        _rag_monitor = RAGMonitor()
    return _rag_monitor


async def record_rag_query(
    query: str,
    response: str,
    confidence: float,
    execution_time: float,
    success: bool,
    error: Optional[str] = None,
    retriever_type: str = "unknown",
    num_docs_retrieved: int = 0,
    llm_provider: str = "unknown"
) -> None:
    """Record a RAG query with metrics"""

    metrics = RAGQueryMetrics(
        query=query,
        response=response,
        confidence=confidence,
        execution_time=execution_time,
        success=success,
        error=error,
        retriever_type=retriever_type,
        num_docs_retrieved=num_docs_retrieved,
        llm_provider=llm_provider
    )

    monitor = get_rag_monitor()
    await monitor.record_query(metrics)


def get_rag_performance_stats(window_minutes: int = 60) -> Dict[str, Any]:
    """Get RAG performance statistics"""
    monitor = get_rag_monitor()
    return monitor.get_performance_stats(window_minutes)


def get_rag_error_summary() -> Dict[str, Any]:
    """Get RAG error summary"""
    monitor = get_rag_monitor()
    return monitor.get_error_summary()


def get_recent_rag_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent RAG queries"""
    monitor = get_rag_monitor()
    return monitor.get_recent_queries(limit)


def get_rag_health_status() -> Dict[str, Any]:
    """Get RAG system health status"""
    monitor = get_rag_monitor()
    return monitor.get_health_status()
