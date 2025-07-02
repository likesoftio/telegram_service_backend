from fastapi import APIRouter
from app.workers.tasks import scan_channels_task, generate_ai_response_task

router = APIRouter()

@router.post("/tasks/scan_channels")
def run_scan_channels():
    scan_channels_task.delay()
    return {"status": "started"}

@router.post("/tasks/generate_ai_response/{message_id}")
def run_generate_ai_response(message_id: int):
    generate_ai_response_task.delay(message_id)
    return {"status": "started"} 