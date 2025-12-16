"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AFRICA STRATEGY API - VERSION 2.1                          ║
║              Backend avec Chargement Progressif des 7 Blocs                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Architecture V2.1 :
- Chargement progressif : BLOC1 immédiat, autres en background
- 7 Assistants OpenAI spécialisés (un par bloc)
- Sessions pour tracking en temps réel
- RAG intégré via File Search d'OpenAI

Auteur: Africa Strategy Platform
Version: 2.1
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json
import time
import asyncio
import uuid
from datetime import datetime

from app.services.openai_assistant_service import openai_assistant_service, BLOC_NAMES, ASSISTANT_IDS
from app.core.config import settings
from app.config.blocs_config import get_bloc_config, get_blocs_for_profil, get_all_blocs

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# STOCKAGE DES SESSIONS EN MÉMOIRE (Redis en production)
# ═══════════════════════════════════════════════════════════════════════════════

ANALYSIS_SESSIONS: Dict[str, Dict[str, Any]] = {}

# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION FASTAPI
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Africa Strategy API V2",
    description="API pour l'analyse stratégique ESG avec 7 blocs spécialisés et assistants OpenAI dédiés",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# MODÈLES DE REQUÊTE
# ═══════════════════════════════════════════════════════════════════════════════

class AnalyzeRequestV2(BaseModel):
    """Données du questionnaire V2 pour l'analyse complète"""
    secteur: str
    profilOrganisation: str
    paysInstallation: str
    zoneGeographique: str
    biensServices: List[str] = []
    autresBiensServices: str = ""
    oddAutomatiques: List[str] = []
    oddManuels: List[str] = []
    objectifsDD: List[str] = []  # Compatibilité
    autresODD: str = ""
    visionOrganisation: str = ""
    missionOrganisation: str = ""
    projetsSignificatifs: str = ""
    fichiers: List[str] = []
    fichiersContext: str = ""


class BlocAnalyzeRequest(BaseModel):
    """Requête pour analyser un bloc spécifique"""
    bloc_id: str
    questionnaire_data: Dict[str, Any]
    previous_results: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    """Requête pour le chatbot"""
    question: str
    analysis_data: Dict[str, Any] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PRINCIPAUX
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT PROGRESSIF - SYSTÈME OPTIMISÉ
# ═══════════════════════════════════════════════════════════════════════════════

def _prepare_questionnaire_data(data: AnalyzeRequestV2) -> Dict[str, Any]:
    """Prépare les données du questionnaire pour les assistants"""
    return {
        "secteur": data.secteur,
        "profilOrganisation": data.profilOrganisation,
        "paysInstallation": data.paysInstallation,
        "zoneGeographique": data.zoneGeographique,
        "biensServices": data.biensServices,
        "autresBiensServices": data.autresBiensServices,
        "oddAutomatiques": data.oddAutomatiques or data.objectifsDD,
        "oddManuels": data.oddManuels,
        "objectifsDD": data.objectifsDD,
        "visionOrganisation": data.visionOrganisation,
        "missionOrganisation": data.missionOrganisation,
        "projetsSignificatifs": data.projetsSignificatifs,
        "fichiers": data.fichiers,
        "fichiersContext": data.fichiersContext,
        "profil": data.profilOrganisation,
        "pays": data.paysInstallation,
        "zone": data.zoneGeographique,
        "marcheCible": data.zoneGeographique,
    }


async def _run_remaining_blocs(session_id: str):
    """
    Tâche background qui exécute les blocs 2-7 après BLOC1
    """
    session = ANALYSIS_SESSIONS.get(session_id)
    if not session:
        logger.error(f"Session {session_id} not found")
        return
    
    questionnaire_data = session["questionnaire_data"]
    bloc1_result = session["blocs"]["BLOC1"]["result"]
    
    try:
        # ─────────────────────────────────────────────────────────────────
        # PHASE 2 : BLOC2, BLOC3, BLOC4 en PARALLÈLE
        # ─────────────────────────────────────────────────────────────────
        logger.info(f"[{session_id}] 📊 Phase 2: Blocs 2, 3, 4 en parallèle")
        
        context_phase2 = {"BLOC1": bloc1_result}
        
        async def run_with_update(bloc_id: str, context: Dict):
            try:
                ANALYSIS_SESSIONS[session_id]["blocs"][bloc_id]["status"] = "running"
                result = await openai_assistant_service._run_bloc(bloc_id, questionnaire_data, context)
                ANALYSIS_SESSIONS[session_id]["blocs"][bloc_id] = {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                }
                logger.info(f"[{session_id}] ✅ {bloc_id} terminé")
                return result
            except Exception as e:
                ANALYSIS_SESSIONS[session_id]["blocs"][bloc_id] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"[{session_id}] ❌ {bloc_id} échoué: {e}")
                return None
        
        # Marquer les blocs comme en cours
        for bloc_id in ["BLOC2", "BLOC3", "BLOC4"]:
            ANALYSIS_SESSIONS[session_id]["blocs"][bloc_id] = {"status": "running"}
        
        phase2_results = await asyncio.gather(
            run_with_update("BLOC2", context_phase2),
            run_with_update("BLOC3", context_phase2),
            run_with_update("BLOC4", context_phase2),
            return_exceptions=True
        )
        
        bloc2_result = phase2_results[0] if not isinstance(phase2_results[0], Exception) else None
        bloc3_result = phase2_results[1] if not isinstance(phase2_results[1], Exception) else None
        bloc4_result = phase2_results[2] if not isinstance(phase2_results[2], Exception) else None
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 3 : BLOC5 (dépend de BLOC1 + BLOC2)
        # ─────────────────────────────────────────────────────────────────
        logger.info(f"[{session_id}] 📊 Phase 3: BLOC5")
        ANALYSIS_SESSIONS[session_id]["blocs"]["BLOC5"] = {"status": "running"}
        
        context_phase3 = {"BLOC1": bloc1_result, "BLOC2": bloc2_result}
        bloc5_result = await run_with_update("BLOC5", context_phase3)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 4 : BLOC6 (dépend de BLOC1 + BLOC2 + BLOC5)
        # ─────────────────────────────────────────────────────────────────
        logger.info(f"[{session_id}] 📊 Phase 4: BLOC6")
        ANALYSIS_SESSIONS[session_id]["blocs"]["BLOC6"] = {"status": "running"}
        
        context_phase4 = {"BLOC1": bloc1_result, "BLOC2": bloc2_result, "BLOC5": bloc5_result}
        bloc6_result = await run_with_update("BLOC6", context_phase4)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 5 : BLOC7 (Synthèse - tous les blocs)
        # ─────────────────────────────────────────────────────────────────
        logger.info(f"[{session_id}] 📊 Phase 5: BLOC7 (Synthèse)")
        ANALYSIS_SESSIONS[session_id]["blocs"]["BLOC7"] = {"status": "running"}
        
        context_phase5 = {
            "BLOC1": bloc1_result,
            "BLOC2": bloc2_result,
            "BLOC3": bloc3_result,
            "BLOC4": bloc4_result,
            "BLOC5": bloc5_result,
            "BLOC6": bloc6_result
        }
        await run_with_update("BLOC7", context_phase5)
        
        # ─────────────────────────────────────────────────────────────────
        # MARQUER LA SESSION COMME TERMINÉE
        # ─────────────────────────────────────────────────────────────────
        ANALYSIS_SESSIONS[session_id]["status"] = "completed"
        ANALYSIS_SESSIONS[session_id]["completed_at"] = datetime.now().isoformat()
        logger.info(f"[{session_id}] ✅ Analyse complète terminée!")
        
    except Exception as e:
        ANALYSIS_SESSIONS[session_id]["status"] = "error"
        ANALYSIS_SESSIONS[session_id]["error"] = str(e)
        logger.error(f"[{session_id}] ❌ Erreur globale: {e}")


@app.post("/api/analyze/start")
async def start_analysis(data: AnalyzeRequestV2, background_tasks: BackgroundTasks):
    """
    🚀 DÉMARRAGE ANALYSE PROGRESSIVE
    
    1. Exécute BLOC1 (PESTEL+) immédiatement
    2. Retourne le résultat BLOC1 + session_id
    3. Lance les 6 autres blocs en background
    
    Le frontend redirige vers le dashboard dès que BLOC1 est prêt !
    """
    try:
        session_id = str(uuid.uuid4())[:8]
        
        logger.info("═" * 60)
        logger.info(f"🚀 [{session_id}] Nouvelle analyse progressive")
        logger.info(f"   Profil: {data.profilOrganisation} | Pays: {data.paysInstallation}")
        logger.info("═" * 60)
        
        questionnaire_data = _prepare_questionnaire_data(data)
        
        # Créer la session
        ANALYSIS_SESSIONS[session_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "questionnaire_data": questionnaire_data,
            "metadata": {
                "profil": data.profilOrganisation,
                "secteur": data.secteur,
                "pays": data.paysInstallation,
                "zone": data.zoneGeographique
            },
            "blocs": {
                "BLOC1": {"status": "running"},
                "BLOC2": {"status": "pending"},
                "BLOC3": {"status": "pending"},
                "BLOC4": {"status": "pending"},
                "BLOC5": {"status": "pending"},
                "BLOC6": {"status": "pending"},
                "BLOC7": {"status": "pending"}
            }
        }
        
        # Exécuter BLOC1 immédiatement
        logger.info(f"[{session_id}] 📊 Exécution BLOC1 (PESTEL+)...")
        bloc1_result = await openai_assistant_service._run_bloc("BLOC1", questionnaire_data, {})
        
        ANALYSIS_SESSIONS[session_id]["blocs"]["BLOC1"] = {
            "status": "completed",
            "result": bloc1_result,
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"[{session_id}] ✅ BLOC1 terminé, lancement des autres en background")
        
        # Lancer les autres blocs en background
        background_tasks.add_task(_run_remaining_blocs, session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "BLOC1 terminé, autres blocs en cours de génération",
            "bloc1": bloc1_result,
            "metadata": ANALYSIS_SESSIONS[session_id]["metadata"]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyze/status/{session_id}")
async def get_analysis_status(session_id: str):
    """
    📊 STATUT DE L'ANALYSE EN TEMPS RÉEL
    
    Retourne l'état de chaque bloc :
    - pending : En attente
    - running : En cours
    - completed : Terminé (avec résultat)
    - error : Erreur
    """
    session = ANALYSIS_SESSIONS.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} non trouvée")
    
    # Calculer le pourcentage de completion
    blocs_done = sum(1 for b in session["blocs"].values() if b.get("status") == "completed")
    progress = int((blocs_done / 7) * 100)
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "progress": progress,
        "blocs_completed": blocs_done,
        "blocs_total": 7,
        "metadata": session.get("metadata", {}),
        "blocs": {
            bloc_id: {
                "status": bloc_data.get("status"),
                "name": BLOC_NAMES.get(bloc_id),
                "result": bloc_data.get("result") if bloc_data.get("status") == "completed" else None,
                "error": bloc_data.get("error") if bloc_data.get("status") == "error" else None
            }
            for bloc_id, bloc_data in session["blocs"].items()
        }
    }


@app.get("/api/analyze/result/{session_id}")
async def get_full_analysis_result(session_id: str):
    """
    📥 RÉSULTAT COMPLET DE L'ANALYSE
    
    Retourne tous les blocs terminés.
    """
    session = ANALYSIS_SESSIONS.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} non trouvée")
    
    blocs_results = {}
    for bloc_id, bloc_data in session["blocs"].items():
        if bloc_data.get("status") == "completed" and bloc_data.get("result"):
            blocs_results[bloc_id] = bloc_data["result"]
    
    return {
        "success": True,
        "session_id": session_id,
        "status": session["status"],
        "metadata": session.get("metadata", {}),
        "blocs": blocs_results
    }


@app.post("/api/analyze")
async def analyze_company(data: AnalyzeRequestV2, background_tasks: BackgroundTasks):
    """
    🚀 ANALYSE COMPLÈTE - 7 BLOCS (Version synchrone)
    
    Pour compatibilité, lance une analyse complète et attend tous les blocs.
    Préférez /api/analyze/start pour une meilleure UX.
    """
    try:
        logger.info("═" * 60)
        logger.info(f"🚀 Nouvelle analyse complète - Profil: {data.profilOrganisation}")
        logger.info(f"   Pays: {data.paysInstallation} | Secteur: {data.secteur}")
        logger.info("═" * 60)
        
        questionnaire_data = _prepare_questionnaire_data(data)
        blocs_applicables = get_blocs_for_profil(data.profilOrganisation)
        logger.info(f"📋 Blocs à générer: {blocs_applicables}")
        
        result = await openai_assistant_service.analyze_company(questionnaire_data)
        
        if isinstance(result, dict) and "metadata" in result:
            result["metadata"]["blocs_demandes"] = blocs_applicables
        
        logger.info("✅ Analyse complète terminée avec succès")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse IA: {str(e)}"
        )


@app.post("/api/analyze/bloc")
async def analyze_single_bloc(data: BlocAnalyzeRequest):
    """
    📊 ANALYSE D'UN BLOC SPÉCIFIQUE
    
    Permet d'exécuter un seul bloc, utile pour :
    - Régénérer un bloc qui a échoué
    - Analyse incrémentale
    - Tests
    """
    try:
        bloc_id = data.bloc_id.upper()
        
        if bloc_id not in ASSISTANT_IDS:
            raise HTTPException(
                status_code=404, 
                detail=f"Bloc '{bloc_id}' non trouvé. Blocs valides: {list(ASSISTANT_IDS.keys())}"
            )
        
        logger.info(f"📊 Analyse bloc unique: {bloc_id} ({BLOC_NAMES.get(bloc_id)})")
        
        result = await openai_assistant_service.analyze_bloc(
            bloc_id=bloc_id,
            questionnaire_data=data.questionnaire_data,
            previous_results=data.previous_results
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur bloc {data.bloc_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du bloc: {str(e)}"
        )


@app.post("/api/analyze/bloc/{bloc_id}")
async def analyze_bloc_by_path(bloc_id: str, data: Dict[str, Any]):
    """
    📊 ANALYSE D'UN BLOC (via path parameter)
    Alternative à /api/analyze/bloc avec bloc_id dans le path
    """
    try:
        bloc_id = bloc_id.upper()
        
        if bloc_id not in ASSISTANT_IDS:
            raise HTTPException(
                status_code=404, 
                detail=f"Bloc '{bloc_id}' non trouvé"
            )
        
        logger.info(f"📊 Analyse bloc: {bloc_id}")
        
        result = await openai_assistant_service.analyze_bloc(
            bloc_id=bloc_id,
            questionnaire_data=data,
            previous_results=data.get("previous_results", {})
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur bloc {bloc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS INFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/blocs")
async def get_available_blocs():
    """
    📋 Liste des 7 blocs d'analyse disponibles
    """
    blocs = []
    for bloc_id, bloc_name in BLOC_NAMES.items():
        blocs.append({
            "id": bloc_id,
            "nom": bloc_name,
            "assistant_id": ASSISTANT_IDS.get(bloc_id, "Non configuré")[:20] + "..."
        })
    
    return {
        "total": len(blocs),
        "blocs": blocs
    }


@app.get("/api/blocs/profil/{profil}")
async def get_blocs_by_profil(profil: str):
    """
    📋 Blocs applicables pour un profil donné
    """
    blocs_ids = get_blocs_for_profil(profil)
    
    return {
        "profil": profil,
        "blocs_count": len(blocs_ids),
        "blocs": [
            {"id": bid, "nom": BLOC_NAMES.get(bid, bid)}
            for bid in blocs_ids
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHATBOT - Utilise Chat Completions pour réponses rapides
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/chat")
async def chat_with_analysis(data: ChatRequest):
    """
    💬 CHATBOT CONTEXTUEL - Questions sur l'analyse
    
    Utilise GPT-4o via Chat Completions pour des réponses rapides
    basées sur les données d'analyse des 7 blocs.
    """
    try:
        if not data.question:
            raise HTTPException(status_code=400, detail="Question requise")
        
        client = openai_assistant_service.client
        if not client:
            raise HTTPException(status_code=500, detail="OpenAI non configuré")
        
        logger.info(f"💬 Question chat: {data.question[:100]}...")
        
        # Extraire les points clés de chaque bloc pour le contexte
        analysis_summary = _build_analysis_context(data.analysis_data)
        
        # System prompt expert
        system_prompt = """Tu es un expert-conseil en stratégie d'entreprise durable pour l'Afrique.
Tu as accès aux résultats d'une analyse stratégique complète en 7 blocs :
- BLOC 1: PESTEL+ (environnement macro)
- BLOC 2: Risques Climat & Transition
- BLOC 3: Marché & Concurrence
- BLOC 4: Chaîne de Valeur
- BLOC 5: ODD & Durabilité
- BLOC 6: Cadre Réglementaire
- BLOC 7: Synthèse Stratégique

RÈGLES DE RÉPONSE:
1. Réponds TOUJOURS en français
2. Sois concis mais complet (2-4 paragraphes max)
3. Cite des données chiffrées et indices quand pertinent
4. Si tu n'as pas l'info, dis-le clairement
5. Utilise des émojis pour structurer (📊 🎯 ⚠️ 💡)
6. Ton professionnel mais accessible"""

        # Appel API Chat Completions (rapide)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""CONTEXTE D'ANALYSE:
{analysis_summary}

QUESTION DE L'UTILISATEUR:
{data.question}

Réponds de manière claire et utile en te basant sur les données ci-dessus."""}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        logger.info(f"✅ Réponse chat générée ({len(answer)} chars)")
        
        return {
            "answer": answer,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_analysis_context(analysis_data: dict) -> str:
    """
    Construit un résumé structuré des analyses pour le contexte du chat.
    """
    if not analysis_data:
        return "Aucune analyse disponible."
    
    context_parts = []
    
    # Metadata
    if "metadata" in analysis_data:
        meta = analysis_data["metadata"]
        context_parts.append(f"""📋 PROFIL:
- Pays: {meta.get('pays', 'N/A')}
- Secteur: {meta.get('secteur', 'N/A')}
- Profil: {meta.get('profil', 'N/A')}""")
    
    # BLOC 1 - PESTEL
    if "BLOC1" in analysis_data:
        b1 = analysis_data["BLOC1"]
        indices_b1 = b1.get("indices", {})
        context_parts.append(f"""🌍 BLOC1 - PESTEL+:
- Score Global: {indices_b1.get('pestel_global', {}).get('score', 'N/A')}/100
- Climat: {indices_b1.get('climat', {}).get('score', 'N/A')}/100
- Synthèse: {str(b1.get('synthese_strategique', {}))[:500]}""")
    
    # BLOC 2 - Risques Climat
    if "BLOC2" in analysis_data:
        b2 = analysis_data["BLOC2"]
        indices_b2 = b2.get("indices", {})
        context_parts.append(f"""🌡️ BLOC2 - Risques Climat:
- Risques Climatiques: {indices_b2.get('risques_climatiques', {}).get('score', 'N/A')}/100
- Opportunités Transition: {indices_b2.get('opportunites_transition', {}).get('score', 'N/A')}/100
- Synthèse: {str(b2.get('synthese_strategique', {}))[:500]}""")
    
    # BLOC 3 - Marché
    if "BLOC3" in analysis_data:
        b3 = analysis_data["BLOC3"]
        indices_b3 = b3.get("indices", {})
        context_parts.append(f"""📈 BLOC3 - Marché & Concurrence:
- Attractivité: {indices_b3.get('attractivite', {}).get('score', 'N/A')}/100
- Concurrence: {indices_b3.get('concurrence', {}).get('score', 'N/A')}/100
- Synthèse: {str(b3.get('synthese_strategique', {}))[:500]}""")
    
    # BLOC 4 - Chaîne de valeur
    if "BLOC4" in analysis_data:
        b4 = analysis_data["BLOC4"]
        context_parts.append(f"""🔗 BLOC4 - Chaîne de Valeur:
- Indices: {str(b4.get('indices', {}))[:300]}
- Synthèse: {str(b4.get('synthese_strategique', {}))[:500]}""")
    
    # BLOC 5 - ODD
    if "BLOC5" in analysis_data:
        b5 = analysis_data["BLOC5"]
        indices_b5 = b5.get("indices", {})
        context_parts.append(f"""🎯 BLOC5 - ODD & Durabilité:
- Score ODD: {indices_b5.get('odd', {}).get('score', 'N/A')}/100
- Finance Durable: {indices_b5.get('finance_durable', {}).get('score', 'N/A')}/100
- Modèles Durables: {str(b5.get('modeles_durables', []))[:300]}""")
    
    # BLOC 6 - Réglementaire
    if "BLOC6" in analysis_data:
        b6 = analysis_data["BLOC6"]
        indices_b6 = b6.get("indices", {})
        context_parts.append(f"""⚖️ BLOC6 - Réglementaire:
- Taxonomie: {indices_b6.get('taxonomie', {}).get('score', 'N/A')}/100
- Net Zero: {indices_b6.get('netzero', {}).get('score', 'N/A')}/100
- Synthèse: {str(b6.get('synthese_reglementaire', {}))[:500]}""")
    
    # BLOC 7 - Synthèse
    if "BLOC7" in analysis_data:
        b7 = analysis_data["BLOC7"]
        context_parts.append(f"""📋 BLOC7 - Synthèse Stratégique:
- Introduction: {str(b7.get('introduction_executive', {}))[:400]}
- SWOT: {str(b7.get('diagnostic_swot_plus', {}))[:500]}
- Recommandations: {str(b7.get('conclusion_strategique', {}))[:500]}""")
    
    # Si pas de blocs structurés, utiliser les données brutes
    if len(context_parts) <= 1:
        context_parts.append(f"Données brutes: {str(analysis_data)[:3000]}")
    
    return "\n\n".join(context_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT ET ENRICHISSEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/enrich")
async def enrich_analysis(data: dict):
    """
    ✨ Enrichit les analyses avec des résumés et points clés
    """
    try:
        from app.services.openrouter_service import openrouter_service
        
        analyses = data.get("analyses", {})
        if not analyses:
            raise HTTPException(status_code=400, detail="Analyses requises")
        
        logger.info("✨ Enrichissement des analyses...")
        
        enriched_analyses = await openrouter_service.enrich_all_tabs(analyses)
        enriched_synthesis = await openrouter_service.generate_synthesis(analyses)
        
        return {
            "success": True,
            "enriched_analyses": enriched_analyses,
            "enriched_synthesis": enriched_synthesis
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur enrichissement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/pdf")
async def export_to_pdf(data: dict):
    """
    📄 Export PDF (à implémenter)
    """
    return {
        "status": "pending",
        "message": "Export PDF en cours de développement"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ET INFO
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """
    ❤️ Health check - Vérifie tous les assistants
    """
    try:
        assistant_status = await openai_assistant_service.health_check()
        
        return {
            "status": assistant_status.get("status", "unknown"),
            "version": "2.0.0",
            "openai_configured": bool(openai_assistant_service.client),
            "assistants": assistant_status.get("assistants", {})
        }
    except Exception as e:
        return {
            "status": "error",
            "version": "2.0.0",
            "error": str(e)
        }


@app.get("/")
async def root():
    """
    🏠 Page d'accueil de l'API
    """
    return {
        "name": "Africa Strategy API",
        "version": "2.0.0",
        "description": "API avec 7 Assistants OpenAI spécialisés",
        "architecture": {
            "BLOC1": "PESTEL+ (Analyse macro-durable)",
            "BLOC2": "Risques Climat & ESG",
            "BLOC3": "Marché & Concurrence",
            "BLOC4": "Chaîne de Valeur",
            "BLOC5": "Modèles Durables & ODD",
            "BLOC6": "Cadre Réglementaire",
            "BLOC7": "Synthèse Stratégique"
        },
        "endpoints": {
            "POST /api/analyze": "Analyse complète (7 blocs)",
            "POST /api/analyze/bloc": "Analyse d'un bloc spécifique",
            "GET /api/blocs": "Liste des blocs disponibles",
            "GET /api/blocs/profil/{profil}": "Blocs par profil",
            "POST /api/chat": "Chatbot sur l'analyse",
            "GET /health": "État des assistants"
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
