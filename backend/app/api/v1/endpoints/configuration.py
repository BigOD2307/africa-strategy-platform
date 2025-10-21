from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models import EntrepreneurConfiguration

logger = logging.getLogger(__name__)

router = APIRouter()

# Schémas Pydantic pour la validation
class EntrepreneurConfigBase(BaseModel):
    secteur: str
    zoneGeographique: str
    profilOrganisation: str
    biensServices: List[str]
    autresBiensServices: Optional[str] = None
    paysInstallation: str
    objectifsDD: List[str]
    positionnementStrategique: str
    visionOrganisation: str
    missionOrganisation: str
    projetsSignificatifs: str

class EntrepreneurConfigCreate(EntrepreneurConfigBase):
    pass

class EntrepreneurConfigResponse(EntrepreneurConfigBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Endpoints API
@router.post("/entrepreneur", response_model=EntrepreneurConfigResponse)
async def create_entrepreneur_config(
    config: EntrepreneurConfigCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle configuration entrepreneur"""
    try:
        # Créer l'objet de configuration
        db_config = EntrepreneurConfiguration(
            secteur=config.secteur,
            zone_geographique=config.zoneGeographique,
            profil_organisation=config.profilOrganisation,
            biens_services=config.biensServices,
            autres_biens_services=config.autresBiensServices,
            pays_installation=config.paysInstallation,
            objectifs_dd=config.objectifsDD,
            positionnement_strategique=config.positionnementStrategique,
            vision_organisation=config.visionOrganisation,
            mission_organisation=config.missionOrganisation,
            projets_significatifs=config.projetsSignificatifs
        )

        # Sauvegarder en base de données
        db.add(db_config)
        db.commit()
        db.refresh(db_config)

        logger.info(f"Configuration entrepreneur créée avec succès: ID {db_config.id}")

        return db_config

    except Exception as e:
        logger.error(f"Erreur lors de la création de la configuration: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde de la configuration")

@router.get("/entrepreneur/{config_id}", response_model=EntrepreneurConfigResponse)
async def get_entrepreneur_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer une configuration entrepreneur par ID"""
    config = db.query(EntrepreneurConfiguration).filter(EntrepreneurConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration non trouvée")
    return config

@router.get("/entrepreneur", response_model=List[EntrepreneurConfigResponse])
async def get_all_entrepreneur_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer toutes les configurations entrepreneur"""
    configs = db.query(EntrepreneurConfiguration).offset(skip).limit(limit).all()
    return configs

@router.put("/entrepreneur/{config_id}", response_model=EntrepreneurConfigResponse)
async def update_entrepreneur_config(
    config_id: int,
    config: EntrepreneurConfigCreate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une configuration entrepreneur"""
    db_config = db.query(EntrepreneurConfiguration).filter(EntrepreneurConfiguration.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration non trouvée")

    try:
        # Mettre à jour les champs
        for field, value in config.dict().items():
            if hasattr(db_config, field):
                setattr(db_config, field, value)

        db.commit()
        db.refresh(db_config)

        logger.info(f"Configuration entrepreneur mise à jour: ID {config_id}")

        return db_config

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")

@router.delete("/entrepreneur/{config_id}")
async def delete_entrepreneur_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une configuration entrepreneur"""
    db_config = db.query(EntrepreneurConfiguration).filter(EntrepreneurConfiguration.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration non trouvée")

    try:
        db.delete(db_config)
        db.commit()

        logger.info(f"Configuration entrepreneur supprimée: ID {config_id}")

        return {"message": "Configuration supprimée avec succès"}

    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")