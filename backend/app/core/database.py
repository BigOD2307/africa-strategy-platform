"""
Configuration de la base de données pour Africa Strategy
Développé par Ousmane Dicko
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Configuration de l'engine SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Métadonnées pour les migrations
metadata = MetaData()


def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Erreur de base de données", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialisation de la base de données"""
    try:
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error("Erreur lors de l'initialisation de la base de données", error=str(e))
        raise
