"""
Lead Scoring Engine for qualifying and scoring leads
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LeadScoringEngine:
    """Engine for scoring and qualifying leads based on various factors"""
    
    def __init__(self):
        self.logger = logger
        
        # Scoring weights for different factors
        self.scoring_weights = {
            "company_size": 0.25,
            "industry": 0.20,
            "budget": 0.30,
            "timeline": 0.15,
            "decision_authority": 0.10
        }
    
    def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a lead based on qualification criteria
        """
        try:
            score = 0.0
            scoring_details = {}
            
            # Company size scoring
            company_size = lead_data.get("company_size", "unknown")
            company_score = self._score_company_size(company_size)
            score += company_score * self.scoring_weights["company_size"]
            scoring_details["company_size"] = {
                "value": company_size,
                "score": company_score,
                "weight": self.scoring_weights["company_size"]
            }
            
            # Industry scoring
            industry = lead_data.get("industry", "unknown")
            industry_score = self._score_industry(industry)
            score += industry_score * self.scoring_weights["industry"]
            scoring_details["industry"] = {
                "value": industry,
                "score": industry_score,
                "weight": self.scoring_weights["industry"]
            }
            
            # Budget scoring
            budget = lead_data.get("budget", "unknown")
            budget_score = self._score_budget(budget)
            score += budget_score * self.scoring_weights["budget"]
            scoring_details["budget"] = {
                "value": budget,
                "score": budget_score,
                "weight": self.scoring_weights["budget"]
            }
            
            # Timeline scoring
            timeline = lead_data.get("timeline", "unknown")
            timeline_score = self._score_timeline(timeline)
            score += timeline_score * self.scoring_weights["timeline"]
            scoring_details["timeline"] = {
                "value": timeline,
                "score": timeline_score,
                "weight": self.scoring_weights["timeline"]
            }
            
            # Decision authority scoring
            decision_authority = lead_data.get("decision_authority", "unknown")
            authority_score = self._score_decision_authority(decision_authority)
            score += authority_score * self.scoring_weights["decision_authority"]
            scoring_details["decision_authority"] = {
                "value": decision_authority,
                "score": authority_score,
                "weight": self.scoring_weights["decision_authority"]
            }
            
            # Normalize score to 0-100
            final_score = min(100, max(0, score * 100))
            
            # Determine lead grade
            lead_grade = self._get_lead_grade(final_score)
            
            return {
                "success": True,
                "lead_score": final_score,
                "lead_grade": lead_grade,
                "scoring_details": scoring_details,
                "recommendations": self._get_recommendations(final_score, lead_data),
                "scored_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Lead scoring failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "lead_score": 0,
                "lead_grade": "F"
            }
    
    def _score_company_size(self, company_size: str) -> float:
        """Score based on company size"""
        size_scores = {
            "enterprise": 1.0,      # 1000+ employees
            "large": 0.8,           # 200-999 employees
            "medium": 0.6,          # 50-199 employees
            "small": 0.4,           # 10-49 employees
            "startup": 0.3,         # 1-9 employees
            "unknown": 0.2
        }
        return size_scores.get(company_size.lower(), 0.2)
    
    def _score_industry(self, industry: str) -> float:
        """Score based on industry fit"""
        # Industries that typically have higher CRM needs
        high_fit_industries = [
            "technology", "software", "saas", "fintech",
            "real_estate", "insurance", "healthcare",
            "manufacturing", "retail", "e_commerce"
        ]
        
        medium_fit_industries = [
            "consulting", "marketing", "advertising",
            "education", "non_profit", "government"
        ]
        
        industry_lower = industry.lower()
        
        if any(ind in industry_lower for ind in high_fit_industries):
            return 1.0
        elif any(ind in industry_lower for ind in medium_fit_industries):
            return 0.6
        else:
            return 0.3
    
    def _score_budget(self, budget: str) -> float:
        """Score based on budget range"""
        budget_scores = {
            "enterprise": 1.0,      # $10k+ per month
            "high": 0.8,           # $5k-10k per month
            "medium": 0.6,         # $1k-5k per month
            "low": 0.3,            # $500-1k per month
            "minimal": 0.1,        # <$500 per month
            "unknown": 0.2
        }
        return budget_scores.get(budget.lower(), 0.2)
    
    def _score_timeline(self, timeline: str) -> float:
        """Score based on implementation timeline"""
        timeline_scores = {
            "immediate": 1.0,       # Ready to start now
            "1_month": 0.9,        # Within 1 month
            "3_months": 0.7,       # Within 3 months
            "6_months": 0.5,       # Within 6 months
            "1_year": 0.3,         # Within 1 year
            "exploring": 0.2,      # Just exploring
            "unknown": 0.2
        }
        return timeline_scores.get(timeline.lower(), 0.2)
    
    def _score_decision_authority(self, authority: str) -> float:
        """Score based on decision-making authority"""
        authority_scores = {
            "decision_maker": 1.0,     # Final decision maker
            "influencer": 0.8,         # Strong influence on decision
            "evaluator": 0.6,          # Evaluates options
            "user": 0.4,               # End user
            "researcher": 0.2,         # Just researching
            "unknown": 0.3
        }
        return authority_scores.get(authority.lower(), 0.3)
    
    def _get_lead_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 80:
            return "A"  # Hot lead
        elif score >= 60:
            return "B"  # Warm lead
        elif score >= 40:
            return "C"  # Cold lead
        elif score >= 20:
            return "D"  # Poor fit
        else:
            return "F"  # Very poor fit
    
    def _get_recommendations(self, score: float, lead_data: Dict[str, Any]) -> List[str]:
        """Get recommendations based on lead score and data"""
        recommendations = []
        
        if score >= 80:
            recommendations.extend([
                "High-priority lead - schedule demo immediately",
                "Assign to senior sales representative",
                "Prepare custom proposal"
            ])
        elif score >= 60:
            recommendations.extend([
                "Good lead - follow up within 24 hours",
                "Send relevant case studies",
                "Schedule discovery call"
            ])
        elif score >= 40:
            recommendations.extend([
                "Nurture lead with educational content",
                "Add to email marketing campaign",
                "Follow up in 1-2 weeks"
            ])
        else:
            recommendations.extend([
                "Low priority - add to long-term nurture campaign",
                "Send general information",
                "Qualify further before sales involvement"
            ])
        
        # Add specific recommendations based on data gaps
        if lead_data.get("company_size") == "unknown":
            recommendations.append("Qualify company size")
        
        if lead_data.get("budget") == "unknown":
            recommendations.append("Understand budget constraints")
        
        if lead_data.get("timeline") == "unknown":
            recommendations.append("Clarify implementation timeline")
        
        return recommendations


# Global lead scoring engine instance
_lead_scoring_engine = None


def get_lead_scoring_engine() -> LeadScoringEngine:
    """Get the global lead scoring engine instance"""
    global _lead_scoring_engine
    if _lead_scoring_engine is None:
        _lead_scoring_engine = LeadScoringEngine()
    return _lead_scoring_engine


# Convenience variable for backward compatibility
lead_scoring_engine = get_lead_scoring_engine()