@echo off
echo ============================================================
echo   Starting RAG System Frontend
echo ============================================================
echo.
echo Changing to frontend directory...
cd frontend

echo.
echo Starting frontend dev server...
echo This will take 5-10 seconds
echo.
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

npm run dev
