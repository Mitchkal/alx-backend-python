#!/usr/bin/python3
"""
middleware
"""
from datetime import datetime


class RequestLoggingMiddleware:
    """
    class for logging middleware
    """

    def __init__(self, get_response):
        """
        middleware initalization
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the request before view
        to log user requests to a file
        including timestamp, user, and request path
        """
        response = self.get_response(request)
        # user = response["User"]
        user = request.user

        with open("requests.log", "a") as f:
            f.write(f"{datetime.now()} - User: {user} - Path: {request.path} \n")

        return response
