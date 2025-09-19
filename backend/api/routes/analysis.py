"""
Business Analysis Routes for ValtricAI Consulting Agent
Provides structured business framework analysis using AI with RAG integration
"""

import logging
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional

from api.dependencies import get_current_user, get_project_id
from models.schemas import (
    SWOTAnalysisInput, 
    SWOTAnalysisResult, 
    PortersFiveForcesInput,
    PortersFiveForcesResult,
    RetrievalSource,
    ConsultantPersona,
    ConsultingFramework
)
from rag_system.retriever import hybrid_retriever
from agent_logic.model_router import model_router
from utils.tracing import RequestTracer, set_current_trace
from config.settings import settings, RAGMode

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analysis/swot", response_model=SWOTAnalysisResult)
async def perform_swot_analysis(
    analysis_input: SWOTAnalysisInput,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Perform comprehensive SWOT analysis using AI with RAG context
    
    Returns structured analysis with:
    - Strengths, Weaknesses, Opportunities, Threats
    - Strategic recommendations
    - Sources used from RAG system
    - Confidence scoring
    """
    
    # Initialize tracing
    tracer = RequestTracer(route="POST /analysis/swot", user_id=user.get("id"))
    set_current_trace(tracer)
    
    try:
        tracer.set_intent("swot_analysis")
        
        # Build query for RAG retrieval
        rag_query = f"SWOT analysis framework {analysis_input.company_description}"
        if analysis_input.industry:
            rag_query += f" {analysis_input.industry} industry"
        if analysis_input.specific_focus:
            rag_query += f" {analysis_input.specific_focus}"
        
        # Retrieve relevant context from RAG
        tracer.start_retrieval()
        try:
            retrieval_result = await hybrid_retriever.retrieve(
                query=rag_query,
                k=8,
                mode=settings.rag_mode,
                project_id=project_id
            )
            tracer.end_retrieval(cache_hit=retrieval_result.from_cache if hasattr(retrieval_result, 'from_cache') else False)
            
            logger.info(f"Retrieved {len(retrieval_result.results)} sources for SWOT analysis")
            
        except Exception as e:
            tracer.end_retrieval(cache_hit=False)
            logger.warning(f"RAG retrieval failed for SWOT analysis: {e}")
            retrieval_result = None
        
        # Build structured prompt for SWOT analysis
        context_text = retrieval_result.context_text if retrieval_result else ""
        
        analysis_prompt = f"""
You are a senior management consultant performing a SWOT analysis. Use the provided framework knowledge and analyze the company systematically.

## Company Information:
- Description: {analysis_input.company_description}
- Industry: {analysis_input.industry or 'Not specified'}
- Timeframe: {analysis_input.timeframe or 'Current analysis'}
- Specific Focus: {analysis_input.specific_focus or 'General strategic analysis'}

## Framework Context:
{context_text}

## Analysis Requirements:
Provide a comprehensive SWOT analysis in the following JSON format:

```json
{{
    "strengths": ["strength 1", "strength 2", ...],
    "weaknesses": ["weakness 1", "weakness 2", ...], 
    "opportunities": ["opportunity 1", "opportunity 2", ...],
    "threats": ["threat 1", "threat 2", ...],
    "strategic_recommendations": ["recommendation 1", "recommendation 2", ...],
    "confidence_score": 0.85
}}
```

Guidelines:
- Provide 3-5 items per SWOT category
- Be specific and actionable
- Base analysis on company details and industry context
- Include strategic recommendations that leverage strengths/opportunities and address weaknesses/threats
- Confidence score should reflect data quality and analysis depth (0.0-1.0)

Focus on practical, implementable insights that provide genuine strategic value.
"""
        
        # Generate AI analysis
        tracer.start_generation()
        try:
            model_response = await model_router.generate_response(
                message=analysis_prompt,
                persona=ConsultantPersona.SENIOR_PARTNER.value,
                context=context_text,
                framework=ConsultingFramework.SWOT.value,
                user_id=user.get("id")
            )

            usage = model_response.usage or {}
            tokens_in = usage.get("prompt_tokens", usage.get("input_tokens", 0))
            tokens_out = usage.get("completion_tokens", usage.get("output_tokens", 0))
            tracer.end_generation(tokens_in, tokens_out, model_response.model_used)

            ai_content = model_response.content
            
        except Exception as e:
            tracer.set_error(f"AI generation failed: {str(e)}")
            logger.error(f"SWOT analysis generation failed: {e}")
            raise HTTPException(status_code=500, detail="Analysis generation failed")
        
        # Parse AI response and extract JSON
        try:
            # Look for JSON in the response
            json_start = ai_content.find('{')
            json_end = ai_content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = ai_content[json_start:json_end]
                analysis_data = json.loads(json_str)
            else:
                # Fallback parsing if no JSON found
                raise ValueError("No valid JSON structure found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse SWOT analysis JSON: {e}")
            tracer.set_error(f"JSON parsing failed: {str(e)}")
            
            # Return fallback response
            analysis_data = {
                "strengths": ["Analysis parsing failed - please try again"],
                "weaknesses": ["Unable to complete structured analysis"],
                "opportunities": ["System optimization needed"],
                "threats": ["Technical limitation encountered"],
                "strategic_recommendations": ["Please retry the analysis request"],
                "confidence_score": 0.1
            }
        
        # Convert RAG sources to RetrievalSource format
        sources_used = []
        if retrieval_result and retrieval_result.results:
            for result in retrieval_result.results[:5]:  # Limit to top 5 sources
                snippet = result.text[:200] + "..." if len(result.text) > 200 else result.text
                source = RetrievalSource(
                    id=result.id or "unknown",
                    text=snippet,
                    similarity_score=result.similarity_score,
                    source_type=result.source_type,
                    source_label=result.source_label,
                    metadata=result.metadata
                )
                sources_used.append(source)
        
        # Build final response
        swot_result = SWOTAnalysisResult(
            strengths=analysis_data.get("strengths", []),
            weaknesses=analysis_data.get("weaknesses", []),
            opportunities=analysis_data.get("opportunities", []),
            threats=analysis_data.get("threats", []),
            strategic_recommendations=analysis_data.get("strategic_recommendations", []),
            confidence_score=analysis_data.get("confidence_score", 0.0),
            sources_used=sources_used
        )
        
        logger.info(f"Completed SWOT analysis for project {project_id}")
        return swot_result
        
    except HTTPException:
        raise
    except Exception as e:
        tracer.set_error(str(e))
        logger.error(f"SWOT analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")
    finally:
        # Finish tracing in background
        background_tasks.add_task(tracer.finish)


@router.post("/analysis/porters", response_model=PortersFiveForcesResult)
async def perform_porters_analysis(
    analysis_input: PortersFiveForcesInput,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """
    Perform Porter's Five Forces analysis using AI with RAG context
    
    Returns structured analysis of:
    - Competitive Rivalry
    - Supplier Power  
    - Buyer Power
    - Threat of Substitution
    - Barriers to Entry
    - Overall industry attractiveness assessment
    """
    
    # Initialize tracing
    tracer = RequestTracer(route="POST /analysis/porters", user_id=user.get("id"))
    set_current_trace(tracer)
    
    try:
        tracer.set_intent("porters_five_forces_analysis")
        
        # Build query for RAG retrieval
        rag_query = f"Porter's Five Forces analysis {analysis_input.company_description} {analysis_input.industry}"
        if analysis_input.market_segment:
            rag_query += f" {analysis_input.market_segment} market segment"
        
        # Retrieve relevant context from RAG
        tracer.start_retrieval()
        try:
            retrieval_result = await hybrid_retriever.retrieve(
                query=rag_query,
                k=8,
                mode=settings.rag_mode,
                project_id=project_id
            )
            tracer.end_retrieval(cache_hit=retrieval_result.from_cache if hasattr(retrieval_result, 'from_cache') else False)
            
            logger.info(f"Retrieved {len(retrieval_result.results)} sources for Porter's Five Forces analysis")
            
        except Exception as e:
            tracer.end_retrieval(cache_hit=False)
            logger.warning(f"RAG retrieval failed for Porter's analysis: {e}")
            retrieval_result = None
        
        # Build structured prompt for Porter's Five Forces analysis
        context_text = retrieval_result.context_text if retrieval_result else ""
        
        analysis_prompt = f"""
You are a senior strategy consultant performing a Porter's Five Forces analysis. Use the provided framework knowledge to systematically analyze the competitive landscape.

## Company & Industry Information:
- Company Description: {analysis_input.company_description}
- Industry: {analysis_input.industry}
- Market Segment: {analysis_input.market_segment or 'General market'}

## Framework Context:
{context_text}

## Analysis Requirements:
Provide a comprehensive Porter's Five Forces analysis in the following JSON format:

```json
{{
    "competitive_rivalry": {{
        "intensity": "High/Medium/Low",
        "factors": ["factor 1", "factor 2", ...],
        "score": 0.75,
        "analysis": "Detailed analysis of competitive rivalry..."
    }},
    "supplier_power": {{
        "intensity": "High/Medium/Low", 
        "factors": ["factor 1", "factor 2", ...],
        "score": 0.60,
        "analysis": "Detailed analysis of supplier power..."
    }},
    "buyer_power": {{
        "intensity": "High/Medium/Low",
        "factors": ["factor 1", "factor 2", ...], 
        "score": 0.50,
        "analysis": "Detailed analysis of buyer power..."
    }},
    "threat_of_substitution": {{
        "intensity": "High/Medium/Low",
        "factors": ["factor 1", "factor 2", ...],
        "score": 0.40,
        "analysis": "Detailed analysis of substitution threats..."
    }},
    "barriers_to_entry": {{
        "intensity": "High/Medium/Low",
        "factors": ["factor 1", "factor 2", ...],
        "score": 0.80,
        "analysis": "Detailed analysis of entry barriers..."
    }},
    "overall_attractiveness": "High/Medium/Low - Detailed assessment of overall industry attractiveness",
    "strategic_implications": ["implication 1", "implication 2", ...],
    "confidence_score": 0.85
}}
```

Guidelines:
- Score each force from 0.0 (very low intensity) to 1.0 (very high intensity)
- Provide 3-5 key factors per force
- Include detailed analysis explaining the scoring
- Strategic implications should be actionable insights
- Overall attractiveness should synthesize all five forces
- Confidence score should reflect analysis quality and data availability

Focus on industry-specific factors and provide practical strategic insights for competitive positioning.
"""
        
        # Generate AI analysis
        tracer.start_generation()
        try:
            model_response = await model_router.generate_response(
                message=analysis_prompt,
                persona=ConsultantPersona.SENIOR_PARTNER.value,
                context=context_text,
                framework=ConsultingFramework.PORTERS.value,
                user_id=user.get("id")
            )

            usage = model_response.usage or {}
            tokens_in = usage.get("prompt_tokens", usage.get("input_tokens", 0))
            tokens_out = usage.get("completion_tokens", usage.get("output_tokens", 0))
            tracer.end_generation(tokens_in, tokens_out, model_response.model_used)

            ai_content = model_response.content
            
        except Exception as e:
            tracer.set_error(f"AI generation failed: {str(e)}")
            logger.error(f"Porter's Five Forces analysis generation failed: {e}")
            raise HTTPException(status_code=500, detail="Analysis generation failed")
        
        # Parse AI response and extract JSON
        try:
            # Look for JSON in the response
            json_start = ai_content.find('{')
            json_end = ai_content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = ai_content[json_start:json_end]
                analysis_data = json.loads(json_str)
            else:
                # Fallback parsing if no JSON found
                raise ValueError("No valid JSON structure found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse Porter's Five Forces analysis JSON: {e}")
            tracer.set_error(f"JSON parsing failed: {str(e)}")
            
            # Return fallback response
            analysis_data = {
                "competitive_rivalry": {
                    "intensity": "Unknown",
                    "factors": ["Analysis parsing failed"],
                    "score": 0.5,
                    "analysis": "Unable to complete analysis - please try again"
                },
                "supplier_power": {
                    "intensity": "Unknown", 
                    "factors": ["Analysis parsing failed"],
                    "score": 0.5,
                    "analysis": "Unable to complete analysis - please try again"
                },
                "buyer_power": {
                    "intensity": "Unknown",
                    "factors": ["Analysis parsing failed"], 
                    "score": 0.5,
                    "analysis": "Unable to complete analysis - please try again"
                },
                "threat_of_substitution": {
                    "intensity": "Unknown",
                    "factors": ["Analysis parsing failed"],
                    "score": 0.5,
                    "analysis": "Unable to complete analysis - please try again"
                },
                "barriers_to_entry": {
                    "intensity": "Unknown",
                    "factors": ["Analysis parsing failed"],
                    "score": 0.5,
                    "analysis": "Unable to complete analysis - please try again"
                },
                "overall_attractiveness": "Unknown - Analysis failed",
                "strategic_implications": ["Please retry the analysis request"],
                "confidence_score": 0.1
            }
        
        # Build final response
        porters_result = PortersFiveForcesResult(
            competitive_rivalry=analysis_data.get("competitive_rivalry", {}),
            supplier_power=analysis_data.get("supplier_power", {}),
            buyer_power=analysis_data.get("buyer_power", {}),
            threat_of_substitution=analysis_data.get("threat_of_substitution", {}),
            barriers_to_entry=analysis_data.get("barriers_to_entry", {}),
            overall_attractiveness=analysis_data.get("overall_attractiveness", "Unknown"),
            strategic_implications=analysis_data.get("strategic_implications", []),
            confidence_score=analysis_data.get("confidence_score", 0.0)
        )
        
        logger.info(f"Completed Porter's Five Forces analysis for project {project_id}")
        return porters_result
        
    except HTTPException:
        raise
    except Exception as e:
        tracer.set_error(str(e))
        logger.error(f"Porter's Five Forces analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")
    finally:
        # Finish tracing in background
        background_tasks.add_task(tracer.finish)


@router.post("/analysis/mckinsey")
async def perform_mckinsey_analysis(
    analysis_input: dict,
    user = Depends(get_current_user),
    project_id = Depends(get_project_id)
):
    """Perform McKinsey 7S analysis using AI"""
    return {"message": "McKinsey analysis endpoint - to be implemented"}
