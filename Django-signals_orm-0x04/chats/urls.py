#!/usr/bin/env python3
"""
routes registration
"""
from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet, NotificationViewSet, UserViewSet
from django.conf.urls.static import static


router = routers.DefaultRouter()

router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"users", UserViewSet, basename="user")

conversations_router = NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)
conversations_router.register(
    r"messages", MessageViewSet, basename="conversation-message"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(conversations_router.urls)),
]
