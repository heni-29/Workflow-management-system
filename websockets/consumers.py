# websockets/consumers.py
"""
TaskConsumer — WebSocket consumer for real-time task updates.

URL:  ws://localhost:8000/ws/projects/<project_id>/tasks/?token=<jwt>
Group: project_<project_id>_tasks

When a task inside this project is updated via the REST API, the view
calls broadcast_task_update(), which channel_layer.group_send()s a
'task_updated' message to everyone connected to that project's group.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class TaskConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group_name = f"project_{self.project_id}"

        # Reject unauthenticated connections
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        # Join the project's channel group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Confirm connection
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "project_id": self.project_id,
            "message": f"Listening for task updates on project {self.project_id}",
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Clients don't send messages upstream — this is server-push only
    async def receive(self, text_data=None, bytes_data=None):
        pass

    # ── Handler called when channel_layer.group_send() sends 'task.updated' ──
    # Note: Django Channels maps type 'task.updated' → method task_updated
    async def task_updated(self, event):
        """Forward a task-update event to the connected WebSocket client."""
        await self.send(text_data=json.dumps(event["data"]))
