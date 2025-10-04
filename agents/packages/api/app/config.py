"""Configurações da aplicação."""

from functools import lru_cache
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # LLM Provider
    provider: Literal["openai", "azure"] = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_embed_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_embed_deployment: str = ""
    azure_openai_chat_deployment: str = ""
    azure_openai_api_version: str = "2024-06-01"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_username: str = ""
    redis_password: str = ""

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
