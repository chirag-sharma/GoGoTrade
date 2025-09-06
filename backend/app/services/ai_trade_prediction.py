"""
Advanced AI Trade Prediction Service
Specialized for predicting trade direction, entry/exit points, stop-loss, and candlestick patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import json

from app.ai_prompts.prompt_manager import AIPromptManager
from app.services.market_data import MarketDataService
from app.services.ai_trading import AITradingEngine


class TradeDirection(Enum):
    """Trade direction prediction"""
    BUY = "BUY"
    SELL = "SELL"
    SHORT_SELL = "SHORT_SELL"
    HOLD = "HOLD"


class CandlestickPattern(Enum):
    """Recognized candlestick patterns"""
    # Bullish Patterns
    HAMMER = "hammer"
    BULLISH_ENGULFING = "bullish_engulfing"
    MORNING_STAR = "morning_star"
    PIERCING_LINE = "piercing_line"
    BULLISH_HARAMI = "bullish_harami"
    DRAGONFLY_DOJI = "dragonfly_doji"
    
    # Bearish Patterns
    SHOOTING_STAR = "shooting_star"
    BEARISH_ENGULFING = "bearish_engulfing"
    EVENING_STAR = "evening_star"
    DARK_CLOUD_COVER = "dark_cloud_cover"
    BEARISH_HARAMI = "bearish_harami"
    GRAVESTONE_DOJI = "gravestone_doji"
    
    # Neutral/Reversal
    DOJI = "doji"
    SPINNING_TOP = "spinning_top"
    HANGING_MAN = "hanging_man"


@dataclass
class TradeSignal:
    """Complete trade signal with all parameters"""
    symbol: str
    direction: TradeDirection
    confidence: float  # 0.0 to 1.0
    
    # Price levels
    entry_price: float
    target_price: float
    stop_loss: float
    
    # Risk metrics
    risk_reward_ratio: float
    position_size_percent: float
    
    # Pattern analysis
    primary_pattern: Optional[CandlestickPattern]
    pattern_strength: float
    
    # Supporting analysis
    technical_reasons: List[str]
    risk_factors: List[str]
    timeframe: str
    
    # Execution details
    order_type: str  # "MARKET", "LIMIT", "SL"
    validity: str    # "DAY", "IOC", "GTC"
    
    timestamp: datetime


@dataclass
class CandlestickAnalysis:
    """Detailed candlestick pattern analysis"""
    pattern: CandlestickPattern
    pattern_name: str
    signal_type: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    strength: float  # 1-10 scale
    confirmation_required: bool
    reliability: float  # Historical success rate
    description: str


class AdvancedTradePredictionService:
    """Advanced AI service for trade prediction and pattern recognition"""
    
    def __init__(self):
        self.prompt_manager = AIPromptManager()
        self.market_data_service = MarketDataService()
        self.ai_service = AITradingEngine()
        
        # Load specialized trading prompts
        self.prediction_prompts = self._load_prediction_prompts()
    
    def _load_prediction_prompts(self) -> Dict:
        """Load specialized prompts for trade prediction"""
        return {
            "trade_direction": """
                Analyze the following market data and predict the optimal trade direction for {symbol}:

                MARKET DATA:
                Current Price: ₹{current_price}
                Day High: ₹{day_high}
                Day Low: ₹{day_low}
                Open Price: ₹{day_open}
                Volume: {volume:,}
                Avg Volume (20D): {avg_volume:,}

                TECHNICAL INDICATORS:
                RSI (14): {rsi:.2f}
                MACD: {macd:.4f}
                MACD Signal: {macd_signal:.4f}
                SMA 20: ₹{sma_20:.2f}
                SMA 50: ₹{sma_50:.2f}
                Bollinger Upper: ₹{bb_upper:.2f}
                Bollinger Lower: ₹{bb_lower:.2f}

                CANDLESTICK PATTERN:
                {candlestick_analysis}

                MARKET CONTEXT:
                Sector Performance: {sector_performance}
                Market Trend: {market_trend}
                VIX Level: {vix_level}

                PREDICTION REQUIREMENTS:
                1. Trade Direction: BUY/SELL/SHORT_SELL/HOLD
                2. Confidence Level: 0-100%
                3. Entry Price: Optimal entry level
                4. Target Price: Primary profit target
                5. Stop Loss: Risk management level
                6. Position Size: Recommended % of portfolio
                7. Risk-Reward Ratio: Expected R:R
                8. Time Horizon: Expected holding period
                9. Key Technical Reasons: Top 3 supporting factors
                10. Risk Factors: Top 3 risk considerations

                Provide response in this JSON format:
                {{
                    "trade_direction": "BUY/SELL/SHORT_SELL/HOLD",
                    "confidence": 85.5,
                    "entry_price": 1250.50,
                    "target_price": 1320.00,
                    "stop_loss": 1180.00,
                    "position_size_percent": 3.5,
                    "risk_reward_ratio": 2.8,
                    "time_horizon": "2-3 weeks",
                    "technical_reasons": ["RSI showing bullish divergence", "Breakout above resistance", "Strong volume confirmation"],
                    "risk_factors": ["Market volatility", "Sector rotation risk", "Global cues"],
                    "order_type": "LIMIT",
                    "validity": "DAY"
                }}
            """,
            
            "candlestick_recognition": """
                Analyze the following OHLC data to identify candlestick patterns for {symbol}:

                RECENT CANDLES (Last 5 days):
                {ohlc_data}

                VOLUME DATA:
                {volume_data}

                PATTERN ANALYSIS REQUIRED:
                1. Primary Pattern: Identify the most significant pattern
                2. Pattern Name: Standard technical analysis name
                3. Signal Type: BULLISH/BEARISH/NEUTRAL
                4. Strength: 1-10 scale (10 = very strong)
                5. Confirmation Status: Whether pattern is confirmed
                6. Reliability: Historical success rate (%)
                7. Action Required: Immediate action needed
                8. Supporting Patterns: Any secondary patterns

                CANDLESTICK PATTERNS TO LOOK FOR:
                - Hammer, Hanging Man
                - Bullish/Bearish Engulfing
                - Doji variations
                - Morning/Evening Star
                - Shooting Star
                - Piercing Line, Dark Cloud Cover
                - Harami patterns

                Provide detailed analysis in this JSON format:
                {{
                    "primary_pattern": "bullish_engulfing",
                    "pattern_name": "Bullish Engulfing",
                    "signal_type": "BULLISH",
                    "strength": 8.5,
                    "confirmation_required": false,
                    "reliability": 75.5,
                    "description": "Strong bullish reversal pattern formed after downtrend",
                    "supporting_patterns": ["hammer", "doji"],
                    "action_required": "Consider long position",
                    "confluence_factors": ["Volume spike", "Support level bounce"]
                }}
            """,
            
            "entry_exit_optimization": """
                Optimize entry and exit points for {symbol} trade based on:

                TRADE SETUP:
                Direction: {trade_direction}
                Current Price: ₹{current_price}
                Pattern Signal: {pattern_signal}

                SUPPORT/RESISTANCE LEVELS:
                Key Resistance: ₹{resistance_levels}
                Key Support: ₹{support_levels}
                Previous High: ₹{prev_high}
                Previous Low: ₹{prev_low}

                VOLATILITY DATA:
                ATR (14): {atr:.2f}
                Historical Volatility: {hist_volatility:.2f}%
                Implied Volatility: {implied_volatility:.2f}%

                OPTIMIZATION REQUIREMENTS:
                1. Optimal Entry Price: Best risk-adjusted entry
                2. Primary Target: High probability target
                3. Secondary Target: Extended target (if applicable)
                4. Initial Stop Loss: Conservative risk management
                5. Trailing Stop: Dynamic risk management
                6. Position Sizing: Based on volatility and risk
                7. Execution Strategy: Market/Limit order guidance

                Consider:
                - Gap risks and overnight positions
                - Liquidity and slippage
                - Market session timing
                - News/events impact

                Provide optimization in JSON format:
                {{
                    "optimal_entry": 1245.75,
                    "entry_reasoning": "Pullback to 61.8% Fibonacci level with volume support",
                    "primary_target": 1310.50,
                    "secondary_target": 1345.00,
                    "initial_stop_loss": 1195.25,
                    "trailing_stop_strategy": "Move to breakeven after 1% profit",
                    "position_size": 4.2,
                    "execution_strategy": "LIMIT order at entry level",
                    "session_timing": "First 30 minutes of market open",
                    "risk_management": ["Set alerts at key levels", "Monitor volume", "Watch sector rotation"]
                }}
            """
        }
    
    async def predict_trade_direction(
        self, 
        symbol: str, 
        timeframe: str = "1D",
        custom_inputs: Optional[Dict] = None
    ) -> TradeSignal:
        """
        Comprehensive trade direction prediction with entry/exit points
        
        Args:
            symbol: Stock symbol
            timeframe: Analysis timeframe
            custom_inputs: Additional user inputs for analysis
        """
        try:
            # Get comprehensive market data
            market_data = await self._get_comprehensive_market_data(symbol, timeframe)
            
            # Perform candlestick pattern analysis
            candlestick_analysis = await self.analyze_candlestick_patterns(symbol, timeframe)
            
            # Prepare analysis context
            analysis_context = {
                **market_data,
                "candlestick_analysis": self._format_candlestick_analysis(candlestick_analysis),
                "symbol": symbol,
                **(custom_inputs or {})
            }
            
            # Get AI prediction using a simulated analysis
            # In production, this would call an actual AI service
            prediction_data = await self._simulate_ai_prediction(analysis_context)
            
            # Create comprehensive trade signal
            trade_signal = TradeSignal(
                symbol=symbol,
                direction=TradeDirection(prediction_data["trade_direction"]),
                confidence=prediction_data["confidence"] / 100.0,
                entry_price=prediction_data["entry_price"],
                target_price=prediction_data["target_price"],
                stop_loss=prediction_data["stop_loss"],
                risk_reward_ratio=prediction_data["risk_reward_ratio"],
                position_size_percent=prediction_data["position_size_percent"],
                primary_pattern=candlestick_analysis.pattern if candlestick_analysis else None,
                pattern_strength=candlestick_analysis.strength if candlestick_analysis else 0.0,
                technical_reasons=prediction_data["technical_reasons"],
                risk_factors=prediction_data["risk_factors"],
                timeframe=timeframe,
                order_type=prediction_data["order_type"],
                validity=prediction_data["validity"],
                timestamp=datetime.now()
            )
            
            return trade_signal
            
        except Exception as e:
            raise RuntimeError(f"Trade prediction failed: {str(e)}") from e
    
    async def analyze_candlestick_patterns(
        self, 
        symbol: str, 
        timeframe: str = "1D",
        lookback_days: int = 5
    ) -> Optional[CandlestickAnalysis]:
        """
        Advanced candlestick pattern recognition using AI
        """
        try:
            # Get OHLC data for pattern analysis
            ohlc_data = await self.market_data_service.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                days=lookback_days
            )
            
            if ohlc_data.empty:
                return None
            
            # Format data for AI analysis
            formatted_ohlc = self._format_ohlc_for_analysis(ohlc_data)
            volume_data = self._format_volume_data(ohlc_data)
            
            # Prepare pattern recognition prompt
            pattern_context = {
                "symbol": symbol,
                "ohlc_data": formatted_ohlc,
                "volume_data": volume_data
            }
            
            pattern_prompt = self.prediction_prompts["candlestick_recognition"].format(**pattern_context)
            
            # Get AI pattern analysis using simulation
            # In production, this would call actual AI pattern recognition
            pattern_data = await self._simulate_pattern_analysis(pattern_context)
            
            # Create candlestick analysis object
            if pattern_data:
                return CandlestickAnalysis(
                    pattern=CandlestickPattern(pattern_data["primary_pattern"]),
                    pattern_name=pattern_data["pattern_name"],
                    signal_type=pattern_data["signal_type"],
                    strength=pattern_data["strength"],
                    confirmation_required=pattern_data["confirmation_required"],
                    reliability=pattern_data["reliability"],
                    description=pattern_data["description"]
                )
            
            return None
            
        except Exception as e:
            print(f"Pattern analysis failed: {e}")
            return None
    
    async def optimize_entry_exit_points(
        self, 
        symbol: str, 
        trade_direction: TradeDirection,
        custom_analysis: Optional[Dict] = None
    ) -> Dict:
        """
        Optimize entry and exit points using advanced AI analysis
        """
        try:
            # Get market data for optimization
            market_data = await self._get_comprehensive_market_data(symbol)
            
            # Get support/resistance levels
            levels = await self._calculate_support_resistance_levels(symbol)
            
            # Prepare optimization context
            optimization_context = {
                "symbol": symbol,
                "trade_direction": trade_direction.value,
                "current_price": market_data["current_price"],
                "pattern_signal": custom_analysis.get("pattern_signal", "N/A") if custom_analysis else "N/A",
                "resistance_levels": levels["resistance"],
                "support_levels": levels["support"],
                "prev_high": levels["prev_high"],
                "prev_low": levels["prev_low"],
                "atr": market_data.get("atr", 0),
                "hist_volatility": market_data.get("hist_volatility", 0),
                "implied_volatility": market_data.get("implied_volatility", 0)
            }
            
            # Get AI optimization using simulation
            # In production, this would call actual AI optimization service
            return await self._simulate_optimization_response(optimization_context)
            
        except Exception as e:
            raise RuntimeError(f"Entry/exit optimization failed: {str(e)}") from e
    
    async def _get_comprehensive_market_data(self, symbol: str, timeframe: str = "1D") -> Dict:
        """Get comprehensive market data for analysis"""
        try:
            # Get current market data
            current_data = await self.market_data_service.get_current_price(symbol)
            
            # Get technical indicators
            indicators = await self.market_data_service.get_technical_indicators(symbol)
            
            # Get volume analysis
            volume_data = await self.market_data_service.get_volume_analysis(symbol)
            
            # Combine all data
            return {
                "current_price": current_data.get("ltp", 0),
                "day_high": current_data.get("high", 0),
                "day_low": current_data.get("low", 0),
                "day_open": current_data.get("open", 0),
                "volume": current_data.get("volume", 0),
                "avg_volume": volume_data.get("avg_volume_20d", 0),
                "rsi": indicators.get("rsi", 50),
                "macd": indicators.get("macd", 0),
                "macd_signal": indicators.get("macd_signal", 0),
                "sma_20": indicators.get("sma_20", 0),
                "sma_50": indicators.get("sma_50", 0),
                "bb_upper": indicators.get("bb_upper", 0),
                "bb_lower": indicators.get("bb_lower", 0),
                "sector_performance": "Technology sector +1.2%",  # This would come from sector analysis
                "market_trend": "Bullish",  # This would come from market analysis
                "vix_level": 15.5  # This would come from volatility index
            }
            
        except Exception as e:
            # Return default values if data fetch fails
            return {
                "current_price": 0, "day_high": 0, "day_low": 0, "day_open": 0,
                "volume": 0, "avg_volume": 0, "rsi": 50, "macd": 0, "macd_signal": 0,
                "sma_20": 0, "sma_50": 0, "bb_upper": 0, "bb_lower": 0,
                "sector_performance": "N/A", "market_trend": "Neutral", "vix_level": 15.0
            }
    
    def _format_candlestick_analysis(self, analysis: Optional[CandlestickAnalysis]) -> str:
        """Format candlestick analysis for prompt"""
        if not analysis:
            return "No significant pattern detected"
        
        return f"""
        Pattern: {analysis.pattern_name}
        Signal: {analysis.signal_type}
        Strength: {analysis.strength}/10
        Reliability: {analysis.reliability}%
        Description: {analysis.description}
        """
    
    def _format_ohlc_for_analysis(self, ohlc_data: pd.DataFrame) -> str:
        """Format OHLC data for AI analysis"""
        formatted_data = []
        for _, row in ohlc_data.tail(5).iterrows():
            formatted_data.append(
                f"Date: {row.name.strftime('%Y-%m-%d')}, "
                f"O: ₹{row['open']:.2f}, H: ₹{row['high']:.2f}, "
                f"L: ₹{row['low']:.2f}, C: ₹{row['close']:.2f}"
            )
        return "\n".join(formatted_data)
    
    def _format_volume_data(self, ohlc_data: pd.DataFrame) -> str:
        """Format volume data for analysis"""
        volume_analysis = []
        for _, row in ohlc_data.tail(5).iterrows():
            volume_analysis.append(
                f"Date: {row.name.strftime('%Y-%m-%d')}, Volume: {row['volume']:,}"
            )
        return "\n".join(volume_analysis)
    
    def _parse_ai_prediction(self, ai_response: str) -> Dict:
        """Parse AI prediction response"""
        try:
            # Extract JSON from AI response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing if JSON format is not found
                return self._fallback_parse_prediction(ai_response)
                
        except Exception as e:
            print(f"Failed to parse AI prediction: {e}")
            return self._get_default_prediction()
    
    def _parse_pattern_analysis(self, ai_response: str) -> Optional[Dict]:
        """Parse candlestick pattern analysis"""
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            return None
            
        except Exception as e:
            print(f"Failed to parse pattern analysis: {e}")
            return None
    
    def _parse_optimization_response(self, ai_response: str) -> Dict:
        """Parse entry/exit optimization response"""
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return self._get_default_optimization()
                
        except Exception as e:
            print(f"Failed to parse optimization response: {e}")
            return self._get_default_optimization()
    
    async def _calculate_support_resistance_levels(self, symbol: str) -> Dict:
        """Calculate support and resistance levels"""
        try:
            # Get historical data for pivot point calculation
            historical_data = await self.market_data_service.get_historical_data(symbol, days=20)
            
            if historical_data.empty:
                return {"resistance": [0], "support": [0], "prev_high": 0, "prev_low": 0}
            
            # Calculate pivot points and levels
            recent_high = historical_data['high'].max()
            recent_low = historical_data['low'].min()
            
            # Simple support/resistance calculation
            resistance_levels = [recent_high * 1.02, recent_high * 1.05]
            support_levels = [recent_low * 0.98, recent_low * 0.95]
            
            return {
                "resistance": resistance_levels,
                "support": support_levels,
                "prev_high": recent_high,
                "prev_low": recent_low
            }
            
        except Exception:
            return {"resistance": [0], "support": [0], "prev_high": 0, "prev_low": 0}
    
    async def _simulate_ai_prediction(self, analysis_context: Dict) -> Dict:
        """Simulate AI prediction for demonstration"""
        import random
        
        current_price = analysis_context.get("current_price", 1000)
        rsi = analysis_context.get("rsi", 50)
        
        # Simulate trade direction based on RSI
        if rsi < 30:
            direction = "BUY"
            confidence = random.uniform(75, 90)
            entry_price = current_price * 0.995  # Slight pullback
            target_price = current_price * 1.05   # 5% target
            stop_loss = current_price * 0.97      # 3% stop
        elif rsi > 70:
            direction = "SELL" 
            confidence = random.uniform(70, 85)
            entry_price = current_price * 1.005
            target_price = current_price * 0.95
            stop_loss = current_price * 1.03
        else:
            direction = "HOLD"
            confidence = random.uniform(60, 75)
            entry_price = current_price
            target_price = current_price * 1.02
            stop_loss = current_price * 0.98
        
        return {
            "trade_direction": direction,
            "confidence": confidence,
            "entry_price": round(entry_price, 2),
            "target_price": round(target_price, 2),
            "stop_loss": round(stop_loss, 2),
            "position_size_percent": random.uniform(2.0, 5.0),
            "risk_reward_ratio": round(abs(target_price - entry_price) / abs(entry_price - stop_loss), 2) if abs(entry_price - stop_loss) > 0 else 1.0,
            "technical_reasons": [
                f"RSI at {rsi:.1f} indicating {'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'} conditions",
                "Volume confirmation detected",
                "Support/resistance level interaction"
            ],
            "risk_factors": [
                "Market volatility risk",
                "Sector rotation uncertainty", 
                "Global market sentiment"
            ],
            "order_type": "LIMIT",
            "validity": "DAY"
        }
    
    async def _simulate_pattern_analysis(self, pattern_context: Dict) -> Optional[Dict]:
        """Simulate candlestick pattern analysis"""
        import random
        
        patterns = [
            ("bullish_engulfing", "Bullish Engulfing", "BULLISH", 8.5, 75.0),
            ("hammer", "Hammer", "BULLISH", 7.2, 68.0),
            ("doji", "Doji", "NEUTRAL", 6.0, 55.0),
            ("shooting_star", "Shooting Star", "BEARISH", 7.8, 72.0)
        ]
        
        # Randomly select a pattern
        pattern_data = random.choice(patterns)
        
        return {
            "primary_pattern": pattern_data[0],
            "pattern_name": pattern_data[1], 
            "signal_type": pattern_data[2],
            "strength": pattern_data[3],
            "confirmation_required": random.choice([True, False]),
            "reliability": pattern_data[4],
            "description": f"Detected {pattern_data[1]} pattern with {pattern_data[2].lower()} implications"
        }
    
    async def _simulate_optimization_response(self, optimization_context: Dict) -> Dict:
        """Simulate optimization response"""
        import random
        
        entry_price = optimization_context.get("current_price", 1000)
        
        return {
            "optimal_entry": round(entry_price * random.uniform(0.995, 1.005), 2),
            "entry_reasoning": "Pullback to key support level with volume confirmation",
            "primary_target": round(entry_price * 1.05, 2),
            "secondary_target": round(entry_price * 1.08, 2),
            "initial_stop_loss": round(entry_price * 0.97, 2),
            "trailing_stop_strategy": "Move to breakeven after 1.5% profit",
            "position_size": round(random.uniform(2.5, 4.5), 1),
            "execution_strategy": "LIMIT order at entry level",
            "session_timing": "First 30 minutes of market session",
            "risk_management": ["Monitor volume", "Watch key levels", "Set alerts"]
        }

    def _fallback_parse_prediction(self, response: str) -> Dict:
        """Fallback parsing for AI prediction"""
        # Basic text parsing as fallback
        return self._get_default_prediction()
    
    def _get_default_prediction(self) -> Dict:
        """Default prediction when parsing fails"""
        return {
            "trade_direction": "HOLD",
            "confidence": 50.0,
            "entry_price": 0.0,
            "target_price": 0.0,
            "stop_loss": 0.0,
            "position_size_percent": 2.0,
            "risk_reward_ratio": 1.0,
            "technical_reasons": ["Analysis unavailable"],
            "risk_factors": ["Data parsing error"],
            "order_type": "MARKET",
            "validity": "DAY"
        }
    
    def _get_default_optimization(self) -> Dict:
        """Default optimization when parsing fails"""
        return {
            "optimal_entry": 0.0,
            "entry_reasoning": "Analysis unavailable",
            "primary_target": 0.0,
            "secondary_target": 0.0,
            "initial_stop_loss": 0.0,
            "trailing_stop_strategy": "Not available",
            "position_size": 2.0,
            "execution_strategy": "MARKET order",
            "session_timing": "Any time",
            "risk_management": ["Monitor closely"]
        }


# Global instance
ai_trade_prediction_service = AdvancedTradePredictionService()
