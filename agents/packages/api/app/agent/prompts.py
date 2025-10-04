"""Prompts para síntese de respostas."""

from typing import List, Dict, Any


def build_synthesis_prompt(question: str, context_docs: List[Dict[str, Any]]) -> str:
    """
    Constrói prompt de síntese seguro e conciso.
    
    Args:
        question: Pergunta do usuário
        context_docs: Lista de documentos relevantes
        
    Returns:
        Prompt formatado para o LLM
    """
    # Montar contexto dos documentos
    context_parts = []
    for idx, doc in enumerate(context_docs[:3], 1):  # Máximo 3 docs no contexto
        title = doc.get("title", "")
        year = doc.get("year", "")
        doi = doc.get("doi", "")
        abstract = doc.get("abstract", "")[:500]  # Limitar abstract

        context_parts.append(
            f"""
[Documento {idx}]
Título: {title}
Ano: {year}
DOI: {doi if doi else "N/A"}
Resumo: {abstract}
"""
        )

    context_text = "\n".join(context_parts)

    # Template do prompt
    prompt = f"""Você é um assistente especializado em artigos científicos sobre ciências espaciais e biomedicina.

Sua tarefa é responder a pergunta abaixo de forma CONCISA e OBJETIVA, baseando-se EXCLUSIVAMENTE nos documentos fornecidos.

REGRAS IMPORTANTES:
1. Responda em português brasileiro (PT-BR)
2. Limite sua resposta a 6-8 linhas
3. Seja direto ao ponto, sem introduções desnecessárias
4. Cite as fontes usando: (Título, Ano) ou (DOI)
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
