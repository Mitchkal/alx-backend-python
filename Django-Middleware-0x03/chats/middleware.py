#!/usr/bin/python3
"""
middleware
"""
from datetime import datetime
import logging


logging.basicConfig(filename="requests.log", level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware class for logging middleware
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

        # user = response["User"]
        response = self.get_response(request)
        # user = request.user
        user = request.user if request.user.is_authenticated else "AnonymousUser"

        # with open("requests.log", "a") as f:
        #     f.write(f"{datetime.now()} - User: {user} - Path: {request.path} \n")
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path} \n")

        return response
