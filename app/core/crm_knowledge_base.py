"""
CRM-specific knowledge base for conversational AI agent
Contains structured information about CRM integrations, setup processes, and best practices
"""

from typing import Dict, Any, List
from datetime import datetime


class CRMKnowledgeBase:
    """Knowledge base for CRM integration information"""

    def __init__(self):
        self.crm_data = self._initialize_crm_data()
        self.integration_guides = self._initialize_integration_guides()
        self.common_questions = self._initialize_common_questions()
        self.automation_opportunities = self._initialize_automation_opportunities()

    def _initialize_crm_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize CRM system data"""
        return {
            "neuracrm": {
                "name": "NeuraCRM",
                "description": "Built-in AI-powered CRM with advanced automation capabilities",
                "integration_complexity": "easy",
                "setup_time_minutes": 5,
                "oauth2_supported": True,
                "webhook_support": True,
                "automation_potential": "high",
                "key_features": [
                    "AI-powered lead scoring",
                    "Automated follow-up sequences",
                    "Predictive analytics",
                    "Smart contact management",
                    "Integrated marketing automation"
                ],
                "pricing": "Included with Unitasa platform",
                "best_for": "Businesses wanting all-in-one AI marketing automation"
            },
            "hubspot": {
                "name": "HubSpot CRM",
                "description": "Popular inbound marketing and sales platform",
                "integration_complexity": "easy",
                "setup_time_minutes": 10,
                "oauth2_supported": True,
                "webhook_support": True,
                "automation_potential": "high",
                "key_features": [
                    "Contact management",
                    "Deal tracking",
                    "Email marketing",
                    "Landing pages",
                    "Analytics dashboard"
                ],
                "api_documentation": "https://developers.hubspot.com/docs/api/overview",
                "best_for": "Marketing teams focused on inbound strategies"
            },
            "salesforce": {
                "name": "Salesforce",
                "description": "Enterprise-grade CRM with extensive customization",
                "integration_complexity": "advanced",
                "setup_time_minutes": 45,
                "oauth2_supported": True,
                "webhook_support": True,
                "automation_potential": "very_high",
                "key_features": [
                    "Advanced customization",
                    "Workflow automation",
                    "AppExchange marketplace",
                    "Enterprise security",
                    "Advanced reporting"
                ],
                "api_documentation": "https://developer.salesforce.com/docs/",
                "best_for": "Large enterprises with complex sales processes"
            },
            "pipedrive": {
                "name": "Pipedrive",
                "description": "Sales-focused CRM with visual pipeline management",
                "integration_complexity": "easy",
                "setup_time_minutes": 15,
                "oauth2_supported": True,
                "webhook_support": True,
                "automation_potential": "medium",
                "key_features": [
                    "Visual sales pipeline",
                    "Activity reminders",
                    "Email integration",
                    "Mobile app",
                    "Sales reporting"
                ],
                "api_documentation": "https://developers.pipedrive.com/docs/api/v1",
                "best_for": "Sales teams focused on pipeline management"
            },
            "zoho": {
                "name": "Zoho CRM",
                "description": "Comprehensive business suite with CRM capabilities",
                "integration_complexity": "medium",
                "setup_time_minutes": 25,
                "oauth2_supported": True,
                "webhook_support": True,
                "automation_potential": "high",
                "key_features": [
                    "Multi-channel communication",
                    "Workflow automation",
                    "AI assistant (Zia)",
                    "Social media integration",
                    "Advanced analytics"
                ],
                "api_documentation": "https://www.zoho.com/crm/developer/docs/",
                "best_for": "Businesses using Zoho ecosystem"
            },
            "monday": {
                "name": "Monday.com",
                "description": "Work management platform with CRM capabilities",
                "integration_complexity": "medium",
                "setup_time_minutes": 20,
                "oauth2_supported": True,
                "webhook_support": True,
                "automation_potential": "medium",
                "key_features": [
                    "Visual project boards",
                    "Custom workflows",
                    "Team collaboration",
                    "Time tracking",
                    "Automation recipes"
                ],
                "api_documentation": "https://developer.monday.com/api-reference/docs",
                "best_for": "Teams wanting project management + CRM"
            }
        }

    def _initialize_integration_guides(self) -> Dict[str, Dict[str, Any]]:
        """Initialize integration setup guides"""
        return {
            "oauth2_setup": {
                "title": "OAuth2 Integration Setup",
                "steps": [
                    "Create developer account with your CRM provider",
                    "Register your application to get Client ID and Secret",
                    "Configure redirect URLs for Unitasa integration",
                    "Authorize the connection through Unitasa interface",
                    "Test the connection with sample data sync"
                ],
                "security_notes": [
                    "OAuth2 tokens are encrypted and stored securely",
                    "Refresh tokens are automatically managed",
                    "Permissions can be revoked at any time"
                ]
            },
            "api_key_setup": {
                "title": "API Key Integration Setup",
                "steps": [
                    "Log into your CRM admin panel",
                    "Navigate to API settings or integrations",
                    "Generate a new API key with appropriate permissions",
                    "Copy the API key to Unitasa integration settings",
                    "Configure sync preferences and field mapping"
                ],
                "security_notes": [
                    "API keys are encrypted at rest",
                    "Use read/write permissions only as needed",
                    "Regularly rotate API keys for security"
                ]
            },
            "field_mapping": {
                "title": "Field Mapping Configuration",
                "description": "Map fields between Unitasa and your CRM",
                "common_mappings": {
                    "contact_fields": {
                        "email": "Email Address",
                        "first_name": "First Name",
                        "last_name": "Last Name",
                        "company": "Company Name",
                        "phone": "Phone Number"
                    },
                    "lead_fields": {
                        "lead_score": "Lead Score",
                        "lead_source": "Lead Source",
                        "lead_status": "Lead Status",
                        "qualification_score": "Qualification Score"
                    }
                }
            }
        }

    def _initialize_common_questions(self) -> List[Dict[str, str]]:
        """Initialize common questions and answers"""
        return [
            {
                "question": "How long does CRM integration take?",
                "answer": "Integration time varies by CRM: NeuraCRM (5 min), HubSpot (10 min), Pipedrive (15 min), Monday.com (20 min), Zoho (25 min), Salesforce (45 min). Most integrations use OAuth2 for quick setup."
            },
            {
                "question": "Is my CRM data secure during integration?",
                "answer": "Yes, we use enterprise-grade security: OAuth2 authentication, encrypted data transmission, secure token storage, and compliance with SOC 2 and GDPR standards. You maintain full control over your data."
            },
            {
                "question": "Can I sync existing CRM data with Unitasa?",
                "answer": "Absolutely! Unitasa can sync existing contacts, leads, and deals from your CRM. We offer both one-time migration and ongoing bi-directional sync to keep everything up-to-date."
            },
            {
                "question": "What if my CRM isn't directly supported?",
                "answer": "We support integration via Zapier, Make.com, or custom webhooks for any CRM with an API. Our team can also build custom connectors for enterprise clients."
            },
            {
                "question": "How does Unitasa enhance my existing CRM?",
                "answer": "Unitasa adds AI-powered lead scoring, automated nurturing sequences, predictive analytics, and marketing automation while keeping your existing CRM as the central hub."
            },
            {
                "question": "Can I use NeuraCRM instead of my current CRM?",
                "answer": "Yes! NeuraCRM is our built-in AI-powered CRM designed for marketing automation. It includes advanced features like predictive lead scoring and automated workflows. Migration assistance is available."
            }
        ]

    def _initialize_automation_opportunities(self) -> Dict[str, List[str]]:
        """Initialize automation opportunities by business type"""
        return {
            "small_business": [
                "Automated lead capture from website forms",
                "Email follow-up sequences for new leads",
                "Lead scoring based on engagement",
                "Automated appointment scheduling",
                "Social media lead generation"
            ],
            "growing_business": [
                "Multi-channel lead nurturing campaigns",
                "Advanced lead segmentation and scoring",
                "Automated sales pipeline management",
                "Customer lifecycle automation",
                "Integration with marketing tools"
            ],
            "enterprise": [
                "Complex workflow automation",
                "Advanced analytics and reporting",
                "Multi-team collaboration workflows",
                "Custom integration development",
                "Enterprise security and compliance"
            ]
        }

    def get_crm_info(self, crm_name: str) -> Dict[str, Any]:
        """Get information about a specific CRM"""
        return self.crm_data.get(crm_name.lower(), {})

    def get_integration_guide(self, guide_type: str) -> Dict[str, Any]:
        """Get integration guide by type"""
        return self.integration_guides.get(guide_type, {})

    def find_answer(self, question: str) -> str:
        """Find answer to a common question"""
        question_lower = question.lower()
        
        for qa in self.common_questions:
            if any(keyword in question_lower for keyword in qa["question"].lower().split()):
                return qa["answer"]
        
        return ""

    def get_automation_opportunities(self, business_size: str = "growing_business") -> List[str]:
        """Get automation opportunities for business size"""
        return self.automation_opportunities.get(business_size, [])

    def get_crm_comparison(self, crm_list: List[str]) -> Dict[str, Any]:
        """Compare multiple CRMs"""
        comparison = {
            "crms": {},
            "summary": {
                "easiest_setup": "",
                "most_features": "",
                "best_automation": "",
                "enterprise_ready": ""
            }
        }
        
        setup_times = {}
        feature_counts = {}
        automation_scores = {"high": 3, "very_high": 4, "medium": 2, "low": 1}
        
        for crm_name in crm_list:
            crm_info = self.get_crm_info(crm_name)
            if crm_info:
                comparison["crms"][crm_name] = {
                    "name": crm_info.get("name", ""),
                    "setup_time": crm_info.get("setup_time_minutes", 0),
                    "complexity": crm_info.get("integration_complexity", ""),
                    "features": crm_info.get("key_features", []),
                    "automation_potential": crm_info.get("automation_potential", ""),
                    "best_for": crm_info.get("best_for", "")
                }
                
                setup_times[crm_name] = crm_info.get("setup_time_minutes", 999)
                feature_counts[crm_name] = len(crm_info.get("key_features", []))
                
        # Determine best options
        if setup_times:
            comparison["summary"]["easiest_setup"] = min(setup_times, key=setup_times.get)
        if feature_counts:
            comparison["summary"]["most_features"] = max(feature_counts, key=feature_counts.get)
        
        return comparison

    def get_setup_checklist(self, crm_name: str) -> List[str]:
        """Get setup checklist for specific CRM"""
        crm_info = self.get_crm_info(crm_name)
        if not crm_info:
            return []
        
        base_checklist = [
            f"Verify {crm_info.get('name', crm_name)} admin access",
            "Backup existing CRM data",
            "Review Unitasa integration requirements",
            "Plan field mapping strategy"
        ]
        
        if crm_info.get("oauth2_supported"):
            base_checklist.extend([
                "Create developer app in CRM",
                "Configure OAuth2 redirect URLs",
                "Test OAuth2 connection"
            ])
        else:
            base_checklist.extend([
                "Generate API key with appropriate permissions",
                "Test API key connectivity"
            ])
        
        base_checklist.extend([
            "Configure initial sync settings",
            "Test data synchronization",
            "Set up automation workflows",
            "Train team on new processes"
        ])
        
        return base_checklist


# Global knowledge base instance
_crm_knowledge_base = None


def get_crm_knowledge_base() -> CRMKnowledgeBase:
    """Get the global CRM knowledge base instance"""
    global _crm_knowledge_base
    if _crm_knowledge_base is None:
        _crm_knowledge_base = CRMKnowledgeBase()
    return _crm_knowledge_base


def query_crm_knowledge(query: str, crm_name: str = None) -> str:
    """Query the CRM knowledge base"""
    kb = get_crm_knowledge_base()
    
    # Try to find direct answer first
    answer = kb.find_answer(query)
    if answer:
        return answer
    
    # If specific CRM mentioned, provide CRM-specific info
    if crm_name:
        crm_info = kb.get_crm_info(crm_name)
        if crm_info:
            return f"{crm_info.get('name', crm_name)}: {crm_info.get('description', '')} - Setup time: {crm_info.get('setup_time_minutes', 0)} minutes. Best for: {crm_info.get('best_for', '')}"
    
    # Default response
    return "I'd be happy to help with CRM integration questions. Could you be more specific about what you'd like to know?"
