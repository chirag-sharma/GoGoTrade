"""
API v1 router initialization
Includes all v1 API endpoints
"""

from fastapi import APIRouter
from .api import apiRouter

# Create the main v1 router
router = APIRouter(prefix="/v1")

# Include the main API router (which includes all strategies, trading-data, and charts endpoints)
router.include_router(apiRouter)

# Health check endpoint for v1 API
@router.get("/status")
async def api_status():
    """API v1 status endpoint"""
    return {
        "status": "healthy",
        "version": "1.0",
        "api_endpoints": [
            # Structured API endpoints
            "/v1/status",
            "/v1/strategies/strategies",
            "/v1/strategies/backtest", 
            "/v1/strategies/signals/{symbol}",
            "/v1/trading-data/market-data/{symbol}",
            "/v1/trading-data/ohlcv/{symbol}",
            "/v1/trading-data/instruments",
            "/v1/charts/chart-data/{symbol}",
            "/v1/charts/indicators/{symbol}"
        ]
    }
