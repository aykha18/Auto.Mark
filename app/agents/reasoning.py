"""
Agentic RAG Reasoning Engine - ReAct loop and multi-step reasoning
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from app.llm.router import get_optimal_llm
from app.agents.tools import get_tool_registry, execute_tool

logger = logging.getLogger(__name__)


class ReasoningAction(Enum):
    """Types of actions the agent can take"""
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    REFLECT = "reflect"
    FINAL_ANSWER = "final_answer"


@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    step_number: int
    action: ReasoningAction
    thought: str
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "step_number": self.step_number,
            "action": self.action.value,
            "thought": self.thought,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ReasoningTrace:
    """Complete trace of reasoning process"""
    query: str
    steps: List[ReasoningStep] = field(default_factory=list)
    final_answer: Optional[str] = None
    confidence: float = 0.0
    success: bool = False
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    def add_step(self, step: ReasoningStep):
        """Add a reasoning step"""
        self.steps.append(step)

    def complete(self, final_answer: str = None, confidence: float = 0.0, success: bool = True, error: str = None):
        """Mark reasoning as complete"""
        self.final_answer = final_answer
        self.confidence = confidence
        self.success = success
        self.error = error
        self.end_time = datetime.utcnow()

    def get_duration(self) -> float:
        """Get total reasoning duration in seconds"""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "query": self.query,
            "steps": [step.to_dict() for step in self.steps],
            "final_answer": self.final_answer,
            "confidence": self.confidence,
            "success": self.success,
            "error": self.error,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration()
        }


class ReActReasoningEngine:
    """
    ReAct (Reasoning + Acting) reasoning engine for agentic RAG

    Follows the ReAct pattern:
    1. Think: Analyze current situation and decide next action
    2. Act: Execute tool or take action
    3. Observe: Process results and update knowledge
    4. Repeat until task is complete
    """

    def __init__(self, max_steps: int = 10, max_tool_calls: int = 5):
        # Use simple LLM to avoid router issues
        from langchain_openai import ChatOpenAI
        from app.core.config import get_settings
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai.model,
            temperature=0.1,
            max_tokens=1500,
            openai_api_key=settings.openai.api_key
        )
        self.tool_registry = get_tool_registry()
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls

    async def reason_and_act(self, query: str, context: Dict[str, Any] = None) -> ReasoningTrace:
        """
        Execute ReAct reasoning loop

        Args:
            query: User query to process
            context: Additional context (conversation history, user info, etc.)

        Returns:
            Complete reasoning trace
        """
        if context is None:
            context = {}

        trace = ReasoningTrace(query=query)
        step_count = 0
        tool_calls = 0

        # Initial context
        current_context = {
            "query": query,
            "available_tools": self.tool_registry.get_available_tools_info(),
            "conversation_context": context.get("conversation_history", ""),
            "user_info": context.get("user_info", {}),
            "previous_steps": []
        }

        try:
            while step_count < self.max_steps:
                step_count += 1

                # Think step
                thought, action, tool_name, tool_input = await self._think_step(current_context, trace)

                # Create reasoning step
                step = ReasoningStep(
                    step_number=step_count,
                    action=ReasoningAction.THINK,
                    thought=thought
                )

                if action == "final_answer":
                    # Final answer reached
                    trace.add_step(step)
                    trace.complete(final_answer=thought, confidence=0.8, success=True)
                    break

                elif action == "tool_call" and tool_name:
                    # Act step - execute tool
                    step.action = ReasoningAction.ACT
                    step.tool_name = tool_name
                    step.tool_input = tool_input

                    # Execute tool
                    tool_result = await self._act_step(tool_name, tool_input)
                    tool_calls += 1

                    # Observe step
                    observation = await self._observe_step(tool_result, current_context)

                    step.observation = observation
                    trace.add_step(step)

                    # Update context with observation
                    current_context["previous_steps"].append({
                        "step": step_count,
                        "tool": tool_name,
                        "input": tool_input,
                        "result": tool_result,
                        "observation": observation
                    })

                    # Check if we should continue or stop
                    if tool_calls >= self.max_tool_calls:
                        # Max tool calls reached, provide summary
                        final_answer = await self._generate_final_answer(current_context, trace)
                        trace.complete(final_answer=final_answer, confidence=0.7, success=True)
                        break

                else:
                    # Invalid action, continue thinking
                    step.observation = f"Invalid action: {action}"
                    trace.add_step(step)

            # Check if we exceeded max steps
            if step_count >= self.max_steps and not trace.final_answer:
                final_answer = await self._generate_final_answer(current_context, trace)
                trace.complete(final_answer=final_answer, confidence=0.5, success=True)

        except Exception as e:
            logger.error(f"ReAct reasoning failed: {e}")
            trace.complete(error=str(e), success=False)

        return trace

    async def _think_step(self, context: Dict[str, Any], trace: ReasoningTrace) -> Tuple[str, str, Optional[str], Optional[Dict]]:
        """
        Think step: Analyze situation and decide next action

        Returns:
            (thought, action, tool_name, tool_input)
        """
        # Build prompt for thinking
        prompt = self._build_think_prompt(context, trace)

        try:
            response = await self.llm.ainvoke(prompt)
            thought_text = response.content if hasattr(response, 'content') else str(response)

            # Parse the response to extract action
            return self._parse_thought_response(thought_text)

        except Exception as e:
            logger.error(f"Think step failed: {e}")
            return "I encountered an error while thinking. Let me try a different approach.", "final_answer", None, None

    async def _act_step(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Act step: Execute the selected tool"""
        try:
            result = execute_tool(tool_name, **tool_input)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    async def _observe_step(self, tool_result: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Observe step: Process and interpret tool results"""
        try:
            # Build observation prompt
            prompt = self._build_observe_prompt(tool_result, context)

            response = await self.llm.ainvoke(prompt)
            observation = response.content if hasattr(response, 'content') else str(response)

            return observation

        except Exception as e:
            logger.error(f"Observe step failed: {e}")
            return f"Tool result: {json.dumps(tool_result, indent=2)}"

    async def _generate_final_answer(self, context: Dict[str, Any], trace: ReasoningTrace) -> str:
        """Generate final answer when reasoning is complete"""
        try:
            prompt = self._build_final_answer_prompt(context, trace)

            response = await self.llm.ainvoke(prompt)
            final_answer = response.content if hasattr(response, 'content') else str(response)

            return final_answer

        except Exception as e:
            logger.error(f"Final answer generation failed: {e}")
            return "I apologize, but I encountered an error while formulating my final answer. Based on the information I've gathered, here's what I can tell you: " + context.get("query", "")

    def _build_think_prompt(self, context: Dict[str, Any], trace: ReasoningTrace) -> str:
        """Build prompt for the thinking step"""
        query = context["query"]
        available_tools = context["available_tools"]
        previous_steps = context["previous_steps"]

        steps_text = ""
        if previous_steps:
            steps_text = "\nPrevious steps taken:\n"
            for step in previous_steps:
                steps_text += f"Step {step['step']}: Used {step['tool']} with input {step['input']}\n"
                steps_text += f"Result: {step['result']}\n"
                steps_text += f"Observation: {step['observation']}\n\n"

        prompt = f"""You are an intelligent assistant that can use tools to help answer questions. Follow this process:

1. Think step-by-step about what you need to do
2. If you need information, choose an appropriate tool to use
3. If you have enough information, provide a final answer

Query: {query}

Available Tools:
{available_tools}

{steps_text}

Now, think about what to do next. Respond in this format:

Thought: [Your reasoning about what to do next]
Action: [tool_call OR final_answer]
Tool: [tool name, if using a tool]
Tool Input: [JSON parameters, if using a tool]

Example:
Thought: I need to look up CRM information to answer this question about HubSpot.
Action: tool_call
Tool: crm_lookup
Tool Input: {{"crm_name": "hubspot", "info_type": "features"}}

Or for final answer:
Thought: I have all the information I need to answer the question.
Action: final_answer"""

        return prompt

    def _build_observe_prompt(self, tool_result: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for the observation step"""
        query = context["query"]

        result_text = json.dumps(tool_result, indent=2)

        prompt = f"""You just executed a tool and received this result:

Tool Result:
{result_text}

Original Query: {query}

Analyze this result and explain what you learned. Consider:
- What useful information was obtained?
- How does this help answer the original query?
- What should be the next step?

Keep your observation concise but informative."""

        return prompt

    def _build_final_answer_prompt(self, context: Dict[str, Any], trace: ReasoningTrace) -> str:
        """Build prompt for generating final answer"""
        query = context["query"]
        previous_steps = context["previous_steps"]

        steps_summary = ""
        if previous_steps:
            steps_summary = "\nTools used and results:\n"
            for step in previous_steps:
                steps_summary += f"- {step['tool']}: {step['observation']}\n"

        prompt = f"""Based on all the information gathered, provide a comprehensive final answer to the query.

Query: {query}

{steps_summary}

Provide a clear, helpful answer that directly addresses the user's question. Include relevant details from the tools used, but keep it conversational and easy to understand."""

        return prompt

    def _parse_thought_response(self, response: str) -> Tuple[str, str, Optional[str], Optional[Dict]]:
        """Parse the LLM response from think step"""
        try:
            lines = response.strip().split('\n')
            thought = ""
            action = "final_answer"
            tool_name = None
            tool_input = None

            for line in lines:
                line = line.strip()
                if line.startswith('Thought:'):
                    thought = line[7:].strip()
                elif line.startswith('Action:'):
                    action = line[7:].strip().lower()
                elif line.startswith('Tool:'):
                    tool_name = line[5:].strip()
                elif line.startswith('Tool Input:'):
                    try:
                        input_str = line[11:].strip()
                        tool_input = json.loads(input_str)
                    except json.JSONDecodeError:
                        tool_input = {}

            return thought, action, tool_name, tool_input

        except Exception as e:
            logger.error(f"Failed to parse thought response: {e}")
            return response, "final_answer", None, None


class QueryDecomposer:
    """Decomposes complex queries into simpler sub-queries"""

    def __init__(self):
        # Use simple LLM to avoid router issues
        from langchain_openai import ChatOpenAI
        from app.core.config import get_settings
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai.model,
            temperature=0.2,
            max_tokens=1000,
            openai_api_key=settings.openai.api_key
        )

    async def decompose_query(self, query: str) -> List[str]:
        """
        Break down complex query into simpler sub-queries

        Args:
            query: Complex user query

        Returns:
            List of simpler sub-queries to answer
        """
        if not self._needs_decomposition(query):
            return [query]

        prompt = f"""Break down this complex query into 2-4 simpler, independent sub-queries that can be answered separately:

Query: {query}

Respond with a JSON array of strings, where each string is a simpler sub-query.

Example:
["What are the key features of HubSpot CRM?", "How much does HubSpot cost?", "How long does setup take?"]

Make sure each sub-query can be answered independently."""

        try:
            response = await self.llm.ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Extract JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                sub_queries = json.loads(json_str)
                return sub_queries if isinstance(sub_queries, list) else [query]

        except Exception as e:
            logger.error(f"Query decomposition failed: {e}")

        return [query]  # Fallback to original query

    def _needs_decomposition(self, query: str) -> bool:
        """Determine if query needs decomposition"""
        indicators = [
            " and ", " or ", " vs ", " compare ", " difference between ",
            " pros and cons ", " advantages ", " vs ", " versus ",
            " how to ", " steps to ", " process for "
        ]

        query_lower = query.lower()
        complexity_score = sum(1 for indicator in indicators if indicator in query_lower)

        # Also check length
        if len(query.split()) > 20:
            complexity_score += 1

        return complexity_score >= 2


class SelfReflectionEngine:
    """Provides self-reflection capabilities for iterative improvement"""

    def __init__(self):
        # Use simple LLM to avoid router issues
        from langchain_openai import ChatOpenAI
        from app.core.config import get_settings
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai.model,
            temperature=0.3,
            max_tokens=800,
            openai_api_key=settings.openai.api_key
        )

    async def reflect_on_answer(self, query: str, answer: str, trace: ReasoningTrace) -> Dict[str, Any]:
        """
        Reflect on the quality of an answer and suggest improvements

        Args:
            query: Original user query
            answer: Generated answer
            trace: Reasoning trace

        Returns:
            Reflection analysis with quality score and suggestions
        """
        prompt = f"""Analyze the quality of this answer and provide constructive feedback:

Query: {query}

Answer: {answer}

Reasoning steps taken: {len(trace.steps)}

Provide analysis in this JSON format:
{{
    "quality_score": 0.0-1.0,
    "strengths": ["list of good aspects"],
    "weaknesses": ["list of issues"],
    "suggestions": ["specific improvements"],
    "confidence_assessment": "explanation of confidence level"
}}

Be critical but constructive. Consider:
- Completeness: Does it fully answer the query?
- Accuracy: Is the information correct?
- Relevance: Is it on-topic?
- Clarity: Is it easy to understand?
- Usefulness: Does it provide actionable information?"""

        try:
            response = await self.llm.ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                reflection = json.loads(json_str)
                return reflection

        except Exception as e:
            logger.error(f"Self-reflection failed: {e}")

        return {
            "quality_score": 0.7,
            "strengths": ["Answer provided"],
            "weaknesses": ["Unable to analyze quality"],
            "suggestions": ["Consider manual review"],
            "confidence_assessment": "Analysis failed, manual review recommended"
        }


# Global instances
_reasoning_engine = None
_query_decomposer = None
_reflection_engine = None

def get_reasoning_engine() -> ReActReasoningEngine:
    """Get global reasoning engine instance"""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReActReasoningEngine()
    return _reasoning_engine

def get_query_decomposer() -> QueryDecomposer:
    """Get global query decomposer instance"""
    global _query_decomposer
    if _query_decomposer is None:
        _query_decomposer = QueryDecomposer()
    return _query_decomposer

def get_reflection_engine() -> SelfReflectionEngine:
    """Get global self-reflection engine instance"""
    global _reflection_engine
    if _reflection_engine is None:
        _reflection_engine = SelfReflectionEngine()
    return _reflection_engine