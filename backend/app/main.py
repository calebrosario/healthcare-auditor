"""
Healthcare Auditor FastAPI Application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .core.database import init_db, close_db
from .api import health, auth
from .middleware import setup_middleware


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Connecting to database: {settings.DATABASE_URL}")
    print(f"Connecting to Neo4j: {settings.NEO4J_URI}")
    
    # Initialize database
    await init_db()
    print("Database initialized successfully")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_db()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Healthcare billing fraud detection and compliance verification system",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Set up middleware
app = setup_middleware(app)


# Include API routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print(f"{settings.PROJECT_NAME} starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    print(f"{settings.PROJECT_NAME} shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
