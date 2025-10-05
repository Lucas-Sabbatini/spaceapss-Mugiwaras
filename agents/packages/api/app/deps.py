"""Dependências compartilhadas da API."""

from packages.api.app.agent.pipeline import get_pipeline


def get_pipeline_dependency():
    """Dependency para injetar pipeline do agente."""
    return get_pipeline()
