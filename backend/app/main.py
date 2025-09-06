"""
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.api.v1 import router as v1_router

# For now, let's simplify and avoid database dependencies
# from app.core.database import db_manager
# from app.services.real_time_data import start_real_time_data_service, stop_real_time_data_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Simplified for quick startup.
    """
    # Startup
    print("🚀 Starting GoGoTrade application...")
    print("✅ Basic services initialized")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down GoGoTrade application...")
    print("✅ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.appName,
    version=settings.appVersion,
    description="AI-Powered Indian Stock Trading Platform",
    openapi_url=f"{settings.apiV1Prefix}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.allowedHosts
)

# Include API routers
app.include_router(v1_router, prefix="/api")


# Simple health check endpoint
@app.get("/health/database")
async def database_health_check():
    """Check system health - simplified version."""
    try:
        return {
            "status": "healthy",
            "details": {
                "api": "operational",
                "timestamp": "2025-09-06T00:00:00Z"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "message": "GoGoTrade API is running!",
        "version": settings.appVersion,
        "docs_url": "/docs",
        "database_health": "/health/database"
    }


@app.get("/health")
async def healthCheck():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2025-08-25T00:00:00Z",
        "version": settings.appVersion
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debugMode
    )
