import os
import asyncio
from ..shared.fetchers import fetch_url, sniff_is_pdf, extract_pdf_text, extract_html_text
from ..shared.sectionizer import sectionize_text

async def extract_url(url: str):
    # fetch bytes + content-type
    content, ctype = await fetch_url(url)
    if sniff_is_pdf(url, ctype, content):
        text = extract_pdf_text(content)
        source_type = "pdf"
    else:
        text = extract_html_text(content)
        source_type = "html"

    sections = sectionize_text(text)
    # Basic schema for MVP
    return {
        "url": url,
        "source_type": source_type,
        "length_chars": len(text or ""),
        "sections": sections
    }
