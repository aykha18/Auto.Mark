"""
MCP Client for CRM Integration
Allows agents to call CRM tools through MCP
"""

import asyncio
import json
# from typing import Dict, List, Optional, Any
from datetime import datetime

from app.mcp.mcp_types import MCPMessage, ToolCall, ToolResult
from app.mcp.client import MCPClient
from app.mcp.monitoring import MCPMonitor


class CRMClient(MCPClient):
    """MCP Client for accessing CRM operations"""

    def __init__(self, server_name: str = "crm_server"):
        super().__init__(server_name)
        self.monitor = MCPMonitor()

    async def get_dashboard(self, organization_id: int = 8):
        """Get CRM dashboard metrics"""
        result = await self.call_tool("get_crm_dashboard", {
            "organization_id": organization_id
        })

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to get dashboard: {result.error}")

    async def search_contacts(self, query: str, organization_id: int = 8, limit: int = 10):
        """Search for contacts"""
        result = await self.call_tool("search_contacts", {
            "query": query,
            "organization_id": organization_id,
            "limit": limit
        })

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to search contacts: {result.error}")

    async def get_leads(self, organization_id: int = 8, status=None,
                       owner_id=None, limit: int = 20):
        """Get leads with optional filtering"""
        params = {"organization_id": organization_id, "limit": limit}
        if status:
            params["status"] = status
        if owner_id:
            params["owner_id"] = owner_id

        result = await self.call_tool("get_leads", params)

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to get leads: {result.error}")

    async def get_deals(self, organization_id: int = 8, stage_id=None,
                       owner_id=None, status=None,
                       limit: int = 20):
        """Get deals with optional filtering"""
        params = {"organization_id": organization_id, "limit": limit}
        if stage_id:
            params["stage_id"] = stage_id
        if owner_id:
            params["owner_id"] = owner_id
        if status:
            params["status"] = status

        result = await self.call_tool("get_deals", params)

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to get deals: {result.error}")

    async def create_lead(self, title: str, contact_name=None,
                         contact_email=None, contact_phone=None,
                         company=None, source=None,
                         organization_id: int = 8, owner_id=None):
        """Create a new lead"""
        params = {
            "title": title,
            "organization_id": organization_id
        }

        if contact_name:
            params["contact_name"] = contact_name
        if contact_email:
            params["contact_email"] = contact_email
        if contact_phone:
            params["contact_phone"] = contact_phone
        if company:
            params["company"] = company
        if source:
            params["source"] = source
        if owner_id:
            params["owner_id"] = owner_id

        result = await self.call_tool("create_lead", params)

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to create lead: {result.error}")

    async def create_contact(self, name: str, email=None,
                           phone=None, company=None,
                           organization_id: int = 8):
        """Create a new contact"""
        params = {
            "name": name,
            "organization_id": organization_id
        }

        if email:
            params["email"] = email
        if phone:
            params["phone"] = phone
        if company:
            params["company"] = company

        result = await self.call_tool("create_contact", params)

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to create contact: {result.error}")

    async def create_deal(self, title: str, value=None,
                         contact_id=None, stage_id: int = 1,
                         organization_id: int = 8, owner_id=None,
                         description=None):
        """Create a new deal"""
        params = {
            "title": title,
            "stage_id": stage_id,
            "organization_id": organization_id
        }

        if value is not None:
            params["value"] = value
        if contact_id:
            params["contact_id"] = contact_id
        if owner_id:
            params["owner_id"] = owner_id
        if description:
            params["description"] = description

        result = await self.call_tool("create_deal", params)

        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to create deal: {result.error}")


class CRMIntegrationMixin:
    """Mixin class to add CRM integration capabilities to agents"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crm_client = None

    async def initialize_crm_client(self):
        """Initialize CRM client connection"""
        if not self.crm_client:
            self.crm_client = CRMClient()
            await self.crm_client.connect()

    async def get_crm_dashboard(self, organization_id: int = 8):
        """Get CRM dashboard data"""
        await self.initialize_crm_client()
        return await self.crm_client.get_dashboard(organization_id)

    async def search_crm_contacts(self, query: str, organization_id: int = 8, limit: int = 10):
        """Search CRM contacts"""
        await self.initialize_crm_client()
        return await self.crm_client.search_contacts(query, organization_id, limit)

    async def get_crm_leads(self, organization_id: int = 8, status=None,
                           owner_id=None, limit: int = 20):
        """Get CRM leads"""
        await self.initialize_crm_client()
        return await self.crm_client.get_leads(organization_id, status, owner_id, limit)

    async def get_crm_deals(self, organization_id: int = 8, stage_id=None,
                           owner_id=None, status=None,
                           limit: int = 20):
        """Get CRM deals"""
        await self.initialize_crm_client()
        return await self.crm_client.get_deals(organization_id, stage_id, owner_id, status, limit)

    async def create_crm_lead(self, title: str, contact_name=None,
                             contact_email=None, contact_phone=None,
                             company=None, source=None,
                             organization_id: int = 8, owner_id=None):
        """Create a new lead in CRM"""
        await self.initialize_crm_client()
        return await self.crm_client.create_lead(
            title, contact_name, contact_email, contact_phone,
            company, source, organization_id, owner_id
        )

    async def create_crm_contact(self, name: str, email=None,
                                phone=None, company=None,
                                organization_id: int = 8):
        """Create a new contact in CRM"""
        await self.initialize_crm_client()
        return await self.crm_client.create_contact(name, email, phone, company, organization_id)

    async def create_crm_deal(self, title: str, value=None,
                             contact_id=None, stage_id: int = 1,
                             organization_id: int = 8, owner_id=None,
                             description=None):
        """Create a new deal in CRM"""
        await self.initialize_crm_client()
        return await self.crm_client.create_deal(
            title, value, contact_id, stage_id, organization_id, owner_id, description
        )


# Example usage and testing
async def test_crm_integration():
    """Test CRM integration functionality"""
    print("Testing CRM MCP Integration...")

    # Create CRM client
    crm_client = CRMClient()

    try:
        # Connect to CRM server
        await crm_client.connect()
        print("✓ Connected to CRM server")

        # Test dashboard
        print("\n--- Testing Dashboard ---")
        dashboard = await crm_client.get_dashboard()
        print(f"Dashboard metrics: {json.dumps(dashboard, indent=2)}")

        # Test contact search
        print("\n--- Testing Contact Search ---")
        contacts = await crm_client.search_contacts("john")
        print(f"Found {len(contacts)} contacts")
        for contact in contacts[:3]:  # Show first 3
            print(f"  - {contact['name']} ({contact['email']})")

        # Test leads
        print("\n--- Testing Leads ---")
        leads = await crm_client.get_leads(limit=5)
        print(f"Found {len(leads)} leads")
        for lead in leads:
            print(f"  - {lead['title']} ({lead['status']})")

        # Test deals
        print("\n--- Testing Deals ---")
        deals = await crm_client.get_deals(limit=5)
        print(f"Found {len(deals)} deals")
        for deal in deals:
            print(f"  - {deal['title']}: ${deal['value']} ({deal['status']})")

        # Test creating a lead
        print("\n--- Testing Lead Creation ---")
        new_lead = await crm_client.create_lead(
            title="Test Lead from MCP",
            contact_name="Test Contact",
            contact_email="test@example.com",
            source="mcp_test"
        )
        print(f"Created lead: {new_lead}")

        print("\n✓ All CRM integration tests passed!")

    except Exception as e:
        print(f"✗ CRM integration test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await crm_client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_crm_integration())
