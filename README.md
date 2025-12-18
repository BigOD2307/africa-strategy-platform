# 🌍 Africa Strategy Platform V2

Plateforme d'analyse stratégique durable pour les entreprises africaines, utilisant l'IA (OpenAI) pour générer des analyses complètes en 7 blocs.

## 🚀 Fonctionnalités

- **7 Assistants IA spécialisés** pour des analyses approfondies
- **Dashboard interactif** avec graphiques et indicateurs
- **Chatbot contextuel** pour poser des questions sur les analyses
- **Formulaire intelligent** adapté aux profils utilisateurs

### Les 7 Blocs d'Analyse

| Bloc | Contenu |
|------|---------|
| 🌍 BLOC 1 | PESTEL+ (Politique, Économie, Social, Tech, Environnement, Légal, Climat, Biodiversité) |
| 🌡️ BLOC 2 | Risques Climat & Transition |
| 📈 BLOC 3 | Marché & Concurrence |
| 🔗 BLOC 4 | Chaîne de Valeur Durable |
| 🎯 BLOC 5 | ODD & Durabilité |
| ⚖️ BLOC 6 | Cadre Réglementaire |
| 📋 BLOC 7 | Synthèse Stratégique |

---

## 📋 Prérequis

- **Python 3.10+**
- **Node.js 18+**
- **Clé API OpenAI** (avec accès aux Assistants)

---

## 🛠️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/BigOD2307/africa-strategy-platform.git
cd africa-strategy-platform
```

### 2. Configurer le Backend

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate

# Activer l'environnement (Mac/Linux)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` dans le dossier `backend/` :

```env
OPENAI_API_KEY=sk-votre-cle-openai-ici
```

### 4. Créer les Assistants OpenAI

Vous devez créer 7 assistants sur [platform.openai.com](https://platform.openai.com/assistants) :

1. Aller sur OpenAI Platform → Assistants → Create Assistant
2. Pour chaque assistant (BLOC1 à BLOC7) :
   - **Nom** : "BLOC1 - PESTEL+", "BLOC2 - Risques Climat", etc.
   - **Instructions** : Ouvrir `backend/app/config/prompts/blocX_prompt.py` et copier le contenu de `SYSTEM_PROMPT`
   - **Model** : `gpt-4o` ou `gpt-4o-mini`
   - **Tools** : Activer "File Search" si vous avez des fichiers RAG
3. Noter l'ID de chaque assistant (format: `asst_xxxxx`)

**Modifier le fichier `backend/app/services/openai_assistant_service.py` aux lignes 36-44 :**

```python
ASSISTANT_IDS = {
    "BLOC1": "asst_votre_id_bloc1",  # Remplacez par votre ID réel
    "BLOC2": "asst_votre_id_bloc2",
    "BLOC3": "asst_votre_id_bloc3",
    "BLOC4": "asst_votre_id_bloc4",
    "BLOC5": "asst_votre_id_bloc5",
    "BLOC6": "asst_votre_id_bloc6",
    "BLOC7": "asst_votre_id_bloc7",
}
```

⚠️ **Important** : Remplacez chaque `asst_votre_id_blocX` par le vrai ID de votre assistant créé sur OpenAI (format: `asst_xxxxx`).

### 5. Configurer le Frontend

```bash
# Revenir à la racine et aller dans frontend
cd ../frontend

# Installer les dépendances
npm install
```

---

## ▶️ Lancement

### Option 1 : Lancement manuel

**Terminal 1 - Backend :**
```bash
cd backend
.\venv\Scripts\activate  # Windows
# ou: source venv/bin/activate  # Mac/Linux
python -m uvicorn app.main_simple:app --reload --port 8000
```

**Terminal 2 - Frontend :**
```bash
cd frontend
npm run dev
```

### Option 2 : Utiliser les scripts (Windows)

Double-cliquer sur :
- `start_backend.bat` pour lancer le backend
- `start_frontend.bat` pour lancer le frontend

---

## 🌐 Accès

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

---

## 📖 Utilisation

1. **Remplir le formulaire** : Sélectionner votre profil, secteur, pays, etc.
2. **Lancer l'analyse** : Cliquer sur "Lancer l'analyse"
3. **Consulter le dashboard** : Les 7 blocs s'affichent progressivement
4. **Poser des questions** : Utiliser le chatbot (💬) pour explorer les résultats

---

## 📁 Structure du Projet

```
africa-strategy-platform/
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── prompts/          # Prompts des 7 assistants
│   │   ├── services/
│   │   │   └── openai_assistant_service.py
│   │   └── main_simple.py        # API principale
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── components/
│   │   └── Chatbot.tsx
│   ├── config/                   # Configs (secteurs, pays, ODD)
│   ├── pages/
│   │   ├── index.tsx             # Formulaire
│   │   └── dashboard.tsx         # Dashboard
│   └── package.json
├── start_backend.bat
├── start_frontend.bat
└── README.md
```

---

## 🔧 Configuration avancée

### Changer le modèle du chatbot

Dans `backend/app/main_simple.py`, modifier la ligne :
```python
model="gpt-4o"  # ou "gpt-4o-mini" pour moins cher
```

### Ajouter des secteurs/pays

Modifier les fichiers dans `frontend/config/` :
- `secteurs.ts` : Liste des secteurs d'activité
- `pays.ts` : Liste des pays africains
- `profils.ts` : Types de profils utilisateurs
- `odds.ts` : Objectifs de Développement Durable

---

## 💰 Coûts estimés (OpenAI)

| Action | Coût approximatif |
|--------|-------------------|
| 1 analyse complète (7 blocs) | ~$0.50 - $1.00 |
| 1 question chatbot | ~$0.01 - $0.02 |

*Les coûts dépendent de la longueur des réponses et du modèle utilisé.*

---

## 🐛 Dépannage

### Le backend ne démarre pas
```bash
# Vérifier que l'environnement est activé
.\venv\Scripts\activate
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur "OPENAI_API_KEY not found"
- Vérifier que le fichier `.env` existe dans `backend/`
- Vérifier que la clé commence par `sk-`

### Le frontend affiche une erreur CORS
- Vérifier que le backend tourne sur le port 8000
- Redémarrer le backend

---

## 📄 Licence

MIT License - Libre d'utilisation et de modification.

---

## 👥 Contributeurs

- Développé par l'équipe Africa Strategy
