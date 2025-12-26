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

### 2. Installation Automatique (Recommandé - Windows)

**Pour le Backend :**
```bash
# Double-cliquer sur install_backend.bat
# OU exécuter dans le terminal :
install_backend.bat
```

Ce script va automatiquement :
- ✅ Vérifier que Python est installé
- ✅ Créer l'environnement virtuel
- ✅ Installer toutes les dépendances
- ✅ Vérifier la configuration

**Pour le Frontend :**
```bash
# Double-cliquer sur install_frontend.bat
# OU exécuter dans le terminal :
install_frontend.bat
```

Ce script va automatiquement :
- ✅ Vérifier que Node.js est installé
- ✅ Installer toutes les dépendances npm

### 3. Installation Manuelle (Alternative)

**Backend :**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**Frontend :**
```bash
cd frontend
npm install
```

### 4. Configurer les variables d'environnement

**Créer un fichier `.env` dans le dossier `backend/` :**

Vous pouvez copier `backend/env.example` et le renommer en `.env`, puis modifier :

```env
OPENAI_API_KEY=sk-votre-cle-openai-ici
```

⚠️ **Important** : Obtenez votre clé API sur [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 5. Créer les Assistants OpenAI

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

---

## ▶️ Lancement

### Option 1 : Scripts Automatiques (Recommandé - Windows)

**Double-cliquer sur :**
- `start_backend.bat` pour démarrer le backend (http://localhost:8000)
- `start_frontend.bat` pour démarrer le frontend (http://localhost:3000)

⚠️ **Important** : Ouvrir deux terminaux séparés, un pour chaque script.

### Option 2 : Lancement manuel

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

### Erreur "The v1 Assistants API has been deprecated"

Si vous voyez cette erreur :
```
Error code: 400 - {'error': {'message': "The v1 Assistants API has been deprecated..."}}
```

✅ **Solution** : Cette erreur est maintenant corrigée ! Le code utilise automatiquement l'API v2.

**Si le problème persiste :**
1. Vérifiez que vous avez la dernière version du code (pull depuis GitHub)
2. Réinstallez les dépendances :
   ```bash
   cd backend
   .\venv\Scripts\activate
   pip install --upgrade openai
   pip install -r requirements.txt
   ```

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
