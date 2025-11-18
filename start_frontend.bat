@echo off
echo ========================================
echo   Demarrage Frontend Africa Strategy
echo ========================================
echo.

cd frontend

if exist "node_modules" (
    echo Lancement du frontend sur http://localhost:3000
    echo.
    npm run dev
) else (
    echo Installation des dependances...
    npm install
    echo.
    echo Lancement du frontend sur http://localhost:3000
    echo.
    npm run dev
)


