import time
from typing import Callable, Dict, Optional, Tuple

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware for API rate limiting using Redis as a backend.
    
    Supports different rate limits based on client type (service, admin, regular user)
    and implements a sliding window rate limiting algorithm.
    """
    
    def __init__(
        self,
        app: FastAPI,
        redis_client: Optional[redis.Redis] = None,
        default_limit: int = 100,
        default_window: int = 60,
        admin_limit: int = 300,
        admin_window: int = 60,
        service_limit: int = 1000,
        service_window: int = 60,
        anonymous_limit: int = 20,
        anonymous_window: int = 60,
        endpoint_limits: Optional[Dict[str, Tuple[int, int]]] = None
    ):
        """
        Initialize the rate limiter middleware.
        
        Args:
            app: The FastAPI application
            redis_client: Redis client, will create one if not provided
            default_limit: Default requests per window for authenticated users
            default_window: Default window in seconds for authenticated users
            admin_limit: Requests per window for admin users
            admin_window: Window in seconds for admin users
            service_limit: Requests per window for service accounts
            service_window: Window in seconds for service accounts
            anonymous_limit: Requests per window for unauthenticated requests
            anonymous_window: Window in seconds for unauthenticated requests
            endpoint_limits: Dict mapping endpoint paths to (limit, window) tuples
        """
        super().__init__(app)
        
        # Initialize Redis client if not provided
        if redis_client is None:
            self.redis = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        else:
            self.redis = redis_client
            
        # Rate limit settings
        self.default_limit = default_limit
        self.default_window = default_window
        self.admin_limit = admin_limit
        self.admin_window = admin_window
        self.service_limit = service_limit
        self.service_window = service_window
        self.anonymous_limit = anonymous_limit
        self.anonymous_window = anonymous_window
        
        # Custom endpoint limits
        self.endpoint_limits = endpoint_limits or {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request through rate limiting.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response from the next handler or 429 if rate limited
        """
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limiting(request.url.path):
            return await call_next(request)
        
        # Get client identifier and determine rate limit
        client_id = await self._get_client_id(request)
        path = request.url.path
        
        # Determine appropriate rate limit for this client and endpoint
        limit, window = self._get_rate_limit(client_id, path)
        
        # Apply rate limiting
        if not self._check_rate_limit(client_id, path, limit, window):
            return Response(
                content="Rate limit exceeded",
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Window": f"{window}s"
                }
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = self._get_remaining_requests(client_id, path, limit)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = f"{window}s"
        
        return response
    
    def _should_skip_rate_limiting(self, path: str) -> bool:
        """
        Determine if rate limiting should be skipped for this path.
        
        Args:
            path: The request path
            
        Returns:
            True if rate limiting should be skipped
        """
        # Skip health check and metrics endpoints
        if path in ("/health", "/metrics", "/docs", "/redoc", "/openapi.json"):
            return True
        
        return False
        
    async def _get_client_id(self, request: Request) -> str:
        """
        Extract client identifier from request.
        
        Args:
            request: The incoming request
            
        Returns:
            Client identifier (user ID, IP address, or API key)
        """
        # Try to get API key from header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"service:{api_key}"
        
        # Try to get authenticated user from request state
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
            # Identify if user is admin for different rate limits
            if request.state.user.is_admin:
                return f"admin:{user_id}"
            return f"user:{user_id}"
        
        # Fall back to IP address for anonymous requests
        client_host = request.client.host if request.client else "unknown"
        return f"anonymous:{client_host}"
    
    def _get_rate_limit(self, client_id: str, path: str) -> Tuple[int, int]:
        """
        Determine the appropriate rate limit for this client and endpoint.
        
        Args:
            client_id: The client identifier
            path: The request path
            
        Returns:
            Tuple of (limit, window in seconds)
        """
        # Check for endpoint-specific limits
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]
        
        # Apply client type-specific limits
        if client_id.startswith("service:"):
            return self.service_limit, self.service_window
        elif client_id.startswith("admin:"):
            return self.admin_limit, self.admin_window
        elif client_id.startswith("user:"):
            return self.default_limit, self.default_window
        else:
            return self.anonymous_limit, self.anonymous_window
    
    def _check_rate_limit(self, client_id: str, path: str, limit: int, window: int) -> bool:
        """
        Check if the client has exceeded their rate limit.
        
        Implements a sliding window rate limiting algorithm using Redis sorted sets.
        
        Args:
            client_id: The client identifier
            path: The request path
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = time.time()
        key = f"ratelimit:{client_id}:{path}"
        
        try:
            pipe = self.redis.pipeline()
            
            # Add the current request timestamp to the sorted set
            pipe.zadd(key, {str(now): now})
            
            # Remove timestamps outside the current window
            pipe.zremrangebyscore(key, 0, now - window)
            
            # Get the current count of requests in the window
            pipe.zcard(key)
            
            # Set expiration on the key to ensure cleanup
            pipe.expire(key, window * 2)
            
            # Execute all commands
            _, _, current_count, _ = pipe.execute()
            
            # Check if limit is exceeded
            return current_count <= limit
            
        except redis.RedisError as e:
            # Log the error and allow the request in case of Redis failure
            logger.error(f"Redis error in rate limiter: {e}")
            return True
            
    def _get_remaining_requests(self, client_id: str, path: str, limit: int) -> int:
        """
        Get the number of remaining requests allowed for this client.
        
        Args:
            client_id: The client identifier
            path: The request path
            limit: Maximum number of requests allowed
            
        Returns:
            Number of remaining requests
        """
        key = f"ratelimit:{client_id}:{path}"
        
        try:
            current_count = self.redis.zcard(key)
            remaining = max(0, limit - current_count)
            return remaining
        except redis.RedisError as e:
            logger.error(f"Redis error getting remaining requests: {e}")
            return 0