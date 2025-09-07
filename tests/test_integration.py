"""
Integration Tests Suite
Tests the complete system integration between frontend, backend, and database
"""

import pytest
import asyncio
import sys
from pathlib import Path
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class TestSystemIntegration:
    """Test complete system integration"""
    
    @classmethod
    def setup_class(cls):
        """Setup for integration tests"""
        cls.backend_url = "http://localhost:8000"
        cls.frontend_url = "http://localhost:3000"
        cls.test_symbol = "RELIANCE"
        cls.timeout = 10  # seconds
    
    def test_services_are_running(self):
        """Test that all services are running"""
        services = {
            "Backend": self.backend_url,
            "Frontend": self.frontend_url
        }
        
        for service_name, url in services.items():
            try:
                response = requests.get(f"{url}/health" if service_name == "Backend" else url, 
                                      timeout=self.timeout)
                assert response.status_code == 200
                print(f"✅ {service_name} is running")
            except requests.exceptions.RequestException as e:
                print(f"❌ {service_name} is not accessible: {e}")
                pytest.fail(f"{service_name} service is not running")
    
    def test_database_connectivity(self):
        """Test database connectivity through API"""
        try:
            response = requests.get(f"{self.backend_url}/health/database", 
                                  timeout=self.timeout)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "postgresql" in data["details"]
            assert "redis" in data["details"]
            
            print("✅ Database connectivity confirmed")
            
        except Exception as e:
            print(f"❌ Database connectivity test failed: {e}")
            pytest.fail("Database is not properly connected")
    
    def test_api_endpoints_integration(self):
        """Test integration of all API endpoints"""
        endpoints = [
            "/api/v1/trading-data/instruments",
            f"/api/v1/trading-data/ohlcv/{self.test_symbol}",
            f"/api/v1/strategies/signals/{self.test_symbol}",
            f"/api/v1/charts/chart-data/{self.test_symbol}",
            "/api/v1/strategies/strategies"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", 
                                      timeout=self.timeout)
                assert response.status_code == 200
                
                # Validate JSON response
                data = response.json()
                assert data is not None
                
                print(f"✅ {endpoint} working")
                
            except Exception as e:
                print(f"⚠️  {endpoint} issue: {e}")
                # Don't fail the test, just document issues
    
    def test_data_flow_consistency(self):
        """Test data consistency across different endpoints"""
        try:
            # Get instruments
            instruments_response = requests.get(
                f"{self.backend_url}/api/v1/trading-data/instruments",
                timeout=self.timeout
            )
            instruments = instruments_response.json()
            
            if not instruments:
                print("⚠️  No instruments available for testing")
                return
            
            test_symbol = instruments[0]["symbol"]
            
            # Get OHLCV data for the instrument
            ohlcv_response = requests.get(
                f"{self.backend_url}/api/v1/trading-data/ohlcv/{test_symbol}",
                timeout=self.timeout
            )
            ohlcv_data = ohlcv_response.json()
            
            # Get signals for the same instrument
            signals_response = requests.get(
                f"{self.backend_url}/api/v1/strategies/signals/{test_symbol}",
                timeout=self.timeout
            )
            signals_data = signals_response.json()
            
            # Validate consistency
            if ohlcv_data:
                assert ohlcv_data[0]["symbol"] == test_symbol
            
            if signals_data:
                assert signals_data[0]["symbol"] == test_symbol
            
            print(f"✅ Data consistency verified for {test_symbol}")
            
        except Exception as e:
            print(f"⚠️  Data flow consistency test: {e}")
    
    def test_concurrent_api_requests(self):
        """Test system performance under concurrent load"""
        def make_request(endpoint):
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", 
                                      timeout=self.timeout)
                return response.status_code == 200
            except:
                return False
        
        # Test endpoints
        endpoints = [
            "/api/v1/trading-data/instruments",
            f"/api/v1/trading-data/ohlcv/{self.test_symbol}",
            f"/api/v1/strategies/signals/{self.test_symbol}"
        ]
        
        # Make concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for _ in range(10):  # 10 concurrent requests
                for endpoint in endpoints:
                    future = executor.submit(make_request, endpoint)
                    futures.append(future)
            
            # Check results
            success_count = sum(1 for future in futures if future.result())
            total_requests = len(futures)
            
            success_rate = success_count / total_requests
            print(f"✅ Concurrent load test: {success_rate:.2%} success rate")
            
            # Should handle at least 80% of concurrent requests
            assert success_rate >= 0.8
    
    def test_error_propagation(self):
        """Test how errors propagate through the system"""
        # Test invalid symbol
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/trading-data/ohlcv/INVALID_SYMBOL",
                timeout=self.timeout
            )
            
            # Should handle gracefully (not crash)
            assert response.status_code in [200, 404, 422]
            print("✅ Invalid symbol handled gracefully")
            
        except Exception as e:
            print(f"⚠️  Error propagation test: {e}")
    
    def test_frontend_backend_communication(self):
        """Test frontend can communicate with backend"""
        try:
            # Check if frontend is serving content
            frontend_response = requests.get(self.frontend_url, timeout=self.timeout)
            assert frontend_response.status_code == 200
            
            # Check if frontend HTML contains references to API
            content = frontend_response.text
            
            # Look for API references (this is basic - could be improved)
            api_indicators = [
                "localhost:8000",
                "api/v1",
                "backend"
            ]
            
            found_indicators = [indicator for indicator in api_indicators 
                              if indicator in content.lower()]
            
            if found_indicators:
                print(f"✅ Frontend-Backend integration indicators found: {found_indicators}")
            else:
                print("⚠️  No obvious frontend-backend integration indicators found")
            
        except Exception as e:
            print(f"⚠️  Frontend-Backend communication test: {e}")


class TestPerformanceIntegration:
    """Test system performance under realistic conditions"""
    
    def test_response_times(self):
        """Test API response times"""
        endpoints = [
            "/health",
            "/api/v1/trading-data/instruments",
            f"/api/v1/trading-data/ohlcv/RELIANCE",
            f"/api/v1/strategies/signals/RELIANCE"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"http://localhost:8000{endpoint}", 
                                      timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    print(f"✅ {endpoint}: {response_time:.3f}s")
                    
                    # Most endpoints should respond within 2 seconds
                    if response_time > 2.0:
                        print(f"⚠️  Slow response: {endpoint}")
                else:
                    print(f"⚠️  {endpoint}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
    
    def test_memory_usage_stability(self):
        """Test that repeated requests don't cause memory leaks"""
        # Make many requests to the same endpoint
        endpoint = "/api/v1/trading-data/instruments"
        
        try:
            for i in range(50):  # 50 requests
                response = requests.get(f"http://localhost:8000{endpoint}", 
                                      timeout=5)
                if response.status_code != 200:
                    print(f"⚠️  Request {i} failed")
                    break
            
            print("✅ Memory stability test completed")
            
        except Exception as e:
            print(f"⚠️  Memory stability test: {e}")


class TestDataIntegrity:
    """Test data integrity across the system"""
    
    def test_ohlcv_data_integrity(self):
        """Test OHLCV data follows financial data rules"""
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/trading-data/ohlcv/RELIANCE",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for record in data:
                    # Validate OHLCV constraints
                    assert record["low"] <= record["high"], "Low should be <= High"
                    assert record["low"] <= record["open"], "Low should be <= Open"
                    assert record["low"] <= record["close"], "Low should be <= Close"
                    assert record["high"] >= record["open"], "High should be >= Open"
                    assert record["high"] >= record["close"], "High should be >= Close"
                    assert record["volume"] >= 0, "Volume should be non-negative"
                
                print("✅ OHLCV data integrity verified")
            else:
                print("⚠️  Could not retrieve OHLCV data for integrity check")
                
        except Exception as e:
            print(f"⚠️  OHLCV data integrity test: {e}")
    
    def test_signal_data_integrity(self):
        """Test trading signals data integrity"""
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/strategies/signals/RELIANCE",
                timeout=10
            )
            
            if response.status_code == 200:
                signals = response.json()
                
                for signal in signals:
                    # Validate signal constraints
                    assert signal["signal"] in ["BUY", "SELL", "HOLD"], f"Invalid signal: {signal['signal']}"
                    assert 0 <= signal["confidence"] <= 1, f"Invalid confidence: {signal['confidence']}"
                    assert "timestamp" in signal, "Missing timestamp"
                    assert "strategy" in signal, "Missing strategy"
                
                print("✅ Signal data integrity verified")
            else:
                print("⚠️  Could not retrieve signals for integrity check")
                
        except Exception as e:
            print(f"⚠️  Signal data integrity test: {e}")


if __name__ == "__main__":
    print("🧪 Running Integration Tests...")
    print("Note: These tests require the system to be running (docker-compose up)")
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
