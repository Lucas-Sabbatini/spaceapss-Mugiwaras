"""Pipeline principal do agente."""

from typing import List

import google.generativeai as genai

from packages.api.app.agent.prompts import build_fallback_prompt, build_synthesis_prompt
from packages.api.app.agent.retriever import get_retriever
from packages.api.app.config import get_settings
from packages.api.app.schemas import Article, ChatResponse, SourceRef
from packages.api.app.services.logger import get_logger, log_error, log_info
from extract.models import ArticleMetadata

logger = get_logger(__name__)
settings = get_settings()


class AgentPipeline:
    """Pipeline orquestrador do agente com RAG usando ArticleMetadata."""

    def __init__(self):
        """Inicializa pipeline."""
        self.retriever = get_retriever()

        # Cliente LLM Google Gemini
        genai.configure(api_key=settings.google_api_key)
        self.chat_model = settings.google_chat_model

        log_info(logger, "AgentPipeline inicializado", provider="google_gemini")

    def answer(self, question: str, top_k: int = 5) -> ChatResponse:
        """
        Responde a uma pergunta sobre artigos científicos usando RAG.
        
        Fluxo:
        1. Recupera ArticleMetadata relevantes via busca vetorial
        2. Extrai campos essenciais para contexto (abstract, results, objectives, etc.)
        3. Sintetiza resposta usando LLM com contexto rico
        4. Monta sources e article a partir dos ArticleMetadata
        5. Retorna resposta completa
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a recuperar
            
        Returns:
            ChatResponse com resposta, sources e article
        """
        log_info(logger, "Pipeline iniciado", question_len=len(question), top_k=top_k)

        # 1. Retrieval - retorna lista de ArticleMetadata
        articles: List[ArticleMetadata] = self.retriever.retrieve(question, top_k=top_k)

        if not articles:
            # Sem documentos relevantes
            fallback_answer = build_fallback_prompt(question)
            log_info(logger, "Nenhum documento encontrado, retornando fallback")

            return ChatResponse(
                answer=fallback_answer,
                sources=[],
                article=None,
            )

        # 2. Preparar contexto para síntese - focar em campos essenciais (Nível 1)
        docs_for_synthesis = []
        for article in articles:
            context_parts = []
            
            # Campos essenciais (Nível 1) - alta densidade semântica
            if article.title:
                context_parts.append(f"TITLE: {article.title}")

            if article.authors:
                context_parts.append(f"AUTHORS: {', '.join(article.authors)}")
            
            if article.abstract:
                context_parts.append(f"ABSTRACT: {article.abstract}")
            
            if article.objectives:
                context_parts.append(f"OBJECTIVES: {'; '.join(article.objectives)}")
            
            if article.hypotheses:
                context_parts.append(f"HYPOTHESES: {'; '.join(article.hypotheses)}")
            
            if article.methods:
                context_parts.append(f"METHODS: {'; '.join(article.methods)}")
            
            if article.results_summary:
                context_parts.append(f"RESULTS: {article.results_summary}")
            
            if article.significant_findings:
                context_parts.append(f"KEY FINDINGS: {'; '.join(article.significant_findings)}")
            
            if article.implications:
                context_parts.append(f"IMPLICATIONS: {'; '.join(article.implications)}")
            
            if article.future_directions:
                context_parts.append(f"FUTURE DIRECTIONS: {'; '.join(article.future_directions)}")
            
            # Juntar tudo
            doc_text = "\n".join(context_parts)
            docs_for_synthesis.append(doc_text)

        # 3. Síntese com LLM
        answer_text = self._synthesize(question, docs_for_synthesis)

        # 4. Montar sources a partir dos ArticleMetadata
        sources = []
        for idx, article in enumerate(articles, 1):
            sources.append(
                SourceRef(
                    id=article.experiment_id,
                    title=article.title or f"Article {idx}",
                    year=article.year,
                    doi=article.doi,
                    url=f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article.experiment_id}/" if article.experiment_id else None,
                    score=None  # MongoDB $vectorSearch não retorna score diretamente
                )
            )

        # 5. Montar article completo (primeiro resultado - mais relevante)
        top_article = articles[0]
        article_response = Article(
            id=top_article.experiment_id,
            title=top_article.title or "Untitled",
            authors=top_article.authors or [],
            year=top_article.year,
            doi=top_article.doi,
            url=f"https://www.ncbi.nlm.nih.gov/pmc/articles/{top_article.experiment_id}/" if top_article.experiment_id else None,
            abstract=top_article.abstract or top_article.summary_en or "",
            sections=None,  # Poderia ser construído a partir dos campos estruturados
            references=None,
            metadata={
                "experiment_id": top_article.experiment_id,
                "journal": top_article.journal,
                "pmid": top_article.pmid,
                "organisms": top_article.organisms,
                "conditions": top_article.conditions,
                "duration": top_article.duration,
                "sample_size": top_article.sample_size,
                "citations": top_article.citations,
                "mesh_terms": top_article.mesh_terms,
            }
        )

        log_info(
            logger,
            "Pipeline concluído",
            answer_len=len(answer_text),
            sources_count=len(sources),
            article_id=article_response.id,
        )

        return ChatResponse(
            answer=answer_text, 
            sources=sources, 
            article=article_response
        )

    def _synthesize(self, question: str, docs: List[str]) -> str:
        """Sintetiza resposta usando LLM."""
        try:
            # Construir prompt
            prompt = build_synthesis_prompt(question, docs)

            # Chamar LLM do Gemini
            model = genai.GenerativeModel(self.chat_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )

            answer = response.text.strip()
            log_info(logger, "Síntese gerada", answer_len=len(answer))

            return answer

        except Exception as e:
            log_error(logger, "Erro ao sintetizar resposta", e)
            return "Erro ao gerar resposta. Por favor, tente novamente."


# Singleton
_pipeline: AgentPipeline | None = None


def get_pipeline() -> AgentPipeline:
    """Retorna instância singleton do pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = AgentPipeline()
    return _pipeline
