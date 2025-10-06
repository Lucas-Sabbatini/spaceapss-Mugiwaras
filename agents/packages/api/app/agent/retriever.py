"""Retriever usando CosmosDataManager."""

from pathlib import Path
from typing import List, Dict, Any

from packages.api.app.config import get_settings
from packages.api.app.services.cosmos_data import CosmosDataManager
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)


class Retriever:
    """Retriever simples usando CosmosDataManager."""

    def __init__(self):
        """Inicializa retriever."""
        try:
            settings = get_settings()
            self.db_manager = CosmosDataManager(
                endpoint=settings.cosmos_endpoint,
                key=settings.cosmos_key,
                database_name=settings.cosmos_database,
                container_name=settings.cosmos_container,
                google_api_key=settings.google_api_key,
                google_embed_model=settings.google_embed_model
            )
            log_info(logger, "Retriever inicializado com CosmosDataManager")
        except Exception as e:
            log_error(logger, "Erro ao inicializar CosmosDataManager", e)
            self.db_manager = None

    def retrieve(self, question: str, top_k: int = 5) -> List[str]:
        """
        Recupera documentos relevantes usando CosmosDataManager.
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de strings relacionadas à pergunta
        """
        if self.db_manager is None:
            log_error(logger, "CosmosDataManager não inicializado", Exception())
            return []

        try:
            results = self.db_manager.query(query_text=question, n_results=top_k)
            with open("retrieved_results.txt", "w", encoding="utf-8") as f:
                for item in results:
                    f.write(item + "\n")
            log_info(
                logger,
                "Retrieval concluído",
                question_len=len(question),
                results=len(results),
            )
            
            return results

        except Exception as e:
            log_error(logger, "Erro no retrieval", e)
            return []
    
    def retrieve_with_metadata(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera documentos relevantes com metadados estruturados.
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de dicionários com dados estruturados dos documentos
        """
        if self.db_manager is None:
            log_error(logger, "CosmosDataManager não inicializado", Exception())
            return []

        try:
            results = self.db_manager.query_with_metadata(query_text=question, n_results=top_k)
            
            log_info(
                logger,
                "Retrieval com metadata concluído",
                question_len=len(question),
                results=len(results),
            )
            
            return results

        except Exception as e:
            log_error(logger, "Erro no retrieval com metadata", e)
            return []


# Singleton
_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    """Retorna instância singleton do retriever."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
