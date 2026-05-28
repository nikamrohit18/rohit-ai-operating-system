from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from memory.postgres import init_db
from api.routes import tasks, webhooks, publish, knowledge, voice


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Rohit AI Operating System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(webhooks.router)
app.include_router(publish.router)
app.include_router(knowledge.router)
app.include_router(voice.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "rohit-ai-operating-system", "version": "0.1.0"}
