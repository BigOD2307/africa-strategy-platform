@echo off
echo ========================================
echo   Installation Frontend Africa Strategy
echo ========================================
echo.

cd frontend

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Node.js n'est pas installe ou pas dans le PATH !
    echo.
    echo Installez Node.js 18+ depuis https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [1/2] Verification de Node.js...
node --version
npm --version
echo.

REM Installer les dépendances
echo [2/2] Installation des dependances...
npm install
if errorlevel 1 (
    echo ERREUR: Echec de l'installation des dependances !
    pause
    exit /b 1
)
echo.

echo ========================================
echo   Installation terminee avec succes !
echo ========================================
echo.
echo Pour demarrer le frontend, utilisez: start_frontend.bat
echo.
pause

