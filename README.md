# Space Biology Knowledge Engine — Azure Free Tier Starter

This starter focuses on the fact that **all content lives behind the 608 links** (CSV with `title,link`). 
It uses **Azure Static Web Apps (Free)** for the frontend and **Azure Functions (Consumption)** for the backend.

## What works in this MVP
- Input a paper **URL** and extract **clean text** from HTML or PDF.
- **Sectionize** the text into: Introduction / Methods / Results / Conclusion / Other (heuristic).
- Return normalized JSON ready for future steps (embeddings, graph, search index).

## Deploy (fast path, Free)
1. **Create Static Web App (Free)** in Azure Portal (Build preset: *Custom*).  
2. In the SWA, configure **Azure Functions API** (Python). Folder: `/api`  
3. Set app artifact location to `/web` (static).  
4. Configure **app settings** in the function (if needed): `FETCH_TIMEOUT_SECS` (default 20).

## Local dev
- Web: just open `web/index.html` or serve with any static server.
- Functions: `cd api && func start` (requires Azure Functions Core Tools + Python 3.11).

## Next steps (keeping FREE as much as possible)
- Add **Azure AI Search (Free)** index for chunk vectors + filters.
- Add **Cosmos DB Free Tier** (Gremlin) for the knowledge graph.
- Add `/api/index` to chunk + embed + upsert to Search (only when a paper is opened or queried).

## Files
- `api/extract` — HTTP endpoint: `GET /api/extract?url=...`
- `api/shared` — helpers for fetching and sectionizing.
- `web/` — simple HTML + JS to test.
