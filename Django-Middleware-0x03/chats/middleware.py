#!/usr/bin/python3
"""
middleware
"""
from datetime import datetime
import logging
from django.http import HttpResponseForbidden


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


class RestrictAccessByTimeMiddleware:
    """
    Restricts access to the messaging app during specific hours of day
    """

    def __init__(self, get_response):
        """
        initialization
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        checks current server time and deny access
        outside 6PM to 9PM
        """
        current_time = datetime.now().hour

        if not (18 <= current_time < 21):
            return HttpResponseForbidden(
                "Access restricted outside allowed hours (6pm to 9pm)."
            )
        response = self.get_response(request)
        return response
