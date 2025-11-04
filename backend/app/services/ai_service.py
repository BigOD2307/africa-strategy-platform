"""
Enhanced AI Service with RAG integration
Combines OpenRouter (Gemini + Perplexity) with Pinecone RAG for superior analyses
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class EnhancedAIService:
    """
    Enhanced AI Service with RAG integration for Africa Strategy
    """

    def __init__(self):
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.perplexity_model = settings.PERPLEXITY_MODEL

        # Initialize HTTP client for OpenRouter
        try:
            import httpx
            self.client = httpx.AsyncClient(
                timeout=60.0,
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                }
            )
            logger.info("Enhanced AI Service initialized with OpenRouter + RAG")
        except Exception as e:
            logger.error(f"Failed to initialize HTTP client: {str(e)}")
            self.client = None

    async def _call_openrouter(self, model: str, messages: List[Dict[str, str]],
                              temperature: float = 0.1) -> Optional[str]:
        """Call OpenRouter API"""
        if not self.client:
            logger.error("HTTP client not initialized")
            return None

        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4000
            }

            response = await self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to call OpenRouter: {str(e)}")
            return None

    async def _get_perplexity_context(self, query: str) -> str:
        """Get context from Perplexity for current information"""
        if not self.client:
            return ""

        try:
            messages = [
                {
                    "role": "user",
                    "content": f"Provide current, factual information about: {query}. Focus on recent developments, trends, and data for Africa, especially Côte d'Ivoire and West Africa. Be concise but comprehensive."
                }
            ]

            context = await self._call_openrouter(self.perplexity_model, messages, temperature=0.1)
            return context or ""

        except Exception as e:
            logger.error(f"Failed to get Perplexity context: {str(e)}")
            return ""

    async def _get_rag_context(self, company_data: Dict[str, Any], analysis_type: str) -> str:
        """Get contextual information from RAG system"""
        try:
            enriched_context = await rag_service.enrich_analysis_context(company_data, analysis_type)

            if enriched_context.get('available', False):
                return enriched_context.get('rag_context', '')
            else:
                logger.info(f"RAG context not available for {analysis_type}")
                return ""

        except Exception as e:
            logger.error(f"Failed to get RAG context: {str(e)}")
            return ""

    async def analyze_pestel_enhanced(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced PESTEL analysis with RAG + Perplexity + Gemini

        Args:
            company_data: Company information

        Returns:
            Complete PESTEL analysis
        """
        logger.info(f"Starting enhanced PESTEL analysis for {company_data.get('company_name', 'Unknown')}")

        try:
            # 1. Get RAG context for sector/country
            rag_context = await self._get_rag_context(company_data, 'pestel')

            # 2. Get current information from Perplexity
            perplexity_query = f"PESTEL analysis trends {company_data.get('sector', '')} {company_data.get('country', '')} 2024-2025"
            perplexity_context = await self._get_perplexity_context(perplexity_query)

            # 3. Build enhanced prompt
            prompt = f"""
Vous êtes un expert en analyse stratégique PESTEL pour l'Afrique. Analysez cette entreprise africaine avec une approche experte.

ENTREPRISE À ANALYSER:
- Nom: {company_data.get('company_name', '')}
- Secteur: {company_data.get('sector', '')}
- Pays: {company_data.get('country', '')}
- Taille: {company_data.get('size', '')}

CONTEXTE SECTORIEL (Base de connaissances):
{rag_context}

CONTEXTE ACTUEL (Données 2024-2025):
{perplexity_context}

INSTRUCTIONS:
Générez une analyse PESTEL professionnelle avec:
1. Score 0-10 pour chaque dimension (Politique, Économique, Social, Technologique, Environnemental, Légal)
2. Analyse détaillée justifiant chaque score
3. Recommandations prioritaires par dimension
4. Opportunités et menaces identifiées
5. Score global consolidé

Format JSON strict:
{{
  "politique": {{"score": 0, "analyse": "", "recommandations": []}},
  "economique": {{"score": 0, "analyse": "", "recommandations": []}},
  "social": {{"score": 0, "analyse": "", "recommandations": []}},
  "technologique": {{"score": 0, "analyse": "", "recommandations": []}},
  "environnemental": {{"score": 0, "analyse": "", "recommandations": []}},
  "legal": {{"score": 0, "analyse": "", "recommandations": []}},
  "opportunites": [],
  "menaces": [],
  "score_global": 0,
  "recommandations_prioritaires": []
}}
"""

            # 4. Call Gemini for analysis
            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            if not response:
                raise Exception("Failed to get response from Gemini")

            # 5. Parse and validate response
            try:
                result = json.loads(response)
                # Add metadata
                result.update({
                    "analysis_type": "pestel",
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.gemini_model,
                    "rag_context_used": bool(rag_context.strip()),
                    "perplexity_context_used": bool(perplexity_context.strip())
                })
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse PESTEL response: {str(e)}")
                logger.error(f"Raw response: {response[:500]}...")
                raise Exception("Invalid JSON response from AI model")

        except Exception as e:
            logger.error(f"Enhanced PESTEL analysis failed: {str(e)}")
            raise

    async def analyze_esg_enhanced(self, company_data: Dict[str, Any],
                                  esg_responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced ESG analysis with RAG + Perplexity + Gemini

        Args:
            company_data: Company information
            esg_responses: ESG questionnaire responses

        Returns:
            Complete ESG analysis
        """
        logger.info(f"Starting enhanced ESG analysis for {company_data.get('company_name', 'Unknown')}")

        try:
            # 1. Get RAG context for ESG frameworks
            rag_context = await self._get_rag_context(company_data, 'esg')

            # 2. Get current ESG trends from Perplexity
            perplexity_query = f"ESG trends and standards {company_data.get('sector', '')} Africa 2024-2025"
            perplexity_context = await self._get_perplexity_context(perplexity_query)

            # 3. Build enhanced prompt
            prompt = f"""
Vous êtes un expert ESG pour les entreprises africaines. Analysez cette entreprise avec une approche professionnelle.

ENTREPRISE À ANALYSER:
- Nom: {company_data.get('company_name', '')}
- Secteur: {company_data.get('sector', '')}
- Pays: {company_data.get('country', '')}
- Taille: {company_data.get('size', '')}

RÉPONSES ESG (Questionnaire):
{json.dumps(esg_responses, indent=2, ensure_ascii=False)}

CADRES ESG RÉFÉRENCE (Base de connaissances):
{rag_context}

TENDANCES ESG ACTUELLES (2024-2025):
{perplexity_context}

INSTRUCTIONS:
Analysez les pratiques ESG de l'entreprise et générez:
1. Scores Environnemental/Social/Gouvernance (0-100)
2. Analyse détaillée par pilier
3. Points forts et axes d'amélioration
4. Plan d'action priorisé
5. Score ESG global

Format JSON strict:
{{
  "environmental": {{
    "score": 0,
    "analysis": "",
    "strengths": [],
    "improvements": []
  }},
  "social": {{
    "score": 0,
    "analysis": "",
    "strengths": [],
    "improvements": []
  }},
  "governance": {{
    "score": 0,
    "analysis": "",
    "strengths": [],
    "improvements": []
  }},
  "overall_score": 0,
  "maturity_level": "",
  "action_plan": [],
  "recommendations": []
}}
"""

            # 4. Call Gemini for analysis
            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            if not response:
                raise Exception("Failed to get response from Gemini")

            # 5. Parse and validate response
            try:
                result = json.loads(response)
                # Add metadata
                result.update({
                    "analysis_type": "esg",
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.gemini_model,
                    "rag_context_used": bool(rag_context.strip()),
                    "perplexity_context_used": bool(perplexity_context.strip())
                })
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse ESG response: {str(e)}")
                logger.error(f"Raw response: {response[:500]}...")
                raise Exception("Invalid JSON response from AI model")

        except Exception as e:
            logger.error(f"Enhanced ESG analysis failed: {str(e)}")
            raise

    async def analyze_integrated_synthesis(self, company_data: Dict[str, Any],
                                         esg_responses: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete integrated analysis: PESTEL + ESG + Market + Value Chain + Impact + Synthesis

        Args:
            company_data: Company information
            esg_responses: ESG questionnaire responses

        Returns:
            Complete strategic analysis
        """
        logger.info(f"Starting integrated synthesis for {company_data.get('company_name', 'Unknown')}")

        try:
            # Run all analyses in parallel for efficiency
            import asyncio

            tasks = []

            # PESTEL Analysis
            tasks.append(self.analyze_pestel_enhanced(company_data))

            # ESG Analysis (if responses provided)
            if esg_responses:
                tasks.append(self.analyze_esg_enhanced(company_data, esg_responses))
            else:
                # Create placeholder ESG analysis
                tasks.append(self._create_placeholder_esg())

            # Market Analysis
            tasks.append(self._analyze_market_enhanced(company_data))

            # Value Chain Analysis
            tasks.append(self._analyze_value_chain_enhanced(company_data))

            # Sustainability Impact Analysis
            tasks.append(self._analyze_sustainability_impact_enhanced(company_data))

            # Execute all analyses
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            pestel_result = results[0] if not isinstance(results[0], Exception) else None
            esg_result = results[1] if not isinstance(results[1], Exception) else None
            market_result = results[2] if not isinstance(results[2], Exception) else None
            value_chain_result = results[3] if not isinstance(results[3], Exception) else None
            impact_result = results[4] if not isinstance(results[4], Exception) else None

            # Generate integrated synthesis
            synthesis = await self._generate_integrated_synthesis(
                company_data, pestel_result, esg_result, market_result,
                value_chain_result, impact_result
            )

            # Calculate overall score
            overall_score = self._calculate_overall_score(synthesis)

            # Generate strategic roadmap
            roadmap = await self._generate_strategic_roadmap(company_data, synthesis, overall_score)

            # Compile final result
            final_result = {
                "company_info": company_data,
                "pestel": pestel_result,
                "esg": esg_result,
                "market_competition": market_result,
                "value_chain": value_chain_result,
                "sustainability_impact": impact_result,
                "integrated_synthesis": synthesis,
                "overall_score": overall_score,
                "maturity_level": self._get_maturity_level(overall_score),
                "strategic_roadmap": roadmap,
                "generated_at": datetime.now().isoformat(),
                "analysis_version": "2.0-enhanced-rag"
            }

            logger.info(f"Integrated synthesis completed for {company_data.get('company_name', 'Unknown')}")
            return final_result

        except Exception as e:
            logger.error(f"Integrated synthesis failed: {str(e)}")
            raise

    async def _analyze_market_enhanced(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced market analysis"""
        try:
            rag_context = await self._get_rag_context(company_data, 'market')
            perplexity_context = await self._get_perplexity_context(
                f"Market analysis {company_data.get('sector', '')} {company_data.get('country', '')} 2024-2025"
            )

            prompt = f"Analyze market for {company_data.get('company_name', '')} in {company_data.get('sector', '')} sector, {company_data.get('country', '')}. Use this context: {rag_context[:1000]}... and current data: {perplexity_context[:1000]}..."

            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            return json.loads(response) if response else {"error": "Market analysis failed"}

        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _analyze_value_chain_enhanced(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced value chain analysis"""
        try:
            rag_context = await self._get_rag_context(company_data, 'value_chain')
            perplexity_context = await self._get_perplexity_context(
                f"Value chain analysis {company_data.get('sector', '')} Africa"
            )

            prompt = f"Analyze value chain for {company_data.get('company_name', '')} in {company_data.get('sector', '')}. Context: {rag_context[:1000]}... Current trends: {perplexity_context[:1000]}..."

            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            return json.loads(response) if response else {"error": "Value chain analysis failed"}

        except Exception as e:
            logger.error(f"Value chain analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _analyze_sustainability_impact_enhanced(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced sustainability impact analysis"""
        try:
            rag_context = await self._get_rag_context(company_data, 'sustainability')
            perplexity_context = await self._get_perplexity_context(
                f"Sustainability impact {company_data.get('sector', '')} {company_data.get('country', '')} ODD goals"
            )

            prompt = f"Analyze sustainability impact for {company_data.get('company_name', '')}. Context: {rag_context[:1000]}... Current frameworks: {perplexity_context[:1000]}..."

            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            return json.loads(response) if response else {"error": "Sustainability impact analysis failed"}

        except Exception as e:
            logger.error(f"Sustainability impact analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _generate_integrated_synthesis(self, company_data: Dict[str, Any],
                                           pestel: Optional[Dict], esg: Optional[Dict],
                                           market: Optional[Dict], value_chain: Optional[Dict],
                                           impact: Optional[Dict]) -> Dict[str, Any]:
        """Generate integrated synthesis from all analyses"""
        try:
            prompt = f"""
Générez une synthèse intégrale pour {company_data.get('company_name', '')} en combinant toutes les analyses:

PESTEL: {json.dumps(pestel, ensure_ascii=False) if pestel else 'N/A'}
ESG: {json.dumps(esg, ensure_ascii=False) if esg else 'N/A'}
MARCHÉ: {json.dumps(market, ensure_ascii=False) if market else 'N/A'}
CHAÎNE DE VALEUR: {json.dumps(value_chain, ensure_ascii=False) if value_chain else 'N/A'}
IMPACT DURABLE: {json.dumps(impact, ensure_ascii=False) if impact else 'N/A'}

Format: {{"executive_summary": "", "key_findings": [], "strategic_recommendations": [], "risks_opportunities": {{}}}}
"""

            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            return json.loads(response) if response else {"error": "Synthesis generation failed"}

        except Exception as e:
            logger.error(f"Synthesis generation failed: {str(e)}")
            return {"error": str(e)}

    def _calculate_overall_score(self, synthesis: Dict[str, Any]) -> float:
        """Calculate overall company score"""
        try:
            # Simple scoring logic - can be enhanced
            base_score = 50.0  # Starting point

            # Adjust based on synthesis insights
            if synthesis and 'key_findings' in synthesis:
                findings = synthesis['key_findings']
                if any('opportunité' in str(f).lower() for f in findings):
                    base_score += 10
                if any('risque' in str(f).lower() for f in findings):
                    base_score -= 5

            return min(100.0, max(0.0, base_score))

        except Exception:
            return 50.0  # Default score

    def _get_maturity_level(self, score: float) -> str:
        """Get maturity level based on score"""
        if score >= 80:
            return "Leader"
        elif score >= 65:
            return "Engagé"
        elif score >= 50:
            return "Conscient"
        else:
            return "Débutant"

    async def _generate_strategic_roadmap(self, company_data: Dict[str, Any],
                                        synthesis: Dict[str, Any], score: float) -> Dict[str, Any]:
        """Generate strategic roadmap"""
        try:
            prompt = f"""
Générez un plan d'action stratégique sur 24 mois pour {company_data.get('company_name', '')}.
Score actuel: {score}/100
Secteur: {company_data.get('sector', '')}
Pays: {company_data.get('country', '')}

Synthèse: {json.dumps(synthesis, ensure_ascii=False)[:1000]}...

Format: {{"phases": [], "total_investment": "", "expected_roi": "", "success_factors": []}}
"""

            messages = [{"role": "user", "content": prompt}]
            response = await self._call_openrouter(self.gemini_model, messages)

            return json.loads(response) if response else {"error": "Roadmap generation failed"}

        except Exception as e:
            logger.error(f"Roadmap generation failed: {str(e)}")
            return {"error": str(e)}

    async def _create_placeholder_esg(self) -> Dict[str, Any]:
        """Create placeholder ESG analysis when no responses provided"""
        return {
            "environmental": {"score": 0, "analysis": "Aucune donnée ESG fournie", "strengths": [], "improvements": []},
            "social": {"score": 0, "analysis": "Aucune donnée ESG fournie", "strengths": [], "improvements": []},
            "governance": {"score": 0, "analysis": "Aucune donnée ESG fournie", "strengths": [], "improvements": []},
            "overall_score": 0,
            "maturity_level": "Non évalué",
            "action_plan": ["Remplir le questionnaire ESG pour obtenir une analyse complète"],
            "recommendations": []
        }

    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()


# Global enhanced AI service instance
enhanced_ai_service = EnhancedAIService()