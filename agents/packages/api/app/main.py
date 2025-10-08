"""Aplicação FastAPI principal."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from packages.api.app.config import get_settings
from packages.api.app.routers import articles, chat, health, graph
from packages.api.app.services.logger import get_logger, log_info

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events da aplicação."""
    yield

    # Shutdown
    log_info(logger, "Encerrando aplicação")


# Criar aplicação
app = FastAPI(
    title="SpaceAPSS Agents API",
    description="API para busca e resposta sobre artigos científicos usando RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(articles.router)
app.include_router(graph.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SpaceAPSS Agents API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "packages.api.app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.is_dev,
    )
