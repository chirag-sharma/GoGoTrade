"""
Market data processor for real-time analysis and signal generation.
Handles technical analysis and pattern recognition on live market data.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db_session
from app.models import Instrument, OHLCVData, TradingSignal
from app.services.advanced_ai import AdvancedAITradingEngine


logger = logging.getLogger(__name__)


class MarketDataProcessor:
    """
    Processes real-time market data and generates trading signals.
    """
    
    def __init__(self):
        self.ai_service = AdvancedAITradingEngine()
        self.price_history: Dict[str, List] = {}
        self.indicators_cache: Dict[str, Dict] = {}
        
    async def initialize(self):
        """Initialize the market data processor."""
        logger.info("Initializing market data processor...")
        # AI service is already initialized in constructor
        logger.info("Market data processor initialized successfully")
    
    async def generate_signal(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """
        Generate trading signal based on current price data.
        
        Args:
            symbol: Trading symbol
            price_data: Current price information
            
        Returns:
            Signal dictionary or None
        """
        try:
            # Get recent OHLCV data for analysis
            ohlcv_data = await self._get_recent_ohlcv(symbol, timeframe='1m', limit=100)
            
            if len(ohlcv_data) < 20:  # Need minimum data for analysis
                return None
            
            # Calculate technical indicators
            indicators = await self._calculate_indicators(ohlcv_data)
            
            # Get current price
            current_price = Decimal(str(price_data['ltp']))
            
            # Generate signal using AI service
            signal_data = {
                'symbol': symbol,
                'current_price': float(current_price),
                'indicators': indicators,
                'price_data': price_data,
                'ohlcv_data': ohlcv_data[-20:]  # Last 20 candles
            }
            
            signal = await self._analyze_signal(signal_data)
            
            if signal:
                # Store signal in database
                await self._store_trading_signal(symbol, signal, current_price)
                
            return signal
            
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {e}")
            return None
    
    async def _get_recent_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List[Dict]:
        """
        Get recent OHLCV data for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
            limit: Number of records to fetch
            
        Returns:
            List of OHLCV dictionaries
        """
        try:
            async with get_db_session() as db:
                # Get instrument
                instrument_result = await db.execute(
                    select(Instrument).where(Instrument.tradingsymbol == symbol)
                )
                instrument = instrument_result.scalar_one_or_none()
                
                if not instrument:
                    return []
                
                # Get recent OHLCV data
                ohlcv_result = await db.execute(
                    select(OHLCVData)
                    .where(
                        OHLCVData.instrument_id == instrument.id,
                        OHLCVData.timeframe == timeframe
                    )
                    .order_by(desc(OHLCVData.timestamp))
                    .limit(limit)
                )
                
                ohlcv_records = ohlcv_result.scalars().all()
                
                # Convert to list of dictionaries
                ohlcv_data = []
                for record in reversed(ohlcv_records):  # Reverse to get chronological order
                    ohlcv_data.append({
                        'timestamp': record.timestamp.isoformat(),
                        'open': float(record.open),
                        'high': float(record.high),
                        'low': float(record.low),
                        'close': float(record.close),
                        'volume': record.volume
                    })
                
                return ohlcv_data
                
        except Exception as e:
            logger.error(f"Failed to get OHLCV data for {symbol}: {e}")
            return []
    
    async def _calculate_indicators(self, ohlcv_data: List[Dict]) -> Dict:
        """
        Calculate technical indicators from OHLCV data.
        
        Args:
            ohlcv_data: List of OHLCV dictionaries
            
        Returns:
            Dictionary of calculated indicators
        """
        try:
            # Convert to pandas DataFrame for easier calculation
            df = pd.DataFrame(ohlcv_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            indicators = {}
            
            # Simple Moving Averages
            indicators['sma_10'] = df['close'].rolling(window=10).mean().iloc[-1] if len(df) >= 10 else None
            indicators['sma_20'] = df['close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else None
            indicators['sma_50'] = df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
            
            # Exponential Moving Averages
            indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1] if len(df) >= 12 else None
            indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1] if len(df) >= 26 else None
            
            # RSI (Relative Strength Index)
            if len(df) >= 14:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            if indicators['ema_12'] and indicators['ema_26']:
                macd_line = indicators['ema_12'] - indicators['ema_26']
                indicators['macd'] = macd_line
                
                # MACD Signal line (9-period EMA of MACD)
                if len(df) >= 35:  # Need enough data for MACD signal
                    macd_series = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
                    indicators['macd_signal'] = macd_series.ewm(span=9).mean().iloc[-1]
                    indicators['macd_histogram'] = macd_line - indicators['macd_signal']
            
            # Bollinger Bands
            if len(df) >= 20:
                sma_20 = df['close'].rolling(window=20).mean()
                std_20 = df['close'].rolling(window=20).std()
                indicators['bb_upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
                indicators['bb_lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
                indicators['bb_middle'] = sma_20.iloc[-1]
            
            # Volume indicators
            indicators['volume_sma_10'] = df['volume'].rolling(window=10).mean().iloc[-1] if len(df) >= 10 else None
            indicators['current_volume'] = df['volume'].iloc[-1]
            
            # Price action indicators
            indicators['current_price'] = df['close'].iloc[-1]
            indicators['price_change'] = df['close'].iloc[-1] - df['close'].iloc[-2] if len(df) >= 2 else 0
            indicators['price_change_percent'] = (indicators['price_change'] / df['close'].iloc[-2] * 100) if len(df) >= 2 else 0
            
            # Volatility (Average True Range approximation)
            if len(df) >= 14:
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                indicators['atr'] = true_range.rolling(window=14).mean().iloc[-1]
            
            # Support and Resistance levels
            if len(df) >= 20:
                recent_highs = df['high'].rolling(window=20).max()
                recent_lows = df['low'].rolling(window=20).min()
                indicators['resistance'] = recent_highs.iloc[-1]
                indicators['support'] = recent_lows.iloc[-1]
            
            # Clean up None values and convert to float
            cleaned_indicators = {}
            for key, value in indicators.items():
                if value is not None and not pd.isna(value):
                    cleaned_indicators[key] = float(value)
            
            return cleaned_indicators
            
        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
            return {}
    
    async def _analyze_signal(self, signal_data: Dict) -> Optional[Dict]:
        """
        Analyze data and generate trading signal.
        
        Args:
            signal_data: Data for signal analysis
            
        Returns:
            Signal dictionary or None
        """
        try:
            indicators = signal_data['indicators']
            current_price = signal_data['current_price']
            
            # Basic signal logic (this would be replaced with ML model)
            signal_strength = 0
            signal_type = 'HOLD'
            confidence = 0.5
            reasoning = []
            
            # RSI Analysis
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:
                    signal_strength += 2
                    reasoning.append(f"RSI oversold ({rsi:.1f})")
                elif rsi > 70:
                    signal_strength -= 2
                    reasoning.append(f"RSI overbought ({rsi:.1f})")
            
            # Moving Average Analysis
            if 'sma_10' in indicators and 'sma_20' in indicators:
                sma_10 = indicators['sma_10']
                sma_20 = indicators['sma_20']
                
                if current_price > sma_10 > sma_20:
                    signal_strength += 1
                    reasoning.append("Price above short MA, uptrend")
                elif current_price < sma_10 < sma_20:
                    signal_strength -= 1
                    reasoning.append("Price below short MA, downtrend")
            
            # MACD Analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                
                if macd > macd_signal:
                    signal_strength += 1
                    reasoning.append("MACD bullish crossover")
                else:
                    signal_strength -= 1
                    reasoning.append("MACD bearish crossover")
            
            # Volume Analysis
            if 'current_volume' in indicators and 'volume_sma_10' in indicators:
                current_vol = indicators['current_volume']
                avg_vol = indicators['volume_sma_10']
                
                if current_vol > avg_vol * 1.5:
                    signal_strength += 1 if signal_strength > 0 else -1
                    reasoning.append("High volume confirmation")
            
            # Bollinger Bands Analysis
            if all(key in indicators for key in ['bb_upper', 'bb_lower', 'bb_middle']):
                bb_upper = indicators['bb_upper']
                bb_lower = indicators['bb_lower']
                bb_middle = indicators['bb_middle']
                
                if current_price <= bb_lower:
                    signal_strength += 1
                    reasoning.append("Price at lower Bollinger Band")
                elif current_price >= bb_upper:
                    signal_strength -= 1
                    reasoning.append("Price at upper Bollinger Band")
            
            # Determine signal type and confidence
            if signal_strength >= 3:
                signal_type = 'BUY'
                confidence = min(0.9, 0.5 + (signal_strength * 0.1))
            elif signal_strength <= -3:
                signal_type = 'SELL'
                confidence = min(0.9, 0.5 + (abs(signal_strength) * 0.1))
            elif signal_strength >= 2:
                signal_type = 'BUY'
                confidence = 0.6
            elif signal_strength <= -2:
                signal_type = 'SELL'
                confidence = 0.6
            
            # Only return signals with reasonable confidence
            if confidence < 0.6:
                return None
            
            # Calculate target and stop loss
            target_price = None
            stop_loss = None
            
            if 'atr' in indicators and signal_type in ['BUY', 'SELL']:
                atr = indicators['atr']
                
                if signal_type == 'BUY':
                    target_price = current_price + (atr * 2)
                    stop_loss = current_price - (atr * 1.5)
                elif signal_type == 'SELL':
                    target_price = current_price - (atr * 2)
                    stop_loss = current_price + (atr * 1.5)
            
            signal = {
                'signal_type': signal_type,
                'confidence': round(confidence, 3),
                'target_price': round(target_price, 2) if target_price else None,
                'stop_loss': round(stop_loss, 2) if stop_loss else None,
                'reasoning': '; '.join(reasoning),
                'indicators_used': list(indicators.keys()),
                'signal_strength': signal_strength,
                'timeframe': '1m',
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Failed to analyze signal: {e}")
            return None
    
    async def _store_trading_signal(self, symbol: str, signal: Dict, current_price: Decimal):
        """
        Store trading signal in database.
        
        Args:
            symbol: Trading symbol
            signal: Signal dictionary
            current_price: Current market price
        """
        try:
            async with get_db_session() as db:
                # Get instrument
                instrument_result = await db.execute(
                    select(Instrument).where(Instrument.tradingsymbol == symbol)
                )
                instrument = instrument_result.scalar_one_or_none()
                
                if not instrument:
                    logger.warning(f"Instrument not found for signal: {symbol}")
                    return
                
                # Create signal record
                signal_record = TradingSignal(
                    instrument_id=instrument.id,
                    generated_at=datetime.now(timezone.utc),
                    strategy_name='real_time_technical',
                    signal_type=signal['signal_type'],
                    confidence_score=Decimal(str(signal['confidence'])),
                    target_price=Decimal(str(signal['target_price'])) if signal['target_price'] else None,
                    stop_loss=Decimal(str(signal['stop_loss'])) if signal['stop_loss'] else None,
                    timeframe=signal['timeframe'],
                    indicators_used=str(signal['indicators_used']),
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
                    is_active=True
                )
                
                db.add(signal_record)
                await db.commit()
                
                logger.info(f"Stored trading signal for {symbol}: {signal['signal_type']} ({signal['confidence']:.1%})")
                
        except Exception as e:
            logger.error(f"Failed to store trading signal: {e}")
    
    async def get_active_signals(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get active trading signals.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of active signals
        """
        try:
            async with get_db_session() as db:
                query = select(TradingSignal, Instrument).join(
                    Instrument, TradingSignal.instrument_id == Instrument.id
                ).where(
                    TradingSignal.is_active == True,
                    TradingSignal.expires_at > datetime.now(timezone.utc)
                )
                
                if symbol:
                    query = query.where(Instrument.tradingsymbol == symbol)
                
                result = await db.execute(query.order_by(desc(TradingSignal.generated_at)))
                records = result.all()
                
                signals = []
                for signal_record, instrument in records:
                    signals.append({
                        'symbol': instrument.tradingsymbol,
                        'signal_type': signal_record.signal_type,
                        'confidence': float(signal_record.confidence_score),
                        'target_price': float(signal_record.target_price) if signal_record.target_price else None,
                        'stop_loss': float(signal_record.stop_loss) if signal_record.stop_loss else None,
                        'timeframe': signal_record.timeframe,
                        'generated_at': signal_record.generated_at.isoformat(),
                        'expires_at': signal_record.expires_at.isoformat(),
                        'strategy_name': signal_record.strategy_name
                    })
                
                return signals
                
        except Exception as e:
            logger.error(f"Failed to get active signals: {e}")
            return []
