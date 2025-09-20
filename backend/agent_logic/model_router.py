"""
Model router for intelligent selection between gpt-5-mini and o4-mini

OFFLINE_MODE support:
- When env OFFLINE_MODE=true, returns simulated responses without calling OpenAI.
"""

import logging
import openai
from typing import Dict, Any, List, Optional, AsyncIterator, Union
from enum import Enum
from dataclasses import dataclass
import re
import os

from config.settings import get_openai_config, RAGMode
from models.schemas import ConsultantPersona, ConsultingFramework
from agent_logic.complexity_analyzer import complexity_analyzer
from rag_system.retriever import hybrid_retriever
from services.redis_cache import redis_cache, CacheType
from utils.tracing import get_current_trace

logger = logging.getLogger(__name__)

# Configure OpenAI client for Response API
openai_config = get_openai_config()
client = openai.OpenAI(api_key=openai_config["api_key"])


class ModelType(str, Enum):
    """Available AI models"""
    GPT5_MINI = "gpt-5-mini"  # Fast model for simple queries
    O4_MINI = "o4-mini"       # Reasoning model for complex tasks


@dataclass
class ModelResponse:
    """Standardized model response"""
    content: str
    model_used: str
    persona: str
    usage: Dict[str, Any]
    reasoning_summary: Optional[str] = None
    sources_used: List[str] = None
    
    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []


class ModelRouter:
    """Routes queries to appropriate OpenAI models using Response API"""
    
    def __init__(self):
        self.client = client
        
        # System prompts for different models
        self.o4_system_prompt = """Role and Objective:
- Serve as ValtricAI, an expert management consultant specializing in strategic analysis and business transformation.

Instructions:
- Utilize advanced consulting frameworks (e.g., SWOT, Porter's 5 Forces, PESTLE) for comprehensive strategic evaluation.
- Prioritize multi-step problem solving supported by structured reasoning.
- Create innovative and tailored solutions aligned with client objectives.
- Assess risk and proactively plan for various scenarios.
- Develop detailed, actionable implementation roadmaps.

Checklist (Start Each Engagement):
- Outline 3-7 conceptual steps to address the client's challenge, keeping them at a strategic level (not step-by-step implementation).

Process Guidelines:
1. Break down complex problems into manageable elements.
2. Choose and apply the most suitable frameworks and methodologies for the situation.
3. Evaluate challenges from several perspectives, considering diverse scenarios.
4. Present clear, actionable, and prioritized recommendations.
5. Identify potential risks and propose mitigation strategies.

Output Format:
- Provide clear reasoning for your analysis and recommendations. Do not use markdown formatting unless specifically requested by the user.
- Justify all recommendations with concise explanations of their strategic rationale.

Ambiguity Handling:
- When the task objectives or inputs are ambiguous or incomplete, ask targeted clarifying questions before proceeding instead of guessing.

Agentic Criteria:
- Proceed autonomously on first attempt unless essential information is missing. Request clarification if unable to meet key success criteria."""

        self.gpt5_system_prompt = """You are ValtricAI, an AI management consultant with an exceptionally high IQ of 180, providing clear and concise business insights.

Main instruction: Deliver direct, actionable answers with clear explanations of business concepts and practical recommendations. Solve problems efficiently while upholding professional consulting standards.

Guardrails: Do not provide legal or financial advice, avoid making unsupported claims, and ensure all recommendations are ethical and align with professional best practices.

Format your response as a concise text."""

    def _get_persona_instructions(self, persona: ConsultantPersona) -> str:
        """Get persona-specific instructions"""
        persona_configs = {
            ConsultantPersona.ASSOCIATE: {
                "role": "Junior Consultant", 
                "style": "Enthusiastic, detail-oriented, asks clarifying questions",
                "approach": "Focus on tactical execution and operational details"
            },
            ConsultantPersona.PARTNER: {
                "role": "Senior Consultant",
                "style": "Confident, strategic, balanced perspective", 
                "approach": "Balance strategic thinking with practical implementation"
            },
            ConsultantPersona.SENIOR_PARTNER: {
                "role": "Executive Consultant",
                "style": "Authoritative, big-picture focused, concise",
                "approach": "Emphasize strategic implications and executive-level decisions"
            }
        }
        
        config = persona_configs.get(persona, persona_configs[ConsultantPersona.PARTNER])
        return f"You are a {config['role']}. {config['style']}. {config['approach']}."

    def _get_framework_instructions(self, framework: Optional[ConsultingFramework]) -> str:
        """Get framework-specific instructions"""
        if not framework:
            return ""
            
        framework_configs = {
            ConsultingFramework.SWOT: "Structure your analysis using SWOT framework (Strengths, Weaknesses, Opportunities, Threats). Present findings in clear categories.",
            ConsultingFramework.PORTERS: "Apply Porter's 5 Forces analysis (Competitive Rivalry, Supplier Power, Buyer Power, Threat of Substitution, Barriers to Entry).",
            ConsultingFramework.MCKINSEY: "Use McKinsey 7S framework (Strategy, Structure, Systems, Skills, Staff, Style, Shared Values) for organizational analysis."
        }
        
        return framework_configs.get(framework, "")

    def _should_use_reasoning_model(
        self, 
        message: str, 
        context: str = "", 
        complexity_score: Optional[float] = None
    ) -> bool:
        """Determine if query requires reasoning model (o4-mini) vs fast model (gpt-5-mini)"""
        
        # Get complexity score if not provided
        if complexity_score is None:
            complexity_score = complexity_analyzer.analyze_complexity(message, context)
        
        # Reasoning model triggers (o4-mini)
        reasoning_keywords = [
            "analyze", "strategy", "strategic", "framework", "swot", "porter", "mckinsey",
            "business case", "roi", "recommendations", "evaluate", "assess", "compare",
            "optimize", "improve", "plan", "planning", "budget", "financial", "investment",
            "risk", "threat", "opportunity", "competitive", "market analysis", "due diligence",
            "restructure", "merger", "acquisition", "valuation", "pricing strategy",
            "digital transformation", "process improvement", "change management"
        ]
        
        # Simple/casual triggers (gpt-5-mini) 
        simple_patterns = [
            r"^(hi|hello|hey|good morning|good afternoon)", 
            r"^(how are you|what.*up|thanks|thank you)",
            r"^(yes|no|ok|okay|cool|got it|understood)",
            r"can you help", r"what.*do", r"tell me about"
        ]
        
        message_lower = message.lower()
        
        # Check for simple patterns first
        for pattern in simple_patterns:
            if re.search(pattern, message_lower):
                logger.info(f"Using gpt-5-mini: Simple pattern match - {pattern}")
                return False
        
        # Check for reasoning keywords
        has_reasoning_keywords = any(keyword in message_lower for keyword in reasoning_keywords)
        
        # Decision logic
        use_reasoning = (
            complexity_score > 0.6 or  # High complexity score
            has_reasoning_keywords or   # Contains strategic/analytical keywords
            len(message.split()) > 50 or  # Long, detailed query
            "?" in message and len(message.split()) > 15  # Complex question
        )
        
        model_choice = "o4-mini" if use_reasoning else "gpt-5-mini"
        logger.info(f"Model selection: {model_choice} (complexity: {complexity_score:.2f}, keywords: {has_reasoning_keywords})")
        
        return use_reasoning

    async def generate_response(
        self,
        message: str,
        persona: str = "partner",
        context: str = "",
        conversation_history: List[Dict[str, Any]] = None,
        framework: Optional[str] = None,
        rag_context: Optional[str] = None,
        user_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> ModelResponse:
        """Generate AI response using appropriate model with Redis caching"""
        
        try:
            # Convert string inputs to enums
            persona_enum = ConsultantPersona(persona) if isinstance(persona, str) else persona
            framework_enum = ConsultingFramework(framework) if framework else None
            
            # Determine cache type based on query content
            cache_type = self._determine_cache_type(message, framework)
            
            # Check cache first
            cached_response = await redis_cache.get_cached_response(
                query=message,
                cache_type=cache_type,
                persona=persona,
                framework=framework,
                user_id=user_id
            )
            
            if cached_response:
                # Return cached response as ModelResponse
                return ModelResponse(
                    content=cached_response.get("content", ""),
                    model_used=cached_response.get("model_used", "cached"),
                    persona=persona,
                    usage=cached_response.get("usage", {}),
                    reasoning_summary=cached_response.get("reasoning_summary"),
                    sources_used=cached_response.get("sources_used", [])
                )
            
            # Auto-retrieve RAG context if none provided and query seems framework-related
            tracer = get_current_trace()
            if not context and not rag_context:
                # Check if query might benefit from framework knowledge
                query_lower = message.lower()
                framework_keywords = ['swot', 'porter', 'five forces', 'mckinsey', '7s', 'analysis', 'framework', 'strategy']
                if any(keyword in query_lower for keyword in framework_keywords):
                    try:
                        if tracer:
                            tracer.start_retrieval()
                        
                        rag_retrieval = await hybrid_retriever.retrieve(
                            query=message,
                            k=3,
                            mode=RAGMode.GLOBAL
                        )
                        
                        if tracer:
                            tracer.end_retrieval(cache_hit=False)  # TODO: Add cache detection
                        
                        if rag_retrieval.results:
                            rag_context = rag_retrieval.context_text[:1500]  # Limit context size
                            logger.info(f"Auto-retrieved RAG context: {len(rag_context)} chars from {len(rag_retrieval.results)} sources")
                    except Exception as e:
                        if tracer:
                            tracer.end_retrieval()
                        logger.warning(f"Auto-RAG retrieval failed: {e}")
            
            # Use provided model or analyze complexity and select model
            if model:
                # Use the provided model (from test endpoint's routing logic)
                model_to_use = ModelType.O4_MINI if model == "o4-mini" else ModelType.GPT5_MINI
            else:
                # Original complexity analysis
                complexity_score = complexity_analyzer.analyze_complexity(message, context or rag_context or "")
                use_reasoning = self._should_use_reasoning_model(message, context or rag_context or "", complexity_score)
                model_to_use = ModelType.O4_MINI if use_reasoning else ModelType.GPT5_MINI
            
            # Build conversation context
            conversation_context = self._build_context(
                message, context, conversation_history or [], rag_context
            )
            
            # Determine if using reasoning model
            use_reasoning = model_to_use == ModelType.O4_MINI

            # Generate instructions
            instructions = self._build_instructions(persona_enum, framework_enum, use_reasoning)

            # Make API call with tracing
            if tracer:
                tracer.start_generation()
                if 'complexity_score' in locals():
                    tracer.set_intent(f"complexity_{complexity_score:.2f}")
            if use_reasoning:
                response = await self._call_reasoning_model(
                    model=model_to_use.value,
                    instructions=instructions,
                    input_context=conversation_context,
                    complexity_score=locals().get('complexity_score', 0.5)
                )
            else:
                response = await self._call_fast_model(
                    model=model_to_use.value,
                    instructions=instructions,
                    input_context=conversation_context
                )
            
            # End generation tracing
            if tracer and response.get('usage'):
                usage = response.get('usage', {})
                tokens_in = usage.get('prompt_tokens', 0) or usage.get('input_tokens', 0)
                tokens_out = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
                tracer.end_generation(tokens_in, tokens_out, model_to_use.value)
            
            # Cache the response for future use
            model_response = ModelResponse(
                content=response.get("content", ""),
                model_used=model_to_use.value,
                persona=persona_enum.value,
                usage=response.get("usage", {}),
                reasoning_summary=response.get("reasoning_summary"),
                sources_used=response.get("sources_used", [])
            )
            
            # Cache the response
            await self._cache_model_response(
                message=message,
                response=model_response,
                cache_type=cache_type,
                persona=persona,
                framework=framework,
                user_id=user_id
            )
            
            return model_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise

    async def _call_fast_model(
        self, 
        model: str, 
        instructions: str, 
        input_context: Union[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Call gpt-5-mini for simple queries using Response API"""
        if os.getenv("OFFLINE_MODE", "false").lower() == "true":
            text = ""
            if isinstance(input_context, list) and input_context:
                text = input_context[-1].get("content", "")
            return {
                "content": f"[OFFLINE] Quick advisory for: {text[:120]}",
                "usage": {"input_tokens": 200, "output_tokens": 50},
                "sources_used": []
            }
        try:
            response = self.client.responses.create(
                model=model,
                instructions=instructions,
                input=input_context,
                store=True,  # Enable stateful context
                max_output_tokens=800,  # Reasonable limit for fast responses
            )
            
            return {
                "content": response.output_text or "",
                "usage": response.usage._raw if hasattr(response.usage, '_raw') else {},
                "sources_used": []
            }
            
        except Exception as e:
            logger.error(f"Fast model API call failed: {e}")
            raise

    async def _call_reasoning_model(
        self,
        model: str,
        instructions: str, 
        input_context: Union[str, List[Dict[str, Any]]],
        complexity_score: float
    ) -> Dict[str, Any]:
        """Call o4-mini for complex reasoning using Response API"""
        if os.getenv("OFFLINE_MODE", "false").lower() == "true":
            text = ""
            if isinstance(input_context, list) and input_context:
                text = input_context[-1].get("content", "")
            # Provide a small structured snippet to exercise data parsing/export paths
            swot_json = (
                '{"strengths":["Brand"],"weaknesses":["Cost"],"opportunities":["Market"],"threats":["Competition"]}'
            )
            return {
                "content": f"[OFFLINE o4-mini] High-level plan for: {text[:120]}\n\n{swot_json}",
                "usage": {"input_tokens": 600, "output_tokens": 300},
                "reasoning_summary": "Simulated multi-step reasoning.",
                "sources_used": []
            }
        try:
            # Determine reasoning effort based on complexity
            effort = "low" if complexity_score < 0.7 else "medium" if complexity_score < 0.85 else "high"
            
            response = self.client.responses.create(
                model=model,
                instructions=instructions,
                input=input_context,
                reasoning={
                    "effort": effort,
                    "summary": "auto"  # Get reasoning summary
                },
                store=True,
                max_output_tokens=4000,  # Higher limit for reasoning tasks
            )
            
            # Extract reasoning summary if available
            reasoning_summary = None
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    if item.type == "reasoning" and hasattr(item, 'summary'):
                        reasoning_summary = " ".join([s.text for s in item.summary if hasattr(s, 'text')])
                        break
            
            return {
                "content": response.output_text or "",
                "usage": response.usage._raw if hasattr(response.usage, '_raw') else {},
                "reasoning_summary": reasoning_summary,
                "sources_used": []
            }
            
        except Exception as e:
            logger.error(f"Reasoning model API call failed: {e}")
            raise

    async def stream_response(
        self,
        message: str,
        persona: str = "partner",
        context: str = "",
        conversation_history: List[Dict[str, Any]] = None,
        framework: Optional[str] = None,
        rag_context: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream AI response using Response API streaming"""
        if os.getenv("OFFLINE_MODE", "false").lower() == "true":
            # Simulated two-chunk stream
            yield {"content": "[OFFLINE] Thinking… ", "model": "gpt-5-mini", "type": "content"}
            yield {"content": "done.", "model": "gpt-5-mini", "type": "content"}
            return
        try:
            # Convert inputs and determine model
            persona_enum = ConsultantPersona(persona) if isinstance(persona, str) else persona
            framework_enum = ConsultingFramework(framework) if framework else None
            
            complexity_score = complexity_analyzer.analyze_complexity(message, context)
            use_reasoning = self._should_use_reasoning_model(message, context, complexity_score)
            model = ModelType.O4_MINI if use_reasoning else ModelType.GPT5_MINI
            
            # Build context and instructions
            conversation_context = self._build_context(
                message, context, conversation_history or [], rag_context
            )
            instructions = self._build_instructions(persona_enum, framework_enum, use_reasoning)
            
            # Stream response
            stream_params = {
                "model": model.value,
                "instructions": instructions,
                "input": conversation_context,
                "stream": True,
                "store": True,
            }
            
            # Add reasoning parameters for complex queries
            if use_reasoning:
                effort = "low" if complexity_score < 0.7 else "medium" if complexity_score < 0.85 else "high"
                stream_params["reasoning"] = {
                    "effort": effort,
                    "summary": "auto"
                }
                stream_params["max_output_tokens"] = 4000
            else:
                stream_params["max_output_tokens"] = 800
            
            # Create streaming response
            stream = self.client.responses.create(**stream_params)
            
            # Yield streaming chunks
            async for chunk in stream:
                if hasattr(chunk, 'output') and chunk.output:
                    for item in chunk.output:
                        if item.type == "message" and hasattr(item, 'content'):
                            for content_item in item.content:
                                if content_item.type == "output_text":
                                    yield {
                                        "content": content_item.text,
                                        "model": model.value,
                                        "type": "content"
                                    }
                        elif item.type == "reasoning" and hasattr(item, 'summary'):
                            yield {
                                "content": "",
                                "model": model.value,
                                "type": "reasoning",
                                "reasoning_summary": " ".join([s.text for s in item.summary if hasattr(s, 'text')])
                            }
                            
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield {
                "content": f"Error generating response: {str(e)}",
                "model": "error",
                "type": "error"
            }

    def _build_context(
        self,
        message: str,
        context: str,
        conversation_history: List[Dict[str, Any]],
        rag_context: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Build conversation context for API call"""
        
        context_items = []
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            context_items.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add RAG context if available
        if rag_context and rag_context.strip():
            context_items.append({
                "role": "system",
                "content": f"Relevant knowledge base context:\n{rag_context}"
            })
        
        # Add current message
        context_items.append({
            "role": "user", 
            "content": message
        })
        
        return context_items

    def _build_instructions(
        self,
        persona: ConsultantPersona,
        framework: Optional[ConsultingFramework],
        use_reasoning_model: bool = False
    ) -> str:
        """Build complete instructions for the model"""

        # Choose appropriate system prompt based on model
        base_prompt = self.o4_system_prompt if use_reasoning_model else self.gpt5_system_prompt
        instructions = [base_prompt]

        # Add persona instructions
        persona_instructions = self._get_persona_instructions(persona)
        instructions.append(f"\nPersona: {persona_instructions}")

        # Add framework instructions if specified
        if framework:
            framework_instructions = self._get_framework_instructions(framework)
            instructions.append(f"\nFramework: {framework_instructions}")

        return "\n".join(instructions)
    
    def _determine_cache_type(self, message: str, framework: Optional[str]) -> CacheType:
        """Determine cache type based on query content and framework"""
        
        message_lower = message.lower()
        
        # Framework queries get long cache (24 hours)
        framework_keywords = [
            'swot', 'porter', 'five forces', 'mckinsey', '7s', 'bcg matrix', 
            'ansoff', 'pestel', 'framework', 'analysis', 'strategic'
        ]
        
        if framework or any(keyword in message_lower for keyword in framework_keywords):
            return CacheType.FRAMEWORK_QUERY
        
        # User-specific queries get short cache (5 minutes)
        user_specific_keywords = [
            'my company', 'my business', 'our company', 'our business',
            'we are', 'we have', 'our revenue', 'my startup'
        ]
        
        if any(keyword in message_lower for keyword in user_specific_keywords):
            return CacheType.USER_SPECIFIC
        
        # General business queries get medium cache (1 hour)
        return CacheType.GENERAL_QUERY
    
    async def _cache_model_response(self,
                                  message: str,
                                  response: ModelResponse,
                                  cache_type: CacheType,
                                  persona: str,
                                  framework: Optional[str],
                                  user_id: Optional[str]) -> None:
        """Cache the model response"""
        try:
            # Convert ModelResponse to cacheable dict
            cache_data = {
                "content": response.content,
                "model_used": response.model_used,
                "persona": response.persona,
                "usage": response.usage,
                "reasoning_summary": response.reasoning_summary,
                "sources_used": response.sources_used
            }
            
            # Cache the response
            await redis_cache.cache_response(
                query=message,
                response=cache_data,
                cache_type=cache_type,
                persona=persona,
                framework=framework,
                user_id=user_id
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
            # Don't fail the request if caching fails


# Global model router instance
model_router = ModelRouter()
