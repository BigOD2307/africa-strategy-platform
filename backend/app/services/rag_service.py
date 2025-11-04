"""
RAG Service for Africa Strategy
Handles document indexing, retrieval, and context enrichment for AI analyses
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for Retrieval-Augmented Generation using Pinecone
    """

    def __init__(self):
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.pinecone_env = settings.PINECONE_ENVIRONMENT
        self.index_name = settings.PINECONE_INDEX_NAME

        # Initialize Pinecone
        if self.pinecone_api_key and self.pinecone_env:
            try:
                self.pc = Pinecone(api_key=self.pinecone_api_key)
                self._ensure_index_exists()
                logger.info(f"RAG Service initialized with Pinecone index: {self.index_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Pinecone: {str(e)}")
                self.pc = None
        else:
            logger.warning("Pinecone credentials not configured - RAG disabled")
            self.pc = None

        # Initialize embeddings
        try:
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"  # Fast and good quality
            )
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {str(e)}")
            self.embeddings = None

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def _ensure_index_exists(self):
        """Ensure Pinecone index exists"""
        if not self.pc:
            return

        try:
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # Dimension for all-MiniLM-L6-v2
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.pinecone_env
                    )
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            else:
                logger.info(f"Pinecone index already exists: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create/verify Pinecone index: {str(e)}")

    def _get_vectorstore(self):
        """Get LangChain Pinecone vectorstore"""
        if not self.pc or not self.embeddings:
            return None

        try:
            return LangchainPinecone.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace="africa-strategy-docs"
            )
        except Exception as e:
            logger.error(f"Failed to get vectorstore: {str(e)}")
            return None

    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the RAG system

        Args:
            documents: List of document dictionaries with 'content', 'metadata', etc.

        Returns:
            Success status
        """
        if not self.pc or not self.embeddings:
            logger.warning("RAG not available - skipping document addition")
            return False

        try:
            vectorstore = self._get_vectorstore()
            if not vectorstore:
                return False

            # Convert to LangChain documents
            langchain_docs = []
            for doc in documents:
                content = doc.get('content', '')
                if not content.strip():
                    continue

                # Split text into chunks
                chunks = self.text_splitter.split_text(content)

                for i, chunk in enumerate(chunks):
                    metadata = doc.get('metadata', {}).copy()
                    metadata.update({
                        'chunk_id': i,
                        'total_chunks': len(chunks),
                        'source': doc.get('source', 'unknown'),
                        'category': doc.get('category', 'general'),
                        'country': doc.get('country', ''),
                        'sector': doc.get('sector', ''),
                        'added_at': datetime.now().isoformat()
                    })

                    langchain_docs.append(Document(
                        page_content=chunk,
                        metadata=metadata
                    ))

            if langchain_docs:
                # Add to vectorstore
                vectorstore.add_documents(langchain_docs)
                logger.info(f"Added {len(langchain_docs)} document chunks to RAG")
                return True
            else:
                logger.warning("No valid documents to add")
                return False

        except Exception as e:
            logger.error(f"Failed to add documents to RAG: {str(e)}")
            return False

    async def search_context(self, query: str, filters: Optional[Dict[str, Any]] = None,
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant context in the RAG system

        Args:
            query: Search query
            filters: Optional metadata filters (country, sector, category, etc.)
            top_k: Number of results to return

        Returns:
            List of relevant documents with scores
        """
        if not self.pc or not self.embeddings:
            logger.warning("RAG not available - returning empty results")
            return []

        try:
            vectorstore = self._get_vectorstore()
            if not vectorstore:
                return []

            # Prepare filter for Pinecone
            pinecone_filter = {}
            if filters:
                if 'country' in filters and filters['country']:
                    pinecone_filter['country'] = filters['country']
                if 'sector' in filters and filters['sector']:
                    pinecone_filter['sector'] = filters['sector']
                if 'category' in filters and filters['category']:
                    pinecone_filter['category'] = filters['category']

            # Search with filters
            if pinecone_filter:
                docs_with_scores = vectorstore.similarity_search_with_score(
                    query, k=top_k, filter=pinecone_filter
                )
            else:
                docs_with_scores = vectorstore.similarity_search_with_score(
                    query, k=top_k
                )

            # Format results
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score),
                    'source': doc.metadata.get('source', 'unknown'),
                    'category': doc.metadata.get('category', 'general')
                })

            logger.info(f"RAG search returned {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Failed to search RAG: {str(e)}")
            return []

    async def get_sector_context(self, sector: str, country: str = "") -> str:
        """
        Get contextual information for a specific sector and country

        Args:
            sector: Business sector
            country: Country (optional)

        Returns:
            Compiled context string
        """
        queries = [
            f"Analyse stratégique secteur {sector} Afrique",
            f"Tendances {sector} Afrique 2024-2025",
            f"Opportunités {sector} Afrique de l'Ouest",
            f"Défis {sector} Afrique développement durable"
        ]

        if country:
            queries.extend([
                f"Marché {sector} {country}",
                f"Réglementations {sector} {country}",
                f"Opportunités {sector} {country}"
            ])

        all_context = []
        for query in queries:
            results = await self.search_context(
                query,
                filters={'sector': sector, 'country': country} if country else {'sector': sector},
                top_k=3
            )

            for result in results:
                if result['score'] > 0.7:  # Only high-confidence results
                    all_context.append(result['content'])

        # Remove duplicates and join
        unique_context = list(set(all_context))
        return "\n\n".join(unique_context[:5])  # Limit to top 5 chunks

    async def get_regulatory_context(self, sector: str, country: str) -> str:
        """
        Get regulatory and legal context for sector/country

        Args:
            sector: Business sector
            country: Country

        Returns:
            Regulatory context
        """
        query = f"Réglementations légales {sector} {country} durabilité environnementale"
        results = await self.search_context(
            query,
            filters={'category': 'regulatory', 'country': country, 'sector': sector},
            top_k=5
        )

        context_parts = []
        for result in results:
            if result['score'] > 0.75:
                context_parts.append(result['content'])

        return "\n\n".join(context_parts)

    async def get_best_practices_context(self, sector: str, challenge: str = "") -> str:
        """
        Get best practices for sector challenges

        Args:
            sector: Business sector
            challenge: Specific challenge (optional)

        Returns:
            Best practices context
        """
        if challenge:
            query = f"Best practices {sector} {challenge} Afrique"
        else:
            query = f"Best practices durabilité {sector} Afrique"

        results = await self.search_context(
            query,
            filters={'category': 'best_practices', 'sector': sector},
            top_k=4
        )

        context_parts = []
        for result in results:
            if result['score'] > 0.7:
                context_parts.append(f"Best Practice: {result['content']}")

        return "\n\n".join(context_parts)

    async def enrich_analysis_context(self, company_data: Dict[str, Any],
                                    analysis_type: str) -> Dict[str, Any]:
        """
        Enrich analysis context with RAG data

        Args:
            company_data: Company information
            analysis_type: Type of analysis (pestel, esg, market, etc.)

        Returns:
            Enriched context dictionary
        """
        sector = company_data.get('sector', '')
        country = company_data.get('country', '')

        if not sector:
            return {'rag_context': '', 'available': False}

        try:
            # Get sector-specific context
            sector_context = await self.get_sector_context(sector, country)

            # Get regulatory context
            regulatory_context = await self.get_regulatory_context(sector, country)

            # Get best practices
            challenge = company_data.get('main_challenge', '')
            best_practices = await self.get_best_practices_context(sector, challenge)

            # Combine all context
            full_context = f"""
CONTEXTE SECTORIEL ({sector}):
{sector_context}

CONTEXTE RÉGLEMENTAIRE ({country}):
{regulatory_context}

BEST PRACTICES:
{best_practices}
""".strip()

            return {
                'rag_context': full_context,
                'available': True,
                'sector_context_length': len(sector_context),
                'regulatory_context_length': len(regulatory_context),
                'best_practices_length': len(best_practices)
            }

        except Exception as e:
            logger.error(f"Failed to enrich analysis context: {str(e)}")
            return {'rag_context': '', 'available': False, 'error': str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """
        Check RAG service health

        Returns:
            Health status dictionary
        """
        health = {
            'service': 'RAG',
            'status': 'unhealthy',
            'pinecone_configured': bool(self.pinecone_api_key and self.pinecone_env),
            'embeddings_loaded': self.embeddings is not None,
            'index_name': self.index_name,
            'timestamp': datetime.now().isoformat()
        }

        if not health['pinecone_configured']:
            health['error'] = 'Pinecone credentials not configured'
            return health

        if not health['embeddings_loaded']:
            health['error'] = 'Embeddings model not loaded'
            return health

        try:
            # Check index exists
            indexes = self.pc.list_indexes().names() if self.pc else []
            health['index_exists'] = self.index_name in indexes

            if health['index_exists']:
                # Try a simple search
                vectorstore = self._get_vectorstore()
                if vectorstore:
                    # Simple test query
                    results = vectorstore.similarity_search("test", k=1)
                    health['search_working'] = True
                else:
                    health['search_working'] = False
                    health['error'] = 'Vectorstore initialization failed'
            else:
                health['search_working'] = False
                health['error'] = f'Index {self.index_name} does not exist'

            health['status'] = 'healthy' if health['search_working'] else 'degraded'

        except Exception as e:
            health['error'] = str(e)
            health['status'] = 'unhealthy'

        return health


# Global RAG service instance
rag_service = RAGService()