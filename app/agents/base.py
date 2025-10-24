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

from langchain_core.runnables import Runnable
# Simplified memory for now - will implement proper memory later
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from app.agents.state import MarketingAgentState, update_state_timestamp
from app.agents.monitoring import record_agent_execution
from app.config import settings

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

        logger.info(f"Initialized agent: {self.name}")

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
            await record_agent_execution(
                agent_name=self.name,
                execution_time=execution_time,
                success=True,
                metadata={"state_keys": list(updated_state.keys())}
            )

            return updated_state

        except Exception as e:
            # Record failed execution
            execution_time = time.time() - start_time
            await record_agent_execution(
                agent_name=self.name,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )

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