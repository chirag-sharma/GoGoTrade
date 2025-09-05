"""
Chart-related endpoints
Handles chart data formatting and technical indicators
"""

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from app.core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter()


class ChartData(BaseModel):
    """Chart data response model"""
    symbol: str
    timeframe: str
    candlesticks: List[dict]
    indicators: dict = {}


@router.get("/chart-data/{symbol}")
async def getChartData(symbol: str, timeframe: str = "5minute", db: AsyncSession = Depends(get_db_session)) -> ChartData:
    """Get formatted chart data for TradingView Lightweight Charts"""
    try:
        # Get OHLCV data from database
        query = text("""
            SELECT timestamp, open, high, low, close, volume
            FROM ohlcv_data 
            WHERE symbol = :symbol 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        result = await db.execute(query, {"symbol": symbol})
        rows = result.fetchall()
        
        if not rows:
            # Fallback to mock data if no database data
            candlesticks = []
            base_date = datetime.now() - timedelta(days=30)
            for i in range(30):
                date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
                price = 100 + random.uniform(-10, 10)
                candlesticks.append({
                    "time": date,
                    "open": round(price + random.uniform(-2, 2), 2),
                    "high": round(price + random.uniform(0, 5), 2),
                    "low": round(price - random.uniform(0, 5), 2),
                    "close": round(price + random.uniform(-2, 2), 2)
                })
        else:
            # Convert database data to chart format
            candlesticks = []
            for row in reversed(rows):  # Reverse to get chronological order
                # Convert timestamp to YYYY-MM-DD format for Lightweight Charts
                candlesticks.append({
                    "time": row[0].strftime("%Y-%m-%d") if hasattr(row[0], 'strftime') else str(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4])
                })
        
        return ChartData(
            symbol=symbol,
            timeframe=timeframe,
            candlesticks=candlesticks,
            indicators={
                "ema20": [99.5],
                "rsi": [65.0]
            }
        )
    except Exception as e:
        print(f"Chart data error: {e}")
        # Fallback to simple mock data
        return ChartData(
            symbol=symbol,
            timeframe=timeframe,
            candlesticks=[
                {
                    "time": "2025-08-25",
                    "open": 99.0,
                    "high": 101.0,
                    "low": 98.0,
                    "close": 100.0
                }
            ],
            indicators={
                "ema20": [99.5],
                "rsi": [65.0]
            }
        )


@router.get("/{symbol}/data")
async def getChartCandlestickData(symbol: str, timeframe: str = "5minute", db: AsyncSession = Depends(get_db_session)):
    """Get candlestick data formatted directly for TradingView Lightweight Charts"""
    try:
        # Get OHLCV data from database
        query = text("""
            SELECT timestamp, open, high, low, close, volume
            FROM ohlcv_data 
            WHERE symbol = :symbol 
            ORDER BY timestamp ASC 
            LIMIT 100
        """)
        result = await db.execute(query, {"symbol": symbol})
        rows = result.fetchall()
        
        if rows:
            # Format database data for TradingView
            candlesticks = []
            for row in rows:
                candlesticks.append({
                    "time": row[0].strftime("%Y-%m-%d") if hasattr(row[0], 'strftime') else str(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4])
                })
            return candlesticks
        else:
            # Fallback to mock data if no database data
            base_date = datetime.now() - timedelta(days=30)
            candlesticks = []
            base_price = 100.0
            
            for i in range(30):
                date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
                # Generate realistic price movement
                open_price = base_price + random.uniform(-2, 2)
                high_price = open_price + random.uniform(0, 5)
                low_price = open_price - random.uniform(0, 5)
                close_price = open_price + random.uniform(-3, 3)
                
                candlesticks.append({
                    "time": date,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2)
                })
                base_price = close_price  # Next day starts from previous close
            
            return candlesticks
        
    except Exception as e:
        print(f"Chart data error: {e}")
        # Return basic sample data as final fallback
        return [
            { "time": "2018-12-22", "open": 75.16, "high": 82.84, "low": 36.16, "close": 45.72 },
            { "time": "2018-12-23", "open": 45.12, "high": 53.90, "low": 45.12, "close": 48.09 },
            { "time": "2018-12-24", "open": 60.71, "high": 60.71, "low": 53.39, "close": 59.29 },
            { "time": "2018-12-25", "open": 68.26, "high": 68.26, "low": 59.04, "close": 60.50 },
            { "time": "2018-12-26", "open": 67.71, "high": 105.85, "low": 66.67, "close": 91.04 },
            { "time": "2018-12-27", "open": 91.04, "high": 121.40, "low": 82.70, "close": 111.40 },
            { "time": "2018-12-28", "open": 111.51, "high": 142.83, "low": 103.34, "close": 131.25 },
            { "time": "2018-12-29", "open": 131.33, "high": 151.17, "low": 77.68, "close": 96.43 },
            { "time": "2018-12-30", "open": 106.33, "high": 110.20, "low": 90.39, "close": 98.10 },
            { "time": "2018-12-31", "open": 109.87, "high": 114.69, "low": 85.66, "close": 111.26 }
        ]


@router.get("/indicators/{symbol}")
async def getIndicators(symbol: str, timeframe: str = "5minute") -> dict:
    """Get technical indicators for a symbol"""
    # TODO: Implement pandas-ta calculations
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "indicators": {
            "ema20": [99.5, 99.8, 100.0],
            "sma50": [98.0, 98.5, 99.0],
            "rsi": [65.0, 62.0, 58.0],
            "macd": {
                "macd": [0.5, 0.8, 1.0],
                "signal": [0.3, 0.6, 0.9],
                "histogram": [0.2, 0.2, 0.1]
            }
        }
    }