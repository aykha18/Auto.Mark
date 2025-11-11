"""
Agentic RAG Tools - Function calling and tool registry for agentic capabilities
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.core.crm_knowledge_base import get_crm_knowledge_base
from app.rag.vectorstore_manager import get_vector_store
from app.llm.router import get_optimal_llm

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of tools available to agents"""
    CRM = "crm"
    CALCULATION = "calculation"
    SEARCH = "search"
    ANALYSIS = "analysis"
    DATA_PROCESSING = "data_processing"


@dataclass
class Tool:
    """Represents a tool that an agent can use"""
    name: str
    description: str
    category: ToolCategory
    func: Callable
    parameters: Dict[str, Any]
    required_params: List[str]
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []


class ToolRegistry:
    """Registry for managing agent tools"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all available tools"""
        self._add_crm_tools()
        self._add_calculation_tools()
        self._add_search_tools()
        self._add_analysis_tools()

    def _add_crm_tools(self):
        """Add CRM-related tools"""
        crm_kb = get_crm_knowledge_base()

        # CRM lookup tool
        self.register_tool(Tool(
            name="crm_lookup",
            description="Look up CRM information, features, pricing, and setup details",
            category=ToolCategory.CRM,
            func=self._crm_lookup,
            parameters={
                "crm_name": {
                    "type": "string",
                    "description": "Name of the CRM (e.g., 'hubspot', 'salesforce', 'pipedrive')"
                },
                "info_type": {
                    "type": "string",
                    "description": "Type of information needed (features, pricing, setup, comparison)",
                    "default": "general"
                }
            },
            required_params=["crm_name"],
            examples=[
                "What are HubSpot's key features?",
                "Compare HubSpot and Salesforce pricing",
                "How do I set up Salesforce integration?"
            ]
        ))

        # CRM comparison tool
        self.register_tool(Tool(
            name="crm_comparison",
            description="Compare multiple CRMs based on features, pricing, and use cases",
            category=ToolCategory.CRM,
            func=self._crm_comparison,
            parameters={
                "crm_list": {
                    "type": "array",
                    "description": "List of CRM names to compare",
                    "items": {"type": "string"}
                },
                "criteria": {
                    "type": "array",
                    "description": "Comparison criteria (features, pricing, ease_of_use, etc.)",
                    "items": {"type": "string"},
                    "default": ["features", "pricing", "ease_of_use"]
                }
            },
            required_params=["crm_list"],
            examples=[
                "Compare HubSpot, Salesforce, and Pipedrive for small businesses",
                "Which CRM is best for marketing teams?"
            ]
        ))

    def _add_calculation_tools(self):
        """Add calculation and mathematical tools"""
        self.register_tool(Tool(
            name="calculate_roi",
            description="Calculate ROI for marketing campaigns or CRM investments",
            category=ToolCategory.CALCULATION,
            func=self._calculate_roi,
            parameters={
                "investment": {
                    "type": "number",
                    "description": "Initial investment amount"
                },
                "returns": {
                    "type": "number",
                    "description": "Total returns generated"
                },
                "timeframe_months": {
                    "type": "number",
                    "description": "Timeframe in months",
                    "default": 12
                }
            },
            required_params=["investment", "returns"],
            examples=[
                "What's the ROI if I invest $10,000 and get $35,000 back?",
                "Calculate 6-month ROI for $50k investment with $180k returns"
            ]
        ))

        self.register_tool(Tool(
            name="calculate_customer_acquisition_cost",
            description="Calculate Customer Acquisition Cost (CAC)",
            category=ToolCategory.CALCULATION,
            func=self._calculate_cac,
            parameters={
                "marketing_spend": {
                    "type": "number",
                    "description": "Total marketing spend"
                },
                "new_customers": {
                    "type": "number",
                    "description": "Number of new customers acquired"
                }
            },
            required_params=["marketing_spend", "new_customers"],
            examples=[
                "What's the CAC if we spent $25,000 and got 50 new customers?",
                "Calculate customer acquisition cost for $100k spend and 200 customers"
            ]
        ))

    def _add_search_tools(self):
        """Add search and information retrieval tools"""
        vectorstore = get_vector_store()

        self.register_tool(Tool(
            name="semantic_search",
            description="Search knowledge base using semantic similarity",
            category=ToolCategory.SEARCH,
            func=self._semantic_search,
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query for semantic matching"
                },
                "top_k": {
                    "type": "number",
                    "description": "Number of results to return",
                    "default": 5
                }
            },
            required_params=["query"],
            examples=[
                "How do I integrate CRM with email marketing?",
                "What are best practices for lead scoring?"
            ]
        ))

        self.register_tool(Tool(
            name="web_search",
            description="Search the web for current information (simulated)",
            category=ToolCategory.SEARCH,
            func=self._web_search,
            parameters={
                "query": {
                    "type": "string",
                    "description": "Web search query"
                },
                "max_results": {
                    "type": "number",
                    "description": "Maximum number of results",
                    "default": 3
                }
            },
            required_params=["query"],
            examples=[
                "Latest CRM market trends 2024",
                "New features in HubSpot Q4 2024"
            ]
        ))

    def _add_analysis_tools(self):
        """Add analysis and processing tools"""
        self.register_tool(Tool(
            name="analyze_competitor",
            description="Analyze competitor CRM offerings and positioning",
            category=ToolCategory.ANALYSIS,
            func=self._analyze_competitor,
            parameters={
                "competitor_name": {
                    "type": "string",
                    "description": "Name of competitor CRM"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis (features, pricing, market_position)",
                    "default": "comprehensive"
                }
            },
            required_params=["competitor_name"],
            examples=[
                "Analyze Salesforce's market position",
                "What makes HubSpot different from competitors?"
            ]
        ))

    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} ({tool.category.value})")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def get_tools_by_category(self, category: ToolCategory) -> List[Tool]:
        """Get all tools in a category"""
        return [tool for tool in self.tools.values() if tool.category == category]

    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_available_tools_info(self) -> str:
        """Get formatted information about available tools"""
        info_parts = []
        for category in ToolCategory:
            category_tools = self.get_tools_by_category(category)
            if category_tools:
                info_parts.append(f"\n{category.value.upper()} TOOLS:")
                for tool in category_tools:
                    info_parts.append(f"- {tool.name}: {tool.description}")
                    if tool.examples:
                        info_parts.append(f"  Examples: {', '.join(tool.examples[:2])}")

        return "\n".join(info_parts)

    # Tool implementations

    def _crm_lookup(self, crm_name: str, info_type: str = "general") -> Dict[str, Any]:
        """Look up CRM information"""
        try:
            crm_kb = get_crm_knowledge_base()
            crm_info = crm_kb.get_crm_info(crm_name.lower())

            if not crm_info:
                return {
                    "error": f"CRM '{crm_name}' not found in knowledge base",
                    "available_crms": list(crm_kb.crm_data.keys())
                }

            if info_type == "features":
                return {
                    "crm": crm_name,
                    "features": crm_info.get("key_features", []),
                    "best_for": crm_info.get("best_for", "")
                }
            elif info_type == "pricing":
                return {
                    "crm": crm_name,
                    "pricing_model": "Contact-based or user-based pricing",
                    "note": "Pricing varies by plan and region"
                }
            elif info_type == "setup":
                return {
                    "crm": crm_name,
                    "setup_time": crm_info.get("setup_time_minutes", 30),
                    "oauth_supported": crm_info.get("oauth2_supported", False),
                    "complexity": crm_info.get("integration_complexity", "medium")
                }
            else:
                return crm_info

        except Exception as e:
            logger.error(f"CRM lookup failed: {e}")
            return {"error": f"Failed to lookup CRM information: {str(e)}"}

    def _crm_comparison(self, crm_list: List[str], criteria: List[str] = None) -> Dict[str, Any]:
        """Compare multiple CRMs"""
        if criteria is None:
            criteria = ["features", "pricing", "ease_of_use"]

        try:
            crm_kb = get_crm_knowledge_base()
            comparison = {}

            for crm_name in crm_list:
                crm_info = crm_kb.get_crm_info(crm_name.lower())
                if crm_info:
                    comparison[crm_name] = {
                        "complexity": crm_info.get("integration_complexity", "unknown"),
                        "setup_time": crm_info.get("setup_time_minutes", "unknown"),
                        "oauth2": crm_info.get("oauth2_supported", False),
                        "best_for": crm_info.get("best_for", "")
                    }

            return {
                "comparison": comparison,
                "criteria_evaluated": criteria,
                "recommendation": self._generate_comparison_recommendation(comparison)
            }

        except Exception as e:
            logger.error(f"CRM comparison failed: {e}")
            return {"error": f"Failed to compare CRMs: {str(e)}"}

    def _calculate_roi(self, investment: float, returns: float, timeframe_months: int = 12) -> Dict[str, Any]:
        """Calculate ROI"""
        try:
            if investment <= 0:
                return {"error": "Investment must be greater than 0"}

            roi_percentage = ((returns - investment) / investment) * 100
            annualized_roi = roi_percentage * (12 / timeframe_months) if timeframe_months > 0 else 0

            return {
                "investment": investment,
                "returns": returns,
                "net_profit": returns - investment,
                "roi_percentage": round(roi_percentage, 2),
                "annualized_roi_percentage": round(annualized_roi, 2),
                "timeframe_months": timeframe_months,
                "interpretation": self._interpret_roi(roi_percentage)
            }

        except Exception as e:
            logger.error(f"ROI calculation failed: {e}")
            return {"error": f"Failed to calculate ROI: {str(e)}"}

    def _calculate_cac(self, marketing_spend: float, new_customers: int) -> Dict[str, Any]:
        """Calculate Customer Acquisition Cost"""
        try:
            if new_customers <= 0:
                return {"error": "Number of new customers must be greater than 0"}

            cac = marketing_spend / new_customers

            return {
                "marketing_spend": marketing_spend,
                "new_customers": new_customers,
                "customer_acquisition_cost": round(cac, 2),
                "benchmark": self._cac_benchmark(cac)
            }

        except Exception as e:
            logger.error(f"CAC calculation failed: {e}")
            return {"error": f"Failed to calculate CAC: {str(e)}"}

    def _semantic_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform semantic search in knowledge base"""
        try:
            vectorstore = get_vector_store()
            docs = vectorstore.similarity_search(query, k=top_k)

            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "score": doc.metadata.get("score", 0)
                })

            return {
                "query": query,
                "results": results,
                "total_found": len(results)
            }

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {"error": f"Failed to perform semantic search: {str(e)}"}

    def _web_search(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """Simulated web search (would integrate with actual search API)"""
        # This is a placeholder - in production, integrate with Google Search API, Bing, etc.
        return {
            "query": query,
            "note": "Web search simulation - integrate with actual search API in production",
            "simulated_results": [
                {
                    "title": f"Latest information about {query}",
                    "snippet": f"This would contain real search results for '{query}' from web sources.",
                    "url": f"https://example.com/search/{query.replace(' ', '-')}"
                }
            ] * max_results
        }

    def _analyze_competitor(self, competitor_name: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze competitor CRM"""
        try:
            crm_kb = get_crm_knowledge_base()
            competitor_info = crm_kb.get_crm_info(competitor_name.lower())

            if not competitor_info:
                return {
                    "error": f"Competitor '{competitor_name}' not found in knowledge base",
                    "available_competitors": list(crm_kb.crm_data.keys())
                }

            analysis = {
                "competitor": competitor_name,
                "market_position": competitor_info.get("best_for", ""),
                "strengths": self._extract_strengths(competitor_info),
                "pricing_tier": "Enterprise" if "enterprise" in competitor_info.get("best_for", "").lower() else "SMB",
                "integration_complexity": competitor_info.get("integration_complexity", "medium")
            }

            if analysis_type == "features":
                analysis["key_features"] = competitor_info.get("key_features", [])
            elif analysis_type == "pricing":
                analysis["pricing_note"] = "Pricing varies by scale and features"

            return analysis

        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"error": f"Failed to analyze competitor: {str(e)}"}

    # Helper methods

    def _generate_comparison_recommendation(self, comparison: Dict) -> str:
        """Generate recommendation based on comparison"""
        if not comparison:
            return "Unable to generate recommendation - no CRM data available"

        # Simple logic: prefer easier integrations for general use
        easy_integrations = [name for name, info in comparison.items()
                           if info.get("complexity") == "easy"]

        if easy_integrations:
            return f"For ease of use, consider: {', '.join(easy_integrations)}"

        return "All compared CRMs have similar complexity levels"

    def _interpret_roi(self, roi_percentage: float) -> str:
        """Interpret ROI percentage"""
        if roi_percentage > 200:
            return "Excellent ROI - highly profitable investment"
        elif roi_percentage > 100:
            return "Good ROI - profitable investment"
        elif roi_percentage > 50:
            return "Moderate ROI - break-even or slight profit"
        elif roi_percentage > 0:
            return "Low ROI - minimal return on investment"
        else:
            return "Negative ROI - investment resulted in loss"

    def _cac_benchmark(self, cac: float) -> str:
        """Benchmark CAC against industry standards"""
        if cac < 100:
            return "Excellent - below industry average ($300-500)"
        elif cac < 300:
            return "Good - within acceptable range"
        elif cac < 500:
            return "Moderate - approaching industry average"
        else:
            return "High - above industry average, consider optimization"

    def _extract_strengths(self, crm_info: Dict) -> List[str]:
        """Extract strengths from CRM info"""
        strengths = []
        if crm_info.get("oauth2_supported"):
            strengths.append("OAuth2 support for easy integration")
        if crm_info.get("integration_complexity") == "easy":
            strengths.append("Easy setup and integration")
        if "marketing" in crm_info.get("best_for", "").lower():
            strengths.append("Strong marketing automation features")

        return strengths if strengths else ["General CRM capabilities"]


# Global tool registry instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry

def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool with given parameters"""
    registry = get_tool_registry()
    tool = registry.get_tool(tool_name)

    if not tool:
        return {"error": f"Tool '{tool_name}' not found"}

    # Validate required parameters
    missing_params = []
    for param in tool.required_params:
        if param not in kwargs:
            missing_params.append(param)

    if missing_params:
        return {"error": f"Missing required parameters: {', '.join(missing_params)}"}

    try:
        result = tool.func(**kwargs)
        return result
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {"error": f"Tool execution failed: {str(e)}"}