"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SERVICE OPENAI ASSISTANTS - AFRICA STRATEGY V2                      ║
║              7 Assistants Spécialisés avec Exécution Parallèle               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Architecture :
- 7 Assistants OpenAI spécialisés (un par bloc)
- Exécution parallèle des blocs indépendants (BLOC1, BLOC3, BLOC4)
- Chaînage des blocs dépendants (BLOC2→BLOC5→BLOC6→BLOC7)
- RAG intégré via File Search d'OpenAI

Auteur: Africa Strategy Platform
Version: 2.0
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI
from app.core.config import settings
from app.services.json_cleaner import json_cleaner

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DES 7 ASSISTANTS
# ═══════════════════════════════════════════════════════════════════════════════

ASSISTANT_IDS = {
    "BLOC1": "asst_cyAXL6hJiw3voOPNe5Ldnvmy",  # PESTEL+
    "BLOC2": "asst_wzCrfNe79wRe2YcrDLUrgt3w",  # Risques Climat
    "BLOC3": "asst_rcF84GElGez5Wohbj2DdlDWb",  # Marché & Concurrence
    "BLOC4": "asst_AaPHFcLr5mrYnyDtbmn8sIaw",  # Chaîne de Valeur
    "BLOC5": "asst_gnmjd9Fzwiut4L3KtlhMPs9D",  # Modèles Durables & ODD
    "BLOC6": "asst_IkNhVkjt0OwFld38baCF2Svi",  # Cadre Réglementaire (corrigé)
    "BLOC7": "asst_7H46XK1u6fhmOdeSFz6jm1mU",  # Synthèse Stratégique
}

BLOC_NAMES = {
    "BLOC1": "PESTEL+",
    "BLOC2": "Risques Climat",
    "BLOC3": "Marché & Concurrence",
    "BLOC4": "Chaîne de Valeur",
    "BLOC5": "Modèles Durables & ODD",
    "BLOC6": "Cadre Réglementaire",
    "BLOC7": "Synthèse Stratégique",
}

# Dépendances entre blocs
BLOC_DEPENDENCIES = {
    "BLOC1": [],                           # Indépendant
    "BLOC2": ["BLOC1"],                    # Dépend de BLOC1
    "BLOC3": ["BLOC1"],                    # Dépend de BLOC1
    "BLOC4": ["BLOC1"],                    # Dépend de BLOC1
    "BLOC5": ["BLOC1", "BLOC2"],          # Dépend de BLOC1 et BLOC2
    "BLOC6": ["BLOC1", "BLOC2", "BLOC5"], # Dépend de BLOC1, BLOC2, BLOC5
    "BLOC7": ["BLOC1", "BLOC2", "BLOC3", "BLOC4", "BLOC5", "BLOC6"],  # Tous
}


class OpenAIAssistantService:
    """
    Service pour orchestrer les 7 Assistants OpenAI spécialisés
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.assistant_ids = ASSISTANT_IDS
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key not configured")
            self.client = None
        else:
            import httpx
            # Configuration pour utiliser l'API v2 des Assistants
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=httpx.Timeout(900.0, connect=30.0),
                default_headers={
                    "OpenAI-Beta": "assistants=v2"
                }
            )
            logger.info("✅ OpenAI Assistant Service V2 initialized (API v2)")
            logger.info(f"   Assistants configurés: {list(self.assistant_ids.keys())}")

    # ═══════════════════════════════════════════════════════════════════════════
    # MÉTHODE PRINCIPALE : ANALYSE COMPLÈTE (7 BLOCS)
    # ═══════════════════════════════════════════════════════════════════════════

    async def analyze_company(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute l'analyse complète sur les 7 blocs avec orchestration intelligente.
        
        Stratégie d'exécution :
        - Phase 1 : BLOC1 (seul, requis par tous)
        - Phase 2 : BLOC2, BLOC3, BLOC4 en parallèle
        - Phase 3 : BLOC5 (dépend de BLOC1 + BLOC2)
        - Phase 4 : BLOC6 (dépend de BLOC1 + BLOC2 + BLOC5)
        - Phase 5 : BLOC7 (consolidation finale)
        """
        if not self.client:
            raise Exception("OpenAI client not initialized - check API key")
        
        start_time = datetime.now()
        results = {}
        errors = {}
        
        logger.info("═" * 60)
        logger.info("🚀 DÉMARRAGE ANALYSE COMPLÈTE - 7 BLOCS")
        logger.info("═" * 60)
        
        try:
            # ─────────────────────────────────────────────────────────────────
            # PHASE 1 : BLOC1 (PESTEL+) - Fondation pour tous les autres
            # ─────────────────────────────────────────────────────────────────
            logger.info("\n📊 PHASE 1 : Analyse PESTEL+ (BLOC1)")
            results["BLOC1"] = await self._run_bloc("BLOC1", questionnaire_data, {})
            logger.info(f"   ✅ BLOC1 terminé")
            
            # ─────────────────────────────────────────────────────────────────
            # PHASE 2 : BLOC2, BLOC3, BLOC4 en PARALLÈLE
            # ─────────────────────────────────────────────────────────────────
            logger.info("\n📊 PHASE 2 : Blocs 2, 3, 4 en parallèle")
            
            context_phase2 = {"BLOC1": results["BLOC1"]}
            
            bloc2_task = self._run_bloc("BLOC2", questionnaire_data, context_phase2)
            bloc3_task = self._run_bloc("BLOC3", questionnaire_data, context_phase2)
            bloc4_task = self._run_bloc("BLOC4", questionnaire_data, context_phase2)
            
            phase2_results = await asyncio.gather(
                bloc2_task, bloc3_task, bloc4_task,
                return_exceptions=True
            )
            
            # Traiter les résultats
            for i, bloc_id in enumerate(["BLOC2", "BLOC3", "BLOC4"]):
                if isinstance(phase2_results[i], Exception):
                    logger.error(f"   ❌ {bloc_id} échoué: {str(phase2_results[i])}")
                    errors[bloc_id] = str(phase2_results[i])
                    results[bloc_id] = {"error": str(phase2_results[i])}
                else:
                    results[bloc_id] = phase2_results[i]
                    logger.info(f"   ✅ {bloc_id} terminé")
            
            # ─────────────────────────────────────────────────────────────────
            # PHASE 3 : BLOC5 (ODD) - Dépend de BLOC1 + BLOC2
            # ─────────────────────────────────────────────────────────────────
            logger.info("\n📊 PHASE 3 : Modèles Durables & ODD (BLOC5)")
            context_phase3 = {
                "BLOC1": results["BLOC1"],
                "BLOC2": results["BLOC2"]
            }
            results["BLOC5"] = await self._run_bloc("BLOC5", questionnaire_data, context_phase3)
            logger.info(f"   ✅ BLOC5 terminé")
            
            # ─────────────────────────────────────────────────────────────────
            # PHASE 4 : BLOC6 (Réglementaire) - Dépend de BLOC1 + BLOC2 + BLOC5
            # ─────────────────────────────────────────────────────────────────
            logger.info("\n📊 PHASE 4 : Cadre Réglementaire (BLOC6)")
            context_phase4 = {
                "BLOC1": results["BLOC1"],
                "BLOC2": results["BLOC2"],
                "BLOC5": results["BLOC5"]
            }
            results["BLOC6"] = await self._run_bloc("BLOC6", questionnaire_data, context_phase4)
            logger.info(f"   ✅ BLOC6 terminé")
            
            # ─────────────────────────────────────────────────────────────────
            # PHASE 5 : BLOC7 (Synthèse) - Consolide tout
            # ─────────────────────────────────────────────────────────────────
            logger.info("\n📊 PHASE 5 : Synthèse Stratégique (BLOC7)")
            results["BLOC7"] = await self._run_bloc("BLOC7", questionnaire_data, results)
            logger.info(f"   ✅ BLOC7 terminé")
            
            # ─────────────────────────────────────────────────────────────────
            # CONSOLIDATION FINALE
            # ─────────────────────────────────────────────────────────────────
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("\n" + "═" * 60)
            logger.info(f"✅ ANALYSE COMPLÈTE TERMINÉE EN {int(duration)} SECONDES")
            logger.info("═" * 60)
            
            # Construire la réponse finale
            final_result = {
                "success": True,
                "metadata": {
                    "generated_at": end_time.isoformat(),
                    "duration_seconds": duration,
                    "blocs_executed": list(results.keys()),
                    "blocs_failed": list(errors.keys()) if errors else [],
                    "questionnaire": {
                        "pays": questionnaire_data.get("paysInstallation", ""),
                        "secteur": questionnaire_data.get("secteur", ""),
                        "profil": questionnaire_data.get("profilOrganisation", ""),
                    }
                },
                "blocs": results,
                "errors": errors if errors else None
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse complète: {str(e)}")
            raise

    # ═══════════════════════════════════════════════════════════════════════════
    # EXÉCUTION D'UN BLOC SPÉCIFIQUE
    # ═══════════════════════════════════════════════════════════════════════════

    async def _run_bloc(
        self, 
        bloc_id: str, 
        questionnaire_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Exécute un bloc spécifique via son assistant dédié.
        """
        assistant_id = self.assistant_ids.get(bloc_id)
        if not assistant_id:
            raise ValueError(f"Assistant ID non trouvé pour {bloc_id}")
        
        bloc_name = BLOC_NAMES.get(bloc_id, bloc_id)
        logger.info(f"   🔄 Lancement {bloc_id} ({bloc_name})...")
        
        try:
            # 1. Créer un thread
            thread = self.client.beta.threads.create()
            thread_id = thread.id
            
            # 2. Construire le message utilisateur
            user_message = self._build_user_message(bloc_id, questionnaire_data, context)
            
            # 3. Envoyer le message
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            
            # 4. Lancer le run
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            
            # 5. Attendre la completion
            run = await self._wait_for_completion(thread_id, run.id, bloc_id)
            
            if run.status != "completed":
                error_msg = f"Run {bloc_id} failed: {run.status}"
                if run.last_error:
                    error_msg += f" - {run.last_error.message}"
                raise Exception(error_msg)
            
            # 6. Récupérer la réponse
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="asc"
            )
            
            assistant_message = None
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    assistant_message = msg
                    break
            
            if not assistant_message or not assistant_message.content:
                raise Exception(f"Pas de réponse de l'assistant {bloc_id}")
            
            content = assistant_message.content[0].text.value
            logger.info(f"   📥 Réponse {bloc_id}: {len(content)} caractères")
            
            # 7. Parser le JSON
            result = json_cleaner.extract_and_parse(content)
            
            if not isinstance(result, dict):
                raise Exception(f"Réponse {bloc_id} n'est pas un objet JSON")
            
            # Ajouter les métadonnées du bloc
            result["_metadata"] = {
                "bloc_id": bloc_id,
                "bloc_name": bloc_name,
                "thread_id": thread_id,
                "run_id": run.id,
                "generated_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Erreur {bloc_id}: {str(e)}")
            raise

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTION DU MESSAGE UTILISATEUR
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_user_message(
        self, 
        bloc_id: str, 
        questionnaire_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Construit le message utilisateur pour un bloc spécifique.
        """
        # Extraire les données du questionnaire
        pays = questionnaire_data.get("paysInstallation", "Non spécifié")
        zone = questionnaire_data.get("zoneGeographique", "Non spécifiée")
        secteur = questionnaire_data.get("secteur", "Non spécifié")
        profil = questionnaire_data.get("profilOrganisation", "Non spécifié")
        biens_services = questionnaire_data.get("biensServices", [])
        if isinstance(biens_services, list):
            biens_services = ", ".join(biens_services)
        marche_cible = questionnaire_data.get("marcheCible", "Non spécifié")
        
        # ODD
        odd_auto = questionnaire_data.get("oddAutomatiques", [])
        odd_manuels = questionnaire_data.get("oddManuels", [])
        odd_declares = list(set(odd_auto + odd_manuels))
        
        vision = questionnaire_data.get("visionOrganisation", "Non spécifiée")
        mission = questionnaire_data.get("missionOrganisation", "Non spécifiée")
        projets = questionnaire_data.get("projetsSignificatifs", "Aucun")
        
        # Fichiers uploadés (contexte)
        fichiers_context = questionnaire_data.get("fichiersContext", "Aucun fichier fourni")
        
        # Message de base
        message = f"""## DONNÉES DU CLIENT

### PROFIL ENTREPRISE
- **Pays** : {pays}
- **Zone géographique** : {zone}
- **Secteur ISIC** : {secteur}
- **Offre (Biens/Services)** : {biens_services}
- **Marché cible** : {marche_cible}
- **Profil utilisateur** : {profil}

### STRATÉGIE DÉCLARÉE
- **Vision** : {vision}
- **Mission** : {mission}
- **Projets significatifs** : {projets}

### ODD SÉLECTIONNÉS
- **ODD déclarés** : {', '.join([f"ODD{o}" for o in odd_declares]) if odd_declares else 'Aucun'}

### FICHIERS COMPLÉMENTAIRES
{fichiers_context}
"""
        
        # Ajouter le contexte des blocs précédents si disponible
        if context:
            message += "\n\n### CONTEXTE DES BLOCS PRÉCÉDENTS\n"
            for prev_bloc_id, prev_result in context.items():
                if prev_result and isinstance(prev_result, dict):
                    # Résumer les indices principaux
                    indices = prev_result.get("indices", {})
                    if indices:
                        message += f"\n**{prev_bloc_id}** - Indices clés:\n"
                        for key, value in indices.items():
                            if isinstance(value, dict) and "score" in value:
                                message += f"  - {key}: {value.get('score', 'N/A')}/100\n"
                            elif isinstance(value, (int, float)):
                                message += f"  - {key}: {value}/100\n"
        
        # Instructions finales
        message += """

---

## INSTRUCTIONS D'EXÉCUTION

1. Utilise les fichiers d'indicateurs attachés à ton assistant
2. Applique rigoureusement le cadre méthodologique
3. Calcule tous les indicateurs avec leurs scores normalisés
4. Produis les analyses qualitatives détaillées
5. Génère la synthèse stratégique
6. **RETOURNE UNIQUEMENT UN JSON VALIDE** selon le format défini dans tes instructions

⚠️ **FORMAT JSON STRICT** :
- Aucun commentaire (// ou /* */)
- Aucun texte avant ou après le JSON
- Toutes les chaînes correctement échappées
- Nombres sans guillemets
"""
        
        return message

    # ═══════════════════════════════════════════════════════════════════════════
    # POLLING ET ATTENTE
    # ═══════════════════════════════════════════════════════════════════════════

    async def _wait_for_completion(
        self, 
        thread_id: str, 
        run_id: str, 
        bloc_id: str,
        max_wait: int = 300
    ) -> Any:
        """
        Attend la completion d'un run avec polling.
        """
        import time
        start_time = time.time()
        poll_count = 0
        
        while True:
            poll_count += 1
            
            try:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
            except Exception as e:
                if "timeout" in str(e).lower():
                    logger.warning(f"   ⏳ Timeout HTTP {bloc_id}, retry...")
                    await asyncio.sleep(5)
                    continue
                raise
            
            elapsed = time.time() - start_time
            
            # Log toutes les 30 secondes
            if poll_count % 15 == 0:
                logger.info(f"   ⏳ {bloc_id}: {run.status} ({int(elapsed)}s)")
            
            if run.status == "completed":
                return run
            
            elif run.status == "failed":
                raise Exception(f"{bloc_id} failed: {run.last_error.message if run.last_error else 'Unknown'}")
            
            elif run.status in ["cancelled", "expired"]:
                raise Exception(f"{bloc_id} {run.status}")
            
            elif run.status == "requires_action":
                # Gérer les tool outputs pour file_search
                if run.required_action and run.required_action.type == "submit_tool_outputs":
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"status": "completed"})
                        })
                    
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run_id,
                        tool_outputs=tool_outputs
                    )
            
            if elapsed > max_wait:
                raise Exception(f"{bloc_id} timeout after {max_wait}s")
            
            await asyncio.sleep(2)

    # ═══════════════════════════════════════════════════════════════════════════
    # MÉTHODE POUR UN BLOC UNIQUE (API PUBLIQUE)
    # ═══════════════════════════════════════════════════════════════════════════

    async def analyze_bloc(
        self, 
        bloc_id: str, 
        questionnaire_data: Dict[str, Any],
        previous_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Exécute un seul bloc spécifique.
        Utilisable pour des analyses incrémentales.
        """
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        bloc_id = bloc_id.upper()
        if bloc_id not in self.assistant_ids:
            raise ValueError(f"Bloc inconnu: {bloc_id}. Blocs valides: {list(self.assistant_ids.keys())}")
        
        context = previous_results or {}
        result = await self._run_bloc(bloc_id, questionnaire_data, context)
        
        return {
            "success": True,
            "bloc_id": bloc_id,
            "bloc_name": BLOC_NAMES.get(bloc_id),
            "result": result
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # HEALTH CHECK
    # ═══════════════════════════════════════════════════════════════════════════

    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie que tous les assistants sont accessibles.
        """
        if not self.client:
            return {"status": "error", "message": "OpenAI client not initialized"}
        
        results = {}
        all_healthy = True
        
        for bloc_id, assistant_id in self.assistant_ids.items():
            try:
                assistant = self.client.beta.assistants.retrieve(assistant_id)
                results[bloc_id] = {
                    "status": "healthy",
                    "name": assistant.name,
                    "model": assistant.model,
                    "tools": [t.type for t in assistant.tools] if assistant.tools else []
                }
            except Exception as e:
                all_healthy = False
                results[bloc_id] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "assistants": results
        }


# ═══════════════════════════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════════════════════════

openai_assistant_service = OpenAIAssistantService()
