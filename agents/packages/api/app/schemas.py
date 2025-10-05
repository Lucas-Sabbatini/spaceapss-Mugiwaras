"""Modelos Pydantic para validação de dados."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Section(BaseModel):
    """Seção de um artigo científico."""

    heading: str = Field(..., description="Título da seção")
    content: str = Field(..., description="Conteúdo da seção")


class Article(BaseModel):
    """Modelo completo de um artigo científico."""

    id: str = Field(..., description="ID único do artigo")
    title: str = Field(..., description="Título do artigo")
    authors: List[str] = Field(default_factory=list, description="Lista de autores (pode estar vazia)")
    year: Optional[int] = Field(None, description="Ano de publicação", ge=1900, le=2100)
    doi: Optional[str] = Field(None, description="DOI do artigo")
    url: Optional[str] = Field(None, description="URL do artigo")  # Mudado de HttpUrl para str
    abstract: str = Field(default="", description="Resumo do artigo")
    sections: Optional[List[Section]] = Field(None, description="Seções do artigo")
    references: Optional[List[str]] = Field(None, description="Referências bibliográficas")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "PMC5391430",
                "title": "Draft Genome Sequences of Several Fungal Strains",
                "authors": [],
                "year": None,
                "doi": None,
                "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5391430/",
                "abstract": "",
                "sections": None,
                "references": None,
                "metadata": {"source": "ChromaDB"},
            }
        }


class ChatRequest(BaseModel):
    """Requisição de chat para o agente."""

    question: str = Field(..., description="Pergunta sobre artigos científicos", min_length=3)
    topK: Optional[int] = Field(5, description="Número de artigos a recuperar", ge=1, le=20)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quais efeitos da microgravidade em células-tronco?",
                "topK": 5,
            }
        }


class SourceRef(BaseModel):
    """Referência a uma fonte/artigo."""

    id: str = Field(..., description="ID do artigo")
    title: str = Field(..., description="Título do artigo")
    year: Optional[int] = Field(None, description="Ano de publicação")
    doi: Optional[str] = Field(None, description="DOI do artigo")
    url: Optional[str] = Field(None, description="URL do artigo")  # Mudado de HttpUrl para str
    score: Optional[float] = Field(None, description="Score de relevância", ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Resposta do agente."""

    answer: str = Field(..., description="Resposta gerada pelo agente")
    sources: List[SourceRef] = Field(default_factory=list, description="Fontes utilizadas (opcional)")
    article: Optional[Article] = Field(None, description="Artigo mais relevante completo (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Estudos mostram que a microgravidade afeta a diferenciação de células-tronco...",
                "sources": [],
                "article": None,
            }
        }


class HealthResponse(BaseModel):
    """Resposta do health check."""

    status: str = Field(..., description="Status do serviço")
    redis: Optional[str] = Field(None, description="Status do Redis")
    version: str = Field("0.1.0", description="Versão da API")
