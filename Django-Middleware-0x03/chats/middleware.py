#!/usr/bin/python3
"""
middleware
"""
from datetime import datetime, timedelta
import logging
from django.http import HttpResponseForbidden, HttpResponse
from collections import defaultdict


logging.basicConfig(filename="requests.log", level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

message_counts = defaultdict(list)


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


class OffensiveLanguageMiddleware:
    """
    Middleware to track number of chat messages
    by each ip addresss anf enforce a time based limit of 5
    minutes
    """

    def __init__(self, get_response):
        """
        initialization
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Enforces time based limit of 5
        minutes per ip on POST request
        """

        ip_address = request.META.get("REMOTE_ADDR", "")
        if not ip_address:
            # Fall back to X-FORWARDED_FOR for proxies
            ip_address = (
                request.META.get("HTTP_X_FORWARDED_FOR", "").split() or "unknown"
            )

        # check if request is a POST to /api/messages
        if request.method == "POST" and request.path.startswith("/api/messages"):
            # Clen up timestamps older than 1 minute
            current_time = datetime.now()
            message_counts[ip_address] = [
                timestamp
                for timestamp in message_counts[ip_address]
                if current_time - timestamp < timedelta(minutes=1)
            ]
            if len(message_counts[ip_address]) >= 5:
                return HttpResponse(
                    "Message limit exceeded: 5 messages per minute allowed", status=249
                )

            # Record new message timestamp
            message_counts[ip_address].append(current_time)

        # process request
        response = self.get_response(request)
        return response
