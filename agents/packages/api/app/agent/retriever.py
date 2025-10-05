"""Retriever usando VectorDBManager."""

from pathlib import Path
from typing import List, Dict, Any

from packages.api.app.services.vector_db import VectorDBManager
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)


class Retriever:
    """Retriever simples usando VectorDBManager."""

    def __init__(self):
        """Inicializa retriever."""
        try:
            self.db_manager = VectorDBManager()
            log_info(logger, "Retriever inicializado com VectorDBManager")
        except Exception as e:
            log_error(logger, "Erro ao inicializar VectorDBManager", e)
            self.db_manager = None

    def retrieve(self, question: str, top_k: int = 5) -> List[str]:
        """
        Recupera documentos relevantes usando VectorDBManager.
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de strings relacionadas à pergunta
        """
        if self.db_manager is None:
            log_error(logger, "VectorDBManager não inicializado", Exception())
            return []

        try:
            # Usar o método query do VectorDBManager
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
            log_error(logger, "VectorDBManager não inicializado", Exception())
            return []

        try:
            # Usar o novo método query_with_metadata
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
