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
    prompt = f"""You are an assistant specializing in scientific articles on space sciences and biomedicine.

Your task is to answer the question below CONCISELY and OBJECTIVELY, based EXCLUSIVELY on the provided documents.

IMPORTANT RULES:
    1.Be direct, without unnecessary introductions
    2.Cite sources mentioned in the documents with author and year (Author, Year)
    3.DO NOT invent information that is not in the documents
    4.If there is not enough information, state clearly: "I did not find enough information in the available articles"
    5.Focus on the main findings and conclusions

Related Documents:
{context_text}

Question:
{question}

Answer:"""

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
