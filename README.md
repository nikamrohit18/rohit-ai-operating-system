# Rohit AI Operating System

> A personal multi-agent AI ecosystem — research, content creation, SEO, social media, YouTube factory, and a voice-enabled digital twin. Built with Python, FastAPI, LangGraph, and Claude.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-FF6B6B?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-D97706?style=flat-square)
![License](https://img.shields.io/badge/License-Private-gray?style=flat-square)

---

## What This Is

Six specialized AI agents, one API, one orchestrator. I use this daily to:

- **Research** any topic in depth using live web search and PDF analysis
- **Write content** in my voice — LinkedIn posts, blogs, articles
- **Optimize SEO/GEO** for [rohitnikam.tech](https://rohitnikam.tech) — including AI citation optimization
- **Generate social media packages** — Twitter/X threads, Instagram captions, LinkedIn posts
- **Produce YouTube content** — titles, descriptions, script outlines, tags, thumbnail concepts
- **Chat with my digital twin** — RAG-powered, voice-enabled via my cloned ElevenLabs voice

Everything runs through a human approval step before anything publishes publicly. No auto-posting.

---

## Architecture

```
                          ┌─────────────────────────────────┐
                          │         FastAPI Backend          │
                          │         (api.main:app)           │
                          └────────────────┬────────────────┘
                                           │
                          ┌────────────────▼────────────────┐
                          │      LangGraph Orchestrator      │
                          │    routes by task_type / NLP     │
                          └──┬──────┬──────┬──────┬─────┬───┘
                             │      │      │      │     │
               ┌─────────────▼─┐ ┌──▼──┐ ┌▼───┐ ┌▼──┐ ┌▼──────┐ ┌──────────┐
               │   Research    │ │ SEO │ │ DT │ │ C │ │Social │ │ YouTube  │
               │  Tavily+PDF   │ │SERP │ │RAG │ │ o │ │Thread │ │ Scripts  │
               └───────────────┘ └─────┘ └────┘ └───┘ └───────┘ └──────────┘
                                                   │
                          ┌────────────────────────▼────────────────────────┐
                          │               Memory Layer                       │
                          │   PostgreSQL · Redis Cache · Qdrant Vector DB   │
                          └────────────────────────────────────────────────-┘
                                           │
                          ┌────────────────▼────────────────┐
                          │       N8N Approval Pipeline      │
                          │  Telegram notify → approve/reject│
                          └─────────────────────────────────┘
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| LLM | Claude only — Sonnet 4.6 (complex), Haiku (fast/cheap) |
| Agent framework | LangGraph |
| Workflow automation | N8N on Hostinger VPS |
| Backend API | FastAPI |
| Database | PostgreSQL |
| Cache | Redis |
| Vector DB | Qdrant (self-hosted) |
| Embeddings | fastembed — `BAAI/bge-small-en-v1.5` (384-dim, no PyTorch) |
| Web search | Tavily API |
| Voice | ElevenLabs (cloned voice) |
| Frontend | Next.js on Vercel |

---

## Agents

| Agent | `task_type` | Model | What it does |
|---|---|---|---|
| Research | `research` | Sonnet | Deep research via Tavily search + PDF extraction + Claude synthesis |
| Content | `content` | Sonnet | LinkedIn posts, blogs, articles in Rohit's voice |
| SEO | `seo` | Sonnet | SEO + GEO optimization for rohitnikam.tech — keyword research, schema, sitemap |
| Digital Twin | `digital_twin` | Sonnet | RAG-powered Q&A as Rohit — answers questions about his work, stack, services |
| Social | `social` | Sonnet | Twitter/X threads, Instagram captions, LinkedIn posts — one platform or all 4 |
| YouTube | `youtube` | Sonnet | Titles, descriptions, script outlines, tags, thumbnail concepts |

The orchestrator routes by `task_type` first, then falls back to keyword matching on the `input` field.

---

## Project Structure

```
rohit-ai-operating-system/
├── config.py                  # Pydantic settings — reads from .env
├── run.py                     # Entry point: python run.py
├── docker-compose.yml         # Local dev — PostgreSQL (5433) + Redis (6380) + Qdrant
├── docker-compose.prod.yml    # VPS — standard ports 5432 / 6379 / 6333
├── requirements.txt
├── .env.example
├── api/
│   ├── main.py                # FastAPI app with lifespan
│   ├── dependencies.py        # Shared deps (DB, cache, vector)
│   └── routes/
│       ├── tasks.py           # POST /tasks, GET /tasks/{id}
│       ├── publish.py         # Approval pipeline: queue, approve, reject
│       ├── knowledge.py       # CRUD for Digital Twin knowledge base
│       ├── voice.py           # ElevenLabs TTS endpoints
│       └── webhooks.py        # N8N webhook trigger
├── orchestrator/
│   ├── state.py               # OrchestratorState TypedDict
│   ├── router.py              # Routes task_type → agent node
│   └── main.py                # LangGraph StateGraph
├── agents/
│   ├── base.py                # BaseAgent — call_claude() / call_claude_fast()
│   ├── research/agent.py
│   ├── content/agent.py
│   ├── seo/agent.py
│   ├── digital_twin/agent.py
│   ├── social/agent.py
│   └── youtube/agent.py
├── memory/
│   ├── postgres.py            # SQLAlchemy models: Task, KnowledgeItem
│   ├── redis_cache.py         # RedisCache class
│   └── vector_store.py        # Qdrant + fastembed
├── tools/
│   ├── search.py              # Tavily web search
│   ├── pdf.py                 # PDF text extraction via pdfplumber
│   ├── fetch.py               # URL content extractor via Tavily
│   └── voice.py               # ElevenLabs TTS
├── data/
│   └── rohit_knowledge.json   # Digital Twin knowledge base (18 chunks)
├── scripts/
│   └── seed_knowledge.py      # Seeds Qdrant with rohit_knowledge.json
├── deploy/
│   ├── rohit-ai-os.service    # systemd service for gunicorn
│   └── nginx.conf             # Nginx reverse proxy config
├── n8n_workflows/
│   ├── task_trigger.json      # N8N import — replace YOUR_VPS_IP
│   └── publish_pipeline.json  # Approval pipeline with Telegram notify
└── frontend/
    ├── app/page.tsx            # Digital Twin chat UI
    └── lib/api.ts              # API client — askDigitalTwin, pollTask, getVoiceUrl
```

---

## Quick Start (Local Dev)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/rohit-ai-operating-system.git
cd rohit-ai-operating-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Fill in ANTHROPIC_API_KEY (required) and TAVILY_API_KEY

# 4. Start databases
docker-compose up -d

# 5. Seed the Digital Twin knowledge base
python scripts/seed_knowledge.py

# 6. Start the API
python run.py
# API:  http://localhost:8000
# Docs: http://localhost:8000/docs

# 7. (Optional) Start the frontend
cd frontend
npm install
npm run dev
# UI: http://localhost:3000
```

> **Local dev note:** `docker-compose.yml` maps PostgreSQL to port `5433` and Redis to `6380` to avoid conflicts with other local services.

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/tasks/` | Submit a task to an agent |
| `GET` | `/tasks/{task_id}` | Poll task status and output |
| `GET` | `/tasks/` | List recent tasks |
| `POST` | `/webhooks/n8n` | N8N webhook trigger |
| `GET` | `/publish/queue` | Tasks awaiting approval |
| `POST` | `/publish/{id}/approve` | Approve → status becomes `published` |
| `POST` | `/publish/{id}/reject` | Reject → status becomes `rejected` |
| `GET` | `/publish/published` | All published tasks |
| `POST` | `/voice/` | Convert text to speech (MP3) |
| `GET` | `/voice/task/{task_id}` | Synthesize a task's output as speech |
| `GET` | `/knowledge/` | List knowledge base entries |
| `POST` | `/knowledge/` | Add a knowledge chunk |
| `DELETE` | `/knowledge/{id}` | Remove a knowledge chunk |

### Task Payload

```json
{
  "task_type": "research | content | seo | digital_twin | social | youtube",
  "input": "Your prompt here",
  "context": {}
}
```

**Context options by agent:**

```jsonc
// research
{ "search_web": true, "pdf_url": "https://..." }

// content
{ "content_type": "linkedin_post | blog | article", "research_results": "...", "search_web": true }

// seo
{ "target_url": "https://rohitnikam.tech/page", "content": "..." }

// social
{ "platform": "twitter_thread | twitter_post | instagram_post | linkedin_post | all", "research_results": "..." }

// youtube
{ "content_type": "full_package | metadata_only | script_only", "search_web": true }
```

---

## Build Phases

| Phase | What | Status |
|---|---|---|
| 1 | Foundation — FastAPI + LangGraph + PostgreSQL + Redis + Qdrant + N8N skeleton | ✅ Done |
| 2 | Research + Content agents with real tools (Tavily search, PDF extraction) | ✅ Done |
| 3 | SEO/GEO agent + human approval publishing pipeline | ✅ Done |
| 4 | Digital Twin — RAG (Qdrant), ElevenLabs cloned voice, Next.js frontend | ✅ Done |
| 5 | Social media factory + YouTube content factory | ✅ Done |

---

## Deployment (VPS)

The backend runs on a Hostinger VPS. N8N is already running there.

```bash
# On VPS — one-time setup
git clone https://github.com/YOUR_USERNAME/rohit-ai-operating-system.git /opt/rohit-ai-os
cd /opt/rohit-ai-os
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start databases (standard ports on VPS)
docker-compose -f docker-compose.prod.yml up -d

# Set environment variables
cp .env.example .env
nano .env   # fill in all keys

# Seed knowledge base
python scripts/seed_knowledge.py

# Install and start systemd service
sudo mkdir -p /var/log/rohit-ai-os
sudo cp deploy/rohit-ai-os.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rohit-ai-os
sudo systemctl start rohit-ai-os

# Set up Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/rohit-ai-os
sudo ln -s /etc/nginx/sites-available/rohit-ai-os /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# SSL (replace with your email)
sudo certbot --nginx -d api.rohitnikam.tech --email nikamrohit18@gmail.com --agree-tos
```

**Deploy updates:**
```bash
cd /opt/rohit-ai-os && git pull && sudo systemctl restart rohit-ai-os
```

---

## Frontend (Vercel)

```bash
cd frontend
# Set NEXT_PUBLIC_API_URL=https://api.rohitnikam.tech in Vercel env vars
vercel deploy --prod
```

> **Note:** Resolve Next.js CVE-2025-66478 before deploying to production.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `TAVILY_API_KEY` | ✅ | Web search (1000 free/month) |
| `ELEVENLABS_API_KEY` | Phase 4 | ElevenLabs TTS — use key from ElevenAPI workspace |
| `ELEVENLABS_VOICE_ID` | Phase 4 | Your cloned voice ID |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `QDRANT_HOST` | ✅ | Qdrant host (default: localhost) |
| `N8N_WEBHOOK_SECRET` | Optional | Shared secret for N8N webhook auth |

See `.env.example` for all defaults.

---

## Adding a New Agent

1. Create `agents/<name>/agent.py` — class extending `BaseAgent`, module-level `run(state) -> dict`
2. Register node in `orchestrator/main.py` — add to `_ALL_NODES` and import the `run` function
3. Add routing in `orchestrator/router.py` — add to `VALID_AGENTS` and `KEYWORD_MAP`

---

*Built by [Rohit Nikam](https://rohitnikam.tech) · Bangkok, Thailand*
