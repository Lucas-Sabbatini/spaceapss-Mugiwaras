"""Wrapper para serviço de embeddings (Google Gemini)."""

from typing import List

import google.generativeai as genai

from packages.api.app.config import get_settings
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingsService:
    """Serviço de geração de embeddings."""

    def __init__(self):
        """Inicializa cliente Google Gemini."""
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.google_embed_model
        log_info(logger, "EmbeddingsService inicializado", provider="google_gemini", model=self.model)

    def get_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto."""
        try:
            # Limitar texto (Gemini aceita ~10k tokens)
            text = text[:40000]

            # Chamar API do Gemini
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )

            embedding = result['embedding']
            log_info(
                logger,
                "Embedding gerado",
                provider="google_gemini",
                dim=len(embedding),
                text_len=len(text),
            )
            return embedding

        except Exception as e:
            log_error(logger, "Erro ao gerar embedding", e, provider="google_gemini")
            raise

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos (batch)."""
        try:
            # Limitar textos
            texts = [text[:40000] for text in texts]

            # Gemini suporta batch com lista de textos
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])

            log_info(
                logger,
                "Embeddings batch gerados",
                provider="google_gemini",
                count=len(embeddings),
            )
            return embeddings

        except Exception as e:
            log_error(logger, "Erro ao gerar embeddings batch", e, provider="google_gemini")
            raise


# Singleton global
_embeddings_service: EmbeddingsService | None = None


def get_embeddings_service() -> EmbeddingsService:
    """Retorna instância singleton do serviço de embeddings."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
