from pydantic import Field
from pydantic_settings import BaseSettings

from src.schemas.enums import LogLevel, Environment


class AppConfig(BaseSettings):
    """Application configuration using environment variables."""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Enable auto-reload in development")
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    
    # App Configuration (used in frontend)
    app_title: str = Field(default="AutoMail Agent", description="Application title")
    app_description: str = Field(default="Automated Gmail Sender", description="Application description")
    
    # Logging Configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    log_date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Log date format"
    )
    
    # Browser Configuration
    browser_timeout: int = Field(default=30000, description="Browser timeout in milliseconds")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
config = AppConfig() 