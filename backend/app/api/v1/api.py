"""
Main API router for Africa Strategy v1
Combines all endpoint modules into a single API
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    users,
    questionnaires,
    analyses,
    roadmaps,
    configuration,
    rag
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    questionnaires.router,
    prefix="/questionnaires",
    tags=["questionnaires"]
)

api_router.include_router(
    analyses.router,
    prefix="/analyses",
    tags=["analyses"]
)

api_router.include_router(
    roadmaps.router,
    prefix="/roadmaps",
    tags=["roadmaps"]
)

api_router.include_router(
    configuration.router,
    prefix="/configuration",
    tags=["configuration"]
)

api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["rag"]
)
