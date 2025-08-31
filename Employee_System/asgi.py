import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import Employee_System.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject3.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Employee_System.routing.websocket_urlpatterns
        )
    ),
})
