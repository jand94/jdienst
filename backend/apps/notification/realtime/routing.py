from django.urls import path

from apps.notification.realtime.notification_socket import NotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
