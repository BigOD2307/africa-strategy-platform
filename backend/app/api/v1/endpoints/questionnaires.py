"""
Endpoints questionnaires pour Africa Strategy
Développé par Ousmane Dicko
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import Questionnaire, User
import structlog

router = APIRouter()
logger = structlog.get_logger()


# Schémas Pydantic
class QuestionnaireBase(BaseModel):
    title: str
    description: str = None


class QuestionnaireCreate(QuestionnaireBase):
    user_id: uuid.UUID


class QuestionnaireUpdate(BaseModel):
    title: str = None
    description: str = None
    responses: Dict[str, Any] = None
    status: str = None
    completion_percentage: int = None


class QuestionnaireResponse(QuestionnaireBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    responses: Dict[str, Any]
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[QuestionnaireResponse])
async def get_questionnaires(
    skip: int = 0,
    limit: int = 100,
    user_id: uuid.UUID = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des questionnaires"""
    query = db.query(Questionnaire)
    
    if user_id:
        query = query.filter(Questionnaire.user_id == user_id)
    if status:
        query = query.filter(Questionnaire.status == status)
    
    questionnaires = query.offset(skip).limit(limit).all()
    return questionnaires


@router.get("/{questionnaire_id}", response_model=QuestionnaireResponse)
async def get_questionnaire(
    questionnaire_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Récupérer un questionnaire par ID"""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire non trouvé"
        )
    
    return questionnaire


@router.get("/{questionnaire_id}/analysis-results")
async def get_analysis_results(
    questionnaire_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Récupérer tous les résultats d'analyse pour un questionnaire"""
    from app.models import PestelAnalysis, EsgAnalysis
    
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire non trouvé"
        )
    
    # Récupérer les analyses
    pestel_analysis = db.query(PestelAnalysis).filter(
        PestelAnalysis.questionnaire_id == questionnaire_id
    ).first()
    
    esg_analysis = db.query(EsgAnalysis).filter(
        EsgAnalysis.questionnaire_id == questionnaire_id
    ).first()
    
    return {
        "questionnaire_id": str(questionnaire_id),
        "questionnaire_status": questionnaire.status,
        "pestel_analysis": {
            "available": pestel_analysis is not None,
            "scores": {
                "political": pestel_analysis.political_score if pestel_analysis else None,
                "economic": pestel_analysis.economic_score if pestel_analysis else None,
                "social": pestel_analysis.social_score if pestel_analysis else None,
                "technological": pestel_analysis.technological_score if pestel_analysis else None,
                "environmental": pestel_analysis.environmental_score if pestel_analysis else None,
                "legal": pestel_analysis.legal_score if pestel_analysis else None,
                "overall": float(pestel_analysis.overall_score) if pestel_analysis and pestel_analysis.overall_score else None
            },
            "analysis_details": pestel_analysis.analysis_details if pestel_analysis else {},
            "recommendations": pestel_analysis.recommendations if pestel_analysis else []
        } if pestel_analysis else None,
        "esg_analysis": {
            "available": esg_analysis is not None,
            "scores": {
                "environmental": esg_analysis.environmental_score if esg_analysis else None,
                "social": esg_analysis.social_score if esg_analysis else None,
                "governance": esg_analysis.governance_score if esg_analysis else None,
                "overall": esg_analysis.overall_score if esg_analysis else None
            },
            "details": {
                "environmental": esg_analysis.environmental_details if esg_analysis else {},
                "social": esg_analysis.social_details if esg_analysis else {},
                "governance": esg_analysis.governance_details if esg_analysis else {}
            },
            "recommendations": esg_analysis.recommendations if esg_analysis else []
        } if esg_analysis else None
    }


@router.post("/", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
async def create_questionnaire(
    questionnaire: QuestionnaireCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouveau questionnaire"""
    # Pour la v1, créer un utilisateur par défaut si nécessaire
    user_id = questionnaire.user_id
    
    # Si l'utilisateur n'existe pas, créer un utilisateur par défaut
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Créer un utilisateur par défaut pour la v1
        default_user = User(
            id=user_id,
            email=f"user_{user_id}@africa-strategy.com",
            password_hash="default",  # En production, utiliser un vrai hash
            first_name="Entrepreneur",
            last_name="Africa Strategy",
            country="Côte d'Ivoire",
            sector="Général",
            is_active=True,
            is_verified=False
        )
        db.add(default_user)
        db.commit()
        logger.info(f"Utilisateur par défaut créé: {user_id}")
    
    # Créer le nouveau questionnaire
    db_questionnaire = Questionnaire(
        user_id=user_id,
        title=questionnaire.title,
        description=questionnaire.description,
        status="draft",
        responses={},
        completion_percentage=0
    )
    
    db.add(db_questionnaire)
    db.commit()
    db.refresh(db_questionnaire)
    
    logger.info(
        "Nouveau questionnaire créé",
        questionnaire_id=str(db_questionnaire.id),
        user_id=str(user_id)
    )
    
    # Retourner le questionnaire (Pydantic convertira automatiquement les UUID en string)
    return db_questionnaire


@router.put("/{questionnaire_id}", response_model=QuestionnaireResponse)
async def update_questionnaire(
    questionnaire_id: uuid.UUID,
    questionnaire_update: QuestionnaireUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un questionnaire"""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire non trouvé"
        )
    
    # Mettre à jour les champs fournis
    update_data = questionnaire_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(questionnaire, field, value)
    
    # Si le questionnaire est marqué comme complété
    if questionnaire_update.status == "completed":
        questionnaire.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(questionnaire)
    
    logger.info("Questionnaire mis à jour", questionnaire_id=str(questionnaire_id))
    return questionnaire


@router.post("/{questionnaire_id}/save-responses")
async def save_responses(
    questionnaire_id: uuid.UUID,
    responses: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Sauvegarder les réponses d'un questionnaire"""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire non trouvé"
        )
    
    # Mettre à jour les réponses
    questionnaire.responses = responses
    
    # Calculer le pourcentage de completion
    total_questions = len(responses.get("questions_esg", {}))
    answered_questions = sum(1 for v in responses.get("questions_esg", {}).values() if v is not None)
    questionnaire.completion_percentage = int((answered_questions / total_questions * 100)) if total_questions > 0 else 0
    
    db.commit()
    
    logger.info(
        "Réponses sauvegardées",
        questionnaire_id=str(questionnaire_id),
        completion_percentage=questionnaire.completion_percentage
    )
    
    return {
        "message": "Réponses sauvegardées avec succès",
        "completion_percentage": questionnaire.completion_percentage
    }


@router.post("/{questionnaire_id}/analyze")
async def trigger_ai_analysis(
    questionnaire_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Déclencher l'analyse IA complète après complétion du questionnaire
    
    Cette endpoint :
    1. Récupère le questionnaire complété
    2. Extrait les données de l'entreprise
    3. Déclenche toutes les analyses IA (PESTEL, ESG, etc.)
    4. Sauvegarde les résultats en base de données
    """
    from fastapi import BackgroundTasks
    from app.services.ai_service import enhanced_ai_service
    from app.models import PestelAnalysis, EsgAnalysis
    
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire non trouvé"
        )
    
    if questionnaire.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le questionnaire doit être complété avant l'analyse"
        )
    
    # Extraire les données de l'entreprise depuis les réponses
    responses = questionnaire.responses or {}
    company_data = {
        "company_name": responses.get("company_name", "Entreprise"),
        "sector": responses.get("secteur", ""),
        "country": responses.get("paysInstallation", ""),
        "zone_geographique": responses.get("zoneGeographique", ""),
        "profil_organisation": responses.get("profilOrganisation", ""),
        "biens_services": responses.get("biensServices", []),
        "objectifs_dd": responses.get("objectifsDD", []),
        "positionnement_strategique": responses.get("positionnementStrategique", ""),
        "vision": responses.get("visionOrganisation", ""),
        "mission": responses.get("missionOrganisation", ""),
        "projets_significatifs": responses.get("projetsSignificatifs", "")
    }
    
    # Extraire les réponses ESG si disponibles
    esg_responses = responses.get("questions_esg", {})
    
    try:
        logger.info(f"Démarrage de l'analyse IA pour le questionnaire {questionnaire_id}")
        
        # Déclencher l'analyse intégrale en arrière-plan
        # Note: On passe les données nécessaires, pas la session DB
        background_tasks.add_task(
            _run_full_analysis,
            str(questionnaire_id),
            company_data,
            esg_responses
        )
        
        return {
            "message": "Analyse IA démarrée avec succès",
            "questionnaire_id": str(questionnaire_id),
            "status": "processing",
            "estimated_time": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'analyse: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du démarrage de l'analyse: {str(e)}"
        )


async def _run_full_analysis(
    questionnaire_id_str: str,
    company_data: Dict[str, Any],
    esg_responses: Dict[str, Any]
):
    """Fonction d'arrière-plan pour exécuter l'analyse complète via OpenAI Assistant"""
    from app.services.openai_assistant_service import openai_assistant_service
    from app.models import PestelAnalysis, EsgAnalysis
    from app.core.database import SessionLocal
    
    questionnaire_id = uuid.UUID(questionnaire_id_str)
    db = SessionLocal()
    
    try:
        # Préparer les données du questionnaire pour l'assistant
        questionnaire_data = {
            **company_data,
            "questions_esg": esg_responses
        }
        
        # Appeler l'assistant OpenAI
        logger.info("Démarrage analyse via OpenAI Assistant...")
        analysis_result = await openai_assistant_service.analyze_company(questionnaire_data)
        
        logger.info("Analyse complète reçue de l'assistant OpenAI")
        
        # Extraire et sauvegarder les analyses
        analyses = analysis_result.get("analyses", {})
        pipeline = analysis_result.get("pipeline_analytique", {})
        
        # 1. Sauvegarder PESTEL
        if "pestel" in analyses:
            pestel_data = analyses["pestel"]
            scores = pestel_data.get("scores", {})
            
            pestel_analysis = PestelAnalysis(
                questionnaire_id=questionnaire_id,
                political_score=int(scores.get("politique", 0) * 10) if scores.get("politique") else 0,
                economic_score=int(scores.get("economique", 0) * 10) if scores.get("economique") else 0,
                social_score=int(scores.get("social", 0) * 10) if scores.get("social") else 0,
                technological_score=int(scores.get("technologique", 0) * 10) if scores.get("technologique") else 0,
                environmental_score=int(scores.get("environnemental", 0) * 10) if scores.get("environnemental") else 0,
                legal_score=int(scores.get("legal", 0) * 10) if scores.get("legal") else 0,
                overall_score=float(scores.get("overall", 0)),
                analysis_details=pestel_data.get("analyse_detaillee", {}),
                recommendations=pestel_data.get("recommandations_prioritaires", [])
            )
            db.add(pestel_analysis)
        
        # 2. Sauvegarder ESG
        if "esg" in analyses:
            esg_data = analyses["esg"]
            scores = esg_data.get("scores", {})
            
            esg_analysis = EsgAnalysis(
                questionnaire_id=questionnaire_id,
                environmental_score=scores.get("environmental", 0),
                social_score=scores.get("social", 0),
                governance_score=scores.get("governance", 0),
                overall_score=scores.get("overall", 0),
                environmental_details=esg_data.get("analyse_detaillee", {}).get("environmental", {}),
                social_details=esg_data.get("analyse_detaillee", {}).get("social", {}),
                governance_details=esg_data.get("analyse_detaillee", {}).get("governance", {}),
                recommendations=esg_data.get("recommandations", [])
            )
            db.add(esg_analysis)
        
        # 3. Sauvegarder l'analyse complète dans les réponses du questionnaire
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.id == questionnaire_id
        ).first()
        if questionnaire:
            questionnaire.status = "analyzed"
            # Sauvegarder l'analyse complète dans les réponses
            current_responses = questionnaire.responses or {}
            current_responses["full_analysis"] = analysis_result
            questionnaire.responses = current_responses
        
        db.commit()
        logger.info(f"Analyse complète terminée et sauvegardée pour le questionnaire {questionnaire_id}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
        raise
    finally:
        db.close()


@router.delete("/{questionnaire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_questionnaire(
    questionnaire_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Supprimer un questionnaire"""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire non trouvé"
        )
    
    db.delete(questionnaire)
    db.commit()
    
    logger.info("Questionnaire supprimé", questionnaire_id=str(questionnaire_id))
    return None
