"""
MCP Monitoring and Observability for AI Marketing Agents
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class MCPMonitor:
    """Monitor MCP operations and agent interactions"""

    def __init__(self):
        self.metrics = {
            "tool_calls": defaultdict(int),
            "tool_call_duration": defaultdict(list),
            "tool_call_errors": defaultdict(int),
            "agent_interactions": defaultdict(int),
            "message_routing": defaultdict(int),
            "discovery_requests": defaultdict(int)
        }
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def record_tool_call_start(self, call_id: str, tool_name: str, from_agent: str, to_agent: str):
        """Record the start of a tool call"""
        async with self._lock:
            self.active_calls[call_id] = {
                "tool_name": tool_name,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "start_time": time.time(),
                "status": "active"
            }

        logger.info(f"Tool call started: {tool_name} from {from_agent} to {to_agent}")

    async def record_tool_call_end(self, call_id: str, success: bool, error: Optional[str] = None):
        """Record the end of a tool call"""
        async with self._lock:
            if call_id in self.active_calls:
                call_info = self.active_calls[call_id]
                duration = time.time() - call_info["start_time"]

                # Update metrics
                tool_name = call_info["tool_name"]
                from_agent = call_info["from_agent"]
                to_agent = call_info["to_agent"]

                self.metrics["tool_calls"][tool_name] += 1
                self.metrics["tool_call_duration"][tool_name].append(duration)
                self.metrics["agent_interactions"][f"{from_agent}->{to_agent}"] += 1

                if not success:
                    self.metrics["tool_call_errors"][tool_name] += 1

                # Clean up
                call_info.update({
                    "end_time": time.time(),
                    "duration": duration,
                    "success": success,
                    "error": error,
                    "status": "completed"
                })

                logger.info(
                    f"Tool call completed: {tool_name} "
                    f"({'success' if success else 'failed'}) "
                    f"in {duration:.2f}s"
                )
            else:
                logger.warning(f"Unknown tool call ended: {call_id}")

    async def record_message_routed(self, message_type: str, sender: str, receiver: str):
        """Record message routing"""
        async with self._lock:
            self.metrics["message_routing"][message_type] += 1

        logger.debug(f"Message routed: {message_type} from {sender} to {receiver}")

    async def record_discovery_request(self, requester: str, agent_filter: Optional[str] = None):
        """Record tool discovery requests"""
        async with self._lock:
            key = f"{requester}->{agent_filter}" if agent_filter else f"{requester}->all"
            self.metrics["discovery_requests"][key] += 1

        logger.info(f"Discovery request: {requester} -> {agent_filter or 'all'}")

    def get_tool_call_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get tool call statistics"""
        if tool_name:
            durations = self.metrics["tool_call_duration"].get(tool_name, [])
            return {
                "tool_name": tool_name,
                "total_calls": self.metrics["tool_calls"].get(tool_name, 0),
                "error_count": self.metrics["tool_call_errors"].get(tool_name, 0),
                "success_rate": self._calculate_success_rate(tool_name),
                "avg_duration": sum(durations) / len(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0
            }
        else:
            # Return stats for all tools
            all_stats = {}
            for tool in self.metrics["tool_calls"].keys():
                all_stats[tool] = self.get_tool_call_stats(tool)
            return all_stats

    def get_agent_interaction_stats(self) -> Dict[str, Any]:
        """Get agent interaction statistics"""
        return dict(self.metrics["agent_interactions"])

    def get_message_routing_stats(self) -> Dict[str, Any]:
        """Get message routing statistics"""
        return dict(self.metrics["message_routing"])

    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery request statistics"""
        return dict(self.metrics["discovery_requests"])

    def _calculate_success_rate(self, tool_name: str) -> float:
        """Calculate success rate for a tool"""
        total_calls = self.metrics["tool_calls"].get(tool_name, 0)
        error_count = self.metrics["tool_call_errors"].get(tool_name, 0)

        if total_calls == 0:
            return 0.0

        return ((total_calls - error_count) / total_calls) * 100

    async def get_overall_stats(self) -> Dict[str, Any]:
        """Get comprehensive MCP statistics"""
        async with self._lock:
            total_tool_calls = sum(self.metrics["tool_calls"].values())
            total_errors = sum(self.metrics["tool_call_errors"].values())
            total_messages = sum(self.metrics["message_routing"].values())
            total_discoveries = sum(self.metrics["discovery_requests"].values())

            # Calculate average durations
            all_durations = []
            for durations in self.metrics["tool_call_duration"].values():
                all_durations.extend(durations)
            avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "total_tool_calls": total_tool_calls,
                    "total_errors": total_errors,
                    "total_messages": total_messages,
                    "total_discoveries": total_discoveries,
                    "overall_success_rate": ((total_tool_calls - total_errors) / total_tool_calls * 100) if total_tool_calls > 0 else 0,
                    "average_call_duration": avg_duration
                },
                "active_calls": len([c for c in self.active_calls.values() if c["status"] == "active"]),
                "tools": self.get_tool_call_stats(),
                "agent_interactions": self.get_agent_interaction_stats(),
                "message_routing": self.get_message_routing_stats(),
                "discovery_requests": self.get_discovery_stats()
            }

    async def reset_stats(self):
        """Reset all monitoring statistics"""
        async with self._lock:
            self.metrics = {
                "tool_calls": defaultdict(int),
                "tool_call_duration": defaultdict(list),
                "tool_call_errors": defaultdict(int),
                "agent_interactions": defaultdict(int),
                "message_routing": defaultdict(int),
                "discovery_requests": defaultdict(int)
            }
            self.active_calls.clear()

        logger.info("MCP monitoring statistics reset")

    async def export_stats(self, format: str = "json") -> str:
        """Export statistics in specified format"""
        stats = await self.get_overall_stats()

        if format == "json":
            import json
            return json.dumps(stats, indent=2, default=str)
        elif format == "csv":
            # Simple CSV export for tool stats
            lines = ["tool_name,total_calls,error_count,success_rate,avg_duration"]
            for tool_name, tool_stats in stats["tools"].items():
                lines.append(",".join([
                    tool_name,
                    str(tool_stats["total_calls"]),
                    str(tool_stats["error_count"]),
                    ".2f",
                    ".2f"
                ]))
            return "\n".join(lines)
        else:
            return str(stats)


# Global monitor instance
_monitor = None


async def get_mcp_monitor() -> MCPMonitor:
    """Get the global MCP monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = MCPMonitor()
    return _monitor


# Convenience functions for monitoring
async def monitor_tool_call_start(call_id: str, tool_name: str, from_agent: str, to_agent: str):
    """Monitor the start of a tool call"""
    monitor = await get_mcp_monitor()
    await monitor.record_tool_call_start(call_id, tool_name, from_agent, to_agent)


async def monitor_tool_call_end(call_id: str, success: bool, error: Optional[str] = None):
    """Monitor the end of a tool call"""
    monitor = await get_mcp_monitor()
    await monitor.record_tool_call_end(call_id, success, error)


async def monitor_message_routed(message_type: str, sender: str, receiver: str):
    """Monitor message routing"""
    monitor = await get_mcp_monitor()
    await monitor.record_message_routed(message_type, sender, receiver)


async def monitor_discovery_request(requester: str, agent_filter: Optional[str] = None):
    """Monitor discovery requests"""
    monitor = await get_mcp_monitor()
    await monitor.record_discovery_request(requester, agent_filter)


async def get_mcp_stats() -> Dict[str, Any]:
    """Get comprehensive MCP statistics"""
    monitor = await get_mcp_monitor()
    return await monitor.get_overall_stats()


async def reset_mcp_stats():
    """Reset MCP monitoring statistics"""
    monitor = await get_mcp_monitor()
    await monitor.reset_stats()
