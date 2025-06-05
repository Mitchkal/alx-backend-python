#!/usr/bin/env python3
""" "
Authentication-related class
for chat application
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    custom serializer to use email as username field
    for jwt Token authentication
    """

    user_name_field = "email"

    def validate(self, attrs):
        """
        validates credentials
        """
        credentials = {"email": attrs.get("email"), "password": attrs.get("password")}
        data = super().validate(credentials)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to use email for JWT authentication
    """

    serializer_class = CustomTokenObtainPairSerializer
