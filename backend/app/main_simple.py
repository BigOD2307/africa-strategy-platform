"""
Backend minimal pour Africa Strategy
Un seul endpoint : /api/analyze qui appelle directement OpenAI Assistant
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import logging
import json
import time
import asyncio

from app.services.openai_assistant_service import openai_assistant_service
from app.core.config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="Africa Strategy API",
    description="API minimaliste pour l'analyse IA",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Augmenter le timeout pour les requêtes longues (analyses IA)
import uvicorn
from fastapi.middleware.trustedhost import TrustedHostMiddleware


# Modèle de requête
class AnalyzeRequest(BaseModel):
    """Données du questionnaire pour l'analyse"""
    secteur: str
    zoneGeographique: str
    profilOrganisation: str
    biensServices: list
    autresBiensServices: str = ""
    paysInstallation: str
    objectifsDD: list
    positionnementStrategique: str
    visionOrganisation: str
    missionOrganisation: str
    projetsSignificatifs: str
    # Questions ESG (optionnel)
    questions_esg: Dict[str, Any] = {}


# Endpoint unique
@app.post("/api/analyze")
async def analyze_company(data: AnalyzeRequest):
    """
    Analyse complète d'une entreprise via OpenAI Assistant
    
    Reçoit les données du formulaire et retourne directement l'analyse complète
    """
    try:
        logger.info("Démarrage de l'analyse IA...")
        
        # Préparer les données pour l'assistant
        questionnaire_data = {
            "secteur": data.secteur,
            "zoneGeographique": data.zoneGeographique,
            "profilOrganisation": data.profilOrganisation,
            "biensServices": data.biensServices,
            "autresBiensServices": data.autresBiensServices,
            "paysInstallation": data.paysInstallation,
            "objectifsDD": data.objectifsDD,
            "positionnementStrategique": data.positionnementStrategique,
            "visionOrganisation": data.visionOrganisation,
            "missionOrganisation": data.missionOrganisation,
            "projetsSignificatifs": data.projetsSignificatifs,
            "questions_esg": data.questions_esg
        }
        
        # Appeler l'assistant OpenAI
        analysis_result = await openai_assistant_service.analyze_company(questionnaire_data)
        
        logger.info("Analyse complétée avec succès")
        
        # Retourner directement les données d'analyse (pas besoin de wrapper)
        # Le frontend attend soit result.data soit result directement
        if isinstance(analysis_result, dict) and "analyses" in analysis_result:
            return analysis_result
        else:
            return {
                "success": True,
                "analyses": analysis_result
            }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse IA: {str(e)}"
        )


@app.post("/api/enrich")
async def enrich_analysis(data: dict):
    """
    Enrichit les analyses avec OpenRouter (résumés, synthèse enrichie)
    """
    try:
        from app.services.openrouter_service import openrouter_service
        
        analyses = data.get("analyses", {})
        
        if not analyses:
            raise HTTPException(status_code=400, detail="Analyses requises")
        
        logger.info("Enrichissement des analyses avec OpenRouter...")
        
        # Enrichir TOUS les onglets (résumés + points clés)
        enriched_analyses = await openrouter_service.enrich_all_tabs(analyses)
        
        # Générer une synthèse stratégique enrichie
        enriched_synthesis = await openrouter_service.generate_synthesis(analyses)
        
        logger.info("✅ Enrichissement complet terminé")
        
        return {
            "success": True,
            "enriched_analyses": enriched_analyses,
            "enriched_synthesis": enriched_synthesis
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enrichissement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enrichissement: {str(e)}"
        )


@app.post("/api/chat")
async def chat_with_analysis(data: dict):
    """
    Chatbot qui répond aux questions sur l'analyse
    Utilise l'IA pour comprendre les questions et répondre en se basant sur les analyses
    """
    try:
        question = data.get("question", "")
        analysis_data = data.get("analysis_data", {})
        
        if not question:
            raise HTTPException(status_code=400, detail="Question requise")
        
        # Préparer le contexte avec les analyses
        context = f"""
Vous êtes un assistant IA expert en stratégie d'entreprise pour l'Afrique. 
Vous devez répondre aux questions de l'utilisateur en vous basant UNIQUEMENT sur les analyses suivantes.

ANALYSES DISPONIBLES:
{json.dumps(analysis_data, indent=2, ensure_ascii=False)}

QUESTION DE L'UTILISATEUR: {question}

INSTRUCTIONS:
1. Répondez de manière claire et concise
2. Citez des données spécifiques des analyses quand c'est pertinent
3. Si la question concerne un aspect non couvert par les analyses, dites-le poliment
4. Utilisez un ton professionnel mais accessible
5. Répondez en français

RÉPONSE:
"""
        
        # Utiliser l'assistant OpenAI pour générer la réponse
        client = openai_assistant_service.client
        
        # Créer un thread
        thread = client.beta.threads.create()
        
        # Ajouter le message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=context
        )
        
        # Lancer l'assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=openai_assistant_service.assistant_id
        )
        
        # Attendre la réponse (timeout plus court pour le chat)
        max_wait = 60  # 1 minute max pour le chat
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run.status == "completed":
                break
            elif run.status == "failed":
                raise Exception(f"Run failed: {run.last_error}")
            
            await asyncio.sleep(1)
        
        if run.status != "completed":
            raise Exception("Timeout lors de la génération de la réponse")
        
        # Récupérer la réponse
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc"
        )
        
        assistant_message = None
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                assistant_message = msg
                break
        
        if not assistant_message or not assistant_message.content:
            raise Exception("Aucune réponse de l'assistant")
        
        answer = assistant_message.content[0].text.value
        
        return {
            "answer": answer,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Erreur dans le chatbot: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la réponse: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "openai_configured": bool(openai_assistant_service.client)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

