"""
Custom middleware for rate limiting, logging, and request tracking.
"""
import time
import uuid
from typing import Callable
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
import logging
from .config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Rate limiting store (in-memory for simplicity - use Redis in production)
rate_limit_store = defaultdict(list)


# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response {request_id}: Status {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.3f}"
        
        # Update Prometheus metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        client_id = request.client.host if request.client else "unknown"
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        
        # Clean old requests from store
        rate_limit_store[client_id] = [
            req_time for req_time in rate_limit_store[client_id]
            if req_time > window_start
        ]
        
        # Check rate limit
        request_count = len(rate_limit_store[client_id])
        if request_count >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(
                f"Rate limit exceeded for client {client_id}: "
                f"{request_count} requests in {settings.RATE_LIMIT_WINDOW}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int((now + timedelta(seconds=settings.RATE_LIMIT_WINDOW)).timestamp()))
                }
            )
        
        # Record request
        rate_limit_store[client_id].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = settings.RATE_LIMIT_REQUESTS - request_count - 1
        reset = int((now + timedelta(seconds=settings.RATE_LIMIT_WINDOW)).timestamp())
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        
        return response


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware to handle health check endpoints without rate limiting."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Bypass rate limiting for health check
        if request.url.path in ["/health", "/metrics", "/"]:
            return await call_next(request)
        return await call_next(request)


def setup_middleware(app: ASGIApp) -> ASGIApp:
    """
    Set up all middleware for the FastAPI application.
    
    Order matters - middleware is applied in reverse order of appearance.
    """
    # CORS middleware (outermost)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Health check middleware
    app.add_middleware(HealthCheckMiddleware)
    
    # Rate limiting
    app.add_middleware(RateLimitMiddleware)
    
    # Request logging (innermost)
    app.add_middleware(RequestLoggingMiddleware)
    
    return app
