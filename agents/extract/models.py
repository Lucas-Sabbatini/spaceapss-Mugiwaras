"""
Modelos de dados para artigos científicos.

Este módulo contém dataclasses e estruturas de dados compartilhadas
para o sistema de enriquecimento de artigos.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ArticleMetadata:
    """
    Estrutura de dados para metadados completos de um artigo científico.
    
    Attributes:
        experiment_id: ID único do experimento (ex: PMC123456)
        doi: Digital Object Identifier
        title: Título do artigo
        abstract: Resumo/abstract original
        summary_en: Resumo estruturado em inglês gerado por LLM
        year: Ano de publicação
        authors: Lista de autores
        institutions: Lista de instituições/afiliações
        funding: Lista de fontes de financiamento
        objectives: Objetivos do estudo
        hypotheses: Hipóteses testadas
        organisms: Organismos/células estudados
        conditions: Condições experimentais (ex: microgravidade)
        methods: Métodos e técnicas utilizados
        parameters_measured: Parâmetros/variáveis medidos
        results_summary: Resumo dos resultados principais
        significant_findings: Descobertas significativas
        implications: Implicações práticas ou teóricas
        limitations: Limitações do estudo
        future_directions: Direções futuras sugeridas
        duration: Duração do experimento
        sample_size: Tamanho da amostra
        conditions_control: Grupos de controle
        related_projects: Projetos/missões relacionados
        citations: Número de citações
        mesh_terms: Termos MeSH do PubMed
        journal: Nome do jornal/revista
        pmid: PubMed ID
    """
    
    experiment_id: str
    doi: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    summary_en: Optional[str] = None
    year: Optional[int] = None
    authors: List[str] = None
    institutions: List[str] = None
    funding: List[str] = None
    objectives: List[str] = None
    hypotheses: List[str] = None
    organisms: List[str] = None
    conditions: List[str] = None
    methods: List[str] = None
    parameters_measured: List[str] = None
    results_summary: Optional[str] = None
    significant_findings: List[str] = None
    implications: List[str] = None
    limitations: List[str] = None
    future_directions: List[str] = None
    duration: Optional[str] = None
    sample_size: Optional[int] = None
    conditions_control: List[str] = None
    related_projects: List[str] = None
    citations: Optional[int] = None
    mesh_terms: List[str] = None
    journal: Optional[str] = None
    pmid: Optional[str] = None
    
    def __post_init__(self):
        """Inicializa listas vazias se None."""
        if self.authors is None:
            self.authors = []
        if self.institutions is None:
            self.institutions = []
        if self.funding is None:
            self.funding = []
        if self.objectives is None:
            self.objectives = []
        if self.hypotheses is None:
            self.hypotheses = []
        if self.organisms is None:
            self.organisms = []
        if self.conditions is None:
            self.conditions = []
        if self.methods is None:
            self.methods = []
        if self.parameters_measured is None:
            self.parameters_measured = []
        if self.significant_findings is None:
            self.significant_findings = []
        if self.implications is None:
            self.implications = []
        if self.limitations is None:
            self.limitations = []
        if self.future_directions is None:
            self.future_directions = []
        if self.conditions_control is None:
            self.conditions_control = []
        if self.related_projects is None:
            self.related_projects = []
        if self.mesh_terms is None:
            self.mesh_terms = []
    
    def to_dict(self) -> dict:
        """
        Converte o artigo para dicionário.
        
        Returns:
            Dicionário com todos os campos
        """
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ArticleMetadata':
        """
        Cria instância a partir de dicionário.
        
        Args:
            data: Dicionário com dados do artigo
            
        Returns:
            Instância de ArticleMetadata
        """
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
