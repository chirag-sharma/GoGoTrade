"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import tradingData, charts, strategies

apiRouter = APIRouter()

# Include endpoint routers
apiRouter.include_router(tradingData.router, prefix="/trading-data", tags=["trading-data"])
apiRouter.include_router(charts.router, prefix="/charts", tags=["charts"])  
apiRouter.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
