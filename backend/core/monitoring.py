"""
StudyBuddy AI - Monitoring & Metrics
=====================================
Prometheus metrics and health checks.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter(
    'studybuddy_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'studybuddy_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'studybuddy_active_requests',
    'Number of active requests'
)

QUIZ_GENERATED = Counter(
    'studybuddy_quizzes_generated_total',
    'Total quizzes generated',
    ['course_id']
)

MATERIALS_PROCESSED = Counter(
    'studybuddy_materials_processed_total',
    'Total materials processed',
    ['file_type', 'status']
)

LLM_REQUESTS = Counter(
    'studybuddy_llm_requests_total',
    'Total LLM API requests',
    ['operation', 'status']
)

LLM_LATENCY = Histogram(
    'studybuddy_llm_latency_seconds',
    'LLM request latency',
    ['operation']
)

VECTOR_SEARCHES = Counter(
    'studybuddy_vector_searches_total',
    'Total vector store searches'
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
        
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            endpoint = self._get_endpoint(request.url.path)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        finally:
            ACTIVE_REQUESTS.dec()
    
    def _get_endpoint(self, path: str) -> str:
        """Normalize endpoint for metrics."""
        # Replace IDs with placeholder
        parts = path.split('/')
        normalized = []
        for part in parts:
            if part and len(part) == 36 and '-' in part:
                normalized.append('{id}')
            else:
                normalized.append(part)
        return '/'.join(normalized) or '/'


def get_metrics() -> Response:
    """Generate Prometheus metrics response."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Helper functions to record custom metrics
def record_quiz_generated(course_id: str):
    """Record quiz generation."""
    QUIZ_GENERATED.labels(course_id=course_id).inc()


def record_material_processed(file_type: str, success: bool):
    """Record material processing."""
    MATERIALS_PROCESSED.labels(
        file_type=file_type,
        status="success" if success else "failed"
    ).inc()


def record_llm_request(operation: str, success: bool, duration: float):
    """Record LLM request."""
    LLM_REQUESTS.labels(
        operation=operation,
        status="success" if success else "failed"
    ).inc()
    LLM_LATENCY.labels(operation=operation).observe(duration)


def record_vector_search():
    """Record vector search."""
    VECTOR_SEARCHES.inc()
