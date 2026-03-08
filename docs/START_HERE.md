# 🚀 Quick Start - RAG System

## Fastest Way to Start (Windows)

### Step 1: Start Backend
**Double-click:** `start_backend.bat`

Wait for this message:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```
⏱️ Takes 10-60 seconds (loading AI models)

### Step 2: Start Frontend  
**Double-click:** `start_frontend.bat`

Wait for this message:
```
➜  Local:   http://localhost:3000/
```
⏱️ Takes 5-10 seconds

### Step 3: Open Browser
Navigate to: **http://localhost:3000**

---

## Manual Start (PowerShell)

### Terminal 1 - Backend
```powershell
cd C:\AskMyDoc
.\.venv\Scripts\Activate.ps1
python main.py serve
```

### Terminal 2 - Frontend
```powershell
cd C:\AskMyDoc\frontend
npm run dev
```

---

## What You Need to Know

### ✅ One-Time Setup (Already Done)
- ✓ Python virtual environment created
- ✓ PyTorch installed (CPU version)
- ✓ All dependencies installed
- ✓ Frontend dependencies installed

### ⏱️ Startup Times
- **Backend:** 10-60 seconds (first time loads AI model)
- **Frontend:** 5-10 seconds
- **Subsequent starts:** Same time (no reinstall needed)

### 🔄 Do I Need to Reinstall Anything?
**NO!** Everything is installed in `.venv` and `frontend/node_modules/`

You only need to:
1. Start backend
2. Start frontend
3. Use the application

---

## Verify Everything Works

Run the integration test:
```powershell
cd C:\AskMyDoc
.\.venv\Scripts\Activate.ps1
python test_integration.py
```

**Expected:** 6/6 tests passing

---

## Access Points

| Service | URL | Status Check |
|---------|-----|--------------|
| Frontend | http://localhost:3000 | Open in browser |
| Backend API | http://localhost:8000 | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs | Interactive API documentation |

---

## Features Available

### 📤 Upload Documents
- Go to **Upload** tab
- Drag & drop or click to upload
- Supports: PDF, Markdown (.md), Text (.txt)
- Max size: 10 MB per file

### 🔍 Query Your Data
- Go to **Query** tab
- Type your question
- Configure options (hybrid search, reranker, top-K)
- Get AI-generated answers with sources

### 📊 View Metrics
- Go to **Metrics** tab
- See system performance
- Monitor vector store size
- Check cache statistics

---

## Troubleshooting

### Backend Won't Start
```powershell
# Check if PyTorch is installed
pip show torch

# Should show: Version: 2.10.0+cpu
# If not, reinstall:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Port Already in Use
```powershell
# Backend (port 8000)
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force

# Frontend (port 3000)
netstat -ano | findstr :3000
Stop-Process -Id <PID> -Force
```

### Need More Help?
See: `STARTUP_GUIDE.md` for detailed instructions

---

## Stop the Services

Press **Ctrl+C** in each terminal window

---

## Summary

1. **Double-click** `start_backend.bat` → Wait 10-60 seconds
2. **Double-click** `start_frontend.bat` → Wait 5-10 seconds  
3. **Open browser** to http://localhost:3000
4. **Start using** the RAG system!

**No reinstallation needed** - everything is already set up! 🎉
