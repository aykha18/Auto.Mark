"""
Configuration management for AI Marketing Agents
Uses Pydantic settings for type-safe configuration
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(..., env="DATABASE_URL")
    pool_size: int = Field(10, env="DB_POOL_SIZE")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DB_POOL_TIMEOUT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


class RedisConfig(BaseSettings):
    """Redis configuration"""
    url: str = Field("redis://localhost:6379", env="REDIS_URL")
    db: int = Field(0, env="REDIS_DB")
    password: Optional[str] = Field(None, env="REDIS_PASSWORD")


class APIConfig(BaseSettings):
    """API configuration"""
    host: str = Field("0.0.0.0", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    debug: bool = Field(False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    api_key_header: str = Field("X-API-Key", env="API_KEY_HEADER")
    cors_origins: list = Field(["http://localhost:3000", "http://localhost:3001", "https://*.railway.app"], env="CORS_ORIGINS")
    allowed_hosts: list = Field(["*"], env="ALLOWED_HOSTS")


class LangSmithConfig(BaseSettings):
    """LangSmith observability configuration"""
    tracing_v2: bool = Field(True, env="LANGCHAIN_TRACING_V2")
    endpoint: str = Field("https://api.smith.langchain.com", env="LANGCHAIN_ENDPOINT")
    api_key: str = Field(..., env="LANGCHAIN_API_KEY")
    project: str = Field("ai-marketing-agents", env="LANGCHAIN_PROJECT")


class PineconeConfig(BaseSettings):
    """Pinecone vector database configuration"""
    api_key: str = Field(..., env="PINECONE_API_KEY")
    environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    index_name: str = Field("marketing-knowledge", env="PINECONE_INDEX_NAME")
    dimension: int = Field(1536, env="PINECONE_DIMENSION")  # text-embedding-3-large


class LLMConfig(BaseSettings):
    """LLM configuration"""
    grok_api_key: str = Field(..., env="GROK_API_KEY")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str = Field("grok-2", env="LLM_MODEL")
    temperature: float = Field(0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(2000, env="LLM_MAX_TOKENS")


class ExternalAPIsConfig(BaseSettings):
    """External API configurations"""
    serpapi_key: str = Field(..., env="SERPAPI_KEY")
    google_ads_client_id: str = Field(..., env="GOOGLE_ADS_CLIENT_ID")
    google_ads_client_secret: str = Field(..., env="GOOGLE_ADS_CLIENT_SECRET")
    google_ads_developer_token: str = Field(..., env="GOOGLE_ADS_DEVELOPER_TOKEN")


class StripeConfig(BaseSettings):
    """Stripe payment processing configuration"""
    secret_key: str = Field(..., env="STRIPE_SECRET_KEY")
    publishable_key: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    webhook_secret: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    currency: str = Field("usd", env="STRIPE_CURRENCY")
    co_creator_price: float = Field(250.0, env="CO_CREATOR_PRICE")


class CircuitBreakerConfig(BaseSettings):
    """Circuit breaker configuration"""
    failure_threshold: int = Field(5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    recovery_timeout: int = Field(60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")
    expected_exception: tuple = Field((Exception,), env="CIRCUIT_BREAKER_EXCEPTIONS")


class Settings(BaseSettings):
    """Main application settings"""

    # Sub-configurations will be initialized after main settings
    database: Optional[DatabaseConfig] = None
    redis: Optional[RedisConfig] = None
    api: Optional[APIConfig] = None
    langsmith: Optional[LangSmithConfig] = None
    pinecone: Optional[PineconeConfig] = None
    llm: Optional[LLMConfig] = None
    external_apis: Optional[ExternalAPIsConfig] = None
    stripe: Optional[StripeConfig] = None
    circuit_breaker: Optional[CircuitBreakerConfig] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize sub-configurations after main settings are loaded
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.api = APIConfig()
        self.langsmith = LangSmithConfig()
        self.pinecone = PineconeConfig()
        self.llm = LLMConfig()
        self.external_apis = ExternalAPIsConfig()
        self.stripe = StripeConfig()
        self.circuit_breaker = CircuitBreakerConfig()

    # Application settings
    app_name: str = Field("AI Marketing Agents", env="APP_NAME")
    version: str = Field("0.1.0", env="APP_VERSION")
    environment: str = Field("development", env="ENVIRONMENT")

    # Performance settings
    max_concurrent_requests: int = Field(100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(30, env="REQUEST_TIMEOUT")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance (lazy loaded)
_settings = None


def get_settings() -> Settings:
    """Get application settings (lazy loaded)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility - removed to avoid circular import issues
# Use get_settings() instead of accessing settings directly


def is_development() -> bool:
    """Check if running in development mode"""
    return settings.environment.lower() == "development"


def is_production() -> bool:
    """Check if running in production mode"""
    return settings.environment.lower() == "production"