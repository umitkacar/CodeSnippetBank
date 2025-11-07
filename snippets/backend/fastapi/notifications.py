"""Push Notifications"""
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import List, Dict
import asyncio

app = FastAPI()

class Notification(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

# Store active WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for push notifications"""
    await websocket.accept()

    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections[user_id].remove(websocket)

@app.post("/send-notification")
async def send_notification(notification: Notification):
    """Send notification to user"""
    if notification.user_id in active_connections:
        for connection in active_connections[notification.user_id]:
            await connection.send_json(notification.model_dump())

    return {"message": "Notification sent"}

@app.post("/broadcast")
async def broadcast_notification(notification: dict):
    """Broadcast notification to all users"""
    for user_connections in active_connections.values():
        for connection in user_connections:
            await connection.send_json(notification)

    return {"message": "Broadcast sent"}
