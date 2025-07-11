"""
Configuration and environment settings for the chat agent
"""
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    """Application settings and configuration"""
    
    def __init__(self):
        self.azure_api_key = os.environ.get("AZURE_API_KEY")
        self.azure_api_base = os.environ.get("AZURE_API_BASE")
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        
        # Model configuration
        self.model_id = "azure/gpt-4-32k"
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that required environment variables are set"""
        required_vars = {
            "AZURE_API_KEY": self.azure_api_key,
            "AZURE_API_BASE": self.azure_api_base,
            "TAVILY_API_KEY": self.tavily_api_key
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
    
    @property
    def has_azure_config(self) -> bool:
        """Check if Azure configuration is available"""
        return bool(self.azure_api_key and self.azure_api_base)
    
    @property
    def has_tavily_config(self) -> bool:
        """Check if Tavily configuration is available"""
        return bool(self.tavily_api_key)


# Global settings instance
settings = Settings()
