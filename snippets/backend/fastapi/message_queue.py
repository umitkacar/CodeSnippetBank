"""Message Queue Integration"""
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
from queue import Queue
import asyncio

app = FastAPI()

class Message(BaseModel):
    topic: str
    payload: dict

message_queue = Queue()

async def process_messages():
    """Background message processor"""
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            print(f"Processing message: {message}")
            await asyncio.sleep(1)
        await asyncio.sleep(0.1)

@app.on_event("startup")
async def startup_event():
    """Start message processor"""
    asyncio.create_task(process_messages())

@app.post("/publish")
async def publish_message(message: Message):
    """Publish message to queue"""
    message_queue.put(message.model_dump())
    return {"message": "Published successfully"}

@app.get("/queue/size")
async def get_queue_size():
    """Get queue size"""
    return {"size": message_queue.qsize()}
