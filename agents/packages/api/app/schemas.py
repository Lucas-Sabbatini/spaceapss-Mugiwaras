"""Modelos Pydantic para validação de dados."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Section(BaseModel):
    """Seção de um artigo científico."""

    heading: str = Field(..., description="Título da seção")
    content: str = Field(..., description="Conteúdo da seção")


class ArticleDetail(BaseModel):
    """Modelo completo de um artigo enriquecido do MongoDB."""

    experiment_id: str = Field(..., description="ID único do experimento (ex: PMC9267413)")
    doi: Optional[str] = Field(None, description="DOI do artigo")
    title: Optional[str] = Field(None, description="Título do artigo")
    abstract: Optional[str] = Field(None, description="Resumo original")
    summary_en: Optional[str] = Field(None, description="Resumo em inglês")
    year: Optional[int] = Field(None, description="Ano de publicação")
    url: Optional[str] = Field(None, description="URL do artigo original")
    authors: List[str] = Field(default_factory=list, description="Lista de autores")
    institutions: List[str] = Field(default_factory=list, description="Instituições")
    funding: List[str] = Field(default_factory=list, description="Fontes de financiamento")
    objectives: List[str] = Field(default_factory=list, description="Objetivos do estudo")
    hypotheses: List[str] = Field(default_factory=list, description="Hipóteses testadas")
    organisms: List[str] = Field(default_factory=list, description="Organismos estudados")
    conditions: List[str] = Field(default_factory=list, description="Condições experimentais")
    methods: List[str] = Field(default_factory=list, description="Métodos utilizados")
    parameters_measured: List[str] = Field(default_factory=list, description="Parâmetros medidos")
    results_summary: Optional[str] = Field(None, description="Resumo dos resultados")
    significant_findings: List[str] = Field(default_factory=list, description="Descobertas significativas")
    implications: List[str] = Field(default_factory=list, description="Implicações")
    limitations: List[str] = Field(default_factory=list, description="Limitações do estudo")
    future_directions: List[str] = Field(default_factory=list, description="Direções futuras")
    duration: Optional[str] = Field(None, description="Duração do experimento")
    sample_size: Optional[int] = Field(None, description="Tamanho da amostra")
    conditions_control: List[str] = Field(default_factory=list, description="Grupos controle")
    related_projects: List[str] = Field(default_factory=list, description="Projetos relacionados")
    citations: Optional[int] = Field(None, description="Número de citações")
    full_text: Optional[str] = Field(None, description="Texto completo")
    mesh_terms: List[str] = Field(default_factory=list, description="Termos MeSH")
    journal: Optional[str] = Field(None, description="Nome do journal")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")

    class Config:
        json_schema_extra = {
            "example": {
                "experiment_id": "PMC9267413",
                "title": "Effects of Microgravity on Cell Behavior",
                "authors": ["John Doe", "Jane Smith"],
                "year": 2022,
                "abstract": "This study investigates...",
                "summary_en": "This study investigates the effects of microgravity...",
            }
        }


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
