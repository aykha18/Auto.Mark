"""
Lead Nurturing Integration Service
Integrates with existing Unitasa agents for lead nurturing workflows
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.campaign import Campaign
from app.agents.communication import AgentCommunicator
from app.agents.content_creator import ContentCreatorAgent
from app.agents.lead_generation import LeadGenerationAgent
from app.core.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class LeadNurturingIntegration:
    """Service for integrating lead capture with Unitasa agent workflows"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)
        
        # Initialize agents
        self.communication_agent = AgentCommunicator()
        self.content_creator = ContentCreatorAgent()
        self.lead_gen_agent = LeadGenerationAgent()
    
    async def trigger_nurturing_workflow(self, lead: Lead, assessment: Optional[Assessment] = None) -> bool:
        """Trigger appropriate nurturing workflow based on lead segment"""
        try:
            # Determine workflow based on lead segment
            if lead.readiness_segment == "cold" or lead.needs_nurturing():
                return await self._trigger_cold_lead_nurturing(lead, assessment)
            elif lead.readiness_segment == "warm" or lead.is_co_creator_qualified():
                return await self._trigger_warm_lead_nurturing(lead, assessment)
            elif lead.readiness_segment == "hot" or lead.is_priority_lead():
                return await self._trigger_hot_lead_nurturing(lead, assessment)
            else:
                # Default nurturing for unscored leads
                return await self._trigger_default_nurturing(lead, assessment)
                
        except Exception as e:
            logger.error(f"Failed to trigger nurturing workflow for lead {lead.id}: {e}")
            return False
    
    async def _trigger_cold_lead_nurturing(self, lead: Lead, assessment: Optional[Assessment] = None) -> bool:
        """Nurture cold leads with educational content and CRM strategy guides"""
        try:
            # Track nurturing initiation
            await self.analytics.track_conversion_event(
                lead_id=lead.id,
                conversion_type="nurturing_started",
                segment="cold",
                workflow_type="educational"
            )
            
            # Create nurturing campaign
            campaign_data = {
                "name": f"Cold Lead Nurturing - {lead.full_name}",
                "description": f"Educational nurturing sequence for cold lead with {lead.current_crm_system or 'unknown'} CRM",
                "campaign_type": "lead_generation",
                "target_audience": {
                    "lead_id": lead.id,
                    "segment": "cold",
                    "crm_system": lead.current_crm_system,
                    "readiness_score": lead.crm_integration_readiness
                },
                "content_requirements": {
                    "content_types": ["crm_strategy_guide", "automation_basics", "integration_overview"],
                    "crm_focus": lead.current_crm_system or "general",
                    "personalization_level": "basic"
                },
                "agent_sequence": ["content_creator", "communication"]
            }
            
            # Generate educational content
            content_requests = [
                {
                    "type": "crm_strategy_guide",
                    "title": f"CRM Strategy Guide for {lead.current_crm_system or 'Your Business'}",
                    "focus": "foundation_building",
                    "crm_system": lead.current_crm_system,
                    "business_context": {
                        "company": lead.company,
                        "industry": lead.industry,
                        "size": lead.company_size
                    }
                },
                {
                    "type": "automation_basics",
                    "title": "Marketing Automation Fundamentals",
                    "focus": "getting_started",
                    "pain_points": lead.pain_points or []
                }
            ]
            
            # Create content using content creator agent
            generated_content = []
            for content_req in content_requests:
                try:
                    content = await self.content_creator.create_educational_content(content_req)
                    if content:
                        generated_content.append(content)
                except Exception as e:
                    logger.warning(f"Failed to generate content for cold lead {lead.id}: {e}")
            
            # Schedule communication sequence
            communication_sequence = [
                {
                    "delay_hours": 1,
                    "type": "welcome_email",
                    "subject": "Your CRM Integration Strategy Guide is Ready",
                    "content_type": "educational",
                    "attachments": generated_content[:1] if generated_content else []
                },
                {
                    "delay_hours": 72,  # 3 days
                    "type": "follow_up_email",
                    "subject": "Building Your Marketing Automation Foundation",
                    "content_type": "educational",
                    "attachments": generated_content[1:] if len(generated_content) > 1 else []
                },
                {
                    "delay_hours": 168,  # 1 week
                    "type": "consultation_offer",
                    "subject": "Ready to Take the Next Step?",
                    "content_type": "consultation_offer",
                    "cta": "Schedule Free CRM Consultation"
                }
            ]
            
            # Execute communication sequence
            for comm in communication_sequence:
                try:
                    await self._schedule_communication(lead, comm)
                except Exception as e:
                    logger.warning(f"Failed to schedule communication for cold lead {lead.id}: {e}")
            
            # Update lead status
            lead.add_tag("nurturing_cold")
            lead.add_tag("educational_sequence")
            self.db.commit()
            
            logger.info(f"Started cold lead nurturing for lead {lead.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger cold lead nurturing: {e}")
            return False
    
    async def _trigger_warm_lead_nurturing(self, lead: Lead, assessment: Optional[Assessment] = None) -> bool:
        """Nurture warm leads with co-creator program presentation"""
        try:
            # Track nurturing initiation
            await self.analytics.track_conversion_event(
                lead_id=lead.id,
                conversion_type="nurturing_started",
                segment="warm",
                workflow_type="co_creator_qualification"
            )
            
            # Create personalized content based on assessment
            assessment_insights = []
            if assessment:
                assessment_insights = [
                    f"Your {assessment.current_crm} setup shows strong potential",
                    f"Integration readiness score: {assessment.overall_score:.0f}%",
                    "You're qualified for our Co-Creator Program"
                ]
            
            # Generate co-creator program presentation
            co_creator_content = await self.content_creator.create_co_creator_presentation({
                "lead_name": lead.full_name,
                "company": lead.company,
                "current_crm": lead.current_crm_system,
                "readiness_score": lead.crm_integration_readiness,
                "assessment_insights": assessment_insights,
                "integration_opportunities": lead.automation_goals or []
            })
            
            # Communication sequence for warm leads
            communication_sequence = [
                {
                    "delay_hours": 0.5,  # 30 minutes
                    "type": "assessment_results",
                    "subject": f"Your AI Readiness Results: {lead.crm_integration_readiness:.0f}% Ready",
                    "content_type": "personalized_results",
                    "assessment_data": assessment.to_dict() if assessment else None
                },
                {
                    "delay_hours": 24,
                    "type": "co_creator_invitation",
                    "subject": "Exclusive Invitation: Join Our Co-Creator Program",
                    "content_type": "co_creator_program",
                    "attachments": [co_creator_content] if co_creator_content else [],
                    "cta": "Join Co-Creator Program ($497)"
                },
                {
                    "delay_hours": 96,  # 4 days
                    "type": "urgency_reminder",
                    "subject": "Limited Seats Remaining - Co-Creator Program",
                    "content_type": "urgency",
                    "cta": "Secure Your Spot Now"
                }
            ]
            
            # Execute communication sequence
            for comm in communication_sequence:
                try:
                    await self._schedule_communication(lead, comm)
                except Exception as e:
                    logger.warning(f"Failed to schedule communication for warm lead {lead.id}: {e}")
            
            # Update lead status
            lead.add_tag("nurturing_warm")
            lead.add_tag("co_creator_qualified")
            self.db.commit()
            
            logger.info(f"Started warm lead nurturing for lead {lead.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger warm lead nurturing: {e}")
            return False
    
    async def _trigger_hot_lead_nurturing(self, lead: Lead, assessment: Optional[Assessment] = None) -> bool:
        """Nurture hot leads with priority demo and partnership opportunities"""
        try:
            # Track nurturing initiation
            await self.analytics.track_conversion_event(
                lead_id=lead.id,
                conversion_type="nurturing_started",
                segment="hot",
                workflow_type="priority_engagement"
            )
            
            # Generate personalized partnership proposal
            partnership_content = await self.content_creator.create_partnership_proposal({
                "lead_name": lead.full_name,
                "company": lead.company,
                "current_crm": lead.current_crm_system,
                "readiness_score": lead.crm_integration_readiness,
                "business_context": {
                    "industry": lead.industry,
                    "company_size": lead.company_size,
                    "monthly_leads": lead.monthly_lead_volume
                },
                "integration_opportunities": lead.automation_goals or []
            })
            
            # Priority communication sequence
            communication_sequence = [
                {
                    "delay_hours": 0.25,  # 15 minutes
                    "type": "priority_alert",
                    "subject": f"Priority Lead Alert: {lead.crm_integration_readiness:.0f}% AI Ready",
                    "content_type": "internal_alert",
                    "recipient": "founder",
                    "priority": "high"
                },
                {
                    "delay_hours": 1,
                    "type": "founder_introduction",
                    "subject": "Personal Introduction from Our Founder",
                    "content_type": "founder_personal",
                    "sender": "founder",
                    "cta": "Book Priority Demo Call"
                },
                {
                    "delay_hours": 24,
                    "type": "partnership_proposal",
                    "subject": "Exclusive Partnership Opportunity",
                    "content_type": "partnership",
                    "attachments": [partnership_content] if partnership_content else [],
                    "cta": "Discuss Partnership"
                }
            ]
            
            # Execute communication sequence
            for comm in communication_sequence:
                try:
                    await self._schedule_communication(lead, comm)
                except Exception as e:
                    logger.warning(f"Failed to schedule communication for hot lead {lead.id}: {e}")
            
            # Update lead status
            lead.add_tag("nurturing_hot")
            lead.add_tag("priority_lead")
            lead.add_tag("partnership_candidate")
            self.db.commit()
            
            logger.info(f"Started hot lead nurturing for lead {lead.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger hot lead nurturing: {e}")
            return False
    
    async def _trigger_default_nurturing(self, lead: Lead, assessment: Optional[Assessment] = None) -> bool:
        """Default nurturing for unscored leads"""
        try:
            # Basic welcome sequence
            communication_sequence = [
                {
                    "delay_hours": 1,
                    "type": "welcome_email",
                    "subject": "Welcome to Unitasa - Your AI Marketing Journey Begins",
                    "content_type": "welcome",
                    "cta": "Complete Your AI Readiness Assessment"
                },
                {
                    "delay_hours": 48,
                    "type": "assessment_reminder",
                    "subject": "Discover Your AI Marketing Potential",
                    "content_type": "assessment_reminder",
                    "cta": "Take 5-Minute Assessment"
                }
            ]
            
            # Execute communication sequence
            for comm in communication_sequence:
                try:
                    await self._schedule_communication(lead, comm)
                except Exception as e:
                    logger.warning(f"Failed to schedule communication for lead {lead.id}: {e}")
            
            # Update lead status
            lead.add_tag("nurturing_default")
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger default nurturing: {e}")
            return False
    
    async def _schedule_communication(self, lead: Lead, communication_config: Dict[str, Any]) -> bool:
        """Schedule a communication using the communication agent"""
        try:
            # Calculate send time
            send_time = datetime.utcnow() + timedelta(hours=communication_config["delay_hours"])
            
            # Prepare communication data
            comm_data = {
                "recipient": {
                    "email": lead.email,
                    "name": lead.full_name,
                    "company": lead.company
                },
                "message": {
                    "type": communication_config["type"],
                    "subject": communication_config["subject"],
                    "content_type": communication_config["content_type"],
                    "personalization": {
                        "lead_id": lead.id,
                        "crm_system": lead.current_crm_system,
                        "readiness_score": lead.crm_integration_readiness,
                        "segment": lead.readiness_segment
                    }
                },
                "schedule": {
                    "send_at": send_time.isoformat(),
                    "timezone": "UTC"
                },
                "tracking": {
                    "campaign_type": "landing_page_nurturing",
                    "lead_segment": lead.readiness_segment,
                    "workflow_stage": communication_config["type"]
                }
            }
            
            # Add CTA if specified
            if "cta" in communication_config:
                comm_data["message"]["cta"] = communication_config["cta"]
            
            # Add attachments if specified
            if "attachments" in communication_config:
                comm_data["message"]["attachments"] = communication_config["attachments"]
            
            # Schedule with communication agent
            result = await self.communication_agent.schedule_communication(comm_data)
            
            if result:
                # Track communication scheduling
                await self.analytics.track_conversion_event(
                    lead_id=lead.id,
                    conversion_type="communication_scheduled",
                    communication_type=communication_config["type"],
                    delay_hours=communication_config["delay_hours"]
                )
                
                logger.info(f"Scheduled {communication_config['type']} for lead {lead.id}")
                return True
            else:
                logger.warning(f"Failed to schedule {communication_config['type']} for lead {lead.id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to schedule communication: {e}")
            return False
    
    async def handle_assessment_completion(self, assessment: Assessment) -> bool:
        """Handle assessment completion and trigger appropriate workflows"""
        try:
            lead = assessment.lead
            if not lead:
                logger.warning(f"No lead found for assessment {assessment.id}")
                return False
            
            # Update lead with assessment data
            factor_scores = assessment.category_scores or {}
            lead.update_assessment_data(
                assessment_data=assessment.responses or {},
                factor_scores=factor_scores,
                segment=assessment.segment,
                confidence=assessment.overall_score / 100.0
            )
            
            # Track assessment completion
            await self.analytics.track_assessment_completion(assessment)
            
            # Trigger appropriate nurturing workflow
            success = await self.trigger_nurturing_workflow(lead, assessment)
            
            if success:
                self.db.commit()
                logger.info(f"Handled assessment completion for lead {lead.id}")
            else:
                self.db.rollback()
                logger.error(f"Failed to handle assessment completion for lead {lead.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to handle assessment completion: {e}")
            self.db.rollback()
            return False
    
    async def update_lead_engagement_score(self, lead_id: int, engagement_data: Dict[str, Any]) -> bool:
        """Update lead engagement score based on interactions"""
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return False
            
            # Calculate engagement boost based on activities
            engagement_boost = 0.0
            
            # Email engagement
            if engagement_data.get("email_opened"):
                engagement_boost += 5.0
            if engagement_data.get("email_clicked"):
                engagement_boost += 10.0
            
            # Content engagement
            if engagement_data.get("content_downloaded"):
                engagement_boost += 15.0
            if engagement_data.get("demo_requested"):
                engagement_boost += 25.0
            
            # CRM integration interest
            if engagement_data.get("crm_demo_viewed"):
                engagement_boost += 20.0
            if engagement_data.get("integration_guide_accessed"):
                engagement_boost += 15.0
            
            # Update lead score
            new_score = min(100.0, lead.crm_integration_readiness + engagement_boost)
            lead.crm_integration_readiness = new_score
            
            # Re-evaluate segment if score changed significantly
            if engagement_boost >= 10.0:
                old_segment = lead.readiness_segment
                
                if new_score >= 71:
                    lead.readiness_segment = "hot"
                elif new_score >= 41:
                    lead.readiness_segment = "warm"
                else:
                    lead.readiness_segment = "cold"
                
                # If segment changed, trigger new workflow
                if old_segment != lead.readiness_segment:
                    await self.trigger_nurturing_workflow(lead)
            
            # Track engagement update
            await self.analytics.track_conversion_event(
                lead_id=lead_id,
                conversion_type="engagement_updated",
                engagement_boost=engagement_boost,
                new_score=new_score,
                segment_change=old_segment != lead.readiness_segment if 'old_segment' in locals() else False
            )
            
            self.db.commit()
            logger.info(f"Updated engagement score for lead {lead_id}: +{engagement_boost} points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lead engagement score: {e}")
            self.db.rollback()
            return False
