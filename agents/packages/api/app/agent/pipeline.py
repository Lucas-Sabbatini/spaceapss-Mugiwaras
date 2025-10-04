"""Pipeline principal do agente."""

from typing import Any, Dict

from openai import AzureOpenAI, OpenAI

from packages.api.app.agent.prompts import build_fallback_prompt, build_synthesis_prompt
from packages.api.app.agent.ranker import rerank_by_year
from packages.api.app.agent.retriever import get_retriever
from packages.api.app.config import get_settings
from packages.api.app.schemas import Article, ChatResponse, SourceRef
from packages.api.app.services.logger import get_logger, log_error, log_info
from packages.api.app.services.redis_client import get_redis_client

logger = get_logger(__name__)
settings = get_settings()


class AgentPipeline:
    """Pipeline orquestrador do agente."""

    def __init__(self):
        """Inicializa pipeline."""
        self.retriever = get_retriever()
        self.redis_client = get_redis_client()

        # Cliente LLM
        if settings.provider == "openai":
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
            self.chat_model = settings.openai_chat_model
        else:
            self.llm_client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )
            self.chat_model = settings.azure_openai_chat_deployment

        log_info(logger, "AgentPipeline inicializado", provider=settings.provider)

    def answer(self, question: str, top_k: int = 5) -> ChatResponse:
        """
        Responde a uma pergunta sobre artigos científicos.
        
        Fluxo:
        1. Recupera documentos relevantes (híbrido: vetorial + textual)
        2. Re-rankeia por ano (mais recentes ganham bônus)
        3. Sintetiza resposta usando LLM
        4. Retorna resposta + fontes + artigo completo
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a recuperar
            
        Returns:
            ChatResponse com resposta, fontes e artigo
        """
        log_info(logger, "Pipeline iniciado", question_len=len(question), top_k=top_k)

        # 1. Retrieval
        docs = self.retriever.retrieve(question, top_k=top_k)

        if not docs:
            # Sem documentos relevantes
            fallback_answer = build_fallback_prompt(question)
            log_info(logger, "Nenhum documento encontrado, retornando fallback")

            # Retornar resposta vazia mas válida
            return ChatResponse(
                answer=fallback_answer,
                sources=[],
                article=Article(
                    id="none",
                    title="N/A",
                    authors=[],
                    year=2024,
                    abstract="Nenhum artigo encontrado",
                ),
            )

        # 2. Re-rank por ano
        ranked_docs = rerank_by_year(docs, year_weight=0.1)

        # 3. Síntese com LLM
        answer_text = self._synthesize(question, ranked_docs)

        # 4. Montar fontes
        sources = [
            SourceRef(
                id=doc.get("id", ""),
                title=doc.get("title", ""),
                year=doc.get("year"),
                doi=doc.get("doi"),
                url=doc.get("url"),
                score=doc.get("score"),
            )
            for doc in ranked_docs[:5]
        ]

        # 5. Recuperar artigo completo do mais relevante
        top_article_id = ranked_docs[0].get("id")
        top_article_data = self._get_full_article(top_article_id)

        log_info(
            logger,
            "Pipeline concluído",
            answer_len=len(answer_text),
            sources_count=len(sources),
            top_article=top_article_id,
        )

        return ChatResponse(answer=answer_text, sources=sources, article=top_article_data)

    def _synthesize(self, question: str, docs: list[Dict[str, Any]]) -> str:
        """Sintetiza resposta usando LLM."""
        try:
            # Construir prompt
            prompt = build_synthesis_prompt(question, docs)

            # Chamar LLM
            response = self.llm_client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )

            answer = response.choices[0].message.content.strip()
            log_info(logger, "Síntese gerada", answer_len=len(answer))

            return answer

        except Exception as e:
            log_error(logger, "Erro ao sintetizar resposta", e)
            return "Erro ao gerar resposta. Por favor, tente novamente."

    def _get_full_article(self, article_id: str) -> Article:
        """Recupera artigo completo do banco."""
        # Tentar Redis primeiro
        if self.redis_client.is_connected():
            article_data = self.redis_client.get_article(article_id)
            if article_data:
                return Article(**article_data)

        # Fallback: buscar no retriever
        if self.retriever.use_fallback:
            for art in self.retriever._fallback_articles:
                if art.get("id") == article_id:
                    return Article(**art)

        # Se não encontrar, retornar artigo vazio
        log_error(logger, "Artigo não encontrado", Exception(), article_id=article_id)
        return Article(
            id=article_id,
            title="Artigo não encontrado",
            authors=[],
            year=2024,
            abstract="Não foi possível recuperar os dados completos do artigo.",
        )


# Singleton
_pipeline: AgentPipeline | None = None


def get_pipeline() -> AgentPipeline:
    """Retorna instância singleton do pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = AgentPipeline()
    return _pipeline
