"""
Co-Creator Onboarding Workflow Service
Handles exclusive onboarding sequence for co-creators using existing agent system
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.co_creator_program import CoCreator
from app.models.user import User
from app.models.lead import Lead
from app.agents.stubs import get_communicator, AgentMessage, get_orchestrator
from app.core.email_service import EmailService
from app.core.config import get_settings

settings = get_settings()


class CoCreatorOnboardingService:
    """Service for managing co-creator onboarding workflows"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.email_service = EmailService()
        self.communicator = get_communicator()
        self.orchestrator = get_orchestrator()
    
    async def start_onboarding_workflow(
        self,
        co_creator_id: int
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Start the complete onboarding workflow for a new co-creator
        Returns: (success, message, workflow_data)
        """
        try:
            # Get co-creator details
            co_creator = self.db.query(CoCreator).filter(CoCreator.id == co_creator_id).first()
            if not co_creator:
                return False, "Co-creator not found", None
            
            if co_creator.status != "active":
                return False, "Co-creator must be active to start onboarding", None
            
            # Initialize onboarding workflow data
            workflow_data = {
                "co_creator_id": co_creator_id,
                "workflow_id": f"onboarding_{co_creator_id}_{datetime.utcnow().timestamp()}",
                "started_at": datetime.utcnow().isoformat(),
                "steps": [],
                "current_step": 0,
                "status": "in_progress"
            }
            
            # Step 1: Provision lifetime access
            step1_success, step1_message = await self._provision_lifetime_access(co_creator)
            workflow_data["steps"].append({
                "step": 1,
                "name": "provision_lifetime_access",
                "status": "completed" if step1_success else "failed",
                "message": step1_message,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            if not step1_success:
                workflow_data["status"] = "failed"
                return False, f"Step 1 failed: {step1_message}", workflow_data
            
            # Step 2: Activate integration support
            step2_success, step2_message = await self._activate_integration_support(co_creator)
            workflow_data["steps"].append({
                "step": 2,
                "name": "activate_integration_support",
                "status": "completed" if step2_success else "failed",
                "message": step2_message,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            if not step2_success:
                workflow_data["status"] = "failed"
                return False, f"Step 2 failed: {step2_message}", workflow_data
            
            # Step 3: Send welcome communications
            step3_success, step3_message = await self._send_welcome_communications(co_creator)
            workflow_data["steps"].append({
                "step": 3,
                "name": "send_welcome_communications",
                "status": "completed" if step3_success else "failed",
                "message": step3_message,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            # Step 4: Set up platform access and privileges
            step4_success, step4_message = await self._setup_platform_privileges(co_creator)
            workflow_data["steps"].append({
                "step": 4,
                "name": "setup_platform_privileges",
                "status": "completed" if step4_success else "failed",
                "message": step4_message,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            # Step 5: Schedule founder engagement
            step5_success, step5_message = await self._schedule_founder_engagement(co_creator)
            workflow_data["steps"].append({
                "step": 5,
                "name": "schedule_founder_engagement",
                "status": "completed" if step5_success else "failed",
                "message": step5_message,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            # Complete workflow
            workflow_data["status"] = "completed"
            workflow_data["completed_at"] = datetime.utcnow().isoformat()
            workflow_data["current_step"] = len(workflow_data["steps"])
            
            # Update co-creator record with onboarding completion
            co_creator.add_metadata("onboarding_completed", True)
            co_creator.add_metadata("onboarding_completed_at", datetime.utcnow().isoformat())
            co_creator.add_metadata("onboarding_workflow_id", workflow_data["workflow_id"])
            
            self.db.commit()
            
            return True, "Onboarding workflow completed successfully", workflow_data
            
        except Exception as e:
            self.db.rollback()
            return False, f"Onboarding workflow failed: {str(e)}", None
    
    async def _provision_lifetime_access(self, co_creator: CoCreator) -> Tuple[bool, str]:
        """Provision lifetime access in User model"""
        try:
            if co_creator.user:
                # Update user with lifetime access
                co_creator.user.lifetime_access = True
                co_creator.user.is_co_creator = True
                co_creator.user.co_creator_joined_at = datetime.utcnow()
                co_creator.user.co_creator_seat_number = co_creator.seat_number
                co_creator.user.subscription_tier = "co_creator"  # Special tier
                co_creator.user.monthly_request_limit = 10000  # Higher limit for co-creators
                
                # Add co-creator benefits
                benefits = [
                    "Lifetime platform access",
                    "Priority integration support",
                    "Direct founder engagement",
                    "Feature influence and voting",
                    "Exclusive co-creator badge",
                    "Early access to new features"
                ]
                co_creator.user.co_creator_benefits = ", ".join(benefits)
                
                self.db.commit()
                return True, "Lifetime access provisioned successfully"
            else:
                return False, "No user associated with co-creator"
                
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to provision lifetime access: {str(e)}"
    
    async def _activate_integration_support(self, co_creator: CoCreator) -> Tuple[bool, str]:
        """Activate integration support workflow using existing agent system"""
        try:
            # Create integration support campaign for this co-creator
            integration_campaign = {
                "name": f"Co-Creator Integration Support - Seat #{co_creator.seat_number}",
                "type": "co_creator_integration_support",
                "co_creator_id": co_creator.id,
                "target_audience": {
                    "co_creator": True,
                    "seat_number": co_creator.seat_number,
                    "current_crm": co_creator.lead.current_crm_system if co_creator.lead else "unknown"
                },
                "priority": "high",
                "support_level": "white_glove",
                "integration_focus": True,
                "personalized": True
            }
            
            # Send message to orchestrator to start integration support
            message = AgentMessage(
                sender="co_creator_onboarding",
                receiver="orchestrator",
                message_type="task_request",
                payload={
                    "task_type": "co_creator_integration_support",
                    "campaign_config": integration_campaign,
                    "co_creator_id": co_creator.id,
                    "priority": "high"
                }
            )
            
            await self.communicator.send_message(message)
            
            # Update co-creator with integration support status
            co_creator.add_metadata("integration_support_activated", True)
            co_creator.add_metadata("integration_support_level", "white_glove")
            co_creator.add_metadata("integration_campaign_id", integration_campaign.get("name"))
            
            self.db.commit()
            
            return True, "Integration support activated successfully"
            
        except Exception as e:
            return False, f"Failed to activate integration support: {str(e)}"
    
    async def _send_welcome_communications(self, co_creator: CoCreator) -> Tuple[bool, str]:
        """Send welcome communications using existing communication agents"""
        try:
            # Get email for communications
            email = None
            if co_creator.user:
                email = co_creator.user.email
            elif co_creator.lead:
                email = co_creator.lead.email
            
            if not email:
                return False, "No email found for co-creator"
            
            # Send welcome email (already handled in payment processing)
            # Here we send additional onboarding communications
            
            # Create welcome communication campaign
            welcome_campaign = {
                "name": f"Co-Creator Welcome Series - Seat #{co_creator.seat_number}",
                "type": "co_creator_welcome_series",
                "co_creator_id": co_creator.id,
                "target_audience": {
                    "email": email,
                    "co_creator": True,
                    "seat_number": co_creator.seat_number,
                    "personalized": True
                },
                "communication_sequence": [
                    {
                        "type": "welcome_email",
                        "delay_hours": 0,
                        "template": "co_creator_welcome"
                    },
                    {
                        "type": "onboarding_guide",
                        "delay_hours": 24,
                        "template": "co_creator_onboarding_guide"
                    },
                    {
                        "type": "founder_introduction",
                        "delay_hours": 48,
                        "template": "founder_introduction"
                    },
                    {
                        "type": "community_invitation",
                        "delay_hours": 72,
                        "template": "community_invitation"
                    }
                ]
            }
            
            # Send message to communication agent
            message = AgentMessage(
                sender="co_creator_onboarding",
                receiver="communication",
                message_type="task_request",
                payload={
                    "task_type": "co_creator_welcome_series",
                    "campaign_config": welcome_campaign,
                    "co_creator_id": co_creator.id,
                    "email": email
                }
            )
            
            await self.communicator.send_message(message)
            
            # Update co-creator with communication status
            co_creator.add_metadata("welcome_communications_sent", True)
            co_creator.add_metadata("welcome_series_started_at", datetime.utcnow().isoformat())
            
            self.db.commit()
            
            return True, "Welcome communications initiated successfully"
            
        except Exception as e:
            return False, f"Failed to send welcome communications: {str(e)}"
    
    async def _setup_platform_privileges(self, co_creator: CoCreator) -> Tuple[bool, str]:
        """Set up platform access and special privileges"""
        try:
            # Define co-creator privileges
            privileges = [
                "lifetime_access",
                "priority_support",
                "feature_voting",
                "beta_access",
                "founder_calls",
                "community_access",
                "integration_priority",
                "custom_requests"
            ]
            
            # Update co-creator with privileges
            co_creator.special_privileges = privileges
            co_creator.access_level = "co_creator"
            co_creator.supporter_badge = True
            
            # If user exists, update their privileges too
            if co_creator.user:
                co_creator.user.role = "co_creator"  # Special role
                co_creator.user.monthly_request_limit = 10000  # Higher limits
                
                # Add special API access if needed
                if not co_creator.user.api_key:
                    import secrets
                    co_creator.user.api_key = f"cc_{secrets.token_urlsafe(32)}"
            
            # Add to co-creator benefits tracking
            co_creator.custom_benefits = [
                {
                    "benefit": "Platform Privileges",
                    "description": "Full access to all co-creator features and privileges",
                    "activated_at": datetime.utcnow().isoformat()
                }
            ]
            
            self.db.commit()
            
            return True, "Platform privileges configured successfully"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to setup platform privileges: {str(e)}"
    
    async def _schedule_founder_engagement(self, co_creator: CoCreator) -> Tuple[bool, str]:
        """Schedule founder engagement and calls"""
        try:
            # Get contact information
            email = None
            name = "Co-Creator"
            
            if co_creator.user:
                email = co_creator.user.email
                name = co_creator.user.full_name or "Co-Creator"
            elif co_creator.lead:
                email = co_creator.lead.email
                name = co_creator.lead.full_name or "Co-Creator"
            
            if not email:
                return False, "No email found for scheduling"
            
            # Create founder engagement schedule
            engagement_schedule = {
                "co_creator_id": co_creator.id,
                "seat_number": co_creator.seat_number,
                "email": email,
                "name": name,
                "engagement_type": "founder_welcome_call",
                "scheduled_for": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "duration_minutes": 30,
                "agenda": [
                    "Welcome and introduction",
                    "Platform overview and capabilities",
                    "CRM integration planning",
                    "Feature roadmap discussion",
                    "Q&A and next steps"
                ]
            }
            
            # Send scheduling request to communication agent
            message = AgentMessage(
                sender="co_creator_onboarding",
                receiver="communication",
                message_type="task_request",
                payload={
                    "task_type": "schedule_founder_engagement",
                    "engagement_config": engagement_schedule,
                    "co_creator_id": co_creator.id
                }
            )
            
            await self.communicator.send_message(message)
            
            # Update co-creator with engagement scheduling
            co_creator.add_metadata("founder_engagement_scheduled", True)
            co_creator.add_metadata("founder_call_scheduled_for", engagement_schedule["scheduled_for"])
            co_creator.add_metadata("engagement_type", "founder_welcome_call")
            
            self.db.commit()
            
            return True, "Founder engagement scheduled successfully"
            
        except Exception as e:
            return False, f"Failed to schedule founder engagement: {str(e)}"
    
    def get_onboarding_status(self, co_creator_id: int) -> Optional[Dict[str, Any]]:
        """Get onboarding status for a co-creator"""
        try:
            co_creator = self.db.query(CoCreator).filter(CoCreator.id == co_creator_id).first()
            if not co_creator:
                return None
            
            # Check onboarding completion
            onboarding_completed = co_creator.co_creator_metadata.get("onboarding_completed", False) if co_creator.co_creator_metadata else False
            
            status = {
                "co_creator_id": co_creator_id,
                "seat_number": co_creator.seat_number,
                "status": co_creator.status,
                "onboarding_completed": onboarding_completed,
                "lifetime_access": co_creator.lifetime_access,
                "supporter_badge": co_creator.supporter_badge,
                "access_level": co_creator.access_level,
                "days_as_co_creator": co_creator.days_as_co_creator,
                "special_privileges": co_creator.special_privileges or [],
                "custom_benefits": co_creator.custom_benefits or []
            }
            
            # Add metadata if available
            if co_creator.co_creator_metadata:
                status.update({
                    "onboarding_completed_at": co_creator.co_creator_metadata.get("onboarding_completed_at"),
                    "integration_support_activated": co_creator.co_creator_metadata.get("integration_support_activated", False),
                    "welcome_communications_sent": co_creator.co_creator_metadata.get("welcome_communications_sent", False),
                    "founder_engagement_scheduled": co_creator.co_creator_metadata.get("founder_engagement_scheduled", False),
                    "founder_call_scheduled_for": co_creator.co_creator_metadata.get("founder_call_scheduled_for")
                })
            
            return status
            
        except Exception as e:
            return None
    
    async def trigger_co_creator_nurturing(self, co_creator_id: int) -> Tuple[bool, str]:
        """Trigger ongoing nurturing workflow for co-creator"""
        try:
            co_creator = self.db.query(CoCreator).filter(CoCreator.id == co_creator_id).first()
            if not co_creator:
                return False, "Co-creator not found"
            
            # Create nurturing campaign
            nurturing_campaign = {
                "name": f"Co-Creator Nurturing - Seat #{co_creator.seat_number}",
                "type": "co_creator_nurturing",
                "co_creator_id": co_creator.id,
                "target_audience": {
                    "co_creator": True,
                    "seat_number": co_creator.seat_number,
                    "engagement_level": "high"
                },
                "nurturing_sequence": [
                    {
                        "type": "feature_updates",
                        "frequency": "weekly",
                        "personalized": True
                    },
                    {
                        "type": "founder_updates",
                        "frequency": "monthly",
                        "direct_communication": True
                    },
                    {
                        "type": "community_highlights",
                        "frequency": "bi_weekly",
                        "social_proof": True
                    },
                    {
                        "type": "integration_tips",
                        "frequency": "as_needed",
                        "crm_specific": True
                    }
                ]
            }
            
            # Send to orchestrator for ongoing nurturing
            message = AgentMessage(
                sender="co_creator_onboarding",
                receiver="orchestrator",
                message_type="task_request",
                payload={
                    "task_type": "co_creator_nurturing",
                    "campaign_config": nurturing_campaign,
                    "co_creator_id": co_creator.id,
                    "ongoing": True
                }
            )
            
            await self.communicator.send_message(message)
            
            return True, "Co-creator nurturing workflow initiated"
            
        except Exception as e:
            return False, f"Failed to trigger nurturing: {str(e)}"
