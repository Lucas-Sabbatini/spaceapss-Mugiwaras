"""Dependências compartilhadas da API."""

from packages.api.app.agent.pipeline import get_pipeline
from packages.api.app.services.redis_client import get_redis_client


def get_redis_dependency():
    """Dependency para injetar cliente Redis."""
    return get_redis_client()


def get_pipeline_dependency():
    """Dependency para injetar pipeline do agente."""
    return get_pipeline()
