"""Router de artigos - busca artigos enriquecidos no MongoDB."""

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from packages.api.app.deps import get_mongodb_database
from packages.api.app.schemas import ArticleDetail
from packages.api.app.services.logger import get_logger
from packages.api.app.config import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/article", tags=["articles"])


@router.get("/{experiment_id}", response_model=ArticleDetail)
async def get_article(
    experiment_id: str,
    db: Database = Depends(get_mongodb_database)
):
    """
    Busca artigo enriquecido pelo experiment_id (ex: PMC9267413).
    
    Este endpoint retorna todos os dados do artigo, incluindo:
    - Metadados básicos (título, autores, ano, etc.)
    - Resumo em inglês (summary_en)
    - Dados extraídos por NLP (objetivos, métodos, resultados, etc.)
    - Texto completo (se disponível)
    
    Args:
        experiment_id: ID do experimento no formato PMC seguido de números (ex: PMC9267413)
        db: Database MongoDB injetado como dependência
        
    Returns:
        ArticleDetail com todos os campos do artigo
        
    Raises:
        HTTPException 404: Se o artigo não for encontrado
        HTTPException 500: Se houver erro ao buscar no banco de dados
    """
    try:
        # Normalizar o experiment_id (adicionar PMC se necessário)
        if not experiment_id.startswith('PMC'):
            experiment_id = f'PMC{experiment_id}'
        
        logger.info(f"Buscando artigo: {experiment_id}")
        
        # Buscar no MongoDB
        settings = get_settings()
        collection = db[settings.mongodb_collection]
        
        article_data = collection.find_one(
            {'experiment_id': experiment_id},
            {'_id': 0}  # Excluir o campo _id do MongoDB
        )
        
        if not article_data:
            logger.warning(f"Artigo não encontrado: {experiment_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Artigo {experiment_id} não encontrado no banco de dados"
            )
        
        logger.info(f"Artigo encontrado: {experiment_id} - {article_data.get('title', 'Sem título')}")
        
        return ArticleDetail(**article_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar artigo {experiment_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar artigo: {str(e)}"
        )
