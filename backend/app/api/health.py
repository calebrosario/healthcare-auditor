"""
Health check and metrics endpoints.
"""
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from . import billing_codes, providers, bills, regulations, alerts, knowledge_graph

router = APIRouter()

# Include sub-routers
router.include_router(billing_codes.router, prefix="/billing-codes", tags=["Billing Codes"])
router.include_router(providers.router, prefix="/providers", tags=["Providers"])
router.include_router(bills.router, prefix="/bills", tags=["Bills"])
router.include_router(regulations.router, prefix="/regulations", tags=["Regulations"])
router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
router.include_router(knowledge_graph.router, prefix="/knowledge-graph", tags=["Knowledge Graph"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns 200 OK if the service is running.
    """
    return {
        "status": "healthy",
        "service": "healthcare-auditor-api",
        "version": "0.1.0",
        "timestamp": "2026-02-04T13:00:00Z"
    }


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    Exposes metrics for monitoring and alerting.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Healthcare Auditor API",
        "version": "0.1.0",
        "description": "Healthcare billing fraud detection and compliance verification system",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "endpoints": {
            "billing_codes": "/api/v1/billing-codes",
            "providers": "/api/v1/providers",
            "bills": "/api/v1/bills",
            "regulations": "/api/v1/regulations",
            "alerts": "/api/v1/alerts",
            "knowledge_graph": "/api/v1/knowledge-graph"
        }
    }
