from fastapi import APIRouter, Depends, HTTPException
from memory.postgres import get_session, Task
from api.auth import require_api_key

router = APIRouter(prefix="/publish", tags=["publish"], dependencies=[Depends(require_api_key)])

PUBLISHABLE_TYPES = {"content", "seo"}


@router.get("/queue")
async def get_approval_queue():
    """Return completed content/seo tasks awaiting human approval."""
    session = get_session()
    try:
        tasks = (
            session.query(Task)
            .filter(Task.status == "completed", Task.task_type.in_(PUBLISHABLE_TYPES))
            .order_by(Task.created_at.desc())
            .limit(20)
            .all()
        )
        return [
            {
                "task_id": t.id,
                "task_type": t.task_type,
                "input": t.input,
                "output_preview": (t.output or "")[:500],
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ]
    finally:
        session.close()


@router.get("/published")
async def list_published():
    """Return all published tasks."""
    session = get_session()
    try:
        tasks = (
            session.query(Task)
            .filter(Task.status == "published")
            .order_by(Task.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "task_id": t.id,
                "task_type": t.task_type,
                "input": t.input,
                "output": t.output,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ]
    finally:
        session.close()


@router.get("/{task_id}")
async def get_published_content(task_id: str):
    """Return full content of a specific published task."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
    finally:
        session.close()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "published":
        raise HTTPException(status_code=403, detail=f"Task is '{task.status}', not published")

    return {
        "task_id": task.id,
        "task_type": task.task_type,
        "input": task.input,
        "output": task.output,
        "sources": (task.context or {}).get("sources"),
        "created_at": task.created_at.isoformat(),
    }


@router.post("/{task_id}/approve")
async def approve_task(task_id: str):
    """Approve a completed task for publishing."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status != "completed":
            raise HTTPException(status_code=400, detail=f"Task status is '{task.status}', expected 'completed'")
        task.status = "published"
        session.commit()
        return {"task_id": task_id, "status": "published"}
    finally:
        session.close()


@router.post("/{task_id}/reject")
async def reject_task(task_id: str):
    """Reject a task — sends it back for revision."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status not in ("completed", "published"):
            raise HTTPException(status_code=400, detail=f"Cannot reject task with status '{task.status}'")
        task.status = "rejected"
        session.commit()
        return {"task_id": task_id, "status": "rejected"}
    finally:
        session.close()
