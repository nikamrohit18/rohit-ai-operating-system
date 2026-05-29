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
| Frontend | Next.js 16 on Vercel |
| Voice | ElevenLabs (cloned voice, model: eleven_turbo_v2_5) |

## Live URLs

| Service | URL |
|---|---|
| API | https://api.rohitnikam.tech |
| Digital Twin | https://twin.rohitnikam.tech |
| API Docs | https://api.rohitnikam.tech/docs |
| N8N | https://n8n.rohitnikam.tech |

## Project Structure

```
rohit-ai-operating-system/
├── config.py                  # Pydantic settings — reads from .env (extra="ignore")
├── run.py                     # Local dev entry point: python run.py
├── Dockerfile                 # Production Docker image
├── docker-compose.yml         # Local dev — PostgreSQL (5433) + Redis (6380) + Qdrant
├── docker-compose.prod.yml    # VPS with standard ports (not used — see docker-compose.vps.yml)
├── docker-compose.vps.yml     # VPS production — Traefik-integrated, all 4 services
├── requirements.txt
├── .env.example
├── api/
│   ├── main.py                # FastAPI app with lifespan + CORS middleware
│   ├── dependencies.py        # Shared FastAPI deps (DB, cache, vector)
│   └── routes/
│       ├── tasks.py           # POST /tasks, GET /tasks/{id}, GET /tasks/
│       ├── webhooks.py        # POST /webhooks/n8n — N8N calls this
│       ├── publish.py         # GET /publish/queue, POST /publish/{id}/approve|reject
│       ├── knowledge.py       # CRUD for Digital Twin knowledge base
│       └── voice.py           # ElevenLabs TTS endpoints
├── orchestrator/
│   ├── state.py               # OrchestratorState TypedDict (LangGraph)
│   ├── router.py              # Routes task_type string → agent node name
│   └── main.py                # LangGraph StateGraph — builds & exposes `orchestrator`
├── agents/
│   ├── base.py                # BaseAgent ABC — call_claude() / call_claude_fast()
│   ├── research/agent.py      # Tavily search + PDF + Claude synthesis
│   ├── content/agent.py       # LinkedIn posts, blogs, articles in Rohit's voice
│   ├── seo/agent.py           # SEO + GEO agent for rohitnikam.tech
│   ├── digital_twin/agent.py  # RAG-powered Q&A as Rohit
│   ├── social/agent.py        # Twitter/X threads, Instagram, LinkedIn packages
│   └── youtube/agent.py       # Titles, descriptions, script outlines, tags
├── memory/
│   ├── postgres.py            # SQLAlchemy models: Task, KnowledgeItem + init_db()
│   ├── redis_cache.py         # RedisCache class (get/set/delete/exists)
│   └── vector_store.py        # VectorStore — Qdrant + fastembed (uses query_points())
├── tools/
│   ├── search.py              # Tavily web search
│   ├── pdf.py                 # PDF text extraction via pdfplumber
│   ├── fetch.py               # URL content extractor via Tavily
│   └── voice.py               # ElevenLabs TTS — strips markdown/emojis before synthesis
├── data/
│   └── rohit_knowledge.json   # 18 knowledge chunks for Digital Twin RAG
├── scripts/
│   └── seed_knowledge.py      # Seeds Qdrant with rohit_knowledge.json
├── deploy/
│   ├── rohit-ai-os.service    # systemd service (reference only — Docker used in prod)
│   └── nginx.conf             # Nginx config (reference only — Traefik used in prod)
├── n8n_workflows/
│   ├── task_trigger.json      # Webhook trigger → POST /tasks/ — live at /webhook/ai-task
│   └── publish_pipeline.json  # Approval pipeline — polls queue, Telegram notify, approve/reject
└── frontend/
    ├── app/page.tsx            # Digital Twin chat UI with voice playback
    ├── app/layout.tsx          # Metadata + favicon
    ├── app/globals.css         # Tailwind + Google Fonts (@import must be first)
    └── lib/api.ts              # askDigitalTwin, pollTask, getVoiceUrl
```

## Running Locally

```bash
# 1. Start databases (uses ports 5433/6380 to avoid conflicts with other local projects)
docker-compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
copy .env.example .env   # then fill in ANTHROPIC_API_KEY and TAVILY_API_KEY

# 4. Seed the Digital Twin knowledge base
python scripts/seed_knowledge.py

# 5. Start the API server
python run.py
# API:  http://localhost:8000
# Docs: http://localhost:8000/docs

# 6. (Optional) Start the frontend
cd frontend && npm install && npm run dev
# UI: http://localhost:3000
```

> **Local port note:** `docker-compose.yml` maps PostgreSQL → 5433 and Redis → 6380 to avoid conflicts with other Docker projects on the same machine. The `.env` must use these ports locally.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/tasks/` | Submit a task to an agent |
| GET | `/tasks/{task_id}` | Poll task status and output |
| GET | `/tasks/` | List recent tasks |
| POST | `/webhooks/n8n` | N8N webhook trigger |
| GET | `/publish/queue` | List completed content/seo tasks awaiting approval |
| POST | `/publish/{id}/approve` | Approve → status becomes `published` |
| POST | `/publish/{id}/reject` | Reject → status becomes `rejected` |
| GET | `/publish/published` | List all published tasks |
| GET | `/publish/{id}` | Get full content of a published task |
| POST | `/voice/` | Convert text to speech (MP3) |
| GET | `/voice/task/{task_id}` | Synthesize a task's output as speech |
| GET | `/knowledge/` | List knowledge base entries |
| POST | `/knowledge/` | Add a knowledge chunk |
| DELETE | `/knowledge/{id}` | Remove a knowledge chunk |

### Task payload

```json
{
  "task_type": "research | content | seo | digital_twin | social | youtube",
  "input": "Your prompt here",
  "context": {}
}
```

**Context options by agent:**
```jsonc
// social
{ "platform": "twitter_thread | twitter_post | instagram_post | linkedin_post | all" }

// youtube
{ "content_type": "full_package | metadata_only | script_only", "search_web": true }

// content
{ "content_type": "linkedin_post | blog | article", "research_results": "..." }

// seo
{ "target_url": "https://rohitnikam.tech/page", "content": "..." }
```

## Agents

| Agent | task_type | Model | Purpose |
|---|---|---|---|
| Research | `research` | Sonnet | Deep research on any topic |
| Content | `content` | Sonnet | LinkedIn posts, blogs, articles in Rohit's voice |
| SEO | `seo` | Sonnet | SEO/GEO optimization for rohitnikam.tech |
| Digital Twin | `digital_twin` | Sonnet | RAG-powered Q&A as Rohit + ElevenLabs voice |
| Social | `social` | Sonnet | Twitter/X threads, Instagram captions, LinkedIn posts |
| YouTube | `youtube` | Sonnet | Video titles, descriptions, script outlines, tags |

The orchestrator routes by `task_type` first, then falls back to keyword matching on the `input` text.

## Adding a New Agent

1. Create `agents/<name>/agent.py` with a class extending `BaseAgent` and a module-level `run(state) -> dict` function
2. Add to `_ALL_NODES` in `orchestrator/main.py` and import the `run` function
3. Add routing in `orchestrator/router.py`: add to `VALID_AGENTS` and `KEYWORD_MAP`

## Coding Conventions

- **One LLM only:** Use `self.call_claude()` (Sonnet) for complex tasks, `self.call_claude_fast()` (Haiku) for cheap tasks — never introduce OpenAI
- **Agent node functions return dicts** with only the fields being updated (LangGraph merges them)
- **No auto-publishing:** All pipelines include a human approval step via N8N before anything posts publicly
- **Self-hosted first:** Prefer tools that run on the VPS before adding paid SaaS
- **No comments explaining what code does** — only add a comment when the WHY is non-obvious
- **Pydantic Settings:** `extra = "ignore"` is required — docker-compose passes DB_PASSWORD which is not a Settings field

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `TAVILY_API_KEY` | ✅ | Web search (1000 free/month) |
| `ELEVENLABS_API_KEY` | Voice | Use key from ElevenAPI workspace (not ElevenCreative) |
| `ELEVENLABS_VOICE_ID` | Voice | Rohit's cloned voice: `F2TzKUqmFUabqzgv2wxy` |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `QDRANT_HOST` | ✅ | Qdrant host (default: localhost) |
| `N8N_WEBHOOK_SECRET` | Optional | Shared secret for N8N webhook auth |

## Build Phases

| Phase | What | Status |
|---|---|---|
| 1 | Foundation — FastAPI + LangGraph + DB + N8N skeleton | ✅ Done |
| 2 | Research + Content agents with real tools (Tavily, PDF) | ✅ Done |
| 3 | SEO agent + auto-publishing pipeline | ✅ Done |
| 4 | Digital Twin — RAG + ElevenLabs voice + Next.js frontend | ✅ Done |
| 5 | Social media + YouTube factory | ✅ Done |

## Deployment (VPS)

The backend runs on Hostinger VPS (`76.13.197.149`) alongside N8N. Traefik handles SSL and routing for both.

```bash
# One-time setup on VPS
git clone https://github.com/nikamrohit18/rohit-ai-operating-system.git /opt/rohit-ai-os
cd /opt/rohit-ai-os
nano .env   # fill in all keys (no leading spaces, no @ in DB_PASSWORD)
docker compose -f docker-compose.vps.yml up -d --build
docker exec rohit-ai-os-api-1 python scripts/seed_knowledge.py
```

```bash
# Deploy updates (run on VPS)
cd /opt/rohit-ai-os && git pull && docker compose -f docker-compose.vps.yml up -d --build api
```

**Traefik integration:** The `api` service joins the `n8n_default` network and uses `mytlschallenge` cert resolver — same as N8N. CORS is handled via Traefik middleware labels in `docker-compose.vps.yml`.

## Frontend (Vercel)

```bash
cd frontend
npx vercel --prod
# NEXT_PUBLIC_API_URL=https://api.rohitnikam.tech (set in Vercel env vars)
```

Custom domain: `twin.rohitnikam.tech` → Vercel A record `76.76.21.21`

## N8N Workflows

Both workflows are imported and active at **n8n.rohitnikam.tech**. URLs use the production domain — no placeholders remain.

### Workflow 1: Task Trigger (`task_trigger.json`)

Exposes a webhook that forwards any task to the API.

- **Webhook URL:** `https://n8n.rohitnikam.tech/webhook/ai-task`
- **Method:** POST
- **Payload:** `{ "task_type": "...", "input": "...", "context": {} }`

Chain: `Webhook → Call AI OS API → Respond to Webhook`

### Workflow 2: Content Approval Pipeline (`publish_pipeline.json`)

Polls the approval queue every 15 minutes. Sends a Telegram notification for each completed content/seo task with approve/reject links.

Chain: `Poll Every 15 Min → Fetch Approval Queue → Send Telegram Notification`

Approve/reject chains (separate triggers in same workflow):
`Approve Webhook → Call Approve API → Respond Approved`
`Reject Webhook → Call Reject API → Respond Rejected`

**Approve URL:** `https://n8n.rohitnikam.tech/webhook/approve?taskid={task_id}`
**Reject URL:** `https://n8n.rohitnikam.tech/webhook/reject?taskid={task_id}`

### N8N Setup Gotchas

- **Query param is `taskid` (no underscore)** — the Telegram links use `?taskid=` and the Call API nodes reference `$json.query.taskid`. Using `task_id` (with underscore) breaks it.
- **Approve/Reject API nodes must use POST** — clicking a Telegram link opens a browser (GET). The N8N webhook receives the GET and forwards it as POST to the API. If the HTTP Request node defaults to GET, the API returns 405.
- **No IF node or SplitInBatches in the pipeline** — the "Has Pending Items?" IF node caused routing failures (items went through false branch). The "Loop Over Tasks" SplitInBatches node caused "different path" errors. Both were removed. N8N handles empty arrays natively — if the queue is empty, downstream nodes don't execute.
- **Telegram links point to N8N, not the API directly** — clicking a link triggers the N8N webhook which calls the API as POST. Direct links to the API would fail (405) since approve/reject are POST-only.
- **Telegram bot token** = Access Token in N8N credential. Chat ID = `1292664278` (Rohit's personal chat).
