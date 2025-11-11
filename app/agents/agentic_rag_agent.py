"""
Agentic RAG Agent - Full agentic capabilities with tool use and reasoning
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Note: Not inheriting from BaseAgent to avoid abstract method requirements
# This agent has a different interface focused on conversational AI
from app.agents.tools import get_tool_registry
from app.agents.reasoning import (
    get_reasoning_engine,
    get_query_decomposer,
    get_reflection_engine,
    ReasoningTrace
)
from app.rag.lcel_chains import get_confidence_rag_chain
from app.core.crm_knowledge_base import get_crm_knowledge_base
from app.llm.router import get_optimal_llm

logger = logging.getLogger(__name__)


class AgenticRAGAgent:
    """
    Full agentic RAG agent with tool use, reasoning, and iterative refinement

    Capabilities:
    ✅ Intent-based routing
    ✅ Multi-source knowledge (structured + RAG)
    ✅ Context accumulation
    ✅ Action-taking (handoff decisions)
    ✅ Qualification signal extraction
    ✅ Tool use / function calling
    ✅ Multi-step reasoning (ReAct loop)
    ✅ Query decomposition
    ✅ Self-reflection
    ✅ Iterative refinement
    """

    def __init__(self):
        super().__init__()
        self.agent_id = f"agentic_rag_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Core components
        # Use a simple LLM instance to avoid router initialization issues
        from langchain_openai import ChatOpenAI
        from app.core.config import get_settings
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai.model,
            temperature=0.1,  # Lower temperature for reasoning
            max_tokens=2000,  # Reasonable limit for reasoning
            openai_api_key=settings.openai.api_key
        )
        self.tool_registry = get_tool_registry()
        self.reasoning_engine = get_reasoning_engine()
        self.query_decomposer = get_query_decomposer()
        self.reflection_engine = get_reflection_engine()

        # Knowledge sources (lazy loaded)
        self._rag_chain = None
        self._crm_kb = None

    @property
    def rag_chain(self):
        """Lazy load RAG chain"""
        if self._rag_chain is None:
            # Use simple RAG for now to avoid initialization issues
            from app.rag.simple_rag import get_simple_rag_chain
            self._rag_chain = get_simple_rag_chain()
        return self._rag_chain

    @property
    def crm_kb(self):
        """Lazy load CRM knowledge base"""
        if self._crm_kb is None:
            from app.core.crm_knowledge_base import get_crm_knowledge_base
            self._crm_kb = get_crm_knowledge_base()
        return self._crm_kb

        # State management
        self.conversation_contexts: Dict[str, Dict[str, Any]] = {}
        self.active_reasoning_traces: Dict[str, ReasoningTrace] = {}

        logger.info(f"Initialized AgenticRAGAgent: {self.agent_id}")

    async def process_message(self, session_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user message with full agentic capabilities

        Args:
            session_id: Conversation session ID
            message: User message
            context: Additional context

        Returns:
            Response with agentic processing results
        """
        if context is None:
            context = {}

        try:
            # Initialize or get conversation context
            conv_context = self._get_conversation_context(session_id)

            # Update conversation history
            conv_context["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Step 1: Intent detection and routing
            intent = await self._detect_intent(message, conv_context)

            # Step 2: Query decomposition (if needed)
            sub_queries = await self.query_decomposer.decompose_query(message)

            responses = []
            reasoning_traces = []

            # Step 3: Process each sub-query with agentic reasoning
            for i, sub_query in enumerate(sub_queries):
                logger.info(f"Processing sub-query {i+1}/{len(sub_queries)}: {sub_query}")

                # Agentic reasoning for each sub-query
                reasoning_context = {
                    "conversation_history": self._format_conversation_history(conv_context),
                    "user_info": conv_context.get("user_info", {}),
                    "intent": intent,
                    "sub_query_index": i,
                    "total_sub_queries": len(sub_queries)
                }

                trace = await self.reasoning_engine.reason_and_act(sub_query, reasoning_context)
                reasoning_traces.append(trace)

                # Generate response for this sub-query
                if trace.final_answer:
                    responses.append(trace.final_answer)
                else:
                    responses.append(f"I wasn't able to find a definitive answer for: {sub_query}")

            # Step 4: Combine responses from sub-queries
            combined_response = await self._combine_sub_query_responses(message, responses, reasoning_traces)

            # Step 5: Self-reflection and iterative refinement
            reflection = await self.reflection_engine.reflect_on_answer(message, combined_response, reasoning_traces[0])

            # Step 6: Determine actions (qualification, handoff, etc.)
            actions = await self._determine_actions(message, combined_response, conv_context, reflection)

            # Step 7: Update conversation context
            conv_context["messages"].append({
                "role": "assistant",
                "content": combined_response,
                "timestamp": datetime.utcnow().isoformat(),
                "reasoning_traces": [trace.to_dict() for trace in reasoning_traces],
                "reflection": reflection,
                "actions": actions
            })

            # Update qualification and other metrics
            await self._update_conversation_metrics(session_id, conv_context, reflection, actions)

            # Prepare final response
            response_data = {
                "response": combined_response,
                "confidence": reflection.get("quality_score", 0.5),
                "reasoning_steps": len(reasoning_traces[0].steps) if reasoning_traces else 0,
                "tools_used": self._extract_tools_used(reasoning_traces),
                "actions": actions,
                "metadata": {
                    "agent_id": self.agent_id,
                    "session_id": session_id,
                    "sub_queries_processed": len(sub_queries),
                    "processing_time": sum(trace.get_duration() for trace in reasoning_traces),
                    "reflection_score": reflection.get("quality_score", 0.0)
                }
            }

            # Store reasoning traces for debugging/analysis
            self.active_reasoning_traces[session_id] = reasoning_traces[0]

            return response_data

        except Exception as e:
            logger.error(f"Agentic processing failed: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again.",
                "confidence": 0.0,
                "error": str(e),
                "actions": []
            }

    async def _detect_intent(self, message: str, context: Dict[str, Any]) -> str:
        """Detect user intent from message"""
        # Simple intent detection - could be enhanced with ML model
        message_lower = message.lower()

        if any(word in message_lower for word in ["integrate", "connect", "setup", "install"]):
            return "integration_help"
        elif any(word in message_lower for word in ["compare", "vs", "versus", "difference"]):
            return "comparison"
        elif any(word in message_lower for word in ["cost", "price", "pricing", "budget"]):
            return "pricing_inquiry"
        elif any(word in message_lower for word in ["feature", "capability", "can it"]):
            return "feature_inquiry"
        elif any(word in message_lower for word in ["roi", "return", "calculate", "cac"]):
            return "calculation_request"
        else:
            return "general_inquiry"

    async def _combine_sub_query_responses(self, original_query: str, responses: List[str], traces: List[ReasoningTrace]) -> str:
        """Combine responses from multiple sub-queries into coherent answer"""
        if len(responses) == 1:
            return responses[0]

        # Use LLM to combine responses
        combine_prompt = f"""Combine these responses into a single, coherent answer to the original query:

Original Query: {original_query}

Individual Responses:
{chr(10).join(f"{i+1}. {response}" for i, response in enumerate(responses))}

Provide a unified answer that flows naturally and covers all aspects of the query."""

        try:
            response = await self.llm.ainvoke(combine_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Response combination failed: {e}")
            return " ".join(responses)  # Fallback to concatenation

    async def _determine_actions(self, message: str, response: str, context: Dict[str, Any], reflection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine actions to take based on conversation state"""
        actions = []

        # Check for handoff conditions
        confidence = reflection.get("quality_score", 0.0)
        qualification_score = context.get("qualification_score", 0)

        if confidence < 0.4:
            actions.append({
                "type": "handoff",
                "reason": "Low confidence in answer",
                "priority": "high"
            })

        if qualification_score > 75:
            actions.append({
                "type": "sales_handoff",
                "reason": "High qualification score - potential sale",
                "priority": "high"
            })

        # Check for follow-up suggestions
        if "compare" in message.lower() or "vs" in message.lower():
            actions.append({
                "type": "suggest_demo",
                "reason": "Comparison query indicates evaluation interest",
                "priority": "medium"
            })

        # Check for clarification needs
        weaknesses = reflection.get("weaknesses", [])
        if any("unclear" in w.lower() or "missing" in w.lower() for w in weaknesses):
            actions.append({
                "type": "request_clarification",
                "reason": "Answer may be incomplete or unclear",
                "priority": "medium"
            })

        return actions

    def _get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get or initialize conversation context"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = {
                "session_id": session_id,
                "start_time": datetime.utcnow(),
                "messages": [],
                "qualification_score": 0,
                "identified_crm": None,
                "user_info": {},
                "tools_used": [],
                "total_reasoning_steps": 0
            }

        return self.conversation_contexts[session_id]

    def _format_conversation_history(self, context: Dict[str, Any]) -> str:
        """Format conversation history for context"""
        messages = context.get("messages", [])
        if len(messages) <= 1:  # Only current message
            return ""

        # Format last few messages
        recent_messages = messages[-6:]  # Last 3 exchanges
        formatted = []
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)

    async def _update_conversation_metrics(self, session_id: str, context: Dict[str, Any], reflection: Dict[str, Any], actions: List[Dict[str, Any]]):
        """Update conversation metrics based on interaction"""
        # Update qualification score based on content
        last_message = context["messages"][-2]["content"] if len(context["messages"]) >= 2 else ""
        last_response = context["messages"][-1]["content"]

        # Simple qualification scoring
        qual_indicators = ["budget", "timeline", "decision", "purchase", "contract", "pricing"]
        qual_score = sum(1 for indicator in qual_indicators if indicator in last_message.lower())

        context["qualification_score"] = min(100, context.get("qualification_score", 0) + qual_score * 5)

        # Track tools used
        tools_used = self._extract_tools_used(context.get("reasoning_traces", []))
        context["tools_used"].extend(tools_used)

        # Update total reasoning steps
        context["total_reasoning_steps"] = sum(
            len(trace.get("steps", [])) for trace in context.get("reasoning_traces", [])
        )

    def _extract_tools_used(self, traces: List[Any]) -> List[str]:
        """Extract tool names used from reasoning traces"""
        tools = []
        for trace in traces:
            if isinstance(trace, ReasoningTrace):
                for step in trace.steps:
                    if step.tool_name:
                        tools.append(step.tool_name)
            elif isinstance(trace, dict):
                for step in trace.get("steps", []):
                    if step.get("tool_name"):
                        tools.append(step["tool_name"])

        return list(set(tools))  # Remove duplicates

    async def get_reasoning_trace(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get reasoning trace for debugging/analysis"""
        trace = self.active_reasoning_traces.get(session_id)
        return trace.to_dict() if trace else None

    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation"""
        context = self.conversation_contexts.get(session_id)
        if not context:
            return {"error": "Conversation not found"}

        return {
            "session_id": session_id,
            "duration_minutes": (datetime.utcnow() - context["start_time"]).total_seconds() / 60,
            "message_count": len(context["messages"]),
            "qualification_score": context.get("qualification_score", 0),
            "tools_used": list(set(context.get("tools_used", []))),
            "total_reasoning_steps": context.get("total_reasoning_steps", 0),
            "identified_crm": context.get("identified_crm")
        }

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        total_conversations = len(self.conversation_contexts)
        total_messages = sum(len(ctx["messages"]) for ctx in self.conversation_contexts.values())
        total_tools_used = sum(len(ctx.get("tools_used", [])) for ctx in self.conversation_contexts.values())
        avg_qualification = sum(ctx.get("qualification_score", 0) for ctx in self.conversation_contexts.values()) / max(total_conversations, 1)

        return {
            "agent_id": self.agent_id,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_tools_used": total_tools_used,
            "average_qualification_score": round(avg_qualification, 2),
            "active_reasoning_traces": len(self.active_reasoning_traces)
        }


# Global agent instance
_agentic_rag_agent = None

def get_agentic_rag_agent() -> AgenticRAGAgent:
    """Get the global agentic RAG agent instance"""
    global _agentic_rag_agent
    if _agentic_rag_agent is None:
        _agentic_rag_agent = AgenticRAGAgent()
    return _agentic_rag_agent