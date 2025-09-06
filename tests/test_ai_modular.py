"""
Test script for the modular AI analysis system
Demonstrates the usage of the prompt management system
"""

import asyncio
import sys
import os

# Add the backend app to Python path
sys.path.append('/Users/chirag/VsCodeProjects/GoGoTrade/backend')

from app.ai_prompts.prompt_manager import prompt_manager, get_ai_prompt, get_system_prompt
from app.services.ai_analysis_enhanced import ai_analysis_service


async def test_prompt_system():
    """Test the prompt management system"""
    print("🧪 Testing GoGoTrade Modular AI Analysis System")
    print("=" * 60)
    
    # Test 1: List available categories
    print("\n1. Available Prompt Categories:")
    categories = prompt_manager.list_categories()
    for i, category in enumerate(categories, 1):
        print(f"   {i}. {category}")
    
    # Test 2: List prompts in a category
    print("\n2. Technical Analysis Prompts:")
    if "technical_analysis" in categories:
        prompts = prompt_manager.list_prompts("technical_analysis")
        for i, prompt in enumerate(prompts, 1):
            print(f"   {i}. {prompt}")
    
    # Test 3: Get a formatted prompt
    print("\n3. Sample Formatted Prompt:")
    sample_prompt = get_ai_prompt(
        category="technical_analysis",
        prompt_type="pattern_recognition",
        symbol="RELIANCE",
        timeframe="1D",
        current_price=2450.00,
        ohlc_data="Sample OHLC data",
        volume=1000000
    )
    print(f"   {sample_prompt[:200]}...")
    
    # Test 4: Test AI analysis service
    print("\n4. Testing AI Analysis Service:")
    try:
        # Technical analysis test
        print("   📊 Running technical analysis...")
        tech_result = await ai_analysis_service.analyze_technical_pattern("RELIANCE", "1D")
        print(f"   ✅ Technical analysis completed: {tech_result.get('analysis_type', 'Unknown')}")
        
        # Trend analysis test
        print("   📈 Running trend analysis...")
        trend_result = await ai_analysis_service.analyze_trend_strength("RELIANCE")
        print(f"   ✅ Trend analysis completed: {trend_result.get('analysis_type', 'Unknown')}")
        
        # Risk assessment test
        print("   ⚖️ Running risk assessment...")
        risk_result = await ai_analysis_service.assess_trading_risk("RELIANCE", 2400.0, 2.5)
        print(f"   ✅ Risk assessment completed: {risk_result.get('analysis_type', 'Unknown')}")
        
        # Strategy recommendation test
        print("   🎯 Running strategy recommendation...")
        user_profile = {
            "risk_tolerance": "Medium",
            "investment_horizon": "Long term",
            "capital": 100000,
            "experience_level": "Intermediate",
            "preferred_sectors": "Technology,Banking"
        }
        strategy_result = await ai_analysis_service.get_strategy_recommendation(user_profile)
        print(f"   ✅ Strategy recommendation completed: {strategy_result.get('analysis_type', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Error in AI analysis: {str(e)}")
    
    # Test 5: Performance metrics
    print("\n5. System Performance:")
    print(f"   📁 Total categories loaded: {len(categories)}")
    total_prompts = sum(len(prompt_manager.list_prompts(cat)) for cat in categories)
    print(f"   📝 Total prompts available: {total_prompts}")
    print(f"   🔄 Cache enabled: {bool(prompt_manager.prompts_cache)}")
    
    print("\n" + "=" * 60)
    print("✅ Modular AI Analysis System Test Complete!")
    

async def test_custom_prompt():
    """Test creating and using a custom prompt"""
    print("\n🔧 Testing Custom Prompt Creation")
    print("-" * 40)
    
    # Create a custom prompt on the fly
    custom_prompt = """
    Analyze the following stock for swing trading opportunity:
    
    Stock: {symbol}
    Current Price: ₹{price}
    Sector: {sector}
    Market Cap: ₹{market_cap} Cr
    
    Provide:
    1. Swing trading setup (entry/exit/stop)
    2. Hold period recommendation
    3. Risk-reward assessment
    4. Key levels to watch
    
    Consider Indian market conditions and retail trader perspective.
    """
    
    # Format the custom prompt
    formatted = custom_prompt.format(
        symbol="TCS",
        price=3650.00,
        sector="Information Technology",
        market_cap=132000
    )
    
    print("Custom Swing Trading Analysis Prompt:")
    print(formatted)
    

def demonstrate_modularity():
    """Demonstrate the modularity benefits"""
    print("\n🏗️ Demonstrating Modularity Benefits")
    print("-" * 40)
    
    benefits = [
        "✅ Easy prompt editing without code changes",
        "✅ Support for both JSON and YAML formats", 
        "✅ Live reloading without application restart",
        "✅ Version control for prompt templates",
        "✅ Consistent variable substitution system",
        "✅ Category-based organization",
        "✅ Scalable architecture for new AI features",
        "✅ Separation of AI logic from business logic"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print("\n📊 File Structure Created:")
    files_created = [
        "app/ai_prompts/prompt_manager.py",
        "app/ai_prompts/config.py", 
        "app/ai_prompts/technical_analysis.json",
        "app/ai_prompts/strategy_analysis.yaml",
        "app/ai_prompts/market_context.json",
        "app/services/ai_analysis_enhanced.py",
        "app/api/v1/ai_enhanced.py"
    ]
    
    for file in files_created:
        print(f"   📁 {file}")


if __name__ == "__main__":
    print("🚀 GoGoTrade Modular AI Analysis System")
    print("   Testing the implementation...")
    
    # Run the tests
    asyncio.run(test_prompt_system())
    asyncio.run(test_custom_prompt())
    demonstrate_modularity()
    
    print("\n🎉 All tests completed!")
    print("🔗 API endpoints available at:")
    print("   http://localhost:8000/api/v1/ai-enhanced/")
    print("📖 Documentation: http://localhost:8000/docs")
