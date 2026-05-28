# Rohit AI Operating System

Personal AI OS for Rohit Nikam — multi-agent ecosystem for content creation, research, SEO, social media, YouTube, and a digital twin at rohitnikam.tech.

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| LLM | Claude only — Sonnet 4.6 (complex), Haiku (cheap/fast) |
| Agent framework | LangGraph |
| Workflow automation | N8N on Hostinger VPS |
| Backend API | FastAPI |
| Database | PostgreSQL |
| Cache | Redis |
| Vector DB | Qdrant (self-hosted) |
| Embeddings | fastembed — `BAAI/bge-small-en-v1.5` (384-dim, no PyTorch) |
| Frontend (Phase 4) | Next.js on Vercel |
| Voice (Phase 4) | ElevenLabs |

## Project Structure

```
rohit-ai-operating-system/
├── config.py                  # Pydantic settings — reads from .env
├── run.py                     # Entry point: python run.py
├── docker-compose.yml         # PostgreSQL + Redis + Qdrant (local dev)
├── requirements.txt
├── .env.example
├── api/
│   ├── main.py                # FastAPI app with lifespan (calls init_db)
│   ├── dependencies.py        # Shared FastAPI deps (DB, cache, vector)
│   └── routes/
│       ├── tasks.py           # POST /tasks, GET /tasks/{id}, GET /tasks/
│       ├── webhooks.py        # POST /webhooks/n8n — N8N calls this
│       └── publish.py         # GET /publish/queue, POST /publish/{id}/approve|reject
├── orchestrator/
│   ├── state.py               # OrchestratorState TypedDict (LangGraph)
│   ├── router.py              # Routes task_type string → agent node name
│   └── main.py                # LangGraph StateGraph — builds & exposes `orchestrator`
├── memory/
│   ├── postgres.py            # SQLAlchemy models: Task, KnowledgeItem + init_db()
│   ├── redis_cache.py         # RedisCache class (get/set/delete/exists)
│   └── vector_store.py        # VectorStore class — Qdrant + fastembed
├── tools/
│   ├── search.py              # Tavily web search — search_web() + format_search_results()
│   ├── pdf.py                 # PDF text extraction — extract_pdf_text(path_or_url)
│   └── fetch.py               # URL content extractor — extract_url_content(url) via Tavily
├── agents/
│   ├── base.py                # BaseAgent ABC — call_claude() / call_claude_fast()
│   ├── research/agent.py      # Research agent — Tavily search + PDF + Claude synthesis
│   ├── content/agent.py       # Content agent — accepts research_results context
│   ├── seo/agent.py           # SEO + GEO agent for rohitnikam.tech
│   └── digital_twin/agent.py  # Rohit's AI digital twin
└── n8n_workflows/
    ├── task_trigger.json      # Import into N8N — replace YOUR_VPS_IP
    └── publish_pipeline.json  # Approval pipeline — polls queue, Telegram notify, approve/reject
```

## Running Locally

```bash
# 1. Start databases
docker-compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
copy .env.example .env   # then fill in ANTHROPIC_API_KEY

# 4. Start the API server
python run.py
# Server runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/tasks/` | Submit a task to an agent |
| GET | `/tasks/{task_id}` | Poll task status and output |
| GET | `/tasks/` | List recent tasks |
| POST | `/webhooks/n8n` | N8N webhook trigger |
| GET | `/publish/queue` | List completed content/seo tasks awaiting approval |
| POST | `/publish/{id}/approve` | Approve a task → status becomes `published` |
| POST | `/publish/{id}/reject` | Reject a task → status becomes `rejected` |
| GET | `/publish/published` | List all published tasks |
| GET | `/publish/{id}` | Get full content of a published task |

### Task payload

```json
{
  "task_type": "research | content | seo | digital_twin | social | youtube",
  "input": "Your prompt here",
  "context": { "content_type": "linkedin_post" }
}
```

## Agents

| Agent | task_type | Model | Purpose |
|---|---|---|---|
| Research | `research` | Sonnet | Deep research on any topic |
| Content | `content` | Sonnet | LinkedIn posts, blogs, articles in Rohit's voice |
| SEO | `seo` | Sonnet | SEO/GEO optimization for rohitnikam.tech |
| Digital Twin | `digital_twin` | Sonnet | Represents Rohit in chat/voice Q&A |
| Social | `social` | Sonnet | Twitter/X threads, Instagram captions, LinkedIn posts |
| YouTube | `youtube` | Sonnet | Video titles, descriptions, script outlines, tags |

The orchestrator routes by `task_type` first, then falls back to keyword matching on the `input` text.

## Adding a New Agent

1. Create `agents/<name>/agent.py` with a class extending `BaseAgent` and a module-level `run(state) -> dict` function
2. Add the node to `orchestrator/main.py`: `graph.add_node("<name>", <name>_run)` and wire edges
3. Add routing in `orchestrator/router.py`: add to `VALID_AGENTS` and `KEYWORD_MAP`

## Coding Conventions

- **One LLM only:** Use `self.call_claude()` (Sonnet) for complex tasks, `self.call_claude_fast()` (Haiku) for cheap tasks — never introduce OpenAI
- **Agent node functions return dicts** with only the fields being updated (LangGraph merges them)
- **No auto-publishing:** All pipelines include a human approval step via N8N before anything posts publicly
- **Self-hosted first:** Prefer tools that run on the VPS before adding paid SaaS
- **No comments explaining what code does** — only add a comment when the WHY is non-obvious

## Environment Variables

See `.env.example` for all variables. Required: `ANTHROPIC_API_KEY`. Everything else has defaults for local dev.

## Build Phases

| Phase | What | Status |
|---|---|---|
| 1 | Foundation — FastAPI + LangGraph + DB + N8N skeleton | ✅ Done |
| 2 | Research + Content agents with real tools (Tavily, PDF) | ✅ Done |
| 3 | SEO agent + auto-publishing pipeline | ✅ Done |
| 4 | Digital Twin — RAG + voice on rohitnikam.tech | ✅ Done |
| 5 | Social media + YouTube factory | ✅ Done |

## Deployment (VPS)

The backend (FastAPI + PostgreSQL + Redis + Qdrant) runs on Hostinger VPS.
N8N is already running there. In Phase 4, the frontend (Next.js) goes on Vercel free tier.

```bash
# On VPS — run databases via docker-compose, then:
gunicorn api.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
