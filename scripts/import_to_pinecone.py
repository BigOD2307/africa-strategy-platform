#!/usr/bin/env python3
"""
Script to import exported JSON data into Pinecone RAG system
Africa Strategy Data Import Tool
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Import our services
from backend.app.services.rag_service import rag_service
from backend.app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PineconeDataImporter:
    """
    Import JSON data files into Pinecone RAG system
    """

    def __init__(self):
        self.import_summary = {
            "import_timestamp": datetime.now().isoformat(),
            "total_files_processed": 0,
            "total_documents_imported": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "categories_processed": {},
            "errors": []
        }

    async def import_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Import all JSON files from a directory into Pinecone

        Args:
            directory_path: Path to directory containing JSON export files

        Returns:
            Import summary
        """
        directory = Path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory_path} does not exist")

        logger.info(f"Starting import from directory: {directory_path}")

        # Find all JSON files (excluding summary file)
        json_files = list(directory.glob("*.json"))
        json_files = [f for f in json_files if f.name != "export_summary.json"]

        if not json_files:
            logger.warning(f"No JSON files found in {directory_path}")
            return self.import_summary

        logger.info(f"Found {len(json_files)} JSON files to import")

        # Process each file
        for json_file in json_files:
            try:
                await self._import_single_file(json_file)
                self.import_summary["total_files_processed"] += 1
            except Exception as e:
                logger.error(f"Failed to import {json_file.name}: {str(e)}")
                self.import_summary["errors"].append({
                    "file": json_file.name,
                    "error": str(e)
                })
                self.import_summary["failed_imports"] += 1

        # Final summary
        self.import_summary["completion_time"] = datetime.now().isoformat()

        logger.info(f"Import completed: {self.import_summary['successful_imports']} successful, {self.import_summary['failed_imports']} failed")

        return self.import_summary

    async def _import_single_file(self, file_path: Path) -> None:
        """
        Import a single JSON file into Pinecone

        Args:
            file_path: Path to JSON file
        """
        logger.info(f"Importing file: {file_path.name}")

        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract table information
            export_info = data.get("export_info", {})
            table_name = export_info.get("table_name", file_path.stem)
            records = data.get("data", [])

            if not records:
                logger.warning(f"No records found in {file_path.name}")
                return

            logger.info(f"Processing {len(records)} records from {table_name}")

            # Convert records to RAG format
            rag_documents = []
            for record in records:
                try:
                    rag_doc = self._convert_record_to_rag(record, table_name)
                    if rag_doc:
                        rag_documents.append(rag_doc)
                except Exception as e:
                    logger.error(f"Failed to convert record {record.get('id', 'unknown')}: {str(e)}")
                    continue

            if not rag_documents:
                logger.warning(f"No valid RAG documents created from {file_path.name}")
                return

            # Import to RAG system
            logger.info(f"Importing {len(rag_documents)} documents to RAG system...")
            success = await rag_service.add_documents(rag_documents)

            if success:
                self.import_summary["successful_imports"] += 1
                self.import_summary["total_documents_imported"] += len(rag_documents)

                # Track by category
                category = self._get_category_from_table(table_name)
                if category not in self.import_summary["categories_processed"]:
                    self.import_summary["categories_processed"][category] = {
                        "files": 0,
                        "documents": 0
                    }
                self.import_summary["categories_processed"][category]["files"] += 1
                self.import_summary["categories_processed"][category]["documents"] += len(rag_documents)

                logger.info(f"✅ Successfully imported {len(rag_documents)} documents from {file_path.name}")
            else:
                self.import_summary["failed_imports"] += 1
                logger.error(f"❌ Failed to import documents from {file_path.name}")

        except Exception as e:
            logger.error(f"Failed to process file {file_path.name}: {str(e)}")
            self.import_summary["failed_imports"] += 1
            raise

    def _convert_record_to_rag(self, record: Dict[str, Any], table_name: str) -> Optional[Dict[str, Any]]:
        """
        Convert a database record to RAG document format

        Args:
            record: Database record
            table_name: Source table name

        Returns:
            RAG-formatted document or None
        """
        try:
            # Use the same conversion logic as data_import_service
            # This ensures consistency between batch import and file import

            # Determine category and conversion based on table name
            if table_name in ['regulatory_documents', 'policy_documents']:
                return self._convert_regulatory_record(record, table_name)
            elif table_name == 'sector_reports':
                return self._convert_sector_report_record(record)
            elif table_name == 'market_intelligence':
                return self._convert_market_data_record(record)
            elif table_name == 'esg_frameworks':
                return self._convert_esg_framework_record(record)
            elif table_name == 'best_practices':
                return self._convert_best_practice_record(record)
            elif table_name == 'case_studies':
                return self._convert_case_study_record(record)
            elif table_name == 'sustainability_reports':
                return self._convert_sustainability_record(record)
            elif table_name == 'company_profiles':
                return self._convert_company_profile_record(record)
            else:
                logger.warning(f"Unknown table type: {table_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to convert record from {table_name}: {str(e)}")
            return None

    def _convert_regulatory_record(self, record: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """Convert regulatory record to RAG format"""
        category = "regulatory" if table_name == "regulatory_documents" else "policy"

        content_parts = []
        if record.get("title"):
            content_parts.append(f"Titre: {record['title']}")
        if record.get("content") or record.get("summary"):
            content_parts.append(f"Contenu: {record.get('content') or record.get('summary')}")
        if record.get("key_points"):
            content_parts.append(f"Points clés: {record['key_points']}")
        if record.get("key_requirements"):
            content_parts.append(f"Exigences: {record['key_requirements']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': f"database_{table_name}",
                'category': category,
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'document_type': record.get('document_type') or record.get('policy_type', ''),
                'is_active': record.get('is_active', True),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': f"database_{table_name}",
            'category': category,
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _convert_sector_report_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert sector report record to RAG format"""
        content_parts = []
        if record.get("title"):
            content_parts.append(f"Rapport: {record['title']}")
        if record.get("executive_summary"):
            content_parts.append(f"Résumé: {record['executive_summary']}")
        if record.get("key_findings"):
            content_parts.append(f"Conclusions: {record['key_findings']}")
        if record.get("recommendations"):
            content_parts.append(f"Recommandations: {record['recommendations']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_sector_reports',
                'category': 'sector_reports',
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'publication_year': record.get('publication_year'),
                'source_organization': record.get('source_organization', ''),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_sector_reports',
            'category': 'sector_reports',
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _convert_market_data_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert market data record to RAG format"""
        content_parts = []
        content_parts.append(f"Marché: {record.get('market_segment', '')}")
        content_parts.append(f"Taille: {record.get('market_size', '')}")
        content_parts.append(f"Croissance: {record.get('growth_rate', '')}")
        if record.get("key_players"):
            content_parts.append(f"Acteurs: {record['key_players']}")
        if record.get("trends"):
            content_parts.append(f"Tendances: {record['trends']}")
        if record.get("opportunities"):
            content_parts.append(f"Opportunités: {record['opportunities']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_market_intelligence',
                'category': 'market_data',
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'data_year': record.get('data_year'),
                'source_org': record.get('source', ''),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_market_intelligence',
            'category': 'market_data',
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _convert_esg_framework_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ESG framework record to RAG format"""
        content_parts = []
        if record.get("framework_name"):
            content_parts.append(f"Cadre ESG: {record['framework_name']}")
        if record.get("description"):
            content_parts.append(f"Description: {record['description']}")
        if record.get("principles"):
            content_parts.append(f"Principes: {record['principles']}")
        if record.get("indicators"):
            content_parts.append(f"Indicateurs: {record['indicators']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_esg_frameworks',
                'category': 'esg_frameworks',
                'country': record.get('country_focus', ''),
                'sector': record.get('sector_applicability', ''),
                'doc_id': str(record.get('id', '')),
                'framework_name': record.get('framework_name', ''),
                'implementing_org': record.get('implementing_organization', ''),
                'version': record.get('version', ''),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_esg_frameworks',
            'category': 'esg_frameworks',
            'country': record.get('country_focus', ''),
            'sector': record.get('sector_applicability', '')
        }

    def _convert_best_practice_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert best practice record to RAG format"""
        content_parts = []
        if record.get("practice_title"):
            content_parts.append(f"Pratique: {record['practice_title']}")
        if record.get("challenge_addressed"):
            content_parts.append(f"Défi: {record['challenge_addressed']}")
        if record.get("solution_implemented"):
            content_parts.append(f"Solution: {record['solution_implemented']}")
        if record.get("outcomes"):
            content_parts.append(f"Résultats: {record['outcomes']}")
        if record.get("lessons_learned"):
            content_parts.append(f"Leçons: {record['lessons_learned']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_best_practices',
                'category': 'best_practices',
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'company_size': record.get('company_size', ''),
                'success_verified': record.get('is_verified', True),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_best_practices',
            'category': 'best_practices',
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _convert_case_study_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert case study record to RAG format"""
        content_parts = []
        if record.get("company_name") and not record.get("is_anonymized"):
            content_parts.append(f"Entreprise: {record['company_name']}")
        if record.get("challenge"):
            content_parts.append(f"Défi: {record['challenge']}")
        if record.get("solution"):
            content_parts.append(f"Solution: {record['solution']}")
        if record.get("outcomes"):
            content_parts.append(f"Résultats: {record['outcomes']}")
        if record.get("lessons_learned"):
            content_parts.append(f"Leçons: {record['lessons_learned']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_case_studies',
                'category': 'case_studies',
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'anonymized': record.get('is_anonymized', False),
                'has_metrics': bool(record.get('metrics')),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_case_studies',
            'category': 'case_studies',
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _convert_sustainability_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert sustainability report record to RAG format"""
        content_parts = []
        if record.get("company_name"):
            content_parts.append(f"Entreprise: {record['company_name']}")
        if record.get("key_achievements"):
            content_parts.append(f"Réalisations: {record['key_achievements']}")
        if record.get("challenges_faced"):
            content_parts.append(f"Défis: {record['challenges_faced']}")
        if record.get("future_commitments"):
            content_parts.append(f"Engagements: {record['future_commitments']}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_sustainability_reports',
                'category': 'sustainability',
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'report_year': record.get('report_year'),
                'esg_scores': record.get('esg_scores', {}),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_sustainability_reports',
            'category': 'sustainability',
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _convert_company_profile_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert company profile record (anonymized) to RAG format"""
        # Only include anonymized insights, not sensitive data
        if not record.get('sector') or not record.get('country'):
            return None

        content_parts = []
        content_parts.append(f"Secteur: {record.get('sector', '')}")
        content_parts.append(f"Pays: {record.get('country', '')}")
        content_parts.append(f"Taille: {record.get('size_category', '')}")
        content_parts.append(f"Maturité ESG: {record.get('esg_maturity', '')}")

        if record.get('main_challenges'):
            content_parts.append(f"Défis principaux: {', '.join(record['main_challenges'])}")
        if record.get('successful_practices'):
            content_parts.append(f"Pratiques réussies: {', '.join(record['successful_practices'])}")

        content = "\n\n".join(content_parts)

        return {
            'content': content,
            'metadata': {
                'source': 'database_aggregated_insights',
                'category': 'aggregated_insights',
                'country': record.get('country', ''),
                'sector': record.get('sector', ''),
                'doc_id': str(record.get('id', '')),
                'data_type': 'anonymized_aggregated',
                'esg_maturity': record.get('esg_maturity', ''),
                'created_at': record.get('created_at', datetime.now().isoformat()),
                'updated_at': record.get('updated_at', datetime.now().isoformat())
            },
            'source': 'database_aggregated_insights',
            'category': 'aggregated_insights',
            'country': record.get('country', ''),
            'sector': record.get('sector', '')
        }

    def _get_category_from_table(self, table_name: str) -> str:
        """Get RAG category from table name"""
        category_map = {
            'regulatory_documents': 'regulatory',
            'policy_documents': 'regulatory',
            'sector_reports': 'sector_reports',
            'market_intelligence': 'market_data',
            'esg_frameworks': 'esg_frameworks',
            'best_practices': 'best_practices',
            'case_studies': 'case_studies',
            'sustainability_reports': 'sustainability',
            'company_profiles': 'aggregated_insights'
        }
        return category_map.get(table_name, 'general')

    def save_import_summary(self, output_file: str = "pinecone_import_summary.json") -> None:
        """Save import summary to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.import_summary, f, ensure_ascii=False, indent=2)
        logger.info(f"Import summary saved to {output_file}")


async def main():
    """Main import function"""
    # Initialize importer
    importer = PineconeDataImporter()

    try:
        # Import from exports directory
        logger.info("Starting Pinecone data import...")
        summary = await importer.import_from_directory("exports")

        # Save summary
        importer.save_import_summary()

        # Print results
        print("\n" + "="*60)
        print("PINECONE IMPORT SUMMARY")
        print("="*60)
        print(f"📁 Files processed: {summary['total_files_processed']}")
        print(f"📄 Documents imported: {summary['total_documents_imported']}")
        print(f"✅ Successful imports: {summary['successful_imports']}")
        print(f"❌ Failed imports: {summary['failed_imports']}")
        print(f"🕐 Import timestamp: {summary['import_timestamp']}")

        if summary['categories_processed']:
            print("\n📊 By category:")
            for category, stats in summary['categories_processed'].items():
                print(f"  • {category}: {stats['documents']} documents")

        if summary['errors']:
            print(f"\n⚠️  Errors encountered: {len(summary['errors'])}")
            for error in summary['errors'][:3]:  # Show first 3 errors
                print(f"  • {error['file']}: {error['error']}")

        print("
💾 Summary saved to: pinecone_import_summary.json"        print("🎯 RAG system ready for enhanced AI analyses!"

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        print(f"\n❌ Import failed: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())