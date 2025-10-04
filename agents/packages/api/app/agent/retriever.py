"""Retriever para busca híbrida (vetorial + textual)."""

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from packages.api.app.agent.ranker import combine_scores
from packages.api.app.services.embeddings import get_embeddings_service
from packages.api.app.services.logger import get_logger, log_error, log_info
from packages.api.app.services.redis_client import get_redis_client

logger = get_logger(__name__)


class Retriever:
    """Retriever híbrido com fallback para modo offline."""

    def __init__(self):
        """Inicializa retriever."""
        self.redis_client = get_redis_client()
        self.embeddings_service = get_embeddings_service()
        self.use_fallback = not self.redis_client.is_connected()

        # Cache para fallback
        self._fallback_articles: List[Dict[str, Any]] = []
        self._fallback_embeddings: np.ndarray | None = None
        self._tfidf_vectorizer: TfidfVectorizer | None = None
        self._tfidf_matrix: np.ndarray | None = None

        if self.use_fallback:
            log_info(logger, "Retriever iniciado em modo FALLBACK (sem Redis)")
            self._load_fallback_data()
        else:
            log_info(logger, "Retriever iniciado com Redis")

    def _load_fallback_data(self) -> None:
        """Carrega dados em memória para modo fallback."""
        try:
            # Procurar samples na pasta ingest
            samples_dir = Path(__file__).parent.parent.parent.parent / "ingest" / "data" / "samples"

            if not samples_dir.exists():
                log_error(logger, "Pasta de samples não encontrada", Exception(), path=samples_dir)
                return

            # Carregar todos os JSONs
            articles = []
            for json_file in samples_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        article = json.load(f)
                        articles.append(article)
                except Exception as e:
                    log_error(logger, f"Erro ao carregar {json_file.name}", e)

            if not articles:
                log_info(logger, "Nenhum artigo encontrado no fallback")
                return

            self._fallback_articles = articles
            log_info(logger, "Artigos carregados no fallback", count=len(articles))

            # Gerar embeddings se necessário
            if not all("embedding" in art for art in articles):
                texts = []
                for art in articles:
                    text = f"{art.get('title', '')} {art.get('abstract', '')}"
                    texts.append(text)

                try:
                    embeddings = self.embeddings_service.get_embeddings_batch(texts)
                    for art, emb in zip(articles, embeddings):
                        art["embedding"] = emb
                except Exception as e:
                    log_error(logger, "Erro ao gerar embeddings no fallback", e)

            # Criar matriz de embeddings
            embeddings_list = [art.get("embedding", []) for art in articles if "embedding" in art]
            if embeddings_list:
                self._fallback_embeddings = np.array(embeddings_list, dtype=np.float32)

            # Criar TF-IDF para busca textual
            texts = [
                f"{art.get('title', '')} {art.get('abstract', '')}" for art in self._fallback_articles
            ]
            self._tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
            self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(texts)

            log_info(logger, "Fallback data preparado com sucesso")

        except Exception as e:
            log_error(logger, "Erro ao carregar fallback data", e)

    def retrieve(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera documentos relevantes usando busca híbrida.
        
        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de documentos ordenados por relevância
        """
        if self.use_fallback:
            return self._retrieve_fallback(question, top_k)
        else:
            return self._retrieve_redis(question, top_k)

    def _retrieve_redis(self, question: str, top_k: int) -> List[Dict[str, Any]]:
        """Busca híbrida usando Redis."""
        try:
            # 1. Gerar embedding da pergunta
            query_embedding = self.embeddings_service.get_embedding(question)

            # 2. Busca vetorial (KNN)
            vector_results = self.redis_client.search_vector(query_embedding, top_k=top_k)

            # 3. Busca textual (BM25)
            text_results = self.redis_client.search_text(question, top_k=top_k)

            # 4. Combinar scores (híbrido)
            combined = combine_scores(vector_results, text_results, alpha=0.7)

            # 5. Retornar top K
            results = combined[:top_k]

            log_info(
                logger,
                "Retrieval Redis concluído",
                question_len=len(question),
                results=len(results),
            )

            return results

        except Exception as e:
            log_error(logger, "Erro no retrieval Redis", e)
            return []

    def _retrieve_fallback(self, question: str, top_k: int) -> List[Dict[str, Any]]:
        """Busca híbrida usando dados em memória."""
        if not self._fallback_articles:
            return []

        try:
            results = []

            # 1. Busca vetorial (cosine similarity)
            if self._fallback_embeddings is not None:
                query_embedding = self.embeddings_service.get_embedding(question)
                query_vec = np.array([query_embedding], dtype=np.float32)

                # Calcular similaridade
                similarities = cosine_similarity(query_vec, self._fallback_embeddings)[0]

                # Adicionar scores aos artigos
                for idx, score in enumerate(similarities):
                    if idx < len(self._fallback_articles):
                        art = self._fallback_articles[idx].copy()
                        art["score"] = float(score)
                        results.append(art)

            # 2. Busca textual (TF-IDF)
            text_results = []
            if self._tfidf_vectorizer and self._tfidf_matrix is not None:
                query_vec = self._tfidf_vectorizer.transform([question])
                similarities = cosine_similarity(query_vec, self._tfidf_matrix)[0]

                for idx, score in enumerate(similarities):
                    if idx < len(self._fallback_articles):
                        text_results.append(
                            {
                                "id": self._fallback_articles[idx].get("id"),
                                "score": float(score),
                            }
                        )

            # 3. Combinar scores
            if results and text_results:
                # Score híbrido
                text_scores = {r["id"]: r["score"] for r in text_results}
                for doc in results:
                    vec_score = doc.get("score", 0.0)
                    txt_score = text_scores.get(doc.get("id"), 0.0)
                    doc["score"] = 0.7 * vec_score + 0.3 * txt_score

            # 4. Ordenar e retornar top K
            results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            results = results[:top_k]

            log_info(
                logger,
                "Retrieval fallback concluído",
                question_len=len(question),
                results=len(results),
            )

            return results

        except Exception as e:
            log_error(logger, "Erro no retrieval fallback", e)
            return []


# Singleton
_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    """Retorna instância singleton do retriever."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
