"""
Routeur principal API v1 pour Africa Strategy
Développé par Ousmane Dicko
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, users, questionnaires, analyses, roadmaps, configuration

api_router = APIRouter()

# Inclusion des routes
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(questionnaires.router, prefix="/questionnaires", tags=["questionnaires"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
