"""
API v1 router initialization
Includes all v1 API endpoints
"""

from fastapi import APIRouter
from . import ai_trading

# Create the main v1 router
router = APIRouter(prefix="/v1")

# Include all endpoint routers
router.include_router(ai_trading.router)

# Health check endpoint for v1 API
@router.get("/status")
async def api_status():
    """API v1 status endpoint"""
    return {
        "status": "healthy",
        "version": "1.0",
        "api_endpoints": [
            "/v1/ai-trading/market-data",
            "/v1/ai-trading/trading-signals", 
            "/v1/ai-trading/historical-data/{symbol}",
            "/v1/ai-trading/dashboard-data",
            "/v1/ai-trading/signal/{symbol}",
            "/v1/ai-trading/health"
        ]
    }
