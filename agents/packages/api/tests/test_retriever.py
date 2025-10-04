"""Testes para o retriever."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from packages.api.app.agent.retriever import Retriever


@pytest.fixture
def mock_redis_client():
    """Mock do RedisClient."""
    mock = MagicMock()
    mock.is_connected.return_value = False  # Usar fallback por padrão
    return mock


@pytest.fixture
def mock_embeddings_service():
    """Mock do EmbeddingsService."""
    mock = MagicMock()
    mock.get_embedding.return_value = [0.1] * 768
    mock.get_embeddings_batch.return_value = [[0.1] * 768, [0.2] * 768]
    return mock


@pytest.fixture
def sample_articles():
    """Artigos exemplo para fallback."""
    return [
        {
            "id": "art-001",
            "title": "Effects of Microgravity on Stem Cells",
            "abstract": "This study investigates microgravity effects on stem cells.",
            "year": 2023,
            "doi": "10.1234/example1",
            "embedding": [0.1] * 768,
        },
        {
            "id": "art-002",
            "title": "Radiation Protection in Space",
            "abstract": "Comprehensive review of radiation protection strategies.",
            "year": 2024,
            "doi": "10.1234/example2",
            "embedding": [0.2] * 768,
        },
        {
            "id": "art-003",
            "title": "Cardiovascular Adaptations in Spaceflight",
            "abstract": "Study of cardiovascular changes during long missions.",
            "year": 2023,
            "doi": "10.1234/example3",
            "embedding": [0.15] * 768,
        },
    ]


def test_retriever_initialization_redis_mode():
    """Testa inicialização do retriever em modo Redis."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service"):
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = True
            mock_get_redis.return_value = mock_redis

            retriever = Retriever()

            assert not retriever.use_fallback
            assert retriever.redis_client is not None


def test_retriever_initialization_fallback_mode():
    """Testa inicialização do retriever em modo fallback."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service"):
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = False
            mock_get_redis.return_value = mock_redis

            retriever = Retriever()

            assert retriever.use_fallback


def test_retrieve_redis_mode():
    """Testa retrieval em modo Redis."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service") as mock_get_emb:
            # Setup mocks
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = True
            mock_redis.search_vector.return_value = [
                {"id": "art-001", "title": "Test 1", "score": 0.9},
                {"id": "art-002", "title": "Test 2", "score": 0.8},
            ]
            mock_redis.search_text.return_value = [
                {"id": "art-001", "title": "Test 1"},
            ]
            mock_get_redis.return_value = mock_redis

            mock_emb = MagicMock()
            mock_emb.get_embedding.return_value = [0.1] * 768
            mock_get_emb.return_value = mock_emb

            retriever = Retriever()
            results = retriever.retrieve("test question", top_k=2)

            # Verificações
            assert len(results) <= 2
            mock_emb.get_embedding.assert_called_once()
            mock_redis.search_vector.assert_called_once()


def test_retrieve_returns_ordered_by_score():
    """Testa que resultados são ordenados por score."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service") as mock_get_emb:
            # Setup mocks
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = True
            mock_redis.search_vector.return_value = [
                {"id": "art-001", "title": "Low", "score": 0.5},
                {"id": "art-002", "title": "High", "score": 0.9},
                {"id": "art-003", "title": "Medium", "score": 0.7},
            ]
            mock_redis.search_text.return_value = []
            mock_get_redis.return_value = mock_redis

            mock_emb = MagicMock()
            mock_emb.get_embedding.return_value = [0.1] * 768
            mock_get_emb.return_value = mock_emb

            retriever = Retriever()
            results = retriever.retrieve("test", top_k=3)

            # Verificar ordenação (score maior primeiro após normalização)
            if len(results) > 1:
                assert results[0].get("score", 0) >= results[1].get("score", 0)


def test_retrieve_respects_top_k():
    """Testa que top_k é respeitado."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service") as mock_get_emb:
            # Setup mocks
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = True
            mock_redis.search_vector.return_value = [
                {"id": f"art-{i:03d}", "title": f"Article {i}", "score": 0.9 - i * 0.1}
                for i in range(10)
            ]
            mock_redis.search_text.return_value = []
            mock_get_redis.return_value = mock_redis

            mock_emb = MagicMock()
            mock_emb.get_embedding.return_value = [0.1] * 768
            mock_get_emb.return_value = mock_emb

            retriever = Retriever()
            results = retriever.retrieve("test", top_k=3)

            assert len(results) <= 3


def test_retrieve_handles_empty_results():
    """Testa comportamento com resultados vazios."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service") as mock_get_emb:
            # Setup mocks
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = True
            mock_redis.search_vector.return_value = []
            mock_redis.search_text.return_value = []
            mock_get_redis.return_value = mock_redis

            mock_emb = MagicMock()
            mock_emb.get_embedding.return_value = [0.1] * 768
            mock_get_emb.return_value = mock_emb

            retriever = Retriever()
            results = retriever.retrieve("test", top_k=5)

            assert len(results) == 0


def test_retrieve_handles_exceptions():
    """Testa tratamento de exceções."""
    with patch("packages.api.app.agent.retriever.get_redis_client") as mock_get_redis:
        with patch("packages.api.app.agent.retriever.get_embeddings_service") as mock_get_emb:
            # Setup mocks
            mock_redis = MagicMock()
            mock_redis.is_connected.return_value = True
            mock_redis.search_vector.side_effect = Exception("Redis error")
            mock_get_redis.return_value = mock_redis

            mock_emb = MagicMock()
            mock_emb.get_embedding.return_value = [0.1] * 768
            mock_get_emb.return_value = mock_emb

            retriever = Retriever()
            results = retriever.retrieve("test", top_k=5)

            # Deve retornar lista vazia em caso de erro
            assert results == []
