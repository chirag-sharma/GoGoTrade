# AI Prompt Customization Examples

This directory contains modular AI prompts for the GoGoTrade platform. The system supports both JSON and YAML formats for easy editing and maintenance.

## 📁 File Structure

```
backend/app/ai_prompts/
├── prompt_manager.py          # Core prompt management system
├── config.py                  # Configuration and settings
├── technical_analysis.json    # Technical analysis prompts
├── strategy_analysis.yaml     # Strategy development prompts
├── market_context.json        # Market sentiment prompts
└── README.md                  # This file
```

## 🔧 How to Customize Prompts

### 1. JSON Format (technical_analysis.json)
```json
{
  "system_prompt": "System-level instructions for the AI",
  "prompts": {
    "prompt_name": "Prompt template with {variables}",
    "another_prompt": "Another template with {symbol} and {price}"
  },
  "metadata": {
    "version": "1.0",
    "description": "Description of prompt category"
  }
}
```

### 2. YAML Format (strategy_analysis.yaml)
```yaml
system_prompt: |
  Multi-line system prompt
  that can span several lines

prompts:
  prompt_name: |
    Multi-line prompt template
    with {variables} support
    
metadata:
  version: "1.0"
  description: "Description"
```

## 🚀 Adding New Prompt Categories

1. Create a new JSON/YAML file in this directory
2. Follow the required structure (system_prompt, prompts, metadata)
3. Use descriptive prompt names
4. Include variable placeholders with {variable_name}
5. Restart the application or call `/api/v1/ai-enhanced/reload-prompts`

## 📝 Variable Substitution

Variables in prompts are replaced using Python's `.format()` method:

```python
prompt = "Analyze {symbol} with price ₹{current_price}"
# Becomes: "Analyze RELIANCE with price ₹2450.00"
```

## 🔄 Live Reloading

Prompts can be reloaded without restarting the application:

```bash
curl -X POST http://localhost:8000/api/v1/ai-enhanced/reload-prompts
```

## 📊 Available Endpoints

- `/ai-enhanced/technical-analysis` - Pattern recognition
- `/ai-enhanced/trend-analysis` - Trend strength analysis  
- `/ai-enhanced/risk-assessment` - Risk evaluation
- `/ai-enhanced/sentiment-analysis` - Market sentiment
- `/ai-enhanced/strategy-recommendation` - Personalized strategies
- `/ai-enhanced/prompt-categories` - List all categories
- `/ai-enhanced/reload-prompts` - Reload prompt files

## 🎯 Best Practices

1. **Clear Instructions**: Make prompts specific and actionable
2. **Indian Market Focus**: Consider SEBI regulations and INR currency
3. **Variable Names**: Use descriptive variable names
4. **Consistent Format**: Follow the same structure across files
5. **Version Control**: Update metadata when changing prompts
6. **Testing**: Test prompts with real data before deployment

## 🔒 Security Considerations

- Avoid sensitive information in prompt files
- Validate all user inputs before prompt substitution
- Use the built-in validation system
- Monitor prompt execution for unusual patterns

## 📈 Performance Tips

- Keep prompts concise but comprehensive
- Use caching for frequently accessed prompts
- Avoid overly complex variable substitutions
- Monitor AI service response times
