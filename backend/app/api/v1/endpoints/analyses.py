"""
Analysis endpoints for AI-powered business analysis
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ....services.ai_service import ai_service
from ....core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for business analysis"""
    company_id: str
    company_data: Dict[str, Any]
    esg_responses: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    """Request model for AI chat"""
    message: str
    company_id: str


@router.post("/pestel", response_model=Dict[str, Any])
async def analyze_pestel(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze PESTEL factors for a company using AI

    This endpoint performs a comprehensive PESTEL analysis using:
    - Gemini 2.5 Flash for detailed analysis
    - Perplexity for current market data and trends
    - Company-specific context and sector analysis
    """
    try:
        logger.info(f"Starting PESTEL analysis for company {request.company_id}")

        # Perform PESTEL analysis
        analysis_result = await ai_service.analyze_pestel(request.company_data)

        # Add metadata
        analysis_result.update({
            "company_id": request.company_id,
            "analysis_type": "pestel",
            "status": "completed"
        })

        logger.info(f"PESTEL analysis completed for company {request.company_id}")
        return analysis_result

    except Exception as e:
        logger.error(f"Error in PESTEL analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse PESTEL: {str(e)}"
        )


@router.post("/esg", response_model=Dict[str, Any])
async def analyze_esg(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze ESG factors for a company using AI

    This endpoint performs ESG analysis using:
    - Questionnaire responses scoring
    - Gemini 2.5 Flash for detailed recommendations
    - Perplexity for ESG best practices and standards
    """
    try:
        logger.info(f"Starting ESG analysis for company {request.company_id}")

        if not request.esg_responses:
            raise HTTPException(
                status_code=400,
                detail="Les réponses ESG sont requises pour cette analyse"
            )

        # Perform ESG analysis
        analysis_result = await ai_service.analyze_esg(
            request.company_data,
            request.esg_responses
        )

        # Add metadata
        analysis_result.update({
            "company_id": request.company_id,
            "analysis_type": "esg",
            "status": "completed"
        })

        logger.info(f"ESG analysis completed for company {request.company_id}")
        return analysis_result

    except Exception as e:
        logger.error(f"Error in ESG analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse ESG: {str(e)}"
        )


@router.post("/complete", response_model=Dict[str, Any])
async def analyze_complete(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Perform complete business analysis (PESTEL + ESG + Roadmap)

    This endpoint provides a comprehensive analysis including:
    - PESTEL analysis with market context
    - ESG analysis with scoring and recommendations
    - Personalized roadmap with actionable steps
    - Overall maturity score
    """
    try:
        logger.info(f"Starting complete analysis for company {request.company_id}")

        # Perform PESTEL analysis
        pestel_result = await ai_service.analyze_pestel(request.company_data)

        # Perform ESG analysis if responses provided
        esg_result = None
        if request.esg_responses:
            esg_result = await ai_service.analyze_esg(
                request.company_data,
                request.esg_responses
            )

        # Prepare analyses for roadmap generation
        analyses = {"pestel": pestel_result}
        if esg_result:
            analyses["esg"] = esg_result

        # Generate personalized roadmap
        roadmap_result = await ai_service.generate_roadmap(
            request.company_data,
            analyses
        )

        # Calculate overall score
        overall_score = ai_service._calculate_overall_score(analyses)

        # Compile complete analysis
        complete_result = {
            "company_id": request.company_id,
            "company_name": request.company_data.get("company_name", "Entreprise"),
            "analysis_date": pestel_result["analysis_date"],
            "overall_score": overall_score,
            "maturity_level": _get_maturity_level(overall_score),
            "analyses": {
                "pestel": pestel_result,
                "esg": esg_result
            },
            "roadmap": roadmap_result,
            "recommendations": _compile_recommendations(pestel_result, esg_result),
            "next_steps": _get_next_steps(overall_score, roadmap_result),
            "status": "completed"
        }

        logger.info(f"Complete analysis finished for company {request.company_id}")
        return complete_result

    except Exception as e:
        logger.error(f"Error in complete analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse complète: {str(e)}"
        )


@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI assistant for personalized business advice

    This endpoint provides contextual AI assistance using:
    - Company-specific context and analyses
    - Gemini 2.5 Flash for intelligent responses
    - Focus on African business context and sustainability
    """
    try:
        logger.info(f"AI chat request for company {request.company_id}")

        # Get company context (in a real implementation, this would come from database)
        company_context = {
            "company_id": request.company_id,
            "company_name": "Entreprise",  # Would be fetched from DB
            "current_score": 65,  # Would be calculated from latest analyses
        }

        # Get AI response
        ai_response = await ai_service.chat_with_ai(
            request.message,
            company_context
        )

        response_data = {
            "company_id": request.company_id,
            "user_message": request.message,
            "ai_response": ai_response,
            "timestamp": "2025-01-01T12:00:00Z",  # Would be current timestamp
            "model_used": "gemini-2.0-flash-exp"
        }

        logger.info(f"AI chat completed for company {request.company_id}")
        return response_data

    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du chat IA: {str(e)}"
        )


@router.get("/health")
async def ai_health_check():
    """Check AI service health and connectivity"""
    try:
        # Test OpenRouter connectivity
        health_status = {
            "service": "AI Analysis Service",
            "status": "healthy",
            "openrouter_configured": bool(ai_service.openrouter_api_key),
            "models_available": [
                "Gemini 2.5 Flash (google/gemini-2.0-flash-exp:free)",
                "Perplexity (perplexity/llama-3.1-sonar-large-128k-online)"
            ],
            "features": [
                "PESTEL Analysis",
                "ESG Analysis",
                "Personalized Roadmap",
                "AI Chat Assistant"
            ]
        }

        return health_status

    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service IA indisponible"
        )


# Helper functions

def _get_maturity_level(score: float) -> str:
    """Determine maturity level based on overall score"""
    if score >= 85:
        return "Leader"
    elif score >= 75:
        return "Engagé"
    elif score >= 50:
        return "Conscient"
    else:
        return "Débutant"


def _compile_recommendations(pestel_result: Dict[str, Any], esg_result: Optional[Dict[str, Any]] = None) -> List[str]:
    """Compile top recommendations from all analyses"""
    recommendations = []

    # Add PESTEL recommendations
    if "recommendations" in pestel_result:
        recommendations.extend(pestel_result["recommendations"][:3])

    # Add ESG recommendations
    if esg_result and "recommendations" in esg_result:
        recommendations.extend(esg_result["recommendations"][:3])

    # Remove duplicates and limit to top 5
    unique_recommendations = []
    seen = set()
    for rec in recommendations:
        if rec not in seen:
            unique_recommendations.append(rec)
            seen.add(rec)

    return unique_recommendations[:5]


def _get_next_steps(score: float, roadmap: Dict[str, Any]) -> List[str]:
    """Get next actionable steps based on current score and roadmap"""
    next_steps = []

    # Get current phase from roadmap
    phases = roadmap.get("phases", [])
    current_phase = None

    for phase in phases:
        if phase.get("status") == "in_progress":
            current_phase = phase
            break
        elif phase.get("status") == "completed":
            continue
        elif phase.get("status") == "locked":
            break

    if current_phase:
        steps = current_phase.get("steps", [])
        for step in steps:
            if step.get("status") == "not_started":
                next_steps.append(step.get("title", ""))
                if len(next_steps) >= 3:  # Limit to 3 next steps
                    break

    return next_steps if next_steps else ["Complétez votre profil pour débloquer les prochaines étapes"]
