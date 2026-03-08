# Complete Startup Guide - RAG System

## Quick Answer to Your Questions

**Q: How much time does backend take to load?**
- First time: 30-60 seconds (loading models)
- Subsequent starts: 10-20 seconds
- The delay is from loading the sentence-transformers embedding model

**Q: Do I need to install torch every time?**
- **NO!** You only installed torch once (we just did it)
- PyTorch is now permanently installed in your `.venv`
- You'll never need to reinstall it unless you delete `.venv`

**Q: Backend startup time normal?**
- Yes, 10-60 seconds is normal for AI/ML backends
- The embedding model (`all-MiniLM-L6-v2`) needs to load into memory
- This happens once per backend start

---

## Prerequisites (One-Time Setup)

### 1. Python Environment
Your `.venv` is already set up with all dependencies installed including:
- ✓ PyTorch 2.10.0+cpu (CPU-only version, no GPU needed)
- ✓ sentence-transformers
- ✓ FastAPI
- ✓ ChromaDB
- ✓ All other dependencies

### 2. Node.js Environment
Frontend dependencies are already installed in `frontend/node_modules/`

---

## Manual Startup Instructions

### Option A: Using PowerShell (Recommended)

#### Terminal 1 - Backend API
```powershell
# Navigate to project root
cd C:\AskMyDoc

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start backend (will take 10-60 seconds first time)
python main.py serve
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Wait for:** "Application startup complete" message before proceeding

#### Terminal 2 - Frontend
```powershell
# Navigate to frontend directory
cd C:\AskMyDoc\frontend

# Start frontend dev server
npm run dev
```

**Expected Output:**
```
VITE v8.0.0-beta.16  ready in 284 ms
➜  Local:   http://localhost:3000/
```

**Access:** Open browser to http://localhost:3000

---

### Option B: Using Command Prompt (CMD)

#### Terminal 1 - Backend API
```cmd
cd C:\AskMyDoc
.venv\Scripts\activate.bat
python main.py serve
```

#### Terminal 2 - Frontend
```cmd
cd C:\AskMyDoc\frontend
npm run dev
```

---

## Verification Steps

### 1. Check Backend Health
Open a new terminal:
```powershell
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "ask_my_doc_api",
  "database": "healthy"
}
```

### 2. Check Frontend
Open browser to: http://localhost:3000

You should see the RAG System interface with three tabs:
- Query
- Upload
- Metrics

### 3. Run Integration Test
```powershell
cd C:\AskMyDoc
.\.venv\Scripts\Activate.ps1
python test_integration.py
```

**Expected:** 6/6 tests passing

---

## Troubleshooting

### Backend Takes Too Long (>2 minutes)

**Check if it's stuck:**
```powershell
# In the backend terminal, press Ctrl+C to stop
# Then restart:
python main.py serve
```

**If it fails with PyTorch error:**
```powershell
# Verify PyTorch is installed
pip show torch

# Should show: Version: 2.10.0+cpu
# If not found, reinstall:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Frontend Port Already in Use

**Error:** `Port 3000 is already in use`

**Solution:**
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force

# Restart frontend
npm run dev
```

### Backend Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
Stop-Process -Id <PID> -Force

# Restart backend
python main.py serve
```

### Virtual Environment Not Activating

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\.venv\Scripts\Activate.ps1
```

---

## Performance Notes

### Backend Startup Time Breakdown

1. **Python initialization:** 1-2 seconds
2. **FastAPI startup:** 1-2 seconds
3. **Database connection:** 1-2 seconds
4. **ChromaDB initialization:** 2-5 seconds
5. **Loading embedding model:** 5-50 seconds (depends on CPU)
   - First time: Downloads model (~90 MB)
   - Subsequent: Loads from cache

**Total:** 10-60 seconds (normal)

### Why Does It Take Time?

The embedding model (`all-MiniLM-L6-v2`) is a neural network that needs to:
1. Load weights from disk (~90 MB)
2. Initialize PyTorch
3. Allocate memory
4. Prepare for inference

This is **one-time per backend start** and is normal for AI/ML applications.

### How to Speed Up Backend Startup

**Option 1: Keep backend running**
- Don't stop the backend between uses
- It stays fast once loaded

**Option 2: Use minimal API (faster startup)**
```powershell
python minimal_api.py
```
- Starts in 5-10 seconds
- Lighter weight
- Same functionality for basic use

---

## Daily Usage Workflow

### Starting Your Work Session

1. **Open Terminal 1 (Backend):**
   ```powershell
   cd C:\AskMyDoc
   .\.venv\Scripts\Activate.ps1
   python main.py serve
   ```
   Wait for "Application startup complete"

2. **Open Terminal 2 (Frontend):**
   ```powershell
   cd C:\AskMyDoc\frontend
   npm run dev
   ```
   Wait for "Local: http://localhost:3000/"

3. **Open Browser:**
   Navigate to http://localhost:3000

4. **Start Working!**
   - Upload documents
   - Query your data
   - View metrics

### Ending Your Work Session

1. **Stop Frontend:** Press `Ctrl+C` in Terminal 2
2. **Stop Backend:** Press `Ctrl+C` in Terminal 1
3. **Close Terminals**

---

## Quick Commands Reference

### Backend Commands
```powershell
# Start backend
python main.py serve

# Check backend health
curl http://localhost:8000/health

# View backend logs
# (logs appear in terminal where backend is running)
```

### Frontend Commands
```powershell
# Start frontend
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Preview production build
npm run preview
```

### Database Commands
```powershell
# Initialize PostgreSQL tables
python database/db_initializer.py

# Check ChromaDB status
python -c "from vectorstore import get_chroma_client; print(get_chroma_client().get_collection_stats())"
```

### Testing Commands
```powershell
# Run integration test
python test_integration.py

# Run vectorstore test
python test_vectorstore.py

# Run frontend tests
cd frontend
npm test
```

---

## Environment Variables

### Backend (.env in root)
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=AskMyDocLOG

# ChromaDB
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION_NAME=ask_my_doc

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2

# API Keys (optional)
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Frontend (.env.local in frontend/)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=60000
```

---

## System Requirements

### Minimum
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 2 GB free space
- **OS:** Windows 10/11

### Recommended
- **CPU:** 4+ cores
- **RAM:** 8+ GB (faster model loading)
- **Disk:** 5 GB free space
- **SSD:** Recommended for faster model loading

---

## FAQ

**Q: Why does backend use so much RAM?**
- The embedding model loads into memory (~500 MB)
- ChromaDB indexes are in memory
- This is normal for AI/ML applications

**Q: Can I use GPU to speed up?**
- Yes, but requires CUDA-enabled GPU
- Install GPU version: `pip install torch torchvision torchaudio`
- Current CPU version works fine for most use cases

**Q: Do I need internet connection?**
- First run: Yes (downloads embedding model)
- Subsequent runs: No (uses cached model)

**Q: Can I run on a different port?**
- Backend: Edit `main.py` or use `--port` flag
- Frontend: Edit `frontend/vite.config.ts` port setting

**Q: How do I update dependencies?**
```powershell
# Backend
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update
```

---

## Next Steps

1. **Start both services** using instructions above
2. **Open browser** to http://localhost:3000
3. **Upload a document** via Upload tab
4. **Query your data** via Query tab
5. **View metrics** via Metrics tab

---

## Support Files

- `test_integration.py` - Verify system health
- `SYSTEM_STATUS.md` - Current system status
- `BACKEND_PYTORCH_ISSUE.md` - PyTorch troubleshooting
- `minimal_api.py` - Lightweight backend alternative

---

## Summary

✓ **No need to reinstall torch** - it's permanently in `.venv`
✓ **Backend startup: 10-60 seconds** - normal for AI apps
✓ **Two terminals needed** - one for backend, one for frontend
✓ **Access at http://localhost:3000** - once both are running
✓ **Keep backend running** - for faster subsequent uses
