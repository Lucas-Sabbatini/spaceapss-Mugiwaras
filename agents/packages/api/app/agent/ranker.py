"""Ranker para re-ordenar documentos recuperados."""

from typing import Any, Dict, List

from packages.api.app.services.logger import get_logger, log_info

logger = get_logger(__name__)


def rerank_by_year(docs: List[Dict[str, Any]], year_weight: float = 0.1) -> List[Dict[str, Any]]:
    """
    Re-rankeia documentos dando bônus para artigos mais recentes.
    
    Args:
        docs: Lista de documentos com score
        year_weight: Peso do bônus por ano (default: 0.1)
        
    Returns:
        Lista de documentos re-rankeados
    """
    if not docs:
        return []

    # Encontrar ano mais recente
    max_year = max((doc.get("year", 1900) for doc in docs), default=2024)

    # Calcular score ajustado
    for doc in docs:
        year = doc.get("year", 1900)
        base_score = doc.get("score", 0.0)

        # Bônus: artigos mais recentes ganham até year_weight extra
        # Normalizado pela diferença do ano mais recente
        if max_year > 1900:
            year_bonus = (year - 1900) / (max_year - 1900) * year_weight
        else:
            year_bonus = 0.0

        doc["adjusted_score"] = base_score + year_bonus

    # Ordenar por score ajustado
    ranked = sorted(docs, key=lambda x: x.get("adjusted_score", 0.0), reverse=True)

    log_info(
        logger,
        "Documentos re-rankeados",
        total=len(ranked),
        year_weight=year_weight,
        max_year=max_year,
    )

    return ranked


def combine_scores(
    vector_docs: List[Dict[str, Any]],
    text_docs: List[Dict[str, Any]],
    alpha: float = 0.7,
) -> List[Dict[str, Any]]:
    """
    Combina scores de busca vetorial e textual (híbrido).
    
    Args:
        vector_docs: Documentos da busca vetorial com score
        text_docs: Documentos da busca textual
        alpha: Peso da busca vetorial (default: 0.7)
        
    Returns:
        Lista de documentos com score híbrido
    """
    # Criar mapa de scores vetoriais (normalizado 0-1, invertido porque cosine menor = melhor)
    vector_scores = {}
    max_vec_score = max((doc.get("score", 0.0) for doc in vector_docs), default=1.0)
    min_vec_score = min((doc.get("score", 0.0) for doc in vector_docs), default=0.0)

    for doc in vector_docs:
        doc_id = doc.get("id")
        raw_score = doc.get("score", 0.0)

        # Normalizar: cosine distance -> similarity score
        if max_vec_score > min_vec_score:
            normalized = 1.0 - (raw_score - min_vec_score) / (max_vec_score - min_vec_score)
        else:
            normalized = 1.0

        vector_scores[doc_id] = normalized

    # BM25: simular score (em produção real, Redis retorna score BM25)
    # Aqui apenas damos score 0.5 para presença no resultado textual
    text_scores = {doc.get("id"): 0.5 for doc in text_docs}

    # Combinar todos os IDs únicos
    all_ids = set(vector_scores.keys()) | set(text_scores.keys())

    # Criar docs combinados
    combined = []
    for doc_id in all_ids:
        vec_score = vector_scores.get(doc_id, 0.0)
        txt_score = text_scores.get(doc_id, 0.0)

        # Score híbrido
        hybrid_score = alpha * vec_score + (1 - alpha) * txt_score

        # Pegar dados do documento (priorizar vector_docs)
        doc_data = next((d for d in vector_docs if d.get("id") == doc_id), None)
        if not doc_data:
            doc_data = next((d for d in text_docs if d.get("id") == doc_id), None)

        if doc_data:
            doc_data["score"] = hybrid_score
            combined.append(doc_data)

    # Ordenar por score híbrido
    combined.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    log_info(logger, "Scores combinados", total=len(combined), alpha=alpha)

    return combined
