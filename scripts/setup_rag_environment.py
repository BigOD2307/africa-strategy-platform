#!/usr/bin/env python3
"""
Setup script for RAG environment
Configure Pinecone and test RAG system
"""

import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_environment_variables():
    """Check if all required environment variables are set"""
    required_vars = [
        'OPENROUTER_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT',
        'PINECONE_INDEX_NAME',
        'DATABASE_URL'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n📝 Please set these in your .env file or environment")
        return False

    print("✅ All environment variables are set")
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print("ℹ️  .env file already exists")
        return

    env_template = """# OpenRouter Configuration
OPENROUTER_API_KEY=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

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=africa-strategy-rag

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/africa_strategy

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Configuration
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads/

# AI Configuration
GEMINI_MODEL=google/gemini-2.0-flash-exp:free
PERPLEXITY_MODEL=perplexity/llama-3.1-sonar-large-128k-online

# Cache Configuration
CACHE_TTL=3600  # 1 hour
ANALYSIS_CACHE_TTL=86400  # 24 hours
"""

    with open('.env', 'w') as f:
        f.write(env_template)

    print("✅ Created .env file with template")
    print("⚠️  Please fill in your Pinecone credentials and database settings")


async def test_rag_system():
    """Test RAG system functionality"""
    try:
        from backend.app.services.rag_service import rag_service

        print("🔍 Testing RAG system...")

        # Test health check
        health = await rag_service.health_check()
        print(f"   • RAG Health: {health.get('status', 'unknown')}")

        if health.get('status') == 'healthy':
            print("   ✅ RAG system is operational")

            # Test sample data creation
            print("   📝 Creating sample data for testing...")
            sample_result = await rag_service._get_rag_context({"test": True}, "health")
            if sample_result:
                print("   ✅ Sample data creation successful")
            else:
                print("   ⚠️  Sample data creation returned empty")

        else:
            print("   ❌ RAG system health check failed")
            print(f"   Error: {health.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"   ❌ RAG test failed: {str(e)}")


async def test_ai_system():
    """Test AI analysis system"""
    try:
        from backend.app.services.enhanced_ai_service import enhanced_ai_service

        print("🤖 Testing AI analysis system...")

        # Test basic connectivity
        test_response = await enhanced_ai_service._call_openrouter(
            enhanced_ai_service.gemini_model,
            [{"role": "user", "content": "Hello, test message"}]
        )

        if test_response:
            print("   ✅ AI system connectivity OK")
        else:
            print("   ❌ AI system connectivity failed")

    except Exception as e:
        print(f"   ❌ AI test failed: {str(e)}")


def create_directory_structure():
    """Create necessary directories"""
    directories = [
        'exports',
        'logs',
        'uploads',
        'scripts'
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def main():
    """Main setup function"""
    print("🚀 Africa Strategy RAG Environment Setup")
    print("=" * 50)

    # Check environment variables
    print("\n1. Checking environment variables...")
    env_ok = check_environment_variables()

    # Create .env file if needed
    print("\n2. Setting up environment file...")
    create_env_file()

    # Create directory structure
    print("\n3. Creating directory structure...")
    create_directory_structure()

    # Test systems if environment is ready
    if env_ok:
        print("\n4. Testing systems...")
        import asyncio
        asyncio.run(test_rag_system())
        asyncio.run(test_ai_system())
    else:
        print("\n4. Skipping system tests (environment not configured)")

    # Print next steps
    print("\n" + "=" * 50)
    print("📋 NEXT STEPS:")
    print("=" * 50)

    if not env_ok:
        print("1. 🔑 Configure your environment variables in .env:")
        print("   • PINECONE_API_KEY")
        print("   • PINECONE_ENVIRONMENT")
        print("   • DATABASE_URL")
        print("2. 🗄️  Create Pinecone index via dashboard or API")
        print("3. 🧪 Run tests again: python scripts/setup_rag_environment.py")

    print("\n4. 📤 Export your PostgreSQL data:")
    print("   python scripts/export_pgadmin_data.py")

    print("\n5. 📥 Import data to Pinecone:")
    print("   python scripts/import_to_pinecone.py")

    print("\n6. 🎯 Test enhanced analyses:")
    print("   curl -X POST http://localhost:8000/api/v1/analyses/integrated-synthesis \\")
    print("     -d '{\"company_name\": \"Test Corp\", \"sector\": \"agriculture\", \"country\": \"Côte d'Ivoire\"}'")

    print("\n🎉 RAG environment setup complete!")
    print("💡 Your AI system is now ready for enhanced analyses with contextual knowledge!")


if __name__ == "__main__":
    main()