"""
Service OpenRouter pour enrichir les analyses
Utilise l'API OpenRouter pour résumer et synthétiser les contenus
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service pour appeler OpenRouter et enrichir les analyses"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3.5-sonnet"  # Modèle puissant pour résumés
        
    async def summarize_text(self, text: str, max_words: int = 200) -> str:
        """
        Résume un texte long en gardant les points essentiels
        """
        if not text or len(text) < 100:
            return text
            
        try:
            prompt = f"""Résume le texte suivant en {max_words} mots maximum, en gardant tous les points clés, chiffres importants et recommandations principales. Réponds uniquement avec le résumé, sans introduction.

TEXTE À RÉSUMER:
{text}

RÉSUMÉ:"""

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": max_words * 2,
                        "temperature": 0.3,
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    summary = result["choices"][0]["message"]["content"]
                    logger.info(f"✅ Texte résumé: {len(text)} -> {len(summary)} caractères")
                    return summary.strip()
                else:
                    logger.error(f"Erreur OpenRouter: {response.status_code}")
                    return text[:500] + "..."  # Fallback: tronquer
                    
        except Exception as e:
            logger.error(f"Erreur lors du résumé: {str(e)}")
            return text[:500] + "..."
    
    async def generate_synthesis(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une synthèse stratégique complète à partir de toutes les analyses
        """
        try:
            # Préparer le contexte avec toutes les analyses
            context = f"""Tu es un expert en stratégie d'entreprise. Tu dois créer une synthèse stratégique complète et détaillée basée sur les analyses suivantes:

ANALYSES DISPONIBLES:
{self._format_analyses_for_prompt(analyses)}

INSTRUCTIONS:
1. Crée une synthèse exécutive globale (200-300 mots)
2. Identifie 5-7 points clés stratégiques
3. Liste 3-5 forces principales
4. Liste 3-5 faiblesses principales
5. Identifie 5-10 opportunités concrètes
6. Identifie 5-10 menaces/risques
7. Propose 8-12 recommandations stratégiques prioritaires
8. Donne une vision stratégique à 3-5 ans
9. Évalue le niveau de maturité stratégique (avec justification)
10. Propose des KPIs de suivi

Réponds en JSON avec cette structure:
{{
  "executive_summary": "...",
  "key_points": ["...", "..."],
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "opportunities": ["...", "..."],
  "threats": ["...", "..."],
  "strategic_recommendations": ["...", "..."],
  "vision_3_5_years": "...",
  "maturity_level": "...",
  "maturity_justification": "...",
  "kpis": ["...", "..."]
}}"""

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": context
                            }
                        ],
                        "max_tokens": 3000,
                        "temperature": 0.5,
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    synthesis_text = result["choices"][0]["message"]["content"]
                    
                    # Parser le JSON
                    import json
                    # Extraire le JSON du texte (peut être entouré de ```json```)
                    if "```json" in synthesis_text:
                        synthesis_text = synthesis_text.split("```json")[1].split("```")[0]
                    elif "```" in synthesis_text:
                        synthesis_text = synthesis_text.split("```")[1].split("```")[0]
                    
                    synthesis = json.loads(synthesis_text.strip())
                    logger.info("✅ Synthèse stratégique générée avec succès")
                    return synthesis
                else:
                    logger.error(f"Erreur OpenRouter: {response.status_code}")
                    return self._create_fallback_synthesis()
                    
        except Exception as e:
            logger.error(f"Erreur lors de la génération de synthèse: {str(e)}")
            return self._create_fallback_synthesis()
    
    def _format_analyses_for_prompt(self, analyses: Dict[str, Any]) -> str:
        """Formate les analyses pour le prompt"""
        import json
        # Limiter la taille pour ne pas dépasser les limites de tokens
        formatted = {}
        for key, value in analyses.items():
            if isinstance(value, dict):
                # Prendre les scores et un résumé si disponible
                formatted[key] = {
                    "scores": value.get("scores", {}),
                    "summary": value.get("summary", value.get("analysis", ""))[:500]
                }
            else:
                formatted[key] = str(value)[:200]
        
        return json.dumps(formatted, indent=2, ensure_ascii=False)
    
    def _create_fallback_synthesis(self) -> Dict[str, Any]:
        """Crée une synthèse par défaut en cas d'erreur"""
        return {
            "executive_summary": "Synthèse stratégique en cours de génération...",
            "key_points": [],
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
            "strategic_recommendations": [],
            "vision_3_5_years": "",
            "maturity_level": "En évaluation",
            "maturity_justification": "",
            "kpis": []
        }
    
    async def enrich_all_tabs(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit TOUS les onglets avec des résumés intelligents
        """
        enriched = {}
        
        for tab_name, tab_data in analyses.items():
            if not isinstance(tab_data, dict):
                enriched[tab_name] = tab_data
                continue
                
            logger.info(f"Enrichissement de l'onglet: {tab_name}")
            enriched_tab = tab_data.copy()
            
            # Résumer l'analyse principale
            if "analysis" in tab_data and isinstance(tab_data["analysis"], str):
                if len(tab_data["analysis"]) > 500:
                    enriched_tab["analysis_short"] = await self.summarize_text(
                        tab_data["analysis"], 
                        max_words=100
                    )
                    enriched_tab["analysis_medium"] = await self.summarize_text(
                        tab_data["analysis"], 
                        max_words=200
                    )
            
            # Résumer la description
            if "description" in tab_data and isinstance(tab_data["description"], str):
                if len(tab_data["description"]) > 500:
                    enriched_tab["description_short"] = await self.summarize_text(
                        tab_data["description"], 
                        max_words=100
                    )
            
            # Extraire des points clés
            analysis_text = tab_data.get("analysis", "") or tab_data.get("description", "")
            if analysis_text and len(analysis_text) > 200:
                enriched_tab["key_points"] = await self._extract_key_points(analysis_text)
            
            enriched[tab_name] = enriched_tab
        
        logger.info(f"✅ Enrichissement terminé pour {len(enriched)} onglets")
        return enriched
    
    async def _extract_key_points(self, text: str) -> list:
        """Extrait 5-7 points clés d'un texte"""
        if not text or len(text) < 100:
            return []
            
        prompt = f"""Extrait 5-7 points clés essentiels de ce texte. Chaque point doit être une phrase courte et impactante.

TEXTE:
{text[:2000]}

Réponds uniquement avec une liste JSON de strings:
["Point 1", "Point 2", ...]"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500,
                        "temperature": 0.3,
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Parser le JSON
                    import json
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0]
                    
                    points = json.loads(content.strip())
                    logger.info(f"✅ {len(points)} points clés extraits")
                    return points
                else:
                    logger.warning(f"Erreur extraction points clés: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Erreur extraction points clés: {str(e)}")
            return []


# Instance globale
openrouter_service = OpenRouterService()



