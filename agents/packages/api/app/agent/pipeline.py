"""Pipeline principal do agente."""

from typing import List

import google.generativeai as genai

from packages.api.app.agent.prompts import build_fallback_prompt, build_synthesis_prompt
from packages.api.app.agent.retriever import get_retriever
from packages.api.app.config import get_settings
from packages.api.app.schemas import ChatResponse
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)
settings = get_settings()


class AgentPipeline:
    """Pipeline orquestrador do agente."""

    def __init__(self):
        """Inicializa pipeline."""
        self.retriever = get_retriever()

        # Cliente LLM Google Gemini
        genai.configure(api_key=settings.google_api_key)
        self.chat_model = settings.google_chat_model

        log_info(logger, "AgentPipeline inicializado", provider="google_gemini")

    def answer(self, question: str, top_k: int = 5) -> ChatResponse:
        """
        Responde a uma pergunta sobre artigos científicos.
        
        Fluxo:
        1. Recupera documentos relevantes usando VectorDBManager
        2. Sintetiza resposta usando LLM com os documentos como contexto
        3. Retorna resposta
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a recuperar
            
        Returns:
            ChatResponse com resposta
        """
        log_info(logger, "Pipeline iniciado", question_len=len(question), top_k=top_k)

        # 1. Retrieval - retorna lista de strings
        docs = self.retriever.retrieve(question, top_k=top_k)

        if not docs:
            # Sem documentos relevantes
            fallback_answer = build_fallback_prompt(question)
            log_info(logger, "Nenhum documento encontrado, retornando fallback")

            return ChatResponse(
                answer=fallback_answer,
                sources=[],
                article=None,
            )

        # 2. Síntese com LLM
        answer_text = self._synthesize(question, docs)

        log_info(
            logger,
            "Pipeline concluído",
            answer_len=len(answer_text),
            docs_count=len(docs),
        )

        return ChatResponse(answer=answer_text, sources=[], article=None)

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
