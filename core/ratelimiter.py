from functools import wraps
from redis import StrictRedis
from django.conf import settings
from django.http import HttpResponse


def rate_limit(limit=10, window=60, key_prefix='rate_limit:'):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            redis_client = StrictRedis(
                host=settings.CACHES['default']['LOCATION'].split(
                    '://')[1].split(':')[0],
                port=int(settings.CACHES['default']['LOCATION'].split(
                    '://')[1].split(':')[1]),
                db=settings.CACHES['default'].get('OPTIONS', {}).get('DB', 0)
            )

            key = f'{key_prefix}{request.META.get("REMOTE_ADDR")}'

            # Check rate limit using Redis atomic operations
            current_requests = redis_client.incr(key)
            if current_requests > limit:
                # Reset counter after window
                redis_client.expire(key, window)
                error_message = 'Too Many Requests'
                encoded_message = error_message.encode()
                return HttpResponse(encoded_message, status=429)

            response = func(request, *args, **kwargs)
            return response
        return wrapper
    return decorator
