"""Task Queue Implementation"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime
import asyncio
from uuid import uuid4, UUID

app = FastAPI()

# Task status enum
class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Models
class Task(BaseModel):
    id: UUID
    type: str
    status: TaskStatus
    data: dict
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    type: str
    data: dict

# Task storage
tasks_db: Dict[UUID, Task] = {}

# Task queue
task_queue: asyncio.Queue = asyncio.Queue()

# Task processor
async def process_task(task: Task):
    """Process a task based on its type"""
    try:
        if task.type == "send_email":
            await asyncio.sleep(2)  # Simulate email sending
            return {"status": "sent", "recipient": task.data.get("to")}

        elif task.type == "generate_report":
            await asyncio.sleep(5)  # Simulate report generation
            return {"status": "generated", "report_id": str(uuid4())}

        elif task.type == "process_image":
            await asyncio.sleep(3)  # Simulate image processing
            return {"status": "processed", "url": "https://example.com/image.jpg"}

        else:
            raise ValueError(f"Unknown task type: {task.type}")

    except Exception as e:
        raise Exception(f"Task processing failed: {str(e)}")

# Worker
async def worker():
    """Background worker to process tasks"""
    while True:
        try:
            task_id = await task_queue.get()
            task = tasks_db.get(task_id)

            if task:
                # Update status
                task.status = TaskStatus.PROCESSING
                task.updated_at = datetime.utcnow()

                # Process task
                try:
                    result = await process_task(task)
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)

                task.updated_at = datetime.utcnow()

            task_queue.task_done()

        except Exception as e:
            print(f"Worker error: {str(e)}")

# Start workers on startup
@app.on_event("startup")
async def startup_event():
    """Start background workers"""
    for _ in range(3):  # Start 3 workers
        asyncio.create_task(worker())

# Endpoints
@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_create: TaskCreate):
    """Create a new task"""
    task_id = uuid4()
    task = Task(
        id=task_id,
        type=task_create.type,
        status=TaskStatus.PENDING,
        data=task_create.data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    tasks_db[task_id] = task
    await task_queue.put(task_id)

    return task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID):
    """Get task status"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return tasks_db[task_id]

@app.get("/tasks/", response_model=List[Task])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    task_type: Optional[str] = None
):
    """List all tasks with optional filtering"""
    tasks = list(tasks_db.values())

    if status:
        tasks = [t for t in tasks if t.status == status]

    if task_type:
        tasks = [t for t in tasks if t.type == task_type]

    return tasks

@app.get("/queue/stats")
async def queue_stats():
    """Get queue statistics"""
    return {
        "total_tasks": len(tasks_db),
        "pending": len([t for t in tasks_db.values() if t.status == TaskStatus.PENDING]),
        "processing": len([t for t in tasks_db.values() if t.status == TaskStatus.PROCESSING]),
        "completed": len([t for t in tasks_db.values() if t.status == TaskStatus.COMPLETED]),
        "failed": len([t for t in tasks_db.values() if t.status == TaskStatus.FAILED]),
        "queue_size": task_queue.qsize()
    }
