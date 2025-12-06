"""Configuration management for VCF HCX Automator."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # API Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = False
    
    # VCF/HCX Configuration
    vcf_host: Optional[str] = None
    vcf_username: Optional[str] = None
    vcf_password: Optional[str] = None
    vcf_verify_ssl: bool = True
    
    # Convex DB Configuration
    convex_url: Optional[str] = None
    convex_token: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"


settings = Settings()