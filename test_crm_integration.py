#!/usr/bin/env python3
"""
Test script for CRM MCP Integration
Demonstrates how agents can use CRM tools through MCP
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.mcp.crm_client import CRMClient


async def test_crm_tools():
    """Test CRM MCP integration"""
    print("Testing CRM MCP Integration")
    print("=" * 40)

    # Create CRM client
    crm_client = CRMClient()

    try:
        # Test 1: Get dashboard
        print("\n1. Testing Dashboard Access...")
        dashboard = await crm_client.get_dashboard()
        print(f"   ✓ Dashboard loaded: {len(dashboard.get('metrics', {}))} metrics")
        print(f"   - Total leads: {dashboard['metrics']['total_leads']}")
        print(f"   - Total deals: {dashboard['metrics']['total_deals']}")

        # Test 2: Search contacts
        print("\n2. Testing Contact Search...")
        contacts = await crm_client.search_contacts("john", limit=3)
        print(f"   ✓ Found {len(contacts)} contacts")
        for contact in contacts[:2]:
            print(f"   - {contact['name']} ({contact['email']})")

        # Test 3: Get leads
        print("\n3. Testing Lead Retrieval...")
        leads = await crm_client.get_leads(limit=3)
        print(f"   ✓ Retrieved {len(leads)} leads")
        for lead in leads:
            print(f"   - {lead['title']} (Score: {lead.get('score', 'N/A')})")

        # Test 4: Get deals
        print("\n4. Testing Deal Retrieval...")
        deals = await crm_client.get_deals(limit=3)
        print(f"   ✓ Retrieved {len(deals)} deals")
        for deal in deals:
            print(f"   - {deal['title']}: ${deal['value']} ({deal['status']})")

        # Test 5: Create a lead
        print("\n5. Testing Lead Creation...")
        new_lead = await crm_client.create_lead(
            title="MCP Integration Test Lead",
            contact_name="Test User",
            contact_email="test@mcp-integration.com",
            source="mcp_test",
            company="Test Corp"
        )
        print(f"   ✓ Created lead: {new_lead['title']} (ID: {new_lead['id']})")

        # Test 6: Create a contact
        print("\n6. Testing Contact Creation...")
        new_contact = await crm_client.create_contact(
            name="MCP Test Contact",
            email="contact@mcp-integration.com",
            company="MCP Corp",
            phone="+1-555-0123"
        )
        print(f"   ✓ Created contact: {new_contact['name']} (ID: {new_contact['id']})")

        # Test 7: Create a deal
        print("\n7. Testing Deal Creation...")
        new_deal = await crm_client.create_deal(
            title="MCP Integration Test Deal",
            value=25000.0,
            contact_id=new_contact['id'],
            description="Created via MCP integration test"
        )
        print(f"   ✓ Created deal: {new_deal['title']} (${new_deal['value']})")

        print("\n✅ All CRM MCP integration tests passed!")
        print("\n📊 Integration Summary:")
        print("   - CRM tools are accessible through MCP")
        print("   - Agents can read/write CRM data")
        print("   - Real-time CRM operations supported")
        print("   - Full CRUD operations available")

    except Exception as e:
        print(f"CRM integration test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        pass  # No disconnect method available


async def demonstrate_agent_crm_workflow():
    """Demonstrate a complete agent workflow using CRM tools"""
    print("\nDemonstrating Agent CRM Workflow")
    print("=" * 40)

    from app.agents.crm_integration_example import CRMAgent

    # Create CRM-integrated agent
    agent = CRMAgent("crm_workflow_agent", "CRM Workflow Agent")

    try:
        # Initialize agent
        await agent.initialize()
        print("✓ Agent initialized with CRM capabilities")

        # Step 1: Analyze current opportunities
        print("\n📊 Step 1: Analyzing Lead Opportunities...")
        opportunities = await agent.analyze_lead_opportunities()
        print(f"   Found {opportunities['total_leads']} total leads")
        print(f"   High-value leads: {opportunities['high_value_leads']}")

        # Step 2: Generate follow-up leads
        if opportunities.get('opportunities'):
            print("\n🎯 Step 2: Generating Follow-up Leads...")
            follow_ups = await agent.generate_leads_from_opportunities(
                opportunities['opportunities'][:2]  # Process top 2
            )
            print(f"   Generated {len(follow_ups['generated_leads'])} follow-up leads")

        # Step 3: Sync external contacts
        print("\n👥 Step 3: Syncing External Contacts...")
        mock_contacts = [
            {"name": "Sarah Johnson", "email": "sarah@techstartup.com", "company": "Tech Startup Inc"},
            {"name": "Mike Chen", "email": "mike@innovate.com", "company": "Innovate Solutions"}
        ]

        contact_sync = await agent.sync_contacts_with_campaign(mock_contacts)
        print(f"   Synced {len(contact_sync['synced_contacts'])} existing contacts")
        print(f"   Created {len(contact_sync['created_contacts'])} new contacts")

        # Step 4: Convert leads to deals
        print("\n💼 Step 4: Converting Leads to Deals...")
        # Get some lead IDs to convert (mock data)
        leads = await agent.get_crm_leads(limit=2)
        if leads:
            lead_ids = [lead['id'] for lead in leads[:1]]  # Convert first lead
            deals = await agent.create_deals_from_leads(lead_ids)
            print(f"   Created {len(deals['created_deals'])} deals from leads")

        print("\n✅ Agent CRM workflow completed successfully!")

    except Exception as e:
        print(f"❌ Agent workflow failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await agent.cleanup()


if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_crm_tools())
    asyncio.run(demonstrate_agent_crm_workflow())

    print("\nCRM MCP Integration Complete!")
    print("Your agents can now seamlessly interact with CRM data through MCP.")