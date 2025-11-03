"""
Assessment Engine for AI readiness and CRM assessments
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AssessmentEngine:
    """Engine for processing and scoring various types of assessments"""
    
    def __init__(self):
        self.logger = logger
    
    def process_ai_readiness_assessment(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process AI readiness assessment responses and generate score
        """
        try:
            total_score = 0
            max_score = 0
            category_scores = {}
            
            # Define assessment categories and their weights
            categories = {
                "data_quality": {
                    "weight": 0.25,
                    "questions": ["data_centralized", "data_clean", "data_accessible"]
                },
                "technical_infrastructure": {
                    "weight": 0.20,
                    "questions": ["cloud_infrastructure", "api_integrations", "security_measures"]
                },
                "team_readiness": {
                    "weight": 0.20,
                    "questions": ["technical_skills", "change_management", "training_budget"]
                },
                "business_processes": {
                    "weight": 0.20,
                    "questions": ["process_documentation", "automation_experience", "kpi_tracking"]
                },
                "budget_timeline": {
                    "weight": 0.15,
                    "questions": ["budget_allocated", "timeline_realistic", "roi_expectations"]
                }
            }
            
            # Score each category
            for category, config in categories.items():
                category_total = 0
                category_max = 0
                
                for question in config["questions"]:
                    if question in responses:
                        # Assuming responses are on a 1-5 scale
                        score = int(responses[question])
                        category_total += score
                        category_max += 5
                
                if category_max > 0:
                    category_percentage = (category_total / category_max) * 100
                    weighted_score = category_percentage * config["weight"]
                    
                    category_scores[category] = {
                        "score": category_percentage,
                        "weight": config["weight"],
                        "weighted_score": weighted_score
                    }
                    
                    total_score += weighted_score
                    max_score += 100 * config["weight"]
            
            # Calculate final percentage
            final_score = min(100, max(0, total_score))
            
            # Determine readiness level
            readiness_level = self._get_readiness_level(final_score)
            
            # Generate recommendations
            recommendations = self._get_ai_readiness_recommendations(final_score, category_scores)
            
            return {
                "success": True,
                "overall_score": round(final_score, 1),
                "readiness_level": readiness_level,
                "category_scores": category_scores,
                "recommendations": recommendations,
                "next_steps": self._get_next_steps(readiness_level),
                "assessed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"AI readiness assessment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_score": 0,
                "readiness_level": "not_ready"
            }
    
    def process_crm_assessment(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process CRM assessment responses and generate recommendations
        """
        try:
            # Analyze current CRM usage
            current_crm = responses.get("current_crm", "none")
            team_size = responses.get("team_size", "small")
            industry = responses.get("industry", "unknown")
            budget = responses.get("budget", "low")
            
            # Score different CRM aspects
            scores = {
                "lead_management": self._score_crm_aspect(responses, "lead_management"),
                "sales_pipeline": self._score_crm_aspect(responses, "sales_pipeline"),
                "customer_service": self._score_crm_aspect(responses, "customer_service"),
                "marketing_automation": self._score_crm_aspect(responses, "marketing_automation"),
                "reporting_analytics": self._score_crm_aspect(responses, "reporting_analytics")
            }
            
            # Calculate overall CRM maturity
            overall_score = sum(scores.values()) / len(scores)
            maturity_level = self._get_crm_maturity_level(overall_score)
            
            # Generate CRM recommendations
            crm_recommendations = self._get_crm_recommendations(
                current_crm, team_size, industry, budget, scores
            )
            
            return {
                "success": True,
                "overall_score": round(overall_score, 1),
                "maturity_level": maturity_level,
                "aspect_scores": scores,
                "current_crm": current_crm,
                "recommended_crms": crm_recommendations,
                "improvement_areas": self._identify_improvement_areas(scores),
                "assessed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"CRM assessment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_score": 0,
                "maturity_level": "basic"
            }
    
    def _get_readiness_level(self, score: float) -> str:
        """Determine AI readiness level based on score"""
        if score >= 80:
            return "highly_ready"
        elif score >= 60:
            return "moderately_ready"
        elif score >= 40:
            return "somewhat_ready"
        else:
            return "not_ready"
    
    def _get_ai_readiness_recommendations(self, score: float, category_scores: Dict[str, Any]) -> List[str]:
        """Generate AI readiness recommendations"""
        recommendations = []
        
        # Overall recommendations based on score
        if score >= 80:
            recommendations.extend([
                "You're ready to implement AI solutions",
                "Consider starting with a pilot project",
                "Focus on measuring ROI and scaling successful implementations"
            ])
        elif score >= 60:
            recommendations.extend([
                "Address key gaps before full AI implementation",
                "Start with low-risk AI applications",
                "Invest in team training and change management"
            ])
        elif score >= 40:
            recommendations.extend([
                "Significant preparation needed before AI implementation",
                "Focus on data quality and infrastructure improvements",
                "Build internal capabilities and processes"
            ])
        else:
            recommendations.extend([
                "Not ready for AI implementation yet",
                "Focus on foundational improvements",
                "Consider consulting services for roadmap development"
            ])
        
        # Category-specific recommendations
        for category, data in category_scores.items():
            if data["score"] < 60:  # Below average
                if category == "data_quality":
                    recommendations.append("Improve data centralization and quality")
                elif category == "technical_infrastructure":
                    recommendations.append("Upgrade technical infrastructure and security")
                elif category == "team_readiness":
                    recommendations.append("Invest in team training and change management")
                elif category == "business_processes":
                    recommendations.append("Document and optimize business processes")
                elif category == "budget_timeline":
                    recommendations.append("Clarify budget allocation and timeline expectations")
        
        return recommendations
    
    def _get_next_steps(self, readiness_level: str) -> List[str]:
        """Get next steps based on readiness level"""
        next_steps = {
            "highly_ready": [
                "Schedule a demo of our AI solutions",
                "Discuss pilot project opportunities",
                "Review implementation timeline and pricing"
            ],
            "moderately_ready": [
                "Download our AI readiness checklist",
                "Schedule a consultation to address gaps",
                "Consider our AI readiness workshop"
            ],
            "somewhat_ready": [
                "Focus on foundational improvements",
                "Download our preparation guide",
                "Schedule a strategy session"
            ],
            "not_ready": [
                "Start with our foundational assessment",
                "Consider consulting services",
                "Download our getting started guide"
            ]
        }
        
        return next_steps.get(readiness_level, [])
    
    def _score_crm_aspect(self, responses: Dict[str, Any], aspect: str) -> float:
        """Score a specific CRM aspect"""
        # Mock scoring logic - in production, this would be more sophisticated
        aspect_questions = {
            "lead_management": ["lead_tracking", "lead_scoring", "lead_nurturing"],
            "sales_pipeline": ["pipeline_visibility", "deal_tracking", "forecasting"],
            "customer_service": ["ticket_management", "customer_history", "service_automation"],
            "marketing_automation": ["email_campaigns", "lead_generation", "campaign_tracking"],
            "reporting_analytics": ["custom_reports", "dashboard_usage", "data_analysis"]
        }
        
        questions = aspect_questions.get(aspect, [])
        if not questions:
            return 50.0  # Default score
        
        total_score = 0
        answered_questions = 0
        
        for question in questions:
            if question in responses:
                total_score += int(responses[question])
                answered_questions += 1
        
        if answered_questions == 0:
            return 50.0  # Default score if no questions answered
        
        # Convert to percentage (assuming 1-5 scale)
        return (total_score / (answered_questions * 5)) * 100
    
    def _get_crm_maturity_level(self, score: float) -> str:
        """Determine CRM maturity level"""
        if score >= 80:
            return "advanced"
        elif score >= 60:
            return "intermediate"
        elif score >= 40:
            return "basic"
        else:
            return "minimal"
    
    def _get_crm_recommendations(self, current_crm: str, team_size: str, 
                               industry: str, budget: str, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate CRM recommendations"""
        # Mock CRM recommendations - in production, this would be more sophisticated
        recommendations = []
        
        if team_size == "small" and budget == "low":
            recommendations.extend([
                {
                    "name": "HubSpot CRM",
                    "fit_score": 85,
                    "reasons": ["Free tier available", "Easy to use", "Good for small teams"],
                    "pricing": "Free - $50/month"
                },
                {
                    "name": "Pipedrive",
                    "fit_score": 80,
                    "reasons": ["Simple pipeline management", "Affordable pricing", "Good mobile app"],
                    "pricing": "$15 - $100/month"
                }
            ])
        elif team_size == "medium":
            recommendations.extend([
                {
                    "name": "Salesforce",
                    "fit_score": 90,
                    "reasons": ["Highly customizable", "Strong automation", "Extensive integrations"],
                    "pricing": "$25 - $300/month per user"
                },
                {
                    "name": "Microsoft Dynamics 365",
                    "fit_score": 85,
                    "reasons": ["Office 365 integration", "AI capabilities", "Industry solutions"],
                    "pricing": "$20 - $200/month per user"
                }
            ])
        else:  # Large teams
            recommendations.extend([
                {
                    "name": "Salesforce Enterprise",
                    "fit_score": 95,
                    "reasons": ["Enterprise features", "Advanced customization", "Scalability"],
                    "pricing": "$150 - $500/month per user"
                },
                {
                    "name": "Oracle CX",
                    "fit_score": 88,
                    "reasons": ["Enterprise-grade", "AI and ML capabilities", "Complete suite"],
                    "pricing": "Custom pricing"
                }
            ])
        
        return recommendations
    
    def _identify_improvement_areas(self, scores: Dict[str, float]) -> List[str]:
        """Identify areas that need improvement"""
        improvement_areas = []
        
        for aspect, score in scores.items():
            if score < 60:  # Below average
                area_names = {
                    "lead_management": "Lead Management",
                    "sales_pipeline": "Sales Pipeline",
                    "customer_service": "Customer Service",
                    "marketing_automation": "Marketing Automation",
                    "reporting_analytics": "Reporting & Analytics"
                }
                improvement_areas.append(area_names.get(aspect, aspect))
        
        return improvement_areas


# Global assessment engine instance
_assessment_engine = None


def get_assessment_engine() -> AssessmentEngine:
    """Get the global assessment engine instance"""
    global _assessment_engine
    if _assessment_engine is None:
        _assessment_engine = AssessmentEngine()
    return _assessment_engine


# Convenience variable for backward compatibility
assessment_engine = get_assessment_engine()