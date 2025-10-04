"""Router de artigos."""

from fastapi import APIRouter, Depends, HTTPException

from packages.api.app.deps import get_redis_dependency
from packages.api.app.schemas import Article
from packages.api.app.services.logger import get_logger, log_error, log_info
from packages.api.app.services.redis_client import RedisClient

logger = get_logger(__name__)
router = APIRouter(prefix="/article", tags=["articles"])


@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: str, redis: RedisClient = Depends(get_redis_dependency)):
    """
    Recupera um artigo completo por ID.
    
    Args:
        article_id: ID do artigo (sem prefixo "article:")
        
    Returns:
        Article completo
    """
    log_info(logger, "Get article request", article_id=article_id)

    try:
        article_data = redis.get_article(article_id)

        if not article_data:
            log_info(logger, "Artigo não encontrado", article_id=article_id)
            raise HTTPException(status_code=404, detail=f"Artigo '{article_id}' não encontrado")

        article = Article(**article_data)
        log_info(logger, "Artigo recuperado com sucesso", article_id=article_id)

        return article

    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, "Erro ao recuperar artigo", e, article_id=article_id)
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar artigo: {str(e)}")
