"""Configuração de fixtures pytest."""

import pytest


@pytest.fixture
def sample_article_data():
    """Fixture com dados de um artigo exemplo."""
    return {
        "id": "test-001",
        "title": "Test Article on Space Medicine",
        "authors": ["Doe, J.", "Smith, A."],
        "year": 2023,
        "doi": "10.1234/test.2023.001",
        "url": "https://example.com/article/test-001",
        "abstract": "This is a test abstract about space medicine and microgravity effects on human health.",
        "sections": [
            {
                "heading": "Introduction",
                "content": "Space medicine is an important field of study.",
            },
            {"heading": "Methods", "content": "We conducted experiments in simulated microgravity."},
        ],
        "references": ["Reference 1", "Reference 2"],
        "metadata": {"keywords": ["space", "medicine", "microgravity"]},
    }


@pytest.fixture
def sample_chat_request():
    """Fixture com request de chat exemplo."""
    return {"question": "What are the effects of microgravity on the human body?", "topK": 5}


@pytest.fixture
def mock_embedding():
    """Fixture com embedding mock (768 dims - Google Gemini)."""
    return [0.1] * 768
