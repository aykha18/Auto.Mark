"""
AI Business Readiness Assessment Engine

This module provides the core assessment functionality including:
- Question configuration and management
- CRM system identification
- Marketing automation gap analysis
- Scoring algorithms
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import json


class CRMSystem(Enum):
    """Supported CRM systems"""
    PIPEDRIVE = "pipedrive"
    ZOHO = "zoho"
    HUBSPOT = "hubspot"
    MONDAY = "monday"
    SALESFORCE = "salesforce"
    NEURACRM = "neuracrm"
    OTHER = "other"
    NONE = "none"


class QuestionType(Enum):
    """Assessment question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    CRM_SELECTOR = "crm_selector"
    TEXT = "text"
    BOOLEAN = "boolean"


class AssessmentCategory(Enum):
    """Assessment scoring categories"""
    CURRENT_CRM = "current_crm"
    DATA_QUALITY = "data_quality"
    AUTOMATION_GAPS = "automation_gaps"
    TECHNICAL_READINESS = "technical_readiness"


@dataclass
class AssessmentQuestion:
    """Assessment question configuration"""
    id: str
    text: str
    integration_insight: str
    question_type: QuestionType
    category: AssessmentCategory
    weight: float
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    required: bool = True


class AssessmentEngine:
    """Core assessment engine for AI Business Readiness Assessment"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
        self.crm_capabilities = self._initialize_crm_capabilities()
        
    def _initialize_questions(self) -> List[AssessmentQuestion]:
        """Initialize the 10 assessment questions"""
        return [
            AssessmentQuestion(
                id="crm_system",
                text="Which CRM system does your business currently use?",
                integration_insight="Understanding your current CRM helps us provide specific integration guidance and automation opportunities.",
                question_type=QuestionType.CRM_SELECTOR,
                category=AssessmentCategory.CURRENT_CRM,
                weight=0.15,
                options=[crm.value for crm in CRMSystem]
            ),
            
            AssessmentQuestion(
                id="crm_usage_level",
                text="How would you describe your current CRM usage?",
                integration_insight="Your CRM usage level determines the complexity of integration and automation opportunities available.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.CURRENT_CRM,
                weight=0.12,
                options=[
                    "We don't use a CRM system",
                    "Basic contact storage only",
                    "Track deals and pipeline",
                    "Advanced workflows and automation",
                    "Full sales and marketing integration"
                ]
            ),
            
            AssessmentQuestion(
                id="data_quality",
                text="How would you rate the quality and completeness of your customer data?",
                integration_insight="Data quality directly impacts the effectiveness of AI-powered automation and personalization.",
                question_type=QuestionType.SCALE,
                category=AssessmentCategory.DATA_QUALITY,
                weight=0.13,
                scale_min=1,
                scale_max=5,
                options=["Poor (lots of missing/outdated data)", "Fair (some gaps)", "Good (mostly complete)", "Very Good (well-maintained)", "Excellent (comprehensive and current)"]
            ),
            
            AssessmentQuestion(
                id="lead_nurturing",
                text="How do you currently handle lead nurturing and follow-up?",
                integration_insight="Automated lead nurturing can increase conversion rates by 50% while reducing manual effort.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.AUTOMATION_GAPS,
                weight=0.14,
                options=[
                    "Manual follow-up only",
                    "Basic email sequences",
                    "Some automated workflows",
                    "Advanced nurturing campaigns",
                    "AI-powered personalized automation"
                ]
            ),
            
            AssessmentQuestion(
                id="marketing_automation",
                text="What marketing automation tools do you currently use?",
                integration_insight="Existing marketing automation can be enhanced with AI and better CRM integration for improved ROI.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.AUTOMATION_GAPS,
                weight=0.12,
                options=[
                    "No marketing automation",
                    "Basic email marketing (MailChimp, etc.)",
                    "CRM-integrated campaigns",
                    "Multi-channel automation platform",
                    "AI-powered marketing automation"
                ]
            ),
            
            AssessmentQuestion(
                id="integration_experience",
                text="How comfortable is your team with integrating new tools and systems?",
                integration_insight="Technical readiness affects implementation timeline and the level of support you'll need.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.TECHNICAL_READINESS,
                weight=0.10,
                options=[
                    "No technical experience",
                    "Basic tool setup only",
                    "Some integration experience",
                    "Comfortable with APIs and webhooks",
                    "Advanced technical team"
                ]
            ),
            
            AssessmentQuestion(
                id="api_access",
                text="Do you have API access or admin rights to your current CRM?",
                integration_insight="API access is essential for seamless integration and real-time data synchronization.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.TECHNICAL_READINESS,
                weight=0.08,
                options=[
                    "No API access available",
                    "Unsure about API access",
                    "Limited API access",
                    "Full API access available",
                    "Admin rights with full control"
                ]
            ),
            
            AssessmentQuestion(
                id="automation_goals",
                text="What's your primary goal for marketing automation?",
                integration_insight="Understanding your goals helps us recommend the most impactful automation workflows for your business.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.AUTOMATION_GAPS,
                weight=0.11,
                options=[
                    "Save time on manual tasks",
                    "Improve lead conversion rates",
                    "Better customer segmentation",
                    "Personalized customer experiences",
                    "Complete marketing-sales alignment"
                ]
            ),
            
            AssessmentQuestion(
                id="monthly_leads",
                text="How many new leads does your business generate monthly?",
                integration_insight="Lead volume determines the automation complexity and ROI potential for your business.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.CURRENT_CRM,
                weight=0.08,
                options=[
                    "Less than 50 leads",
                    "50-200 leads",
                    "200-500 leads",
                    "500-1000 leads",
                    "1000+ leads"
                ]
            ),
            
            AssessmentQuestion(
                id="budget_timeline",
                text="What's your timeline and budget for implementing marketing automation?",
                integration_insight="Timeline and budget help us recommend the right implementation approach and support level.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=AssessmentCategory.TECHNICAL_READINESS,
                weight=0.07,
                options=[
                    "Exploring options (no budget yet)",
                    "Small budget, need ROI proof",
                    "Moderate budget, 3-6 month timeline",
                    "Significant budget, immediate implementation",
                    "Enterprise budget, comprehensive solution"
                ]
            )
        ]
    
    def _initialize_crm_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize CRM system capabilities and integration complexity"""
        return {
            CRMSystem.PIPEDRIVE.value: {
                "name": "Pipedrive",
                "api_quality": "excellent",
                "integration_complexity": "easy",
                "setup_time_minutes": 15,
                "oauth2_supported": True,
                "webhook_support": True,
                "common_objects": ["deals", "persons", "organizations", "activities"],
                "automation_potential": "high",
                "documentation_quality": "excellent"
            },
            CRMSystem.ZOHO.value: {
                "name": "Zoho CRM",
                "api_quality": "good",
                "integration_complexity": "medium",
                "setup_time_minutes": 25,
                "oauth2_supported": True,
                "webhook_support": True,
                "common_objects": ["leads", "contacts", "accounts", "deals"],
                "automation_potential": "high",
                "documentation_quality": "good"
            },
            CRMSystem.HUBSPOT.value: {
                "name": "HubSpot",
                "api_quality": "excellent",
                "integration_complexity": "easy",
                "setup_time_minutes": 10,
                "oauth2_supported": True,
                "webhook_support": True,
                "common_objects": ["contacts", "companies", "deals", "tickets"],
                "automation_potential": "very_high",
                "documentation_quality": "excellent"
            },
            CRMSystem.MONDAY.value: {
                "name": "Monday.com",
                "api_quality": "good",
                "integration_complexity": "medium",
                "setup_time_minutes": 20,
                "oauth2_supported": True,
                "webhook_support": True,
                "common_objects": ["items", "boards", "updates", "users"],
                "automation_potential": "medium",
                "documentation_quality": "good"
            },
            CRMSystem.SALESFORCE.value: {
                "name": "Salesforce",
                "api_quality": "excellent",
                "integration_complexity": "advanced",
                "setup_time_minutes": 45,
                "oauth2_supported": True,
                "webhook_support": True,
                "common_objects": ["leads", "contacts", "accounts", "opportunities"],
                "automation_potential": "very_high",
                "documentation_quality": "excellent"
            },
            CRMSystem.NEURACRM.value: {
                "name": "NeuraCRM (Built-in)",
                "api_quality": "excellent",
                "integration_complexity": "easy",
                "setup_time_minutes": 5,
                "oauth2_supported": True,
                "webhook_support": True,
                "common_objects": ["leads", "contacts", "campaigns", "events"],
                "automation_potential": "very_high",
                "documentation_quality": "excellent"
            },
            CRMSystem.OTHER.value: {
                "name": "Other CRM",
                "api_quality": "unknown",
                "integration_complexity": "advanced",
                "setup_time_minutes": 60,
                "oauth2_supported": False,
                "webhook_support": False,
                "common_objects": ["contacts", "deals"],
                "automation_potential": "medium",
                "documentation_quality": "varies"
            },
            CRMSystem.NONE.value: {
                "name": "No CRM",
                "api_quality": "n/a",
                "integration_complexity": "easy",
                "setup_time_minutes": 5,
                "oauth2_supported": False,
                "webhook_support": False,
                "common_objects": [],
                "automation_potential": "very_high",
                "documentation_quality": "n/a"
            }
        }
    
    def get_questions(self) -> List[Dict[str, Any]]:
        """Get all assessment questions in API format"""
        return [
            {
                "id": q.id,
                "text": q.text,
                "integration_insight": q.integration_insight,
                "type": q.question_type.value,
                "category": q.category.value,
                "weight": q.weight,
                "options": q.options,
                "scale_min": q.scale_min,
                "scale_max": q.scale_max,
                "required": q.required
            }
            for q in self.questions
        ]
    
    def identify_crm_system(self, crm_response: str) -> CRMSystem:
        """Identify CRM system from response"""
        crm_lower = crm_response.lower().strip()
        
        # Direct matches
        for crm in CRMSystem:
            if crm.value == crm_lower:
                return crm
        
        # Fuzzy matching for common variations
        crm_mappings = {
            "pipe": CRMSystem.PIPEDRIVE,
            "pipedrive": CRMSystem.PIPEDRIVE,
            "zoho": CRMSystem.ZOHO,
            "hub": CRMSystem.HUBSPOT,
            "hubspot": CRMSystem.HUBSPOT,
            "monday": CRMSystem.MONDAY,
            "monday.com": CRMSystem.MONDAY,
            "sales": CRMSystem.SALESFORCE,
            "salesforce": CRMSystem.SALESFORCE,
            "sfdc": CRMSystem.SALESFORCE,
            "neura": CRMSystem.NEURACRM,
            "neuracrm": CRMSystem.NEURACRM,
            "none": CRMSystem.NONE,
            "no crm": CRMSystem.NONE,
            "nothing": CRMSystem.NONE
        }
        
        for key, crm in crm_mappings.items():
            if key in crm_lower:
                return crm
        
        return CRMSystem.OTHER
    
    def calculate_category_scores(self, responses: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for each assessment category"""
        category_scores = {}
        category_weights = {}
        
        # Initialize categories
        for category in AssessmentCategory:
            category_scores[category.value] = 0.0
            category_weights[category.value] = 0.0
        
        # Calculate weighted scores for each category
        for question in self.questions:
            response = responses.get(question.id)
            if response is None:
                continue
            
            # Calculate question score based on type and response
            question_score = self._calculate_question_score(question, response)
            
            # Add to category totals
            category = question.category.value
            category_scores[category] += question_score * question.weight
            category_weights[category] += question.weight
        
        # Normalize scores by category weights
        for category in category_scores:
            if category_weights[category] > 0:
                category_scores[category] = (category_scores[category] / category_weights[category]) * 100
            else:
                category_scores[category] = 0.0
        
        return category_scores
    
    def _calculate_question_score(self, question: AssessmentQuestion, response: Any) -> float:
        """Calculate score for individual question response (0-1 scale)"""
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            return self._score_multiple_choice(question.id, response, question.options)
        elif question.question_type == QuestionType.SCALE:
            return self._score_scale(response, question.scale_min, question.scale_max)
        elif question.question_type == QuestionType.CRM_SELECTOR:
            return self._score_crm_selection(response)
        elif question.question_type == QuestionType.BOOLEAN:
            return 1.0 if response else 0.0
        else:
            return 0.5  # Default for text responses
    
    def _score_multiple_choice(self, question_id: str, response: str, options: List[str]) -> float:
        """Score multiple choice responses based on business readiness"""
        if not options or response not in options:
            return 0.0
        
        # Question-specific scoring logic
        scoring_maps = {
            "crm_usage_level": {
                "We don't use a CRM system": 0.0,
                "Basic contact storage only": 0.2,
                "Track deals and pipeline": 0.5,
                "Advanced workflows and automation": 0.8,
                "Full sales and marketing integration": 1.0
            },
            "lead_nurturing": {
                "Manual follow-up only": 0.0,
                "Basic email sequences": 0.3,
                "Some automated workflows": 0.6,
                "Advanced nurturing campaigns": 0.8,
                "AI-powered personalized automation": 1.0
            },
            "marketing_automation": {
                "No marketing automation": 0.0,
                "Basic email marketing (MailChimp, etc.)": 0.3,
                "CRM-integrated campaigns": 0.6,
                "Multi-channel automation platform": 0.8,
                "AI-powered marketing automation": 1.0
            },
            "integration_experience": {
                "No technical experience": 0.2,
                "Basic tool setup only": 0.4,
                "Some integration experience": 0.6,
                "Comfortable with APIs and webhooks": 0.8,
                "Advanced technical team": 1.0
            },
            "api_access": {
                "No API access available": 0.0,
                "Unsure about API access": 0.2,
                "Limited API access": 0.5,
                "Full API access available": 0.8,
                "Admin rights with full control": 1.0
            },
            "automation_goals": {
                "Save time on manual tasks": 0.4,
                "Improve lead conversion rates": 0.6,
                "Better customer segmentation": 0.7,
                "Personalized customer experiences": 0.8,
                "Complete marketing-sales alignment": 1.0
            },
            "monthly_leads": {
                "Less than 50 leads": 0.3,
                "50-200 leads": 0.5,
                "200-500 leads": 0.7,
                "500-1000 leads": 0.9,
                "1000+ leads": 1.0
            },
            "budget_timeline": {
                "Exploring options (no budget yet)": 0.1,
                "Small budget, need ROI proof": 0.3,
                "Moderate budget, 3-6 month timeline": 0.6,
                "Significant budget, immediate implementation": 0.8,
                "Enterprise budget, comprehensive solution": 1.0
            }
        }
        
        if question_id in scoring_maps:
            return scoring_maps[question_id].get(response, 0.0)
        
        # Default scoring: higher index = higher score
        try:
            index = options.index(response)
            return index / (len(options) - 1) if len(options) > 1 else 0.5
        except ValueError:
            return 0.0
    
    def _score_scale(self, response: Any, scale_min: int, scale_max: int) -> float:
        """Score scale responses (normalize to 0-1)"""
        try:
            value = float(response)
            if scale_min is not None and scale_max is not None:
                return (value - scale_min) / (scale_max - scale_min)
            return value / 5.0  # Default 1-5 scale
        except (ValueError, TypeError):
            return 0.0
    
    def _score_crm_selection(self, response: str) -> float:
        """Score CRM selection based on integration potential"""
        crm = self.identify_crm_system(response)
        
        # Score based on integration complexity and automation potential
        crm_scores = {
            CRMSystem.NEURACRM: 1.0,  # Built-in, highest score
            CRMSystem.HUBSPOT: 0.9,   # Excellent API and automation
            CRMSystem.PIPEDRIVE: 0.8, # Great API, easy integration
            CRMSystem.SALESFORCE: 0.7, # Powerful but complex
            CRMSystem.ZOHO: 0.6,      # Good but medium complexity
            CRMSystem.MONDAY: 0.5,    # Different paradigm
            CRMSystem.OTHER: 0.3,     # Unknown integration complexity
            CRMSystem.NONE: 0.4       # No existing system, fresh start
        }
        
        return crm_scores.get(crm, 0.3)
    
    def calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate overall assessment score from category scores"""
        # Weight categories based on business impact
        category_weights = {
            AssessmentCategory.CURRENT_CRM.value: 0.30,
            AssessmentCategory.DATA_QUALITY.value: 0.25,
            AssessmentCategory.AUTOMATION_GAPS.value: 0.25,
            AssessmentCategory.TECHNICAL_READINESS.value: 0.20
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = category_weights.get(category, 0.0)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def generate_recommendations(self, responses: Dict[str, Any], 
                               category_scores: Dict[str, float],
                               overall_score: float) -> Dict[str, List[str]]:
        """Generate personalized recommendations based on assessment results"""
        crm_system = self.identify_crm_system(responses.get("crm_system", ""))
        crm_info = self.crm_capabilities.get(crm_system.value, {})
        
        recommendations = {
            "integration_recommendations": [],
            "automation_opportunities": [],
            "technical_requirements": [],
            "next_steps": []
        }
        
        # CRM-specific integration recommendations
        if crm_system == CRMSystem.NONE:
            recommendations["integration_recommendations"].extend([
                "Consider starting with NeuraCRM for built-in AI automation",
                "Implement lead capture and basic contact management first",
                "Set up automated lead scoring and qualification"
            ])
        elif crm_system == CRMSystem.NEURACRM:
            recommendations["integration_recommendations"].extend([
                "Leverage advanced AI features for predictive lead scoring",
                "Implement automated campaign optimization",
                "Use built-in analytics for performance insights"
            ])
        else:
            recommendations["integration_recommendations"].extend([
                f"Connect {crm_info.get('name', 'your CRM')} via {crm_info.get('setup_time_minutes', 30)}-minute setup",
                f"Sync {', '.join(crm_info.get('common_objects', []))} for comprehensive automation",
                "Enable real-time data synchronization with webhooks"
            ])
        
        # Automation opportunities based on gaps
        automation_score = category_scores.get(AssessmentCategory.AUTOMATION_GAPS.value, 0)
        if automation_score < 40:
            recommendations["automation_opportunities"].extend([
                "Implement automated lead nurturing sequences",
                "Set up behavior-triggered email campaigns",
                "Create automated lead scoring and qualification"
            ])
        elif automation_score < 70:
            recommendations["automation_opportunities"].extend([
                "Add AI-powered personalization to existing campaigns",
                "Implement cross-channel automation workflows",
                "Set up predictive analytics for better targeting"
            ])
        else:
            recommendations["automation_opportunities"].extend([
                "Optimize existing automation with AI insights",
                "Implement advanced attribution modeling",
                "Add voice and conversational AI capabilities"
            ])
        
        # Technical requirements based on readiness
        tech_score = category_scores.get(AssessmentCategory.TECHNICAL_READINESS.value, 0)
        if tech_score < 50:
            recommendations["technical_requirements"].extend([
                "Ensure admin access to your CRM system",
                "Verify API availability and permissions",
                "Plan for basic technical support during setup"
            ])
        else:
            recommendations["technical_requirements"].extend([
                "Prepare OAuth2 credentials for secure integration",
                "Set up webhook endpoints for real-time sync",
                "Configure custom field mapping as needed"
            ])
        
        # Next steps based on overall score and segment
        if overall_score <= 40:  # Cold leads
            recommendations["next_steps"].extend([
                "Download our free CRM Integration Strategy Guide",
                "Schedule a consultation to assess your specific needs",
                "Start with basic lead capture and nurturing automation"
            ])
        elif overall_score <= 70:  # Warm leads
            recommendations["next_steps"].extend([
                "Join our Co-Creator Program for lifetime integration support",
                "Get priority access to new CRM connectors",
                "Receive personalized implementation guidance"
            ])
        else:  # Hot leads
            recommendations["next_steps"].extend([
                "Book a priority demo with our founder",
                "Discuss partnership opportunities for early adoption",
                "Get immediate access to beta features and integrations"
            ])
        
        return recommendations


# Global assessment engine instance
assessment_engine = AssessmentEngine()
