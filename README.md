# 🌍 Africa Strategy - Plateforme IA pour Entrepreneurs Africains

Plateforme d'accompagnement IA pour aider les entrepreneurs africains à intégrer des pratiques durables et accéder aux financements verts.

## 🎯 Vision

Créer un écosystème digital qui :
- **Analyse** les pratiques ESG des entreprises africaines
- **Accompagne** les entrepreneurs vers la durabilité
- **Connecte** avec les investisseurs et fonds d'impact
- **Transforme** le modèle économique des PME africaines

## 🚀 Fonctionnalités

### 🤖 Intelligence Artificielle
- **Analyse PESTEL** : Évaluation stratégique complète (Politique, Économique, Social, Technologique, Environnemental, Légal)
- **Analyse ESG** : Scoring Environnemental, Social et Gouvernance
- **Roadmap Personnalisée** : Plan d'action adapté au contexte africain
- **Chatbot IA** : Assistant conversationnel pour conseils personnalisés

### 📊 Dashboard Interactif
- **Graphiques PESTEL** : Radar chart avec 6 dimensions
- **Graphiques ESG** : Barres comparatives avec benchmarks
- **Carte Géographique** : Opportunités par pays/région
- **Système de Progression** : Badges Bronze/Argent/Or

### 🎓 Accompagnement
- **Questionnaire Intelligent** : 11 étapes pour profil complet
- **Recommandations Actionnables** : Coûts, délais, priorités
- **Suivi de Progression** : KPIs et métriques personnalisés
- **Connexion Investisseurs** : Matching avec fonds climat

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** : API REST haute performance
- **PostgreSQL** : Base de données relationnelle
- **OpenRouter API** : Accès aux meilleurs modèles IA
  - **Gemini 2.5 Flash** : Analyses stratégiques
  - **Perplexity** : Recherche internet temps réel

### Frontend
- **Next.js 14** : Framework React moderne
- **TypeScript** : Code typé et maintenable
- **Tailwind CSS** : Interface élégante et responsive
- **Chart.js** : Graphiques interactifs

### Infrastructure
- **Docker** : Conteneurisation complète
- **Redis** : Cache haute performance (optionnel)

## 📋 Prérequis

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Clé API OpenRouter** (gratuite)

## 🚀 Installation Rapide

### 1. Cloner le repository
```bash
git clone https://github.com/BigOD2307/africa-strategy-platform.git
cd africa-strategy-platform
```

### 2. Configuration
```bash
# Copier le fichier d'environnement
cp env.example .env

# Éditer .env avec vos clés API
nano .env
```

### 3. Lancement avec Docker
```bash
# Démarrer tous les services
docker-compose up -d

# Ou utiliser le script Windows
start.bat
```

### 4. Accès aux applications
- **Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🔧 Configuration API

### OpenRouter (Obligatoire)
1. Créer un compte sur [OpenRouter.ai](https://openrouter.ai)
2. Générer une clé API gratuite
3. Ajouter dans `.env` :
```env
OPENROUTER_API_KEY=votre-cle-api-ici
```

### Base de Données (PostgreSQL)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/africa_strategy
```

## 📊 Utilisation

### 1. Configuration Entrepreneur
- Remplir le questionnaire en 11 étapes
- Validation automatique des données
- Sauvegarde en temps réel

### 2. Analyses IA
```bash
# Analyse PESTEL
curl -X POST http://localhost:8000/api/v1/analyses/pestel \
  -H "Content-Type: application/json" \
  -d '{"company_id": "123", "company_data": {...}}'

# Analyse ESG
curl -X POST http://localhost:8000/api/v1/analyses/esg \
  -H "Content-Type: application/json" \
  -d '{"company_id": "123", "company_data": {...}, "esg_responses": {...}}'

# Analyse Complète + Roadmap
curl -X POST http://localhost:8000/api/v1/analyses/complete \
  -H "Content-Type: application/json" \
  -d '{"company_id": "123", "company_data": {...}, "esg_responses": {...}}'
```

### 3. Chat IA
```bash
curl -X POST http://localhost:8000/api/v1/analyses/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment améliorer mon score ESG ?", "company_id": "123"}'
```

## 🎯 APIs Disponibles

### Analyses IA
- `POST /api/v1/analyses/pestel` - Analyse PESTEL
- `POST /api/v1/analyses/esg` - Analyse ESG
- `POST /api/v1/analyses/complete` - Analyse complète + roadmap
- `POST /api/v1/analyses/chat` - Chat avec IA

### Configuration Entrepreneur
- `POST /api/v1/configuration` - Sauvegarder configuration
- `GET /api/v1/configuration/{company_id}` - Récupérer configuration

### Système
- `GET /api/v1/health` - Santé du système
- `GET /api/v1/analyses/health` - Santé du service IA

## 💰 Coûts et Budget

### Développement
- **Total estimé** : 4 semaines de développement
- **Coût** : Selon accord avec l'équipe technique

### Infrastructure (Mensuel)
- **OpenRouter API** : 50-200€/mois (selon utilisation)
- **Hébergement** : 50€/mois (serveurs cloud)
- **Base de données** : 20€/mois (PostgreSQL)
- **Total** : 120-270€/mois

### Revenus Attendus
- **100 entreprises/mois** : 5,000€
- **500 entreprises/mois** : 25,000€
- **1000 entreprises/mois** : 50,000€

## 🗺️ Roadmap Produit

### ✅ Semaine 1-2 : Infrastructure & Configuration
- [x] API FastAPI complète
- [x] Formulaire entrepreneur 11 étapes
- [x] Base de données PostgreSQL
- [x] Interface Next.js responsive

### 🔄 Semaine 3 : IA Core (EN COURS)
- [x] Configuration OpenRouter
- [x] Service IA avec Gemini 2.5 Flash
- [x] Intégration Perplexity pour données temps réel
- [ ] Tests et validation analyses
- [ ] Optimisation performances

### 🔄 Semaine 4 : Dashboard Analytics
- [ ] Graphiques PESTEL (radar chart)
- [ ] Graphiques ESG (barres)
- [ ] Carte géographique interactive
- [ ] Score global avec progression

### 🔄 Semaine 5 : Roadmap & Chatbot
- [ ] Système de roadmap personnalisée
- [ ] Chatbot IA contextuel
- [ ] Upload de documents
- [ ] Validation d'étapes

### 🔄 Semaine 6 : Finalisation
- [ ] Tests utilisateurs complets
- [ ] Optimisations performance
- [ ] Documentation développeur
- [ ] Déploiement production

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📞 Contact

**Hamed** - Entrepreneur visionnaire
**Équipe Technique** - Développement et maintenance

**Africa Strategy** - Transformer les PME africaines vers la durabilité ! 🌍✨

---

## 🔧 Scripts Disponibles

```bash
# Développement
npm run dev          # Frontend Next.js
cd backend && uvicorn app.main:app --reload  # Backend FastAPI

# Production
docker-compose up -d  # Tout démarrer
docker-compose down   # Tout arrêter

# Tests
pytest backend/       # Tests backend
npm test             # Tests frontend
```

## 🌟 Impact Attendu

- **500+ entreprises** accompagnées la première année
- **50M FCFA** de financements verts débloqués
- **Réduction de 30%** de l'empreinte carbone moyenne
- **Création d'écosystème** durable en Afrique de l'Ouest

---

*Développé avec ❤️ pour l'Afrique durable*
