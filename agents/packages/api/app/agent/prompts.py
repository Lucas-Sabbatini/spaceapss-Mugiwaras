"""Prompts para síntese de respostas."""

from typing import List


def build_synthesis_prompt(question: str, context_docs: List[str]) -> str:
    """
    Constrói prompt de síntese seguro e conciso.
    
    Args:
        question: Pergunta do usuário
        context_docs: Lista de strings relacionadas à pergunta
        
    Returns:
        Prompt formatado para o LLM
    """
    # Montar contexto dos documentos (apenas strings)
    context_parts = []
    for idx, doc_text in enumerate(context_docs[:5], 1):  # Máximo 5 docs no contexto
        context_parts.append(f"[Documento {idx}]\n{doc_text}\n")

    context_text = "\n".join(context_parts)

    # Template do prompt
    prompt = f"""Você é um assistente especializado em artigos científicos sobre ciências espaciais e biomedicina.

Sua tarefa é responder a pergunta abaixo de forma CONCISA e OBJETIVA, baseando-se EXCLUSIVAMENTE nos documentos fornecidos.

REGRAS IMPORTANTES:
1. Responda em português brasileiro (PT-BR)
2. Limite sua resposta a 6-8 linhas
3. Seja direto ao ponto, sem introduções desnecessárias
4. Cite as fontes mencionadas nos documentos
5. NÃO invente informações que não estão nos documentos
6. Se não houver informação suficiente, diga claramente: "Não encontrei informações suficientes nos artigos disponíveis"
7. Foque nos achados principais e conclusões

DOCUMENTOS RELEVANTES:
{context_text}

PERGUNTA:
{question}

RESPOSTA (6-8 linhas, citando fontes):"""

    return prompt


def build_fallback_prompt(question: str) -> str:
    """
    Prompt quando não há documentos relevantes.
    
    Args:
        question: Pergunta do usuário
        
    Returns:
        Mensagem de fallback
    """
    return f"""Não encontrei artigos científicos relevantes no banco de dados para responder à pergunta:

"{question}"

Por favor, tente reformular sua pergunta ou verificar se os artigos sobre este tema foram ingeridos no sistema."""
