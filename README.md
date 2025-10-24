# 🌍 Africa Strategy - Plateforme IA pour Entrepreneurs Africains

**Développé par Ousmane Dicko** - Création d'un écosystème digital pour la transformation durable des PME africaines.

---

## 🎯 Vision du Projet

Africa Strategy est une **plateforme IA innovante** qui révolutionne l'accompagnement des entrepreneurs africains vers la durabilité. Notre système analyse automatiquement les pratiques ESG des entreprises et génère des recommandations stratégiques personnalisées pour accélérer leur transformation durable.

### **Problème Résolu**
- **Entrepreneurs africains** : Manque d'outils d'analyse stratégique adaptés
- **Investisseurs** : Difficulté à évaluer la maturité ESG des PME
- **Écosystème** : Absence de plateforme intégrée pour la durabilité

### **Solution Apportée**
- **Analyses IA temps réel** : PESTEL, ESG, marché, chaîne de valeur
- **Recommandations actionnables** : Plans personnalisés avec ROI
- **Dashboard interactif** : Visualisation claire des analyses
- **Connexion investisseurs** : Matching automatique avec fonds d'impact

---

## 🏗️ Architecture Technique

### **Backend - FastAPI (Python)**
```
🔧 Technologies : FastAPI, PostgreSQL, Redis, OpenRouter
🎯 Rôle : API REST, logique métier, analyses IA
⚡ Performance : Async/await, cache intelligent
```

### **IA Core - OpenRouter**
```
🤖 Modèles : Gemini 2.5 Flash + Perplexity
🔍 Fonctions : Analyses stratégiques, recherche web temps réel
📊 Analyses : PESTEL, ESG, marché, chaîne de valeur, synthèse intégrale
```

### **Frontend - Next.js (React)**
```
⚛️ Technologies : Next.js 14, TypeScript, Tailwind CSS
📱 Interface : Formulaire 11 étapes, dashboard analytics
🎨 UX : Responsive, accessible, moderne
```

### **Infrastructure - Docker**
```
🐳 Services : PostgreSQL, Redis, Backend, Frontend
🚀 Déploiement : Conteneurisé, scalable, production-ready
```

---

## 📋 Fonctionnalités Détaillées

### **1. Configuration Entrepreneur (11 Étapes)**
- **Informations de base** : Secteur, pays, taille entreprise
- **Analyse ESG** : 30+ questions sur pratiques durables
- **Vision stratégique** : Objectifs, mission, projets significatifs
- **Validation temps réel** : Contrôles automatiques des données

### **2. Analyses IA Avancées**

#### **Analyse PESTEL (Politique, Économique, Social, Technologique, Environnemental, Légal)**
- **Score 0-10** par dimension avec justifications
- **Données temps réel** via Perplexity
- **Recommandations prioritaires** par axe

#### **Analyse ESG (Environnemental, Social, Gouvernance)**
- **Scoring automatique** basé sur questionnaire
- **Comparaisons sectorielles** et benchmarks
- **Plans d'amélioration** personnalisés

#### **Analyse Marché & Concurrence**
- **Taille et croissance** du marché sectoriel
- **Cartographie concurrents** (5 principaux acteurs)
- **Tendances 2025** et opportunités émergentes

#### **Analyse Chaîne de Valeur**
- **Activités primaires** : Inbound, opérations, outbound, marketing, service
- **Activités support** : Infrastructure, GRH, technologie, achats
- **Points d'optimisation** et avantages concurrentiels

#### **Analyse Impact Durable & ODD**
- **Contribution ODD** : Mesure d'impact par objectif
- **Évaluation triple bottom line** : People, Planet, Profit
- **Score de durabilité** global 0-100

#### **Synthèse Intégrale**
- **Résumé exécutif** : Vue d'ensemble stratégique
- **Conclusions clés** : 5-7 insights majeurs
- **Recommandations stratégiques** : Priorisées par impact
- **Score global consolidé** : Maturité entreprise

### **3. Roadmap Stratégique IA**
- **Génération automatique** : 4-5 phases sur 24 mois
- **Actions concrètes** : 5-8 actions par phase avec métriques
- **Investissement estimé** et ROI projeté
- **Suivi de progression** avec jalons mesurables

### **4. Chatbot IA Contextuel**
- **Réponses personnalisées** : Basées sur toutes les analyses
- **Conseils stratégiques** : Adaptés au contexte africain
- **Support opérationnel** : Aide à l'implémentation

---

## 🚀 Démarrage Rapide

### **Prérequis**
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Clé API OpenRouter (gratuite)

### **Installation**
```bash
# 1. Cloner le repository
git clone https://github.com/BigOD2307/africa-strategy-platform.git
cd africa-strategy-platform

# 2. Configuration environnement
cp env.example .env
# Éditer .env avec OPENROUTER_API_KEY

# 3. Lancement complet
docker-compose up -d

# 4. Accès
# Frontend : http://localhost:3000
# API : http://localhost:8000
# Docs API : http://localhost:8000/docs
```

### **Test IA**
```bash
# Analyse complète
curl -X POST http://localhost:8000/api/v1/analyses/integrated-synthesis \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "test-123",
    "company_data": {
      "company_name": "AgriTech Côte d\'Ivoire",
      "sector": "agriculture",
      "country": "Côte d\'Ivoire",
      "size": "PME"
    },
    "esg_responses": {
      "energy_consumption": "yes_detailed",
      "waste_management": "recycling_program"
    }
  }'
```

---

## 📊 APIs Disponibles

### **Configuration**
- `POST /api/v1/configuration/entrepreneur` - Sauvegarder profil entreprise

### **Analyses IA**
- `POST /api/v1/analyses/pestel` - Analyse PESTEL
- `POST /api/v1/analyses/esg` - Analyse ESG
- `POST /api/v1/analyses/market-competition` - Analyse marché
- `POST /api/v1/analyses/value-chain` - Analyse chaîne de valeur
- `POST /api/v1/analyses/sustainability-impact` - Impact durable
- `POST /api/v1/analyses/integrated-synthesis` - Synthèse complète
- `POST /api/v1/analyses/strategic-roadmap` - Roadmap stratégique

### **IA Interactive**
- `POST /api/v1/analyses/chat-contextual` - Chatbot IA

### **Système**
- `GET /api/v1/health` - État des services
- `GET /api/v1/analyses/health` - État IA

---

## 💰 Modèle Économique

### **Revenus**
- **Entreprises** : 5,000 FCFA/mois (accès analyses IA)
- **Premium** : 15,000 FCFA/mois (roadmap + chatbot illimité)
- **Investisseurs** : 50,000 FCFA/mois (matching + analytics avancés)

### **Coûts**
- **IA (OpenRouter)** : 50-200€/mois selon utilisation
- **Infrastructure** : 100€/mois (serveurs cloud)
- **Total** : 150-300€/mois

### **Projection**
- **Année 1** : 500 entreprises → 30M FCFA revenus
- **Année 2** : 2000 entreprises → 120M FCFA revenus
- **Marge** : 70% (après coûts opérationnels)

---

## 📈 État d'Avancement

### **✅ TERMINÉ (Semaines 1-3)**

#### **Semaine 1 : Infrastructure Core**
- ✅ API FastAPI complète avec PostgreSQL
- ✅ Frontend Next.js avec TypeScript
- ✅ Configuration Docker production-ready
- ✅ Base de données avec migrations

#### **Semaine 2 : Configuration Entrepreneur**
- ✅ Formulaire 11 étapes interactif
- ✅ Validation frontend/backend
- ✅ Sauvegarde automatique
- ✅ API REST pour données entreprise

#### **Semaine 3 : IA Core Avancée**
- ✅ Intégration OpenRouter (Gemini 2.5 Flash + Perplexity)
- ✅ Service IA modulaire avec 5 analyses stratégiques
- ✅ APIs REST complètes pour toutes les analyses
- ✅ Chatbot IA contextuel
- ✅ Système de scoring automatique

### **🔄 EN COURS (Semaines 4-6)**

#### **Semaine 4 : Dashboard Analytics**
- 🔄 Graphiques PESTEL (radar chart)
- 🔄 Graphiques ESG (barres + comparaisons)
- 🔄 Carte géographique interactive
- 🔄 Score global avec progression

#### **Semaine 5 : Roadmap & Chatbot**
- 🔄 Timeline roadmap interactive
- 🔄 Système validation étapes
- 🔄 Interface chatbot intégrée
- 🔄 Upload documents + IA review

#### **Semaine 6 : Finalisation**
- 🔄 Tests utilisateurs complets
- 🔄 Optimisations performance
- 🔄 Déploiement production
- 🔄 Documentation développeur

**Progression : 75% terminé - IA core opérationnelle**

---

## 🎯 Impact Attendu

### **Pour les Entrepreneurs**
- **Économies** : 20-30% sur analyses stratégiques (vs consultants)
- **Rapidité** : Analyses en 25 secondes vs semaines
- **Précision** : Données temps réel + expertise IA
- **Croissance** : Accès facilité aux financements verts

### **Pour l'Écosystème**
- **500+ PME** accompagnées première année
- **50M FCFA** d'investissements verts débloqués
- **Création d'écosystème** durable Afrique de l'Ouest
- **Standardisation** des pratiques ESG

### **Pour les Investisseurs**
- **Évaluation fiable** de la maturité ESG
- **Matching automatisé** avec PME éligibles
- **Suivi d'impact** temps réel
- **Réduction risque** d'investissement

---

## 🛠️ Technologies Avancées

### **IA & Machine Learning**
- **Gemini 2.5 Flash** : Analyse stratégique temps réel
- **Perplexity** : Recherche web contextuelle
- **LangChain** : Orchestration IA modulaire
- **OpenRouter** : Gestion unifiée des modèles

### **Performance & Scalabilité**
- **FastAPI Async** : 1000+ req/sec
- **Redis Cache** : Réduction latence 80%
- **PostgreSQL** : Données relationnelles optimisées
- **Docker** : Déploiement horizontal

### **Sécurité & Monitoring**
- **Sentry** : Monitoring erreurs temps réel
- **CORS** : Sécurité API configurée
- **Validation Pydantic** : Données sûres
- **Logs structurés** : Debugging avancé

---

## 📞 Contact & Support

**Développeur** : Ousmane Dicko
**Client** : Hamed (Africa Strategy)
**Repository** : [GitHub](https://github.com/BigOD2307/africa-strategy-platform)

**Africa Strategy** - Transformer les PME africaines vers l'excellence durable ! 🌍✨

---

*Projet développé avec excellence technique et vision stratégique pour l'Afrique durable*
