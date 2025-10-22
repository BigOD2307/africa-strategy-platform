    async def analyze_market_competition(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market and competition for a company

        Args:
            company_data: Company information

        Returns:
            Market and competition analysis
        """
        try:
            # Get market data using Perplexity
            market_context = await self._get_market_competition_data(company_data)

            # Generate competition analysis
            competition_analysis = await self._generate_market_competition_analysis(
                company_data, market_context
            )

            return {
                "company_name": company_data.get("company_name", "Entreprise"),
                "sector": company_data.get("sector", ""),
                "country": company_data.get("country", ""),
                "analysis_date": datetime.now().isoformat(),
                "market_size": competition_analysis.get("market_size", {}),
                "competition_analysis": competition_analysis.get("competition", {}),
                "market_trends": competition_analysis.get("trends", []),
                "opportunities": competition_analysis.get("opportunities", []),
                "threats": competition_analysis.get("threats", []),
                "market_context": market_context
            }

        except Exception as e:
            logger.error(f"Error in market competition analysis: {str(e)}")
            raise

    async def analyze_value_chain(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze value chain for a company

        Args:
            company_data: Company information

        Returns:
            Value chain analysis
        """
        try:
            # Get value chain context
            value_chain_context = await self._get_value_chain_context(company_data)

            # Generate value chain analysis
            value_chain_analysis = await self._generate_value_chain_analysis(
                company_data, value_chain_context
            )

            return {
                "company_name": company_data.get("company_name", "Entreprise"),
                "sector": company_data.get("sector", ""),
                "country": company_data.get("country", ""),
                "analysis_date": datetime.now().isoformat(),
                "primary_activities": value_chain_analysis.get("primary_activities", []),
                "support_activities": value_chain_analysis.get("support_activities", []),
                "value_creation_points": value_chain_analysis.get("value_creation_points", []),
                "efficiency_opportunities": value_chain_analysis.get("efficiency_opportunities", []),
                "competitive_advantages": value_chain_analysis.get("competitive_advantages", []),
                "value_chain_context": value_chain_context
            }

        except Exception as e:
            logger.error(f"Error in value chain analysis: {str(e)}")
            raise

    async def analyze_sustainability_impact(self, company_data: Dict[str, Any], esg_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sustainability impact and SDGs contribution

        Args:
            company_data: Company information
            esg_data: ESG analysis data

        Returns:
            Sustainability impact analysis
        """
        try:
            # Get SDGs and sustainability context
            sustainability_context = await self._get_sustainability_context(company_data)

            # Generate sustainability impact analysis
            impact_analysis = await self._generate_sustainability_impact_analysis(
                company_data, esg_data, sustainability_context
            )

            return {
                "company_name": company_data.get("company_name", "Entreprise"),
                "sector": company_data.get("sector", ""),
                "country": company_data.get("country", ""),
                "analysis_date": datetime.now().isoformat(),
                "sdgs_contribution": impact_analysis.get("sdgs_contribution", []),
                "environmental_impact": impact_analysis.get("environmental_impact", {}),
                "social_impact": impact_analysis.get("social_impact", {}),
                "economic_impact": impact_analysis.get("economic_impact", {}),
                "sustainability_score": impact_analysis.get("sustainability_score", 0),
                "impact_recommendations": impact_analysis.get("impact_recommendations", []),
                "sustainability_context": sustainability_context
            }

        except Exception as e:
            logger.error(f"Error in sustainability impact analysis: {str(e)}")
            raise

    async def generate_integrated_synthesis(self, company_data: Dict[str, Any], all_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate integrated synthesis of all analyses

        Args:
            company_data: Company information
            all_analyses: All analysis results (PESTEL, Market, Value Chain, ESG, Impact)

        Returns:
            Integrated synthesis and strategic recommendations
        """
        try:
            # Generate comprehensive synthesis
            synthesis = await self._generate_integrated_synthesis(
                company_data, all_analyses
            )

            return {
                "company_name": company_data.get("company_name", "Entreprise"),
                "sector": company_data.get("sector", ""),
                "country": company_data.get("country", ""),
                "analysis_date": datetime.now().isoformat(),
                "executive_summary": synthesis.get("executive_summary", ""),
                "key_findings": synthesis.get("key_findings", []),
                "strategic_recommendations": synthesis.get("strategic_recommendations", []),
                "implementation_priorities": synthesis.get("implementation_priorities", []),
                "risk_assessment": synthesis.get("risk_assessment", {}),
                "growth_opportunities": synthesis.get("growth_opportunities", []),
                "sustainability_transformation": synthesis.get("sustainability_transformation", {}),
                "overall_score": synthesis.get("overall_score", 0),
                "maturity_level": synthesis.get("maturity_level", ""),
                "next_steps": synthesis.get("next_steps", [])
            }

        except Exception as e:
            logger.error(f"Error in integrated synthesis: {str(e)}")
            raise

    async def generate_strategic_roadmap(self, company_data: Dict[str, Any], synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate strategic roadmap based on synthesis

        Args:
            company_data: Company information
            synthesis: Integrated synthesis results

        Returns:
            Strategic roadmap with phases and actions
        """
        try:
            roadmap = await self._generate_strategic_roadmap(company_data, synthesis)

            return {
                "company_id": company_data.get("id", ""),
                "generated_at": datetime.now().isoformat(),
                "overall_score": synthesis.get("overall_score", 0),
                "target_score": 85,
                "roadmap_title": roadmap.get("title", ""),
                "phases": roadmap.get("phases", []),
                "milestones": roadmap.get("milestones", []),
                "estimated_timeline": roadmap.get("estimated_timeline", ""),
                "total_investment": roadmap.get("total_investment", ""),
                "expected_roi": roadmap.get("expected_roi", ""),
                "success_metrics": roadmap.get("success_metrics", [])
            }

        except Exception as e:
            logger.error(f"Error generating strategic roadmap: {str(e)}")
            raise

    async def chat_with_context(self, message: str, company_context: Dict[str, Any], analyses_context: Dict[str, Any]) -> str:
        """
        Enhanced chat with full context of all analyses

        Args:
            message: User message
            company_context: Company information
            analyses_context: All analysis results

        Returns:
            Contextual AI response
        """
        try:
            # Create comprehensive context
            full_context = {
                "company": company_context,
                "analyses": analyses_context,
                "current_date": datetime.now().isoformat(),
                "conversation_history": []  # Could be enhanced with actual history
            }

            chat_prompt = f"""
            Tu es un assistant IA expert en stratégie d'entreprise et développement durable pour PME africaines.

            CONTEXTE COMPLET DE L'ENTREPRISE :
            - Nom : {full_context['company'].get('company_name', '')}
            - Secteur : {full_context['company'].get('sector', '')}
            - Pays : {full_context['company'].get('country', '')}
            - Score global : {analyses_context.get('overall_score', 0)}/100

            ANALYSES DISPONIBLES :
            - PESTEL : {analyses_context.get('pestel', {}).get('overall_score', 'N/A')}/10
            - ESG : {analyses_context.get('esg', {}).get('overall_score', 'N/A')}/100
            - Marché : {len(analyses_context.get('market_competition', {}).get('opportunities', []))} opportunités identifiées
            - Chaîne de valeur : {len(analyses_context.get('value_chain', {}).get('efficiency_opportunities', []))} opportunités d'efficacité
            - Impact durable : {analyses_context.get('sustainability_impact', {}).get('sustainability_score', 'N/A')}/100

            QUESTION UTILISATEUR : {message}

            Réponds de manière :
            1. **Contextuelle** : Utilise les données des analyses disponibles
            2. **Actionnable** : Donne des conseils pratiques et spécifiques
            3. **Africaine** : Considère le contexte africain et local
            4. **Stratégique** : Lie les réponses aux objectifs de durabilité
            5. **Mesurable** : Quand possible, suggère des KPIs ou métriques

            Si la question nécessite des données spécifiques des analyses, fais référence aux résultats disponibles.
            Si c'est une question générale, utilise ta connaissance générale enrichie du contexte.
            """

            response = await self.gemini_llm.ainvoke([SystemMessage(content="Assistant IA stratégique pour PME africaines"), HumanMessage(content=chat_prompt)])

            return response.content.strip()

        except Exception as e:
            logger.error(f"Error in contextual chat: {str(e)}")
            return "Désolé, je rencontre un problème technique. Veuillez réessayer ou contacter le support."

    # Private helper methods for new analyses

    async def _get_market_competition_data(self, company_data: Dict[str, Any]) -> str:
        """Get market and competition data"""
        query = f"""
        Analyse du marché et de la concurrence pour {company_data.get('sector', '')}
        en {company_data.get('country', '')} et Afrique de l'Ouest.
        Inclure : taille du marché, acteurs principaux, tendances,
        opportunités de croissance, menaces concurrentielles.
        Données récentes et projections.
        """
        response = await self.perplexity_llm.ainvoke([HumanMessage(content=query)])
        return response.content.strip()

    async def _get_value_chain_context(self, company_data: Dict[str, Any]) -> str:
        """Get value chain context"""
        query = f"""
        Analyse de la chaîne de valeur pour le secteur {company_data.get('sector', '')}
        en Afrique, particulièrement {company_data.get('country', '')}.
        Inclure : activités primaires, activités de support,
        points de création de valeur, opportunités d'optimisation.
        """
        response = await self.perplexity_llm.ainvoke([HumanMessage(content=query)])
        return response.content.strip()

    async def _get_sustainability_context(self, company_data: Dict[str, Any]) -> str:
        """Get sustainability and SDGs context"""
        query = f"""
        Impact durable et contribution aux ODD pour les entreprises {company_data.get('sector', '')}
        en {company_data.get('country', '')}.
        Inclure : ODD pertinents, mesures d'impact, meilleures pratiques,
        certifications disponibles, initiatives régionales.
        """
        response = await self.perplexity_llm.ainvoke([HumanMessage(content=query)])
        return response.content.strip()

    async def _generate_market_competition_analysis(self, company_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate market competition analysis"""
        prompt = f"""
        Analyse approfondie du marché et de la concurrence :

        ENTREPRISE :
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}
        - Taille : {company_data.get('size', '')}

        CONTEXTE MARCHÉ :
        {context}

        Fournis une analyse structurée avec :
        1. Taille et croissance du marché
        2. Analyse des concurrents (5 principaux)
        3. Positionnement concurrentiel
        4. Tendances du marché (3-5 ans)
        5. Opportunités de croissance
        6. Menaces concurrentielles

        Format JSON détaillé.
        """
        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en analyse de marché"), HumanMessage(content=prompt)])
        return json.loads(response.content.strip())

    async def _generate_value_chain_analysis(self, company_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate value chain analysis"""
        prompt = f"""
        Analyse de la chaîne de valeur :

        ENTREPRISE :
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}
        - Activités : {company_data.get('biens_services', [])}

        CONTEXTE CHAÎNE DE VALEUR :
        {context}

        Analyse structurée avec :
        1. Activités primaires (entrant, opérations, sortant, marketing, service)
        2. Activités de support (infrastructure, GRH, technologie, achats)
        3. Points de création de valeur
        4. Opportunités d'efficacité et d'optimisation
        5. Avantages concurrentiels potentiels

        Format JSON détaillé.
        """
        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en analyse de chaîne de valeur"), HumanMessage(content=prompt)])
        return json.loads(response.content.strip())

    async def _generate_sustainability_impact_analysis(self, company_data: Dict[str, Any], esg_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate sustainability impact analysis"""
        prompt = f"""
        Analyse de l'impact durable et contribution aux ODD :

        ENTREPRISE :
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}
        - ODD ciblés : {company_data.get('objectifs_dd', [])}
        - Scores ESG : {esg_data.get('esg_scores', {})}

        CONTEXTE DURABILITÉ :
        {context}

        Analyse complète avec :
        1. Contribution aux ODD (mesure et impact)
        2. Impact environnemental (émissions, ressources, biodiversité)
        3. Impact social (emploi, communauté, droits humains)
        4. Impact économique (création de valeur, inclusion)
        5. Score de durabilité global (0-100)
        6. Recommandations d'amélioration d'impact

        Format JSON détaillé.
        """
        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en impact durable et ODD"), HumanMessage(content=prompt)])
        return json.loads(response.content.strip())

    async def _generate_integrated_synthesis(self, company_data: Dict[str, Any], all_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate integrated synthesis of all analyses"""
        prompt = f"""
        SYNTHÈSE INTÉGRALE DE TOUTES LES ANALYSES

        ENTREPRISE :
        - Nom : {company_data.get('company_name', '')}
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}

        RÉSULTATS DES ANALYSES :
        - PESTEL : {all_analyses.get('pestel', {})}
        - Marché & Concurrence : {all_analyses.get('market_competition', {})}
        - Chaîne de valeur : {all_analyses.get('value_chain', {})}
        - ESG : {all_analyses.get('esg', {})}
        - Impact Durable : {all_analyses.get('sustainability_impact', {})}

        Génère une synthèse exécutive intégrant tous ces éléments :

        1. Résumé exécutif (3-4 paragraphes)
        2. Principales conclusions (5-7 points clés)
        3. Recommandations stratégiques prioritaires
        4. Priorités d'implémentation (court/moyen/long terme)
        5. Évaluation des risques
        6. Opportunités de croissance
        7. Plan de transformation durable
        8. Score global consolidé
        9. Niveau de maturité
        10. Prochaines étapes concrètes

        Format JSON structuré et actionnable.
        """
        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en synthèse stratégique intégrale"), HumanMessage(content=prompt)])
        return json.loads(response.content.strip())

    async def _generate_strategic_roadmap(self, company_data: Dict[str, Any], synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic roadmap"""
        prompt = f"""
        ROADMAP STRATÉGIQUE PERSONNALISÉE

        ENTREPRISE :
        - Nom : {company_data.get('company_name', '')}
        - Secteur : {company_data.get('sector', '')}
        - Pays : {company_data.get('country', '')}
        - Score actuel : {synthesis.get('overall_score', 0)}/100

        SYNTHÈSE STRATÉGIQUE :
        {synthesis}

        Crée une roadmap stratégique complète avec :

        1. Titre de la roadmap
        2. 4-5 phases stratégiques (6-24 mois)
        3. Pour chaque phase :
           - Objectifs spécifiques
           - Actions concrètes (5-8 par phase)
           - Jalons mesurables
           - Ressources nécessaires
           - Indicateurs de succès
        4. Investissement total estimé
        5. ROI attendu
        6. Métriques de succès globales

        Format JSON détaillé et opérationnel.
        """
        response = await self.gemini_llm.ainvoke([SystemMessage(content="Expert en planification stratégique"), HumanMessage(content=prompt)])
        return json.loads(response.content.strip())