"""
Service OpenAI Assistants pour Africa Strategy
Utilise l'API OpenAI Assistants pour générer les analyses stratégiques complètes
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from openai import OpenAI
from app.core.config import settings
from app.services.json_cleaner import json_cleaner

logger = logging.getLogger(__name__)


class OpenAIAssistantService:
    """
    Service pour interagir avec l'Assistant OpenAI
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.assistant_id = settings.OPENAI_ASSISTANT_ID
        
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            # Créer le client avec un timeout HTTP très long (15 minutes)
            # pour les analyses longues qui peuvent prendre du temps
            import httpx
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=httpx.Timeout(900.0, connect=30.0)  # 15 minutes total, 30s pour connexion
            )
            logger.info(f"OpenAI Assistant Service initialized with assistant ID: {self.assistant_id}")

    async def analyze_company(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse complète d'une entreprise via l'Assistant OpenAI
        
        Args:
            questionnaire_data: Données du questionnaire rempli par l'utilisateur
            
        Returns:
            Analyse complète au format JSON structuré
        """
        if not self.client:
            raise Exception("OpenAI client not initialized - check API key")
        
        try:
            logger.info("Starting OpenAI Assistant analysis...")
            
            # 1. Créer un thread de conversation
            thread = self.client.beta.threads.create()
            thread_id = thread.id
            logger.info(f"Created thread: {thread_id}")
            
            # 2. Préparer le message avec les données du questionnaire
            message_content = self._prepare_questionnaire_message(questionnaire_data)
            
            # **IMPORTANT** : Ajouter des instructions strictes sur le format JSON
            final_message = f"""{message_content}

⚠️ INSTRUCTIONS CRITIQUES POUR LE FORMAT DE SORTIE :
1. Génère un JSON STRICTEMENT VALIDE sans AUCUN commentaire (//, /* */)
2. NE PAS utiliser de raccourcis comme "// ... (ajout de X autres éléments...)"
3. Si tu ne peux pas générer tous les éléments, génère uniquement ceux que tu peux compléter entièrement
4. CHAQUE élément du JSON doit être complet et valide
5. Le JSON doit être parsable directement sans aucun nettoyage

RÉPONDS UNIQUEMENT AVEC UN JSON VALIDE, RIEN D'AUTRE."""
            
            # 3. Ajouter le message au thread
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=final_message
            )
            logger.info("Message added to thread (avec instructions de format JSON)")
            
            # 4. Lancer l'assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            logger.info(f"Run started: {run.id}")
            
            # 5. Attendre la completion (avec polling)
            # Timeout augmenté à 10 minutes pour les analyses longues
            logger.info("⏳ Attente de la réponse de l'assistant (peut prendre 2-10 minutes)...")
            run = await self._wait_for_completion(thread_id, run.id, max_wait=600)
            
            if run.status != "completed":
                error_msg = f"Run failed with status: {run.status}"
                if run.last_error:
                    error_msg += f" - {run.last_error.message}"
                raise Exception(error_msg)
            
            # 6. Récupérer la réponse
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="asc"
            )
            
            # Trouver le dernier message de l'assistant
            assistant_message = None
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    assistant_message = msg
                    break
            
            if not assistant_message:
                raise Exception("No response from assistant")
            
            # 7. Extraire le contenu JSON
            if not assistant_message.content or len(assistant_message.content) == 0:
                raise Exception("Assistant message has no content")
            
            content = assistant_message.content[0].text.value
            logger.info(f"✅ Réponse reçue de l'assistant ({len(content)} caractères)")
            
            # Logger un aperçu du contenu pour debug
            preview = content[:200] if len(content) > 200 else content
            logger.info(f"   Aperçu: {preview}...")
            
            # 8. Parser le JSON avec le nouveau cleaner robuste
            logger.info("🔍 Parsing de la réponse avec JSONCleaner...")
            analysis_result = json_cleaner.extract_and_parse(content)

            if not isinstance(analysis_result, dict):
                raise Exception("Assistant response is not a JSON object")

            # Garantir l'existence des blocs clés
            if "analyses" not in analysis_result or not isinstance(analysis_result.get("analyses"), dict):
                logger.warning("⚠️ Clé 'analyses' absente ou invalide, initialisation d'un dictionnaire vide.")
                analysis_result["analyses"] = {}
            if "pipeline_analytique" not in analysis_result or not isinstance(analysis_result.get("pipeline_analytique"), dict):
                logger.warning("⚠️ Clé 'pipeline_analytique' absente ou invalide, initialisation d'un dictionnaire vide.")
                analysis_result["pipeline_analytique"] = {}
            if "metadata" not in analysis_result or not isinstance(analysis_result.get("metadata"), dict):
                logger.warning("⚠️ Clé 'metadata' absente ou invalide, initialisation d'un dictionnaire vide.")
                analysis_result["metadata"] = {}
            
            # 9. Ajouter les métadonnées
            analysis_result["metadata"]["run_id"] = run.id
            analysis_result["metadata"]["thread_id"] = thread_id
            analysis_result["metadata"]["generated_at"] = datetime.now().isoformat()
            
            logger.info("Analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"OpenAI Assistant analysis failed: {str(e)}")
            raise

    def _prepare_questionnaire_message(self, data: Dict[str, Any]) -> str:
        """
        Prépare le message pour l'assistant avec les données du questionnaire
        """
        message = f"""Analyse cette entreprise africaine en appliquant le pipeline analytique complet.

DONNÉES DE L'ENTREPRISE:
- Secteur d'activité: {data.get('secteur', 'Non spécifié')}
- Zone géographique: {data.get('zoneGeographique', 'Non spécifiée')}
- Pays d'installation: {data.get('paysInstallation', 'Non spécifié')}
- Profil organisation: {data.get('profilOrganisation', 'Non spécifié')}
- Biens/Services: {', '.join(data.get('biensServices', []))}
- Autres biens/services: {data.get('autresBiensServices', 'Aucun')}
- Objectifs DD: {', '.join(data.get('objectifsDD', []))}
- Positionnement stratégique: {data.get('positionnementStrategique', 'Non spécifié')}
- Vision: {data.get('visionOrganisation', 'Non spécifiée')}
- Mission: {data.get('missionOrganisation', 'Non spécifiée')}
- Projets significatifs: {data.get('projetsSignificatifs', 'Aucun')}

INSTRUCTIONS:
1. Collecte massivement des données depuis tes connaissances, la base RAG, et Internet
2. Applique rigoureusement le pipeline analytique avec toutes les formules
3. Génère les 6 analyses détaillées (PESTEL, ESG, Marché, Chaîne de valeur, Impact durable, Synthèse)
4. Retourne UNIQUEMENT un JSON valide et bien structuré selon le format demandé
5. Assure-toi que l'analyse fait au moins 20 000 caractères de contenu valuable

Retourne maintenant l'analyse complète au format JSON."""
        
        return message

    async def _wait_for_completion(self, thread_id: str, run_id: str, max_wait: int = 600) -> Any:
        """
        Attend la completion du run avec polling
        max_wait: 600 secondes (10 minutes) par défaut pour les analyses longues
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
                # Si une requête HTTP timeout, on continue à essayer
                logger.warning(f"Erreur lors de la récupération du run (tentative {poll_count}): {str(e)}")
                if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    logger.info("   Timeout HTTP, on continue à attendre...")
                    await asyncio.sleep(5)  # Attendre un peu plus avant de réessayer
                    continue
                else:
                    # Autre erreur, on la propage
                    raise
            
            # Calculer le temps écoulé
            elapsed = time.time() - start_time
            
            # Logger le statut toutes les 10 secondes
            if poll_count % 5 == 0 or run.status != "in_progress":
                logger.info(f"Run status: {run.status} | Temps écoulé: {int(elapsed)}s / {max_wait}s")
            
            if run.status == "completed":
                logger.info(f"✅ Run complété en {int(elapsed)} secondes")
                return run
            elif run.status == "failed":
                error_msg = f"Run failed: {run.last_error.message if run.last_error else 'Unknown error'}"
                logger.error(error_msg)
                raise Exception(error_msg)
            elif run.status in ["cancelled", "expired"]:
                error_msg = f"Run {run.status}"
                logger.error(error_msg)
                raise Exception(error_msg)
            elif run.status == "requires_action":
                # L'assistant attend une action (utilisation d'outils comme file_search, code_interpreter, etc.)
                logger.info(f"⚠️ Run requires_action - L'assistant utilise des outils")
                
                if run.required_action and run.required_action.type == "submit_tool_outputs":
                    # L'assistant a utilisé des outils et attend les résultats
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    logger.info(f"   Nombre d'outils utilisés: {len(tool_calls)}")
                    
                    # Pour chaque tool_call, déterminer le type d'outil et soumettre un output approprié
                    tool_outputs = []
                    for tool_call in tool_calls:
                        tool_type = tool_call.function.name if hasattr(tool_call, 'function') else 'unknown'
                        logger.info(f"   Outil: {tool_type} (ID: {tool_call.id})")
                        
                        # Pour les outils gérés automatiquement par OpenAI (file_search, etc.)
                        # On peut soumettre un output vide ou un message de confirmation
                        # Les outils comme file_search sont exécutés automatiquement par OpenAI
                        if tool_type in ['file_search', 'code_interpreter']:
                            # Ces outils sont gérés automatiquement, on soumet juste une confirmation
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"status": "completed", "message": "Tool executed successfully"})
                            })
                        else:
                            # Pour les autres outils, on soumet un output par défaut
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"status": "completed"})
                            })
                    
                    # Soumettre les outputs pour continuer le run
                    logger.info(f"   Soumission de {len(tool_outputs)} outputs...")
                    try:
                        updated_run = self.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_outputs=tool_outputs
                        )
                        logger.info(f"   ✅ Outputs soumis avec succès. Nouveau statut: {updated_run.status}")
                        # Mettre à jour le run pour la prochaine itération
                        run = updated_run
                    except Exception as e:
                        logger.error(f"   ❌ Erreur lors de la soumission des outputs: {str(e)}")
                        # Continuer quand même, peut-être que l'outil se gère automatiquement
                else:
                    # Autre type d'action requise
                    logger.warning(f"   Type d'action inconnu: {run.required_action.type if run.required_action else 'None'}")
                    # On continue quand même à attendre
            elif run.status == "queued":
                logger.info(f"⏳ Run en file d'attente...")
            elif run.status == "in_progress":
                # Statut normal, on continue
                pass
            else:
                logger.warning(f"⚠️ Statut inconnu: {run.status}")
            
            # Vérifier le timeout
            if elapsed > max_wait:
                error_msg = f"Run timeout after {max_wait} seconds (status: {run.status})"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Limite de sécurité : si on a fait trop de polls, logger un avertissement
            if poll_count > 300:  # 10 minutes à 2 secondes par poll
                logger.warning(f"⚠️ Nombre de polls élevé: {poll_count} (statut: {run.status}, temps: {int(elapsed)}s)")
            
            # Attendre avant de re-poll
            # Si requires_action vient d'être traité, attendre un peu plus
            wait_time = 3 if run.status == "requires_action" else 2
            await asyncio.sleep(wait_time)

    def _parse_assistant_response(self, content: str) -> Dict[str, Any]:
        """
        Parse la réponse de l'assistant pour extraire le JSON
        Gère les grandes réponses (20K+ caractères) de manière robuste
        """
        try:
            import re
            
            logger.info(f"Parsing response ({len(content)} caractères)...")
            
            # Nettoyer le contenu : enlever les espaces en début/fin
            content = content.strip()
            
            # Pattern 1: ```json ... ``` (le plus courant)
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info("JSON trouvé dans bloc ```json```")
                
                # **NOUVEAU** : Supprimer les commentaires JavaScript (// ...)
                logger.info("Nettoyage des commentaires JavaScript...")
                # Supprimer les commentaires // jusqu'à la fin de ligne
                json_str = re.sub(r'//[^\n]*', '', json_str)
                # Supprimer les commentaires /* ... */
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            else:
                # Pattern 2: ``` ... ``` (sans json)
                json_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                    logger.info("JSON trouvé dans bloc ```")
                    
                    # **NOUVEAU** : Supprimer les commentaires JavaScript
                    json_str = re.sub(r'//[^\n]*', '', json_str)
                    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                else:
                    # Pattern 3: Chercher le premier { jusqu'au dernier }
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = content[start:end]
                        logger.info(f"JSON trouvé directement (position {start} à {end})")
                    else:
                        raise Exception("No JSON found in assistant response")
            
            # **NOUVEAU** : Nettoyer les commentaires JS partout (au cas où)
            logger.info("🧹 Nettoyage des commentaires JavaScript...")
            json_str = re.sub(r'//[^\n]*', '', json_str)
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            
            # Nettoyer les lignes vides multiples
            json_str = re.sub(r'\n\s*\n', '\n', json_str)
            
            # Nettoyer le JSON : enlever les espaces
            json_str = json_str.strip()
            
            logger.info(f"📏 JSON après nettoyage : {len(json_str)} caractères")
            
            # Parser le JSON avec gestion d'erreur détaillée
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError as json_err:
                # Si erreur de parsing, essayer de corriger les problèmes courants
                logger.warning(f"Erreur JSON initiale: {str(json_err)}")
                
                # Essayer de corriger les virgules en fin de ligne
                json_str_fixed = re.sub(r',\s*}', '}', json_str)
                json_str_fixed = re.sub(r',\s*]', ']', json_str_fixed)
                
                # **NOUVEAU** : Corrections supplémentaires
                # Supprimer les virgules en double
                json_str_fixed = re.sub(r',\s*,', ',', json_str_fixed)
                
                # Supprimer les virgules avant les accolades (cas non couvert)
                json_str_fixed = re.sub(r',(\s*\})', r'\1', json_str_fixed)
                json_str_fixed = re.sub(r',(\s*\])', r'\1', json_str_fixed)
                
                # Nettoyer les espaces multiples
                json_str_fixed = re.sub(r'\s+', ' ', json_str_fixed)
                
                try:
                    result = json.loads(json_str_fixed)
                    logger.info("✅ JSON corrigé et parsé avec succès")
                except:
                    # Si ça ne marche toujours pas, logger plus de détails
                    error_pos = getattr(json_err, 'pos', None)
                    if error_pos:
                        start_context = max(0, error_pos - 100)
                        end_context = min(len(json_str), error_pos + 100)
                        logger.error(f"Contexte de l'erreur (position {error_pos}):")
                        logger.error(f"{json_str[start_context:end_context]}")
                    
                    # **NOUVEAU** : Enregistrer le JSON problématique pour debug
                    try:
                        with open("failed_json_debug.txt", "w", encoding="utf-8") as f:
                            f.write(json_str_fixed)
                        logger.error("💾 JSON problématique sauvegardé dans failed_json_debug.txt")
                    except:
                        pass
                    
                    raise json_err
            
            # Valider la structure de base
            if not isinstance(result, dict):
                raise Exception("Response is not a JSON object")
            
            # S'assurer que les clés principales existent avec des valeurs par défaut
            if "analyses" not in result:
                result["analyses"] = {}
            if "pipeline_analytique" not in result:
                result["pipeline_analytique"] = {}
            if "metadata" not in result:
                result["metadata"] = {}
            
            logger.info(f"✅ JSON parsé avec succès. Clés principales: {list(result.keys())}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de parsing JSON: {str(e)}")
            error_pos = getattr(e, 'pos', None)
            if error_pos:
                preview_start = max(0, error_pos - 200)
                preview_end = min(len(content), error_pos + 200)
                logger.error(f"Contexte de l'erreur (position {error_pos}):")
                logger.error(f"{content[preview_start:preview_end]}")
            else:
                logger.error(f"Aperçu du contenu: {content[:1000]}")
            raise Exception(f"Failed to parse JSON from assistant response: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erreur lors du parsing: {str(e)}")
            logger.error(f"Type d'erreur: {type(e).__name__}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie que le service est opérationnel
        """
        if not self.client:
            return {
                "status": "error",
                "message": "OpenAI client not initialized"
            }
        
        try:
            # Vérifier que l'assistant existe
            assistant = self.client.beta.assistants.retrieve(self.assistant_id)
            
            return {
                "status": "healthy",
                "assistant_id": self.assistant_id,
                "assistant_name": assistant.name,
                "model": assistant.model,
                "tools": [tool.type for tool in assistant.tools] if assistant.tools else []
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Instance globale du service
openai_assistant_service = OpenAIAssistantService()

