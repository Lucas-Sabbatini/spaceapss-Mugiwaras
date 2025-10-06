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
        context_parts.append(f"[Document {idx}]\n{doc_text}\n")

    context_text = "\n".join(context_parts)

    # Template do prompt
    prompt = f"""You are a specialized assistant for scientific articles about space sciences and biomedicine.

Your task is to provide a COMPREHENSIVE and DETAILED response to the question below, based EXCLUSIVELY on the provided documents.

IMPORTANT RULES:
1. Respond in English using proper Markdown formatting
2. Provide a thorough and complete answer with sufficient detail
3. Include relevant background information, methods, findings, and implications
4. Always cite the sources mentioned in the documents
5. DO NOT invent information that is not in the documents
6. If there is insufficient information, start with a clear statement and then provide what information IS available
7. Structure your response logically with clear sections
8. Include specific data, numbers, and results when available in the documents
9. Explain technical terms or concepts when necessary for understanding
10. Highlight key findings, significant results, and their scientific implications

FORMATTING GUIDELINES:
- Use **bold** for important terms, findings, or emphasis
- Use *italics* for document references or technical terms
- Use bullet points (- or *) for lists of findings, methods, or key points
- Use > for important quotes or highlighted information
- Organize information with clear paragraph breaks
- When listing multiple findings, use bullet points for clarity
- If information is incomplete, structure your response as:
  1. First paragraph: State what information is missing or limited
  2. Following section: "**Available Information:**" followed by bullet points of what IS known
  3. Optional: Brief conclusion about limitations

RELEVANT DOCUMENTS:
{context_text}

QUESTION:
{question}

DETAILED RESPONSE (using Markdown formatting with citations):"""

    return prompt


def build_fallback_prompt(question: str) -> str:
    """
    Prompt quando não há documentos relevantes.
    
    Args:
        question: Pergunta do usuário
        
    Returns:
        Mensagem de fallback
    """
    return f"""**No Relevant Articles Found**

I could not find relevant scientific articles in the database to answer the question:

> "{question}"

**Suggestions:**
- Try rephrasing your question with different keywords
- Verify if articles on this topic have been ingested into the system
- Check if your query is within the scope of space sciences and biomedicine research"""
