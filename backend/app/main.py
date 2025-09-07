"""
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.api.v1 import router as v1_router
from app.core.database import init_database, close_database, get_db_session

# Import database for health check
from sqlalchemy import text

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initialize database on startup.
    """
    # Startup
    print("🚀 Starting GoGoTrade application...")
    try:
        await init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🔄 Shutting down GoGoTrade application...")
    try:
        await close_database()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"⚠️  Database cleanup error: {e}")
    print("✅ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Indian Stock Trading Platform",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
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
    allowed_hosts=settings.allowed_hosts
)

# Include API routers
app.include_router(v1_router, prefix="/api")


# Simple health check endpoint
@app.get("/health/database")
async def database_health_check():
    """Check database health with real connection test."""
    try:
        async with get_db_session() as db:
            # Test database connection
            result = await db.execute(text("SELECT 1"))
            db_status = result.scalar() == 1
            
            # Count instruments
            result = await db.execute(text("SELECT COUNT(*) FROM instruments"))
            instruments_count = result.scalar()
            
            # Count extended info
            result = await db.execute(text("SELECT COUNT(*) FROM instruments_extended"))
            extended_count = result.scalar()
            
            return {
                "status": "healthy" if db_status else "unhealthy",
                "details": {
                    "database": "connected" if db_status else "disconnected",
                    "instruments_loaded": instruments_count,
                    "extended_info_loaded": extended_count,
                    "timestamp": "2025-09-06T00:00:00Z"
                }
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": {
                "database": "disconnected",
                "timestamp": "2025-09-06T00:00:00Z"
            }
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
