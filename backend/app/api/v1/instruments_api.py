"""
Enhanced Instruments API with search, filtering, and watchlist management.
Provides comprehensive securities discovery and management.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import get_db_session
from app.models import Instrument, InstrumentType
from app.models.market_data import (
    InstrumentExtended, Watchlist, WatchlistItem, MarketStats,
    SectorPerformance, IndustryGroup, MarketSegment
)

router = APIRouter(prefix="/instruments", tags=["Instruments & Securities"])

# Request Models
class InstrumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50, description="Search query")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results")
    exchange: Optional[str] = Field(default=None, description="Filter by exchange (NSE, BSE)")
    instrument_type: Optional[InstrumentType] = Field(default=None, description="Filter by type")
    industry_group: Optional[IndustryGroup] = Field(default=None, description="Filter by industry")
    market_segment: Optional[MarketSegment] = Field(default=None, description="Filter by market cap")

class InstrumentFilterRequest(BaseModel):
    exchange: Optional[str] = None
    instrument_type: Optional[InstrumentType] = None
    industry_group: Optional[IndustryGroup] = None
    market_segment: Optional[MarketSegment] = None
    market_cap_min: Optional[int] = None
    market_cap_max: Optional[int] = None
    pe_ratio_max: Optional[float] = None
    is_f_and_o: Optional[bool] = None
    nifty_index: Optional[str] = None  # Filter by NIFTY index membership
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class WatchlistCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_default: bool = Field(default=False)

class WatchlistUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

class WatchlistAddItemRequest(BaseModel):
    instrument_id: str
    notes: Optional[str] = Field(default=None, max_length=1000)
    price_alert_high: Optional[float] = None
    price_alert_low: Optional[float] = None

# Response Models
class InstrumentResponse(BaseModel):
    id: str
    instrument_token: int
    tradingsymbol: str
    name: str
    last_price: Optional[float]
    exchange: str
    instrument_type: str
    # Extended info
    industry_group: Optional[str]
    sector: Optional[str]
    market_segment: Optional[str]
    market_cap: Optional[int]
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    is_f_and_o: bool
    nifty_indices: Optional[List[str]]

class WatchlistResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_default: bool
    items_count: int
    created_at: datetime

class WatchlistItemResponse(BaseModel):
    id: str
    instrument: InstrumentResponse
    notes: Optional[str]
    price_alert_high: Optional[float]
    price_alert_low: Optional[float]
    added_at: datetime

class MarketMoversResponse(BaseModel):
    gainers: List[InstrumentResponse]
    losers: List[InstrumentResponse]
    most_active: List[InstrumentResponse]

class SectorAnalysisResponse(BaseModel):
    sector_name: str
    industry_group: Optional[str]
    total_stocks: int
    gainers_count: int
    losers_count: int
    avg_change_percent: float
    top_performers: List[InstrumentResponse]

# API Endpoints

@router.get("/search", response_model=List[InstrumentResponse])
async def search_instruments(
    query: str = Query(..., min_length=1, description="Search by symbol or company name"),
    limit: int = Query(default=20, ge=1, le=100),
    exchange: Optional[str] = Query(default=None, description="Filter by exchange"),
    instrument_type: Optional[str] = Query(default=None, description="Filter by type"),
    industry_group: Optional[str] = Query(default=None, description="Filter by industry")
):
    """
    🔍 **Symbol Search API**: Advanced search with filters
    
    Search instruments by symbol or company name with multiple filter options.
    Supports fuzzy matching and ranking by relevance.
    
    **Examples:**
    - `/search?query=infy` - Find Infosys
    - `/search?query=bank&industry_group=BANKING` - Find banking stocks
    - `/search?query=nifty&instrument_type=FUTURES` - Find NIFTY futures
    """
    async with get_db_session() as db:
        try:
            # Build query
            query_stmt = select(Instrument)
            
            # Add search conditions (case-insensitive, partial match)
            search_conditions = or_(
                Instrument.tradingsymbol.ilike(f"%{query}%"),
                Instrument.name.ilike(f"%{query}%")
            )
            query_stmt = query_stmt.where(search_conditions)
            
            # Add filters
            if exchange:
                query_stmt = query_stmt.where(Instrument.exchange == exchange.upper())
            
            if instrument_type:
                query_stmt = query_stmt.where(Instrument.instrument_type == instrument_type.upper())
            
            if industry_group:
                query_stmt = query_stmt.where(InstrumentExtended.industry_group == industry_group.upper())
            
            # Order by relevance (exact symbol match first, then by name)
            query_stmt = query_stmt.order_by(
                Instrument.tradingsymbol.ilike(f"{query}%").desc(),
                Instrument.name
            ).limit(limit)
            
            result = await db.execute(query_stmt)
            instruments_data = result.fetchall()
            
            # Format response
            instruments = []
            for row in instruments_data:
                # row is a tuple, access by index
                instruments.append(InstrumentResponse(
                    id=str(row[0]),  # instrument.id
                    instrument_token=row[1],  # instrument.instrument_token
                    tradingsymbol=row[2],  # instrument.tradingsymbol
                    name=row[3],  # instrument.name
                    last_price=float(row[4]) if row[4] else 0.0,  # instrument.last_price
                    exchange=row[5],  # instrument.exchange
                    instrument_type=row[6].value if hasattr(row[6], 'value') else str(row[6]),  # instrument.instrument_type
                    industry_group=None,  # No extended data
                    sector=None,  # No extended data
                    market_segment=None,  # No extended data
                    market_cap=None,  # No extended data
                    pe_ratio=None,  # No extended data
                    pb_ratio=None,  # No extended data
                    is_f_and_o=False,  # No extended data
                    nifty_indices=None  # No extended data
                ))
            
            return instruments
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/filter", response_model=List[InstrumentResponse])
async def filter_instruments(
    exchange: Optional[str] = Query(default=None),
    instrument_type: Optional[str] = Query(default=None),
    industry_group: Optional[str] = Query(default=None),
    market_segment: Optional[str] = Query(default=None),
    market_cap_min: Optional[int] = Query(default=None, description="Minimum market cap in INR"),
    market_cap_max: Optional[int] = Query(default=None, description="Maximum market cap in INR"),
    pe_ratio_max: Optional[float] = Query(default=None, description="Maximum P/E ratio"),
    is_f_and_o: Optional[bool] = Query(default=None, description="Futures & Options available"),
    nifty_index: Optional[str] = Query(default=None, description="NIFTY index membership"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """
    🎯 **Instrument Browser**: Advanced filtering by multiple criteria
    
    Filter instruments by sector, market cap, exchange, and other criteria.
    Perfect for discovering investment opportunities.
    
    **Examples:**
    - `/filter?industry_group=IT&market_cap_min=100000000000` - Large cap IT stocks
    - `/filter?is_f_and_o=true&pe_ratio_max=20` - F&O stocks with low P/E
    - `/filter?nifty_index=NIFTY50` - NIFTY 50 stocks
    """
    async with get_db_session() as db:
        try:
            # Build filtered query
            query_stmt = (
                select(Instrument, InstrumentExtended)
                .outerjoin(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                .where(InstrumentExtended.is_active == True)
            )
            
            # Apply filters
            if exchange:
                query_stmt = query_stmt.where(Instrument.exchange == exchange.upper())
            
            if instrument_type:
                query_stmt = query_stmt.where(Instrument.instrument_type == instrument_type.upper())
            
            if industry_group:
                query_stmt = query_stmt.where(InstrumentExtended.industry_group == industry_group.upper())
            
            if market_segment:
                query_stmt = query_stmt.where(InstrumentExtended.market_segment == market_segment.upper())
            
            if market_cap_min:
                query_stmt = query_stmt.where(InstrumentExtended.market_cap >= market_cap_min)
            
            if market_cap_max:
                query_stmt = query_stmt.where(InstrumentExtended.market_cap <= market_cap_max)
            
            if pe_ratio_max:
                query_stmt = query_stmt.where(InstrumentExtended.pe_ratio <= pe_ratio_max)
            
            if is_f_and_o is not None:
                query_stmt = query_stmt.where(InstrumentExtended.is_f_and_o == is_f_and_o)
            
            if nifty_index:
                query_stmt = query_stmt.where(
                    InstrumentExtended.nifty_indices.contains([nifty_index])
                )
            
            # Order by market cap desc
            query_stmt = query_stmt.order_by(
                InstrumentExtended.market_cap.desc().nullslast()
            ).offset(offset).limit(limit)
            
            result = await db.execute(query_stmt)
            instruments_data = result.fetchall()
            
            # Format response (same as search)
            instruments = []
            for instrument, extended in instruments_data:
                instruments.append(InstrumentResponse(
                    id=str(instrument.id),
                    instrument_token=instrument.instrument_token,
                    tradingsymbol=instrument.tradingsymbol,
                    name=instrument.name,
                    last_price=float(instrument.last_price) if instrument.last_price else None,
                    exchange=instrument.exchange,
                    instrument_type=instrument.instrument_type.value,
                    industry_group=extended.industry_group.value if extended and extended.industry_group else None,
                    sector=extended.sector if extended else None,
                    market_segment=extended.market_segment.value if extended and extended.market_segment else None,
                    market_cap=extended.market_cap if extended else None,
                    pe_ratio=float(extended.pe_ratio) if extended and extended.pe_ratio else None,
                    pb_ratio=float(extended.pb_ratio) if extended and extended.pb_ratio else None,
                    is_f_and_o=extended.is_f_and_o if extended else False,
                    nifty_indices=extended.nifty_indices if extended else None
                ))
            
            return instruments
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Filter failed: {str(e)}")

@router.get("/market-movers", response_model=MarketMoversResponse)
async def get_market_movers():
    """
    📈 **Popular Symbols**: Get trending and most active stocks
    
    Returns today's top gainers, losers, and most active stocks.
    Updated multiple times during trading hours.
    """
    async with get_db_session() as db:
        try:
            today = datetime.now().date()
            
            # Get top gainers
            gainers_query = (
                select(Instrument, InstrumentExtended, MarketStats)
                .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                .outerjoin(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                .where(
                    func.date(MarketStats.stats_date) == today,
                    MarketStats.gainer_rank.isnot(None)
                )
                .order_by(MarketStats.gainer_rank)
                .limit(10)
            )
            
            # Get top losers  
            losers_query = (
                select(Instrument, InstrumentExtended, MarketStats)
                .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                .outerjoin(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                .where(
                    func.date(MarketStats.stats_date) == today,
                    MarketStats.loser_rank.isnot(None)
                )
                .order_by(MarketStats.loser_rank)
                .limit(10)
            )
            
            # Get most active
            active_query = (
                select(Instrument, InstrumentExtended, MarketStats)
                .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                .outerjoin(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                .where(
                    func.date(MarketStats.stats_date) == today,
                    MarketStats.volume_rank.isnot(None)
                )
                .order_by(MarketStats.volume_rank)
                .limit(10)
            )
            
            # Execute queries
            gainers_result = await db.execute(gainers_query)
            losers_result = await db.execute(losers_query)
            active_result = await db.execute(active_query)
            
            def format_instrument(instrument, extended, stats=None):
                return InstrumentResponse(
                    id=str(instrument.id),
                    instrument_token=instrument.instrument_token,
                    tradingsymbol=instrument.tradingsymbol,
                    name=instrument.name,
                    last_price=float(stats.close_price) if stats and stats.close_price else float(instrument.last_price) if instrument.last_price else None,
                    exchange=instrument.exchange,
                    instrument_type=instrument.instrument_type.value,
                    industry_group=extended.industry_group.value if extended and extended.industry_group else None,
                    sector=extended.sector if extended else None,
                    market_segment=extended.market_segment.value if extended and extended.market_segment else None,
                    market_cap=extended.market_cap if extended else None,
                    pe_ratio=float(extended.pe_ratio) if extended and extended.pe_ratio else None,
                    pb_ratio=float(extended.pb_ratio) if extended and extended.pb_ratio else None,
                    is_f_and_o=extended.is_f_and_o if extended else False,
                    nifty_indices=extended.nifty_indices if extended else None
                )
            
            return MarketMoversResponse(
                gainers=[format_instrument(i, e, s) for i, e, s in gainers_result.fetchall()],
                losers=[format_instrument(i, e, s) for i, e, s in losers_result.fetchall()],
                most_active=[format_instrument(i, e, s) for i, e, s in active_result.fetchall()]
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Market movers fetch failed: {str(e)}")

# Watchlist Management APIs

@router.get("/watchlists", response_model=List[WatchlistResponse])
async def get_watchlists(user_id: str = "default_user"):
    """
    📋 **Watchlist Management**: Get all user watchlists
    """
    async with get_db_session() as db:
        try:
            query = (
                select(Watchlist, func.count(WatchlistItem.id).label('items_count'))
                .outerjoin(WatchlistItem, Watchlist.id == WatchlistItem.watchlist_id)
                .where(Watchlist.user_id == user_id)
                .group_by(Watchlist.id)
                .order_by(Watchlist.is_default.desc(), Watchlist.created_at)
            )
            
            result = await db.execute(query)
            watchlists_data = result.fetchall()
            
            return [
                WatchlistResponse(
                    id=str(wl.id),
                    name=wl.name,
                    description=wl.description,
                    is_default=wl.is_default,
                    items_count=count,
                    created_at=wl.created_at
                ) for wl, count in watchlists_data
            ]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watchlists fetch failed: {str(e)}")

@router.post("/watchlists", response_model=WatchlistResponse)
async def create_watchlist(request: WatchlistCreateRequest, user_id: str = "default_user"):
    """
    ➕ **Create Watchlist**: Create a new watchlist
    """
    async with get_db_session() as db:
        try:
            # If this is set as default, unset other defaults
            if request.is_default:
                await db.execute(
                    update(Watchlist)
                    .where(Watchlist.user_id == user_id)
                    .values(is_default=False)
                )
            
            watchlist = Watchlist(
                name=request.name,
                description=request.description,
                user_id=user_id,
                is_default=request.is_default
            )
            
            db.add(watchlist)
            await db.commit()
            await db.refresh(watchlist)
            
            return WatchlistResponse(
                id=str(watchlist.id),
                name=watchlist.name,
                description=watchlist.description,
                is_default=watchlist.is_default,
                items_count=0,
                created_at=watchlist.created_at
            )
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Watchlist creation failed: {str(e)}")

@router.get("/watchlists/{watchlist_id}/items", response_model=List[WatchlistItemResponse])
async def get_watchlist_items(watchlist_id: str):
    """
    📄 **Watchlist Items**: Get all instruments in a watchlist
    """
    async with get_db_session() as db:
        try:
            query = (
                select(WatchlistItem, Instrument, InstrumentExtended)
                .join(Instrument, WatchlistItem.instrument_id == Instrument.id)
                .outerjoin(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                .where(WatchlistItem.watchlist_id == watchlist_id)
                .order_by(WatchlistItem.sort_order, WatchlistItem.added_at)
            )
            
            result = await db.execute(query)
            items_data = result.fetchall()
            
            return [
                WatchlistItemResponse(
                    id=str(item.id),
                    instrument=InstrumentResponse(
                        id=str(instrument.id),
                        instrument_token=instrument.instrument_token,
                        tradingsymbol=instrument.tradingsymbol,
                        name=instrument.name,
                        last_price=float(instrument.last_price) if instrument.last_price else None,
                        exchange=instrument.exchange,
                        instrument_type=instrument.instrument_type.value,
                        industry_group=extended.industry_group.value if extended and extended.industry_group else None,
                        sector=extended.sector if extended else None,
                        market_segment=extended.market_segment.value if extended and extended.market_segment else None,
                        market_cap=extended.market_cap if extended else None,
                        pe_ratio=float(extended.pe_ratio) if extended and extended.pe_ratio else None,
                        pb_ratio=float(extended.pb_ratio) if extended and extended.pb_ratio else None,
                        is_f_and_o=extended.is_f_and_o if extended else False,
                        nifty_indices=extended.nifty_indices if extended else None
                    ),
                    notes=item.notes,
                    price_alert_high=float(item.price_alert_high) if item.price_alert_high else None,
                    price_alert_low=float(item.price_alert_low) if item.price_alert_low else None,
                    added_at=item.added_at
                ) for item, instrument, extended in items_data
            ]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watchlist items fetch failed: {str(e)}")

@router.post("/watchlists/{watchlist_id}/items")
async def add_to_watchlist(watchlist_id: str, request: WatchlistAddItemRequest):
    """
    ➕ **Add to Watchlist**: Add instrument to watchlist
    """
    async with get_db_session() as db:
        try:
            # Check if already exists
            existing = await db.execute(
                select(WatchlistItem).where(
                    and_(
                        WatchlistItem.watchlist_id == watchlist_id,
                        WatchlistItem.instrument_id == request.instrument_id
                    )
                )
            )
            
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Instrument already in watchlist")
            
            # Get next sort order
            max_order = await db.execute(
                select(func.max(WatchlistItem.sort_order))
                .where(WatchlistItem.watchlist_id == watchlist_id)
            )
            next_order = (max_order.scalar() or 0) + 1
            
            item = WatchlistItem(
                watchlist_id=watchlist_id,
                instrument_id=request.instrument_id,
                notes=request.notes,
                price_alert_high=Decimal(str(request.price_alert_high)) if request.price_alert_high else None,
                price_alert_low=Decimal(str(request.price_alert_low)) if request.price_alert_low else None,
                sort_order=next_order
            )
            
            db.add(item)
            await db.commit()
            
            return {"message": "Instrument added to watchlist", "item_id": str(item.id)}
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Add to watchlist failed: {str(e)}")

@router.get("/sectors/analysis", response_model=List[SectorAnalysisResponse])
async def get_sector_analysis():
    """
    🏢 **Sector Analysis**: Analyze performance by sector
    
    Returns sector-wise performance metrics and top performers.
    """
    async with get_db_session() as db:
        try:
            today = datetime.now().date()
            
            # Get sector performance
            sector_query = (
                select(SectorPerformance)
                .where(func.date(SectorPerformance.stats_date) == today)
                .order_by(SectorPerformance.avg_change_percent.desc())
            )
            
            result = await db.execute(sector_query)
            sectors_data = result.fetchall()
            
            # For each sector, get top performers
            response = []
            for sector in sectors_data:
                # Get top 3 performers in this sector
                performers_query = (
                    select(Instrument, InstrumentExtended, MarketStats)
                    .join(InstrumentExtended, Instrument.id == InstrumentExtended.instrument_id)
                    .join(MarketStats, Instrument.id == MarketStats.instrument_id)
                    .where(
                        and_(
                            InstrumentExtended.sector == sector.sector_name,
                            func.date(MarketStats.stats_date) == today
                        )
                    )
                    .order_by(MarketStats.price_change_percent.desc())
                    .limit(3)
                )
                
                performers_result = await db.execute(performers_query)
                performers_data = performers_result.fetchall()
                
                top_performers = [
                    InstrumentResponse(
                        id=str(i.id),
                        instrument_token=i.instrument_token,
                        tradingsymbol=i.tradingsymbol,
                        name=i.name,
                        last_price=float(s.close_price) if s.close_price else None,
                        exchange=i.exchange,
                        instrument_type=i.instrument_type.value,
                        industry_group=e.industry_group.value if e.industry_group else None,
                        sector=e.sector,
                        market_segment=e.market_segment.value if e.market_segment else None,
                        market_cap=e.market_cap,
                        pe_ratio=float(e.pe_ratio) if e.pe_ratio else None,
                        pb_ratio=float(e.pb_ratio) if e.pb_ratio else None,
                        is_f_and_o=e.is_f_and_o,
                        nifty_indices=e.nifty_indices
                    ) for i, e, s in performers_data
                ]
                
                response.append(SectorAnalysisResponse(
                    sector_name=sector.sector_name,
                    industry_group=sector.industry_group.value if sector.industry_group else None,
                    total_stocks=sector.total_stocks,
                    gainers_count=sector.gainers_count,
                    losers_count=sector.losers_count,
                    avg_change_percent=float(sector.avg_change_percent),
                    top_performers=top_performers
                ))
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sector analysis failed: {str(e)}")
