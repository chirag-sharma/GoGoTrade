"""
Configuration management for GoGoTrade application
Handles environment variables and application settings
"""

from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application settings
    app_name: str = "GoGoTrade"
    app_version: str = "0.1.0"
    debug_mode: bool = False

    # API settings
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: list[str] = ["*"]

    # Database settings
    database_url: Optional[str] = None
    redis_url: Optional[str] = None

    # Zerodha Kite Connect settings
    kite_api_key: Optional[str] = None
    kite_access_token: Optional[str] = None
    kite_api_secret: Optional[str] = None

    # Trading settings
    max_position_size: float = 0.02  # 2% max position size
    max_daily_loss: float = 0.05     # 5% max daily loss
    risk_free_rate: float = 0.06     # 6% risk-free rate (Indian government bonds)

    # Compliance settings
    algo_order_tag: str = "GOGOTRADE_ALGO"
    enable_audit_log: bool = True

    model_config = ConfigDict(
        env_file=".env"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
