#!/usr/bin/env python3
"""
GoGoTrade System Health Check
Comprehensive system validation for all components.
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime
import subprocess
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemHealthChecker:
    """Comprehensive system health checker for GoGoTrade."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = {}
        
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
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Print test result with formatting."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.results[test_name] = success
    
    async def check_backend_running(self):
        """Check if backend server is running."""
        self.print_header("Backend Server Status")
        
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    self.print_result("Backend Server", True, f"Running on {self.base_url}")
                    return True
                else:
                    self.print_result("Backend Server", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.print_result("Backend Server", False, f"Connection failed: {e}")
            return False
    
    async def check_api_endpoints(self):
        """Check core API endpoints."""
        self.print_header("API Endpoints Health")
        
        endpoints = [
            ("/api/v1/status", "API Status"),
            ("/api/v1/real-time/status", "Real-time Status"),
            ("/docs", "API Documentation"),
            ("/openapi.json", "OpenAPI Schema")
        ]
        
        for endpoint, name in endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    success = response.status == 200
                    details = f"HTTP {response.status}" if not success else "OK"
                    self.print_result(name, success, details)
            except Exception as e:
                self.print_result(name, False, f"Error: {e}")
    
    async def check_database_connection(self):
        """Check database connectivity."""
        self.print_header("Database Connectivity")
        
        try:
            # Check if we can access database through API
            async with self.session.get(f"{self.base_url}/api/v1/trading-data/instruments") as response:
                if response.status == 200:
                    data = await response.json()
                    self.print_result("Database Connection", True, f"Connected, {len(data)} instruments")
                else:
                    self.print_result("Database Connection", False, f"HTTP {response.status}")
        except Exception as e:
            self.print_result("Database Connection", False, f"Error: {e}")
    
    async def check_yahoo_finance_integration(self):
        """Check Yahoo Finance data integration."""
        self.print_header("Yahoo Finance Integration")
        
        # Test symbols
        test_symbols = ["AAPL", "RELIANCE"]
        
        try:
            # First, subscribe to symbols
            subscription_payload = {"symbols": test_symbols}
            async with self.session.post(
                f"{self.base_url}/api/v1/real-time/subscribe",
                json=subscription_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.print_result("Real-time Subscription", True, f"Subscribed to {len(test_symbols)} symbols")
                else:
                    self.print_result("Real-time Subscription", False, f"HTTP {response.status}")
                    return
            
            # Wait for data to be fetched
            print("    ⏳ Waiting 45 seconds for Yahoo Finance data...")
            await asyncio.sleep(45)
            
            # Check if we can get live prices
            success_count = 0
            for symbol in test_symbols:
                try:
                    async with self.session.get(f"{self.base_url}/api/v1/real-time/price/{symbol}") as response:
                        if response.status == 200:
                            price_data = await response.json()
                            price = price_data.get('ltp', 0)
                            change = price_data.get('change_percent', 0)
                            source = price_data.get('source', 'unknown')
                            self.print_result(f"Live Price - {symbol}", True, 
                                            f"${price:.2f} ({change:+.2f}%) from {source}")
                            success_count += 1
                        else:
                            self.print_result(f"Live Price - {symbol}", False, f"HTTP {response.status}")
                except Exception as e:
                    self.print_result(f"Live Price - {symbol}", False, f"Error: {e}")
            
            overall_success = success_count > 0
            self.print_result("Yahoo Finance Overall", overall_success, 
                            f"{success_count}/{len(test_symbols)} symbols working")
            
        except Exception as e:
            self.print_result("Yahoo Finance Integration", False, f"Error: {e}")
    
    async def check_trading_signals(self):
        """Check trading signal generation."""
        self.print_header("Trading Signal Generation")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/real-time/signals") as response:
                if response.status == 200:
                    signals = await response.json()
                    if signals:
                        self.print_result("Signal Generation", True, f"{len(signals)} active signals")
                        # Show first signal as example
                        if len(signals) > 0:
                            signal = signals[0]
                            print(f"    Example: {signal['symbol']} {signal['signal_type']} "
                                  f"(confidence: {signal['confidence']:.1%})")
                    else:
                        self.print_result("Signal Generation", True, "No active signals (normal)")
                else:
                    self.print_result("Signal Generation", False, f"HTTP {response.status}")
        except Exception as e:
            self.print_result("Signal Generation", False, f"Error: {e}")
    
    async def check_ai_services(self):
        """Check AI services."""
        self.print_header("AI Services")
        
        # Test AI enhanced analysis
        try:
            payload = {
                "symbol": "AAPL",
                "timeframe": "1d",
                "indicators": ["RSI", "MACD", "SMA"]
            }
            async with self.session.post(
                f"{self.base_url}/api/v1/ai-enhanced/technical-analysis",
                json=payload
            ) as response:
                if response.status == 200:
                    self.print_result("AI Technical Analysis", True, "Working")
                else:
                    self.print_result("AI Technical Analysis", False, f"HTTP {response.status}")
        except Exception as e:
            self.print_result("AI Technical Analysis", False, f"Error: {e}")
        
        # Test trade prediction
        try:
            payload = {
                "symbol": "AAPL",
                "timeframe": "1h",
                "analysis_depth": "standard"
            }
            async with self.session.post(
                f"{self.base_url}/api/v1/trade-prediction/predict",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    prediction = data.get('prediction', {}).get('direction', 'N/A')
                    confidence = data.get('prediction', {}).get('confidence', 0)
                    self.print_result("AI Trade Prediction", True, 
                                    f"Prediction: {prediction} ({confidence:.1%} confidence)")
                else:
                    self.print_result("AI Trade Prediction", False, f"HTTP {response.status}")
        except Exception as e:
            self.print_result("AI Trade Prediction", False, f"Error: {e}")
    
    async def check_websocket_connection(self):
        """Check WebSocket connectivity."""
        self.print_header("WebSocket Connection")
        
        try:
            import websockets
            
            ws_url = self.base_url.replace("http", "ws") + "/api/v1/real-time/ws"
            
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Send ping
                ping_msg = {"action": "ping"}
                await websocket.send(json.dumps(ping_msg))
                
                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get("type") == "pong":
                    self.print_result("WebSocket Connection", True, "Ping/Pong successful")
                else:
                    self.print_result("WebSocket Connection", False, "Unexpected response")
                    
        except Exception as e:
            self.print_result("WebSocket Connection", False, f"Error: {e}")
    
    async def check_advanced_strategies(self):
        """Check advanced strategies functionality."""
        self.print_header("Advanced Strategies")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/advanced-strategies/strategy-parameters") as response:
                if response.status == 200:
                    data = await response.json()
                    strategies = data.get('available_strategies', [])
                    self.print_result("Advanced Strategies", True, f"{len(strategies)} strategies available")
                else:
                    self.print_result("Advanced Strategies", False, f"HTTP {response.status}")
        except Exception as e:
            self.print_result("Advanced Strategies", False, f"Error: {e}")
    
    def check_dependencies(self):
        """Check Python dependencies."""
        self.print_header("Python Dependencies")
        
        required_packages = [
            "fastapi",
            "uvicorn", 
            "yfinance",
            "pandas",
            "numpy",
            "sqlalchemy",
            "redis",
            "websockets",
            "aiohttp"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.print_result(f"Package - {package}", True, "Installed")
            except ImportError:
                self.print_result(f"Package - {package}", False, "Missing")
    
    def print_summary(self):
        """Print test summary."""
        self.print_header("Test Summary")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 System Status: HEALTHY")
            print("The GoGoTrade system is working properly!")
        elif success_rate >= 60:
            print("\n⚠️  System Status: DEGRADED")
            print("Some components have issues but core functionality works.")
        else:
            print("\n🚨 System Status: UNHEALTHY")
            print("Multiple critical issues detected. Check the failures above.")
        
        return success_rate >= 80
    
    async def run_comprehensive_check(self):
        """Run all system checks."""
        print("🚀 GoGoTrade System Health Check")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await self.initialize()
        
        try:
            # Check dependencies first
            self.check_dependencies()
            
            # Check if backend is running
            backend_running = await self.check_backend_running()
            
            if not backend_running:
                print("\n🚨 Backend server is not running!")
                print("To start the backend:")
                print("  cd backend")
                print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
                return False
            
            # Run all other checks
            await self.check_api_endpoints()
            await self.check_database_connection()
            await self.check_yahoo_finance_integration()
            await self.check_trading_signals()
            await self.check_ai_services()
            await self.check_websocket_connection()
            await self.check_advanced_strategies()
            
            # Print summary
            return self.print_summary()
            
        finally:
            await self.close()


async def main():
    """Main function to run system health check."""
    checker = SystemHealthChecker()
    
    try:
        success = await checker.run_comprehensive_check()
        
        if success:
            print("\n🔗 Quick Links:")
            print("• API Documentation: http://localhost:8000/docs")
            print("• Health Status: http://localhost:8000/api/v1/status")
            print("• Real-time Status: http://localhost:8000/api/v1/real-time/status")
            
            print("\n🧪 Test Commands:")
            print("• Test Yahoo Finance: python test_yahoo_finance.py")
            print("• Test Real-time Integration: python test_real_time_integration.py")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Health check interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        return 1


if __name__ == "__main__":
    print("GoGoTrade System Health Checker")
    print("This script will verify all system components are working properly.")
    print()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
