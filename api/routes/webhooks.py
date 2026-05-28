import hmac
import hashlib
import uuid
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from memory.postgres import get_session, Task
from config import get_settings
from api.routes.tasks import _run_task

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_signature(secret: str, body: bytes, signature: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/n8n")
async def n8n_webhook(request: Request, background_tasks: BackgroundTasks):
    settings = get_settings()
    body = await request.body()

    if settings.n8n_webhook_secret:
        signature = request.headers.get("X-N8N-Signature", "")
        if not signature or not _verify_signature(settings.n8n_webhook_secret, body, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    task_type = payload.get("task_type", "research")
    input_text = payload.get("input", "").strip()
    context = payload.get("context")

    if not input_text:
        raise HTTPException(status_code=400, detail="'input' field is required")

    task_id = str(uuid.uuid4())
    session = get_session()
    try:
        task = Task(id=task_id, task_type=task_type, input=input_text, context=context, status="pending")
        session.add(task)
        session.commit()
    finally:
        session.close()

    background_tasks.add_task(_run_task, task_id, task_type, input_text, context)
    return {"task_id": task_id, "status": "accepted", "message": f"Task queued for agent: {task_type}"}
