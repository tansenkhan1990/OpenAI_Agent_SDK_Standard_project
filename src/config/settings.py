"""
Configuration management for the Agentic AI application.
Follows 12-factor app principles: configuration from environment.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from src.utils.constants import (
    OLLAMA_DEFAULT_BASE_URL,
    OLLAMA_DEFAULT_API_KEY,
    OLLAMA_MODEL_NAME,
    LOG_LEVEL,
)


@dataclass
class OllamaConfig:
    """Ollama model provider configuration."""
    base_url: str
    api_key: str
    model_name: str
    
    @staticmethod
    def from_env() -> "OllamaConfig":
        """Create from environment variables."""
        load_dotenv()
        return OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", OLLAMA_DEFAULT_BASE_URL),
            api_key=os.getenv("OLLAMA_API_KEY", OLLAMA_DEFAULT_API_KEY),
            model_name=os.getenv("OLLAMA_MODEL_NAME", OLLAMA_MODEL_NAME),
        )
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.base_url:
            raise ValueError("OLLAMA_BASE_URL is required")
        if not self.api_key:
            raise ValueError("OLLAMA_API_KEY is required")
        if not self.model_name:
            raise ValueError("OLLAMA_MODEL_NAME is required")


@dataclass
class ApplicationConfig:
    """Main application configuration."""
    ollama: OllamaConfig
    log_level: str = LOG_LEVEL
    debug: bool = False
    enable_tracing: bool = False
    
    @staticmethod
    def from_env() -> "ApplicationConfig":
        """Create from environment variables."""
        load_dotenv()
        
        config = ApplicationConfig(
            ollama=OllamaConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", LOG_LEVEL),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            enable_tracing=os.getenv("ENABLE_TRACING", "false").lower() == "true",
        )
        
        config.validate()
        return config
    
    def validate(self) -> None:
        """Validate entire configuration."""
        self.ollama.validate()
        if self.log_level.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}")


# Global configuration instance
_config: Optional[ApplicationConfig] = None


def get_config() -> ApplicationConfig:
    """Get the global application configuration (lazy loaded)."""
    global _config
    if _config is None:
        _config = ApplicationConfig.from_env()
    return _config


def reload_config() -> ApplicationConfig:
    """Force reload of configuration."""
    global _config
    _config = ApplicationConfig.from_env()
    return _config
