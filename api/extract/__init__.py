import logging
import json
import azure.functions as func
from . import extractor

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
        result = await extractor.extract_url(url)
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
