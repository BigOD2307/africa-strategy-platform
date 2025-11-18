"""
Data Import Service for Africa Strategy RAG
Imports data from PostgreSQL database to Pinecone for RAG
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import asyncpg
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logger.warning("asyncpg not installed - data import service disabled")

from app.core.config import settings
from app.services.rag_service import rag_service


class DataImportService:
    """
    Service to import data from PostgreSQL to Pinecone RAG system
    """

    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.engine = None
        self.session_maker = None

    async def initialize_db(self):
        """Initialize database connection"""
        if not self.engine:
            self.engine = create_async_engine(self.db_url, echo=False)
            self.session_maker = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

    async def get_db_session(self) -> AsyncSession:
        """Get database session"""
        await self.initialize_db()
        return self.session_maker()

    async def import_africa_strategy_data(self) -> Dict[str, Any]:
        """
        Import all Africa Strategy data from PostgreSQL to Pinecone

        Returns:
            Import summary
        """
        logger.info("Starting Africa Strategy data import to RAG")

        summary = {
            'start_time': datetime.now().isoformat(),
            'total_documents': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'categories': {},
            'errors': []
        }

        try:
            # Import different types of data
            categories = [
                'regulatory_data',
                'sector_reports',
                'esg_frameworks',
                'market_data',
                'best_practices',
                'case_studies',
                'policy_documents'
            ]

            for category in categories:
                logger.info(f"Importing category: {category}")
                category_summary = await self._import_category(category)
                summary['categories'][category] = category_summary
                summary['total_documents'] += category_summary['documents_count']
                summary['successful_imports'] += category_summary['successful_imports']
                summary['failed_imports'] += category_summary['failed_imports']

                if category_summary['errors']:
                    summary['errors'].extend(category_summary['errors'])

            summary['end_time'] = datetime.now().isoformat()
            summary['duration_seconds'] = (
                datetime.fromisoformat(summary['end_time']) -
                datetime.fromisoformat(summary['start_time'])
            ).total_seconds()

            logger.info(f"Data import completed: {summary['successful_imports']} successful, {summary['failed_imports']} failed")
            return summary

        except Exception as e:
            logger.error(f"Data import failed: {str(e)}")
            summary['errors'].append(str(e))
            return summary

    async def _import_category(self, category: str) -> Dict[str, Any]:
        """
        Import a specific category of data

        Args:
            category: Category name

        Returns:
            Category import summary
        """
        category_summary = {
            'documents_count': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'errors': []
        }

        try:
            # Get data from database based on category
            documents = await self._fetch_category_data(category)

            if not documents:
                logger.warning(f"No documents found for category: {category}")
                return category_summary

            category_summary['documents_count'] = len(documents)

            # Convert to RAG format
            rag_documents = []
            for doc in documents:
                try:
                    rag_doc = self._convert_to_rag_format(doc, category)
                    if rag_doc:
                        rag_documents.append(rag_doc)
                except Exception as e:
                    logger.error(f"Failed to convert document {doc.get('id', 'unknown')}: {str(e)}")
                    category_summary['failed_imports'] += 1
                    category_summary['errors'].append(f"Document {doc.get('id', 'unknown')}: {str(e)}")

            # Import to RAG system
            if rag_documents:
                success = await rag_service.add_documents(rag_documents)
                if success:
                    category_summary['successful_imports'] = len(rag_documents)
                    logger.info(f"Successfully imported {len(rag_documents)} documents for category: {category}")
                else:
                    category_summary['failed_imports'] = len(rag_documents)
                    category_summary['errors'].append(f"RAG import failed for category: {category}")

        except Exception as e:
            logger.error(f"Failed to import category {category}: {str(e)}")
            category_summary['errors'].append(str(e))

        return category_summary

    async def _fetch_category_data(self, category: str) -> List[Dict[str, Any]]:
        """
        Fetch data for a specific category from database

        Args:
            category: Category name

        Returns:
            List of documents
        """
        session = await self.get_db_session()

        try:
            if category == 'regulatory_data':
                # Import regulatory frameworks and laws
                query = """
                SELECT id, title, content, country, sector, category,
                       created_at, updated_at, source_url, language
                FROM regulatory_documents
                WHERE is_active = true
                ORDER BY created_at DESC
                """

            elif category == 'sector_reports':
                # Import sector analysis reports
                query = """
                SELECT id, title, executive_summary, full_content, sector,
                       country, publication_year, source_organization,
                       key_findings, recommendations
                FROM sector_reports
                WHERE is_published = true
                ORDER BY publication_year DESC
                """

            elif category == 'esg_frameworks':
                # Import ESG frameworks and standards
                query = """
                SELECT id, framework_name, description, principles,
                       indicators, sector_applicability, country_focus,
                       implementing_organization, version, release_date
                FROM esg_frameworks
                WHERE is_active = true
                ORDER BY release_date DESC
                """

            elif category == 'market_data':
                # Import market intelligence data
                query = """
                SELECT id, market_segment, country, sector, market_size,
                       growth_rate, key_players, trends, opportunities,
                       threats, data_year, source
                FROM market_intelligence
                WHERE is_verified = true
                ORDER BY data_year DESC
                """

            elif category == 'best_practices':
                # Import best practices and case studies
                query = """
                SELECT id, practice_title, sector, country, company_size,
                       challenge_addressed, solution_implemented,
                       outcomes, lessons_learned, implementation_time,
                       cost_estimate, success_factors
                FROM best_practices
                WHERE is_verified = true AND is_public = true
                ORDER BY created_at DESC
                """

            elif category == 'case_studies':
                # Import detailed case studies
                query = """
                SELECT id, company_name, sector, country, challenge,
                       solution, implementation_steps, outcomes,
                       metrics, timeline, budget, lessons_learned,
                       contact_info, is_anonymized
                FROM case_studies
                WHERE is_published = true
                ORDER BY created_at DESC
                """

            elif category == 'policy_documents':
                # Import policy and strategy documents
                query = """
                SELECT id, document_title, country, sector, policy_type,
                       summary, key_points, implementation_status,
                       responsible_ministry, timeline, budget_allocated,
                       expected_impact
                FROM policy_documents
                WHERE is_active = true
                ORDER BY created_at DESC
                """

            else:
                logger.warning(f"Unknown category: {category}")
                return []

            # Execute query
            result = await session.execute(query)
            rows = result.fetchall()

            # Convert to dictionaries
            documents = []
            for row in rows:
                doc_dict = dict(row._mapping)
                documents.append(doc_dict)

            logger.info(f"Fetched {len(documents)} documents for category: {category}")
            return documents

        except Exception as e:
            logger.error(f"Failed to fetch data for category {category}: {str(e)}")
            return []
        finally:
            await session.close()

    def _convert_to_rag_format(self, doc: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
        """
        Convert database document to RAG format

        Args:
            doc: Database document
            category: Document category

        Returns:
            RAG-formatted document or None if invalid
        """
        try:
            # Build content based on category
            if category == 'regulatory_data':
                content = f"""
                Document Réglementaire: {doc.get('title', '')}

                Pays: {doc.get('country', '')}
                Secteur: {doc.get('sector', '')}
                Catégorie: {doc.get('category', '')}

                Contenu:
                {doc.get('content', '')}

                Source: {doc.get('source_url', '')}
                Langue: {doc.get('language', '')}
                """

            elif category == 'sector_reports':
                content = f"""
                Rapport Sectoriel: {doc.get('title', '')}

                Secteur: {doc.get('sector', '')}
                Pays: {doc.get('country', '')}
                Année: {doc.get('publication_year', '')}
                Organisation: {doc.get('source_organization', '')}

                Résumé Exécutif:
                {doc.get('executive_summary', '')}

                Contenu Complet:
                {doc.get('full_content', '')}

                Conclusions Clés:
                {doc.get('key_findings', '')}

                Recommandations:
                {doc.get('recommendations', '')}
                """

            elif category == 'esg_frameworks':
                content = f"""
                Cadre ESG: {doc.get('framework_name', '')}

                Description: {doc.get('description', '')}
                Organisation: {doc.get('implementing_organization', '')}
                Version: {doc.get('version', '')}
                Date: {doc.get('release_date', '')}

                Principes:
                {doc.get('principles', '')}

                Indicateurs:
                {doc.get('indicators', '')}

                Applicabilité Sectorielle: {doc.get('sector_applicability', '')}
                Focus Pays: {doc.get('country_focus', '')}
                """

            elif category == 'market_data':
                content = f"""
                Intelligence Marché: {doc.get('market_segment', '')}

                Pays: {doc.get('country', '')}
                Secteur: {doc.get('sector', '')}
                Année: {doc.get('data_year', '')}
                Source: {doc.get('source', '')}

                Taille Marché: {doc.get('market_size', '')}
                Taux Croissance: {doc.get('growth_rate', '')}

                Acteurs Clés: {doc.get('key_players', '')}
                Tendances: {doc.get('trends', '')}
                Opportunités: {doc.get('opportunities', '')}
                Menaces: {doc.get('threats', '')}
                """

            elif category == 'best_practices':
                content = f"""
                Bonne Pratique: {doc.get('practice_title', '')}

                Secteur: {doc.get('sector', '')}
                Pays: {doc.get('country', '')}
                Taille Entreprise: {doc.get('company_size', '')}

                Défi: {doc.get('challenge_addressed', '')}
                Solution: {doc.get('solution_implemented', '')}

                Résultats: {doc.get('outcomes', '')}
                Leçons Apprises: {doc.get('lessons_learned', '')}

                Temps Implémentation: {doc.get('implementation_time', '')}
                Coût Estimé: {doc.get('cost_estimate', '')}
                Facteurs Succès: {doc.get('success_factors', '')}
                """

            elif category == 'case_studies':
                content = f"""
                Étude Cas: {doc.get('company_name', '')}

                Secteur: {doc.get('sector', '')}
                Pays: {doc.get('country', '')}

                Défi: {doc.get('challenge', '')}
                Solution: {doc.get('solution', '')}

                Étapes Implémentation: {doc.get('implementation_steps', '')}
                Résultats: {doc.get('outcomes', '')}
                Métriques: {doc.get('metrics', '')}

                Timeline: {doc.get('timeline', '')}
                Budget: {doc.get('budget', '')}
                Leçons: {doc.get('lessons_learned', '')}
                """

            elif category == 'policy_documents':
                content = f"""
                Document Politique: {doc.get('document_title', '')}

                Pays: {doc.get('country', '')}
                Secteur: {doc.get('sector', '')}
                Type: {doc.get('policy_type', '')}

                Résumé: {doc.get('summary', '')}
                Points Clés: {doc.get('key_points', '')}

                Statut Implémentation: {doc.get('implementation_status', '')}
                Ministère Responsable: {doc.get('responsible_ministry', '')}
                Timeline: {doc.get('timeline', '')}
                Budget: {doc.get('budget_allocated', '')}
                Impact Attendu: {doc.get('expected_impact', '')}
                """

            else:
                return None

            # Clean content
            content = content.strip()
            if not content:
                return None

            # Build metadata
            metadata = {
                'source': f"database_{category}",
                'category': category,
                'country': doc.get('country', ''),
                'sector': doc.get('sector', ''),
                'doc_id': str(doc.get('id', '')),
                'created_at': doc.get('created_at', datetime.now()).isoformat() if doc.get('created_at') else datetime.now().isoformat(),
                'updated_at': doc.get('updated_at', datetime.now()).isoformat() if doc.get('updated_at') else datetime.now().isoformat()
            }

            # Add category-specific metadata
            if category == 'sector_reports':
                metadata.update({
                    'publication_year': doc.get('publication_year', ''),
                    'source_organization': doc.get('source_organization', '')
                })
            elif category == 'esg_frameworks':
                metadata.update({
                    'framework_name': doc.get('framework_name', ''),
                    'implementing_organization': doc.get('implementing_organization', ''),
                    'version': doc.get('version', '')
                })

            return {
                'content': content,
                'metadata': metadata,
                'source': f"database_{category}",
                'category': category,
                'country': doc.get('country', ''),
                'sector': doc.get('sector', '')
            }

        except Exception as e:
            logger.error(f"Failed to convert document to RAG format: {str(e)}")
            return None

    async def create_sample_data(self) -> Dict[str, Any]:
        """
        Create sample data for testing RAG system

        Returns:
            Sample data creation summary
        """
        logger.info("Creating sample data for RAG testing")

        sample_documents = [
            # Regulatory data
            {
                'content': """
                Loi sur la Durabilité Environnementale - Côte d'Ivoire 2024

                La Côte d'Ivoire s'engage dans une transition durable avec des objectifs ambitieux :
                - Réduction de 30% des émissions de CO2 d'ici 2030
                - 40% d'énergies renouvelables dans le mix énergétique
                - Protection de 20% du territoire national
                - Développement durable de l'agriculture cacao

                Principales réglementations :
                - Certification obligatoire pour exportateurs cacao
                - Subventions pour énergies renouvelables
                - Taxe carbone sur industries polluantes
                - Formation obligatoire en RSE pour entreprises >50 employés
                """,
                'metadata': {
                    'source': 'sample_regulatory',
                    'category': 'regulatory',
                    'country': 'Côte d\'Ivoire',
                    'sector': 'all',
                    'doc_type': 'law'
                },
                'source': 'sample_regulatory',
                'category': 'regulatory',
                'country': 'Côte d\'Ivoire',
                'sector': 'all'
            },

            # Sector report
            {
                'content': """
                Rapport Sectoriel : Agriculture Côte d'Ivoire 2024

                Le secteur agricole représente 25% du PIB ivoirien avec le cacao comme principale culture.
                Défis majeurs :
                - Changement climatique affectant les rendements
                - Concurrence internationale accrue
                - Besoin de modernisation des pratiques

                Opportunités :
                - Certification durable (Rainforest Alliance, UTZ)
                - Export vers marchés premium européens
                - Agriculture de précision et technologies vertes
                - Développement de filières alternatives (hévéa, palmier)

                Tendances 2024-2025 :
                - Augmentation de 15% de la demande cacao bio
                - Développement des coopératives durables
                - Investissements étrangers en agriculture tech
                """,
                'metadata': {
                    'source': 'sample_sector_report',
                    'category': 'sector_reports',
                    'country': 'Côte d\'Ivoire',
                    'sector': 'agriculture',
                    'publication_year': '2024'
                },
                'source': 'sample_sector_report',
                'category': 'sector_reports',
                'country': 'Côte d\'Ivoire',
                'sector': 'agriculture'
            },

            # ESG Framework
            {
                'content': """
                Cadre ESG pour PME Africaines

                Principes fondamentaux :
                1. Gouvernance : Transparence et éthique
                2. Environnemental : Réduction impact écologique
                3. Social : Bien-être employés et communautés

                Indicateurs clés pour PME :
                - Consommation énergétique (kWh/employé)
                - Taux recyclage déchets (%)
                - Formation employés (heures/an)
                - Satisfaction clients (%)
                - Impact communautaire (projets sociaux)

                Outils recommandés :
                - Bilan carbone simplifié
                - Audit social interne
                - Système management environnemental
                - Rapport RSE annuel
                """,
                'metadata': {
                    'source': 'sample_esg_framework',
                    'category': 'esg_frameworks',
                    'country': 'Multi-pays',
                    'sector': 'all',
                    'framework_name': 'ESG PME Afrique'
                },
                'source': 'sample_esg_framework',
                'category': 'esg_frameworks',
                'country': 'Multi-pays',
                'sector': 'all'
            },

            # Best practice
            {
                'content': """
                Bonne Pratique : AgriTech Côte d'Ivoire - Certification Cacao Durable

                Entreprise : 50 employés, secteur cacao
                Défi : Accès difficile aux marchés premium européens
                Solution : Certification Rainforest Alliance + agriculture durable

                Implémentation :
                1. Diagnostic initial (2 mois)
                2. Formation équipe (1 mois)
                3. Mise en conformité pratiques (4 mois)
                4. Audit certification (2 mois)

                Résultats :
                - Prix vente +25%
                - Accès nouveaux marchés européens
                - Amélioration image marque
                - Réduction coûts (efficacité énergétique)

                Leçons apprises :
                - Investissement initial rentable à moyen terme
                - Formation équipe cruciale pour succès
                - Certification = avantage concurrentiel durable
                """,
                'metadata': {
                    'source': 'sample_best_practice',
                    'category': 'best_practices',
                    'country': 'Côte d\'Ivoire',
                    'sector': 'agriculture',
                    'company_size': 'PME'
                },
                'source': 'sample_best_practice',
                'category': 'best_practices',
                'country': 'Côte d\'Ivoire',
                'sector': 'agriculture'
            }
        ]

        # Import sample data
        success = await rag_service.add_documents(sample_documents)

        return {
            'sample_data_created': success,
            'documents_count': len(sample_documents),
            'categories': ['regulatory', 'sector_reports', 'esg_frameworks', 'best_practices'],
            'message': 'Sample data created for RAG testing'
        }


# Global data import service instance
data_import_service = DataImportService()