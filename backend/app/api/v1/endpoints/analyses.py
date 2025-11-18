"""
Enhanced AI Analyses API endpoints
Provides comprehensive strategic analyses with RAG integration
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from app.services.ai_service import enhanced_ai_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/pestel")
async def analyze_pestel(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced PESTEL Analysis with RAG + Perplexity + Gemini

    Performs a comprehensive Political, Economic, Social, Technological,
    Environmental, and Legal analysis using multiple AI sources for maximum accuracy.

    Args:
        company_data: Company information including sector, country, size, etc.

    Returns:
        Complete PESTEL analysis with scores, justifications, and recommendations
    """
    try:
        if not company_data.get('company_name') or not company_data.get('sector'):
            raise HTTPException(
                status_code=400,
                detail="Company name and sector are required"
            )

        logger.info(f"Starting enhanced PESTEL analysis for {company_data.get('company_name')}")

        result = await enhanced_ai_service.analyze_pestel_enhanced(company_data)

        logger.info(f"PESTEL analysis completed for {company_data.get('company_name')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PESTEL analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/esg")
async def analyze_esg(
    company_data: Dict[str, Any],
    esg_responses: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Enhanced ESG Analysis with RAG + Perplexity + Gemini

    Analyzes Environmental, Social, and Governance practices using
    questionnaire responses and contextual knowledge for accurate scoring.

    Args:
        company_data: Company information
        esg_responses: ESG questionnaire responses (optional)

    Returns:
        Complete ESG analysis with pillar scores and improvement plans
    """
    try:
        if not company_data.get('company_name'):
            raise HTTPException(
                status_code=400,
                detail="Company name is required"
            )

        if not esg_responses:
            # Return basic analysis without questionnaire data
            return {
                "message": "ESG analysis requires questionnaire responses",
                "status": "incomplete",
                "recommendation": "Complete the ESG questionnaire for full analysis"
            }

        logger.info(f"Starting enhanced ESG analysis for {company_data.get('company_name')}")

        result = await enhanced_ai_service.analyze_esg_enhanced(company_data, esg_responses)

        logger.info(f"ESG analysis completed for {company_data.get('company_name')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ESG analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"ESG analysis failed: {str(e)}"
        )


@router.post("/market-competition")
async def analyze_market_competition(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Market and Competition Analysis

    Analyzes market size, competitive landscape, opportunities, and threats
    for the company's sector and region.
    """
    try:
        if not company_data.get('sector') or not company_data.get('country'):
            raise HTTPException(
                status_code=400,
                detail="Sector and country are required"
            )

        logger.info(f"Starting market analysis for {company_data.get('company_name', 'Unknown')}")

        result = await enhanced_ai_service._analyze_market_enhanced(company_data)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Market analysis failed: {str(e)}"
        )


@router.post("/value-chain")
async def analyze_value_chain(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Value Chain Analysis

    Analyzes the company's value creation process from inbound logistics
    to customer service, identifying optimization opportunities.
    """
    try:
        if not company_data.get('sector'):
            raise HTTPException(
                status_code=400,
                detail="Sector is required for value chain analysis"
            )

        logger.info(f"Starting value chain analysis for {company_data.get('company_name', 'Unknown')}")

        result = await enhanced_ai_service._analyze_value_chain_enhanced(company_data)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Value chain analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Value chain analysis failed: {str(e)}"
        )


@router.post("/sustainability-impact")
async def analyze_sustainability_impact(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sustainability Impact Analysis

    Evaluates the company's contribution to UN Sustainable Development Goals (SDGs)
    and overall positive impact on society and environment.
    """
    try:
        logger.info(f"Starting sustainability impact analysis for {company_data.get('company_name', 'Unknown')}")

        result = await enhanced_ai_service._analyze_sustainability_impact_enhanced(company_data)

        return result

    except Exception as e:
        logger.error(f"Sustainability impact analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sustainability impact analysis failed: {str(e)}"
        )


@router.post("/integrated-synthesis")
async def analyze_integrated_synthesis(
    company_data: Dict[str, Any],
    esg_responses: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Complete Integrated Strategic Analysis

    Performs ALL analyses (PESTEL, ESG, Market, Value Chain, Sustainability Impact)
    and generates a comprehensive synthesis with strategic roadmap.

    This is the flagship analysis combining all AI capabilities for maximum insight.

    Args:
        company_data: Complete company information
        esg_responses: ESG questionnaire responses (optional)
        background_tasks: FastAPI background tasks for async processing

    Returns:
        Complete strategic analysis package
    """
    try:
        if not company_data.get('company_name') or not company_data.get('sector'):
            raise HTTPException(
                status_code=400,
                detail="Company name and sector are required"
            )

        logger.info(f"Starting integrated synthesis for {company_data.get('company_name')}")

        # For large analyses, could run in background
        # if background_tasks:
        #     background_tasks.add_task(
        #         enhanced_ai_service.analyze_integrated_synthesis,
        #         company_data, esg_responses
        #     )
        #     return {"status": "processing", "message": "Analysis started in background"}

        # Run complete analysis
        result = await enhanced_ai_service.analyze_integrated_synthesis(company_data, esg_responses)

        logger.info(f"Integrated synthesis completed for {company_data.get('company_name')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Integrated synthesis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Integrated synthesis failed: {str(e)}"
        )


@router.post("/strategic-roadmap")
async def generate_strategic_roadmap(
    company_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate Strategic Roadmap

    Creates a detailed 24-month action plan based on company analysis,
    with phases, timelines, investments, and success metrics.
    """
    try:
        if not company_data.get('company_name'):
            raise HTTPException(
                status_code=400,
                detail="Company name is required"
            )

        logger.info(f"Generating strategic roadmap for {company_data.get('company_name')}")

        # If analysis results provided, use them; otherwise generate basic roadmap
        if analysis_results:
            synthesis = analysis_results.get('integrated_synthesis', {})
            score = analysis_results.get('overall_score', 50)
        else:
            synthesis = {}
            score = 50

        roadmap = await enhanced_ai_service._generate_strategic_roadmap(company_data, synthesis, score)

        return {
            "company_info": company_data,
            "roadmap": roadmap,
            "generated_at": "2025-11-04T12:06:10.520Z",
            "analysis_based": bool(analysis_results)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strategic roadmap generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Strategic roadmap generation failed: {str(e)}"
        )


@router.post("/chat-contextual")
async def chat_contextual(
    message: str,
    company_id: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Contextual AI Chat Assistant

    Provides intelligent responses based on company analysis history
    and general business knowledge for Africa Strategy.

    Args:
        message: User message
        company_id: Company identifier
        conversation_history: Previous conversation messages

    Returns:
        AI response with context
    """
    try:
        if not message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        # Build context-aware prompt
        context_prompt = f"""
Tu es un assistant IA expert pour Africa Strategy, spécialisé dans l'accompagnement des entrepreneurs africains vers la durabilité.

CONTEXTE ENTREPRISE:
- ID: {company_id}
- Historique conversation: {json.dumps(conversation_history[-5:] if conversation_history else [], ensure_ascii=False)}

QUESTION UTILISATEUR: {message}

INSTRUCTIONS:
- Réponds en français de manière professionnelle et accessible
- Base tes réponses sur les analyses stratégiques (PESTEL, ESG, etc.)
- Adapte tes conseils au contexte africain (Côte d'Ivoire, Afrique de l'Ouest)
- Sois encourageant et propose des actions concrètes
- Si tu n'as pas assez d'informations, suggère de compléter les analyses

Réponds de manière utile et actionnable.
"""

        messages = [{"role": "user", "content": context_prompt}]

        response = await enhanced_ai_service._call_openrouter(
            enhanced_ai_service.gemini_model,
            messages,
            temperature=0.7  # More creative for conversation
        )

        if not response:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate AI response"
            )

        return {
            "response": response,
            "company_id": company_id,
            "timestamp": "2025-11-04T12:06:10.520Z",
            "model_used": enhanced_ai_service.gemini_model,
            "conversation_context": bool(conversation_history)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contextual chat failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/health")
async def ai_analysis_health() -> Dict[str, Any]:
    """
    AI Analysis Service Health Check

    Returns comprehensive health information about all AI analysis capabilities,
    including OpenRouter connection, RAG status, and analysis performance.
    """
    try:
        health = {
            "service": "AI Analysis Engine",
            "status": "unknown",
            "timestamp": "2025-11-04T12:06:10.520Z",
            "capabilities": {
                "pestel_analysis": True,
                "esg_analysis": True,
                "market_analysis": True,
                "value_chain_analysis": True,
                "sustainability_impact": True,
                "integrated_synthesis": True,
                "strategic_roadmap": True,
                "contextual_chat": True
            },
            "integrations": {
                "openrouter": bool(enhanced_ai_service.openrouter_api_key),
                "gemini_model": enhanced_ai_service.gemini_model,
                "perplexity_model": enhanced_ai_service.perplexity_model,
                "rag_enabled": True  # Always enabled now
            }
        }

        # Test basic connectivity
        try:
            # Simple test call (could be cached)
            test_response = await enhanced_ai_service._call_openrouter(
                enhanced_ai_service.gemini_model,
                [{"role": "user", "content": "Hello"}]
            )
            health["openrouter_connection"] = bool(test_response)
        except Exception:
            health["openrouter_connection"] = False

        # Check RAG status
        try:
            rag_health = await enhanced_ai_service._get_rag_context({"test": True}, "health")
            health["rag_status"] = "operational" if rag_health else "limited"
        except Exception:
            health["rag_status"] = "error"

        # Overall status
        if health["openrouter_connection"] and health["rag_status"] != "error":
            health["status"] = "healthy"
        elif health["openrouter_connection"]:
            health["status"] = "degraded"
        else:
            health["status"] = "unhealthy"

        health["description"] = "Enhanced AI analysis engine with RAG integration for Africa Strategy"

        return health

    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        return {
            "service": "AI Analysis Engine",
            "status": "error",
            "error": str(e),
            "timestamp": "2025-11-04T12:06:10.520Z"
        }
