# Deployment Guide — AskMyDoc

**Backend:** Render (Docker + Persistent Disk)
**Frontend:** Vercel (Static Site)
**Database:** Supabase (Managed PostgreSQL)
**LLM:** Groq (Free Tier)

---

## Prerequisites

- GitHub repository with your code pushed
- Accounts on: [Render](https://render.com), [Vercel](https://vercel.com), [Supabase](https://supabase.com)
- Supabase project already created with migration SQL applied

---

## Step 1: Supabase — Create Tables

1. Go to [Supabase Dashboard](https://supabase.com/dashboard) → your project
2. Open **SQL Editor**
3. Paste the contents of `database/supabase_migration.sql`
4. Click **Run**
5. Verify: go to **Table Editor** — you should see 6 `rag_*` tables

---

## Step 2: Render — Deploy Backend

### Option A: Blueprint (Automatic)

1. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
2. Connect your GitHub repo
3. Render auto-detects `render.yaml`
4. Set the secret environment variables when prompted:
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_ANON_KEY`
5. Click **Apply**

### Option B: Manual Setup

1. Go to Render → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `askmydoc-api` |
| **Runtime** | Docker |
| **Dockerfile Path** | `./Dockerfile` |
| **Plan** | Starter ($7/mo) or Free |
| **Region** | Oregon (or nearest) |
| **Health Check Path** | `/health` |

4. **Add Disk:**
   - Mount Path: `/data`
   - Size: 1 GB (increase as needed)

5. **Environment Variables:**

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `gsk_uCFcNydT...` (your key) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` |
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGci...` (your key) |
| `SUPABASE_ANON_KEY` | `sb_publishable_...` (your key) |
| `CHROMA_PERSIST_DIR` | `/data/chroma_db` |
| `CHROMA_COLLECTION_NAME` | `ask_my_doc` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| `CHUNK_SIZE` | `600` |
| `CHUNK_OVERLAP` | `100` |
| `TOP_K` | `5` |
| `TOP_K_INITIAL` | `20` |
| `MAX_CONTEXT_TOKENS` | `4000` |
| `CACHE_ENABLED` | `false` |

6. Click **Create Web Service**

### First Deploy Notes
- First build takes **10-15 minutes** (installs PyTorch + sentence-transformers)
- First request takes **30-60 seconds** (downloads embedding/reranker models)
- Subsequent requests are fast (models cached on disk at `/data`)
- Verify at: `https://askmydoc-api.onrender.com/health`

---

## Step 3: Vercel — Deploy Frontend

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) → **Add New** → **Project**
2. Import your GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Framework** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

4. **Environment Variables:**

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://askmydoc-api.onrender.com` |
| `VITE_API_TIMEOUT` | `60000` |

   > Replace the URL with your actual Render backend URL from Step 2.

5. Click **Deploy**

### After Deploy
- Your frontend will be at: `https://askmydoc-frontend.vercel.app` (or custom domain)
- Test: open the URL → Query tab → ask a question

---

## Step 4: Verify Everything Works

1. **Health check:** `curl https://askmydoc-api.onrender.com/health`
   ```json
   {"status":"ok","service":"ask_my_doc_api","version":"2.0.0","database":"healthy"}
   ```

2. **Upload a document** via the Upload tab on the frontend

3. **Ask a question** via the Query tab

4. **Check Supabase** → Table Editor → `rag_query_logs` — you should see query logs

---

## Architecture Diagram

```
┌──────────────────────┐     HTTPS     ┌──────────────────────────────┐
│   Vercel (Frontend)  │ ──────────>   │   Render (Backend)           │
│   React + Vite       │               │   FastAPI + uvicorn          │
│                      │   /api/v1/*   │                              │
└──────────────────────┘               │   ┌──────────────────────┐   │
                                       │   │ ChromaDB (persistent)│   │
                                       │   │ mounted at /data     │   │
                                       │   └──────────────────────┘   │
                                       │                              │
                                       │   ┌──────────────┐          │
                                       │   │ Groq API     │ (LLM)   │
                                       │   └──────────────┘          │
                                       └──────────────┬───────────────┘
                                                      │
                                                      │ HTTPS
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │   Supabase (PostgreSQL)      │
                                       │   Query logs, error logs,    │
                                       │   metrics, analytics         │
                                       └──────────────────────────────┘
```

---

## Costs

| Service | Plan | Cost |
|---------|------|------|
| **Render** (backend) | Starter | $7/mo (Free available but sleeps after inactivity) |
| **Render** Disk | 1 GB | Included with Starter |
| **Vercel** (frontend) | Hobby | Free |
| **Supabase** | Free | Free (500 MB DB, 50k rows) |
| **Groq** | Free | Free (30 req/min, 14.4k tokens/min) |
| **Total** | | **$7/mo** (or $0 with Render free tier) |

---

## Troubleshooting

### Backend takes forever to start
The first cold start downloads ~350MB of ML models (sentence-transformers, cross-encoder). These are cached to the persistent disk at `/data`. Subsequent starts are faster.

### CORS errors in browser console
Make sure `VITE_API_BASE_URL` on Vercel points to the exact Render URL (with `https://`, no trailing slash).

### Render free tier spins down
Free tier services sleep after 15 minutes of inactivity. First request after sleep takes ~60s. Use Starter ($7/mo) for always-on.

### Supabase "relation does not exist"
Run the migration SQL in `database/supabase_migration.sql` via Supabase SQL Editor.

### Groq rate limits
Free tier: 30 requests/minute. If you hit limits, add retry logic or upgrade to paid.
