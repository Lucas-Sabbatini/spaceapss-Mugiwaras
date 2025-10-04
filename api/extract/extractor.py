import os
import asyncio
from shared.fetchers import fetch_url, sniff_is_pdf, extract_pdf_text, extract_html_text

# Função centralizada para extrair texto de uma URL (seja HTML ou PDF)
async def extract_url(url: str):
    """
    Extrai o texto limpo de uma URL, detectando automaticamente se é HTML ou PDF.
    Retorna uma tupla com (texto_extraído, tipo_da_fonte).
    """
    content, ctype = await fetch_url(url)
    is_pdf = sniff_is_pdf(url, ctype, content)
    text = extract_pdf_text(content) if is_pdf else extract_html_text(content)
    source_type = "pdf" if is_pdf else "html"
    return text.strip(), source_type