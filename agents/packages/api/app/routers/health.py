"""Router de health check."""

from fastapi import APIRouter, Depends

from packages.api.app.deps import get_redis_dependency
from packages.api.app.schemas import HealthResponse
from packages.api.app.services.redis_client import RedisClient

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(redis: RedisClient = Depends(get_redis_dependency)):
    """
    Health check do serviço.
    
    Verifica se a API está respondendo e se Redis está conectado.
    """
    redis_status = "connected" if redis.is_connected() else "disconnected (fallback mode)"

    return HealthResponse(status="ok", redis=redis_status, version="0.1.0")
