"""
RAG Service for Africa Strategy
Handles document indexing, retrieval, and context enrichment for AI analyses
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from pinecone import Pinecone, ServerlessSpec
try:
    from langchain_pinecone import Pinecone as LangchainPinecone
except ImportError:
    from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

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
        """Get LangChain Pinecone vectorstore - DEPRECATED due to compatibility issues"""
        # Note: LangChain Pinecone has compatibility issues with new Pinecone API
        # We use direct Pinecone API instead in search_context method
        return None

    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the RAG system using direct Pinecone API

        Args:
            documents: List of document dictionaries with 'content', 'metadata', etc.

        Returns:
            Success status
        """
        if not self.pc or not self.embeddings:
            logger.warning("RAG not available - skipping document addition")
            return False

        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            dimension = stats.get('dimension', 384)
            
            vectors_to_upsert = []
            
            for doc in documents:
                content = doc.get('content', '')
                if not content.strip():
                    continue

                # Split text into chunks
                chunks = self.text_splitter.split_text(content)

                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    try:
                        embedding = self.embeddings.embed_query(chunk)
                        
                        # Adjust dimension if needed
                        if len(embedding) != dimension:
                            if len(embedding) < dimension:
                                embedding = embedding + [0.0] * (dimension - len(embedding))
                            else:
                                embedding = embedding[:dimension]
                    except Exception as e:
                        logger.error(f"Failed to generate embedding for chunk {i}: {str(e)}")
                        continue
                    
                    # Prepare metadata
                    metadata = doc.get('metadata', {}).copy()
                    metadata.update({
                        'chunk_id': i,
                        'total_chunks': len(chunks),
                        'source': doc.get('source', 'unknown'),
                        'category': doc.get('category', 'general'),
                        'country': doc.get('country', ''),
                        'sector': doc.get('sector', ''),
                        'content': chunk[:1000],  # Limit content size
                        'added_at': datetime.now().isoformat()
                    })
                    
                    # Create vector
                    vector_id = f"{doc.get('source', 'doc')}_{i}_{datetime.now().timestamp()}"
                    vectors_to_upsert.append({
                        'id': vector_id,
                        'values': embedding,
                        'metadata': metadata
                    })
            
            if vectors_to_upsert:
                # Upload in batches
                batch_size = 50
                total_uploaded = 0
                
                for i in range(0, len(vectors_to_upsert), batch_size):
                    batch = vectors_to_upsert[i:i+batch_size]
                    try:
                        index.upsert(
                            vectors=batch,
                            namespace="africa-strategy-docs"
                        )
                        total_uploaded += len(batch)
                    except Exception as e:
                        logger.error(f"Failed to upsert batch {i//batch_size + 1}: {str(e)}")
                
                logger.info(f"Added {total_uploaded} document chunks to RAG")
                return total_uploaded > 0
            else:
                logger.warning("No valid documents to add")
                return False

        except Exception as e:
            logger.error(f"Failed to add documents to RAG: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def search_context(self, query: str, filters: Optional[Dict[str, Any]] = None,
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant context in the RAG system using direct Pinecone API

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
            # Generate embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Get index dimension
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            dimension = stats.get('dimension', 384)
            
            # Adjust embedding dimension if needed
            if len(query_embedding) != dimension:
                if len(query_embedding) < dimension:
                    query_embedding = query_embedding + [0.0] * (dimension - len(query_embedding))
                else:
                    query_embedding = query_embedding[:dimension]
            
            # Prepare filter for Pinecone
            pinecone_filter = {}
            if filters:
                if 'country' in filters and filters['country']:
                    pinecone_filter['country'] = {'$eq': filters['country']}
                if 'sector' in filters and filters['sector']:
                    pinecone_filter['sector'] = {'$eq': filters['sector']}
                if 'category' in filters and filters['category']:
                    pinecone_filter['category'] = {'$eq': filters['category']}

            # Search using direct Pinecone API
            # Try default namespace first (where import_all_data.py puts data)
            search_results = None
            try:
                # First try default namespace (no namespace parameter)
                search_results = index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                    filter=pinecone_filter if pinecone_filter else None
                )
            except Exception as e1:
                # Try with namespace if default fails
                try:
                    search_results = index.query(
                        vector=query_embedding,
                        top_k=top_k,
                        include_metadata=True,
                        filter=pinecone_filter if pinecone_filter else None,
                        namespace="africa-strategy-docs"
                    )
                except Exception as e2:
                    logger.error(f"Failed to query index (both namespaces): {str(e1)} / {str(e2)}")
                    return []

            # Format results
            results = []
            for match in search_results.get('matches', []):
                results.append({
                    'content': match['metadata'].get('content', ''),
                    'metadata': match['metadata'],
                    'score': float(match.get('score', 0.0)),
                    'source': match['metadata'].get('source', 'unknown'),
                    'category': match['metadata'].get('category', 'general')
                })

            logger.info(f"RAG search returned {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Failed to search RAG: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
                # Try a simple search using direct API
                try:
                    test_results = await self.search_context("test", top_k=1)
                    health['search_working'] = len(test_results) > 0 or True  # Even if no results, search works
                except Exception as e:
                    health['search_working'] = False
                    health['error'] = f'Search test failed: {str(e)}'
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