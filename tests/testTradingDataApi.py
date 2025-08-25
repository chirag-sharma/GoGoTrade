"""
Test trading data API endpoints
Following camelCase naming convention
"""

import pytest
from fastapi import status
from tests.conftest import testClient, TestConfig, assertResponseStructure, assertValidOhlcv


class TestTradingDataEndpoints:
    """Test cases for trading data API endpoints"""
    
    def testGetMarketDataSuccess(self):
        """Test successful market data retrieval"""
        response = testClient.get(f"/api/v1/trading-data/market-data/{TestConfig.testSymbol}")
        
        assert response.status_code == status.HTTP_200_OK
        
        responseData = response.json()
        assertResponseStructure(responseData, TestConfig.requiredMarketDataFields)
        
        # Validate specific fields
        assert responseData["symbol"] == TestConfig.testSymbol
        assert isinstance(responseData["price"], (int, float))
        assert isinstance(responseData["volume"], int)
        assert isinstance(responseData["changePercent"], (int, float))
    
    def testGetOhlcvDataSuccess(self):
        """Test successful OHLCV data retrieval"""
        response = testClient.get(
            f"/api/v1/trading-data/ohlcv/{TestConfig.testSymbol}",
            params={
                "timeframe": TestConfig.testTimeframe,
                "startDate": TestConfig.testStartDate,
                "endDate": TestConfig.testEndDate
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        responseData = response.json()
        assert isinstance(responseData, list)
        assert len(responseData) > 0
        
        # Validate first OHLCV record
        firstRecord = responseData[0]
        assertValidOhlcv(firstRecord)
        assert firstRecord["symbol"] == TestConfig.testSymbol
    
    def testGetInstrumentsSuccess(self):
        """Test successful instruments list retrieval"""
        response = testClient.get("/api/v1/trading-data/instruments")
        
        assert response.status_code == status.HTTP_200_OK
        
        responseData = response.json()
        assert isinstance(responseData, list)
        assert len(responseData) > 0
        
        # Validate first instrument
        firstInstrument = responseData[0]
        requiredFields = ["symbol", "name", "exchange"]
        assertResponseStructure(firstInstrument, requiredFields)
    
    def testGetMarketDataInvalidSymbol(self):
        """Test market data with invalid symbol"""
        invalidSymbol = "INVALID_SYMBOL_123"
        response = testClient.get(f"/api/v1/trading-data/market-data/{invalidSymbol}")
        
        # Should still return 200 with mock data for now
        # TODO: Implement proper validation when real data source is connected
        assert response.status_code == status.HTTP_200_OK
        
        responseData = response.json()
        assert responseData["symbol"] == invalidSymbol
