from django.urls import path
from aurora_socket.cousumers import ChatConsumer
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
 
application = ProtocolTypeRouter({
    'websocket':AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('beat/',ChatConsumer.as_asgi())
                    ]
            )
        )
    )
})

