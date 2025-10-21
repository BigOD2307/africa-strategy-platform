"""
Endpoints utilisateurs pour Africa Strategy
Développé par Ousmane Dicko
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import User
import structlog

router = APIRouter()
logger = structlog.get_logger()


# Schémas Pydantic
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    company_name: str = None
    phone: str = None
    country: str
    city: str = None
    sector: str
    company_size: str = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    company_name: str = None
    phone: str = None
    city: str = None
    sector: str = None
    company_size: str = None


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des utilisateurs"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Récupérer un utilisateur par ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    db_user = User(
        email=user.email,
        password_hash=f"hashed_{user.password}",  # TODO: Implémenter le hachage réel
        first_name=user.first_name,
        last_name=user.last_name,
        company_name=user.company_name,
        phone=user.phone,
        country=user.country,
        city=user.city,
        sector=user.sector,
        company_size=user.company_size
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info("Nouvel utilisateur créé", user_id=str(db_user.id), email=user.email)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un utilisateur"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Mettre à jour les champs fournis
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    logger.info("Utilisateur mis à jour", user_id=str(user_id))
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Supprimer un utilisateur"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    db.delete(user)
    db.commit()
    
    logger.info("Utilisateur supprimé", user_id=str(user_id))
    return None
