"""Dependências compartilhadas da API."""

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from packages.api.app.agent.pipeline import get_pipeline
from packages.api.app.config import get_settings


def get_pipeline_dependency():
    """Dependency para injetar pipeline do agente."""
    return get_pipeline()


@lru_cache
def get_mongodb_client() -> MongoClient:
    """Retorna cliente MongoDB singleton."""
    settings = get_settings()
    return MongoClient(settings.mongodb_uri)


def get_mongodb_database() -> Database:
    """Dependency para injetar database MongoDB."""
    settings = get_settings()
    client = get_mongodb_client()
    return client[settings.mongodb_database]
