import time
"""
Base agent class for all marketing AI agents using LangChain and LangGraph
"""

import asyncio
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

# Simplified agents without langchain dependencies for deployment
from app.core.config import get_settings
from app.agents.state import MarketingAgentState, update_state_timestamp
from app.mcp.tools import MCPTool
from app.mcp.server import AgentMCPServer
from app.mcp.client import AgentMCPClient
# from app.core.monitoring import record_agent_execution  # TODO: Implement monitoring

settings = get_settings()

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all marketing AI agents using LangChain and LangGraph"""

    def __init__(
        self,
        name: str,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[Tool]] = None,
        memory=None
    ):
        self.name = name
        self.llm = llm or ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
            openai_api_key=settings.llm.openai_api_key
        )
        self.tools = tools or []
        self.memory = memory  # Simplified for now

        # Create agent using Runnable interface
        self.agent = self.create_agent()

        # Initialize MCP capabilities
        self.mcp_server = AgentMCPServer(self.name, self)
        self.mcp_client = AgentMCPClient(self.name)

        logger.info(f"Initialized agent: {self.name} with MCP capabilities")

    async def execute(self, state: MarketingAgentState) -> MarketingAgentState:
        """Execute agent task with state management"""
        start_time = time.time()

        try:
            # Build input from state
            input_data = self.build_input(state)

            # Execute agent
            result = await self.agent.ainvoke(input_data)

            # Update state
            updated_state = self.update_state(state, result)

            # Record successful execution
            execution_time = time.time() - start_time
            # await record_agent_execution(
            #     agent_name=self.name,
            #     execution_time=execution_time,
            #     success=True,
            #     metadata={"state_keys": list(updated_state.keys())}
            # )

            return updated_state

        except Exception as e:
            # Record failed execution
            execution_time = time.time() - start_time
            # await record_agent_execution(
            #     agent_name=self.name,
            #     execution_time=execution_time,
            #     success=False,
            #     error=str(e)
            # )

            logger.error(f"Agent {self.name} execution failed: {e}")
            return self.handle_error(state, e)

    @abstractmethod
    def get_system_prompt(self) -> ChatPromptTemplate:
        """Get agent-specific system prompt"""
        pass

    @abstractmethod
    def create_agent(self) -> Runnable:
        """Create the agent using Runnable interface"""
        pass

    @abstractmethod
    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input data from shared state"""
        pass

    @abstractmethod
    def update_state(self, state: MarketingAgentState, result) -> MarketingAgentState:
        """Update shared state with agent results"""
        pass

    def handle_error(self, state: MarketingAgentState, error: Exception) -> MarketingAgentState:
        """Handle agent execution errors"""
        state["errors"] = state.get("errors", [])
        state["errors"].append({
            "agent": self.name,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        })
        return update_state_timestamp(state)

    def log_agent_activity(self, activity: str, details: Optional[Dict[str, Any]] = None):
        """Log agent activity for monitoring"""
        log_data = {
            "agent": self.name,
            "activity": activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        if details:
            log_data.update(details)

        logger.info(f"Agent activity: {activity}", **log_data)

    def validate_state(self, state: MarketingAgentState) -> bool:
        """Validate that state has required fields for this agent"""
        required_fields = ["campaign_config", "current_agent"]
        return all(field in state for field in required_fields)

    async def pre_execute_hook(self, state: MarketingAgentState) -> MarketingAgentState:
        """Hook called before agent execution"""
        self.log_agent_activity("pre_execute", {"state_keys": list(state.keys())})
        return state

    async def post_execute_hook(self, state: MarketingAgentState) -> MarketingAgentState:
        """Hook called after agent execution"""
        self.log_agent_activity("post_execute", {"state_keys": list(state.keys())})
        return state

    # MCP-related methods
    async def expose_capabilities(self) -> int:
        """Expose agent capabilities as MCP tools"""
        capabilities = self._get_agent_capabilities()
        registered_count = await self.mcp_server.register_tools(capabilities)
        logger.info(f"Agent {self.name} exposed {registered_count} capabilities via MCP")
        return registered_count

    def _get_agent_capabilities(self) -> List[MCPTool]:
        """Get agent capabilities as MCP tools"""
        return [
            MCPTool(
                name=f"{self.name}_execute",
                description=f"Execute {self.name} agent with campaign state",
                parameters={
                    "type": "object",
                    "properties": {
                        "campaign_config": {"type": "object"},
                        "target_audience": {"type": "object"},
                        "current_state": {"type": "object"}
                    },
                    "required": ["campaign_config"]
                },
                handler=self._mcp_execute_handler,
                agent_name=self.name
            ),
            MCPTool(
                name=f"{self.name}_status",
                description=f"Get {self.name} agent status and capabilities",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._mcp_status_handler,
                agent_name=self.name
            ),
            MCPTool(
                name=f"{self.name}_results",
                description=f"Get {self.name} agent execution results",
                parameters={
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"}
                    },
                    "required": []
                },
                handler=self._mcp_results_handler,
                agent_name=self.name
            )
        ]

    async def _mcp_execute_handler(self, **kwargs) -> Dict[str, Any]:
        """MCP handler for agent execution"""
        try:
            # Create a basic state from parameters
            campaign_config = kwargs.get("campaign_config", {})
            target_audience = kwargs.get("target_audience", {})
            current_state = kwargs.get("current_state", {})

            # Merge into a state object
            state = MarketingAgentState(
                campaign_config=campaign_config,
                target_audience=target_audience,
                current_agent=self.name,
                **current_state
            )

            # Execute the agent
            result_state = await self.execute(state)

            return {
                "success": True,
                "result": dict(result_state),
                "agent": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }

    async def _mcp_status_handler(self, **kwargs) -> Dict[str, Any]:
        """MCP handler for agent status"""
        return {
            "agent_name": self.name,
            "status": "active",
            "capabilities": [tool.name for tool in self._get_agent_capabilities()],
            "tools_count": len(self.tools),
            "mcp_enabled": True
        }

    async def _mcp_results_handler(self, **kwargs) -> Dict[str, Any]:
        """MCP handler for agent results"""
        campaign_id = kwargs.get("campaign_id")
        # In a real implementation, this would query results by campaign_id
        return {
            "agent_name": self.name,
            "campaign_id": campaign_id,
            "results_available": False,
            "message": "Results query not implemented yet"
        }

    async def call_agent_tool(self, target_agent: str, tool_name: str, **kwargs) -> Any:
        """Call a tool from another agent via MCP"""
        return await self.mcp_client.call_agent_tool(target_agent, tool_name, **kwargs)

    async def discover_agent_tools(self, agent_name: str) -> List[MCPTool]:
        """Discover tools available from another agent"""
        return await self.mcp_client.get_agent_tools(agent_name)
