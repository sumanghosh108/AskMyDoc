# RAG System - Retrieval-Augmented Generation

Production-grade RAG system with React frontend, FastAPI backend, ChromaDB vector store, and PostgreSQL logging.

##  Quick Start

### Fastest Way (Windows)
1. **Double-click:** `start_backend.bat` → Wait 10-60 seconds
2. **Double-click:** `start_frontend.bat` → Wait 5-10 seconds
3. **Open browser:** http://localhost:3000

### Manual Start
```powershell
# Terminal 1 - Backend
cd C:\AskMyDoc
.\.venv\Scripts\Activate.ps1
python main.py serve

# Terminal 2 - Frontend
cd C:\AskMyDoc\frontend
npm run dev
```

##  Features

### Frontend (http://localhost:3000)
- **Query Interface** - Ask questions, get AI-generated answers
- **Document Upload** - Drag & drop PDF, Markdown, or text files
- **Metrics Dashboard** - Monitor system performance
- **Responsive Design** - Works on desktop and mobile

### Backend (http://localhost:8000)
- **RESTful API** - FastAPI with automatic documentation
- **Vector Search** - Semantic search using ChromaDB
- **AI Embeddings** - sentence-transformers (all-MiniLM-L6-v2)
- **PostgreSQL Logging** - Query and error tracking


##  Architecture

```
Browser (localhost:3000)
    ↓
Frontend (React + Vite)
    ↓ HTTP API
Backend (FastAPI)
    ↓
ChromaDB (Vector Store) + PostgreSQL (Logs)
```

##  Tech Stack

### Frontend
- React 19.2
- TypeScript 5.9
- Vite 8.0
- TailwindCSS 4.2
- Zustand (state management)
- Axios (HTTP client)

### Backend
- Python 3.12
- FastAPI
- PyTorch 2.10.0+cpu
- sentence-transformers
- ChromaDB
- PostgreSQL

##  Configuration

### Ports
- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432

### Environment Files
- Backend: `.env` (root directory)
- Frontend: `frontend/.env.local`

##  Troubleshooting

### Backend takes too long?
- **Normal:** 10-60 seconds (loading AI models)
- **First time:** May download model (~90 MB)
- **Subsequent:** Loads from cache

##  API Documentation

Once backend is running, visit:
- **Interactive docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

##  Project Structure

```
C:\AskMyDoc\
├── start_backend.bat          # Start backend
├── start_frontend.bat         # Start frontend
├── test_integration.py        # Integration tests
├── .venv\                     # Python environment
├── frontend\                  # React application
├── src\                       # Backend source
├── vectorstore\               # ChromaDB package
├── database\                  # PostgreSQL package
└── chroma_db\                 # Vector database storage
```

##  Key Points

- **PyTorch is permanent** - Installed in `.venv`, no need to reinstall
- **Keep backend running** - Faster for subsequent uses

##  Usage

1. **Upload documents** via Upload tab
2. **Query your data** via Query tab
3. **View metrics** via Metrics tab

##  License

MIT License

##  Ready to Use!

Everything is set up. Just start the services and begin using your RAG system!

```powershell
# Start backend
start_backend.bat

# Start frontend  
start_frontend.bat

# Open browser
http://localhost:3000
```

**Enjoy!** 
