from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class VCenterSettings(BaseSettings):
    host: str = Field(..., description="vCenter Server hostname or IP")
    username: str = Field(..., description="vCenter username")
    password: SecretStr = Field(..., description="vCenter password")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

class NSXSettings(BaseSettings):
    manager: Optional[str] = Field(None, description="NSX Manager hostname or IP")
    username: Optional[str] = Field(None, description="NSX username")
    password: Optional[SecretStr] = Field(None, description="NSX password")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

class HCXSettings(BaseSettings):
    manager: str = Field(..., description="HCX Manager hostname or IP")
    username: str = Field(..., description="HCX username")
    password: SecretStr = Field(..., description="HCX password")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        env_prefix="APP_"
    )

    app_name: str = "VCF HCX Automator"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    vcenter: VCenterSettings
    nsx: NSXSettings = Field(default_factory=lambda: NSXSettings())
    hcx: HCXSettings

# Global settings instance
# Note: This will fail to instantiate if required env vars are missing.
# It is recommended to instantiate this in main or a dependency injection container.
