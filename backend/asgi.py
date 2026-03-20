# backend/asgi.py
"""
ASGI config — routes HTTP traffic to Django and WebSocket traffic to Channels.

Run with Daphne (not gunicorn):
    daphne -p 8000 backend.asgi:application
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Must call get_asgi_application() before importing anything that touches models
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from websockets.routing import websocket_urlpatterns         # noqa: E402
from websockets.middleware import JwtAuthMiddlewareStack     # noqa: E402

application = ProtocolTypeRouter({
    # Standard HTTP requests → unchanged Django handling
    "http": django_asgi_app,

    # WebSocket requests → JWT middleware → URL router → TaskConsumer
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
