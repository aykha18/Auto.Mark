"""
Standalone Chat API endpoints without database dependencies
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel


def generate_contextual_response(user_content: str) -> str:
    """
    Generate comprehensive responses about all aspects of Unitasa platform
    """
    user_content = user_content.lower().strip()
    
    # Greeting responses
    if any(word in user_content for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return "Hello! 👋 I'm Unitasa's AI Marketing Assistant. I'm here to help you discover how our AI Marketing Automation Platform can transform your business with seamless CRM integrations. What would you like to know about Unitasa?"
    
    # Personal questions
    if any(phrase in user_content for phrase in ["how are you", "what's up", "how's it going"]):
        return "I'm doing great, thank you! I'm excited to help you explore Unitasa's AI-powered marketing automation capabilities. We specialize in connecting with your existing CRM (Salesforce, HubSpot, Pipedrive, Zoho, Monday.com) to automate your lead generation 24/7. What specific challenges are you facing with your current marketing setup?"
    
    # What is Unitasa / Platform overview
    if any(phrase in user_content for phrase in ["what is unitasa", "what's unitasa", "tell me about unitasa", "unitasa platform", "what do you do"]):
        return """Unitasa is an AI Marketing Automation Platform that works seamlessly with your existing CRM! 🚀

**Key Features:**
• **Plug-and-Play CRM Integration** - Connect with Salesforce, HubSpot, Pipedrive, Zoho, Monday.com in 2 clicks
• **NeuraCRM Built-in** - Our default AI-powered CRM with advanced automation
• **24/7 Lead Generation** - AI agents that never sleep, constantly nurturing prospects
• **Smart Lead Scoring** - Automatically qualify and prioritize your best prospects
• **Marketing Automation** - Personalized campaigns that adapt to customer behavior

Built by a founder who went from zero to automated lead generation, Unitasa eliminates the frustration of disconnected tools and lost leads. Would you like to take our AI Readiness Assessment to see how we can integrate with your current setup?"""
    
    # CRM Integration questions
    if any(word in user_content for word in ["crm", "integration", "connect", "sync", "salesforce", "hubspot", "pipedrive", "zoho", "monday"]):
        return """🔗 **CRM Integration is our specialty!** We support all major CRMs:

**Supported CRMs:**
• **Salesforce** - Enterprise-grade with advanced automation
• **HubSpot** - Marketing & sales alignment with smart workflows  
• **Pipedrive** - Sales-focused with deal tracking automation
• **Zoho CRM** - All-in-one business suite integration
• **Monday.com** - Project management meets CRM automation
• **NeuraCRM** - Our built-in AI-powered CRM (default option)

**Integration Features:**
✅ 2-click OAuth2 setup (no technical skills needed)
✅ Real-time contact & deal synchronization
✅ Automated lead scoring and qualification
✅ Custom field mapping and workflow triggers
✅ Webhook support for instant updates

**Setup Time:** 5-15 minutes depending on your CRM
**Technical Support:** Full integration assistance included

Which CRM are you currently using? I can show you exactly how Unitasa will integrate with your setup!"""
    
    # Assessment questions
    if any(phrase in user_content for phrase in ["assessment", "test", "quiz", "evaluate", "ready", "score"]):
        return """📊 **AI Business Readiness Assessment - Get Your Personalized Plan!**

**What the assessment evaluates:**
🔍 **Current CRM Setup** - Which system you use and how well it's configured
🔍 **Data Quality** - How clean and organized your customer data is
🔍 **Automation Gaps** - Where you're losing leads or missing opportunities
🔍 **Technical Readiness** - Your team's ability to implement AI solutions
🔍 **Integration Complexity** - How easily we can connect with your current tools

**Takes only 10 questions, 3-5 minutes**

**Your Results Include:**
✅ Readiness Score (0-100%)
✅ Specific integration recommendations for YOUR CRM
✅ Automation opportunities you're missing
✅ Technical requirements and setup complexity
✅ Personalized next steps

**Based on your score:**
• **71-100%** → Priority demo with founder + early adopter program
• **41-70%** → Co-creator program eligibility ($250 lifetime access)
• **0-40%** → Free CRM strategy guide + nurturing sequence

Ready to discover your AI readiness? The assessment is completely free and gives you actionable insights regardless of whether you choose Unitasa!"""
    
    # Co-creator program questions
    if any(phrase in user_content for phrase in ["co-creator", "program", "founding", "lifetime", "$250", "early adopter"]):
        return """🌟 **Co-Creator Program - Shape the Future of AI Marketing!**

**Exclusive Benefits (Only 25 Seats Available):**
🎯 **Lifetime Platform Access** - Never pay monthly fees again
🎯 **Direct Founder Access** - Weekly calls and direct communication
🎯 **Roadmap Influence** - Vote on features and suggest improvements
🎯 **Custom Integration Support** - We'll personally help set up your CRM
🎯 **Early Feature Access** - Get new capabilities before anyone else
🎯 **Supporter Recognition** - Featured as a founding supporter (with permission)

**Investment:** $250 one-time (vs $97/month regular pricing)
**ROI Timeline:** Pays for itself in 3 months
**Commitment:** Help us improve through feedback and testimonials

**Who Qualifies:**
✅ Businesses ready to implement AI marketing automation
✅ Current CRM users looking to enhance their setup
✅ Teams willing to provide feedback and suggestions
✅ Assessment score of 41-70% (warm leads)

This isn't just software access - you're becoming a partner in building the future of AI marketing automation. Your input directly shapes our product development!

Want to check if you qualify? Take our assessment first!"""
    
    # Pricing questions
    if any(word in user_content for word in ["price", "cost", "pricing", "expensive", "cheap", "money", "payment"]):
        return """💰 **Unitasa Pricing - Flexible Options for Every Business**

**🌟 Co-Creator Program (Limited Time)**
• **$250 one-time** → Lifetime access + founder support
• Only 25 seats available
• Includes custom CRM integration setup
• Direct influence on product roadmap
• Best value: Saves $1,164+ annually vs regular pricing

**📈 Regular Pricing (After Co-Creator Program)**
• **Starter:** $47/month - Basic CRM integration + automation
• **Professional:** $97/month - Advanced AI features + multi-CRM
• **Enterprise:** $197/month - Custom integrations + dedicated support

**💡 ROI Calculator:**
• Average customer saves 20+ hours/week on manual tasks
• 40% increase in qualified leads
• 60% improvement in lead response time
• Typical ROI: 300-500% in first year

Ready to transform your marketing ROI? The Co-Creator Program won't last long!"""
    
    # Default response for unmatched queries
    return f"""I'd be happy to help you with that! I can assist you with:

🎯 **Popular Topics:**
• **Platform Overview** - What Unitasa does and how it works
• **CRM Integrations** - Salesforce, HubSpot, Pipedrive, Zoho, Monday.com
• **AI Readiness Assessment** - Free 10-question evaluation
• **Co-Creator Program** - $250 lifetime access (25 seats only)
• **Pricing & Plans** - Flexible options for every business

**Quick Actions:**
• Type "assessment" to start your AI readiness evaluation
• Type "demo" to see Unitasa in action
• Type "pricing" for detailed cost information
• Type "CRM" to learn about integrations

What would you like to explore first? I'm here to provide detailed information about any aspect of Unitasa that interests you!"""

router = APIRouter()


class ChatSessionCreateRequest(BaseModel):
    """Request to create a new chat session"""
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for chat service
    """
    return {
        "status": "healthy",
        "service": "chat_service_standalone",
        "message": "Chat service is operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/initialize")
async def initialize_chat_session(
    request: Optional[ChatSessionCreateRequest] = None,
    http_request: Request = None
) -> Dict[str, Any]:
    """
    Create a new chat session (standalone version)
    """
    try:
        # Generate a simple session ID
        session_id = str(uuid.uuid4())
        
        # Return a basic session response that matches frontend expectations
        response_data = {
            "session_id": session_id,
            "id": session_id,  # Frontend uses session.id for WebSocket URL
            "active": True,  # Frontend expects 'active' boolean instead of 'status'
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "content": "Welcome to Unitasa! I'm here to help you with CRM integrations and marketing automation questions.\n\nTry asking:\n• \"How does Unitasa integrate with Salesforce?\"\n• \"What CRM features do you support?\"\n• \"Help me choose the right integration\"\n• \"Tell me about the co-creator program\"",
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "text"
                }
            ],
            "context": request.context if request and request.context else {},
            "voiceEnabled": True
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.post("/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send a message to the chat (standalone version)
    """
    try:
        user_content = message_data.get("content", "").lower()
        
        # Generate contextual responses based on user input
        response_content = generate_contextual_response(user_content)
        
        response_message = {
            "id": str(uuid.uuid4()),
            "content": response_content,
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text"
        }
        return response_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/{session_id}/message")
async def send_chat_message_fallback(
    session_id: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fallback message endpoint (standalone version)
    """
    try:
        user_content = message_data.get("content", "")
        
        # Generate contextual responses based on user input using the knowledge base
        response_content = generate_contextual_response(user_content)
        
        response_message = {
            "id": str(uuid.uuid4()),
            "content": response_content,
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text"
        }
        return response_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """
    Basic WebSocket endpoint for chat (standalone version)
    """
    await websocket.accept()
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connection established"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            print(f"[WEBSOCKET] Received data: {data}")
            
            if data.get("type") == "message":
                user_content = data.get("content", "").lower()
                
                # Generate contextual responses
                if "hi" in user_content or "hello" in user_content:
                    response_content = "Hello! 👋 I'm Unitasa's AI Marketing Assistant. I'm here to help you transform your marketing operations with AI-powered CRM integrations. What can I help you with today?"
                elif "how are you" in user_content:
                    response_content = "I'm doing great, thank you for asking! I'm ready to help you with CRM integrations, marketing automation, and AI solutions. What specific challenges are you facing with your current marketing setup?"
                elif "crm" in user_content:
                    response_content = "Great question about CRM! Unitasa integrates with major CRM platforms like Salesforce, HubSpot, Pipedrive, and more. We can help automate your lead generation, scoring, and nurturing processes. Which CRM are you currently using?"
                elif "salesforce" in user_content:
                    response_content = "Excellent choice! Unitasa has deep Salesforce integration capabilities. We can help you automate lead capture, scoring, and nurturing directly in Salesforce. Would you like to know about our specific Salesforce features?"
                elif "price" in user_content or "cost" in user_content:
                    response_content = "Our pricing is designed to scale with your business needs. We offer flexible plans starting from basic integrations to enterprise solutions. Would you like me to connect you with our team for a personalized quote?"
                else:
                    response_content = f"Thanks for your message! I'm Unitasa's AI Marketing Assistant. I can help you with CRM integrations, marketing automation, lead generation, and AI readiness assessments. What specific area would you like to explore?"
                
                # Send back a proper chat message
                response_message = {
                    "id": str(uuid.uuid4()),
                    "content": response_content,
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "text"
                }
                print(f"[WEBSOCKET] Sending response: {response_message}")
                await websocket.send_json(response_message)
                
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        })


@router.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """
    Test endpoint to verify chat router is working
    """
    return {
        "success": True,
        "message": "Standalone chat router is working correctly",
        "timestamp": datetime.utcnow().isoformat()
    }