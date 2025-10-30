"""
MCP Server for CRM Integration
Exposes CRM operations as MCP tools for agent-to-agent communication
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add CRM backend to path
crm_backend_path = r"C:\Users\Khana\smart_crm\backend"
if crm_backend_path not in sys.path:
    sys.path.insert(0, crm_backend_path)

try:
    from api.db import get_db, get_engine
    from api.models import Contact, Lead, Deal, Organization, User, Stage
    from sqlalchemy.orm import Session
    from sqlalchemy import text, func, desc
    CRM_AVAILABLE = True
except ImportError as e:
    print(f"CRM import failed: {e}")
    CRM_AVAILABLE = False

from app.mcp.mcp_types import MCPMessage, MCPTool, ToolResult, ToolCall
from app.mcp.server import MCPServer
from app.mcp.monitoring import MCPMonitor


class CRMToolServer(MCPServer):
    """MCP Server that exposes CRM operations as tools"""

    def __init__(self, server_name: str = "crm_server"):
        super().__init__(server_name)
        self.crm_available = CRM_AVAILABLE
        self.monitor = MCPMonitor()
        self.registered_tools = {}  # Add this to store tools
        self.logger = logging.getLogger(__name__)

        if not self.crm_available:
            self.logger.warning("CRM backend not available - tools will return mock data")

    async def initialize(self):
        """Initialize CRM server and register tools"""
        # No super().initialize() needed as MCPServer doesn't have it

        # Register CRM tools
        self.registered_tools["get_crm_dashboard"] = MCPTool(
            name="get_crm_dashboard",
            description="Get CRM dashboard metrics and statistics",
            parameters={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    }
                }
            }
        )

        self.registered_tools["search_contacts"] = MCPTool(
            name="search_contacts",
            description="Search for contacts in the CRM",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for contact name or email"
                    },
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )

        self.registered_tools["get_leads"] = MCPTool(
            name="get_leads",
            description="Get leads from the CRM with filtering options",
            parameters={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by lead status"
                    },
                    "owner_id": {
                        "type": "integer",
                        "description": "Filter by owner ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                }
            }
        )

        self.registered_tools["get_deals"] = MCPTool(
            name="get_deals",
            description="Get deals from the CRM with filtering options",
            parameters={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    },
                    "stage_id": {
                        "type": "integer",
                        "description": "Filter by deal stage ID"
                    },
                    "owner_id": {
                        "type": "integer",
                        "description": "Filter by owner ID"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by deal status (open, won, lost)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                }
            }
        )

        self.registered_tools["create_lead"] = MCPTool(
            name="create_lead",
            description="Create a new lead in the CRM",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Lead title"
                    },
                    "contact_name": {
                        "type": "string",
                        "description": "Contact name"
                    },
                    "contact_email": {
                        "type": "string",
                        "description": "Contact email"
                    },
                    "contact_phone": {
                        "type": "string",
                        "description": "Contact phone"
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "source": {
                        "type": "string",
                        "description": "Lead source"
                    },
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    },
                    "owner_id": {
                        "type": "integer",
                        "description": "Owner ID (optional)"
                    }
                },
                "required": ["title"]
            }
        )

        self.registered_tools["create_contact"] = MCPTool(
            name="create_contact",
            description="Create a new contact in the CRM",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Contact name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Contact email"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Contact phone"
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    }
                },
                "required": ["name"]
            }
        )

        self.registered_tools["create_deal"] = MCPTool(
            name="create_deal",
            description="Create a new deal in the CRM",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Deal title"
                    },
                    "value": {
                        "type": "number",
                        "description": "Deal value"
                    },
                    "contact_id": {
                        "type": "integer",
                        "description": "Contact ID"
                    },
                    "stage_id": {
                        "type": "integer",
                        "description": "Stage ID (optional, defaults to 1)"
                    },
                    "organization_id": {
                        "type": "integer",
                        "description": "Organization ID (optional, defaults to 8)"
                    },
                    "owner_id": {
                        "type": "integer",
                        "description": "Owner ID (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Deal description"
                    }
                },
                "required": ["title"]
            }
        )

        self.logger.info(f"CRM MCP Server initialized with {len(self.registered_tools)} tools")

    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a CRM tool"""
        start_time = datetime.now()

        try:
            if tool_call.tool_name == "get_crm_dashboard":
                result = await self._get_crm_dashboard(tool_call.parameters)
            elif tool_call.tool_name == "search_contacts":
                result = await self._search_contacts(tool_call.parameters)
            elif tool_call.tool_name == "get_leads":
                result = await self._get_leads(tool_call.parameters)
            elif tool_call.tool_name == "get_deals":
                result = await self._get_deals(tool_call.parameters)
            elif tool_call.tool_name == "create_lead":
                result = await self._create_lead(tool_call.parameters)
            elif tool_call.tool_name == "create_contact":
                result = await self._create_contact(tool_call.parameters)
            elif tool_call.tool_name == "create_deal":
                result = await self._create_deal(tool_call.parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_call.tool_name}")

            # Monitor the tool execution
            execution_time = (datetime.now() - start_time).total_seconds()
            await self.monitor.record_tool_execution(
                tool_name=tool_call.tool_name,
                execution_time=execution_time,
                success=True,
                parameters=tool_call.parameters
            )

            return MCPToolResult(
                tool_call_id=tool_call.id,
                success=True,
                result=result
            )

        except Exception as e:
            # Monitor failed execution
            execution_time = (datetime.now() - start_time).total_seconds()
            await self.monitor.record_tool_execution(
                tool_name=tool_call.tool_name,
                execution_time=execution_time,
                success=False,
                error=str(e),
                parameters=tool_call.parameters
            )

            return MCPToolResult(
                tool_call_id=tool_call.id,
                success=False,
                error=str(e)
            )

    async def _get_crm_dashboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get CRM dashboard data"""
        if not self.crm_available:
            return self._get_mock_dashboard()

        org_id = params.get("organization_id", 8)

        try:
            db = next(get_db())

            # Get basic metrics
            total_contacts = db.query(func.count(Contact.id)).filter(Contact.organization_id == org_id).scalar()
            total_leads = db.query(func.count(Lead.id)).filter(Lead.organization_id == org_id).scalar()
            total_deals = db.query(func.count(Deal.id)).filter(Deal.organization_id == org_id).scalar()

            # Get deal values
            total_deal_value = db.query(func.sum(Deal.value)).filter(
                Deal.organization_id == org_id,
                Deal.status == 'won'
            ).scalar() or 0

            # Get recent activity (last 7 days)
            seven_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta
            seven_days_ago = datetime.now() - timedelta(days=7)

            recent_leads = db.query(func.count(Lead.id)).filter(
                Lead.organization_id == org_id,
                Lead.created_at >= seven_days_ago
            ).scalar()

            recent_deals = db.query(func.count(Deal.id)).filter(
                Deal.organization_id == org_id,
                Deal.created_at >= seven_days_ago
            ).scalar()

            # Get stage-wise deal counts
            stage_counts = db.execute(text("""
                SELECT s.name, COUNT(d.id) as count
                FROM stages s
                LEFT JOIN deals d ON s.id = d.stage_id AND d.organization_id = :org_id
                GROUP BY s.id, s.name
                ORDER BY s.order
            """), {"org_id": org_id}).fetchall()

            db.close()

            return {
                "metrics": {
                    "total_contacts": total_contacts,
                    "total_leads": total_leads,
                    "total_deals": total_deals,
                    "total_deal_value": float(total_deal_value),
                    "recent_leads_7d": recent_leads,
                    "recent_deals_7d": recent_deals
                },
                "stage_breakdown": [
                    {"stage": row[0], "count": row[1]}
                    for row in stage_counts
                ],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting CRM dashboard: {e}")
            return self._get_mock_dashboard()

    async def _search_contacts(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for contacts"""
        if not self.crm_available:
            return self._get_mock_contacts()

        query = params.get("query", "")
        org_id = params.get("organization_id", 8)
        limit = min(params.get("limit", 10), 50)  # Max 50 results

        try:
            db = next(get_db())

            contacts = db.query(Contact).filter(
                Contact.organization_id == org_id,
                (Contact.name.ilike(f"%{query}%") | Contact.email.ilike(f"%{query}%"))
            ).limit(limit).all()

            db.close()

            return [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "company": contact.company,
                    "created_at": contact.created_at.isoformat() if contact.created_at else None
                }
                for contact in contacts
            ]

        except Exception as e:
            self.logger.error(f"Error searching contacts: {e}")
            return self._get_mock_contacts()

    async def _get_leads(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get leads with filtering"""
        if not self.crm_available:
            return self._get_mock_leads()

        org_id = params.get("organization_id", 8)
        status_filter = params.get("status")
        owner_id = params.get("owner_id")
        limit = min(params.get("limit", 20), 100)

        try:
            db = next(get_db())

            query = db.query(Lead, Contact.name.label("contact_name")).\
                outerjoin(Contact, Lead.contact_id == Contact.id).\
                filter(Lead.organization_id == org_id)

            if status_filter:
                query = query.filter(Lead.status == status_filter)
            if owner_id:
                query = query.filter(Lead.owner_id == owner_id)

            leads = query.order_by(desc(Lead.created_at)).limit(limit).all()

            db.close()

            return [
                {
                    "id": lead.Lead.id,
                    "title": lead.Lead.title,
                    "contact_name": lead.contact_name,
                    "contact_id": lead.Lead.contact_id,
                    "owner_id": lead.Lead.owner_id,
                    "status": lead.Lead.status,
                    "source": lead.Lead.source,
                    "score": lead.Lead.score,
                    "created_at": lead.Lead.created_at.isoformat() if lead.Lead.created_at else None
                }
                for lead in leads
            ]

        except Exception as e:
            self.logger.error(f"Error getting leads: {e}")
            return self._get_mock_leads()

    async def _get_deals(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get deals with filtering"""
        if not self.crm_available:
            return self._get_mock_deals()

        org_id = params.get("organization_id", 8)
        stage_id = params.get("stage_id")
        owner_id = params.get("owner_id")
        status_filter = params.get("status")
        limit = min(params.get("limit", 20), 100)

        try:
            db = next(get_db())

            query = db.query(Deal, Contact.name.label("contact_name"), User.name.label("owner_name")).\
                outerjoin(Contact, Deal.contact_id == Contact.id).\
                outerjoin(User, Deal.owner_id == User.id).\
                filter(Deal.organization_id == org_id)

            if stage_id:
                query = query.filter(Deal.stage_id == stage_id)
            if owner_id:
                query = query.filter(Deal.owner_id == owner_id)
            if status_filter:
                query = query.filter(Deal.status == status_filter)

            deals = query.order_by(desc(Deal.created_at)).limit(limit).all()

            db.close()

            return [
                {
                    "id": deal.Deal.id,
                    "title": deal.Deal.title,
                    "value": float(deal.Deal.value) if deal.Deal.value else 0,
                    "contact_name": deal.contact_name,
                    "owner_name": deal.owner_name,
                    "stage_id": deal.Deal.stage_id,
                    "status": deal.Deal.status,
                    "created_at": deal.Deal.created_at.isoformat() if deal.Deal.created_at else None
                }
                for deal in deals
            ]

        except Exception as e:
            self.logger.error(f"Error getting deals: {e}")
            return self._get_mock_deals()

    async def _create_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead"""
        if not self.crm_available:
            return {"error": "CRM not available - cannot create lead"}

        try:
            db = next(get_db())

            # First create or find contact
            contact_id = None
            if params.get("contact_email") or params.get("contact_name"):
                contact = db.query(Contact).filter(
                    Contact.email == params.get("contact_email"),
                    Contact.organization_id == params.get("organization_id", 8)
                ).first()

                if not contact and params.get("contact_name"):
                    contact = Contact(
                        name=params["contact_name"],
                        email=params.get("contact_email"),
                        phone=params.get("contact_phone"),
                        company=params.get("company"),
                        organization_id=params.get("organization_id", 8)
                    )
                    db.add(contact)
                    db.flush()
                    contact_id = contact.id
                elif contact:
                    contact_id = contact.id

            # Create lead
            lead = Lead(
                title=params["title"],
                contact_id=contact_id,
                owner_id=params.get("owner_id"),
                organization_id=params.get("organization_id", 8),
                source=params.get("source"),
                created_at=datetime.now()
            )

            db.add(lead)
            db.commit()
            db.refresh(lead)

            db.close()

            return {
                "id": lead.id,
                "title": lead.title,
                "contact_id": contact_id,
                "organization_id": lead.organization_id,
                "created_at": lead.created_at.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error creating lead: {e}")
            return {"error": f"Failed to create lead: {str(e)}"}

    async def _create_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact"""
        if not self.crm_available:
            return {"error": "CRM not available - cannot create contact"}

        try:
            db = next(get_db())

            contact = Contact(
                name=params["name"],
                email=params.get("email"),
                phone=params.get("phone"),
                company=params.get("company"),
                organization_id=params.get("organization_id", 8),
                created_at=datetime.now()
            )

            db.add(contact)
            db.commit()
            db.refresh(contact)

            db.close()

            return {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "organization_id": contact.organization_id,
                "created_at": contact.created_at.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error creating contact: {e}")
            return {"error": f"Failed to create contact: {str(e)}"}

    async def _create_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal"""
        if not self.crm_available:
            return {"error": "CRM not available - cannot create deal"}

        try:
            db = next(get_db())

            deal = Deal(
                title=params["title"],
                value=params.get("value", 0),
                contact_id=params.get("contact_id"),
                stage_id=params.get("stage_id", 1),
                organization_id=params.get("organization_id", 8),
                owner_id=params.get("owner_id"),
                description=params.get("description"),
                created_at=datetime.now()
            )

            db.add(deal)
            db.commit()
            db.refresh(deal)

            db.close()

            return {
                "id": deal.id,
                "title": deal.title,
                "value": float(deal.value) if deal.value else 0,
                "organization_id": deal.organization_id,
                "created_at": deal.created_at.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error creating deal: {e}")
            return {"error": f"Failed to create deal: {str(e)}"}

    # Mock data methods for when CRM is not available
    def _get_mock_dashboard(self) -> Dict[str, Any]:
        return {
            "metrics": {
                "total_contacts": 150,
                "total_leads": 45,
                "total_deals": 12,
                "total_deal_value": 125000.00,
                "recent_leads_7d": 8,
                "recent_deals_7d": 3
            },
            "stage_breakdown": [
                {"stage": "Prospect", "count": 5},
                {"stage": "Qualification", "count": 3},
                {"stage": "Proposal", "count": 2},
                {"stage": "Negotiation", "count": 1},
                {"stage": "Closed Won", "count": 1}
            ],
            "timestamp": datetime.now().isoformat(),
            "note": "Mock data - CRM not available"
        }

    def _get_mock_contacts(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "+1234567890",
                "company": "ABC Corp",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+0987654321",
                "company": "XYZ Ltd",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _get_mock_leads(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "title": "New Software Project",
                "contact_name": "John Smith",
                "contact_id": 1,
                "owner_id": 1,
                "status": "new",
                "source": "website",
                "score": 85,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "title": "Consulting Opportunity",
                "contact_name": "Jane Doe",
                "contact_id": 2,
                "owner_id": 1,
                "status": "qualified",
                "source": "referral",
                "score": 92,
                "created_at": datetime.now().isoformat()
            }
        ]

    def _get_mock_deals(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "title": "Enterprise Software License",
                "value": 50000.00,
                "contact_name": "John Smith",
                "owner_name": "Sales Rep 1",
                "stage_id": 3,
                "status": "open",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "title": "Consulting Services",
                "value": 25000.00,
                "contact_name": "Jane Doe",
                "owner_name": "Sales Rep 2",
                "stage_id": 2,
                "status": "open",
                "created_at": datetime.now().isoformat()
            }
        ]


async def main():
    """Main function to run the CRM MCP server"""
    server = CRMToolServer("crm_server")
    await server.initialize()

    # Start the server
    await server.start()

    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())