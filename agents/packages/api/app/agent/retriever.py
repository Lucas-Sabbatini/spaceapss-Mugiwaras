"""Retriever usando VectorDBManager."""

from pathlib import Path
from typing import List

from packages.api.app.services.vector_db import VectorDBManager
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)


class Retriever:
    """Retriever simples usando VectorDBManager."""

    def __init__(self):
        """Inicializa retriever."""
        try:
            # Caminho para o chroma_db relativo ao diretório do projeto
            db_path = str(Path(__file__).parent.parent.parent.parent.parent.parent / "chroma_db")
            self.db_manager = VectorDBManager(db_path=db_path)
            log_info(logger, "Retriever inicializado com VectorDBManager", db_path=db_path)
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


# Singleton
_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    """Retorna instância singleton do retriever."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
