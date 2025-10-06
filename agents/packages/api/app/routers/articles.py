"""Router de artigos - busca artigos do Cosmos DB."""

from fastapi import APIRouter, HTTPException

from packages.api.app.schemas import ArticleDetail
from packages.api.app.services.logger import get_logger
from packages.api.app.services.cosmos_data import CosmosDataManager
from packages.api.app.config import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/article", tags=["articles"])


@router.get("/{experiment_id}", response_model=ArticleDetail)
async def get_article(experiment_id: str):
    """
    Busca artigo pelo experiment_id (ex: PMC9267413).
    
    Este endpoint retorna dados básicos do artigo do Cosmos DB:
    - Metadados básicos (título, abstract, url)
    - Conteúdo extraído
    
    Args:
        experiment_id: ID do experimento no formato PMC seguido de números (ex: PMC9267413)
        
    Returns:
        ArticleDetail com os campos disponíveis do artigo
        
    Raises:
        HTTPException 404: Se o artigo não for encontrado
        HTTPException 500: Se houver erro ao buscar no banco de dados
    """
    try:
        # Normalizar o experiment_id (adicionar PMC se necessário)
        if not experiment_id.startswith('PMC'):
            experiment_id = f'PMC{experiment_id}'
        
        logger.info(f"Buscando artigo no Cosmos DB: {experiment_id}")
        
        # Buscar no Cosmos DB
        settings = get_settings()
        db_manager = CosmosDataManager(
            endpoint=settings.cosmos_endpoint,
            key=settings.cosmos_key,
            database_name=settings.cosmos_database,
            container_name=settings.cosmos_container
        )
        
        if not db_manager.enabled:
            raise HTTPException(
                status_code=503,
                detail="Cosmos DB não está configurado"
            )
        
        # Buscar documento por ID
        try:
            article_data = db_manager.container.read_item(
                item=experiment_id,
                partition_key=experiment_id
            )
        except Exception as e:
            logger.warning(f"Artigo não encontrado no Cosmos DB: {experiment_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Artigo {experiment_id} não encontrado"
            )
        
        logger.info(f"Artigo encontrado: {experiment_id} - {article_data.get('title', 'Sem título')}")
        
        # Converter para ArticleDetail (com campos opcionais)
        return ArticleDetail(
            experiment_id=article_data.get('doc_id', experiment_id),
            title=article_data.get('title'),
            abstract=article_data.get('abstract'),
            summary_en=article_data.get('content', '')[:500] if article_data.get('content') else None,
            url=article_data.get('url'),
            full_text=article_data.get('content')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar artigo {experiment_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar artigo: {str(e)}"
        )
