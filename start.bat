@echo off
echo Starte CDMS...

echo [1/2] Backend starten...
start "CDMS Backend" cmd /k "cd backend && venv\Scripts\uvicorn app.main:app --reload --port 8000"

timeout /t 2

echo [2/2] Frontend starten...
start "CDMS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo CDMS laeuft!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
