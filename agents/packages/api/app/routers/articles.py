"""Router de artigos (DESABILITADO - não usado no fluxo simplificado)."""

from fastapi import APIRouter, HTTPException

from packages.api.app.schemas import Article
from packages.api.app.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/article", tags=["articles"])


@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """
    Endpoint desabilitado - não é mais usado no fluxo simplificado.
    
    O sistema agora retorna apenas respostas sintetizadas, não artigos completos.
    """
    raise HTTPException(
        status_code=501,
        detail="Endpoint não implementado. Use /chat para fazer perguntas."
    )
