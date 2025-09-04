"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from app.api.v1.endpoints import tradingData, charts, strategies

apiRouter = APIRouter()

# Status endpoint
@apiRouter.get("/status")
async def status():
    """Get API status"""
    return {
        "status": "ok",
        "message": "GoGoTrade API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Include endpoint routers
apiRouter.include_router(tradingData.router, prefix="/trading-data", tags=["trading-data"])
apiRouter.include_router(charts.router, prefix="/charts", tags=["charts"])  
apiRouter.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
