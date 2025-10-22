"""
AI Service for Africa Strategy
Handles OpenRouter API integration with Gemini 2.5 Flash and Perplexity
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class AIService:
    """Service for AI-powered business analysis using OpenRouter"""

    def __init__(self):
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL

        # Initialize Gemini 2.5 Flash for analysis
        self.gemini_llm = ChatOpenAI(
            model=settings.GEMINI_MODEL,
            openai_api_key=self.openrouter_api_key,
            openai_api_base=self.base_url,
            temperature=0.1,
            max_tokens=4000
        )

        # Initialize Perplexity for internet search
        self.perplexity_llm = ChatOpenAI(
            model=settings.PERPLEXITY_MODEL,
            openai_api_key=self.openrouter_api_key,
            openai_api_base=self.base_url,
            temperature=0.1,
            max_tokens=3000
        )

        logger.info("AI Service initialized with OpenRouter")

    async def analyze_pestel(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze PESTEL factors for a company using Gemini + Perplexity

        Args:
            company_data: Company information from questionnaire

        Returns:
            PESTEL analysis with scores and recommendations
        """
        try:
            # 1. Get current market data using Perplexity
            market_context = await self._get_market_context(company_data)

            # 2. Generate PESTEL analysis with Gemini
            pestel_analysis = await self._generate_pestel_analysis(
                company_data, market_context
            )

            # 3. Calculate overall score
            overall_score = self._calculate_pestel_score(pestel_analysis)

            return {
                "company_name": company_data.get("company_name", "Entreprise"),
                "sector": company_data.get("sector", ""),
                "country": company_data.get("country", ""),
                "analysis_date": datetime.now().isoformat(),
                "pestel": pestel_analysis,
                "overall_score": overall_score,
                "recommendations": self._generate_pestel_recommendations(pestel_analysis),
                "market_context": market_context
            }

        except Exception as e:
            logger.error(f"Error in PESTEL analysis: {str(e)}")
            raise

    async def analyze_esg(self, company_data: Dict[str, Any], esg_responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze ESG factors for a company

        Args:
            company_data: Company information
            esg_responses: ESG questionnaire responses

        Returns:
            ESG analysis with scores and recommendations
        """
        try:
            # 1. Get ESG context and best practices
            esg_context = await self._get_esg_context(company_data)

            # 2. Calculate ESG scores from responses
            esg_scores = self._calculate_esg_scores(esg_responses)

            # 3. Generate detailed ESG analysis
            esg_analysis = await self._generate_esg_analysis(
                company_data, esg_scores, esg_context
            )

            return {
                "company_name": company_data.get("company_name", "Entreprise"),
                "sector": company_data.get("sector", ""),
                "country": company_data.get("country", ""),
                "analysis_date": datetime.now().isoformat(),
                "esg_scores": esg_scores,
                "esg_analysis": esg_analysis,
                "overall_score": (esg_scores["environmental"] + esg_scores["social"] + esg_scores["governance"]) / 3,
                "recommendations": self._generate_esg_recommendations(esg_scores, esg_analysis),
                "esg_context": esg_context
            }

        except Exception as e:
            logger.error(f"Error in ESG analysis: {str(e)}")
            raise

    async def generate_roadmap(self, company_data: Dict[str, Any], analyses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized roadmap based on analyses

        Args:
            company_data: Company information
            analyses: PESTEL and ESG analysis results

        Returns:
            Personalized roadmap with phases and steps
        """
        try:
            roadmap_prompt = f"""
            En tant qu'expert en développement durable pour les PME africaines,
            créez un plan d'action personnalisé (roadmap) pour cette entreprise :

            ENTREPRISE :
            - Nom : {company_data.get('company_name', 'Entreprise')}
            - Secteur : {company_data.get('sector', '')}
            - Pays : {company_data.get('country', '')}
            - Taille : {company_data.get('size', '')}

            ANALYSES :
            - Score PESTEL global : {analyses.get('pestel', {}).get('overall_score', 0)}/10
            - Score ESG global : {analyses.get('esg', {}).get('overall_score', 0)}/100

            POINTS FAIBLES IDENTIFIÉS :
            {self._extract_weaknesses(analyses)}

            Créez une roadmap avec 3 phases :
            1. Diagnostic et Quick Wins (1-3 mois)
            2. Transformation Structurelle (3-6 mois)
            3. Excellence Durable (6-12 mois)

            Pour chaque phase, listez 3-5 étapes concrètes avec :
            - Titre de l'étape
            - Description détaillée
            - Impact sur le score de maturité
            - Coût estimé (en FCFA)
            - Durée estimée
            - Ressources nécessaires

            Format JSON uniquement.
            """

            response = await self.gemini_llm.ainvoke([SystemMessage(content="Vous êtes un expert en développement durable pour les PME africaines."), HumanMessage(content=roadmap_prompt)])

            # Parse and structure the roadmap
            roadmap_data = json.loads(response.content.strip())

            return {
                "company_id": company_data.get("id", ""),
                "generated_at": datetime.now().isoformat(),
                "overall_score": self._calculate_overall_score(analyses),
                "target_score": 85,  # Target score for excellence
                "phases": roadmap_data.get("phases", []),
                "milestones": self._generate_milestones(),
                "estimated_completion": "12_months"
            }

        except Exception as e:
            logger.error(f"Error generating roadmap: {str(e)}")
            raise

    async def chat_with_ai(self, message: str, company_context: Dict[str, Any]) -> str:
        """
        Chat with AI assistant for company-specific advice

        Args:
            message: User message
            company_context: Company information and analyses

        Returns:
            AI response
        """
        try:
            chat_prompt = f"""
            Vous êtes un assistant IA spécialisé dans le développement durable des PME africaines.

            CONTEXTE ENTREPRISE :
            - Nom : {company_context.get('company_name', '')}
            - Secteur : {company_context.get('sector', '')}
            - Pays : {company_context.get('country', '')}
            - Score actuel : {company_context.get('current_score', 0)}/100

            QUESTION UTILISATEUR : {message}

            Répondez de manière :
            1. Spécifique au contexte africain
            2. Pratique et actionnable
            3. Encouragante et motivante
            4. Basée sur les meilleures pratiques ESG

            Réponse concise mais complète.
            """

            response = await self.gemini_llm.ainvoke([SystemMessage(content="Assistant IA pour PME africaines durables"), HumanMessage(content=chat_prompt)])

            return response.content.strip()

        except Exception as e:
            logger.error(f"Error in AI chat: {str(e)}")
            return "Désolé, je rencontre un problème technique. Veuillez réessayer."

    # Private helper methods

    async def _get_market_context(self, company_data: Dict[str, Any]) -> str:
        """Get current market context using Perplexity"""
        query = f"""
        Données économiques et tendances récentes pour {company_data.get('sector', '')}
        en {company_data.get('country', '')} et Afrique de l'Ouest.
        Focus sur : opportunités, défis, réglementations, investissements.
        Actualités des 6 derniers mois.
        """

        try:
            response = await self.perplexity_llm.ainvoke([HumanMessage(content=query)])
            return response.content.strip()
        except Exception as e:
            logger.warning(f"Could not get market context: {str(e)}")
            return "Contexte marché non disponible"

    async def _get_esg_context(self, company_data: Dict[str, Any]) -> str:
        """Get ESG best practices context"""
        query = f"""
        Meilleures pratiques ESG pour les entreprises {company_data.get('sector', '')}
        en Afrique, particulièrement {company_data.get('country', '')}.
        Focus sur : certifications, standards, initiatives régionales.
        """

        try:
            response = await self.perplexity_llm.ainvoke([HumanMessage(content=query)])
            return response.content.strip()
        except Exception as e:
            logger.warning(f"Could not get ESG context: {str(e)}")
            return "Contexte ESG non disponible"

    async def _generate_pestel_analysis(self, company_data: Dict[str, Any], market_context: str) -> Dict[str, Any]:
        """Generate detailed PESTEL analysis"""
        pestel_prompt = f"""
        Analysez les facteurs PESTEL pour cette entreprise africaine :

        ENTREPRISE :
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}
        - Taille : {company_data.get('size', '')}

        CONTEXTE MARCHÉ :
        {market_context}

        Pour chaque facteur PESTEL (Politique, Économique, Social, Technologique, Environnemental, Légal),
        fournissez :
        1. Score sur 10 (0 = très défavorable, 10 = très favorable)
        2. Analyse détaillée (2-3 phrases)
        3. Opportunités identifiées
        4. Menaces identifiées
        5. Recommandations spécifiques

        Format JSON avec structure claire.
        """

        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en analyse stratégique PESTEL"), HumanMessage(content=pestel_prompt)])

        return json.loads(response.content.strip())

    async def _generate_esg_analysis(self, company_data: Dict[str, Any], esg_scores: Dict[str, float], esg_context: str) -> Dict[str, Any]:
        """Generate detailed ESG analysis"""
        esg_prompt = f"""
        Analysez les pratiques ESG de cette entreprise :

        ENTREPRISE :
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}
        - Scores calculés : Environnemental {esg_scores['environmental']}/100, Social {esg_scores['social']}/100, Gouvernance {esg_scores['governance']}/100

        CONTEXTE ESG :
        {esg_context}

        Pour chaque pilier ESG, fournissez :
        1. Évaluation détaillée des forces et faiblesses
        2. Comparaison avec les standards sectoriels
        3. Opportunités d'amélioration
        4. Actions prioritaires
        5. Indicateurs de suivi

        Format JSON structuré.
        """

        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en analyse ESG"), HumanMessage(content=esg_prompt)])

        return json.loads(response.content.strip())

    def _calculate_pestel_score(self, pestel_analysis: Dict[str, Any]) -> float:
        """Calculate overall PESTEL score"""
        factors = ['politique', 'economique', 'social', 'technologique', 'environnemental', 'legal']
        total_score = 0

        for factor in factors:
            if factor in pestel_analysis and 'score' in pestel_analysis[factor]:
                total_score += pestel_analysis[factor]['score']

        return round(total_score / len(factors), 1)

    def _calculate_esg_scores(self, esg_responses: Dict[str, Any]) -> Dict[str, float]:
        """Calculate ESG scores from questionnaire responses"""
        # This is a simplified scoring logic - can be enhanced
        environmental_score = self._score_environmental_responses(esg_responses)
        social_score = self._score_social_responses(esg_responses)
        governance_score = self._score_governance_responses(esg_responses)

        return {
            "environmental": environmental_score,
            "social": social_score,
            "governance": governance_score
        }

    def _score_environmental_responses(self, responses: Dict[str, Any]) -> float:
        """Score environmental responses"""
        # Simplified scoring - can be made more sophisticated
        score = 50  # Base score

        # Add points for positive environmental practices
        if responses.get('energy_consumption') == 'yes_detailed':
            score += 20
        elif responses.get('energy_consumption') == 'yes_basic':
            score += 10

        if responses.get('waste_management') == 'recycling_program':
            score += 20
        elif responses.get('waste_management') == 'basic_separation':
            score += 10

        return min(100, max(0, score))

    def _score_social_responses(self, responses: Dict[str, Any]) -> float:
        """Score social responses"""
        score = 50  # Base score

        if responses.get('employee_training') == 'regular_training':
            score += 25
        elif responses.get('employee_training') == 'occasional':
            score += 10

        return min(100, max(0, score))

    def _score_governance_responses(self, responses: Dict[str, Any]) -> float:
        """Score governance responses"""
        score = 50  # Base score

        # Add governance scoring logic here
        # This is a placeholder for actual governance questions

        return min(100, max(0, score))

    def _generate_pestel_recommendations(self, pestel_analysis: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations from PESTEL analysis"""
        recommendations = []

        for factor, data in pestel_analysis.items():
            if data.get('score', 0) < 6:  # Below average
                if 'recommendations' in data:
                    recommendations.extend(data['recommendations'][:2])  # Top 2 per factor

        return recommendations[:5]  # Top 5 overall

    def _generate_esg_recommendations(self, esg_scores: Dict[str, float], esg_analysis: Dict[str, Any]) -> List[str]:
        """Generate ESG recommendations"""
        recommendations = []

        for pillar, score in esg_scores.items():
            if score < 60:  # Below threshold
                if pillar in esg_analysis and 'actions_prioritaires' in esg_analysis[pillar]:
                    recommendations.extend(esg_analysis[pillar]['actions_prioritaires'][:2])

        return recommendations[:5]

    def _extract_weaknesses(self, analyses: Dict[str, Any]) -> str:
        """Extract main weaknesses from analyses"""
        weaknesses = []

        pestel_score = analyses.get('pestel', {}).get('overall_score', 5)
        if pestel_score < 6:
            weaknesses.append(f"Score PESTEL faible ({pestel_score}/10)")

        esg_score = analyses.get('esg', {}).get('overall_score', 50)
        if esg_score < 60:
            weaknesses.append(f"Score ESG faible ({esg_score}/100)")

        return "\n".join(weaknesses) if weaknesses else "Aucune faiblesse majeure identifiée"

    def _calculate_overall_score(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall company maturity score"""
        pestel_score = analyses.get('pestel', {}).get('overall_score', 5)
        esg_score = analyses.get('esg', {}).get('overall_score', 50)

        # Convert to same scale and average
        normalized_pestel = (pestel_score / 10) * 100
        overall_score = (normalized_pestel + esg_score) / 2

        return round(overall_score, 1)

    def _generate_milestones(self) -> List[Dict[str, Any]]:
        """Generate achievement milestones"""
        return [
            {
                "score": 50,
                "title": "Entreprise Consciente",
                "benefits": [
                    "Badge Bronze",
                    "Accès formations avancées",
                    "Visible par investisseurs locaux"
                ]
            },
            {
                "score": 75,
                "title": "Entreprise Engagée",
                "benefits": [
                    "Badge Argent",
                    "Matching fonds d'impact",
                    "Certification ESG"
                ]
            },
            {
                "score": 85,
                "title": "Entreprise Leader",
                "benefits": [
                    "Badge Or",
                    "Accès investisseurs internationaux",
                    "Partenariats stratégiques"
                ]
            }
        ]


# Global AI service instance
ai_service = AIService()