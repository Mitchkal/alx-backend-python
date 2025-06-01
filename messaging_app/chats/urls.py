#!/usr/bin/env python3
"""
routes registration
"""
from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet


router = routers.DefaultRouter(trailing_slash=False)

router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("", include(router.urls)),
]
