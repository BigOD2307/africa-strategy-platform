"""
Script de test rapide pour vérifier que le backend fonctionne
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.openai_assistant_service import openai_assistant_service

def test_config():
    print("=== TEST CONFIGURATION ===")
    print(f"OPENAI_API_KEY: {'✅ Configurée' if settings.OPENAI_API_KEY else '❌ Manquante'}")
    print(f"OPENAI_ASSISTANT_ID: {'✅ Configurée' if settings.OPENAI_ASSISTANT_ID else '❌ Manquante'}")
    print(f"CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    
    if not settings.OPENAI_API_KEY:
        print("\n❌ ERREUR: OPENAI_API_KEY n'est pas configurée!")
        print("Créez un fichier .env dans backend/ avec:")
        print("OPENAI_API_KEY=votre_cle")
        print("OPENAI_ASSISTANT_ID=votre_assistant_id")
        return False
    
    if not settings.OPENAI_ASSISTANT_ID:
        print("\n❌ ERREUR: OPENAI_ASSISTANT_ID n'est pas configurée!")
        return False
    
    print("\n✅ Configuration OK")
    return True

def test_openai_service():
    print("\n=== TEST SERVICE OPENAI ===")
    
    if not openai_assistant_service.client:
        print("❌ ERREUR: Client OpenAI non initialisé")
        return False
    
    print("✅ Client OpenAI initialisé")
    
    try:
        # Test de health check (c'est une méthode async)
        import asyncio
        health_result = asyncio.run(openai_assistant_service.health_check())
        if isinstance(health_result, dict):
            print(f"✅ Health check: {health_result.get('status', 'unknown')}")
            if health_result.get('status') == 'healthy':
                print(f"   Assistant: {health_result.get('assistant_name', 'N/A')}")
                print(f"   Model: {health_result.get('model', 'N/A')}")
            else:
                print(f"   ⚠️ Message: {health_result.get('message', 'N/A')}")
        else:
            print(f"⚠️ Health check: {health_result}")
    except Exception as e:
        print(f"❌ Erreur health check: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("\n" + "="*50)
    print("TEST DU BACKEND AFRICA STRATEGY")
    print("="*50 + "\n")
    
    config_ok = test_config()
    if not config_ok:
        sys.exit(1)
    
    service_ok = test_openai_service()
    if not service_ok:
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("="*50)
    print("\nLe backend est prêt. Démarrez-le avec:")
    print("  python -m uvicorn app.main_simple:app --reload --port 8000")

