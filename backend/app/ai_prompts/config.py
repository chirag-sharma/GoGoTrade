"""
AI Prompt Configuration
Global settings and configurations for the AI prompt system
"""

# Prompt system settings
PROMPT_SYSTEM_CONFIG = {
    "enabled": True,
    "cache_prompts": True,
    "reload_on_change": True,
    "supported_formats": ["json", "yaml"],
    "max_prompt_length": 10000,
    "default_timeout": 30,  # seconds
    "fallback_prompts": True
}

# AI Service Configuration
AI_SERVICE_CONFIG = {
    "provider": "simulated",  # Options: "openai", "claude", "local", "simulated"
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1500,
    "timeout": 30,
    "rate_limit": 100,  # requests per minute
    "retry_attempts": 3
}

# Prompt Categories Configuration
PROMPT_CATEGORIES = {
    "technical_analysis": {
        "description": "Technical analysis prompts for pattern recognition and trend analysis",
        "priority": 1,
        "enabled": True
    },
    "strategy_analysis": {
        "description": "Strategy development and portfolio optimization prompts",
        "priority": 2,
        "enabled": True
    },
    "market_context": {
        "description": "Market sentiment and contextual analysis prompts",
        "priority": 3,
        "enabled": True
    },
    "risk_management": {
        "description": "Risk assessment and management prompts",
        "priority": 4,
        "enabled": True
    }
}

# Default prompt variables
DEFAULT_PROMPT_VARIABLES = {
    "currency": "INR",
    "market": "Indian",
    "timezone": "Asia/Kolkata",
    "regulatory_framework": "SEBI",
    "default_timeframe": "1D",
    "confidence_threshold": 0.7
}

# Prompt validation rules
PROMPT_VALIDATION = {
    "required_fields": ["system_prompt", "prompts", "metadata"],
    "max_categories": 20,
    "max_prompts_per_category": 50,
    "forbidden_keywords": ["delete", "drop", "truncate"],
    "validate_syntax": True
}
