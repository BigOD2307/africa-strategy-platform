"""
Endpoints questionnaires pour Africa Strategy
Développé par Ousmane Dicko
"""

from fastapi import APIRouter, Depends, HTTPException, status
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


@router.post("/", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
async def create_questionnaire(
    questionnaire: QuestionnaireCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouveau questionnaire"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == questionnaire.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Créer le nouveau questionnaire
    db_questionnaire = Questionnaire(
        user_id=questionnaire.user_id,
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
        user_id=str(questionnaire.user_id)
    )
    
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
