# websockets/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ws://host/ws/projects/<project_id>/tasks/?token=<jwt>
    re_path(r"^ws/projects/(?P<project_id>\d+)/$", consumers.TaskConsumer.as_asgi()),
]
