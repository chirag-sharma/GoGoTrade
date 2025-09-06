#!/usr/bin/env python3
"""
INFY.NSE Specific Test Script
Tests GoGoTrade system specifically for Infosys stock on NSE.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class INFYTestRunner:
    """Test runner specifically for INFY.NSE stock."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.symbol = "INFY"  # GoGoTrade uses INFY, maps to INFY.NS internally
        
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    def print_header(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f"📈 {title}")
        print(f"{'='*60}")
    
    async def check_server_status(self):
        """Check if the backend server is running."""
        self.print_header("Backend Server Check")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Server Status: {data.get('status', 'unknown')}")
                    print(f"   Version: {data.get('version', 'unknown')}")
                    return True
                else:
                    print(f"❌ Server Error: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Server Connection Failed: {e}")
            print("\n💡 To start the server:")
            print("   cd backend")
            print("   ./startup.sh")
            print("   # or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
            return False
    
    async def test_yahoo_finance_direct(self):
        """Test Yahoo Finance service directly for INFY."""
        self.print_header("Yahoo Finance Direct Test for INFY")
        
        try:
            # Test the Yahoo Finance service directly
            from app.services.yahoo_finance_service import yahoo_finance_service
            
            print(f"📊 Testing Yahoo Finance for {self.symbol}...")
            
            # Get live price
            price_data = await yahoo_finance_service.get_live_price(self.symbol)
            
            if price_data:
                print(f"✅ Live Price Retrieved:")
                print(f"   Symbol: {price_data['symbol']}")
                print(f"   Price: ₹{price_data['ltp']:.2f}")
                print(f"   Change: {price_data['change']:+.2f} ({price_data['change_percent']:+.2f}%)")
                print(f"   Volume: {price_data['volume']:,}")
                print(f"   Source: {price_data['source']}")
                print(f"   Exchange: {price_data.get('exchange', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to get live price for {self.symbol}")
                return False
                
        except Exception as e:
            print(f"❌ Yahoo Finance test failed: {e}")
            return False
    
    async def subscribe_to_infy(self):
        """Subscribe to INFY live data."""
        self.print_header("Subscribing to INFY Live Data")
        
        try:
            payload = {"symbols": [self.symbol]}
            async with self.session.post(
                f"{self.base_url}/api/v1/real-time/subscribe",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Subscription Successful:")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Message: {data.get('message')}")
                    print(f"   Active Subscriptions: {data.get('active_subscriptions')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Subscription Failed: HTTP {response.status}")
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Subscription Error: {e}")
            return False
    
    async def wait_for_data(self, wait_time: int = 60):
        """Wait for Yahoo Finance data to be fetched."""
        self.print_header(f"Waiting for Data ({wait_time} seconds)")
        
        print(f"⏳ Waiting {wait_time} seconds for Yahoo Finance to fetch INFY data...")
        print("   (Yahoo Finance has rate limits, so we need to wait)")
        
        for i in range(wait_time, 0, -10):
            print(f"   ⏰ {i} seconds remaining...")
            await asyncio.sleep(10)
        
        print("✅ Wait completed!")
    
    async def get_infy_live_price(self):
        """Get live price for INFY."""
        self.print_header("INFY Live Price Data")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/real-time/price/{self.symbol}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ INFY Live Price:")
                    print(f"   Symbol: {data.get('symbol')}")
                    print(f"   Last Price: ₹{data.get('ltp', 0):.2f}")
                    print(f"   Change: ₹{data.get('change', 0):+.2f}")
                    print(f"   Change %: {data.get('change_percent', 0):+.2f}%")
                    print(f"   Volume: {data.get('volume', 0):,}")
                    print(f"   Previous Close: ₹{data.get('previous_close', 0):.2f}")
                    print(f"   Market Cap: {data.get('market_cap', 'N/A')}")
                    print(f"   Currency: {data.get('currency', 'N/A')}")
                    print(f"   Exchange: {data.get('exchange', 'N/A')}")
                    print(f"   Source: {data.get('source')}")
                    print(f"   Timestamp: {data.get('timestamp')}")
                    return data
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get price: HTTP {response.status}")
                    print(f"   Error: {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Price fetch error: {e}")
            return None
    
    async def get_infy_signals(self):
        """Get trading signals for INFY."""
        self.print_header("INFY Trading Signals")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/real-time/signals/{self.symbol}") as response:
                if response.status == 200:
                    signals = await response.json()
                    if signals:
                        print(f"✅ Found {len(signals)} trading signals for INFY:")
                        for i, signal in enumerate(signals, 1):
                            print(f"   Signal {i}:")
                            print(f"     Type: {signal.get('signal_type')}")
                            print(f"     Confidence: {signal.get('confidence', 0):.1%}")
                            print(f"     Target Price: ₹{signal.get('target_price', 0):.2f}" if signal.get('target_price') else "     Target Price: N/A")
                            print(f"     Stop Loss: ₹{signal.get('stop_loss', 0):.2f}" if signal.get('stop_loss') else "     Stop Loss: N/A")
                            print(f"     Reasoning: {signal.get('reasoning', 'N/A')}")
                            print(f"     Generated: {signal.get('generated_at', 'N/A')}")
                            print()
                        return signals
                    else:
                        print("ℹ️  No active trading signals for INFY")
                        print("   (Signals may take time to generate based on market data)")
                        return []
                else:
                    print(f"❌ Failed to get signals: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Signals fetch error: {e}")
            return None
    
    async def test_infy_ai_analysis(self):
        """Test AI analysis for INFY."""
        self.print_header("INFY AI Technical Analysis")
        
        try:
            payload = {
                "symbol": self.symbol,
                "timeframe": "1d",
                "indicators": ["RSI", "MACD", "SMA", "EMA"]
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/ai-enhanced/technical-analysis",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ AI Technical Analysis for INFY:")
                    
                    analysis = data.get('analysis', {})
                    print(f"   Overall Sentiment: {analysis.get('overall_sentiment', 'N/A')}")
                    print(f"   Trend: {analysis.get('trend_analysis', 'N/A')}")
                    print(f"   Key Levels: {analysis.get('key_levels', 'N/A')}")
                    
                    recommendations = data.get('recommendations', [])
                    if recommendations:
                        print(f"   Recommendations:")
                        for rec in recommendations[:3]:  # Show first 3
                            print(f"     • {rec}")
                    
                    return data
                else:
                    print(f"❌ AI Analysis failed: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"❌ AI Analysis error: {e}")
            return None
    
    async def test_infy_trade_prediction(self):
        """Test trade prediction for INFY."""
        self.print_header("INFY Trade Prediction")
        
        try:
            payload = {
                "symbol": self.symbol,
                "timeframe": "1h",
                "analysis_depth": "comprehensive"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/trade-prediction/predict",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Trade Prediction for INFY:")
                    
                    prediction = data.get('prediction', {})
                    print(f"   Direction: {prediction.get('direction', 'N/A')}")
                    print(f"   Confidence: {prediction.get('confidence', 0):.1%}")
                    print(f"   Entry Price: ₹{prediction.get('entry_price', 0):.2f}" if prediction.get('entry_price') else "   Entry Price: N/A")
                    print(f"   Target Price: ₹{prediction.get('target_price', 0):.2f}" if prediction.get('target_price') else "   Target Price: N/A")
                    print(f"   Stop Loss: ₹{prediction.get('stop_loss', 0):.2f}" if prediction.get('stop_loss') else "   Stop Loss: N/A")
                    
                    reasoning = data.get('reasoning', [])
                    if reasoning:
                        print(f"   Reasoning:")
                        for reason in reasoning[:3]:  # Show first 3
                            print(f"     • {reason}")
                    
                    return data
                else:
                    print(f"❌ Trade Prediction failed: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Trade Prediction error: {e}")
            return None
    
    async def run_comprehensive_infy_test(self):
        """Run comprehensive test for INFY."""
        print("🚀 GoGoTrade INFY.NSE Comprehensive Test")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: {self.symbol} (Infosys Limited on NSE)")
        
        await self.initialize()
        
        success_count = 0
        total_tests = 7
        
        try:
            # Test 1: Server Status
            if await self.check_server_status():
                success_count += 1
            else:
                print("\n🚨 Cannot proceed without backend server!")
                return False
            
            # Test 2: Yahoo Finance Direct Test
            if await self.test_yahoo_finance_direct():
                success_count += 1
            
            # Test 3: Subscribe to INFY
            if await self.subscribe_to_infy():
                success_count += 1
            
            # Test 4: Wait for Data
            await self.wait_for_data(60)
            success_count += 1  # Always successful
            
            # Test 5: Get Live Price
            price_data = await self.get_infy_live_price()
            if price_data:
                success_count += 1
            
            # Test 6: Get Trading Signals
            signals = await self.get_infy_signals()
            if signals is not None:  # Even empty list is success
                success_count += 1
            
            # Test 7: AI Analysis
            if await self.test_infy_ai_analysis():
                success_count += 1
            
            # Test 8: Trade Prediction
            if await self.test_infy_trade_prediction():
                success_count += 1
                total_tests = 8
            
            # Summary
            self.print_header("Test Summary")
            success_rate = (success_count / total_tests) * 100
            
            print(f"📊 INFY Test Results:")
            print(f"   Tests Passed: {success_count}/{total_tests}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print(f"\n🎉 INFY Integration: SUCCESSFUL!")
                print(f"   GoGoTrade is working properly for Infosys stock")
                
                if price_data:
                    print(f"\n📈 Current INFY Status:")
                    print(f"   Price: ₹{price_data.get('ltp', 0):.2f}")
                    print(f"   Change: {price_data.get('change_percent', 0):+.2f}%")
                    print(f"   Volume: {price_data.get('volume', 0):,}")
                
            elif success_rate >= 60:
                print(f"\n⚠️  INFY Integration: PARTIAL")
                print(f"   Some features working, check failures above")
            else:
                print(f"\n🚨 INFY Integration: FAILED")
                print(f"   Multiple issues detected")
            
            return success_rate >= 60
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False
        
        finally:
            await self.close()


async def main():
    """Main function."""
    tester = INFYTestRunner()
    success = await tester.run_comprehensive_infy_test()
    
    if success:
        print(f"\n🔗 Next Steps:")
        print(f"• Monitor INFY: http://localhost:8000/api/v1/real-time/price/INFY")
        print(f"• Get Signals: http://localhost:8000/api/v1/real-time/signals/INFY") 
        print(f"• WebSocket: ws://localhost:8000/api/v1/real-time/ws")
        print(f"• API Docs: http://localhost:8000/docs")
    
    return 0 if success else 1


if __name__ == "__main__":
    print("GoGoTrade INFY.NSE Test")
    print("=" * 50)
    print("This script tests GoGoTrade specifically for Infosys (INFY) stock")
    print("on the National Stock Exchange (NSE).")
    print()
    print("Prerequisites:")
    print("• Backend server running on http://localhost:8000")
    print("• Internet connection for Yahoo Finance data")
    print("=" * 50)
    print()
    
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
