"""
Lead Scoring and Segmentation Engine

This module provides advanced lead scoring algorithms and segmentation logic
for CRM integration readiness and co-creator program qualification.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

from app.core.assessment_engine import CRMSystem, AssessmentCategory


class LeadSegment(Enum):
    """Lead segments based on readiness score"""
    COLD = "cold"  # 0-40%: Nurture with guides
    WARM = "warm"  # 41-70%: Co-creator qualified
    HOT = "hot"    # 71-100%: Priority integration


class ScoringFactor(Enum):
    """Factors that influence lead scoring"""
    CRM_INTEGRATION_READINESS = "crm_integration_readiness"
    TECHNICAL_CAPABILITY = "technical_capability"
    BUSINESS_MATURITY = "business_maturity"
    INVESTMENT_CAPACITY = "investment_capacity"
    AUTOMATION_GAPS = "automation_gaps"
    DATA_QUALITY = "data_quality"


@dataclass
class ScoringWeight:
    """Scoring weight configuration"""
    factor: ScoringFactor
    weight: float
    description: str


@dataclass
class LeadScore:
    """Lead scoring result"""
    overall_score: float
    factor_scores: Dict[str, float]
    segment: LeadSegment
    confidence: float
    reasoning: List[str]


@dataclass
class PersonalizedRecommendation:
    """Personalized recommendation for a lead"""
    title: str
    description: str
    priority: str  # high, medium, low
    category: str  # integration, automation, technical, business
    crm_specific: bool
    estimated_impact: str  # high, medium, low
    implementation_effort: str  # easy, medium, hard


class LeadScoringEngine:
    """Advanced lead scoring and segmentation engine"""
    
    def __init__(self):
        self.scoring_weights = self._initialize_scoring_weights()
        self.crm_readiness_matrix = self._initialize_crm_readiness_matrix()
        self.segment_thresholds = {
            LeadSegment.COLD: (0, 40),
            LeadSegment.WARM: (41, 70),
            LeadSegment.HOT: (71, 100)
        }
    
    def _initialize_scoring_weights(self) -> List[ScoringWeight]:
        """Initialize scoring factor weights"""
        return [
            ScoringWeight(
                factor=ScoringFactor.CRM_INTEGRATION_READINESS,
                weight=0.25,
                description="Current CRM system and integration potential"
            ),
            ScoringWeight(
                factor=ScoringFactor.TECHNICAL_CAPABILITY,
                weight=0.20,
                description="Team's technical readiness and API access"
            ),
            ScoringWeight(
                factor=ScoringFactor.BUSINESS_MATURITY,
                weight=0.20,
                description="Lead volume, data quality, and process maturity"
            ),
            ScoringWeight(
                factor=ScoringFactor.INVESTMENT_CAPACITY,
                weight=0.15,
                description="Budget and timeline for implementation"
            ),
            ScoringWeight(
                factor=ScoringFactor.AUTOMATION_GAPS,
                weight=0.15,
                description="Current automation level and improvement potential"
            ),
            ScoringWeight(
                factor=ScoringFactor.DATA_QUALITY,
                weight=0.05,
                description="Quality and completeness of existing data"
            )
        ]
    
    def _initialize_crm_readiness_matrix(self) -> Dict[str, Dict[str, float]]:
        """Initialize CRM-specific readiness scoring matrix"""
        return {
            CRMSystem.NEURACRM.value: {
                "integration_complexity": 1.0,
                "automation_potential": 1.0,
                "setup_time_factor": 1.0,
                "api_quality": 1.0,
                "support_level": 1.0
            },
            CRMSystem.HUBSPOT.value: {
                "integration_complexity": 0.9,
                "automation_potential": 0.95,
                "setup_time_factor": 0.95,
                "api_quality": 0.9,
                "support_level": 0.85
            },
            CRMSystem.PIPEDRIVE.value: {
                "integration_complexity": 0.85,
                "automation_potential": 0.8,
                "setup_time_factor": 0.9,
                "api_quality": 0.85,
                "support_level": 0.8
            },
            CRMSystem.SALESFORCE.value: {
                "integration_complexity": 0.6,
                "automation_potential": 0.9,
                "setup_time_factor": 0.5,
                "api_quality": 0.9,
                "support_level": 0.7
            },
            CRMSystem.ZOHO.value: {
                "integration_complexity": 0.7,
                "automation_potential": 0.75,
                "setup_time_factor": 0.7,
                "api_quality": 0.75,
                "support_level": 0.7
            },
            CRMSystem.MONDAY.value: {
                "integration_complexity": 0.65,
                "automation_potential": 0.6,
                "setup_time_factor": 0.75,
                "api_quality": 0.7,
                "support_level": 0.65
            },
            CRMSystem.OTHER.value: {
                "integration_complexity": 0.3,
                "automation_potential": 0.5,
                "setup_time_factor": 0.3,
                "api_quality": 0.4,
                "support_level": 0.3
            },
            CRMSystem.NONE.value: {
                "integration_complexity": 0.8,  # Fresh start advantage
                "automation_potential": 0.9,
                "setup_time_factor": 0.9,
                "api_quality": 0.9,
                "support_level": 0.9
            }
        }
    
    def calculate_lead_score(self, assessment_data: Dict[str, Any], 
                           category_scores: Dict[str, float],
                           lead_data: Optional[Dict[str, Any]] = None) -> LeadScore:
        """
        Calculate comprehensive lead score for CRM integration readiness
        
        Args:
            assessment_data: Raw assessment responses
            category_scores: Calculated category scores from assessment
            lead_data: Additional lead information (optional)
        
        Returns:
            LeadScore object with detailed scoring breakdown
        """
        factor_scores = {}
        reasoning = []
        
        # Calculate CRM Integration Readiness Score
        crm_score = self._calculate_crm_integration_readiness(assessment_data, reasoning)
        factor_scores[ScoringFactor.CRM_INTEGRATION_READINESS.value] = crm_score
        
        # Calculate Technical Capability Score
        tech_score = self._calculate_technical_capability(assessment_data, reasoning)
        factor_scores[ScoringFactor.TECHNICAL_CAPABILITY.value] = tech_score
        
        # Calculate Business Maturity Score
        business_score = self._calculate_business_maturity(assessment_data, reasoning)
        factor_scores[ScoringFactor.BUSINESS_MATURITY.value] = business_score
        
        # Calculate Investment Capacity Score
        investment_score = self._calculate_investment_capacity(assessment_data, reasoning)
        factor_scores[ScoringFactor.INVESTMENT_CAPACITY.value] = investment_score
        
        # Calculate Automation Gaps Score
        automation_score = self._calculate_automation_gaps(assessment_data, category_scores, reasoning)
        factor_scores[ScoringFactor.AUTOMATION_GAPS.value] = automation_score
        
        # Calculate Data Quality Score
        data_score = self._calculate_data_quality(assessment_data, category_scores, reasoning)
        factor_scores[ScoringFactor.DATA_QUALITY.value] = data_score
        
        # Calculate weighted overall score
        overall_score = 0.0
        for weight_config in self.scoring_weights:
            factor_score = factor_scores.get(weight_config.factor.value, 0.0)
            overall_score += factor_score * weight_config.weight
        
        # Determine segment
        segment = self._determine_segment(overall_score)
        
        # Calculate confidence based on response completeness and consistency
        confidence = self._calculate_confidence(assessment_data, factor_scores)
        
        return LeadScore(
            overall_score=overall_score,
            factor_scores=factor_scores,
            segment=segment,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _calculate_crm_integration_readiness(self, assessment_data: Dict[str, Any], 
                                           reasoning: List[str]) -> float:
        """Calculate CRM integration readiness score"""
        crm_system = assessment_data.get("crm_system", "none")
        crm_usage = assessment_data.get("crm_usage_level", "")
        api_access = assessment_data.get("api_access", "")
        
        # Base score from CRM system
        crm_readiness = self.crm_readiness_matrix.get(crm_system, {})
        base_score = (
            crm_readiness.get("integration_complexity", 0.5) * 0.3 +
            crm_readiness.get("automation_potential", 0.5) * 0.3 +
            crm_readiness.get("api_quality", 0.5) * 0.2 +
            crm_readiness.get("setup_time_factor", 0.5) * 0.2
        ) * 100
        
        # Adjust based on usage level
        usage_multipliers = {
            "We don't use a CRM system": 0.4,
            "Basic contact storage only": 0.6,
            "Track deals and pipeline": 0.8,
            "Advanced workflows and automation": 1.0,
            "Full sales and marketing integration": 1.2
        }
        usage_multiplier = usage_multipliers.get(crm_usage, 0.7)
        
        # Adjust based on API access
        api_multipliers = {
            "No API access available": 0.3,
            "Unsure about API access": 0.5,
            "Limited API access": 0.7,
            "Full API access available": 1.0,
            "Admin rights with full control": 1.1
        }
        api_multiplier = api_multipliers.get(api_access, 0.6)
        
        final_score = min(100, base_score * usage_multiplier * api_multiplier)
        
        # Add reasoning
        if crm_system == "neuracrm":
            reasoning.append("Built-in NeuraCRM provides seamless integration")
        elif crm_system in ["hubspot", "pipedrive"]:
            reasoning.append(f"Excellent {crm_system.title()} API support enables quick integration")
        elif crm_system == "none":
            reasoning.append("Fresh start with NeuraCRM offers maximum automation potential")
        elif api_access in ["No API access available", "Unsure about API access"]:
            reasoning.append("Limited API access may require additional setup steps")
        
        return final_score
    
    def _calculate_technical_capability(self, assessment_data: Dict[str, Any], 
                                      reasoning: List[str]) -> float:
        """Calculate technical capability score"""
        integration_exp = assessment_data.get("integration_experience", "")
        api_access = assessment_data.get("api_access", "")
        
        # Base technical capability score
        exp_scores = {
            "No technical experience": 20,
            "Basic tool setup only": 40,
            "Some integration experience": 60,
            "Comfortable with APIs and webhooks": 80,
            "Advanced technical team": 100
        }
        
        api_scores = {
            "No API access available": 0,
            "Unsure about API access": 20,
            "Limited API access": 50,
            "Full API access available": 80,
            "Admin rights with full control": 100
        }
        
        exp_score = exp_scores.get(integration_exp, 30)
        api_score = api_scores.get(api_access, 30)
        
        # Weighted combination
        final_score = exp_score * 0.6 + api_score * 0.4
        
        # Add reasoning
        if exp_score >= 80:
            reasoning.append("Strong technical team can handle complex integrations")
        elif exp_score <= 40:
            reasoning.append("May need additional technical support during setup")
        
        if api_score <= 20:
            reasoning.append("API access needs to be verified before integration")
        
        return final_score
    
    def _calculate_business_maturity(self, assessment_data: Dict[str, Any], 
                                   reasoning: List[str]) -> float:
        """Calculate business maturity score"""
        monthly_leads = assessment_data.get("monthly_leads", "")
        data_quality = assessment_data.get("data_quality", 1)
        
        # Lead volume scoring
        lead_scores = {
            "Less than 50 leads": 30,
            "50-200 leads": 50,
            "200-500 leads": 70,
            "500-1000 leads": 85,
            "1000+ leads": 100
        }
        
        lead_score = lead_scores.get(monthly_leads, 40)
        
        # Data quality scoring (1-5 scale)
        try:
            data_score = (float(data_quality) - 1) / 4 * 100
        except (ValueError, TypeError):
            data_score = 50
        
        # Weighted combination
        final_score = lead_score * 0.6 + data_score * 0.4
        
        # Add reasoning
        if lead_score >= 85:
            reasoning.append("High lead volume provides strong ROI potential for automation")
        elif lead_score <= 40:
            reasoning.append("Growing lead volume will benefit from early automation setup")
        
        if data_score >= 80:
            reasoning.append("High-quality data enables advanced AI personalization")
        elif data_score <= 40:
            reasoning.append("Data quality improvements will enhance automation effectiveness")
        
        return final_score
    
    def _calculate_investment_capacity(self, assessment_data: Dict[str, Any], 
                                     reasoning: List[str]) -> float:
        """Calculate investment capacity score"""
        budget_timeline = assessment_data.get("budget_timeline", "")
        
        capacity_scores = {
            "Exploring options (no budget yet)": 10,
            "Small budget, need ROI proof": 30,
            "Moderate budget, 3-6 month timeline": 60,
            "Significant budget, immediate implementation": 85,
            "Enterprise budget, comprehensive solution": 100
        }
        
        score = capacity_scores.get(budget_timeline, 25)
        
        # Add reasoning
        if score >= 85:
            reasoning.append("Strong investment capacity enables comprehensive implementation")
        elif score >= 60:
            reasoning.append("Moderate budget allows for phased implementation approach")
        elif score <= 30:
            reasoning.append("ROI demonstration will be important for budget approval")
        
        return score
    
    def _calculate_automation_gaps(self, assessment_data: Dict[str, Any], 
                                 category_scores: Dict[str, float], 
                                 reasoning: List[str]) -> float:
        """Calculate automation gaps score (higher gaps = higher potential)"""
        lead_nurturing = assessment_data.get("lead_nurturing", "")
        marketing_automation = assessment_data.get("marketing_automation", "")
        
        # Inverse scoring - more gaps mean more opportunity
        nurturing_gaps = {
            "Manual follow-up only": 100,
            "Basic email sequences": 80,
            "Some automated workflows": 60,
            "Advanced nurturing campaigns": 40,
            "AI-powered personalized automation": 20
        }
        
        marketing_gaps = {
            "No marketing automation": 100,
            "Basic email marketing (MailChimp, etc.)": 75,
            "CRM-integrated campaigns": 50,
            "Multi-channel automation platform": 30,
            "AI-powered marketing automation": 10
        }
        
        nurturing_score = nurturing_gaps.get(lead_nurturing, 70)
        marketing_score = marketing_gaps.get(marketing_automation, 70)
        
        # Weighted combination
        final_score = nurturing_score * 0.6 + marketing_score * 0.4
        
        # Add reasoning based on gaps
        if nurturing_score >= 80:
            reasoning.append("Significant lead nurturing automation opportunity")
        if marketing_score >= 75:
            reasoning.append("Major marketing automation potential for improved ROI")
        
        return final_score
    
    def _calculate_data_quality(self, assessment_data: Dict[str, Any], 
                              category_scores: Dict[str, float], 
                              reasoning: List[str]) -> float:
        """Calculate data quality score"""
        data_quality = assessment_data.get("data_quality", 1)
        
        try:
            score = (float(data_quality) - 1) / 4 * 100
        except (ValueError, TypeError):
            score = 50
        
        # Add reasoning
        if score >= 80:
            reasoning.append("Excellent data quality enables advanced AI features")
        elif score <= 40:
            reasoning.append("Data quality improvements will be part of implementation")
        
        return score
    
    def _determine_segment(self, overall_score: float) -> LeadSegment:
        """Determine lead segment based on overall score"""
        for segment, (min_score, max_score) in self.segment_thresholds.items():
            if min_score <= overall_score <= max_score:
                return segment
        
        # Default to cold if score is below all thresholds
        return LeadSegment.COLD
    
    def _calculate_confidence(self, assessment_data: Dict[str, Any], 
                            factor_scores: Dict[str, float]) -> float:
        """Calculate confidence in the scoring based on data completeness"""
        total_questions = 10
        answered_questions = len([v for v in assessment_data.values() if v is not None and v != ""])
        completeness = answered_questions / total_questions
        
        # Check for consistency in scores
        score_variance = self._calculate_score_variance(factor_scores)
        consistency = max(0, 1 - score_variance / 50)  # Normalize variance
        
        # Weighted confidence
        confidence = completeness * 0.7 + consistency * 0.3
        
        return min(1.0, confidence)
    
    def _calculate_score_variance(self, factor_scores: Dict[str, float]) -> float:
        """Calculate variance in factor scores"""
        scores = list(factor_scores.values())
        if len(scores) < 2:
            return 0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        return math.sqrt(variance)
    
    def generate_personalized_recommendations(self, lead_score: LeadScore, 
                                            assessment_data: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """Generate personalized recommendations based on lead score and assessment data"""
        recommendations = []
        crm_system = assessment_data.get("crm_system", "none")
        
        # CRM-specific integration recommendations
        if lead_score.segment == LeadSegment.HOT:
            recommendations.extend(self._get_hot_lead_recommendations(crm_system, assessment_data))
        elif lead_score.segment == LeadSegment.WARM:
            recommendations.extend(self._get_warm_lead_recommendations(crm_system, assessment_data))
        else:
            recommendations.extend(self._get_cold_lead_recommendations(crm_system, assessment_data))
        
        # Add factor-specific recommendations
        for factor, score in lead_score.factor_scores.items():
            if score < 50:  # Areas needing improvement
                recommendations.extend(self._get_improvement_recommendations(factor, score, assessment_data))
        
        # Sort by priority and impact
        recommendations.sort(key=lambda r: (
            {"high": 3, "medium": 2, "low": 1}[r.priority],
            {"high": 3, "medium": 2, "low": 1}[r.estimated_impact]
        ), reverse=True)
        
        return recommendations[:8]  # Return top 8 recommendations
    
    def _get_hot_lead_recommendations(self, crm_system: str, 
                                    assessment_data: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """Get recommendations for hot leads (71-100%)"""
        return [
            PersonalizedRecommendation(
                title="Priority Partnership Opportunity",
                description="Book a direct consultation with our founder to discuss partnership and early adopter benefits",
                priority="high",
                category="business",
                crm_specific=False,
                estimated_impact="high",
                implementation_effort="easy"
            ),
            PersonalizedRecommendation(
                title=f"Immediate {crm_system.title()} Integration",
                description=f"Fast-track your {crm_system.title()} integration with dedicated technical support",
                priority="high",
                category="integration",
                crm_specific=True,
                estimated_impact="high",
                implementation_effort="medium"
            ),
            PersonalizedRecommendation(
                title="Beta Feature Access",
                description="Get exclusive access to cutting-edge AI features before general release",
                priority="high",
                category="automation",
                crm_specific=False,
                estimated_impact="high",
                implementation_effort="easy"
            )
        ]
    
    def _get_warm_lead_recommendations(self, crm_system: str, 
                                     assessment_data: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """Get recommendations for warm leads (41-70%)"""
        return [
            PersonalizedRecommendation(
                title="Co-Creator Program Invitation",
                description="Join our exclusive Co-Creator Program for lifetime access and integration support",
                priority="high",
                category="business",
                crm_specific=False,
                estimated_impact="high",
                implementation_effort="easy"
            ),
            PersonalizedRecommendation(
                title=f"Guided {crm_system.title()} Setup",
                description=f"Step-by-step integration guide specifically for {crm_system.title()} users",
                priority="medium",
                category="integration",
                crm_specific=True,
                estimated_impact="medium",
                implementation_effort="medium"
            ),
            PersonalizedRecommendation(
                title="Automation Quick Wins",
                description="Implement high-impact automation workflows that show immediate ROI",
                priority="medium",
                category="automation",
                crm_specific=False,
                estimated_impact="high",
                implementation_effort="medium"
            )
        ]
    
    def _get_cold_lead_recommendations(self, crm_system: str, 
                                     assessment_data: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """Get recommendations for cold leads (0-40%)"""
        return [
            PersonalizedRecommendation(
                title="Free CRM Integration Strategy Guide",
                description="Download our comprehensive guide to CRM integration and marketing automation",
                priority="medium",
                category="business",
                crm_specific=False,
                estimated_impact="medium",
                implementation_effort="easy"
            ),
            PersonalizedRecommendation(
                title="Foundation Building Workshop",
                description="Join our workshop on building marketing automation foundations",
                priority="medium",
                category="automation",
                crm_specific=False,
                estimated_impact="medium",
                implementation_effort="easy"
            ),
            PersonalizedRecommendation(
                title="Technical Readiness Assessment",
                description="Get a detailed assessment of your technical requirements and next steps",
                priority="low",
                category="technical",
                crm_specific=False,
                estimated_impact="medium",
                implementation_effort="easy"
            )
        ]
    
    def _get_improvement_recommendations(self, factor: str, score: float, 
                                       assessment_data: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        """Get recommendations for improving specific scoring factors"""
        recommendations = []
        
        if factor == ScoringFactor.TECHNICAL_CAPABILITY.value and score < 50:
            recommendations.append(
                PersonalizedRecommendation(
                    title="Technical Support Package",
                    description="Get dedicated technical support to ensure smooth integration",
                    priority="medium",
                    category="technical",
                    crm_specific=False,
                    estimated_impact="high",
                    implementation_effort="easy"
                )
            )
        
        if factor == ScoringFactor.DATA_QUALITY.value and score < 50:
            recommendations.append(
                PersonalizedRecommendation(
                    title="Data Quality Improvement",
                    description="Implement data cleaning and enrichment as part of your integration",
                    priority="medium",
                    category="technical",
                    crm_specific=True,
                    estimated_impact="medium",
                    implementation_effort="medium"
                )
            )
        
        return recommendations
    
    def get_segment_next_steps(self, segment: LeadSegment, crm_system: str) -> List[str]:
        """Get specific next steps based on lead segment"""
        if segment == LeadSegment.HOT:
            return [
                "Book a priority demo with our founder",
                "Discuss partnership opportunities for early adoption",
                "Get immediate access to beta features and integrations",
                f"Fast-track {crm_system.title()} integration with dedicated support"
            ]
        elif segment == LeadSegment.WARM:
            return [
                "Join the $497 Co-Creator Program for lifetime AI platform access",
                "Get priority access to new CRM connectors",
                "Receive personalized implementation guidance",
                f"Start with guided {crm_system.title()} integration setup"
            ]
        else:  # COLD
            return [
                "Download our free CRM Integration Strategy Guide",
                "Schedule a consultation to assess your specific needs",
                "Start with basic lead capture and nurturing automation",
                "Join our foundation building workshop"
            ]


# Global lead scoring engine instance
lead_scoring_engine = LeadScoringEngine()
