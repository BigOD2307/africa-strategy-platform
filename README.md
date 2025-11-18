# Africa Strategy – Notes d’atelier & Guide de prise en main

Version nettoyée : seuls les fichiers utiles à l’exécution (backend, frontend, scripts de démarrage, docker-compose, README) restent dans le dépôt.

---

## 1. Comment nous avons construit la solution (A ➜ Z)

1. **Formulaire Next.js multi-étapes**  
   - `pages/index.tsx` collecte secteur, profil, ODD, vision/mission et sauvegarde tout dans `sessionStorage`.

2. **API FastAPI dédiée**  
   - `POST /api/analyze` (voir `backend/app/api/v1/endpoints/analyses.py`) crée un thread OpenAI Assistants, suit le run (polling 10 min), puis parse le JSON avec `JSONCleaner` pour supprimer commentaires/rescapés.
   - `POST /api/enrich` passe les textes dans OpenRouter pour générer résumés et points clés.
   - `POST /api/chat` transforme la dernière analyse en contexte pour le chatbot (Assistant OpenAI).

3. **Dashboard Next.js**  
   - `pages/dashboard.tsx` récupère `analysisResult` + formulaire, affiche 6 onglets (Overview, PESTEL, ESG, Market, Risk, Synthesis) avec Chart.js (radars, barres, doughnuts, lignes).
   - Le chatbot (`components/Chatbot.tsx`) reprend la logique ChatGPT : bulles, suggestions, modal pleine largeur sur mobile. Il tape directement dans `/api/chat`.

4. **Design system rapide**  
   - Tailwind + classes utilitaires, couleurs harmonisées (palette `chartPalette`), cartes glassmorphism.
   - Scripts `start_backend.bat` / `start_frontend.bat` pour tout lancer sans CLI.

---

## 2. Lancer et tester la solution

### Pré-requis
| Outil | Version |
| --- | --- |
| Python | >= 3.10 |
| Node.js | >= 18 |
| npm | >= 9 |
| Clés API | `OPENAI_API_KEY`, `OPENAI_ASSISTANT_ID`, `OPENROUTER_API_KEY` |

Copier `env.example` → `backend/.env`, puis compléter :

```env
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_...
OPENROUTER_API_KEY=or-...
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
DEBUG=true
```

### Option 1 – 100 % clic (Windows)
1. Double-cliquer sur `start_backend.bat` → active le venv + lance `uvicorn app.main_simple:app --reload --port 8000`.
2. Double-cliquer sur `start_frontend.bat` → `npm run dev` (Next.js) sur `http://localhost:3000`.
3. Ouvrir le navigateur, remplir le formulaire, attendre l’analyse (logs côté backend), consulter le dashboard, ouvrir le chatbot via l’icône 💬.

### Option 2 – CLI (cross-platform)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # ou venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main_simple:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Tests rapides
- **Ping API** : `curl http://localhost:8000/health`
- **Type-check front** : `npm run type-check`
- **Lint Next** : `npm run lint`

---

## 3. Structure minimale à connaître

```
A-S/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints     # analyze, enrich, chat, health
│   │   ├── core                 # config, logging
│   │   └── services             # OpenAI assistant, OpenRouter, JSON cleaner
│   ├── main_simple.py           # entrypoint uvicorn
│   ├── requirements.txt
│   └── start_backend.bat
├── frontend/
│   ├── pages/index.tsx          # questionnaire
│   ├── pages/dashboard.tsx      # dashboard complet
│   ├── components/Chatbot.tsx
│   └── start_frontend.bat
├── docker-compose.yml           # optionnel, boot dev rapide
├── env.example
└── README.md
```

Ce qui a été retiré : anciens dumps SQLite, dossier `data/` et scripts de test obsolètes. Il ne reste que les éléments nécessaires à l’exécution décrits ci-dessus.

---

## 4. Décisions design & bonnes pratiques

- **JSONCleaner** reconstruit les réponses Assistant (supprime commentaires, équilibre accolades) pour éviter les plantages.
- **Chart.js** custom (palette + borderRadius) pour des visuels premium.
- **Chatbot** en modal type ChatGPT, accessible via un simple bouton flottant.
- **Scripts start\_*.bat** pour les utilisateurs non techniques (double clic suffit).

---

## 5. Dépannage rapide

| Symptôme | Vérification |
| --- | --- |
| Analyse qui échoue | Logs backend (`uvicorn`), clé OpenAI correcte, JSONCleaner n’a pas écrit de `failed_json*.txt` |
| Dashboard vide | `sessionStorage` n’a pas `analysisResult` (relancer le formulaire) |
| Chatbot muet | L’icône 💬 s’affiche uniquement quand une analyse est en mémoire |

---

## 6. Roadmap (idées)
- Persister les analyses en base (historique).
- Auth simple + multi-projets.
- Export PDF / partage de rapport.
- Intégration RAG complète avec Pinecone/Chroma.

---

Projet maintenu par **Ousmane Dicko** – toute suggestion ou bug : ouvrir une issue ou pinger l’équipe interne.

DATABASE_URL=sqlite:///./africa_strategy.db

# CORS (pour le frontend)
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Environnement
ENVIRONMENT=development
DEBUG=true
```

### 2. Configuration de l'Assistant OpenAI

L'assistant OpenAI doit être configuré avec :
- **Modèle** : GPT-4 ou GPT-4 Turbo
- **Fonctionnalités** : 
  - Code Interpreter (pour les calculs)
  - Retrieval (pour RAG, optionnel)
  - Internet (pour recherches web)
- **Instructions** : Voir `docs/ASSISTANT_IA_SPECIFICATIONS.md`

---

## 🎮 Utilisation

### Démarrage du Backend

```bash
cd backend

# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Démarrer le serveur
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
```

Le serveur démarre sur : **http://localhost:8000**

### Démarrage du Frontend

```bash
cd frontend

# Démarrer le serveur de développement
npm run dev
```

Le frontend démarre sur : **http://localhost:3000**

### Utilisation de l'Application

1. **Accéder au formulaire** : Ouvrez http://localhost:3000
2. **Remplir le questionnaire** : Suivez les 11 étapes
3. **Lancer l'analyse** : Cliquez sur "Terminer et Analyser"
4. **Attendre l'analyse** : L'IA génère l'analyse (2-10 minutes)
5. **Consulter le dashboard** : Visualisez les résultats détaillés

---

## 🧪 Tests

### Test du Backend

```bash
cd backend

# Activer l'environnement virtuel
venv\Scripts\activate

# Tester la connexion OpenAI
python test_backend.py

# Tester l'API
curl http://localhost:8000/health
```

### Test du Frontend

```bash
cd frontend

# Lancer les tests
npm test

# Vérifier les types TypeScript
npm run type-check
```

### Test End-to-End

1. Démarrer le backend (port 8000)
2. Démarrer le frontend (port 3000)
3. Remplir le formulaire complet
4. Vérifier que l'analyse se lance
5. Vérifier que le dashboard affiche les résultats

---

## 📁 Structure du Projet

```
Africa-Strategy/
├── backend/                      # Backend FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/    # Endpoints API
│   │   ├── core/
│   │   │   ├── config.py        # Configuration
│   │   │   └── database.py      # Base de données
│   │   ├── models/              # Modèles SQLAlchemy
│   │   ├── services/
│   │   │   ├── openai_assistant_service.py  # Service OpenAI
│   │   │   └── rag_service.py                # Service RAG (optionnel)
│   │   └── main_simple.py       # Point d'entrée FastAPI
│   ├── requirements.txt         # Dépendances Python
│   └── test_backend.py          # Tests backend
│
├── frontend/                     # Frontend Next.js
│   ├── components/
│   │   └── ui/                  # Composants UI
│   ├── lib/
│   │   └── utils.ts             # Utilitaires
│   ├── pages/
│   │   ├── index.tsx            # Page questionnaire
│   │   ├── dashboard.tsx        # Page dashboard
│   │   └── _app.tsx             # App Next.js
│   ├── styles/
│   │   └── globals.css          # Styles globaux
│   ├── package.json             # Dépendances Node
│   └── tailwind.config.js       # Config Tailwind
│
├── data/                         # Données pour RAG (optionnel)
│   └── ...                      # Documents à indexer
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # Architecture détaillée
│   ├── ASSISTANT_IA_SPECIFICATIONS.md  # Spécifications IA
│   └── TYPES_ANALYSES_DASHBOARD.md    # Types d'analyses
│
├── scripts/                      # Scripts utilitaires
│   ├── test_questionnaire.py    # Test questionnaire
│   └── test_system.py           # Test système
│
├── .env                          # Variables d'environnement (à créer)
├── .gitignore                    # Fichiers ignorés par Git
└── README.md                     # Ce fichier
```

---

## 📚 Documentation Technique

### Documentation Disponible

- **`docs/ARCHITECTURE.md`** : Architecture détaillée du système
- **`docs/ASSISTANT_IA_SPECIFICATIONS.md`** : Spécifications complètes de l'assistant IA
- **`docs/TYPES_ANALYSES_DASHBOARD.md`** : Types d'analyses et structure des données

### API Endpoints

#### POST `/api/analyze`
Analyse complète d'une entreprise via OpenAI Assistant.

**Request Body:**
```json
{
  "secteur": "Agriculture",
  "zoneGeographique": "Afrique de l'Ouest",
  "profilOrganisation": "Entreprise privée",
  "paysInstallation": "Sénégal",
  "objectifsDD": ["ODD 1 : Pas de pauvreté"],
  "positionnementStrategique": "...",
  "visionOrganisation": "...",
  "missionOrganisation": "...",
  "projetsSignificatifs": "..."
}
```

**Response:**
```json
{
  "analyses": {
    "pestel": { ... },
    "esg": { ... },
    "market": { ... },
    "risk": { ... },
    "synthesis": { ... }
  },
  "pipeline_analytique": { ... },
  "metadata": { ... }
}
```

#### GET `/health`
Health check du serveur.

---

## 🔧 Développement

### Comment Nous Avons Créé le Projet

1. **Backend FastAPI** : Création d'une API REST simple avec un seul endpoint `/api/analyze`
2. **Intégration OpenAI Assistant** : Utilisation de l'API Assistants pour générer des analyses complètes
3. **Frontend Next.js** : Création d'un formulaire multi-étapes et d'un dashboard interactif
4. **Visualisation** : Intégration de Chart.js pour les graphiques
5. **Design** : Style minimaliste avec inline styles pour garantir le rendu

### Améliorations Futures

- [ ] Ajout de l'authentification utilisateur
- [ ] Sauvegarde des analyses en base de données
- [ ] Export PDF des analyses
- [ ] Comparaison d'analyses multiples
- [ ] Intégration RAG complète avec Pinecone
- [ ] Mode hors ligne

---

## 🐛 Dépannage

### Problèmes Courants

#### Backend ne démarre pas
- Vérifier que Python 3.8+ est installé
- Vérifier que les dépendances sont installées : `pip install -r requirements.txt`
- Vérifier que le fichier `.env` existe avec `OPENAI_API_KEY`

#### Frontend ne démarre pas
- Vérifier que Node.js 18+ est installé
- Installer les dépendances : `npm install`
- Vérifier que le port 3000 n'est pas utilisé

#### L'analyse ne se lance pas
- Vérifier que le backend est démarré sur le port 8000
- Vérifier la clé API OpenAI dans `.env`
- Vérifier les logs du backend pour les erreurs

#### Le dashboard est vide
- Vérifier que l'analyse s'est bien terminée
- Vérifier la console du navigateur pour les erreurs
- Vérifier que `sessionStorage` contient `analysisResult`

---

## 📝 Licence

Développé par Ousmane Dicko

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📞 Support

Pour toute question ou problème :
- Consulter la documentation dans `docs/`
- Vérifier les logs du serveur backend
- Ouvrir une issue sur GitHub

---

**Version 1.0** - Décembre 2025