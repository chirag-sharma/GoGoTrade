"""
Configuration management for GoGoTrade application
Handles environment variables and application settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application settings
    appName: str = "GoGoTrade"
    appVersion: str = "0.1.0"
    debugMode: bool = False
    
    # API settings
    apiV1Prefix: str = "/api/v1"
    allowedHosts: list = ["*"]
    
    # Database settings
    databaseUrl: Optional[str] = None
    redisUrl: Optional[str] = None
    
    # Zerodha Kite Connect settings
    kiteApiKey: Optional[str] = None
    kiteAccessToken: Optional[str] = None
    kiteApiSecret: Optional[str] = None
    
    # Trading settings
    maxPositionSize: float = 0.02  # 2% max position size
    maxDailyLoss: float = 0.05     # 5% max daily loss
    riskFreeRate: float = 0.06     # 6% risk-free rate (Indian government bonds)
    
    # Compliance settings
    algoOrderTag: str = "GOGOTRADE_ALGO"
    enableAuditLog: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def getSettings() -> Settings:
    """Get application settings instance"""
    return settings
