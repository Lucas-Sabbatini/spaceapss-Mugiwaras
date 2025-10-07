"""Retriever usando MongoDataManager."""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Adicionar agents ao sys.path para importar extract.models
agents_path = Path(__file__).parent.parent.parent.parent.parent
if str(agents_path) not in sys.path:
    sys.path.insert(0, str(agents_path))

from packages.api.app.services.mongo_data import MongoDataManager
from extract.models import ArticleMetadata
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)


class Retriever:
    """Retriever usando MongoDataManager com ArticleMetadata."""

    def __init__(self):
        """Inicializa retriever."""
        try:
            self.db_manager = MongoDataManager()
            log_info(logger, "Retriever inicializado com MongoDataManager")
        except Exception as e:
            log_error(logger, "Erro ao inicializar MongoDataManager", e)
            self.db_manager = None

    def retrieve(self, question: str, top_k: int = 5) -> List[ArticleMetadata]:
        """
        Recupera documentos relevantes usando MongoDataManager.
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de ArticleMetadata ordenados por relevância semântica
        """
        if self.db_manager is None:
            log_error(logger, "MongoDataManager não inicializado", Exception())
            return []

        try:
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
