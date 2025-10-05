import os
import asyncio
from extract.fetchers import fetch_url, sniff_is_pdf, extract_pdf_text, extract_html_text
from extract.ncbi_fetcher import fetch_pmc_from_url

# Função centralizada para extrair texto de uma URL (seja HTML ou PDF)
async def extract_url(url: str):
    """
    Extrai o texto limpo de uma URL, detectando automaticamente se é HTML ou PDF.
    Para URLs do NCBI PMC, usa a API oficial.
    Retorna uma tupla com (texto_extraído, tipo_da_fonte).
    """
    # Detectar se é URL do NCBI PMC e usar API oficial
    if 'ncbi.nlm.nih.gov/pmc' in url:
        result = await fetch_pmc_from_url(url)
        if result:
            # Combina abstract e content
            text = f"{result['abstract']}\n\n{result['content']}"
            return text.strip(), "ncbi_api"
        else:
            return "", "ncbi_api_failed"
    
    # Caso contrário, usa o método tradicional
    content, ctype = await fetch_url(url)
    is_pdf = sniff_is_pdf(url, ctype, content)
    text = extract_pdf_text(content) if is_pdf else extract_html_text(content)
    source_type = "pdf" if is_pdf else "html"
    return text.strip(), source_type