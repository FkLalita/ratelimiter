from django.conf import settings
from django.http import HttpResponse
from redis import StrictRedis
from asgiref.sync import iscoroutinefunction, markcoroutinefunction


class RateLimiterMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = StrictRedis(
            host=settings.CACHES['default']['LOCATION'].split(
                '://')[1].split(':')[0],  # Extract hostname from location
            port=int(settings.CACHES['default']['LOCATION'].split(
                '://')[1].split(':')[1]),  # Extract port from location
            db=settings.CACHES['default'].get('OPTIONS', {}).get(
                'DB', 0)  # Use specific database if provided
        )

        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        # Define rate limit parameters (adjust as needed)
        limit = 2  # Maximum requests per window
        window = 22  # Time window (seconds)
        # Use IP address as key (consider user/session for granular control)
        key = f'rate_limit:{request.META.get("REMOTE_ADDR")}'

        # Check rate limit using Redis atomic operations
        current_requests = self.redis_client.incr(key)
        if current_requests > limit:
            # Reset counter after window
            self.redis_client.expire(key, window)
            return self.handle_throttled_request(request)

        # Allow request if within limit
        response = await self.get_response(request)
        # Decrement counter after successful request
        self.redis_client.decr(key)
        return response

    def handle_throttled_request(self, request):
        # Customize error response (e.g., HTTP 429 Too Many Requests)
        error_message = "Too many requests. Please try again later."
        encoded_message = error_message.encode('utf-8')
        return HttpResponse(encoded_message)
