import logging
import json
import azure.functions as func
from . import extractor
from shared.sectionizer import sectionize_text

# HTTP Trigger: GET /api/extract?url=...
async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        url = req.params.get("url")
        if not url:
            return func.HttpResponse(
                json.dumps({"error": "missing url param"}),
                status_code=400,
                mimetype="application/json",
            )
        
        # 1. Extrai o texto usando a função centralizada
        text, source_type = await extractor.extract_url(url)
        
        # 2. Separa o texto em seções
        sections = sectionize_text(text)
        
        # 3. Monta o resultado JSON final para a API
        result = {
            "url": url,
            "source_type": source_type,
            "length_chars": len(text),
            "sections": sections,
        }

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.exception("extract failed")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )