import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API 설정
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 7000
    
    # OpenAI 설정
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_TTL: int = 86400  # 24시간
    
    # MariaDB 설정
    MARIADB_HOST: str = "localhost"
    MARIADB_PORT: int = 3306
    MARIADB_DATABASE: str = "chatbot_db"
    MARIADB_USER: str = "chatbot_user"
    MARIADB_PASSWORD: str = "chatbot_password"
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()