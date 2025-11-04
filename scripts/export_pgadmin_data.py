#!/usr/bin/env python3
"""
Script to export data from PostgreSQL (pgAdmin) to JSON format for RAG import
Africa Strategy Data Export Tool
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncpg
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PgAdminDataExporter:
    """
    Export data from PostgreSQL database to JSON format for RAG system
    """

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None

    async def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = await asyncpg.connect(**self.db_config)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")

    async def export_table_to_json(self, table_name: str, output_file: str,
                                 transform_func=None) -> Dict[str, Any]:
        """
        Export a table to JSON format

        Args:
            table_name: Name of the table to export
            output_file: Output JSON file path
            transform_func: Optional function to transform each row

        Returns:
            Export summary
        """
        try:
            # Get table schema
            schema_query = f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
            """
            schema = await self.connection.fetch(schema_query)

            # Get all data
            data_query = f"SELECT * FROM {table_name}"
            rows = await self.connection.fetch(data_query)

            # Transform data
            exported_data = []
            for row in rows:
                row_dict = dict(row)

                # Apply transformation if provided
                if transform_func:
                    row_dict = transform_func(row_dict)

                exported_data.append(row_dict)

            # Create export structure
            export_structure = {
                "export_info": {
                    "table_name": table_name,
                    "exported_at": datetime.now().isoformat(),
                    "total_records": len(exported_data),
                    "schema": [{"name": col["column_name"], "type": col["data_type"]}
                              for col in schema]
                },
                "data": exported_data
            }

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_structure, f, ensure_ascii=False, indent=2)

            logger.info(f"Exported {len(exported_data)} records from {table_name} to {output_file}")

            return {
                "table": table_name,
                "records": len(exported_data),
                "file": output_file,
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to export table {table_name}: {str(e)}")
            return {
                "table": table_name,
                "error": str(e),
                "success": False
            }

    async def export_africa_strategy_data(self, output_dir: str = "exports") -> Dict[str, Any]:
        """
        Export all Africa Strategy relevant data for RAG system

        Args:
            output_dir: Directory to save export files

        Returns:
            Complete export summary
        """
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)

        export_summary = {
            "export_timestamp": datetime.now().isoformat(),
            "database": self.db_config.get("database", "unknown"),
            "exports": [],
            "total_files": 0,
            "total_records": 0
        }

        # Define tables to export and their transformations
        tables_to_export = {
            # Regulatory data
            "regulatory_documents": {
                "category": "regulatory",
                "transform": self._transform_regulatory_doc
            },
            "policy_documents": {
                "category": "regulatory",
                "transform": self._transform_policy_doc
            },

            # Sector reports and analysis
            "sector_reports": {
                "category": "sector_reports",
                "transform": self._transform_sector_report
            },
            "market_intelligence": {
                "category": "market_data",
                "transform": self._transform_market_data
            },

            # ESG and sustainability
            "esg_frameworks": {
                "category": "esg_frameworks",
                "transform": self._transform_esg_framework
            },
            "sustainability_reports": {
                "category": "sustainability",
                "transform": self._transform_sustainability_report
            },

            # Best practices and case studies
            "best_practices": {
                "category": "best_practices",
                "transform": self._transform_best_practice
            },
            "case_studies": {
                "category": "case_studies",
                "transform": self._transform_case_study
            },

            # Company and entrepreneur data (anonymized)
            "company_profiles": {
                "category": "company_data",
                "transform": self._transform_company_profile
            }
        }

        # Export each table
        for table_name, config in tables_to_export.items():
            output_file = os.path.join(output_dir, f"{table_name}.json")

            try:
                result = await self.export_table_to_json(
                    table_name=table_name,
                    output_file=output_file,
                    transform_func=config["transform"]
                )

                if result["success"]:
                    export_summary["exports"].append({
                        "table": table_name,
                        "category": config["category"],
                        "records": result["records"],
                        "file": result["file"]
                    })
                    export_summary["total_records"] += result["records"]
                    export_summary["total_files"] += 1
                else:
                    export_summary["exports"].append({
                        "table": table_name,
                        "error": result.get("error", "Unknown error"),
                        "success": False
                    })

            except Exception as e:
                logger.error(f"Failed to export {table_name}: {str(e)}")
                export_summary["exports"].append({
                    "table": table_name,
                    "error": str(e),
                    "success": False
                })

        # Save export summary
        summary_file = os.path.join(output_dir, "export_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(export_summary, f, ensure_ascii=False, indent=2)

        logger.info(f"Export completed: {export_summary['total_files']} files, {export_summary['total_records']} records")
        return export_summary

    # Transformation functions for each data type

    def _transform_regulatory_doc(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform regulatory document for RAG"""
        return {
            "id": row.get("id"),
            "title": row.get("title", ""),
            "content": row.get("content", ""),
            "country": row.get("country", ""),
            "sector": row.get("sector", ""),
            "document_type": row.get("document_type", ""),
            "issuing_authority": row.get("issuing_authority", ""),
            "publication_date": str(row.get("publication_date", "")),
            "effective_date": str(row.get("effective_date", "")),
            "key_requirements": row.get("key_requirements", ""),
            "compliance_deadlines": row.get("compliance_deadlines", ""),
            "source_url": row.get("source_url", ""),
            "language": row.get("language", "fr"),
            "is_active": row.get("is_active", True),
            "rag_category": "regulatory",
            "rag_metadata": {
                "document_type": "regulation",
                "compliance_required": True,
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "urgency_level": "high"
            }
        }

    def _transform_policy_doc(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform policy document for RAG"""
        return {
            "id": row.get("id"),
            "title": row.get("document_title", ""),
            "summary": row.get("summary", ""),
            "key_points": row.get("key_points", ""),
            "country": row.get("country", ""),
            "sector": row.get("sector", ""),
            "policy_type": row.get("policy_type", ""),
            "responsible_ministry": row.get("responsible_ministry", ""),
            "timeline": row.get("timeline", ""),
            "budget_allocated": row.get("budget_allocated", ""),
            "expected_impact": row.get("expected_impact", ""),
            "implementation_status": row.get("implementation_status", ""),
            "rag_category": "policy",
            "rag_metadata": {
                "document_type": "policy",
                "implementation_phase": row.get("implementation_status", ""),
                "budget_impact": bool(row.get("budget_allocated")),
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", "")
            }
        }

    def _transform_sector_report(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform sector report for RAG"""
        return {
            "id": row.get("id"),
            "title": row.get("title", ""),
            "executive_summary": row.get("executive_summary", ""),
            "full_content": row.get("full_content", ""),
            "sector": row.get("sector", ""),
            "country": row.get("country", ""),
            "publication_year": row.get("publication_year"),
            "source_organization": row.get("source_organization", ""),
            "key_findings": row.get("key_findings", ""),
            "recommendations": row.get("recommendations", ""),
            "methodology": row.get("methodology", ""),
            "data_sources": row.get("data_sources", ""),
            "rag_category": "sector_analysis",
            "rag_metadata": {
                "document_type": "sector_report",
                "analysis_depth": "comprehensive",
                "data_freshness": row.get("publication_year"),
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "credibility_level": "high"
            }
        }

    def _transform_market_data(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform market intelligence data for RAG"""
        return {
            "id": row.get("id"),
            "market_segment": row.get("market_segment", ""),
            "country": row.get("country", ""),
            "sector": row.get("sector", ""),
            "market_size": row.get("market_size", ""),
            "growth_rate": row.get("growth_rate", ""),
            "key_players": row.get("key_players", ""),
            "trends": row.get("trends", ""),
            "opportunities": row.get("opportunities", ""),
            "threats": row.get("threats", ""),
            "data_year": row.get("data_year"),
            "source": row.get("source", ""),
            "confidence_level": row.get("confidence_level", ""),
            "rag_category": "market_intelligence",
            "rag_metadata": {
                "document_type": "market_data",
                "data_type": "quantitative",
                "time_period": row.get("data_year"),
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "forecast_horizon": "medium_term"
            }
        }

    def _transform_esg_framework(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform ESG framework for RAG"""
        return {
            "id": row.get("id"),
            "framework_name": row.get("framework_name", ""),
            "description": row.get("description", ""),
            "principles": row.get("principles", ""),
            "indicators": row.get("indicators", ""),
            "sector_applicability": row.get("sector_applicability", ""),
            "country_focus": row.get("country_focus", ""),
            "implementing_organization": row.get("implementing_organization", ""),
            "version": row.get("version", ""),
            "release_date": str(row.get("release_date", "")),
            "certification_process": row.get("certification_process", ""),
            "rag_category": "esg_framework",
            "rag_metadata": {
                "document_type": "framework",
                "framework_type": "esg",
                "certification_available": bool(row.get("certification_process")),
                "geographic_scope": row.get("country_focus", ""),
                "sector_scope": row.get("sector_applicability", ""),
                "maturity_level": "mature"
            }
        }

    def _transform_sustainability_report(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform sustainability report for RAG"""
        return {
            "id": row.get("id"),
            "company_name": row.get("company_name", ""),
            "sector": row.get("sector", ""),
            "country": row.get("country", ""),
            "report_year": row.get("report_year"),
            "esg_scores": row.get("esg_scores", {}),
            "key_achievements": row.get("key_achievements", ""),
            "challenges_faced": row.get("challenges_faced", ""),
            "future_commitments": row.get("future_commitments", ""),
            "stakeholder_engagement": row.get("stakeholder_engagement", ""),
            "rag_category": "sustainability_report",
            "rag_metadata": {
                "document_type": "company_report",
                "report_type": "sustainability",
                "data_type": "qualitative",
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "benchmark_potential": True
            }
        }

    def _transform_best_practice(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform best practice for RAG"""
        return {
            "id": row.get("id"),
            "practice_title": row.get("practice_title", ""),
            "sector": row.get("sector", ""),
            "country": row.get("country", ""),
            "company_size": row.get("company_size", ""),
            "challenge_addressed": row.get("challenge_addressed", ""),
            "solution_implemented": row.get("solution_implemented", ""),
            "outcomes": row.get("outcomes", ""),
            "lessons_learned": row.get("lessons_learned", ""),
            "implementation_time": row.get("implementation_time", ""),
            "cost_estimate": row.get("cost_estimate", ""),
            "success_factors": row.get("success_factors", ""),
            "contact_info": row.get("contact_info", ""),
            "rag_category": "best_practice",
            "rag_metadata": {
                "document_type": "case_study",
                "practice_type": "implementation",
                "success_verified": True,
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "company_size": row.get("company_size", ""),
                "implementation_complexity": "medium"
            }
        }

    def _transform_case_study(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform case study for RAG"""
        return {
            "id": row.get("id"),
            "company_name": row.get("company_name", ""),
            "sector": row.get("sector", ""),
            "country": row.get("country", ""),
            "challenge": row.get("challenge", ""),
            "solution": row.get("solution", ""),
            "implementation_steps": row.get("implementation_steps", ""),
            "outcomes": row.get("outcomes", ""),
            "metrics": row.get("metrics", ""),
            "timeline": row.get("timeline", ""),
            "budget": row.get("budget", ""),
            "lessons_learned": row.get("lessons_learned", ""),
            "is_anonymized": row.get("is_anonymized", False),
            "rag_category": "case_study",
            "rag_metadata": {
                "document_type": "case_study",
                "study_type": "implementation",
                "anonymized": row.get("is_anonymized", False),
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "outcome_measured": bool(row.get("metrics")),
                "budget_tracked": bool(row.get("budget"))
            }
        }

    def _transform_company_profile(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform company profile (anonymized) for RAG"""
        # Note: This should only include anonymized, aggregated data
        # Never include sensitive company information
        return {
            "sector": row.get("sector", ""),
            "country": row.get("country", ""),
            "company_size": row.get("size_category", ""),
            "esg_maturity_level": row.get("esg_maturity", ""),
            "main_challenges": row.get("main_challenges", []),
            "successful_practices": row.get("successful_practices", []),
            "rag_category": "aggregated_insights",
            "rag_metadata": {
                "document_type": "aggregated_data",
                "data_type": "anonymized",
                "aggregation_level": "sector_country",
                "geographic_scope": row.get("country", ""),
                "sector_scope": row.get("sector", ""),
                "sample_size": "multiple_companies"
            }
        }


async def main():
    """Main export function"""
    # Database configuration - MODIFY THESE VALUES
    db_config = {
        "host": "localhost",  # Your PostgreSQL host
        "port": 5432,         # Your PostgreSQL port
        "database": "africa_strategy",  # Your database name
        "user": "your_username",      # Your PostgreSQL username
        "password": "your_password"   # Your PostgreSQL password
    }

    # Initialize exporter
    exporter = PgAdminDataExporter(db_config)

    try:
        # Connect to database
        await exporter.connect()

        # Export all data
        logger.info("Starting Africa Strategy data export...")
        summary = await exporter.export_africa_strategy_data("exports")

        # Print summary
        print("\n" + "="*50)
        print("EXPORT SUMMARY")
        print("="*50)
        print(f"Total files exported: {summary['total_files']}")
        print(f"Total records exported: {summary['total_records']}")
        print(f"Export timestamp: {summary['export_timestamp']}")
        print("\nFiles created:")
        for export in summary['exports']:
            if 'records' in export:
                print(f"  ✅ {export['table']}: {export['records']} records")
            else:
                print(f"  ❌ {export['table']}: {export.get('error', 'Failed')}")

        print(f"\n📁 All files saved in 'exports/' directory")
        print("📤 Ready to import into Pinecone RAG system")

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        print(f"\n❌ Export failed: {str(e)}")
    finally:
        await exporter.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())