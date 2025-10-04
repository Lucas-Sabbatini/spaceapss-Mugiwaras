"""Cliente Redis com suporte a RedisJSON e RediSearch."""

import json
from typing import Any, Dict, List, Optional

import redis
from redis.commands.json.path import Path
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from packages.api.app.config import get_settings
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)
settings = get_settings()


class RedisClient:
    """Cliente Redis com RedisJSON e RediSearch."""

    def __init__(self):
        """Inicializa conexão com Redis."""
        self.client: Optional[redis.Redis] = None
        self.index_name = "idx:articles"
        self.key_prefix = "article:"
        self._connected = False

    def connect(self) -> bool:
        """Conecta ao Redis e cria índice se necessário."""
        try:
            # Parsear URL
            url = settings.redis_url
            username = settings.redis_username or None
            password = settings.redis_password or None

            self.client = redis.from_url(
                url, username=username, password=password, decode_responses=True
            )

            # Testar conexão
            self.client.ping()
            log_info(logger, "Conectado ao Redis", url=url)

            # Criar índice se não existir
            self._create_index()
            self._connected = True
            return True

        except Exception as e:
            log_error(logger, "Erro ao conectar ao Redis", e, url=settings.redis_url)
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """Verifica se está conectado."""
        return self._connected and self.client is not None

    def _create_index(self) -> None:
        """Cria índice vetorial no Redis se não existir."""
        if not self.client:
            return

        try:
            # Verificar se índice já existe
            self.client.ft(self.index_name).info()
            log_info(logger, "Índice já existe", index=self.index_name)
            return
        except redis.exceptions.ResponseError:
            pass

        try:
            # Definir schema do índice
            schema = [
                TextField("$.title", as_name="title"),
                TextField("$.abstract", as_name="abstract"),
                NumericField("$.year", as_name="year"),
                TagField("$.doi", as_name="doi"),
                VectorField(
                    "$.embedding",
                    "FLAT",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": 768,  # Google Gemini text-embedding-004
                        "DISTANCE_METRIC": "COSINE",
                    },
                    as_name="embedding",
                ),
            ]

            # Criar índice
            definition = IndexDefinition(prefix=[self.key_prefix], index_type=IndexType.JSON)

            self.client.ft(self.index_name).create_index(schema, definition=definition)
            log_info(logger, "Índice criado com sucesso", index=self.index_name)

        except Exception as e:
            log_error(logger, "Erro ao criar índice", e, index=self.index_name)

    def set_article(self, article_id: str, article_data: Dict[str, Any]) -> bool:
        """Salva artigo no Redis usando JSON.SET."""
        if not self.client:
            return False

        try:
            key = f"{self.key_prefix}{article_id}"
            self.client.json().set(key, Path.root_path(), article_data)
            log_info(logger, "Artigo salvo", article_id=article_id)
            return True
        except Exception as e:
            log_error(logger, "Erro ao salvar artigo", e, article_id=article_id)
            return False

    def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Recupera artigo do Redis."""
        if not self.client:
            return None

        try:
            key = f"{self.key_prefix}{article_id}"
            data = self.client.json().get(key)
            return data
        except Exception as e:
            log_error(logger, "Erro ao recuperar artigo", e, article_id=article_id)
            return None

    def update_embedding(self, article_id: str, embedding: List[float]) -> bool:
        """Atualiza embedding de um artigo."""
        if not self.client:
            return False

        try:
            key = f"{self.key_prefix}{article_id}"
            self.client.json().set(key, Path(".embedding"), embedding)
            log_info(logger, "Embedding atualizado", article_id=article_id)
            return True
        except Exception as e:
            log_error(logger, "Erro ao atualizar embedding", e, article_id=article_id)
            return False

    def search_vector(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Busca vetorial (KNN) no Redis."""
        if not self.client:
            return []

        try:
            # Criar query KNN
            query = (
                Query(f"*=>[KNN {top_k} @embedding $vec AS score]")
                .return_fields("title", "abstract", "year", "doi", "score")
                .sort_by("score")
                .paging(0, top_k)
                .dialect(2)
            )

            # Executar busca - converter embedding para bytes (array de float32)
            import struct
            vec_bytes = struct.pack(f"{len(query_embedding)}f", *query_embedding)
            params = {"vec": vec_bytes}
            results = self.client.ft(self.index_name).search(query, params)

            # Processar resultados
            docs = []
            for doc in results.docs:
                docs.append(
                    {
                        "id": doc.id.replace(self.key_prefix, ""),
                        "title": doc.title,
                        "abstract": doc.abstract,
                        "year": int(doc.year) if hasattr(doc, "year") else None,
                        "doi": doc.doi if hasattr(doc, "doi") else None,
                        "score": float(doc.score),
                    }
                )

            log_info(logger, "Busca vetorial executada", num_results=len(docs))
            return docs

        except Exception as e:
            log_error(logger, "Erro na busca vetorial", e)
            return []

    def search_text(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca textual (BM25) no Redis."""
        if not self.client:
            return []

        try:
            # Sanitizar query
            query_text = query_text.replace('"', '\\"')

            # Criar query BM25
            query = (
                Query(f"@title|abstract:({query_text})")
                .return_fields("title", "abstract", "year", "doi")
                .paging(0, top_k)
            )

            # Executar busca
            results = self.client.ft(self.index_name).search(query)

            # Processar resultados
            docs = []
            for doc in results.docs:
                docs.append(
                    {
                        "id": doc.id.replace(self.key_prefix, ""),
                        "title": doc.title,
                        "abstract": doc.abstract,
                        "year": int(doc.year) if hasattr(doc, "year") else None,
                        "doi": doc.doi if hasattr(doc, "doi") else None,
                    }
                )

            log_info(logger, "Busca textual executada", num_results=len(docs))
            return docs

        except Exception as e:
            log_error(logger, "Erro na busca textual", e)
            return []

    def list_all_keys(self, pattern: str = "article:*") -> List[str]:
        """Lista todas as chaves que correspondem ao padrão."""
        if not self.client:
            return []

        try:
            keys = self.client.keys(pattern)
            return [key.replace(self.key_prefix, "") for key in keys]
        except Exception as e:
            log_error(logger, "Erro ao listar chaves", e)
            return []

    def close(self) -> None:
        """Fecha conexão com Redis."""
        if self.client:
            self.client.close()
            log_info(logger, "Conexão com Redis fechada")


# Singleton global
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Retorna instância singleton do cliente Redis."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        _redis_client.connect()
    return _redis_client
