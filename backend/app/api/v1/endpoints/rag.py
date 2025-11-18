"""
RAG API endpoints for Africa Strategy
Manage document indexing and retrieval for enhanced AI analyses
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
import logging

from app.services.rag_service import rag_service

try:
    from app.services.data_import_service import data_import_service
    DATA_IMPORT_AVAILABLE = True
except ImportError:
    DATA_IMPORT_AVAILABLE = False
    data_import_service = None

logger = logging.getLogger(__name__)

router = APIRouter()


class DocumentInput(BaseModel):
    """Document input for RAG indexing"""
    content: str = Field(..., description="Document content to index")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")
    source: str = Field(..., description="Document source")
    category: str = Field(..., description="Document category")
    country: Optional[str] = Field("", description="Country relevance")
    sector: Optional[str] = Field("", description="Sector relevance")


class SearchQuery(BaseModel):
    """Search query for RAG retrieval"""
    query: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Search filters")
    top_k: Optional[int] = Field(5, description="Number of results", ge=1, le=20)


class ImportResponse(BaseModel):
    """Response for data import operations"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@router.post("/documents/add", response_model=ImportResponse)
async def add_document(document: DocumentInput) -> ImportResponse:
    """
    Add a single document to the RAG system

    This endpoint allows adding individual documents to enhance the AI's knowledge base
    for more accurate and contextually relevant analyses.
    """
    try:
        # Convert to RAG format
        rag_document = {
            'content': document.content,
            'metadata': document.metadata,
            'source': document.source,
            'category': document.category,
            'country': document.country,
            'sector': document.sector
        }

        success = await rag_service.add_documents([rag_document])

        if success:
            return ImportResponse(
                success=True,
                message="Document added successfully to RAG system",
                details={"documents_processed": 1}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to add document to RAG system"
            )

    except Exception as e:
        logger.error(f"Failed to add document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding document: {str(e)}"
        )


@router.post("/documents/batch-add", response_model=ImportResponse)
async def add_documents_batch(documents: List[DocumentInput]) -> ImportResponse:
    """
    Add multiple documents to the RAG system

    Batch endpoint for efficient bulk document indexing.
    """
    try:
        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No documents provided"
            )

        if len(documents) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 documents per batch"
            )

        # Convert to RAG format
        rag_documents = []
        for doc in documents:
            rag_documents.append({
                'content': doc.content,
                'metadata': doc.metadata,
                'source': doc.source,
                'category': doc.category,
                'country': doc.country,
                'sector': doc.sector
            })

        success = await rag_service.add_documents(rag_documents)

        if success:
            return ImportResponse(
                success=True,
                message=f"Successfully added {len(rag_documents)} documents to RAG system",
                details={"documents_processed": len(rag_documents)}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to add documents batch to RAG system"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add documents batch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding documents batch: {str(e)}"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_documents(search_query: SearchQuery) -> Dict[str, Any]:
    """
    Search for relevant documents in the RAG system

    Returns contextually relevant documents based on semantic search
    to enhance AI analysis accuracy.
    """
    try:
        results = await rag_service.search_context(
            query=search_query.query,
            filters=search_query.filters,
            top_k=search_query.top_k
        )

        return {
            "query": search_query.query,
            "results_count": len(results),
            "results": results,
            "filters_applied": search_query.filters
        }

    except Exception as e:
        logger.error(f"Failed to search documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/context/sector/{sector}")
async def get_sector_context(
    sector: str,
    country: Optional[str] = Query(None, description="Country filter")
) -> Dict[str, Any]:
    """
    Get contextual information for a specific sector

    Returns compiled sector-specific knowledge from the RAG system
    to enrich AI analyses with domain expertise.
    """
    try:
        context = await rag_service.get_sector_context(sector, country or "")

        return {
            "sector": sector,
            "country": country,
            "context_available": bool(context.strip()),
            "context_length": len(context),
            "context": context[:2000] + "..." if len(context) > 2000 else context
        }

    except Exception as e:
        logger.error(f"Failed to get sector context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting sector context: {str(e)}"
        )


@router.get("/context/regulatory/{sector}/{country}")
async def get_regulatory_context(sector: str, country: str) -> Dict[str, Any]:
    """
    Get regulatory and legal context for sector/country combination

    Provides legal frameworks and regulatory information relevant
    to business operations in specific markets.
    """
    try:
        context = await rag_service.get_regulatory_context(sector, country)

        return {
            "sector": sector,
            "country": country,
            "regulatory_context_available": bool(context.strip()),
            "context_length": len(context),
            "context": context[:2000] + "..." if len(context) > 2000 else context
        }

    except Exception as e:
        logger.error(f"Failed to get regulatory context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting regulatory context: {str(e)}"
        )


@router.get("/context/best-practices/{sector}")
async def get_best_practices_context(
    sector: str,
    challenge: Optional[str] = Query(None, description="Specific challenge")
) -> Dict[str, Any]:
    """
    Get best practices for a sector

    Returns proven successful approaches and lessons learned
    from similar businesses in the same sector.
    """
    try:
        context = await rag_service.get_best_practices_context(sector, challenge or "")

        return {
            "sector": sector,
            "challenge": challenge,
            "best_practices_available": bool(context.strip()),
            "context_length": len(context),
            "context": context[:2000] + "..." if len(context) > 2000 else context
        }

    except Exception as e:
        logger.error(f"Failed to get best practices context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting best practices context: {str(e)}"
        )


@router.post("/import/database", response_model=ImportResponse)
async def import_database_data(
    background_tasks: BackgroundTasks,
    categories: Optional[List[str]] = Query(
        None,
        description="Categories to import (default: all)"
    )
) -> ImportResponse:
    """
    Import data from PostgreSQL database to RAG system

    This endpoint triggers a background import of all relevant
    Africa Strategy data from the database into the RAG system
    for enhanced AI analyses.
    """
    if not DATA_IMPORT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Data import service not available (asyncpg not installed)"
        )
    try:
        # Default categories if none specified
        if not categories:
            categories = [
                'regulatory_data',
                'sector_reports',
                'esg_frameworks',
                'market_data',
                'best_practices',
                'case_studies',
                'policy_documents'
            ]

        # Start background import
        background_tasks.add_task(
            data_import_service._import_categories_background,
            categories
        )

        return ImportResponse(
            success=True,
            message=f"Database import started for categories: {', '.join(categories)}",
            details={
                "categories": categories,
                "status": "running_in_background",
                "note": "Check /api/v1/rag/health for import progress"
            }
        )

    except Exception as e:
        logger.error(f"Failed to start database import: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting database import: {str(e)}"
        )


@router.post("/import/sample-data", response_model=ImportResponse)
async def create_sample_data() -> ImportResponse:
    """
    Create and import sample data for RAG testing

    This endpoint creates sample documents representing different
    types of Africa Strategy data for testing the RAG system.
    """
    if not DATA_IMPORT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Data import service not available (asyncpg not installed)"
        )
    try:
        result = await data_import_service.create_sample_data()

        return ImportResponse(
            success=result.get('sample_data_created', False),
            message=result.get('message', 'Sample data creation completed'),
            details={
                "documents_created": result.get('documents_count', 0),
                "categories": result.get('categories', [])
            }
        )

    except Exception as e:
        logger.error(f"Failed to create sample data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating sample data: {str(e)}"
        )


@router.get("/health")
async def rag_health_check() -> Dict[str, Any]:
    """
    Check RAG system health and status

    Returns comprehensive health information about the RAG system,
    including Pinecone connection, index status, and search functionality.
    """
    try:
        health = await rag_service.health_check()

        # Add additional context
        health.update({
            "description": "Retrieval-Augmented Generation system for Africa Strategy",
            "capabilities": [
                "Document indexing and semantic search",
                "Context enrichment for AI analyses",
                "Sector-specific knowledge retrieval",
                "Regulatory information access",
                "Best practices recommendations"
            ],
            "supported_categories": [
                "regulatory_data",
                "sector_reports",
                "esg_frameworks",
                "market_data",
                "best_practices",
                "case_studies",
                "policy_documents"
            ]
        })

        return health

    except Exception as e:
        logger.error(f"Failed to check RAG health: {str(e)}")
        return {
            "service": "RAG",
            "status": "error",
            "error": str(e),
            "timestamp": "2025-11-04T12:04:10.061Z"
        }


@router.delete("/documents/clear")
async def clear_rag_documents() -> ImportResponse:
    """
    Clear all documents from RAG system (ADMIN ONLY)

    WARNING: This operation permanently deletes all indexed documents.
    Use with extreme caution - primarily for testing/development.
    """
    try:
        # Note: Pinecone doesn't have a simple clear operation
        # This would need to be implemented based on specific requirements
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="Clear operation not implemented - use Pinecone dashboard for index management"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear RAG documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing RAG documents: {str(e)}"
        )