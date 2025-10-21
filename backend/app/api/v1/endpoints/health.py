"""
Endpoints de santé pour Africa Strategy
Développé par Ousmane Dicko
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "service": "Africa Strategy API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/database")
async def database_health(db: Session = Depends(get_db)):
    """Vérification de la connexion à la base de données"""
    try:
        # Test simple de connexion
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Base de données accessible"
        }
    except Exception as e:
        logger.error("Erreur de connexion à la base de données", error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Base de données inaccessible"
        )


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Vérification détaillée de tous les services"""
    health_status = {
        "status": "healthy",
        "service": "Africa Strategy API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Vérification base de données
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Connexion établie"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Erreur: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Vérification Redis (à implémenter plus tard)
    health_status["checks"]["redis"] = {
        "status": "not_implemented",
        "message": "Vérification Redis non implémentée"
    }
    
    # Vérification OpenAI (à implémenter plus tard)
    health_status["checks"]["openai"] = {
        "status": "not_implemented",
        "message": "Vérification OpenAI non implémentée"
    }
    
    # Vérification Pinecone (à implémenter plus tard)
    health_status["checks"]["pinecone"] = {
        "status": "not_implemented",
        "message": "Vérification Pinecone non implémentée"
    }
    
    return health_status
