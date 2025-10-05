import os
import aiohttp
import asyncio
from io import BytesIO
from bs4 import BeautifulSoup
from readability import Document
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

DEFAULT_TIMEOUT = int(os.getenv("FETCH_TIMEOUT_SECS", "20"))

async def fetch_url(url: str):
    timeout = aiohttp.ClientTimeout(total=20)
    # Adiciona um cabeçalho para simular um navegador comum
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        async with session.get(url, allow_redirects=True) as resp:
            # Verifica se o pedido foi bem-sucedido (código 200)
            if resp.status != 200:
                print(f"  [ERRO HTTP] Recebido status {resp.status} para a URL: {url}")
                return b"", ""  # Retorna conteúdo vazio em caso de erro
            content = await resp.read()
            ctype = resp.headers.get("Content-Type", "")
            return content, ctype

def sniff_is_pdf(url: str, ctype: str, content: bytes) -> bool:
    if "application/pdf" in ctype.lower():
        return True
    if url.lower().endswith(".pdf"):
        return True
    # verificação simples de "magic number"
    return content[:4] == b"%PDF"

def extract_pdf_text(content: bytes) -> str:
    try:
        bio = BytesIO(content)
        return extract_text(bio)
    except PDFSyntaxError:
        return ""
    except Exception:
        return ""

def extract_html_text(content: bytes) -> str:
    html = content.decode("utf-8", errors="ignore")
    # Tenta primeiro com readability
    try:
        doc = Document(html)
        main = doc.summary(html_partial=True)
        soup = BeautifulSoup(main, "lxml")
        text = soup.get_text(separator="\n")
        if text and len(text.strip()) > 100:
            return text
    except Exception:
        pass
    # Alternativa: texto da página completa
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script","style","noscript"]): tag.decompose()
    return soup.get_text(separator="\n")