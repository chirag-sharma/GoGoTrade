"""
Simple FastAPI test server for NSE securities API testing.
This bypasses complex dependencies and focuses on testing our instruments API.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime

# Direct imports for testing
from app.core.database import init_database, close_database, get_db_session
from app.models import Instrument
from app.models.market_data import InstrumentExtended, Watchlist, MarketStats, SectorPerformance
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="GoGoTrade NSE API Test",
    version="1.0.0",
    description="Testing NSE Securities Management API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_database()
    print("✅ Database initialized for testing")

@app.on_event("shutdown")
async def shutdown_event():
    await close_database()
    print("✅ Database connections closed")

# Include simplified instruments endpoints
@app.get("/api/v1/search")
async def search_instruments(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Number of results")
):
    """Search for instruments by symbol or name."""
    try:
        async with get_db_session() as db:
            # Search by symbol or name
            result = await db.execute(
                select(Instrument, InstrumentExtended)
                .join(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                .where(
                    (Instrument.tradingsymbol.ilike(f"%{q}%")) |
                    (Instrument.name.ilike(f"%{q}%"))
                )
                .limit(limit)
            )
            
            instruments = []
            for instrument, extended in result:
                instruments.append({
                    "symbol": instrument.tradingsymbol,
                    "name": instrument.name,
                    "exchange": instrument.exchange,
                    "last_price": float(instrument.last_price) if instrument.last_price else None,
                    "sector": extended.sector,
                    "industry_group": extended.industry_group,
                    "market_segment": extended.market_segment,
                    "market_cap": float(extended.market_cap) if extended.market_cap else None
                })
            
            return {
                "query": q,
                "results": instruments,
                "total": len(instruments)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/instruments")
async def get_instruments(
    sector: Optional[str] = None,
    market_segment: Optional[str] = None,
    limit: int = Query(50, description="Number of results")
):
    """Get instruments with optional filtering."""
    try:
        async with get_db_session() as db:
            query = select(Instrument, InstrumentExtended).join(
                InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id
            )
            
            if sector:
                query = query.where(InstrumentExtended.sector.ilike(f"%{sector}%"))
            
            if market_segment:
                query = query.where(InstrumentExtended.market_segment == market_segment)
            
            query = query.limit(limit)
            result = await db.execute(query)
            
            instruments = []
            for instrument, extended in result:
                instruments.append({
                    "symbol": instrument.tradingsymbol,
                    "name": instrument.name,
                    "exchange": instrument.exchange,
                    "last_price": float(instrument.last_price) if instrument.last_price else None,
                    "sector": extended.sector,
                    "industry_group": extended.industry_group,
                    "market_segment": extended.market_segment,
                    "market_cap": float(extended.market_cap) if extended.market_cap else None
                })
            
            return {
                "instruments": instruments,
                "total": len(instruments),
                "filters": {
                    "sector": sector,
                    "market_segment": market_segment
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market-movers")
async def get_market_movers():
    """Get market movers (gainers, losers, most active)."""
    try:
        async with get_db_session() as db:
            # Get top gainers
            gainers_result = await db.execute(
                select(Instrument.tradingsymbol, MarketStats.price_change_percent)
                .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                .where(MarketStats.gainer_rank.isnot(None))
                .order_by(MarketStats.gainer_rank)
                .limit(10)
            )
            gainers = [{"symbol": symbol, "change_percent": float(change)} 
                      for symbol, change in gainers_result]
            
            # Get top losers
            losers_result = await db.execute(
                select(Instrument.tradingsymbol, MarketStats.price_change_percent)
                .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                .where(MarketStats.loser_rank.isnot(None))
                .order_by(MarketStats.loser_rank)
                .limit(10)
            )
            losers = [{"symbol": symbol, "change_percent": float(change)} 
                     for symbol, change in losers_result]
            
            # Get most active
            active_result = await db.execute(
                select(Instrument.tradingsymbol, MarketStats.volume)
                .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                .where(MarketStats.volume_rank.isnot(None))
                .order_by(MarketStats.volume_rank)
                .limit(10)
            )
            most_active = [{"symbol": symbol, "volume": volume} 
                          for symbol, volume in active_result]
            
            return {
                "gainers": gainers,
                "losers": losers,
                "most_active": most_active,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sectors")
async def get_sector_performance():
    """Get sector performance data."""
    try:
        async with get_db_session() as db:
            result = await db.execute(
                select(SectorPerformance)
                .order_by(SectorPerformance.avg_change_percent.desc())
                .limit(20)
            )
            
            sectors = []
            for sector_perf in result.scalars():
                sectors.append({
                    "sector_name": sector_perf.sector_name,
                    "industry_group": sector_perf.industry_group,
                    "total_stocks": sector_perf.total_stocks,
                    "gainers_count": sector_perf.gainers_count,
                    "losers_count": sector_perf.losers_count,
                    "avg_change_percent": float(sector_perf.avg_change_percent),
                    "stats_date": sector_perf.stats_date.isoformat()
                })
            
            return {
                "sectors": sectors,
                "total": len(sectors)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "GoGoTrade NSE API Test Server",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/v1/search",
            "instruments": "/api/v1/instruments",
            "watchlists": "/api/v1/watchlists",
            "market_movers": "/api/v1/market-movers",
            "sectors": "/api/v1/sectors"
        }
    }

@app.get("/health")
async def health_check():
    """Database health check."""
    try:
        async with get_db_session() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM instruments"))
            instruments_count = result.scalar()
            
            return {
                "status": "healthy",
                "database": "connected", 
                "instruments": instruments_count
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
