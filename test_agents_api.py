#!/usr/bin/env python3
"""
Simple script to test the agent API endpoints without pytest
"""

import asyncio
import json
import httpx
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-here"  # Replace with actual API key

# Headers for API requests
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


async def make_request(method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an HTTP request to the API"""
    url = f"{BASE_URL}{endpoint}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=HEADERS)
            elif method.upper() == "POST":
                response = await client.post(url, headers=HEADERS, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            return {"error": str(e)}


async def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    result = await make_request("GET", "/health")
    print(f"Health Status: {result.get('status', 'unknown')}")
    return result


async def test_available_agents():
    """Test getting available agents"""
    print("\n🤖 Testing Available Agents...")
    result = await make_request("GET", "/api/v1/agents")
    if "error" not in result:
        print("Available agents:")
        for agent, description in result.items():
            print(f"  - {agent}: {description}")
    else:
        print(f"Error: {result['error']}")
    return result


async def test_agent_metrics():
    """Test getting agent metrics"""
    print("\n📊 Testing Agent Metrics...")
    for agent in ["lead_generation", "content_creator", "ad_manager"]:
        result = await make_request("GET", f"/api/v1/agents/{agent}/metrics")
        if "error" not in result:
            print(f"{agent} metrics: {result['total_calls']} calls, {result['success_rate']:.2f} success rate")
        else:
            print(f"Error getting {agent} metrics: {result['error']}")


async def test_lead_generation():
    """Test lead generation agent"""
    print("\n🔍 Testing Lead Generation Agent...")
    result = await make_request("GET", "/api/v1/test/lead-generation")
    if "error" not in result:
        print(f"Lead generation test: {result['status']}")
        print(f"Leads found: {result['leads_found']}")
        print(f"Qualified leads: {result['qualified_leads']}")
    else:
        print(f"Error: {result['error']}")
    return result


async def test_content_creation():
    """Test content creation agent"""
    print("\n✍️ Testing Content Creation Agent...")
    result = await make_request("GET", "/api/v1/test/content-creation")
    if "error" not in result:
        print(f"Content creation test: {result['status']}")
        print(f"Content created: {result['content_created']}")
    else:
        print(f"Error: {result['error']}")
    return result


async def test_ad_management():
    """Test ad management agent"""
    print("\n📢 Testing Ad Management Agent...")
    result = await make_request("GET", "/api/v1/test/ad-management")
    if "error" not in result:
        print(f"Ad management test: {result['status']}")
        print(f"Ad creatives: {result['ad_creatives']}")
    else:
        print(f"Error: {result['error']}")
    return result


async def test_full_workflow():
    """Test the complete agent workflow"""
    print("\n🚀 Testing Full Agent Workflow...")

    campaign_config = {
        "name": "API Test Campaign",
        "target_audience": {
            "industry": "technology",
            "company_size": "50-200",
            "job_titles": ["CTO", "VP Engineering"]
        },
        "content_required": True,
        "content_requirements": {
            "type": "blog_post",
            "topic": "AI Marketing Strategies",
            "tone": "professional"
        },
        "ad_platforms": ["google_ads"],
        "budget": 2000.0,
        "brand_guidelines": {
            "tone": "professional",
            "prohibited_words": ["cheap"]
        }
    }

    result = await make_request("POST", "/api/v1/campaigns/run", campaign_config)
    if "error" not in result:
        print(f"Full workflow test: {result['status']}")
        print(f"Campaign ID: {result['campaign_id']}")
        print(f"Qualified leads: {result['qualified_leads']}")
        print(f"Content created: {result['content_created']}")
        print(f"Ad campaigns: {result['ad_campaigns']}")
        print(".2f")
    else:
        print(f"Error: {result['error']}")
    return result


async def test_agent_communication():
    """Test inter-agent communication"""
    print("\n💬 Testing Agent Communication...")

    # Send a test message
    message_data = {
        "sender": "test_script",
        "receiver": "lead_generation",
        "message_type": "task_request",
        "payload": {"task": "test_communication", "data": "Hello from test script!"}
    }

    result = await make_request("POST", "/api/v1/messages/send", message_data)
    if "error" not in result:
        print(f"Message sent successfully: {result['correlation_id']}")

        # Try to receive messages
        messages = await make_request("GET", "/api/v1/messages/lead_generation")
        if "error" not in messages:
            print(f"Messages received: {messages['message_count']}")
        else:
            print(f"Error receiving messages: {messages['error']}")
    else:
        print(f"Error sending message: {result['error']}")
    return result


async def test_campaign_validation():
    """Test campaign configuration validation"""
    print("\n✅ Testing Campaign Validation...")

    # Valid config
    valid_config = {
        "name": "Valid Test Campaign",
        "target_audience": {"industry": "technology"}
    }

    result = await make_request("POST", "/api/v1/campaigns/validate", valid_config)
    if "error" not in result:
        print(f"Validation result: {'Valid' if result['valid'] else 'Invalid'}")
        if result.get('warnings'):
            print(f"Warnings: {result['warnings']}")
    else:
        print(f"Error: {result['error']}")
    return result


async def main():
    """Run all tests"""
    print("🧪 AI Marketing Agents API Test Suite")
    print("=" * 50)

    # Test basic endpoints
    await test_health_check()
    await test_available_agents()
    await test_agent_metrics()

    # Test individual agents
    await test_lead_generation()
    await test_content_creation()
    await test_ad_management()

    # Test integration
    await test_full_workflow()
    await test_agent_communication()
    await test_campaign_validation()

    print("\n🎉 API Testing Complete!")
    print("\nTo run individual tests:")
    print("python test_agents_api.py")


if __name__ == "__main__":
    asyncio.run(main())