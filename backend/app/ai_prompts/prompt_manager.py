"""
AI Prompt Management System for GoGoTrade
Modular prompt system for easy scalability and maintenance
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class AIPromptManager:
    """
    Manages AI prompts for different analysis types
    Supports JSON and YAML formats for easy editing
    """
    
    def __init__(self, prompts_dir: str = "app/ai_prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_cache = {}
        self.load_all_prompts()
    
    def load_all_prompts(self):
        """Load all prompt files into cache"""
        try:
            if not self.prompts_dir.exists():
                print(f"Creating prompts directory: {self.prompts_dir}")
                self.prompts_dir.mkdir(parents=True, exist_ok=True)
                return
            
            for prompt_file in self.prompts_dir.glob("*.json"):
                category = prompt_file.stem
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts_cache[category] = json.load(f)
            
            for prompt_file in self.prompts_dir.glob("*.yaml"):
                category = prompt_file.stem
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts_cache[category] = yaml.safe_load(f)
                    
            print(f"Loaded {len(self.prompts_cache)} prompt categories")
            
        except Exception as e:
            print(f"Error loading prompts: {e}")
            self.prompts_cache = {}
    
    def get_prompt(self, category: str, prompt_type: str, **kwargs) -> str:
        """
        Get a specific prompt with variable substitution
        
        Args:
            category: Category of prompt (e.g., 'technical_analysis', 'market_sentiment')
            prompt_type: Type within category (e.g., 'pattern_recognition', 'trend_analysis')
            **kwargs: Variables to substitute in the prompt
        
        Returns:
            Formatted prompt string
        """
        try:
            if category not in self.prompts_cache:
                return f"Prompt category '{category}' not found"
            
            category_prompts = self.prompts_cache[category]
            
            if prompt_type not in category_prompts.get('prompts', {}):
                return f"Prompt type '{prompt_type}' not found in category '{category}'"
            
            prompt_template = category_prompts['prompts'][prompt_type]
            
            # Add default context variables
            default_vars = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'system_name': 'GoGoTrade AI',
                **kwargs
            }
            
            # Format the prompt with variables
            return prompt_template.format(**default_vars)
            
        except Exception as e:
            return f"Error formatting prompt: {e}"
    
    def get_system_prompt(self, category: str) -> str:
        """Get system prompt for a category"""
        if category in self.prompts_cache:
            return self.prompts_cache[category].get('system_prompt', '')
        return ''
    
    def reload_prompts(self):
        """Reload all prompts from files"""
        self.prompts_cache.clear()
        self.load_all_prompts()
    
    def list_categories(self) -> list:
        """List all available prompt categories"""
        return list(self.prompts_cache.keys())
    
    def list_prompts(self, category: str) -> list:
        """List all prompts in a category"""
        if category in self.prompts_cache:
            return list(self.prompts_cache[category].get('prompts', {}).keys())
        return []


# Global prompt manager instance
prompt_manager = AIPromptManager()


def get_ai_prompt(category: str, prompt_type: str, **kwargs) -> str:
    """Convenience function to get formatted prompt"""
    return prompt_manager.get_prompt(category, prompt_type, **kwargs)


def get_system_prompt(category: str) -> str:
    """Convenience function to get system prompt"""
    return prompt_manager.get_system_prompt(category)
