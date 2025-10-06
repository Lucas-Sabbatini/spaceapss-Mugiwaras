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
    Busca artigo pelo experiment_id (ex: PMC9267413, article-1).
    
    Este endpoint retorna dados básicos do artigo do Cosmos DB:
    - Metadados básicos (título, abstract, url)
    - Conteúdo extraído
    
    Args:
        experiment_id: ID do experimento (ex: PMC9267413, article-1)
        
    Returns:
        ArticleDetail com os campos disponíveis do artigo
        
    Raises:
        HTTPException 404: Se o artigo não for encontrado
        HTTPException 500: Se houver erro ao buscar no banco de dados
    """
    try:
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
        # Tentar primeiro com o ID original
        article_data = None
        try:
            article_data = db_manager.container.read_item(
                item=experiment_id,
                partition_key=experiment_id
            )
            logger.info(f"Artigo encontrado com ID: {experiment_id}")
        except Exception:
            # Se não encontrar, tentar com prefixo PMC (para compatibilidade com IDs numéricos)
            if not experiment_id.startswith('PMC'):
                pmc_id = f'PMC{experiment_id}'
                try:
                    article_data = db_manager.container.read_item(
                        item=pmc_id,
                        partition_key=pmc_id
                    )
                    logger.info(f"Artigo encontrado com ID PMC: {pmc_id}")
                    experiment_id = pmc_id
                except Exception:
                    pass
        
        if not article_data:
            logger.warning(f"Artigo não encontrado no Cosmos DB: {experiment_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Artigo {experiment_id} não encontrado"
            )
        
        logger.info(f"Artigo encontrado: {experiment_id} - {article_data.get('title', 'Sem título')}")
        
        # Converter para ArticleDetail (com campos opcionais)
        # Usar doc_id ou id do documento como experiment_id
        doc_id = article_data.get('doc_id') or article_data.get('id') or experiment_id
        
        return ArticleDetail(
            experiment_id=doc_id,
            title=article_data.get('title'),
            abstract=article_data.get('abstract'),
            summary_en=article_data.get('content', '')[:500] if article_data.get('content') else None,
            url=article_data.get('url'),
            full_text=article_data.get('full_text') or article_data.get('content')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar artigo {experiment_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar artigo: {str(e)}"
        )
