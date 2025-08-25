"""
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import getSettings
from app.api.v1.api import apiRouter

settings = getSettings()

# Create FastAPI application
app = FastAPI(
    title=settings.appName,
    version=settings.appVersion,
    description="AI-Powered Indian Stock Trading Platform",
    openapi_url=f"{settings.apiV1Prefix}/openapi.json"
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

# Include API router
app.include_router(apiRouter, prefix=settings.apiV1Prefix)


@app.get("/")
async def root():
    """Root endpoint with basic application info"""
    return {
        "message": f"Welcome to {settings.appName} API",
        "version": settings.appVersion,
        "status": "running",
        "docs": "/docs"
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
