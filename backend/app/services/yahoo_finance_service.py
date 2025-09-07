"""
Yahoo Finance data integration service.
Provides real market data using yfinance for live prices and historical data.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class YahooFinanceDataService:
    """
    Service for fetching real market data from Yahoo Finance.
    Handles both live prices and historical OHLCV data.
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.symbol_mapping = {
            # Indian stocks - add .NS suffix for NSE
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS', 
            'INFY': 'INFY.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'HINDUNILVR': 'HINDUNILVR.NS',
            'ITC': 'ITC.NS',
            'SBIN': 'SBIN.NS',
            'BHARTIARTL': 'BHARTIARTL.NS',
            'KOTAKBANK': 'KOTAKBANK.NS',
            
            # US stocks - use as-is
            'AAPL': 'AAPL',
            'GOOGL': 'GOOGL',
            'MSFT': 'MSFT',
            'TSLA': 'TSLA',
            'AMZN': 'AMZN',
            'META': 'META',
            'NVDA': 'NVDA',
            'NFLX': 'NFLX',
            'AMD': 'AMD',
            'INTC': 'INTC'
        }
        
        # Cache for ticker objects
        self.ticker_cache: Dict[str, yf.Ticker] = {}
        self.last_update_time: Dict[str, datetime] = {}
        
    def _get_yf_symbol(self, symbol: str) -> str:
        """
        Convert symbol to Yahoo Finance format.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Yahoo Finance symbol
        """
        return self.symbol_mapping.get(symbol, symbol)
    
    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """
        Get or create yfinance Ticker object.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            yfinance Ticker object
        """
        yf_symbol = self._get_yf_symbol(symbol)
        
        if yf_symbol not in self.ticker_cache:
            self.ticker_cache[yf_symbol] = yf.Ticker(yf_symbol)
        
        return self.ticker_cache[yf_symbol]
    
    async def get_live_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current live price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with current price data
        """
        try:
            # Use thread executor for synchronous yfinance calls
            loop = asyncio.get_event_loop()
            ticker = self._get_ticker(symbol)
            
            # Get current price info
            info = await loop.run_in_executor(
                self.executor, 
                self._fetch_ticker_info, 
                ticker
            )
            
            if not info:
                return None
            
            # Get fast info for real-time data
            try:
                fast_info = await loop.run_in_executor(
                    self.executor,
                    lambda: ticker.fast_info
                )
                current_price = fast_info.get('lastPrice') or fast_info.get('regularMarketPrice')
                previous_close = fast_info.get('previousClose') or fast_info.get('regularMarketPreviousClose')
            except:
                # Fallback to regular info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            
            if not current_price or not previous_close:
                logger.warning(f"Missing price data for {symbol}")
                return None
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            # Get volume
            volume = info.get('volume') or info.get('regularMarketVolume', 0)
            
            return {
                'symbol': symbol,
                'ltp': round(float(current_price), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_percent), 2),
                'volume': int(volume) if volume else 0,
                'previous_close': round(float(previous_close), 2),
                'market_cap': info.get('marketCap'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'UNKNOWN'),
                'source': 'yahoo_finance',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get live price for {symbol}: {e}")
            return None
    
    def _fetch_ticker_info(self, ticker: yf.Ticker) -> Optional[Dict]:
        """
        Fetch ticker info in thread executor.
        
        Args:
            ticker: yfinance Ticker object
            
        Returns:
            Ticker info dictionary
        """
        try:
            return ticker.info
        except Exception as e:
            logger.error(f"Failed to fetch ticker info: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1d", 
        interval: str = "1m"
    ) -> Optional[List[Dict]]:
        """
        Get historical OHLCV data.
        
        Args:
            symbol: Trading symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            List of OHLCV dictionaries
        """
        try:
            loop = asyncio.get_event_loop()
            ticker = self._get_ticker(symbol)
            
            # Fetch historical data
            hist_data = await loop.run_in_executor(
                self.executor,
                lambda: ticker.history(period=period, interval=interval)
            )
            
            if hist_data.empty:
                logger.warning(f"No historical data for {symbol}")
                return None
            
            # Convert to list of dictionaries
            ohlcv_data = []
            for timestamp, row in hist_data.iterrows():
                if pd.isna(row['Close']) or row['Close'] <= 0:
                    continue
                    
                ohlcv_data.append({
                    'timestamp': timestamp.isoformat(),
                    'open': round(float(row['Open']), 4),
                    'high': round(float(row['High']), 4),
                    'low': round(float(row['Low']), 4),
                    'close': round(float(row['Close']), 4),
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0
                })
            
            return ohlcv_data
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return None
    
    async def get_multiple_live_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get live prices for multiple symbols efficiently.
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary mapping symbols to price data
        """
        try:
            # Convert to Yahoo Finance symbols
            yf_symbols = [self._get_yf_symbol(symbol) for symbol in symbols]
            yf_symbols_str = ' '.join(yf_symbols)
            
            loop = asyncio.get_event_loop()
            
            # Fetch data for multiple tickers
            tickers_data = await loop.run_in_executor(
                self.executor,
                lambda: yf.download(
                    yf_symbols_str,
                    period="2d",  # Get 2 days to calculate change
                    interval="1d",
                    progress=False,
                    threads=True
                )
            )
            
            prices = {}
            
            if len(symbols) == 1:
                # Single symbol case
                symbol = symbols[0]
                if not tickers_data.empty and len(tickers_data) >= 2:
                    latest = tickers_data.iloc[-1]
                    previous = tickers_data.iloc[-2]
                    
                    current_price = latest['Close']
                    previous_close = previous['Close']
                    volume = latest['Volume']
                    
                    if not pd.isna(current_price) and not pd.isna(previous_close):
                        change = current_price - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        prices[symbol] = {
                            'symbol': symbol,
                            'ltp': round(float(current_price), 2),
                            'change': round(float(change), 2),
                            'change_percent': round(float(change_percent), 2),
                            'volume': int(volume) if not pd.isna(volume) else 0,
                            'previous_close': round(float(previous_close), 2),
                            'source': 'yahoo_finance_batch',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
            else:
                # Multiple symbols case
                for i, symbol in enumerate(symbols):
                    yf_symbol = yf_symbols[i]
                    
                    try:
                        if ('Close', yf_symbol) in tickers_data.columns:
                            close_data = tickers_data[('Close', yf_symbol)].dropna()
                            volume_data = tickers_data[('Volume', yf_symbol)].dropna()
                            
                            if len(close_data) >= 2:
                                current_price = close_data.iloc[-1]
                                previous_close = close_data.iloc[-2]
                                volume = volume_data.iloc[-1] if len(volume_data) > 0 else 0
                                
                                change = current_price - previous_close
                                change_percent = (change / previous_close) * 100
                                
                                prices[symbol] = {
                                    'symbol': symbol,
                                    'ltp': round(float(current_price), 2),
                                    'change': round(float(change), 2),
                                    'change_percent': round(float(change_percent), 2),
                                    'volume': int(volume) if not pd.isna(volume) else 0,
                                    'previous_close': round(float(previous_close), 2),
                                    'source': 'yahoo_finance_batch',
                                    'timestamp': datetime.now(timezone.utc).isoformat()
                                }
                    except Exception as e:
                        logger.warning(f"Failed to process data for {symbol}: {e}")
                        continue
            
            return prices
            
        except Exception as e:
            logger.error(f"Failed to get multiple live prices: {e}")
            return {}
    
    async def get_market_status(self) -> Dict:
        """
        Get market status information.
        
        Returns:
            Market status dictionary
        """
        try:
            # Use a major index to determine market status
            loop = asyncio.get_event_loop()
            spy_ticker = yf.Ticker("SPY")  # S&P 500 ETF
            
            info = await loop.run_in_executor(
                self.executor,
                lambda: spy_ticker.info
            )
            
            # Check if market is currently open
            now = datetime.now()
            market_state = info.get('marketState', 'UNKNOWN')
            
            # Basic market hours check (US markets)
            is_market_open = False
            market_session = "Closed"
            
            if market_state in ['REGULAR', 'OPEN']:
                is_market_open = True
                market_session = "Regular"
            elif market_state == 'PRE':
                market_session = "Pre-Market"
            elif market_state == 'POST':
                market_session = "After-Hours"
            
            return {
                'is_market_open': is_market_open,
                'market_session': market_session,
                'market_state': market_state,
                'timezone': info.get('timeZoneFullName', 'UTC'),
                'currency': info.get('currency', 'USD'),
                'last_update': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get market status: {e}")
            return {
                'is_market_open': False,
                'market_session': 'Unknown',
                'market_state': 'UNKNOWN',
                'error': str(e),
                'last_update': datetime.now(timezone.utc).isoformat()
            }
    
    async def search_symbols(self, query: str) -> List[Dict]:
        """
        Search for symbols matching the query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching symbols with info
        """
        try:
            # For now, return symbols from our mapping that match the query
            matching_symbols = []
            query_lower = query.lower()
            
            for symbol, yf_symbol in self.symbol_mapping.items():
                if query_lower in symbol.lower():
                    matching_symbols.append({
                        'symbol': symbol,
                        'yf_symbol': yf_symbol,
                        'name': symbol,  # Would need additional API call to get full name
                        'exchange': 'NSE' if yf_symbol.endswith('.NS') else 'NASDAQ'
                    })
            
            return matching_symbols[:10]  # Limit to 10 results
            
        except Exception as e:
            logger.error(f"Failed to search symbols: {e}")
            return []
    
    async def cleanup(self):
        """Clean up resources."""
        if self.executor:
            self.executor.shutdown(wait=True)
        self.ticker_cache.clear()
        logger.info("Yahoo Finance service cleaned up")


# Global instance
yahoo_finance_service = YahooFinanceDataService()
