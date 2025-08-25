"""
Test configuration and utilities
Following camelCase naming convention
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

# Test client for FastAPI
testClient = TestClient(app)

class TestConfig:
    """Test configuration class"""
    
    # Test data
    testSymbol = "RELIANCE"
    testTimeframe = "5minute"
    testStartDate = "2025-08-01"
    testEndDate = "2025-08-25"
    
    # Expected response fields
    requiredMarketDataFields = ["symbol", "timestamp", "price", "volume", "changePercent"]
    requiredOhlcvFields = ["symbol", "timestamp", "open", "high", "low", "close", "volume"]


def assertResponseStructure(response: dict, requiredFields: list) -> None:
    """Assert that response contains all required fields"""
    for field in requiredFields:
        assert field in response, f"Missing required field: {field}"


def assertValidOhlcv(ohlcvData: dict) -> None:
    """Assert that OHLCV data is valid"""
    assertResponseStructure(ohlcvData, TestConfig.requiredOhlcvFields)
    
    # Validate OHLCV logic
    assert ohlcvData["low"] <= ohlcvData["high"], "Low should be <= High"
    assert ohlcvData["low"] <= ohlcvData["open"], "Low should be <= Open" 
    assert ohlcvData["low"] <= ohlcvData["close"], "Low should be <= Close"
    assert ohlcvData["high"] >= ohlcvData["open"], "High should be >= Open"
    assert ohlcvData["high"] >= ohlcvData["close"], "High should be >= Close"
    assert ohlcvData["volume"] >= 0, "Volume should be non-negative"
