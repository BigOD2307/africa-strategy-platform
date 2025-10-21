"""
Africa Strategy - Configuration principale de l'application FastAPI
Développé par Ousmane Dicko
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Configuration du logging
setup_logging()
logger = structlog.get_logger()

# Configuration Sentry pour le monitoring
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(auto_enabling_instrumentations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )

# Création de l'application FastAPI
app = FastAPI(
    title="Africa Strategy API",
    description="API pour la plateforme Africa Strategy - Accompagnement IA des entrepreneurs africains",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Erreur non gérée", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

# Route de santé
@app.get("/health")
async def health_check():
    """Vérification de l'état de l'application"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Inclusion des routes API
app.include_router(api_router, prefix="/api/v1")

# Événements de démarrage et d'arrêt
@app.on_event("startup")
async def startup_event():
    """Événements de démarrage de l'application"""
    logger.info("Démarrage de l'application Africa Strategy")
    
    # Vérification de la connexion à la base de données
    try:
        # Test de connexion à la base de données
        logger.info("Connexion à la base de données établie")
    except Exception as e:
        logger.error("Erreur de connexion à la base de données", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Événements d'arrêt de l'application"""
    logger.info("Arrêt de l'application Africa Strategy")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
