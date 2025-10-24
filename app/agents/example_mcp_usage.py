"""
Example usage of MCP (Model Context Protocol) in AI Marketing Agents
Demonstrates agent-to-agent tool sharing and communication
"""

import asyncio
import logging
from typing import Dict, Any

from app.agents.lead_generation import LeadGenerationAgent
from app.agents.content_creator import ContentCreatorAgent
from app.agents.ad_manager import AdManagerAgent
from app.agents.communication import call_agent_tool_via_mcp, discover_agent_tools_via_mcp, broadcast_agent_capabilities
from app.agents.state import create_initial_state
from app.config import settings
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


async def example_mcp_agent_interaction():
    """Example of MCP-based agent-to-agent interaction"""

    print("🤖 MCP Agent-to-Agent Interaction Demo")
    print("=" * 50)

    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
        openai_api_key=settings.llm.openai_api_key
    )

    # Initialize agents with MCP capabilities
    lead_agent = LeadGenerationAgent(llm)
    content_agent = ContentCreatorAgent(llm)
    ad_agent = AdManagerAgent(llm)

    print("✅ Agents initialized with MCP capabilities")

    # Step 1: Agents expose their capabilities via MCP
    print("\n📤 Agents exposing MCP capabilities...")

    await lead_agent.expose_capabilities()
    await content_agent.expose_capabilities()
    await ad_agent.expose_capabilities()

    # Broadcast capabilities to the network
    await broadcast_agent_capabilities("lead_generation", ["find_leads", "qualify_leads"])
    await broadcast_agent_capabilities("content_creator", ["generate_content", "optimize_seo"])
    await broadcast_agent_capabilities("ad_manager", ["create_campaign", "analyze_performance"])

    print("✅ Agent capabilities broadcast via MCP")

    # Step 2: Content creator discovers lead generation tools
    print("\n🔍 Content creator discovering lead generation tools...")

    tools = await discover_agent_tools_via_mcp("content_creator", "lead_generation")
    print(f"📋 Discovered tools from lead_generation: {len(tools.get('tools', []))} tools")

    for tool in tools.get('tools', []):
        print(f"  - {tool['name']}: {tool['description']}")

    # Step 3: Content creator calls lead generation tool via MCP
    print("\n🔄 Content creator calling lead generation tool via MCP...")

    # Create a campaign state for context
    campaign_config = {
        "name": "MCP Demo Campaign",
        "target_audience": {
            "industry": "technology",
            "company_size": "50-200",
            "job_titles": ["CTO", "VP Engineering"]
        }
    }

    result = await call_agent_tool_via_mcp(
        from_agent="content_creator",
        to_agent="lead_generation",
        tool_name="lead_generation_execute",
        campaign_config=campaign_config,
        target_audience=campaign_config["target_audience"],
        current_state={"current_agent": "content_creator"}
    )

    if result["success"]:
        print("✅ Successfully called lead generation tool via MCP")
        print(f"📊 Result: {result['result']}")
    else:
        print(f"❌ Tool call failed: {result['error']}")

    # Step 4: Ad manager discovers content creation tools
    print("\n🎨 Ad manager discovering content creation tools...")

    content_tools = await discover_agent_tools_via_mcp("ad_manager", "content_creator")
    print(f"📋 Discovered tools from content_creator: {len(content_tools.get('tools', []))} tools")

    # Step 5: Ad manager calls content creation tool
    print("\n✍️ Ad manager calling content creation tool via MCP...")

    content_result = await call_agent_tool_via_mcp(
        from_agent="ad_manager",
        to_agent="content_creator",
        tool_name="content_creator_execute",
        campaign_config=campaign_config,
        content_requirements={
            "type": "ad_copy",
            "topic": "AI Marketing Solutions",
            "tone": "professional"
        },
        target_audience=campaign_config["target_audience"],
        current_state={"current_agent": "ad_manager"}
    )

    if content_result["success"]:
        print("✅ Successfully called content creation tool via MCP")
        print(f"📝 Generated content: {content_result['result']}")
    else:
        print(f"❌ Content generation failed: {content_result['error']}")

    # Step 6: Demonstrate cross-agent tool discovery
    print("\n🌐 Demonstrating cross-agent tool discovery...")

    all_tools = await discover_agent_tools_via_mcp("orchestrator")
    print(f"📊 Total tools discovered across all agents: {len(all_tools.get('tools', []))}")

    # Group tools by agent
    agent_tools = {}
    for tool in all_tools.get('tools', []):
        agent = tool['agent_name']
        if agent not in agent_tools:
            agent_tools[agent] = []
        agent_tools[agent].append(tool['name'])

    for agent, tools_list in agent_tools.items():
        print(f"  🤖 {agent}: {len(tools_list)} tools - {', '.join(tools_list)}")

    print("\n🎉 MCP Agent-to-Agent Interaction Demo Complete!")
    print("\nKey Achievements:")
    print("• ✅ Agents can discover each other's tools")
    print("• ✅ Agents can call tools across boundaries")
    print("• ✅ Standardized communication via MCP")
    print("• ✅ Tool registration and discovery system")
    print("• ✅ Error handling and result propagation")


async def example_mcp_error_handling():
    """Example of MCP error handling and resilience"""

    print("\n🛡️ MCP Error Handling Demo")
    print("=" * 30)

    # Try calling a non-existent tool
    print("Testing error handling with non-existent tool...")

    result = await call_agent_tool_via_mcp(
        from_agent="test_agent",
        to_agent="non_existent_agent",
        tool_name="fake_tool",
        test_param="value"
    )

    if not result["success"]:
        print(f"✅ Error handled gracefully: {result['error']}")
    else:
        print("❌ Expected error but got success")

    # Try calling with invalid parameters
    print("\nTesting error handling with invalid parameters...")

    result = await call_agent_tool_via_mcp(
        from_agent="test_agent",
        to_agent="lead_generation",
        tool_name="lead_generation_execute"
        # Missing required parameters
    )

    if not result["success"]:
        print(f"✅ Parameter validation error handled: {result['error']}")
    else:
        print("❌ Expected parameter error but got success")

    print("✅ MCP error handling working correctly")


async def main():
    """Main demo function"""

    print("🚀 AI Marketing Agents - MCP Integration Demo")
    print("=" * 60)

    try:
        # Run the main MCP interaction demo
        await example_mcp_agent_interaction()

        # Run error handling demo
        await example_mcp_error_handling()

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

    print("\n🎯 MCP Integration Summary:")
    print("• Standardized agent-to-agent communication")
    print("• Tool discovery and registration system")
    print("• Cross-agent tool calling capabilities")
    print("• Error handling and resilience patterns")
    print("• Foundation for external service integrations")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run the demo
    asyncio.run(main())