"""
Agent API endpoints for testing and interacting with marketing agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from app.agents.orchestrator import run_marketing_campaign, get_orchestrator
from app.agents.monitoring import get_agent_monitor, get_all_agent_metrics
from app.agents.communication import get_communicator, AgentMessage
from app.agents.resilience import get_resilience_manager, get_agent_health
from app.agents.state import create_initial_state
from app.core.auth import get_api_key

router = APIRouter()


# Pydantic models for API requests/responses
class CampaignConfig(BaseModel):
    """Campaign configuration model"""
    name: str = Field(..., description="Campaign name")
    target_audience: Dict[str, Any] = Field(..., description="Target audience criteria")
    content_required: bool = Field(True, description="Whether content creation is needed")
    content_requirements: Optional[Dict[str, Any]] = Field(None, description="Content requirements")
    ad_platforms: List[str] = Field(default_factory=list, description="Ad platforms to use")
    budget: Optional[float] = Field(None, description="Campaign budget")
    brand_guidelines: Optional[Dict[str, Any]] = Field(None, description="Brand guidelines")


class CampaignResponse(BaseModel):
    """Campaign execution response"""
    campaign_id: str
    status: str
    qualified_leads: int
    content_created: int
    ad_campaigns: int
    performance_score: Optional[float]
    errors: List[Dict[str, Any]]
    execution_time: Optional[float]


class AgentMetrics(BaseModel):
    """Agent metrics response"""
    agent_name: str
    total_calls: int
    success_rate: float
    error_count: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float


class HealthResponse(BaseModel):
    """System health response"""
    status: str
    timestamp: str
    agents: Dict[str, Dict[str, Any]]
    langsmith_enabled: bool
    overall_health: str


class MessageRequest(BaseModel):
    """Inter-agent message request"""
    sender: str
    receiver: str
    message_type: str
    payload: Dict[str, Any]


@router.post("/campaigns/run", response_model=CampaignResponse)
async def run_campaign(
    config: CampaignConfig,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Execute a complete marketing campaign"""
    try:
        # Convert config to dict
        campaign_config = config.dict()

        # Run campaign (this will be async in background for long-running campaigns)
        start_time = datetime.utcnow()

        # For immediate response, run synchronously
        # In production, you'd want to run this in background for long campaigns
        final_state = await run_marketing_campaign(campaign_config)

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return CampaignResponse(
            campaign_id=final_state.get("campaign_id", "unknown"),
            status="completed",
            qualified_leads=len(final_state.get("qualified_leads", [])),
            content_created=len(final_state.get("generated_content", [])),
            ad_campaigns=len(final_state.get("ad_creatives", [])),
            performance_score=final_state.get("campaign_performance", {}).get("overall_score"),
            errors=final_state.get("errors", []),
            execution_time=execution_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign execution failed: {str(e)}")


@router.post("/campaigns/validate")
async def validate_campaign_config(
    config: CampaignConfig,
    api_key: str = Depends(get_api_key)
):
    """Validate campaign configuration"""
    orchestrator = get_orchestrator()
    result = orchestrator.validate_campaign_config(config.dict())
    return result


@router.get("/agents", response_model=Dict[str, str])
async def get_available_agents(api_key: str = Depends(get_api_key)):
    """Get information about available agents"""
    orchestrator = get_orchestrator()
    return orchestrator.get_available_agents()


@router.get("/agents/{agent_name}/metrics", response_model=AgentMetrics)
async def get_agent_metrics(
    agent_name: str,
    api_key: str = Depends(get_api_key)
):
    """Get metrics for a specific agent"""
    monitor = get_agent_monitor()
    metrics = monitor.get_agent_metrics(agent_name)

    if "error" in metrics:
        raise HTTPException(status_code=404, detail=metrics["error"])

    return AgentMetrics(**metrics)


@router.get("/agents/metrics", response_model=Dict[str, Any])
async def get_all_agents_metrics(api_key: str = Depends(get_api_key)):
    """Get metrics for all agents"""
    return get_all_agent_metrics()


@router.get("/health", response_model=HealthResponse)
async def get_system_health(api_key: str = Depends(get_api_key)):
    """Get system health status"""
    try:
        # Get agent health
        agent_health = await get_agent_health()

        # Get monitoring status
        monitor = get_agent_monitor()
        metrics = monitor.get_all_metrics()

        return HealthResponse(
            status="healthy" if agent_health.get("overall_health") == "healthy" else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            agents=agent_health.get("agents", {}),
            langsmith_enabled=metrics.get("langsmith_enabled", False),
            overall_health=agent_health.get("overall_health", "unknown")
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            agents={},
            langsmith_enabled=False,
            overall_health="error"
        )


@router.post("/messages/send")
async def send_agent_message(
    message: MessageRequest,
    api_key: str = Depends(get_api_key)
):
    """Send a message between agents"""
    try:
        communicator = get_communicator()
        agent_message = AgentMessage(
            sender=message.sender,
            receiver=message.receiver,
            message_type=message.message_type,
            payload=message.payload
        )

        await communicator.send_message(agent_message)
        return {"status": "sent", "correlation_id": agent_message.correlation_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/messages/{agent_name}")
async def get_agent_messages(
    agent_name: str,
    api_key: str = Depends(get_api_key)
):
    """Get messages for a specific agent"""
    try:
        communicator = get_communicator()
        messages = await communicator.receive_messages(agent_name)

        return {
            "agent": agent_name,
            "message_count": len(messages),
            "messages": [
                {
                    "sender": msg.sender,
                    "message_type": msg.message_type,
                    "payload": msg.payload,
                    "timestamp": msg.timestamp,
                    "correlation_id": msg.correlation_id
                }
                for msg in messages
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.post("/agents/{agent_name}/reset")
async def reset_agent(
    agent_name: str,
    api_key: str = Depends(get_api_key)
):
    """Reset circuit breaker for an agent"""
    try:
        resilience_manager = get_resilience_manager()
        resilience_manager.reset_agent(agent_name)
        return {"status": "reset", "agent": agent_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset agent: {str(e)}")


@router.get("/test/lead-generation")
async def test_lead_generation(api_key: str = Depends(get_api_key)):
    """Test lead generation agent with sample data"""
    try:
        from app.agents.lead_generation import LeadGenerationAgent
        from langchain_openai import ChatOpenAI
        from app.config import settings

        llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            openai_api_key=settings.llm.openai_api_key
        )

        agent = LeadGenerationAgent(llm)
        state = create_initial_state({
            "name": "Test Campaign",
            "target_audience": {"industry": "technology", "company_size": "50-200"}
        })

        result_state = await agent.execute(state)

        return {
            "status": "success",
            "leads_found": len(result_state.get("leads", [])),
            "qualified_leads": len(result_state.get("qualified_leads", [])),
            "sample_leads": result_state.get("qualified_leads", [])[:3]  # First 3 leads
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead generation test failed: {str(e)}")


@router.get("/test/content-creation")
async def test_content_creation(api_key: str = Depends(get_api_key)):
    """Test content creation agent with sample data"""
    try:
        from app.agents.content_creator import ContentCreatorAgent
        from langchain_openai import ChatOpenAI
        from app.config import settings

        llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            openai_api_key=settings.llm.openai_api_key
        )

        agent = ContentCreatorAgent(llm)
        state = create_initial_state({
            "name": "Test Campaign",
            "target_audience": {"industry": "technology"},
            "content_requirements": {
                "type": "blog_post",
                "topic": "AI Marketing Trends",
                "tone": "professional"
            }
        })

        result_state = await agent.execute(state)

        return {
            "status": "success",
            "content_created": len(result_state.get("generated_content", [])),
            "sample_content": result_state.get("generated_content", [])[:1],  # First content
            "performance_metrics": result_state.get("content_performance", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content creation test failed: {str(e)}")


@router.get("/test/ad-management")
async def test_ad_management(api_key: str = Depends(get_api_key)):
    """Test ad management agent with sample data"""
    try:
        from app.agents.ad_manager import AdManagerAgent
        from langchain_openai import ChatOpenAI
        from app.config import settings

        llm = ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            openai_api_key=settings.llm.openai_api_key
        )

        agent = AdManagerAgent(llm)
        state = create_initial_state({
            "name": "Test Campaign",
            "target_audience": {"industry": "technology"},
            "ad_platforms": ["google_ads"],
            "budget": 1000.0
        })

        # Add some mock qualified leads
        state["qualified_leads"] = [
            {"name": "John Doe", "company": "Tech Corp", "score": 0.85},
            {"name": "Jane Smith", "company": "Innovate Ltd", "score": 0.92}
        ]

        result_state = await agent.execute(state)

        return {
            "status": "success",
            "ad_creatives": len(result_state.get("ad_creatives", [])),
            "campaign_performance": result_state.get("campaign_performance", {}),
            "sample_creatives": result_state.get("ad_creatives", [])[:2]  # First 2 creatives
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ad management test failed: {str(e)}")


@router.get("/test/full-workflow")
async def test_full_workflow(api_key: str = Depends(get_api_key)):
    """Test the complete agent workflow"""
    try:
        campaign_config = {
            'name': 'API Test Campaign',
            'target_audience': {
                'industry': 'technology',
                'company_size': '50-200',
                'job_titles': ['CTO', 'VP Engineering']
            },
            'content_required': True,
            'content_requirements': {
                'type': 'blog_post',
                'topic': 'AI Marketing Strategies',
                'tone': 'professional'
            },
            'ad_platforms': ['google_ads'],
            'budget': 2000.0,
            'brand_guidelines': {
                'tone': 'professional',
                'prohibited_words': ['cheap']
            }
        }

        start_time = datetime.utcnow()
        final_state = await run_marketing_campaign(campaign_config)
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return {
            "status": "success",
            "campaign_id": final_state.get("campaign_id"),
            "execution_time": execution_time,
            "results": {
                "leads_found": len(final_state.get("leads", [])),
                "qualified_leads": len(final_state.get("qualified_leads", [])),
                "content_created": len(final_state.get("generated_content", [])),
                "ad_campaigns": len(final_state.get("ad_creatives", [])),
                "performance_score": final_state.get("campaign_performance", {}).get("overall_score"),
                "errors": len(final_state.get("errors", []))
            },
            "errors": final_state.get("errors", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full workflow test failed: {str(e)}")
