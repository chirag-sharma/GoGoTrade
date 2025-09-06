"""
Enhanced AI Trading API with Modular Prompt System
New endpoints using the modular AI analysis service
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.ai_analysis_enhanced import ai_analysis_service


router = APIRouter(prefix="/ai-enhanced", tags=["AI Enhanced Analysis"])


# Request/Response Models
class TechnicalAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., 'RELIANCE', 'NIFTY')")
    timeframe: str = Field(default="1D", description="Analysis timeframe")


class TrendAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")


class RiskAssessmentRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    entry_price: float = Field(..., description="Entry price for position")
    position_size: float = Field(..., description="Position size as percentage of portfolio")


class SentimentAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")


class StrategyRequest(BaseModel):
    risk_tolerance: str = Field(..., description="Low/Medium/High")
    investment_horizon: str = Field(..., description="Short/Medium/Long term")
    capital: float = Field(..., description="Available capital in INR")
    experience_level: str = Field(..., description="Beginner/Intermediate/Advanced")
    preferred_sectors: str = Field(default="Technology,Banking", description="Comma-separated sectors")


class AIAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
    execution_time_ms: Optional[float] = None


@router.post("/technical-analysis", response_model=AIAnalysisResponse)
async def enhanced_technical_analysis(request: TechnicalAnalysisRequest):
    """
    Enhanced technical analysis using modular AI prompts
    
    Provides comprehensive pattern recognition, signal analysis, and trading recommendations
    using configurable prompt templates for easy customization.
    """
    try:
        start_time = datetime.now()
        
        # Perform AI analysis using modular prompts
        analysis_result = await ai_analysis_service.analyze_technical_pattern(
            symbol=request.symbol.upper(),
            timeframe=request.timeframe
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return AIAnalysisResponse(
            success=True,
            data=analysis_result,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Technical analysis failed: {str(e)}")


@router.post("/trend-analysis", response_model=AIAnalysisResponse)
async def enhanced_trend_analysis(request: TrendAnalysisRequest):
    """
    Enhanced trend analysis using moving averages, momentum indicators, and AI interpretation
    
    Provides comprehensive trend strength assessment with configurable analysis prompts.
    """
    try:
        start_time = datetime.now()
        
        analysis_result = await ai_analysis_service.analyze_trend_strength(
            symbol=request.symbol.upper()
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return AIAnalysisResponse(
            success=True,
            data=analysis_result,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")


@router.post("/risk-assessment", response_model=AIAnalysisResponse)
async def enhanced_risk_assessment(request: RiskAssessmentRequest):
    """
    Enhanced risk assessment using AI analysis
    
    Provides comprehensive risk evaluation including position sizing, stop-loss levels,
    and risk-reward analysis using modular prompt system.
    """
    try:
        start_time = datetime.now()
        
        analysis_result = await ai_analysis_service.assess_trading_risk(
            symbol=request.symbol.upper(),
            entry_price=request.entry_price,
            position_size=request.position_size
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return AIAnalysisResponse(
            success=True,
            data=analysis_result,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/sentiment-analysis", response_model=AIAnalysisResponse)
async def enhanced_sentiment_analysis(request: SentimentAnalysisRequest):
    """
    Enhanced market sentiment analysis using multiple data sources
    
    Analyzes price action, volume, news sentiment, social media, and institutional flows
    using configurable sentiment analysis prompts.
    """
    try:
        start_time = datetime.now()
        
        analysis_result = await ai_analysis_service.analyze_market_sentiment(
            symbol=request.symbol.upper()
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return AIAnalysisResponse(
            success=True,
            data=analysis_result,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.post("/strategy-recommendation", response_model=AIAnalysisResponse)
async def enhanced_strategy_recommendation(request: StrategyRequest):
    """
    Enhanced personalized strategy recommendation
    
    Provides customized trading strategies based on user profile, risk tolerance,
    and current market conditions using modular strategy prompts.
    """
    try:
        start_time = datetime.now()
        
        user_profile = {
            "risk_tolerance": request.risk_tolerance,
            "investment_horizon": request.investment_horizon,
            "capital": request.capital,
            "experience_level": request.experience_level,
            "preferred_sectors": request.preferred_sectors
        }
        
        analysis_result = await ai_analysis_service.get_strategy_recommendation(user_profile)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return AIAnalysisResponse(
            success=True,
            data=analysis_result,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy recommendation failed: {str(e)}")


@router.get("/prompt-categories", response_model=AIAnalysisResponse)
async def get_prompt_categories():
    """
    Get available AI prompt categories for customization
    
    Returns all available prompt categories and their types for
    administrators to understand and modify the AI analysis system.
    """
    try:
        from app.ai_prompts.prompt_manager import prompt_manager
        
        categories = prompt_manager.list_categories()
        category_details = {}
        
        for category in categories:
            category_details[category] = {
                "prompts": prompt_manager.list_prompts(category),
                "system_prompt": prompt_manager.get_system_prompt(category)[:100] + "..."
            }
        
        return AIAnalysisResponse(
            success=True,
            data={
                "available_categories": categories,
                "category_details": category_details,
                "total_categories": len(categories)
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prompt categories: {str(e)}")


@router.post("/reload-prompts", response_model=AIAnalysisResponse)
async def reload_ai_prompts():
    """
    Reload AI prompts from files
    
    Allows administrators to reload prompt templates after making changes
    without restarting the application.
    """
    try:
        from app.ai_prompts.prompt_manager import prompt_manager
        
        prompt_manager.reload_prompts()
        categories = prompt_manager.list_categories()
        
        return AIAnalysisResponse(
            success=True,
            data={
                "message": "AI prompts reloaded successfully",
                "categories_loaded": categories,
                "total_categories": len(categories)
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload prompts: {str(e)}")


@router.get("/health")
async def ai_enhanced_health():
    """Health check for enhanced AI analysis service"""
    try:
        from app.ai_prompts.prompt_manager import prompt_manager
        
        categories = prompt_manager.list_categories()
        
        return {
            "status": "healthy",
            "service": "AI Enhanced Analysis",
            "prompt_system": "operational",
            "categories_loaded": len(categories),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
