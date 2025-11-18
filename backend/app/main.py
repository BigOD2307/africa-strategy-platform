"""
Application principale FastAPI pour Africa Strategy (VERSION SIMPLIFIÉE)
Un seul endpoint : /api/analyze qui appelle directement OpenAI Assistant
"""

# Importer la version simplifiée
from app.main_simple import app

# L'application est déjà configurée dans main_simple.py
__all__ = ["app"]
