"""

Module dédié au nettoyage robuste de JSON invalide
Gère tous les cas problématiques de l'assistant OpenAI
"""
import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class JSONCleaner:
    """
    Nettoie et répare les JSON invalides générés par l'IA
    """
    
    @staticmethod
    def clean(json_str: str) -> str:
        """
        Nettoie un JSON potentiellement invalide
        
        Args:
            json_str: Chaîne JSON à nettoyer
            
        Returns:
            JSON nettoyé et valide
        """
        logger.info("🧹 Début du nettoyage JSON approfondi...")
        original_length = len(json_str)
        
        # 1. Supprimer les commentaires tout en préservant le contenu des chaînes
        json_str = JSONCleaner._remove_comments_preserving_strings(json_str)
        logger.info("   Commentaires supprimés")
        
        # 2. Nettoyer les virgules problématiques
        # Virgules avant accolades fermantes
        json_str = re.sub(r',\s*}', '}', json_str)
        # Virgules avant crochets fermants
        json_str = re.sub(r',\s*]', ']', json_str)
        # Virgules doubles
        json_str = re.sub(r',\s*,+', ',', json_str)
        
        logger.info(f"   Virgules nettoyées")
        
        # 3. Nettoyer les espaces et sauts de ligne
        # Lignes vides multiples
        json_str = re.sub(r'\n\s*\n+', '\n', json_str)
        # Espaces multiples (mais pas dans les strings)
        # On fait attention à ne pas toucher aux strings
        
        logger.info(f"   Espaces nettoyés")
        
        # 4. Réparer les structures incomplètes
        # Compter les accolades et crochets
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        if open_braces > close_braces:
            missing = open_braces - close_braces
            logger.warning(f"   ⚠️ {missing} accolades fermantes manquantes - ajout automatique")
            json_str += '}' * missing
        
        if open_brackets > close_brackets:
            missing = open_brackets - close_brackets
            logger.warning(f"   ⚠️ {missing} crochets fermants manquants - ajout automatique")
            json_str += ']' * missing
        
        # 5. Nettoyer les trailing commas qui pourraient rester
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 6. Nettoyer les espaces en début/fin
        json_str = json_str.strip()
        
        cleaned_length = len(json_str)
        reduction = original_length - cleaned_length
        logger.info(f"✅ Nettoyage terminé: {original_length} → {cleaned_length} caractères (-{reduction})")
        
        return json_str
    
    @staticmethod
    def extract_and_parse(content: str) -> Dict[str, Any]:
        """
        Extrait le JSON du contenu et le parse
        
        Args:
            content: Contenu brut (peut contenir du texte avant/après le JSON)
            
        Returns:
            JSON parsé en dictionnaire
            
        Raises:
            Exception: Si le parsing échoue
        """
        try:
            logger.info(f"📦 Extraction du JSON depuis {len(content)} caractères...")
            
            # Essayer de trouver le JSON dans différents formats
            json_str = None
            
            # Pattern 1: ```json ... ```
            match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                logger.info("   JSON trouvé dans bloc ```json```")
            else:
                # Pattern 2: ``` ... ```
                match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if match:
                    json_str = match.group(1).strip()
                    logger.info("   JSON trouvé dans bloc ```")
                else:
                    # Pattern 3: Premier { jusqu'au dernier }
                    start = content.find('{')
                    end = content.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        json_str = content[start:end+1]
                        logger.info(f"   JSON trouvé directement (pos {start} à {end})")
                    else:
                        raise Exception("Aucun JSON trouvé dans le contenu")
            
            # Nettoyer le JSON
            json_str = JSONCleaner.clean(json_str)
            
            # Tenter de parser
            try:
                result = json.loads(json_str)
                logger.info("✅ JSON parsé avec succès du premier coup")
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Échec parsing initial: {e}")
                
                # Sauvegarder pour debug
                try:
                    with open("failed_json_debug.txt", "w", encoding="utf-8") as f:
                        f.write(json_str)
                    logger.info("💾 JSON problématique sauvegardé dans failed_json_debug.txt")
                except:
                    pass
                
                # Afficher le contexte de l'erreur
                if hasattr(e, 'pos') and e.pos:
                    start = max(0, e.pos - 150)
                    end = min(len(json_str), e.pos + 150)
                    context = json_str[start:end]
                    logger.error(f"❌ Contexte de l'erreur (pos {e.pos}):")
                    logger.error(f"   {context}")
                
                # Dernière tentative: nettoyage plus agressif
                logger.info("🔧 Tentative de nettoyage agressif...")
                
                # Supprimer TOUT ce qui ressemble à un commentaire
                json_str_aggressive = re.sub(r'//.*', '', json_str)
                json_str_aggressive = re.sub(r'/\*.*?\*/', '', json_str_aggressive, flags=re.DOTALL)
                
                # Supprimer les lignes qui ne contiennent que des espaces
                lines = json_str_aggressive.split('\n')
                lines = [line for line in lines if line.strip()]
                json_str_aggressive = '\n'.join(lines)
                
                # Re-nettoyer les virgules
                json_str_aggressive = re.sub(r',\s*([}\]])', r'\1', json_str_aggressive)
                json_str_aggressive = re.sub(r',\s*,+', ',', json_str_aggressive)
                
                try:
                    result = json.loads(json_str_aggressive)
                    logger.info("✅ JSON parsé après nettoyage agressif")
                    return result
                except json.JSONDecodeError as e2:
                    logger.error(f"❌ Échec même après nettoyage agressif: {e2}")
                    
                    # Sauvegarder la version agressive aussi
                    try:
                        with open("failed_json_aggressive_debug.txt", "w", encoding="utf-8") as f:
                            f.write(json_str_aggressive)
                        logger.info("💾 Version agressive sauvegardée dans failed_json_aggressive_debug.txt")
                    except:
                        pass
                    
                    raise Exception(f"Impossible de parser le JSON: {str(e2)}")
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction/parsing: {str(e)}")
            raise

    @staticmethod
    def _remove_comments_preserving_strings(content: str) -> str:
        """
        Supprime les commentaires // et /* */ sans toucher aux chaînes de caractères
        (pour éviter de casser les URLs de type https://, etc.)
        """
        result = []
        i = 0
        length = len(content)
        in_string = False
        string_delim = ''

        while i < length:
            char = content[i]

            if in_string:
                result.append(char)
                if char == '\\':
                    # Conserver le caractère d'échappement et le suivant
                    if i + 1 < length:
                        result.append(content[i + 1])
                        i += 1
                elif char == string_delim:
                    in_string = False
                i += 1
                continue

            # Début de chaîne
            if char in ('"', "'"):
                in_string = True
                string_delim = char
                result.append(char)
                i += 1
                continue

            # Commentaire sur une ligne
            if char == '/' and i + 1 < length and content[i + 1] == '/':
                i += 2
                while i < length and content[i] not in ('\n', '\r'):
                    i += 1
                continue

            # Commentaire multi-ligne
            if char == '/' and i + 1 < length and content[i + 1] == '*':
                i += 2
                while i + 1 < length and not (content[i] == '*' and content[i + 1] == '/'):
                    i += 1
                i += 2
                continue

            result.append(char)
            i += 1

        return ''.join(result)


# Instance globale
json_cleaner = JSONCleaner()


