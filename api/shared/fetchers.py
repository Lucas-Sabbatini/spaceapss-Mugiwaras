import aiohttp
import asyncio
from io import BytesIO
from bs4 import BeautifulSoup
from readability import Document
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

DEFAULT_TIMEOUT = int(os.getenv("FETCH_TIMEOUT_SECS", "20"))

async def fetch_url(url: str):
    timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, allow_redirects=True) as resp:
            content = await resp.read()
            ctype = resp.headers.get("Content-Type", "")
            return content, ctype

def sniff_is_pdf(url: str, ctype: str, content: bytes) -> bool:
    if "application/pdf" in ctype.lower():
        return True
    if url.lower().endswith(".pdf"):
        return True
    # simple magic number check
    return content[:4] == b"%PDF"

def extract_pdf_text(content: bytes) -> str:
    try:
        bio = BytesIO(content)
        return extract_text(bio)
    except PDFSyntaxError:
        return ""

def extract_html_text(content: bytes) -> str:
    html = content.decode("utf-8", errors="ignore")
    # readability first
    try:
        doc = Document(html)
        main = doc.summary(html_partial=True)
        soup = BeautifulSoup(main, "lxml")
        text = soup.get_text(separator="\n")
        if text and len(text.strip()) > 100:
            return text
    except Exception:
        pass
    # fallback: full page text
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script","style","noscript"]): tag.decompose()
    return soup.get_text(separator="\n")
