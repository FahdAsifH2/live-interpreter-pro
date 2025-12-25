from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Live Interpreter Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Deepgram
    DEEPGRAM_API_KEY: str
    DEEPGRAM_MODEL: str = "nova-2"
    
    # DeepL
    DEEPL_API_KEY: str
    DEEPL_API_URL: str = "https://api-free.deepl.com/v2"
    
    # Azure Translator (fallback)
    AZURE_TRANSLATOR_KEY: Optional[str] = None
    AZURE_TRANSLATOR_ENDPOINT: Optional[str] = None
    AZURE_TRANSLATOR_REGION: Optional[str] = None
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Audio
    MAX_AUDIO_DURATION_SECONDS: int = 3600  # 1 hour
    AUDIO_CHUNK_SIZE: int = 4096
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

