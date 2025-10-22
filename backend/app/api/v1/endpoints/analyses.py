ackend/app/api/v1/endpoints/analyses.py</path>
<content">@router.post("/market-competition", response_model=Dict[str, Any])
async def analyze_market_competition(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze market and competition for a company using AI

    This endpoint performs market analysis using:
    - Perplexity for current market data and trends
    - Gemini 2.5 Flash for competition analysis
    - Sector-specific insights and opportunities
    """
    try:
        logger.info(f"Starting market competition analysis for company {request.company_id}")

        # Perform market competition analysis
        analysis_result = await ai_service.analyze_market_competition(request.company_data)

        # Add metadata
        analysis_result.update({
            "company_id": request.company_id,
            "analysis_type": "market_competition",
            "status": "completed"
        })

        logger.info(f"Market competition analysis completed for company {request.company_id}")
        return analysis_result

    except Exception as e:
        logger.error(f"Error in market competition analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse marché/concurrence: {str(e)}"
        )


@router.post("/value-chain", response_model=Dict[str, Any])
async def analyze_value_chain(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze value chain for a company using AI

    This endpoint performs value chain analysis using:
    - Industry best practices from Perplexity
    - Gemini 2.5 Flash for company-specific analysis
    - Efficiency opportunities and competitive advantages
    """
    try:
        logger.info(f"Starting value chain analysis for company {request.company_id}")

        # Perform value chain analysis
        analysis_result = await ai_service.analyze_value_chain(request.company_data)

        # Add metadata
        analysis_result.update({
            "company_id": request.company_id,
            "analysis_type": "value_chain",
            "status": "completed"
        })

        logger.info(f"Value chain analysis completed for company {request.company_id}")
        return analysis_result

    except Exception as e:
        logger.error(f"Error in value chain analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse chaîne de valeur: {str(e)}"
        )


@router.post("/sustainability-impact", response_model=Dict[str, Any])
async def analyze_sustainability_impact(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze sustainability impact and SDGs contribution

    This endpoint performs sustainability analysis using:
    - ESG data and SDGs context from Perplexity
    - Gemini 2.5 Flash for impact assessment
    - Environmental, social, and economic impact evaluation
    """
    try:
        logger.info(f"Starting sustainability impact analysis for company {request.company_id}")

        if not request.esg_responses:
            raise HTTPException(
                status_code=400,
                detail="Les réponses ESG sont requises pour l'analyse d'impact durable"
            )

        # Perform sustainability impact analysis
        analysis_result = await ai_service.analyze_sustainability_impact(
            request.company_data, {"esg_scores": request.esg_responses}
        )

        # Add metadata
        analysis_result.update({
            "company_id": request.company_id,
            "analysis_type": "sustainability_impact",
            "status": "completed"
        })

        logger.info(f"Sustainability impact analysis completed for company {request.company_id}")
        return analysis_result

    except Exception as e:
        logger.error(f"Error in sustainability impact analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse impact durable: {str(e)}"
        )


@router.post("/integrated-synthesis", response_model=Dict[str, Any])
async def generate_integrated_synthesis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Generate integrated synthesis of all analyses

    This endpoint creates a comprehensive synthesis using:
    - All previous analysis results
    - Gemini 2.5 Flash for strategic integration
    - Executive summary and strategic recommendations
    """
    try:
        logger.info(f"Starting integrated synthesis for company {request.company_id}")

        # First, perform all individual analyses
        pestel_result = await ai_service.analyze_pestel(request.company_data)

        market_result = await ai_service.analyze_market_competition(request.company_data)

        value_chain_result = await ai_service.analyze_value_chain(request.company_data)

        esg_result = None
        sustainability_result = None
        if request.esg_responses:
            esg_result = await ai_service.analyze_esg(request.company_data, request.esg_responses)
            sustainability_result = await ai_service.analyze_sustainability_impact(
                request.company_data, {"esg_scores": request.esg_responses}
            )

        # Prepare all analyses for synthesis
        all_analyses = {
            "pestel": pestel_result,
            "market_competition": market_result,
            "value_chain": value_chain_result,
            "esg": esg_result,
            "sustainability_impact": sustainability_result
        }

        # Generate integrated synthesis
        synthesis_result = await ai_service.generate_integrated_synthesis(
            request.company_data, all_analyses
        )

        # Generate strategic roadmap
        roadmap_result = await ai_service.generate_strategic_roadmap(
            request.company_data, synthesis_result
        )

        # Compile complete result
        complete_result = {
            "company_id": request.company_id,
            "company_name": request.company_data.get("company_name", "Entreprise"),
            "analysis_date": synthesis_result["analysis_date"],
            "synthesis": synthesis_result,
            "roadmap": roadmap_result,
            "all_analyses": all_analyses,
            "status": "completed"
        }

        logger.info(f"Integrated synthesis completed for company {request.company_id}")
        return complete_result

    except Exception as e:
        logger.error(f"Error in integrated synthesis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la synthèse intégrale: {str(e)}"
        )


@router.post("/strategic-roadmap", response_model=Dict[str, Any])
async def generate_strategic_roadmap(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Generate strategic roadmap based on company analysis

    This endpoint creates a strategic roadmap using:
    - Company data and analysis results
    - Gemini 2.5 Flash for strategic planning
    - Phased implementation with timelines and resources
    """
    try:
        logger.info(f"Starting strategic roadmap generation for company {request.company_id}")

        # First generate synthesis if not provided
        synthesis_result = await ai_service.generate_integrated_synthesis(
            request.company_data,
            {}  # Empty analyses - will be generated internally
        )

        # Generate strategic roadmap
        roadmap_result = await ai_service.generate_strategic_roadmap(
            request.company_data, synthesis_result
        )

        # Add metadata
        roadmap_result.update({
            "company_id": request.company_id,
            "analysis_type": "strategic_roadmap",
            "status": "completed"
        })

        logger.info(f"Strategic roadmap generated for company {request.company_id}")
        return roadmap_result

    except Exception as e:
        logger.error(f"Error generating strategic roadmap: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération roadmap stratégique: {str(e)}"
        )


@router.post("/chat-contextual", response_model=Dict[str, Any])
async def chat_with_full_context(request: ChatRequest):
    """
    Enhanced chat with full analysis context

    This endpoint provides contextual AI assistance using:
    - All company analyses and data
    - Gemini 2.5 Flash for intelligent responses
    - Strategic and practical advice
    """
    try:
        logger.info(f"Contextual AI chat request for company {request.company_id}")

        # Get comprehensive company context
        # In a real implementation, this would fetch from database
        company_context = {
            "company_id": request.company_id,
            "company_name": "Entreprise",  # Would be fetched from DB
            "sector": "General",  # Would be fetched from DB
            "country": "Côte d'Ivoire",  # Would be fetched from DB
            "current_score": 65,  # Would be calculated
        }

        # Get all analyses context
        # In a real implementation, this would fetch from database/cache
        analyses_context = {
            "overall_score": 65,
            "pestel": {"overall_score": 6.5},
            "esg": {"overall_score": 65},
            "market_competition": {"opportunities": []},
            "value_chain": {"efficiency_opportunities": []},
            "sustainability_impact": {"sustainability_score": 65}
        }

        # Get contextual AI response
        ai_response = await ai_service.chat_with_context(
            request.message,
            company_context,
            analyses_context
        )

        response_data = {
            "company_id": request.company_id,
            "user_message": request.message,
            "ai_response": ai_response,
            "timestamp": "2025-01-01T12:00:00Z",
            "model_used": "gemini-2.0-flash-exp",
            "context_used": True
        }

        logger.info(f"Contextual AI chat completed for company {request.company_id}")
        return response_data

    except Exception as e:
        logger.error(f"Error in contextual chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du chat contextuel: {str(e)}"
        )
