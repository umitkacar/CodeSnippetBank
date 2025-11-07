"""Event-Driven Architecture"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Callable, List, Dict
from datetime import datetime

app = FastAPI()

class Event(BaseModel):
    type: str
    data: dict
    timestamp: datetime = None

class EventBus:
    """Simple event bus"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event):
        """Publish event"""
        event.timestamp = datetime.utcnow()
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                await handler(event)

event_bus = EventBus()

async def on_user_created(event: Event):
    """Handle user created event"""
    print(f"User created: {event.data}")

async def on_order_placed(event: Event):
    """Handle order placed event"""
    print(f"Order placed: {event.data}")

# Register handlers
event_bus.subscribe("user.created", on_user_created)
event_bus.subscribe("order.placed", on_order_placed)

@app.post("/events")
async def publish_event(event: Event):
    """Publish an event"""
    await event_bus.publish(event)
    return {"message": "Event published"}
