"""
NSE Securities Data Fetching Service
Fetches complete NSE instruments list and market data.
"""

import asyncio
import logging
import json
import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import aiohttp
from pathlib import Path
from sqlalchemy import select

from app.core.database import db_manager
from app.models import Instrument, InstrumentType
from app.models.market_data import (
    InstrumentExtended, MarketStats, SectorPerformance, 
    IndustryGroup, MarketSegment
)

logger = logging.getLogger(__name__)


class NSEDataService:
    """
    Service for fetching complete NSE securities data.
    """
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        # NSE API endpoints
        self.nse_urls = {
            'equity_master': 'https://www.nseindia.com/api/equity-master',
            'market_status': 'https://www.nseindia.com/api/marketStatus',
            'gainers': 'https://www.nseindia.com/api/equity-stockIndices?index=gainers',
            'losers': 'https://www.nseindia.com/api/equity-stockIndices?index=losers',
            'active_securities': 'https://www.nseindia.com/api/equity-stockIndices?index=active',
            'nifty_indices': 'https://www.nseindia.com/api/allIndices',
        }
        
        # Industry mapping (NSE to our enum)
        self.industry_mapping = {
            'AUTOMOBILE': IndustryGroup.AUTOMOBILE,
            'BANKING': IndustryGroup.BANKING,
            'CONSUMER DURABLES': IndustryGroup.CONSUMER_DURABLES,
            'CONSUMER GOODS': IndustryGroup.CONSUMER_GOODS,
            'ENERGY': IndustryGroup.ENERGY,
            'FINANCIAL SERVICES': IndustryGroup.FINANCIAL_SERVICES,
            'FMCG': IndustryGroup.FMCG,
            'HEALTHCARE': IndustryGroup.HEALTHCARE,
            'IT': IndustryGroup.IT,
            'MEDIA': IndustryGroup.MEDIA,
            'METALS': IndustryGroup.METALS,
            'PHARMA': IndustryGroup.PHARMA,
            'TELECOM': IndustryGroup.TELECOM,
            'INFRASTRUCTURE': IndustryGroup.INFRASTRUCTURE,
            'OIL & GAS': IndustryGroup.OIL_AND_GAS,
            'CHEMICALS': IndustryGroup.CHEMICALS,
            'TEXTILES': IndustryGroup.TEXTILES,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def fetch_nse_equity_master(self) -> Optional[List[Dict]]:
        """
        Fetch complete NSE equity master list.
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(self.nse_urls['equity_master']) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Fetched {len(data)} NSE equity instruments")
                    return data
                else:
                    logger.error(f"NSE API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to fetch NSE equity master: {e}")
            return None

    async def fetch_nifty_indices_data(self) -> Optional[Dict]:
        """
        Fetch NIFTY indices composition and data.
        """
        try:
            async with self.session.get(self.nse_urls['nifty_indices']) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Fetched NIFTY indices data")
                    return data
                else:
                    logger.error(f"NIFTY indices API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to fetch NIFTY indices: {e}")
            return None

    async def fetch_market_movers(self) -> Dict[str, List]:
        """
        Fetch market movers (gainers, losers, most active).
        """
        movers = {'gainers': [], 'losers': [], 'active': []}
        
        try:
            for category in ['gainers', 'losers', 'active_securities']:
                async with self.session.get(self.nse_urls[category]) as response:
                    if response.status == 200:
                        data = await response.json()
                        key = category.replace('_securities', '')
                        movers[key] = data.get('data', [])
                        
            logger.info("✅ Fetched market movers data")
            return movers
            
        except Exception as e:
            logger.error(f"Failed to fetch market movers: {e}")
            return movers

    def _determine_market_segment(self, market_cap: int) -> MarketSegment:
        """
        Determine market segment based on market cap.
        Based on SEBI guidelines (approximate thresholds in crores).
        """
        if market_cap >= 2000000:  # 20,000 Cr
            return MarketSegment.LARGE_CAP
        elif market_cap >= 50000:   # 500 Cr
            return MarketSegment.MID_CAP
        elif market_cap >= 5000:    # 50 Cr
            return MarketSegment.SMALL_CAP
        else:
            return MarketSegment.MICRO_CAP

    def _parse_industry_group(self, industry: str) -> Optional[IndustryGroup]:
        """
        Map NSE industry to our IndustryGroup enum.
        """
        if not industry:
            return None
            
        industry_upper = industry.upper()
        return self.industry_mapping.get(industry_upper)

    async def save_instruments_to_db(self, instruments_data: List[Dict]) -> int:
        """
        Save NSE instruments to database.
        """
        saved_count = 0
        
        async with db_manager.get_session() as db:
            try:
                for item in instruments_data:
                    # Create base instrument
                    instrument = Instrument(
                        instrument_token=item.get('symbol_id', 0),
                        exchange_token=item.get('token', 0),
                        tradingsymbol=item.get('symbol', ''),
                        name=item.get('company_name', item.get('symbol', '')),
                        last_price=Decimal(str(item.get('last_price', 0))) if item.get('last_price') else None,
                        tick_size=Decimal('0.05'),
                        lot_size=1,
                        instrument_type=InstrumentType.EQUITY,
                        segment='NSE',
                        exchange='NSE'
                    )
                    
                    db.add(instrument)
                    await db.flush()  # Get the ID
                    
                    # Create extended info
                    market_cap = item.get('market_cap')
                    if market_cap:
                        market_cap = int(float(market_cap) * 10000000)  # Convert to INR
                    
                    extended = InstrumentExtended(
                        instrument_id=instrument.id,
                        industry_group=self._parse_industry_group(item.get('industry')),
                        sector=item.get('sector'),
                        market_segment=self._determine_market_segment(market_cap) if market_cap else None,
                        market_cap=market_cap,
                        pe_ratio=Decimal(str(item.get('pe_ratio'))) if item.get('pe_ratio') else None,
                        pb_ratio=Decimal(str(item.get('pb_ratio'))) if item.get('pb_ratio') else None,
                        isin=item.get('isin'),
                        is_active=True,
                        is_f_and_o=item.get('derivatives_available', False),
                        data_last_updated=datetime.now(timezone.utc)
                    )
                    
                    db.add(extended)
                    saved_count += 1
                
                await db.commit()
                logger.info(f"✅ Saved {saved_count} instruments to database")
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to save instruments: {e}")
                raise
        
        return saved_count

    async def update_market_stats(self, movers_data: Dict) -> None:
        """
        Update daily market statistics.
        """
        stats_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        async with db_manager.get_session() as db:
            try:
                # Process gainers, losers, and active stocks
                for category, stocks in movers_data.items():
                    rank = 1
                    for stock in stocks[:100]:  # Top 100 only
                        symbol = stock.get('symbol')
                        if not symbol:
                            continue
                        
                        # Find instrument
                        instrument = await db.execute(
                            select(Instrument).where(Instrument.tradingsymbol == symbol)
                        )
                        instrument = instrument.scalar_one_or_none()
                        
                        if not instrument:
                            continue
                        
                        # Create or update market stats
                        stats = MarketStats(
                            instrument_id=instrument.id,
                            stats_date=stats_date,
                            volume=stock.get('total_traded_volume', 0),
                            turnover=stock.get('total_traded_value', 0),
                            open_price=Decimal(str(stock.get('open', 0))),
                            high_price=Decimal(str(stock.get('day_high', 0))),
                            low_price=Decimal(str(stock.get('day_low', 0))),
                            close_price=Decimal(str(stock.get('last_price', 0))),
                            price_change=Decimal(str(stock.get('change', 0))),
                            price_change_percent=Decimal(str(stock.get('percent_change', 0))),
                        )
                        
                        # Set rank based on category
                        if category == 'gainers':
                            stats.gainer_rank = rank
                        elif category == 'losers':
                            stats.loser_rank = rank
                        elif category == 'active':
                            stats.volume_rank = rank
                        
                        db.add(stats)
                        rank += 1
                
                await db.commit()
                logger.info("✅ Updated market statistics")
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to update market stats: {e}")
                raise

    async def full_nse_data_sync(self) -> Dict[str, int]:
        """
        Complete NSE data synchronization.
        """
        results = {'instruments': 0, 'market_stats': 0, 'errors': 0}
        
        try:
            async with self:  # Use context manager
                # 1. Fetch and save instruments
                logger.info("🔄 Starting NSE instruments sync...")
                instruments_data = await self.fetch_nse_equity_master()
                
                if instruments_data:
                    results['instruments'] = await self.save_instruments_to_db(instruments_data)
                
                # 2. Fetch and save market movers
                logger.info("🔄 Starting market movers sync...")
                movers_data = await self.fetch_market_movers()
                
                if movers_data:
                    await self.update_market_stats(movers_data)
                    results['market_stats'] = 1
                
                logger.info(f"✅ NSE sync completed: {results}")
                
        except Exception as e:
            logger.error(f"NSE sync failed: {e}")
            results['errors'] = 1
        
        return results


# CLI script for manual data sync
async def sync_nse_data():
    """Manual NSE data synchronization."""
    service = NSEDataService()
    results = await service.full_nse_data_sync()
    
    print(f"NSE Data Sync Results:")
    print(f"  Instruments: {results['instruments']}")
    print(f"  Market Stats: {results['market_stats']}")
    print(f"  Errors: {results['errors']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(sync_nse_data())
