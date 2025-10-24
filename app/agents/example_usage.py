"""
Example usage of the Phase 3 Marketing Agent Architecture
This demonstrates how to use the implemented agent system
"""

import asyncio
import logging
from app.agents.orchestrator import run_marketing_campaign
from app.agents.communication import get_communicator, send_lead_notification
from app.agents.monitoring import get_agent_monitor, get_all_agent_metrics
from app.agents.resilience import get_agent_health
from app.agents.state import create_initial_state
from langchain_openai import ChatOpenAI
from app.config import settings


async def example_campaign_execution():
    """Example of running a complete marketing campaign"""

    # Define campaign configuration
    campaign_config = {
        'name': 'AI Marketing Campaign Example',
        'target_audience': {
            'industry': 'technology',
            'company_size': '50-200',
            'job_titles': ['CTO', 'VP Engineering']
        },
        'content_required': True,
        'content_requirements': {
            'type': 'blog_post',
            'topic': 'AI-Powered Marketing Strategies',
            'tone': 'professional'
        },
        'ad_platforms': ['google_ads', 'linkedin'],
        'budget': 2000.0,
        'brand_guidelines': {
            'tone': 'professional',
            'prohibited_words': ['cheap'],
            'required_elements': ['call-to-action']
        }
    }

    print("🚀 Starting Marketing Campaign...")
    print(f"Campaign: {campaign_config['name']}")
    print(f"Target: {campaign_config['target_audience']['industry']} companies")

    try:
        # Execute the campaign
        final_state = await run_marketing_campaign(campaign_config)

        # Display results
        print("\n📊 Campaign Results:")
        print(f"Campaign ID: {final_state.get('campaign_id')}")
        print(f"Leads Found: {len(final_state.get('leads', []))}")
        print(f"Qualified Leads: {len(final_state.get('qualified_leads', []))}")
        print(f"Content Generated: {len(final_state.get('generated_content', []))}")
        print(f"Ad Campaigns Created: {len(final_state.get('ad_creatives', []))}")

        if final_state.get('campaign_performance'):
            perf = final_state['campaign_performance']
            print(f"Overall Performance Score: {perf.get('overall_score', 0):.1f}")

        if final_state.get('errors'):
            print(f"\n⚠️ Errors Encountered: {len(final_state['errors'])}")
            for error in final_state['errors'][:3]:  # Show first 3 errors
                print(f"  - {error['agent']}: {error['error'][:100]}...")

        return final_state

    except Exception as e:
        print(f"❌ Campaign execution failed: {e}")
        return None


async def example_agent_communication():
    """Example of inter-agent communication"""

    communicator = get_communicator()

    print("\n📨 Testing Agent Communication...")

    # Simulate lead generation completion
    leads = [
        {
            'name': 'John Smith',
            'company': 'Tech Corp',
            'job_title': 'CTO',
            'score': 0.85
        },
        {
            'name': 'Jane Doe',
            'company': 'Innovate Ltd',
            'job_title': 'VP Engineering',
            'score': 0.92
        }
    ]

    # Send lead notification
    await send_lead_notification('lead_generation', leads)
    print(f"✅ Sent notification about {len(leads)} new leads")

    # Content creator receives the message
    messages = await communicator.receive_messages('content_creator')
    print(f"📬 Content creator received {len(messages)} messages")

    for msg in messages:
        print(f"  Message type: {msg.message_type}")
        print(f"  Payload: {len(msg.payload.get('leads', []))} leads")


async def example_resilience_monitoring():
    """Example of monitoring agent health and resilience"""

    print("\n🛡️ Checking Agent Health...")

    health_status = await get_agent_health()

    for agent, status in health_status.items():
        if agent == 'overall_health':
            continue
        state = status['circuit_breaker']
        failures = status['failures']
        healthy = status['healthy']

        status_icon = "✅" if healthy else "❌"
        print(f"{status_icon} {agent}: {state} (failures: {failures})")

    overall = health_status.get('overall_health', 'unknown')
    print(f"\nOverall System Health: {overall}")


async def example_individual_agent_usage():
    """Example of using individual agents directly"""

    from app.agents.lead_generation import LeadGenerationAgent
    from app.agents.content_creator import ContentCreatorAgent
    from app.agents.ad_manager import AdManagerAgent
    from app.agents.state import create_initial_state

    print("\n🤖 Testing Individual Agents...")

    # Initialize LLM (you would configure this with actual API keys)
    llm = ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
        openai_api_key=settings.llm.openai_api_key
    )

    # Test Lead Generation Agent
    print("🔍 Testing Lead Generation Agent...")
    try:
        lead_agent = LeadGenerationAgent(llm)
        state = create_initial_state({
            "name": "Test Campaign",
            "target_audience": {"industry": "technology", "company_size": "50-200"}
        })

        result_state = await lead_agent.execute(state)
        print(f"✅ Found {len(result_state.get('leads', []))} leads, qualified {len(result_state.get('qualified_leads', []))}")
    except Exception as e:
        print(f"❌ Lead generation failed: {e}")

    # Test Content Creator Agent
    print("\n✍️ Testing Content Creator Agent...")
    try:
        content_agent = ContentCreatorAgent(llm)
        state = create_initial_state({
            "name": "Test Campaign",
            "target_audience": {"industry": "technology"},
            "content_requirements": {
                "type": "blog_post",
                "topic": "AI Marketing Trends",
                "tone": "professional"
            }
        })

        result_state = await content_agent.execute(state)
        print(f"✅ Generated {len(result_state.get('generated_content', []))} content pieces")
    except Exception as e:
        print(f"❌ Content creation failed: {e}")

    # Test Ad Manager Agent
    print("\n📢 Testing Ad Manager Agent...")
    try:
        ad_agent = AdManagerAgent(llm)
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

        result_state = await ad_agent.execute(state)
        print(f"✅ Created {len(result_state.get('ad_creatives', []))} ad creatives")
    except Exception as e:
        print(f"❌ Ad management failed: {e}")


def main():
    """Main example execution"""

    print("🎯 AI Marketing Agents - Phase 3 Implementation Demo")
    print("=" * 60)

    async def run_examples():
        # Example 1: Complete campaign
        campaign_result = await example_campaign_execution()

        # Example 2: Agent communication
        await example_agent_communication()

        # Example 3: Resilience monitoring
        await example_resilience_monitoring()

        # Example 4: Individual agents
        await example_individual_agent_usage()

        print("\n🎉 Demo completed!")
        print("\nKey Features Demonstrated:")
        print("• Multi-agent orchestration with LangGraph")
        print("• Shared state management")
        print("• Inter-agent communication")
        print("• Circuit breaker resilience patterns")
        print("• RAG-enhanced content generation")
        print("• Lead qualification and scoring")
        print("• Multi-platform ad campaign management")

    # Run the async examples
    asyncio.run(run_examples())


if __name__ == "__main__":
    main()