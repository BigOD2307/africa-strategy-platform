@echo off
echo 🚀 Démarrage d'Africa Strategy
echo ================================

echo.
echo 📦 Vérification des prérequis...

:: Vérifier Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js n'est pas installé
    echo Veuillez installer Node.js 18+ depuis https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js détecté

:: Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé
    echo Veuillez installer Python 3.11+ depuis https://python.org/
    pause
    exit /b 1
)
echo ✅ Python détecté

:: Vérifier Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé
    echo Veuillez installer Docker Desktop depuis https://docker.com/
    pause
    exit /b 1
)
echo ✅ Docker détecté

echo.
echo 🗄️ Démarrage des services de base de données...
docker-compose up -d postgres redis

echo.
echo ⏳ Attente du démarrage des services...
timeout /t 10 /nobreak >nul

echo.
echo 📦 Installation des dépendances frontend...
cd frontend
if not exist node_modules (
    npm install
) else (
    echo ✅ Dépendances frontend déjà installées
)
cd ..

echo.
echo 📦 Installation des dépendances backend...
cd backend
if not exist venv (
    echo Création de l'environnement virtuel...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo.
echo 🚀 Démarrage des services...

echo 📊 Démarrage du backend...
start "Africa Strategy Backend" cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo ⏳ Attente du démarrage du backend...
timeout /t 5 /nobreak >nul

echo 🎨 Démarrage du frontend...
start "Africa Strategy Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Africa Strategy est en cours de démarrage!
echo.
echo 📊 Backend: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo 🎨 Frontend: http://localhost:3000
echo.
echo Appuyez sur une touche pour continuer...
pause >nul
