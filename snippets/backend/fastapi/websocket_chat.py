"""WebSocket Chat Implementation"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime, timezone
import json

app = FastAPI()

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, room: str = "general"):
        """Connect a client to a room"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(client_id)

        # Notify room about new connection
        await self.broadcast_to_room(
            room,
            {
                "type": "user_joined",
                "client_id": client_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "room": room
            },
            exclude=client_id
        )

    def disconnect(self, client_id: str, room: str = "general"):
        """Disconnect a client from a room"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if room in self.rooms and client_id in self.rooms[room]:
            self.rooms[room].remove(client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

    async def broadcast_to_room(self, room: str, message: dict, exclude: str = None):
        """Broadcast a message to all clients in a room"""
        if room not in self.rooms:
            return

        for client_id in self.rooms[room]:
            if exclude and client_id == exclude:
                continue
            await self.send_personal_message(message, client_id)

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients"""
        for client_id in self.active_connections:
            await self.send_personal_message(message, client_id)

    def get_room_users(self, room: str) -> List[str]:
        """Get all users in a room"""
        return self.rooms.get(room, [])

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Basic WebSocket endpoint"""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Process message
            message = {
                "type": "message",
                "client_id": client_id,
                "content": data.get("content", ""),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Broadcast to all clients
            await manager.broadcast_to_all(message)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast_to_all({
            "type": "user_left",
            "client_id": client_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

@app.websocket("/ws/{room}/{client_id}")
async def websocket_room_endpoint(websocket: WebSocket, room: str, client_id: str):
    """WebSocket endpoint with room support"""
    await manager.connect(websocket, client_id, room)

    try:
        # Send room info to client
        await manager.send_personal_message(
            {
                "type": "room_info",
                "room": room,
                "users": manager.get_room_users(room),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            client_id
        )

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type", "message")

            if message_type == "message":
                # Broadcast message to room
                message = {
                    "type": "message",
                    "client_id": client_id,
                    "room": room,
                    "content": data.get("content", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await manager.broadcast_to_room(room, message)

            elif message_type == "private":
                # Send private message to specific user
                target_id = data.get("target_id")
                message = {
                    "type": "private_message",
                    "from": client_id,
                    "content": data.get("content", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await manager.send_personal_message(message, target_id)

            elif message_type == "typing":
                # Broadcast typing indicator
                await manager.broadcast_to_room(
                    room,
                    {
                        "type": "typing",
                        "client_id": client_id,
                        "is_typing": data.get("is_typing", False)
                    },
                    exclude=client_id
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id, room)
        await manager.broadcast_to_room(
            room,
            {
                "type": "user_left",
                "client_id": client_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@app.get("/rooms/{room}/users")
async def get_room_users(room: str):
    """Get all users in a room"""
    return {
        "room": room,
        "users": manager.get_room_users(room),
        "count": len(manager.get_room_users(room))
    }

@app.get("/rooms/")
async def get_all_rooms():
    """Get all active rooms"""
    return {
        "rooms": [
            {
                "name": room,
                "users": users,
                "count": len(users)
            }
            for room, users in manager.rooms.items()
        ]
    }
