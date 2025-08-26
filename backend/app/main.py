"""
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import getSettings
from app.api.v1.api import apiRouter
from app.core.database import db_manager

settings = getSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for database connections.
    """
    # Startup
    print("🚀 Starting GoGoTrade application...")
    try:
        await db_manager.initialize()
        print("✅ Database connections initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Continue without database for development
    
    yield
    
    # Shutdown
    print("🔄 Shutting down GoGoTrade application...")
    try:
        await db_manager.close()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"⚠️  Database cleanup warning: {e}")


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
app.include_router(apiRouter, prefix=settings.apiV1Prefix)


# Database health check endpoint
@app.get("/health/database")
async def database_health_check():
    """Check database connection health."""
    try:
        health_status = await db_manager.health_check()
        return {
            "status": "healthy" if health_status.get("postgresql") and health_status.get("redis") else "degraded",
            "details": health_status
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
