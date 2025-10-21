# Africa Strategy - Plateforme IA pour Entrepreneurs Africains

## 📋 Description du Projet

Africa Strategy est une plateforme innovante qui utilise l'intelligence artificielle pour accompagner les entrepreneurs africains vers la durabilité. La plateforme propose des analyses PESTEL/ESG personnalisées, des dashboards interactifs et une roadmap d'accompagnement.

## 🎯 Fonctionnalités Principales

- **Questionnaire Intelligent** : Collecte de données via un questionnaire adaptatif
- **Analyses IA** : Génération d'analyses PESTEL et ESG personnalisées
- **Dashboard Interactif** : Visualisation des données avec graphiques et cartes
- **Roadmap Personnalisée** : Accompagnement étape par étape
- **Chatbot Contextuel** : Assistant IA pour guider les entrepreneurs

## 🛠️ Stack Technique

### Frontend
- **Next.js 14** + React 18 + TypeScript
- **Chart.js** + React-Chartjs-2 pour les visualisations
- **React-Leaflet** pour les cartes interactives
- **Tailwind CSS** + Shadcn/ui pour l'interface

### Backend
- **Python 3.11** + FastAPI
- **LangChain** + LangGraph pour l'orchestration IA
- **OpenAI Gemini 2.5** pour les analyses
- **Pinecone** pour la base de données vectorielle

### Infrastructure
- **PostgreSQL 15** pour les données relationnelles
- **Redis** pour le cache
- **Docker** + Docker Compose
- **Vercel** (Frontend) + **Railway** (Backend)

## 📁 Structure du Projet

```
africa-strategy/
├── frontend/                 # Application Next.js
│   ├── src/
│   │   ├── components/      # Composants React
│   │   ├── pages/           # Pages de l'application
│   │   ├── hooks/           # Hooks personnalisés
│   │   ├── utils/           # Utilitaires
│   │   └── types/           # Types TypeScript
│   ├── public/              # Assets statiques
│   └── package.json
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/             # Endpoints API
│   │   ├── core/            # Configuration
│   │   ├── models/          # Modèles de données
│   │   ├── services/        # Services métier
│   │   └── utils/           # Utilitaires
│   ├── tests/               # Tests unitaires
│   └── requirements.txt
├── database/                # Scripts de base de données
│   ├── migrations/          # Migrations SQL
│   └── seeds/               # Données de test
├── docs/                    # Documentation
├── docker-compose.yml       # Configuration Docker
└── README.md
```

## 🚀 Installation et Démarrage

### Prérequis
- Node.js 18+
- Python 3.11+
- PostgreSQL 15
- Docker Desktop

### Installation Frontend
```bash
cd frontend
npm install
npm run dev
```

### Installation Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Base de données
```bash
docker-compose up -d postgres redis
```

## 📊 Variables d'Environnement

Créer les fichiers `.env` suivants :

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/africa_strategy
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
```

## 🧪 Tests

```bash
# Tests Frontend
cd frontend && npm test

# Tests Backend
cd backend && pytest
```

## 📚 Documentation API

Une fois le serveur démarré, la documentation Swagger est disponible à :
- http://localhost:8000/docs

## 👨‍💻 Développeur

**Ousmane Dicko** - Développeur IA Full-Stack

## 📄 Licence

Propriétaire - Tous droits réservés
