import time
"""
Marketing Agent Orchestrator - LangGraph-based multi-agent workflow coordination
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from langgraph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.agents.state import MarketingAgentState, create_initial_state
from app.agents.lead_generation import LeadGenerationAgent
from app.agents.content_creator import ContentCreatorAgent
from app.agents.ad_manager import AdManagerAgent
from app.agents.monitoring import get_agent_monitor
from app.config import settings

logger = logging.getLogger(__name__)


class MarketingAgentGraph:
    """LangGraph-based multi-agent orchestration for marketing campaigns"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
            openai_api_key=settings.llm.openai_api_key
        )

        # Initialize specialized agents
        self.agents = {
            'lead_gen': LeadGenerationAgent(self.llm),
            'content_creator': ContentCreatorAgent(self.llm),
            'ad_manager': AdManagerAgent(self.llm),
        }

        # Initialize monitoring
        self.monitor = get_agent_monitor()

        # Build the workflow graph
        self.graph = self.build_graph()

        logger.info("Marketing Agent Graph initialized")

    def build_graph(self) -> StateGraph:
        """Build the multi-agent workflow graph"""

        workflow = StateGraph(MarketingAgentState)

        # Add agent nodes
        workflow.add_node("lead_generation", self.agents['lead_gen'].execute)
        workflow.add_node("content_creation", self.agents['content_creator'].execute)
        workflow.add_node("ad_management", self.agents['ad_manager'].execute)

        # Define workflow edges
        workflow.set_entry_point("lead_generation")

        # Conditional routing based on campaign type and results
        workflow.add_conditional_edges(
            "lead_generation",
            self.route_after_lead_gen,
            {
                "content_creation": "content_creation",
                "ad_management": "ad_management",
                "end": END
            }
        )

        workflow.add_edge("content_creation", "ad_management")
        workflow.add_edge("ad_management", END)  # End after ad management

        # Optional: Add analytics loop for optimization (commented out for simplicity)
        # workflow.add_conditional_edges(
        #     "ad_management",
        #     self.should_optimize,
        #     {
        #         "content_creation": "content_creation",  # Loop back for optimization
        #         "end": END
        #     }
        # )

        return workflow.compile()

    def route_after_lead_gen(self, state: MarketingAgentState) -> str:
        """Decide next step after lead generation"""
        leads = state.get('qualified_leads', [])
        campaign_config = state.get('campaign_config', {})

        # If we have qualified leads and need content
        if leads and campaign_config.get('content_required', True):
            return "content_creation"

        # If we have leads and ad platforms specified
        if leads and campaign_config.get('ad_platforms'):
            return "ad_management"

        # If no qualified leads, end the workflow
        if not leads:
            return "end"

        # Default to content creation if we have leads
        return "content_creation"

    def should_optimize(self, state: MarketingAgentState) -> str:
        """Decide if campaign needs optimization"""
        performance = state.get('campaign_performance', {})
        optimization_attempts = state.get('optimization_attempts', 0)

        # Check if performance is below threshold and we haven't optimized too many times
        if (performance.get('overall_score', 0) < 0.7 and
            optimization_attempts < 3):
            return "content_creation"

        return "end"

    async def run_campaign(self, campaign_config: Dict[str, Any]) -> MarketingAgentState:
        """Execute complete marketing campaign workflow"""

        # Initialize state
        initial_state = create_initial_state(campaign_config)

        # Add campaign ID
        initial_state["campaign_id"] = str(uuid.uuid4())

        logger.info(
            "Starting marketing campaign",
            campaign_id=initial_state["campaign_id"],
            config=campaign_config
        )

        campaign_start_time = time.time()

        try:
            # Execute workflow
            final_state = await self.graph.ainvoke(initial_state)

            # Record campaign execution in monitoring
            campaign_execution_time = time.time() - campaign_start_time
            await self.monitor.create_campaign_trace(
                campaign_id=final_state.get("campaign_id"),
                campaign_config=campaign_config,
                final_state=final_state
            )

            # Log completion
            logger.info(
                "Marketing campaign completed",
                campaign_id=final_state.get("campaign_id"),
                qualified_leads=len(final_state.get("qualified_leads", [])),
                content_created=len(final_state.get("generated_content", [])),
                errors=len(final_state.get("errors", [])),
                execution_time=campaign_execution_time
            )

            return final_state

        except Exception as e:
            logger.error(f"Campaign execution failed: {e}", campaign_id=initial_state["campaign_id"])
            # Return state with error
            initial_state["errors"] = initial_state.get("errors", [])
            initial_state["errors"].append({
                "agent": "orchestrator",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            return initial_state

    async def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running campaign"""
        # In a production system, this would query a database or cache
        # For now, return None as we don't have persistent state
        return None

    def get_available_agents(self) -> Dict[str, str]:
        """Get information about available agents"""
        return {
            "lead_generation": "Discovers and qualifies potential leads",
            "content_creator": "Generates marketing content with RAG enhancement",
            "ad_manager": "Manages multi-platform ad campaigns"
        }

    def validate_campaign_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate campaign configuration"""
        errors = []
        warnings = []

        # Required fields
        required_fields = ['name', 'target_audience']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate target audience
        audience = config.get('target_audience', {})
        if not audience:
            errors.append("target_audience cannot be empty")
        elif not isinstance(audience, dict):
            errors.append("target_audience must be a dictionary")

        # Validate budget if specified
        budget = config.get('budget')
        if budget is not None:
            if not isinstance(budget, (int, float)) or budget <= 0:
                errors.append("budget must be a positive number")

        # Validate platforms
        platforms = config.get('ad_platforms', [])
        valid_platforms = ['google_ads', 'linkedin', 'facebook']
        for platform in platforms:
            if platform not in valid_platforms:
                warnings.append(f"Unknown platform: {platform}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> MarketingAgentGraph:
    """Get the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MarketingAgentGraph()
    return _orchestrator


async def run_marketing_campaign(campaign_config: Dict[str, Any]) -> MarketingAgentState:
    """Convenience function to run a marketing campaign"""
    orchestrator = get_orchestrator()
    return await orchestrator.run_campaign(campaign_config)