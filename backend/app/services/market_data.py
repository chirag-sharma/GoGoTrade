"""
Market Data Service for Indian Stock Markets
Integrates with NSE/BSE APIs and provides real-time market data
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    timestamp: datetime

@dataclass
class OHLCData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class MarketDataService:
    """Service for fetching real-time and historical market data"""
    
    def __init__(self):
        self.base_urls = {
            'nse': 'https://www.nseindia.com/api',
            'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart'
        }
        self.session = None
        self.cache = {}
        self.cache_duration = 60  # seconds
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_market_data(self, symbols: List[str]) -> List[MarketData]:
        """Fetch real-time market data for given symbols"""
        try:
            market_data = []
            
            for symbol in symbols:
                # Check cache first
                cached_data = self._get_from_cache(symbol)
                if cached_data:
                    market_data.append(cached_data)
                    continue
                
                # Fetch from API
                data = await self._fetch_symbol_data(symbol)
                if data:
                    market_data.append(data)
                    self._cache_data(symbol, data)
            
            return market_data
        
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            # Return mock data for development
            return self._get_mock_data(symbols)
    
    async def _fetch_symbol_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch data for a single symbol from NSE/Yahoo Finance"""
        try:
            # Try NSE first (for Indian stocks)
            if symbol.endswith('.NS') or symbol in ['NIFTY', 'SENSEX']:
                return await self._fetch_from_nse(symbol)
            
            # Fallback to Yahoo Finance
            return await self._fetch_from_yahoo(symbol)
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def _fetch_from_nse(self, symbol: str) -> Optional[MarketData]:
        """Fetch data from NSE (mock implementation for now)"""
        # Mock implementation - replace with actual NSE API
        await asyncio.sleep(0.1)  # Simulate API delay
        
        base_prices = {
            'NIFTY': 19500,
            'SENSEX': 65000,
            'RELIANCE.NS': 2500,
            'TCS.NS': 3600,
            'INFY.NS': 1400,
        }
        
        if symbol not in base_prices:
            return None
        
        # Simulate price fluctuations
        import random
        base_price = base_prices[symbol]
        change_percent = random.uniform(-2.5, 2.5)
        change = base_price * (change_percent / 100)
        current_price = base_price + change
        
        return MarketData(
            symbol=symbol,
            price=current_price,
            change=change,
            change_percent=change_percent,
            volume=random.randint(100000, 10000000),
            high=current_price + abs(change) * 0.5,
            low=current_price - abs(change) * 0.5,
            open=base_price,
            timestamp=datetime.now()
        )
    
    async def _fetch_from_yahoo(self, symbol: str) -> Optional[MarketData]:
        """Fetch data from Yahoo Finance API"""
        try:
            url = f"{self.base_urls['yahoo']}/{symbol}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Parse Yahoo Finance response
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    return MarketData(
                        symbol=symbol,
                        price=meta['regularMarketPrice'],
                        change=meta['regularMarketPrice'] - meta['previousClose'],
                        change_percent=((meta['regularMarketPrice'] - meta['previousClose']) / meta['previousClose']) * 100,
                        volume=meta['regularMarketVolume'],
                        high=meta['regularMarketDayHigh'],
                        low=meta['regularMarketDayLow'],
                        open=meta['regularMarketOpen'],
                        timestamp=datetime.fromtimestamp(meta['regularMarketTime'])
                    )
        
        except Exception as e:
            logger.error(f"Yahoo Finance API error for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[OHLCData]:
        """Fetch historical OHLC data for technical analysis"""
        try:
            # Mock implementation - replace with actual API
            historical_data = []
            base_price = 2500  # Mock base price
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i)
                
                # Simulate price movement
                import random
                daily_change = random.uniform(-0.05, 0.05)
                open_price = base_price * (1 + daily_change)
                high_price = open_price * (1 + abs(daily_change) * 0.5)
                low_price = open_price * (1 - abs(daily_change) * 0.5)
                close_price = open_price + random.uniform(-50, 50)
                
                historical_data.append(OHLCData(
                    symbol=symbol,
                    timestamp=date,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=random.randint(100000, 1000000)
                ))
                
                base_price = close_price
            
            return historical_data
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    def _get_from_cache(self, symbol: str) -> Optional[MarketData]:
        """Get data from cache if valid"""
        if symbol in self.cache:
            cached_time, data = self.cache[symbol]
            if (datetime.now() - cached_time).seconds < self.cache_duration:
                return data
        return None
    
    def _cache_data(self, symbol: str, data: MarketData):
        """Cache market data"""
        self.cache[symbol] = (datetime.now(), data)
    
    def _get_mock_data(self, symbols: List[str]) -> List[MarketData]:
        """Generate mock data for development/testing"""
        mock_data = []
        base_prices = {
            'NIFTY': 19500,
            'SENSEX': 65000, 
            'RELIANCE.NS': 2500,
            'TCS.NS': 3600,
            'INFY.NS': 1400,
        }
        
        import random
        for symbol in symbols:
            base_price = base_prices.get(symbol, 1000)
            change_percent = random.uniform(-2.0, 2.0)
            change = base_price * (change_percent / 100)
            
            mock_data.append(MarketData(
                symbol=symbol,
                price=base_price + change,
                change=change,
                change_percent=change_percent,
                volume=random.randint(100000, 5000000),
                high=base_price + abs(change) * 1.2,
                low=base_price - abs(change) * 1.2,
                open=base_price,
                timestamp=datetime.now()
            ))
        
        return mock_data

# Global market data service instance
market_service = MarketDataService()
