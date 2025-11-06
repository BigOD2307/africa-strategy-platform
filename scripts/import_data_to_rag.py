#!/usr/bin/env python3
"""
Script simple pour importer tes données CSV dans Pinecone RAG
Africa Strategy - Import de données pour le système IA
"""

import os
import csv
import sys
from pathlib import Path

# Ajouter le répertoire backend au path pour importer nos modules
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from pinecone import Pinecone

def main():
    """Import des données CSV dans Pinecone"""

    print("🚀 IMPORT DE DONNÉES DANS PINECONE RAG")
    print("=" * 50)

    # Configuration Pinecone
    PINECONE_API_KEY = "pcsk_6G2UeY_ScBjoYZbxAMTH1zTviegZV1uZPsRnemffMYKFMXAR35DYNYMHE7t74GRdJHehZD"
    PINECONE_INDEX_NAME = "africa-strategy-rag"

    print("🔑 Connexion à Pinecone...")

    try:
        # Connexion à Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        print("✅ Connecté à Pinecone")
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return

    # Liste des fichiers CSV à importer
    csv_files = [
        'regulatory_documents.csv',
        'sector_reports.csv',
        'esg_frameworks.csv',
        'market_intelligence.csv',
        'best_practices.csv',
        'case_studies.csv',
        'policy_documents.csv'
    ]

    total_imported = 0

    for csv_file in csv_files:
        print(f"\n📁 Import de {csv_file}...")

        if not os.path.exists(csv_file):
            print(f"⚠️  Fichier {csv_file} non trouvé - ignoré")
            continue

        try:
            imported = import_csv_file(csv_file, index)
            total_imported += imported
            print(f"✅ {imported} documents importés depuis {csv_file}")
        except Exception as e:
            print(f"❌ Erreur avec {csv_file}: {str(e)}")

    print(f"\n🎉 IMPORT TERMINÉ: {total_imported} documents au total")

    # Test de recherche
    print("\n🧪 Test de recherche...")
    test_search(index)

def import_csv_file(csv_file_path, index):
    """Import un fichier CSV dans Pinecone"""

    vectors = []
    imported_count = 0

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, 1):
            # Créer l'ID unique
            vector_id = f"{csv_file_path.replace('.csv', '')}_{row_num}"

            # Récupérer le contenu (colonne 'content' ou 'title')
            content = row.get('content', '').strip()
            if not content:
                content = row.get('title', '').strip()

            if not content:
                continue  # Skip si pas de contenu

            # Métadonnées pour le filtrage
            metadata = {
                'title': row.get('title', ''),
                'content': content,
                'country': row.get('country', ''),
                'sector': row.get('sector', ''),
                'source': csv_file_path.replace('.csv', ''),
                'category': get_category(csv_file_path),
                'row_id': str(row_num)
            }

            # Ajouter d'autres colonnes comme métadonnées
            for key, value in row.items():
                if key not in ['content', 'title'] and value.strip():
                    metadata[key] = value

            # Créer le vector (Pinecone gère les embeddings automatiquement)
            vector = {
                'id': vector_id,
                'values': [],  # Vide = génération automatique
                'metadata': metadata
            }

            vectors.append(vector)

    # Upload par batches
    batch_size = 50  # Plus petit pour éviter les timeouts
    total_uploaded = 0

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]

        try:
            index.upsert(vectors=batch)
            total_uploaded += len(batch)
            print(f"  📦 Batch {i//batch_size + 1}: {len(batch)} documents")
        except Exception as e:
            print(f"  ❌ Erreur batch {i//batch_size + 1}: {str(e)}")

    return total_uploaded

def get_category(filename):
    """Détermine la catégorie selon le nom du fichier"""
    filename = filename.lower()

    if 'regulatory' in filename:
        return 'regulatory'
    elif 'sector' in filename or 'report' in filename:
        return 'sector_reports'
    elif 'esg' in filename or 'framework' in filename:
        return 'esg_frameworks'
    elif 'market' in filename:
        return 'market_data'
    elif 'best_practice' in filename:
        return 'best_practices'
    elif 'case_study' in filename:
        return 'case_studies'
    elif 'policy' in filename:
        return 'policy'
    else:
        return 'general'

def test_search(index):
    """Test que la recherche fonctionne"""

    try:
        # Test de recherche simple
        results = index.query(
            vector=[0.0] * 384,  # Vector nul pour test
            top_k=3,
            include_metadata=True
        )

        if results['matches']:
            print("✅ Recherche fonctionnelle!")
            for i, match in enumerate(results['matches'], 1):
                metadata = match['metadata']
                print(f"  {i}. {metadata.get('title', 'Sans titre')} ({metadata.get('country', 'N/A')})")
        else:
            print("⚠️  Aucune donnée trouvée - vérifie l'import")

    except Exception as e:
        print(f"❌ Erreur de test: {str(e)}")

if __name__ == "__main__":
    main()