"""Configurações da aplicação."""

from functools import lru_cache
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # Google Gemini
    google_api_key: str = ""
    google_embed_model: str = "models/text-embedding-004"
    google_chat_model: str = "gemini-2.0-flash"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_username: str = ""
    redis_password: str = ""

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_database: str = "spaceapss"
    mongodb_collection: str = "experiments"

    # API
    api_port: int = 8000
    env: Literal["dev", "prod"] = "dev"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de origens CORS."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_dev(self) -> bool:
        """Retorna True se ambiente é dev."""
        return self.env == "dev"


@lru_cache
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()