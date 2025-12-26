@echo off
echo ========================================
echo   Installation Backend Africa Strategy
echo ========================================
echo.

cd backend

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH !
    echo.
    echo Installez Python 3.10+ depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b 1
)

echo [1/4] Verification de Python...
python --version
echo.

REM Créer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo [2/4] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo ERREUR: Impossible de creer l'environnement virtuel !
        pause
        exit /b 1
    )
    echo Environnement virtuel cree avec succes.
) else (
    echo [2/4] Environnement virtuel deja present.
)
echo.

REM Activer l'environnement virtuel
echo [3/4] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERREUR: Impossible d'activer l'environnement virtuel !
    pause
    exit /b 1
)
echo.

REM Mettre à jour pip
echo Mise a jour de pip...
python -m pip install --upgrade pip
echo.

REM Installer les dépendances
echo [4/4] Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR: Echec de l'installation des dependances !
    pause
    exit /b 1
)
echo.

REM Vérifier si .env existe
if not exist ".env" (
    echo.
    echo ATTENTION: Le fichier .env n'existe pas !
    echo.
    echo Creer un fichier .env dans le dossier backend avec:
    echo   OPENAI_API_KEY=votre_cle_api_openai
    echo.
    echo Vous pouvez copier env.example et le renommer en .env
    echo.
) else (
    echo Fichier .env trouve.
)
echo.

echo ========================================
echo   Installation terminee avec succes !
echo ========================================
echo.
echo Pour demarrer le backend, utilisez: start_backend.bat
echo.
pause

