"""Testes para schemas Pydantic."""

import pytest
from pydantic import ValidationError

from packages.api.app.schemas import Article, ChatRequest, ChatResponse, Section, SourceRef


def test_section_validation():
    """Testa validação de Section."""
    # Válido
    section = Section(heading="Introduction", content="This is the intro.")
    assert section.heading == "Introduction"
    assert section.content == "This is the intro."

    # Inválido - faltando campos
    with pytest.raises(ValidationError):
        Section(heading="Test")


def test_article_validation(sample_article_data):
    """Testa validação de Article."""
    # Válido
    article = Article(**sample_article_data)
    assert article.id == "test-001"
    assert article.title == "Test Article on Space Medicine"
    assert len(article.authors) == 2
    assert article.year == 2023
    assert article.doi == "10.1234/test.2023.001"

    # Inválido - ano fora do range
    invalid_data = sample_article_data.copy()
    invalid_data["year"] = 1800
    with pytest.raises(ValidationError):
        Article(**invalid_data)

    # Inválido - faltando campo obrigatório
    invalid_data = sample_article_data.copy()
    del invalid_data["title"]
    with pytest.raises(ValidationError):
        Article(**invalid_data)


def test_chat_request_validation(sample_chat_request):
    """Testa validação de ChatRequest."""
    # Válido
    request = ChatRequest(**sample_chat_request)
    assert request.question == "What are the effects of microgravity on the human body?"
    assert request.topK == 5

    # Válido - topK opcional
    request2 = ChatRequest(question="Test question")
    assert request2.topK == 5  # default

    # Inválido - question muito curta
    with pytest.raises(ValidationError):
        ChatRequest(question="Hi", topK=5)

    # Inválido - topK fora do range
    with pytest.raises(ValidationError):
        ChatRequest(question="Valid question here", topK=50)


def test_source_ref_validation():
    """Testa validação de SourceRef."""
    # Válido
    source = SourceRef(
        id="art-001",
        title="Test Article",
        year=2023,
        doi="10.1234/test",
        url="https://example.com",
        score=0.95,
    )
    assert source.id == "art-001"
    assert source.score == 0.95

    # Válido - campos opcionais
    source2 = SourceRef(id="art-002", title="Another Article")
    assert source2.year is None
    assert source2.score is None


def test_chat_response_validation(sample_article_data):
    """Testa validação de ChatResponse."""
    # Válido
    article = Article(**sample_article_data)
    sources = [
        SourceRef(id="art-001", title="Article 1", score=0.9),
        SourceRef(id="art-002", title="Article 2", score=0.8),
    ]

    response = ChatResponse(
        answer="Microgravity affects the human body in multiple ways...", sources=sources, article=article
    )

    assert len(response.answer) > 0
    assert len(response.sources) == 2
    assert response.article.id == "test-001"

    # Inválido - faltando campos obrigatórios
    with pytest.raises(ValidationError):
        ChatResponse(answer="Test", sources=[])


def test_article_with_sections(sample_article_data):
    """Testa Article com seções."""
    article = Article(**sample_article_data)

    assert len(article.sections) == 2
    assert article.sections[0].heading == "Introduction"
    assert article.sections[1].heading == "Methods"


def test_article_without_optional_fields():
    """Testa Article sem campos opcionais."""
    minimal_article = Article(
        id="min-001",
        title="Minimal Article",
        authors=["Author, A."],
        year=2024,
        abstract="A minimal abstract.",
    )

    assert minimal_article.doi is None
    assert minimal_article.url is None
    assert minimal_article.sections is None
    assert minimal_article.references is None
    assert minimal_article.metadata is None
