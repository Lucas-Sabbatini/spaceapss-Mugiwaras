# Agente de Artigos Científicos - SpaceAPSS

Um sistema monorepo em Python para busca e resposta sobre artigos científicos usando Redis Stack, FastAPI e OpenAI.

## Stack

- **Python**: 3.11+
- **API**: FastAPI + Uvicorn
- **Validação**: Pydantic v2
- **Database**: Redis Stack (RedisJSON + RediSearch)
- **Embeddings**: OpenAI / Azure OpenAI
- **Orquestração**: Vanilla (sem LangChain)
- **Testes**: pytest
- **Lint/Format**: ruff + black
- **Container**: Docker Compose

## Estrutura

```
agents/
  README.md
  .env.example
  docker-compose.yml
  pyproject.toml
  Makefile
  packages/
    api/
      app/
        main.py              # FastAPI app
        deps.py              # Dependências
        config.py            # Configurações
        schemas.py           # Modelos Pydantic
        routers/
          health.py          # Health check
          chat.py            # Chat endpoint
          articles.py        # Artigos CRUD
        agent/
          pipeline.py        # Orquestração principal
          retriever.py       # Busca vetorial + BM25
          ranker.py          # Re-ranking
          prompts.py         # Templates de prompts
        services/
          redis_client.py    # Cliente Redis
          embeddings.py      # Embeddings OpenAI/Azure
          logger.py          # Logger
      tests/
        test_schemas.py
        test_retriever.py
        conftest.py
    ingest/
      app/
        load_json.py         # Carrega artigos
        make_embeddings.py   # Gera embeddings
        utils.py
      data/
        samples/
          sample_01.json
          sample_02.json
          sample_03.json
```

## Setup

### 1. Instalar dependências

```bash
# Usando uv (recomendado)
pip install uv
uv pip install -e .

# Ou usando pip
pip install -e .
```

### 2. Configurar variáveis de ambiente

Copie o `.env.example` para `.env` e preencha os valores:

```bash
cp .env.example .env
```

### 3. Subir Redis Stack

```bash
docker compose up -d
```

Acesse Redis Insight em http://localhost:8001

### 4. Ingerir dados de exemplo

```bash
# Carregar artigos no Redis
python -m packages.ingest.app.load_json

# Gerar embeddings
python -m packages.ingest.app.make_embeddings
```

Ou usando Makefile:

```bash
make ingest
make embed
```

### 5. Iniciar API

```bash
uvicorn packages.api.app.main:app --reload --port 8000
```

Ou:

```bash
make dev
```

## Uso

### Exemplo: Fazer uma pergunta

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Quais efeitos da microgravidade em células-tronco?","topK":5}'
```

Resposta:

```json
{
  "answer": "Estudos mostram que a microgravidade afeta a diferenciação...",
  "sources": [
    {
      "id": "art-001",
      "title": "Effects of Microgravity on Stem Cells",
      "year": 2023,
      "doi": "10.1234/example",
      "url": "https://example.com/article",
      "score": 0.89
    }
  ],
  "article": {
    "id": "art-001",
    "title": "...",
    "authors": ["..."],
    ...
  }
}
```

### Obter artigo por ID

```bash
curl http://localhost:8000/article/art-001
```

### Health check

```bash
curl http://localhost:8000/health
```

## Makefile

```bash
make deps      # Instalar dependências
make up        # Subir Redis Stack
make dev       # Rodar API em modo dev
make ingest    # Ingerir samples
make embed     # Gerar embeddings
make test      # Rodar testes
make format    # Formatar código (black)
make lint      # Lint (ruff)
```

## Fluxo do Agente

1. **Recebe pergunta** via POST /chat
2. **Gera embedding** da pergunta usando OpenAI
3. **Busca vetorial** (KNN) no Redis + busca textual (BM25)
4. **Score híbrido**: 0.7 × cosine + 0.3 × BM25
5. **Re-rank** por ano (mais recente ganha pequeno bônus)
6. **Síntese** via LLM (OpenAI/Azure) com contexto dos tops
7. **Retorna** resposta + fontes + artigo completo

## Banco de Dados (Redis Stack)

- **Key**: `article:{id}` → JSON completo do artigo
- **Índice**: `idx:articles`
  - `$.title` (TEXT)
  - `$.abstract` (TEXT)
  - `$.year` (NUMERIC)
  - `$.doi` (TAG)
  - `$.embedding` (VECTOR, FLOAT32, dim=1536)

## Modo Fallback (sem Redis)

Se `REDIS_URL` não estiver disponível, o sistema:

- Carrega samples em memória
- Usa numpy para similaridade coseno
- Usa scikit-learn para BM25 (TF-IDF)
- Mantém mesma API

## Testes

```bash
pytest
```

Ou:

```bash
make test
```

## Formatação e Lint

```bash
# Formatar
black packages/

# Lint
ruff check packages/
```

## Variáveis de Ambiente

Veja `.env.example` para configurações completas.

Principais:

- `PROVIDER`: `openai` ou `azure`
- `OPENAI_API_KEY`: Chave da OpenAI
- `REDIS_URL`: URL do Redis (padrão: `redis://localhost:6379`)
- `ENV`: `dev` ou `prod`

## Desenvolvimento

O código segue boas práticas:

- ✅ Tipagem completa (Pydantic v2)
- ✅ Logs estruturados
- ✅ Tratamento de erros (HTTPException)
- ✅ CORS habilitado para frontend
- ✅ Testes unitários
- ✅ Código formatado (black) e lintado (ruff)

## Licença

MIT
