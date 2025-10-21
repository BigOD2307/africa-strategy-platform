"""
Endpoints roadmaps pour Africa Strategy
Développé par Ousmane Dicko
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import Roadmap, RoadmapStep, User
import structlog

router = APIRouter()
logger = structlog.get_logger()


# Schémas Pydantic
class RoadmapStepResponse(BaseModel):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    title: str
    description: str = None
    phase: str
    order_index: int
    status: str
    priority: str
    estimated_cost: float = None
    estimated_duration_days: int = None
    actual_cost: float = None
    actual_duration_days: int = None
    completion_date: datetime = None
    documents: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoadmapResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str = None
    current_phase: str
    progress_percentage: int
    phases: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    steps: List[RoadmapStepResponse] = []

    class Config:
        from_attributes = True


class RoadmapCreate(BaseModel):
    user_id: uuid.UUID
    title: str
    description: str = None


class RoadmapStepCreate(BaseModel):
    roadmap_id: uuid.UUID
    title: str
    description: str = None
    phase: str
    order_index: int
    priority: str = "medium"
    estimated_cost: float = None
    estimated_duration_days: int = None


@router.get("/", response_model=List[RoadmapResponse])
async def get_roadmaps(
    skip: int = 0,
    limit: int = 100,
    user_id: uuid.UUID = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des roadmaps"""
    query = db.query(Roadmap)
    
    if user_id:
        query = query.filter(Roadmap.user_id == user_id)
    
    roadmaps = query.offset(skip).limit(limit).all()
    return roadmaps


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Récupérer une roadmap par ID"""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap non trouvée"
        )
    
    return roadmap


@router.post("/", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    roadmap: RoadmapCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle roadmap"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == roadmap.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Créer la nouvelle roadmap
    db_roadmap = Roadmap(
        user_id=roadmap.user_id,
        title=roadmap.title,
        description=roadmap.description,
        current_phase="diagnostic",
        progress_percentage=0,
        phases=[
            {
                "id": "diagnostic",
                "name": "Diagnostic",
                "status": "completed",
                "description": "Analyse de la situation actuelle"
            },
            {
                "id": "quick_wins",
                "name": "Quick Wins",
                "status": "in_progress",
                "description": "Actions rapides à impact immédiat"
            },
            {
                "id": "transformation",
                "name": "Transformation",
                "status": "locked",
                "description": "Changements structurels majeurs"
            }
        ],
        milestones=[]
    )
    
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    
    logger.info(
        "Nouvelle roadmap créée",
        roadmap_id=str(db_roadmap.id),
        user_id=str(roadmap.user_id)
    )
    
    return db_roadmap


@router.post("/{roadmap_id}/steps", response_model=RoadmapStepResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap_step(
    roadmap_id: uuid.UUID,
    step: RoadmapStepCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle étape de roadmap"""
    # Vérifier que la roadmap existe
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap non trouvée"
        )
    
    # Créer la nouvelle étape
    db_step = RoadmapStep(
        roadmap_id=roadmap_id,
        title=step.title,
        description=step.description,
        phase=step.phase,
        order_index=step.order_index,
        priority=step.priority,
        estimated_cost=step.estimated_cost,
        estimated_duration_days=step.estimated_duration_days,
        status="pending",
        documents=[]
    )
    
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    
    logger.info(
        "Nouvelle étape créée",
        step_id=str(db_step.id),
        roadmap_id=str(roadmap_id)
    )
    
    return db_step


@router.put("/{roadmap_id}/steps/{step_id}/status")
async def update_step_status(
    roadmap_id: uuid.UUID,
    step_id: uuid.UUID,
    status: str,
    db: Session = Depends(get_db)
):
    """Mettre à jour le statut d'une étape"""
    step = db.query(RoadmapStep).filter(
        RoadmapStep.id == step_id,
        RoadmapStep.roadmap_id == roadmap_id
    ).first()
    
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étape non trouvée"
        )
    
    step.status = status
    
    if status == "completed":
        step.completion_date = datetime.utcnow()
    
    db.commit()
    
    logger.info(
        "Statut d'étape mis à jour",
        step_id=str(step_id),
        status=status
    )
    
    return {
        "message": "Statut mis à jour avec succès",
        "step_id": str(step_id),
        "status": status
    }


@router.get("/{roadmap_id}/steps", response_model=List[RoadmapStepResponse])
async def get_roadmap_steps(
    roadmap_id: uuid.UUID,
    phase: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Récupérer les étapes d'une roadmap"""
    query = db.query(RoadmapStep).filter(RoadmapStep.roadmap_id == roadmap_id)
    
    if phase:
        query = query.filter(RoadmapStep.phase == phase)
    if status:
        query = query.filter(RoadmapStep.status == status)
    
    steps = query.order_by(RoadmapStep.order_index).all()
    return steps
