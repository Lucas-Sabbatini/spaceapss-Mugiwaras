"""Wrapper para serviço de embeddings (OpenAI/Azure OpenAI)."""

from typing import List

from openai import AzureOpenAI, OpenAI

from packages.api.app.config import get_settings
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingsService:
    """Serviço de geração de embeddings."""

    def __init__(self):
        """Inicializa cliente OpenAI ou Azure OpenAI."""
        self.provider = settings.provider
        self.client = None

        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_embed_model
            log_info(logger, "EmbeddingsService inicializado", provider="openai")

        elif self.provider == "azure":
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )
            self.model = settings.azure_openai_embed_deployment
            log_info(logger, "EmbeddingsService inicializado", provider="azure")

    def get_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto."""
        if not self.client:
            raise ValueError("Cliente de embeddings não inicializado")

        try:
            # Limitar texto a ~8000 tokens (aproximado)
            text = text[:32000]

            # Chamar API
            response = self.client.embeddings.create(input=[text], model=self.model)

            embedding = response.data[0].embedding
            log_info(
                logger,
                "Embedding gerado",
                provider=self.provider,
                dim=len(embedding),
                text_len=len(text),
            )
            return embedding

        except Exception as e:
            log_error(logger, "Erro ao gerar embedding", e, provider=self.provider)
            raise

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos (batch)."""
        if not self.client:
            raise ValueError("Cliente de embeddings não inicializado")

        try:
            # Limitar textos
            texts = [text[:32000] for text in texts]

            # Chamar API
            response = self.client.embeddings.create(input=texts, model=self.model)

            embeddings = [item.embedding for item in response.data]
            log_info(
                logger,
                "Embeddings batch gerados",
                provider=self.provider,
                count=len(embeddings),
            )
            return embeddings

        except Exception as e:
            log_error(logger, "Erro ao gerar embeddings batch", e, provider=self.provider)
            raise


# Singleton global
_embeddings_service: EmbeddingsService | None = None


def get_embeddings_service() -> EmbeddingsService:
    """Retorna instância singleton do serviço de embeddings."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
