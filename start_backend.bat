@echo off
echo ============================================================
echo   Starting RAG System Backend
echo ============================================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting backend server...
echo This may take 10-60 seconds on first start (loading AI models)
echo.
echo Backend will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python main.py serve --no-reload
