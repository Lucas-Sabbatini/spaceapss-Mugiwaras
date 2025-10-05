"""Router de chat/perguntas."""

from fastapi import APIRouter, Depends, HTTPException

from packages.api.app.agent.pipeline import AgentPipeline
from packages.api.app.deps import get_pipeline_dependency
from packages.api.app.schemas import ChatRequest, ChatResponse
from packages.api.app.services.logger import get_logger, log_error, log_info

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, pipeline: AgentPipeline = Depends(get_pipeline_dependency)):
    """
    Endpoint principal de chat.
    
    Recebe uma pergunta e retorna:
    - Resposta sintetizada pelo LLM
    - Lista de fontes/artigos relevantes
    - Artigo completo mais relevante
    
    Args:
        request: ChatRequest com question e topK opcional
        
    Returns:
        ChatResponse com answer, sources e article
    """
    log_info(logger, "Chat request recebido", question_len=len(request.question), top_k=request.topK)

    try:
        # Executar pipeline
        response = pipeline.answer(question=request.question, top_k=request.topK or 5)

        log_info(logger, "Chat response gerado com sucesso")
        return response

    except Exception as e:
        log_error(logger, "Erro ao processar chat request", e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")