"""
Enhanced AI Analysis Service with Modular Prompt System
Integrates with the prompt management system for scalable AI analysis
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.ai_prompts.prompt_manager import get_ai_prompt, get_system_prompt
from app.services.market_data import MarketDataService
from app.core.database import db_manager


class AIAnalysisService:
    """
    Enhanced AI Analysis Service using modular prompt system
    Provides comprehensive analysis using configurable prompts
    """
    
    def __init__(self):
        self.market_service = MarketDataService()
        
    async def analyze_technical_pattern(self, symbol: str, timeframe: str = "1D") -> Dict[str, Any]:
        """
        Analyze technical patterns using modular prompts
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'NIFTY')
            timeframe: Analysis timeframe ('1D', '1H', '5M')
            
        Returns:
            Comprehensive technical analysis
        """
        try:
            # Get market data
            market_data = await self.market_service.get_historical_data(symbol, days=30)
            
            if not market_data:
                return {"error": f"No data available for {symbol}"}
            
            # Calculate technical indicators
            df = pd.DataFrame(market_data)
            current_price = df['close'].iloc[-1]
            volume = df['volume'].iloc[-1]
            
            # Prepare data for AI analysis
            ohlc_data = df[['open', 'high', 'low', 'close']].tail(5).to_dict('records')
            
            # Get AI prompt for pattern recognition
            prompt = get_ai_prompt(
                category="technical_analysis",
                prompt_type="pattern_recognition",
                symbol=symbol,
                timeframe=timeframe,
                ohlc_data=ohlc_data,
                volume=volume,
                current_price=current_price
            )
            
            # Simulate AI analysis (replace with actual AI service call)
            analysis = await self._simulate_ai_response(prompt, "pattern_analysis")
            
            return {
                "symbol": symbol,
                "analysis_type": "pattern_recognition",
                "timestamp": datetime.now().isoformat(),
                "prompt_used": prompt[:200] + "...",  # Truncated for logging
                "analysis": analysis,
                "market_data_points": len(market_data),
                "confidence_score": np.random.uniform(0.7, 0.95)  # Simulated confidence
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def analyze_trend_strength(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze trend strength using moving averages and momentum indicators
        """
        try:
            # Get extended market data for trend analysis
            market_data = await self.market_service.get_historical_data(symbol, days=200)
            
            if not market_data:
                return {"error": f"No data available for {symbol}"}
            
            df = pd.DataFrame(market_data)
            
            # Calculate technical indicators
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['sma_200'] = df['close'].rolling(200).mean()
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            
            # Get latest values
            latest = df.iloc[-1]
            
            # Prepare prompt variables
            prompt = get_ai_prompt(
                category="technical_analysis",
                prompt_type="trend_analysis",
                symbol=symbol,
                current_price=latest['close'],
                sma_20=latest['sma_20'],
                sma_50=latest['sma_50'],
                sma_200=latest['sma_200'],
                rsi=latest['rsi'],
                macd_signal="Bullish" if latest['macd'] > latest['macd_signal'] else "Bearish",
                volume_trend="High" if latest['volume'] > df['volume'].rolling(20).mean().iloc[-1] else "Normal"
            )
            
            # Get AI analysis
            analysis = await self._simulate_ai_response(prompt, "trend_analysis")
            
            return {
                "symbol": symbol,
                "analysis_type": "trend_analysis",
                "timestamp": datetime.now().isoformat(),
                "technical_indicators": {
                    "current_price": float(latest['close']),
                    "sma_20": float(latest['sma_20']),
                    "sma_50": float(latest['sma_50']),
                    "sma_200": float(latest['sma_200']),
                    "rsi": float(latest['rsi']),
                    "macd": float(latest['macd']),
                    "macd_signal": float(latest['macd_signal'])
                },
                "analysis": analysis,
                "confidence_score": np.random.uniform(0.75, 0.9)
            }
            
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    async def assess_trading_risk(self, symbol: str, entry_price: float, 
                                position_size: float) -> Dict[str, Any]:
        """
        Assess trading risk using AI analysis
        """
        try:
            # Get market data and volatility metrics
            market_data = await self.market_service.get_historical_data(symbol, days=30)
            
            if not market_data:
                return {"error": f"No data available for {symbol}"}
            
            df = pd.DataFrame(market_data)
            current_price = df['close'].iloc[-1]
            
            # Calculate volatility and other risk metrics
            returns = df['close'].pct_change().dropna()
            volatility_30d = returns.std() * np.sqrt(252) * 100  # Annualized volatility
            avg_volume = df['volume'].mean()
            
            # Simulate additional risk metrics
            market_cap = np.random.uniform(1000, 50000)  # Simulated market cap in Cr
            beta = np.random.uniform(0.5, 2.0)  # Simulated beta
            sector = "Technology"  # This would come from company data
            
            # Get risk assessment prompt
            prompt = get_ai_prompt(
                category="technical_analysis",
                prompt_type="risk_assessment",
                symbol=symbol,
                entry_price=entry_price,
                current_price=current_price,
                position_size=position_size,
                market_cap=market_cap,
                avg_volume=avg_volume,
                volatility_30d=volatility_30d,
                beta=beta,
                sector=sector
            )
            
            # Get AI risk assessment
            analysis = await self._simulate_ai_response(prompt, "risk_assessment")
            
            return {
                "symbol": symbol,
                "analysis_type": "risk_assessment",
                "timestamp": datetime.now().isoformat(),
                "risk_metrics": {
                    "entry_price": entry_price,
                    "current_price": float(current_price),
                    "position_size_percent": position_size,
                    "volatility_30d": float(volatility_30d),
                    "average_volume": float(avg_volume),
                    "beta": beta,
                    "market_cap_cr": market_cap
                },
                "analysis": analysis,
                "risk_score": np.random.uniform(3, 8)  # 1-10 scale
            }
            
        except Exception as e:
            return {"error": f"Risk assessment failed: {str(e)}"}
    
    async def analyze_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze market sentiment using various factors
        """
        try:
            # Simulate sentiment data (in real implementation, this would come from news, social media, etc.)
            sentiment_data = {
                "price_action": "Bullish breakout above resistance",
                "volume_analysis": "Above average volume confirming move",
                "news_sentiment": "Positive earnings outlook",
                "social_sentiment": "Moderately bullish retail sentiment",
                "institutional_flow": "FII buying, DII neutral",
                "fii_dii_data": "Net FII inflow ₹150 Cr",
                "sector_performance": "IT sector outperforming"
            }
            
            # Get sentiment analysis prompt
            prompt = get_ai_prompt(
                category="technical_analysis",
                prompt_type="market_sentiment",
                symbol=symbol,
                **sentiment_data
            )
            
            # Get AI sentiment analysis
            analysis = await self._simulate_ai_response(prompt, "sentiment_analysis")
            
            return {
                "symbol": symbol,
                "analysis_type": "market_sentiment",
                "timestamp": datetime.now().isoformat(),
                "sentiment_factors": sentiment_data,
                "analysis": analysis,
                "sentiment_score": np.random.uniform(6, 8)  # 1-10 scale (bearish to bullish)
            }
            
        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    async def get_strategy_recommendation(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized strategy recommendations
        """
        try:
            # Simulate market conditions
            market_conditions = {
                "market_trend": "Bullish with consolidation",
                "vix_level": 15.5,
                "interest_rates": 6.5,
                "institutional_flow": "Mixed - FII buying, DII selling",
                "sector_rotation": "From defensives to cyclicals"
            }
            
            # Get strategy recommendation prompt
            prompt = get_ai_prompt(
                category="strategy_analysis",
                prompt_type="strategy_recommendation",
                **market_conditions,
                **user_profile
            )
            
            # Get AI strategy recommendation
            analysis = await self._simulate_ai_response(prompt, "strategy_recommendation")
            
            return {
                "analysis_type": "strategy_recommendation",
                "timestamp": datetime.now().isoformat(),
                "user_profile": user_profile,
                "market_conditions": market_conditions,
                "analysis": analysis,
                "confidence_score": np.random.uniform(0.8, 0.95)
            }
            
        except Exception as e:
            return {"error": f"Strategy recommendation failed: {str(e)}"}
    
    async def _simulate_ai_response(self, prompt: str, analysis_type: str) -> str:
        """
        Simulate AI response (replace with actual AI service call)
        """
        # In real implementation, this would call OpenAI, Claude, or local LLM
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        responses = {
            "pattern_analysis": """
**Pattern Recognition Analysis:**

1. **Identified Pattern**: Bullish Engulfing Pattern
   - Strong bullish signal with high confidence
   - Pattern completed with above-average volume

2. **Signal Strength**: 8/10 (Strong Bullish)
   - Clear reversal from support level
   - Volume confirmation present

3. **Entry/Exit Recommendations**:
   - Entry: Current market price (₹2,450)
   - Target 1: ₹2,520 (3% upside)
   - Target 2: ₹2,580 (5% upside)
   - Stop Loss: ₹2,380 (3% downside)

4. **Risk Management**:
   - Position size: 2-3% of portfolio
   - Risk-reward ratio: 1:2.3
   - Hold period: 2-3 weeks

5. **Target Price Levels**:
   - Immediate resistance: ₹2,480
   - Strong resistance: ₹2,550
   - Support: ₹2,400
""",
            "trend_analysis": """
**Comprehensive Trend Analysis:**

1. **Primary Trend**: Bullish (7/10 strength)
   - Price above all major moving averages
   - Strong upward momentum confirmed

2. **Moving Average Analysis**:
   - SMA 20 > SMA 50 > SMA 200 (Golden alignment)
   - Price 8% above SMA 200 (healthy uptrend)

3. **Momentum Indicators**:
   - RSI: 68 (Bullish but approaching overbought)
   - MACD: Bullish crossover confirmed

4. **Support & Resistance**:
   - Key support: ₹2,350-2,380
   - Immediate resistance: ₹2,480-2,500
   - Major resistance: ₹2,550

5. **Trading Strategy**:
   - Buy on dips to SMA 20 support
   - Book profits near resistance zones
   - Trail stop-loss using SMA 20
""",
            "risk_assessment": """
**Risk Assessment Report:**

1. **Overall Risk Level**: Medium (6/10)
   - Moderate volatility with good liquidity
   - Well-established company fundamentals

2. **Position Sizing**: Recommended 2.5% of portfolio
   - Current position aligns with risk tolerance
   - Allows for proper diversification

3. **Stop-Loss Levels**:
   - Conservative: ₹2,380 (3% below entry)
   - Aggressive: ₹2,340 (5% below entry)

4. **Risk-Reward Analysis**:
   - Expected return: 12-15% (6 months)
   - Maximum risk: 5%
   - Risk-reward ratio: 1:3

5. **Risk Factors to Monitor**:
   - Sector-wide regulatory changes
   - Quarterly earnings volatility
   - Market correlation during corrections
""",
            "sentiment_analysis": """
**Market Sentiment Analysis:**

1. **Overall Sentiment Score**: 7.5/10 (Bullish)
   - Strong positive momentum across indicators
   - Institutional support visible

2. **Key Sentiment Drivers**:
   - Positive earnings revision cycle
   - Strong FII inflows in sector
   - Improving business fundamentals

3. **Institutional vs Retail**:
   - Institutions: Bullish (buying on dips)
   - Retail: Moderately bullish (profit booking)

4. **Short-term vs Long-term**:
   - Short-term (1-3 months): Bullish
   - Long-term (6-12 months): Very Bullish

5. **Sentiment-based Strategy**:
   - Accumulate on market weakness
   - Maintain core long position
   - Use options for additional upside
""",
            "strategy_recommendation": """
**Personalized Strategy Recommendation:**

1. **Primary Strategy**: Momentum Growth Strategy
   - Focus on quality growth stocks
   - Systematic trend following approach

2. **Asset Allocation**:
   - Large Cap: 60% (stability focus)
   - Mid Cap: 30% (growth focus)
   - Small Cap: 10% (high growth potential)

3. **Entry/Exit Criteria**:
   - Enter: RSI < 40 with volume confirmation
   - Exit: RSI > 75 or 15% profit target

4. **Risk Management**:
   - Maximum position: 5% per stock
   - Stop-loss: 8% from entry
   - Portfolio stop: 15% drawdown

5. **Implementation Steps**:
   - Start with paper trading for 1 month
   - Begin with 50% capital allocation
   - Scale up based on performance
"""
        }
        
        return responses.get(analysis_type, "Analysis completed successfully.")


# Global service instance
ai_analysis_service = AIAnalysisService()
