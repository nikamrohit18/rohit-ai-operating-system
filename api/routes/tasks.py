import uuid
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from orchestrator.main import orchestrator
from memory.postgres import get_session, Task
from api.auth import require_api_key

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    task_type: str
    input: str
    context: Optional[dict] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
    output: Optional[str] = None
    sources: Optional[list[str]] = None


def _run_task(task_id: str, task_type: str, input_text: str, context: Optional[dict]):
    session = get_session()
    try:
        result = orchestrator.invoke({
            "task_id": task_id,
            "task_type": task_type,
            "input": input_text,
            "context": context or {},
            "output": None,
            "status": "running",
            "error": None,
            "sources": None,
            "messages": [],
        })
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = result.get("status", "completed")
            task.output = result.get("output") or result.get("error")
            sources = result.get("sources")
            if sources:
                task.context = {**(task.context or {}), "sources": sources}
            session.commit()
    except Exception as e:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.output = str(e)
            session.commit()
    finally:
        session.close()


@router.post("/", response_model=TaskResponse, status_code=202, dependencies=[Depends(require_api_key)])
async def create_task(payload: TaskCreate, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    session = get_session()
    try:
        task = Task(
            id=task_id,
            task_type=payload.task_type,
            input=payload.input,
            context=payload.context,
            status="pending",
        )
        session.add(task)
        session.commit()
    finally:
        session.close()

    background_tasks.add_task(_run_task, task_id, payload.task_type, payload.input, payload.context)
    return TaskResponse(task_id=task_id, status="pending")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
    finally:
        session.close()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    sources = (task.context or {}).get("sources")
    return TaskResponse(task_id=task.id, status=task.status, output=task.output, sources=sources)


@router.get("/", response_model=list[TaskResponse], dependencies=[Depends(require_api_key)])
async def list_tasks(limit: int = 20):
    session = get_session()
    try:
        tasks = session.query(Task).order_by(Task.created_at.desc()).limit(limit).all()
    finally:
        session.close()

    return [
        TaskResponse(
            task_id=t.id,
            status=t.status,
            output=t.output,
            sources=(t.context or {}).get("sources"),
        )
        for t in tasks
    ]
