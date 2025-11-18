@echo off
echo ========================================
echo   Demarrage Backend Africa Strategy
echo ========================================
echo.

cd backend

if exist "venv\Scripts\python.exe" (
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
    echo.
    echo Lancement du backend sur http://localhost:8000
    echo.
    python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
) else (
    echo ERREUR: Environnement virtuel non trouve !
    echo.
    echo Creer un environnement virtuel avec:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
)

