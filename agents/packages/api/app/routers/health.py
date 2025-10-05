"""Router de health check."""

from fastapi import APIRouter

from packages.api.app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check do serviço.
    
    Verifica se a API está respondendo.
    """
    return HealthResponse(status="ok", redis=None, version="0.1.0")
